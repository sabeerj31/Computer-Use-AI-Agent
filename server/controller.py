# server/controller.py

from google.adk.agents import LiveRequestQueue
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig
from google.genai import types
from google.genai.types import Modality

from server.sessions import create_unique_session, get_session_service
from agent.root_agent import root_agent


APP_NAME = "Live Computer Agent"


async def start_agent_session(raw_session_id: str, audio_enabled: bool):
    """
    Create a unique session and start an ADK Runner session.

    Returns:
        live_events      -> async iterator of events from Gemini
        live_request_q   -> queue for sending messages TO Gemini
        actual_session_id -> final unique session ID used
    """

    session_service = get_session_service()

    # Create a unique session ID (avoids "session already exists" errors)
    session, actual_session_id = await create_unique_session(
        APP_NAME, raw_session_id, raw_session_id
    )

    # Runner created with your root_agent + session store
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    # ✓ AUDIO MODE
    if audio_enabled:
        speech_config = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Zephyr"
                )
            )
        )

        run_config = RunConfig(
            response_modalities=[Modality.AUDIO],
            speech_config=speech_config,
            output_audio_transcription={},  # also returns text transcripts
        )

    # ✓ TEXT MODE
    else:
        run_config = RunConfig(
            response_modalities=[Modality.TEXT]
        )

    # Queue for sending user text/audio to Gemini
    live_request_queue = LiveRequestQueue()

    # Start streaming interaction
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )

    return live_events, live_request_queue, actual_session_id
