import pyautogui
from PIL import Image
import io

def capture_screen() -> dict:
    """
    Captures the current screen and returns it as a dictionary containing the image bytes.
    Returns JPEG format which is optimized for streaming.
    """
    try:
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        # Use JPEG for "video-like" streaming input
        screenshot.save(img_byte_arr, format='JPEG', quality=80)
        img_byte_arr = img_byte_arr.getvalue()
        
        # Sanity check for empty or black screens
        if len(img_byte_arr) < 100:
            return {"status": "error", "message": "Screenshot capture failed (empty data)."}
            
        return {"status": "success", "screenshot": img_byte_arr}
    except Exception as e:
        return {"status": "error", "message": str(e)}
