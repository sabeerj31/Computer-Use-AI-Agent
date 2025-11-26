import pyautogui
import time

# Safety: Fail-safe to abort if mouse moves to top-left corner
pyautogui.FAILSAFE = True

def type_text(text: str) -> dict:
    """
    Types the given text using the keyboard.

    Args:
        text: The text to type.
    """
    try:
        pyautogui.typewrite(text)
        return {"status": "success", "message": f"Typed: {text}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def press_key(key: str) -> dict:
    """
    Presses a single key on the keyboard.

    Args:
        key: The key to press (e.g., 'enter', 'esc', 'backspace', 'win').
    """
    try:
        pyautogui.press(key)
        return {"status": "success", "message": f"Pressed key: {key}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def hotkey(keys: list[str]) -> dict:
    """
    Presses a combination of keys (hotkey).

    Args:
        keys: A list of keys to press simultaneously (e.g., ['ctrl', 'c']).
    """
    try:
        pyautogui.hotkey(*keys)
        return {"status": "success", "message": f"Pressed hotkey: {'+'.join(keys)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def click_mouse(x: int, y: int, button: str) -> dict:
    """
    Clicks the mouse at the specified coordinates.

    Args:
        x: The x-coordinate on the screen/grid.
        y: The y-coordinate on the screen/grid.
        button: The mouse button to click. Must be 'left', 'right', or 'middle'.
    """
    try:
        # Move first, then click. This is more human-like and reliable.
        pyautogui.click(x, y, button=button)
        return {"status": "success", "message": f"Clicked {button} at ({x}, {y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def scroll(amount: int) -> dict:
    """
    Scrolls the mouse wheel.

    Args:
        amount: The amount to scroll. Positive for up, negative for down. (e.g. 500 or -500)
    """
    try:
        pyautogui.scroll(amount)
        return {"status": "success", "message": f"Scrolled by {amount}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}