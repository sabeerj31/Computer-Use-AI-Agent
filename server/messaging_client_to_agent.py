import json
import base64
from google.genai import types


async def client_to_agent(websocket, queue):
    while True:
        raw = await websocket.receive_text()
        msg = json.loads(raw)

        if msg["mime_type"] == "text/plain":
            content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=msg["data"])]
            )
            queue.send_content(content)

        elif msg["mime_type"] == "audio/pcm":
            audio = base64.b64decode(msg["data"])
            queue.send_realtime(types.Blob(
                mime_type="audio/pcm",
                data=audio
            ))
