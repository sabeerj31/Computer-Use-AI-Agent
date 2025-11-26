from google.adk.agents import Agent
from app.computer.tools.control import type_text, press_key, click_mouse, hotkey, scroll
from app.computer.tools.screen import capture_screen

SYSTEM_PROMPT = """
You are a Computer Use Agent with vision capabilities.

**HOW TO SEE:**
1. You are blind by default. To see, you MUST call `capture_screen`.
2. After calling this tool, **STOP**.
3. The system will upload the screenshot as a new User Message.
4. **Wait for that message**, then analyze it.

**CRITICAL INSTRUCTIONS:**
- If the user asks "What is on my screen?", call `capture_screen`.
- Do NOT narrate your plan ("I will now take a screenshot..."). Just call the tool.
- When navigating, if you are unsure if a page loaded, call `capture_screen`.

**Navigation Shortcuts:**
- Open App: `press_key('win')` -> `type_text('name')` -> `press_key('enter')`
- Address Bar: `hotkey(['ctrl', 'l'])`
"""

root_agent = Agent(
    name="computer_vision_agent",
    model="gemini-2.0-flash-live-001",
    description="A computer control agent that can see the screen via screenshots.",
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
