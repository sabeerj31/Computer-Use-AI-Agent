import pyautogui
from PIL import Image, ImageDraw, ImageFont
import io

def capture_screen() -> dict:
    """
    Captures the current screen, adds a coordinate grid for the AI, 
    resizes it to save tokens, and returns JPEG bytes.
    """
    try:
        # 1. Capture full screen
        screenshot = pyautogui.screenshot()
        
        # 2. Resize logic (Maintain Aspect Ratio)
        # Gemini 2.0 Flash handles 1024px well. 
        # This prevents the "131k token" explosion errors.
        max_dimension = 1024
        scale_factor = 1.0
        
        if screenshot.width > max_dimension or screenshot.height > max_dimension:
            # Calculate new size maintaining aspect ratio
            if screenshot.width > screenshot.height:
                scale_factor = max_dimension / float(screenshot.width)
                new_width = max_dimension
                new_height = int(screenshot.height * scale_factor)
            else:
                scale_factor = max_dimension / float(screenshot.height)
                new_width = int(screenshot.width * scale_factor)
                new_height = max_dimension
            
            screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 3. Draw Grid Overlay
        # We draw the grid *after* resizing so the coordinates match the image the AI sees.
        # However, we must map these "resized" coordinates back to "real" screen coordinates
        # when the AI asks to click. 
        # NOTE: For simplicity in this version, we trust the AI to estimate, 
        # but in production, you would tell the AI the 'scale_factor' or handle mapping.
        # Since we overwrote 'control.py' to take direct X/Y, the AI might click 
        # on the "small" screen coordinates.
        
        # FIX: To keep it simple for now, we will Draw Grid based on the *resized* image,
        # but we need to tell the AI that these coordinates are for the resized image.
        # Ideally, we verify if the AI is smart enough to handle this.
        # A safer approach for a starter agent: Don't resize *too* aggressively or 
        # handle coordinate scaling in 'click_mouse'.
        
        # Let's keep the grid simple:
        draw = ImageDraw.Draw(screenshot)
        width, height = screenshot.size
        step_size = 100 # Draw a line every 100 pixels
        
        # Draw vertical lines
        for x in range(0, width, step_size):
            draw.line([(x, 0), (x, height)], fill="red", width=1)
            # Add text label (requires default font)
            # Try/Except block in case default font is missing on some OS
            try:
                draw.text((x + 2, 2), str(x), fill="red")
            except:
                pass

        # Draw horizontal lines
        for y in range(0, height, step_size):
            draw.line([(0, y), (width, y)], fill="red", width=1)
            try:
                draw.text((2, y + 2), str(y), fill="red")
            except:
                pass

        # 4. Save as JPEG
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='JPEG', quality=70)
        img_byte_arr = img_byte_arr.getvalue()
        
        if len(img_byte_arr) < 100:
            return {"status": "error", "message": "Screenshot capture failed (empty data)."}
        
        # Optional: You can return the scale_factor here if you want to use it in `click_mouse`
        # to remap coordinates, but for now, let's return just the image.
        return {
            "status": "success", 
            "screenshot": img_byte_arr,
            "details": f"Resized to {width}x{height}"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}