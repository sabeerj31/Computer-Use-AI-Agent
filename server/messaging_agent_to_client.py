import json
import base64
from google.genai import types
from google.adk.events.event import Event


async def agent_to_client(websocket, events):
    async for event in events:
        if event is None:
            continue

        # turn complete
        if event.turn_complete:
            await websocket.send_json({"turn_complete": True})
            continue

        part = event.content and event.content.parts and event.content.parts[0]
        if not isinstance(part, types.Part):
            continue

        # TEXT
        if part.text:
            await websocket.send_json({
                "mime_type": "text/plain",
                "data": part.text,
                "role": "model"
            })
            continue

        # AUDIO
        if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
            await websocket.send_json({
                "mime_type": "audio/pcm",
                "data": base64.b64encode(part.inline_data.data).decode(),
                "role": "model"
            })
