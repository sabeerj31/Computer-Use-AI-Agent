from google.adk.agents import Agent
from tools.control import type_text, press_key, click_mouse, hotkey, scroll
from tools.screen import capture_screen

SYSTEM_PROMPT = """
You are a computer control agent with vision.
To see the screen, call capture_screen.
"""

root_agent = Agent(
    name="computer_agent",
    model="gemini-2.0-flash-live-001",
    instruction=SYSTEM_PROMPT,
    tools=[
        type_text,
        press_key,
        click_mouse,
        hotkey,
        scroll,
        capture_screen
    ]
)
