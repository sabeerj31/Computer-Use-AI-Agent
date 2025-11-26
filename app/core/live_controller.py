import asyncio
from google.adk.runners import Runner
from google.genai import types
from app.computer.agent import root_agent
from app.core.sessions import session_service, create_session, USER_ID, SESSION_ID, APP_NAME
from app.computer.tools.screen import capture_screen as capture_screen_tool
from app.computer.tools import control

class LiveController:
    """
    Manages the live interaction with the computer vision agent.
    """
    def __init__(self):
        self.runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )

    async def run(self):
        """
        Starts the main loop for the agent.
        """
        await create_session()
        print("\n💬 Ready for commands! (Type 'exit' to quit)")
        print("   Try: 'Open notepad and write hello world'")

        while True:
            try:
                user_input = await asyncio.to_thread(input, "\nUser: ")
                if user_input.lower() in ["exit", "quit"]:
                    break

                # Start the agent run process
                await self.process_user_command(user_input)

            except Exception as e:
                print(f"\n❌ An error occurred: {e}")

    async def process_user_command(self, user_input: str):
        """
        Processes a single user command.
        """
        print("🤖 Agent is thinking...", end="", flush=True)

        # Initial screenshot
        screenshot_result = capture_screen_tool()
        if screenshot_result["status"] == "error":
            print(f"\nError taking screenshot: {screenshot_result['message']}")
            return

        message = types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_input),
                types.Part.from_data(
                    data=screenshot_result["screenshot"],
                    mime_type="image/png"
                ),
            ],
        )

        iterator = self.runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message)

        is_running = True
        while is_running:
            tool_called = False
            async for event in iterator:
                if hasattr(event, 'tool_calls') and event.tool_calls:
                    print(f"\n   🛠️  Calling Tool: {event.tool_calls[0].name}")
                    await self.handle_tool_call(event.tool_calls[0])
                    tool_called = True

                if event.is_final_response() and event.content:
                    response_text = event.content.parts[0].text
                    print(f"\n\n✨ Agent: {response_text}")

            if tool_called:
                # After a tool is called, capture the screen again and continue
                screenshot_result = capture_screen_tool()
                if screenshot_result["status"] == "error":
                    print(f"\nError taking screenshot: {screenshot_result['message']}")
                    is_running = False
                    continue

                # We don't need to provide the text again, just the new image
                message = types.Content(
                    role="user",
                    parts=[
                        types.Part.from_data(
                            data=screenshot_result["screenshot"],
                            mime_type="image/png"
                        ),
                    ],
                )
                iterator = self.runner.continue_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message)
            else:
                is_running = False


    async def handle_tool_call(self, tool_call):
        """
        Executes a tool call.
        """
        tool_name = tool_call.name
        tool_args = tool_call.args

        tool_functions = {
            "type_text": control.type_text,
            "press_key": control.press_key,
            "hotkey": control.hotkey,
            "click_mouse": control.click_mouse,
            "scroll": control.scroll,
            "capture_screen": capture_screen_tool,
        }

        if tool_name in tool_functions:
            result = tool_functions[tool_name](**tool_args)
            print(f"   Tool Result: {result}")
        else:
            print(f"   Unknown tool: {tool_name}")
