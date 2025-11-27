# session.py
from google.adk.sessions.in_memory_session_service import InMemorySessionService

APP_NAME = "computer_vision_app"

# Shared session service for the whole backend
session_service = InMemorySessionService()

async def create_session(user_id: str, session_id: str):
    """
    Create and return a new ADK session.
    """
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
    return session
