# run.py
import asyncio
import json
import base64
from pathlib import Path
from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from controller import start_agent_session
from google.genai import types

app = FastAPI()
STATIC_DIR = Path("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


async def agent_to_client_messaging(websocket: WebSocket, live_events):
    """
    Convert agent events -> websocket messages (text or audio).
    """
    try:
        async for event in live_events:
            if event is None:
                continue

            # If turn complete / interrupted, notify
            if event.turn_complete:
                await websocket.send_text(json.dumps({"turn_complete": True}))
                continue

            # send tool notifications if present (optional)
            if hasattr(event, "tool_calls") and event.tool_calls:
                for tool_call in event.tool_calls:
                    await websocket.send_text(json.dumps({
                        "mime_type": "text/plain",
                        "data": f"Agent called tool: {tool_call.name}",
                        "role": "system"
                    }))

            if event.content and event.content.parts:
                for part in event.content.parts:
                    # TEXT part
                    if part.text:
                        await websocket.send_text(json.dumps({
                            "mime_type": "text/plain",
                            "data": part.text,
                            "role": "model"
                        }))

                    # AUDIO part (inline_data)
                    if getattr(part, "inline_data", None) and getattr(part.inline_data, "mime_type", "").startswith("audio/pcm"):
                        audio_bytes = part.inline_data.data
                        if audio_bytes:
                            await websocket.send_text(json.dumps({
                                "mime_type": "audio/pcm",
                                "data": base64.b64encode(audio_bytes).decode("ascii"),
                                "role": "model"
                            }))
    except Exception as e:
        print("agent_to_client error:", e)


async def client_to_agent_messaging(websocket: WebSocket, live_request_queue):
    """
    Convert websocket messages -> live_request_queue.
    Supports: text/plain and audio/pcm (base64).
    """
    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)
            mime_type = message.get("mime_type")
            data = message.get("data")
            role = message.get("role", "user")

            if mime_type == "text/plain":
                content = types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=data)]
                )
                live_request_queue.send_content(content=content)
                continue

            if mime_type == "audio/pcm":
                # when client sends audio, send as realtime blob (binary)
                decoded = base64.b64decode(data)
                live_request_queue.send_realtime(types.Blob(data=decoded, mime_type="audio/pcm"))
                continue

            # unknown type
            await websocket.send_text(json.dumps({"mime_type": "text/plain", "data": f"Unsupported MIME: {mime_type}", "role": "system"}))

    except Exception as e:
        print("client_to_agent error:", e)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, is_audio: str = Query("false")):
    await websocket.accept()
    audio_enabled = is_audio.lower() == "true"

    # start agent session (makes session id unique internally if needed)
    live_events, live_request_queue, actual_session_id = await start_agent_session(session_id, audio_enabled)

    # create tasks to shuttle messages both ways
    agent_task = asyncio.create_task(agent_to_client_messaging(websocket, live_events))
    client_task = asyncio.create_task(client_to_agent_messaging(websocket, live_request_queue))

    done, pending = await asyncio.wait([agent_task, client_task], return_when=asyncio.FIRST_COMPLETED)
    for p in pending:
        p.cancel()
    await websocket.close()
