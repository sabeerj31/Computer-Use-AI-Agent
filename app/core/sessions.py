from google.adk.sessions.in_memory_session_service import InMemorySessionService

APP_NAME = "computer_vision_app"
USER_ID = "client_user"
SESSION_ID = "session_01"

session_service = InMemorySessionService()

async def create_session():
    """
    Creates a new session for the agent.
    """
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
