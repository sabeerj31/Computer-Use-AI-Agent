# app/computer/tools/vision.py
import os
import io
import pyautogui
from PIL import Image
from google.genai import Client, types
from dotenv import load_dotenv

load_dotenv()

def analyze_screen(question: str = "Describe the visible content on the screen in detail.") -> dict:
    """
    Captures the current screen and asks a vision AI model to describe it or answer a question about it.
    Use this when you need to 'see' or know what is on the user's screen.
    
    Args:
        question: A specific question about the screen (e.g., "What error message is shown?", "Describe the layout").
                  Defaults to a general description.
    """
    try:
        # 1. Capture Screen
        screenshot = pyautogui.screenshot()
        
        # Resize if necessary to speed up upload/processing (optional, keeping it efficient)
        max_dimension = 1024
        if screenshot.width > max_dimension or screenshot.height > max_dimension:
            screenshot.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        # Convert to Bytes
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        png_bytes = img_byte_arr.getvalue()

        # 2. Initialize Client (Stateless call to vision model)
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return {"status": "error", "message": "GOOGLE_API_KEY not found in environment."}
        
        client = Client(api_key=api_key)

        # 3. Call the Vision Model (The "Image Agent")
        # We use the Flash model for speed
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=png_bytes, mime_type="image/png"),
                        types.Part.from_text(text=question)
                    ]
                )
            ]
        )
        
        # 4. Return the description
        return {
            "status": "success", 
            "description": response.text
        }

    except Exception as e:
        print(f"Vision tool error: {e}")
        return {"status": "error", "message": str(e)}
