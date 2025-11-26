import pyautogui
import time

def type_text(text: str) -> dict:
    """
    Types the given text using the keyboard.

    Args:
        text (str): The text to type.

    Returns:
        dict: A dictionary with the status of the operation.
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
        key (str): The key to press (e.g., 'enter', 'esc').

    Returns:
        dict: A dictionary with the status of the operation.
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
        keys (list[str]): A list of keys to press simultaneously (e.g., ['ctrl', 'c']).

    Returns:
        dict: A dictionary with the status of the operation.
    """
    try:
        pyautogui.hotkey(*keys)
        return {"status": "success", "message": f"Pressed hotkey: {'+'.join(keys)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def click_mouse(x: int, y: int, button: str = 'left') -> dict:
    """
    Clicks the mouse at the specified coordinates.

    Args:
        x (int): The x-coordinate.
        y (int): The y-coordinate.
        button (str, optional): The mouse button to click ('left', 'right', 'middle'). Defaults to 'left'.

    Returns:
        dict: A dictionary with the status of the operation.
    """
    try:
        pyautogui.click(x, y, button=button)
        return {"status": "success", "message": f"Clicked mouse at ({x}, {y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def scroll(amount: int) -> dict:
    """
    Scrolls the mouse wheel.

    Args:
        amount (int): The amount to scroll. Positive for up, negative for down.

    Returns:
        dict: A dictionary with the status of the operation.
    """
    try:
        pyautogui.scroll(amount)
        return {"status": "success", "message": f"Scrolled by {amount}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
