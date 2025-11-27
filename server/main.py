import asyncio
import json
import base64
from fastapi import FastAPI, WebSocket, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from agent.root_agent import root_agent

app = FastAPI()
session_service = InMemorySessionService()
app.mount("/static", StaticFiles(directory="static"), name="static")


def start_session(session_id: str, audio_enabled: bool):
    """Create session + runner with TEXT / AUDIO config"""

    session = session_service.create_session(
        app_name="Live Computer Agent",
        user_id=session_id,
        session_id=session_id
    )

    runner = Runner(
        app_name="Live Computer Agent",
        agent=root_agent,
        session_service=session_service
    )

    # ---------- AUDIO ENABLED ----------
    if audio_enabled:
        speech_cfg = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Zephyr"
                )
            )
        )
        config = RunConfig(
            response_modalities=["AUDIO"],
            speech_config=speech_cfg,
            output_audio_transcription={}
        )
    else:
        # ---------- TEXT ONLY ----------
        config = RunConfig(
            response_modalities=["TEXT"]
        )

    queue = LiveRequestQueue()
    events = runner.run_live(
        session=session,
        live_request_queue=queue,
        run_config=config
    )
    return events, queue
