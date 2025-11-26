import asyncio
import os
import sys
from dotenv import load_dotenv
from app.core.live_controller import LiveController

# Load environment variables from .env file
load_dotenv()

async def main():
    """
    Main entry point for the CLI version of the Computer Vision Agent.
    """
    print("-----------------------------------------")
    print("🖥️  Gemini ADK Computer Agent Initialized")
    print("-----------------------------------------")

    # 1. Validate API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found.")
        print("   Please ensure the file is named '.env' and contains GOOGLE_API_KEY=AIza...")
        sys.exit(1)

    # 2. Initialize the Controller
    # This controller handles the "capture -> send to Gemini -> execute tool" loop
    controller = LiveController()

    # 3. Start the Event Loop
    try:
        await controller.run()
    except KeyboardInterrupt:
        print("\n\n👋 Agent stopped by user. Exiting...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        # Fix for Windows specific asyncio loop policy if needed
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())
