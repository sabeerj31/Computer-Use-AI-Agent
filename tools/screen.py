# screen.py
import io
from PIL import Image, ImageDraw
import pyautogui

def capture_screen(max_dimension: int = 1024, grid_step: int = 100):
    """
    Capture the screen, optionally resize to max_dimension (largest side),
    overlay a simple coordinate grid and return JPEG bytes.
    """
    try:
        screenshot = pyautogui.screenshot()
        width, height = screenshot.size

        # Resize while keeping aspect ratio if larger than max_dimension
        if max_dimension and (width > max_dimension or height > max_dimension):
            if width >= height:
                scale = max_dimension / float(width)
            else:
                scale = max_dimension / float(height)
            new_w = int(width * scale)
            new_h = int(height * scale)
            screenshot = screenshot.resize((new_w, new_h), Image.Resampling.LANCZOS)
            width, height = screenshot.size

        # Draw lightweight grid (red labels)
        draw = ImageDraw.Draw(screenshot)
        try:
            for x in range(0, width, grid_step):
                draw.line([(x, 0), (x, height)], fill=(200, 20, 20), width=1)
                draw.text((x + 2, 2), str(x), fill=(200, 20, 20))
            for y in range(0, height, grid_step):
                draw.line([(0, y), (width, y)], fill=(200, 20, 20), width=1)
                draw.text((2, y + 2), str(y), fill=(200, 20, 20))
        except Exception:
            # if text/font isn't available, ignore labels
            pass

        buf = io.BytesIO()
        screenshot.save(buf, format="JPEG", quality=70)
        data = buf.getvalue()
        if len(data) < 50:
            return {"status": "error", "message": "Captured image empty"}
        return {"status": "success", "screenshot": data, "width": width, "height": height}
    except Exception as e:
        return {"status": "error", "message": str(e)}
