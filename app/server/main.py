import asyncio
import json
import os
import base64

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
from google.genai.types import Modality

import warnings

# Agent & Tools
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


# -----------------------------------------------------------
# FIXED: async session creator
# -----------------------------------------------------------
async def start_agent_session(session_id: str):
    """Starts the ADK Live Runner session."""

    # FIX -> MUST await session creation
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )

    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

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


# -----------------------------------------------------------
# AGENT ➜ CLIENT
# -----------------------------------------------------------
async def agent_to_client_messaging(
    websocket: WebSocket,
    live_events: AsyncIterable[Event | None],
    live_request_queue: LiveRequestQueue
):
    current_turn_text = ""

    try:
        async for event in live_events:
            if event is None:
                continue

            # ============================================================
            # TOOL CALLS
            # ============================================================
            if hasattr(event, "tool_calls") and event.tool_calls:
                for tool_call in event.tool_calls:
                    print(f"🛠️ Agent calling tool: {tool_call.name}")

                    tool_response_data = {}

                    # -----------------------------
                    # SCREEN CAPTURE
                    # -----------------------------
                    if tool_call.name == "capture_screen":
                        result = capture_screen()
                        if result["status"] == "success":
                            # Notify frontend
                            await websocket.send_json({
                                "mime_type": "text/plain",
                                "data": "📸 Screenshot captured.",
                                "role": "system"
                            })

                            img_bytes = result["screenshot"]

                            # Send screenshot to agent as user message
                            image_content = types.Content(
                                role="user",
                                parts=[
                                    types.Part.from_data(
                                        data=img_bytes,
                                        mime_type="image/jpeg"
                                    ),
                                    types.Part.from_text(
                                        text="[SYSTEM] Screenshot received."
                                    )
                                ]
                            )
                            live_request_queue.send_content(content=image_content)
                            tool_response_data = {"result": "Image uploaded"}
                        else:
                            tool_response_data = {"error": result.get("message", "Unknown error")}

                    # -----------------------------
                    # CONTROL TOOLS (click, type, etc.)
                    # -----------------------------
                    elif hasattr(control, tool_call.name):
                        func = getattr(control, tool_call.name)
                        try:
                            raw_result = func(**tool_call.args)

                            tool_response_data = (
                                raw_result if isinstance(raw_result, dict)
                                else {"result": str(raw_result)}
                            )

                            # ⭐ IMPORTANT FIX:
                            # Notify frontend that a tool was executed.
                            await websocket.send_json({
                                "mime_type": "text/plain",
                                "data": f"⚡ Executed tool: {tool_call.name}",
                                "role": "system"
                            })

                            if tool_call.name in ["press_key", "click_mouse"]:
                                await asyncio.sleep(0.5)

                        except Exception as e:
                            print(f"❌ Error executing tool: {e}")
                            tool_response_data = {"error": str(e)}

                    else:
                        tool_response_data = {"error": f"Unknown tool: {tool_call.name}"}

                    # -----------------------------
                    # SEND TOOL RESPONSE BACK TO AGENT
                    # -----------------------------
                    tool_response = types.LiveClientToolResponse(
                        function_responses=[
                            types.FunctionResponse(
                                name=tool_call.name,
                                id=tool_call.id,
                                response=tool_response_data,
                            )
                        ]
                    )
                    live_request_queue.send_tool_response(tool_response)

            # ============================================================
            # TEXT FROM AGENT
            # ============================================================
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        chunk = part.text

                        # dedupe logic
                        if chunk.startswith(current_turn_text):
                            delta = chunk[len(current_turn_text):]
                        else:
                            delta = chunk

                        if delta:
                            current_turn_text += delta

                            await websocket.send_json({
                                "mime_type": "text/plain",
                                "data": delta,
                                "role": "model"
                            })

            # ============================================================
            # TURN COMPLETE
            # ============================================================
            if event.turn_complete:
                current_turn_text = ""
                await websocket.send_json({
                    "mime_type": "text/plain",
                    "data": "",
                    "role": "model",
                    "turn_complete": True
                })

    except Exception as e:
        print(f"Error in agent_to_client: {e}")



# -----------------------------------------------------------
# CLIENT ➜ AGENT
# -----------------------------------------------------------
async def client_to_agent_messaging(
    websocket: WebSocket,
    live_request_queue: LiveRequestQueue
):
    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)

            mime_type = message.get("mime_type")
            data = message.get("data")
            role = message.get("role", "user")

            # -------------------------------
            # TEXT MESSAGE
            # -------------------------------
            if mime_type == "text/plain":
                print(f"🟦 User (text): {data}")

                content = types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=data)]
                )

                # NOT ASYNC — Do NOT await
                live_request_queue.send_content(content=content)
                continue

            # -------------------------------
            # AUDIO MESSAGE
            # -------------------------------
            if mime_type == "audio/pcm":
                audio_bytes = base64.b64decode(data)
                print(f"🎤 User (audio/pcm): {len(audio_bytes)} bytes")

                content = types.Content(
                    role="user",
                    parts=[
                        types.Part.from_data(
                            data=audio_bytes,
                            mime_type="audio/pcm"
                        )
                    ]
                )

                # NOT ASYNC — Do NOT await
                live_request_queue.send_content(content=content)
                continue

            print("⚠ Unsupported MIME type:", message)

    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:
        print("❌ Error in client_to_agent:", e)



# -----------------------------------------------------------
# ROUTES
# -----------------------------------------------------------
@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print(f"Client connected: {session_id}")

    # FIX: await session startup
    live_events, live_request_queue = await start_agent_session(session_id)

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
