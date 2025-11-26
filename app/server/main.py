import asyncio
import json
import os
from pathlib import Path
from typing import AsyncIterable

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from google.genai.types import Modality  # FIX: Import Modality enum
import warnings

# Import your agent and tools
# Ensure these paths match your project structure
from app.computer.agent import root_agent
from app.computer.tools.screen import capture_screen
from app.computer.tools import control
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
load_dotenv()

APP_NAME = "Computer Use Live Agent"
STATIC_DIR = Path("static")

session_service = InMemorySessionService()
app = FastAPI()

# Ensure static directory exists
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def start_agent_session(session_id: str):
    """Starts the ADK Live Runner session."""
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )

    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    # FIX: Use Enum for modalities to prevent Pydantic warnings/errors
    run_config = RunConfig(
        response_modalities=[Modality.TEXT],
    )

    live_request_queue = LiveRequestQueue()

    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )

    return live_events, live_request_queue


async def agent_to_client_messaging(
    websocket: WebSocket, 
    live_events: AsyncIterable[Event | None],
    live_request_queue: LiveRequestQueue
):
    """
    Handles events from Agent -> Client.
    """
    # FIX: Track accumulated text for the current turn to prevent duplicates
    # while still allowing full text if the agent sends it all at once.
    current_turn_text = ""

    try:
        async for event in live_events:
            if event is None:
                continue

            # --- HANDLE TOOL CALLS ---
            if hasattr(event, 'tool_calls') and event.tool_calls:
                for tool_call in event.tool_calls:
                    print(f"🛠️ Agent calling tool: {tool_call.name}")
                    
                    tool_response_data = {}
                    
                    # 1. Screen Capture
                    if tool_call.name == "capture_screen":
                        result = capture_screen()
                        if result["status"] == "success":
                            await websocket.send_json({"role": "system", "text": "📸 Screenshot captured."})

                            # --- INJECT IMAGE AS CONTENT ---
                            img_bytes = result["screenshot"]
                            
                            image_content = types.Content(
                                role="user",
                                parts=[
                                    types.Part.from_data(
                                        data=img_bytes,
                                        mime_type="image/jpeg" # JPEG is safer for streaming
                                    ),
                                    types.Part.from_text(
                                        text="[SYSTEM] Here is the screenshot. Analyze it."
                                    )
                                ]
                            )
                            
                            await live_request_queue.send_content(image_content)
                            tool_response_data = {"result": "Image uploaded to chat history."}
                        else:
                            tool_response_data = {"error": result.get("message", "Unknown error")}

                    # 2. Control Tools
                    elif hasattr(control, tool_call.name):
                        func = getattr(control, tool_call.name)
                        try:
                            # Execute the tool
                            raw_result = func(**tool_call.args)
                            
                            # FIX: CRITICAL - SANITIZE RESPONSE FOR 1011 ERROR
                            # The API crashes if response is not a clean dict
                            if isinstance(raw_result, dict):
                                tool_response_data = raw_result
                            else:
                                tool_response_data = {"result": str(raw_result)}
                                
                            print(f"   ✅ Executed {tool_call.name}")
                            await websocket.send_json({"role": "system", "text": f"⚡ Executed: {tool_call.name}"})
                            
                            # Small delay for UI to update after Enter/Click
                            if tool_call.name in ["press_key", "click_mouse"]:
                                await asyncio.sleep(0.5)

                        except Exception as e:
                            print(f"   ❌ Error executing {tool_call.name}: {e}")
                            tool_response_data = {"error": str(e)}
                    
                    else:
                        tool_response_data = {"error": f"Unknown tool: {tool_call.name}"}

                    # --- SEND TOOL RESPONSE ---
                    tool_response = types.LiveClientToolResponse(
                        function_responses=[
                            types.FunctionResponse(
                                name=tool_call.name,
                                id=tool_call.id,
                                response=tool_response_data
                            )
                        ]
                    )
                    await live_request_queue.send_tool_response(tool_response)

            # --- HANDLE TEXT RESPONSES (DEDUPLICATION) ---
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        text_chunk = part.text
                        
                        # Calculate the *new* text logic
                        # If chunk starts with what we already have, it's a cumulative update.
                        # Otherwise, it's a new distinct chunk.
                        if text_chunk.startswith(current_turn_text):
                            delta = text_chunk[len(current_turn_text):]
                        else:
                            delta = text_chunk
                        
                        if delta:
                            current_turn_text += delta
                            await websocket.send_json({
                                "role": "model",
                                "text": delta,
                                "partial": True
                            })

            # Signal end of turn
            if event.turn_complete:
                current_turn_text = "" # Reset for next turn
                await websocket.send_json({
                    "role": "model",
                    "text": "",
                    "partial": False 
                })
                
    except Exception as e:
        print(f"Error in agent_to_client: {e}")


async def client_to_agent_messaging(
    websocket: WebSocket, 
    live_request_queue: LiveRequestQueue
):
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if "text" in message:
                print(f"User: {message['text']}")
                content = types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=message["text"])]
                )
                live_request_queue.send_content(content=content)
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in client_to_agent: {e}")


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print(f"Client connected: {session_id}")

    live_events, live_request_queue = start_agent_session(session_id)

    agent_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events, live_request_queue)
    )
    client_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    done, pending = await asyncio.wait(
        [agent_task, client_task], 
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()
