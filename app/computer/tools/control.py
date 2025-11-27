import pyautogui
import time
import os
import shutil
import subprocess
import pygetwindow as gw
from pywinauto.application import Application
import win32gui
import win32con
import psutil
import pyperclip
import screen_brightness_control as sbc
from win10toast import ToastNotifier

pyautogui.FAILSAFE = True


# =============================
# KEYBOARD / MOUSE BASICS
# =============================

def type_text(text: str) -> dict:
    try:
        pyautogui.typewrite(text)
        return {"status": "success", "message": f"Typed: {text}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def type_human(text: str) -> dict:
    try:
        import random
        for c in text:
            pyautogui.typewrite(c)
            time.sleep(random.uniform(0.03, 0.12))
        return {"status": "success", "message": "Typed like a human"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def press_key(key: str) -> dict:
    try:
        pyautogui.press(key)
        return {"status": "success", "message": f"Pressed key: {key}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def hotkey(keys: list[str]) -> dict:
    try:
        pyautogui.hotkey(*keys)
        return {"status": "success", "message": f"Pressed hotkey: {'+'.join(keys)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def click_mouse(x: int, y: int, button: str) -> dict:
    try:
        pyautogui.click(x, y, button=button)
        return {"status": "success", "message": f"Clicked {button} at ({x},{y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def scroll(amount: int) -> dict:
    try:
        pyautogui.scroll(amount)
        return {"status": "success", "message": f"Scrolled by {amount}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def move_cursor_smooth(x: int, y: int, steps: int = 50) -> dict:
    try:
        cx, cy = pyautogui.position()
        for i in range(steps):
            nx = cx + (x - cx) * (i / steps)
            ny = cy + (y - cy) * (i / steps)
            pyautogui.moveTo(nx, ny)
        return {"status": "success", "message": "Cursor moved smoothly"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =============================
# WINDOW MANAGEMENT
# =============================

def list_windows() -> dict:
    try:
        titles = [w.title for w in gw.getAllWindows() if w.title.strip()]
        return {"status": "success", "windows": titles}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def window_exists(title: str) -> dict:
    try:
        exists = len(gw.getWindowsWithTitle(title)) > 0
        return {"status": "success", "exists": exists}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _get_window(title: str):
    wins = gw.getWindowsWithTitle(title)
    if not wins:
        raise Exception(f"No window matches '{title}'")
    return wins[0]


def focus_window(title: str) -> dict:
    try:
        win = _get_window(title)
        win.activate()
        time.sleep(0.2)
        return {"status": "success", "message": f"Focused {win.title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def minimize_window(title: str) -> dict:
    try:
        win = _get_window(title)
        win.minimize()
        return {"status": "success", "message": f"Minimized {win.title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def maximize_window(title: str) -> dict:
    try:
        win = _get_window(title)
        win.maximize()
        return {"status": "success", "message": f"Maximized {win.title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def restore_window(title: str) -> dict:
    try:
        win = _get_window(title)
        win.restore()
        return {"status": "success", "message": f"Restored {win.title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def move_window(title: str, x: int, y: int) -> dict:
    try:
        win = _get_window(title)
        win.moveTo(x, y)
        return {"status": "success", "message": f"Moved {win.title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def resize_window(title: str, width: int, height: int) -> dict:
    try:
        win = _get_window(title)
        win.resizeTo(width, height)
        return {"status": "success", "message": f"Resized {win.title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def close_window(title: str) -> dict:
    try:
        win = _get_window(title)
        hwnd = win._hWnd
        app = Application().connect(handle=hwnd)
        app.window(handle=hwnd).close()
        return {"status": "success", "message": f"Closed {win.title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Snapping
def snap_left(title: str) -> dict:
    try:
        focus_window(title)
        pyautogui.hotkey('win', 'left')
        return {"status": "success", "message": "Snapped left"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def snap_right(title: str) -> dict:
    try:
        focus_window(title)
        pyautogui.hotkey('win', 'right')
        return {"status": "success", "message": "Snapped right"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def snap_top(title: str) -> dict:
    try:
        focus_window(title)
        pyautogui.hotkey('win', 'up')
        return {"status": "success", "message": "Snapped top"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def snap_bottom(title: str) -> dict:
    try:
        focus_window(title)
        pyautogui.hotkey('win', 'down')
        return {"status": "success", "message": "Snapped bottom"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def tile_two_windows(left_title: str, right_title: str) -> dict:
    try:
        snap_left(left_title)
        time.sleep(0.2)
        snap_right(right_title)
        return {"status": "success", "message": "Tiled two windows"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def tile_four_windows(a: str, b: str, c: str, d: str) -> dict:
    try:
        snap_left(a); pyautogui.hotkey('win', 'up')
        snap_left(b); pyautogui.hotkey('win', 'down')
        snap_right(c); pyautogui.hotkey('win', 'up')
        snap_right(d); pyautogui.hotkey('win', 'down')
        return {"status": "success", "message": "Tiled four windows"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Desktop control
def unfocus_all() -> dict:
    try:
        pyautogui.hotkey('win', 'd')
        return {"status": "success", "message": "Desktop shown"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def minimize_all() -> dict:
    try:
        pyautogui.hotkey('win', 'm')
        return {"status": "success", "message": "All minimized"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def restore_all() -> dict:
    try:
        pyautogui.hotkey('win', 'shift', 'm')
        return {"status": "success", "message": "Restored all windows"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_active_window() -> dict:
    try:
        hwnd = win32gui.GetForegroundWindow()
        return {"status": "success", "title": win32gui.GetWindowText(hwnd)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_window_info(title: str) -> dict:
    try:
        win = _get_window(title)
        return {
            "status": "success",
            "x": win.left,
            "y": win.top,
            "width": win.width,
            "height": win.height
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =============================
# VOLUME CONTROL
# =============================

def set_volume(level: int) -> dict:
    try:
        level = max(0, min(100, level))
        for _ in range(50):
            pyautogui.press("volumedown")
        for _ in range(level // 2):
            pyautogui.press("volumeup")
        return {"status": "success", "message": f"Volume set to {level}%"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def mute() -> dict:
    try:
        pyautogui.press("volumemute")
        return {"status": "success", "message": "Muted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def unmute() -> dict:
    try:
        pyautogui.press("volumemute")
        return {"status": "success", "message": "Unmuted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def volume_up() -> dict:
    try:
        pyautogui.press("volumeup")
        return {"status": "success", "message": "Volume up"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def volume_down() -> dict:
    try:
        pyautogui.press("volumedown")
        return {"status": "success", "message": "Volume down"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =============================
# BRIGHTNESS CONTROL
# =============================

def set_brightness(level: int) -> dict:
    try:
        sbc.set_brightness(level)
        return {"status": "success", "message": f"Brightness set to {level}%"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def increase_brightness(amount: int = 10) -> dict:
    try:
        current = sbc.get_brightness()[0]
        sbc.set_brightness(min(100, current + amount))
        return {"status": "success", "message": "Brightness increased"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def decrease_brightness(amount: int = 10) -> dict:
    try:
        current = sbc.get_brightness()[0]
        sbc.set_brightness(max(0, current - amount))
        return {"status": "success", "message": "Brightness decreased"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =============================
# CLIPBOARD
# =============================

def copy_text() -> dict:
    try:
        hotkey(["ctrl", "c"])
        content = pyperclip.paste()
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def paste_text() -> dict:
    try:
        hotkey(["ctrl", "v"])
        return {"status": "success", "message": "Pasted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =============================
# FILE TOOLS (DESTRUCTIVE INCLUDED)
# =============================

def list_folder(path: str) -> dict:
    try:
        return {"status": "success", "items": os.listdir(path)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_folder(path: str) -> dict:
    try:
        os.makedirs(path, exist_ok=True)
        return {"status": "success", "message": "Folder created"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_file(path: str) -> dict:
    try:
        os.remove(path)
        return {"status": "success", "message": "File deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_folder(path: str) -> dict:
    try:
        shutil.rmtree(path)
        return {"status": "success", "message": "Folder deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def rename_file(old: str, new: str) -> dict:
    try:
        os.rename(old, new)
        return {"status": "success", "message": "File renamed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def move_file(src: str, dst: str) -> dict:
    try:
        shutil.move(src, dst)
        return {"status": "success", "message": "File moved"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def read_file(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {"status": "success", "content": f.read()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def write_file(path: str, content: str) -> dict:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "message": "File written"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =============================
# MEDIA CONTROL
# =============================

def play_pause() -> dict:
    try:
        pyautogui.press("playpause")
        return {"status": "success", "message": "Play/Pause"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def next_track() -> dict:
    try:
        pyautogui.press("nexttrack")
        return {"status": "success", "message": "Next track"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def prev_track() -> dict:
    try:
        pyautogui.press("prevtrack")
        return {"status": "success", "message": "Previous track"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =============================
# SYSTEM INFO
# =============================

def get_cpu_usage() -> dict:
    try:
        return {"status": "success", "cpu": psutil.cpu_percent(interval=1)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_ram_usage() -> dict:
    try:
        ram = psutil.virtual_memory()
        return {"status": "success", "ram_percent": ram.percent}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_battery() -> dict:
    try:
        batt = psutil.sensors_battery()
        return {
            "status": "success",
            "percent": batt.percent,
            "plugged": batt.power_plugged
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_uptime() -> dict:
    try:
        uptime = time.time() - psutil.boot_time()
        return {"status": "success", "uptime_seconds": uptime}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_processes() -> dict:
    try:
        procs = [p.info for p in psutil.process_iter(['pid', 'name'])]
        return {"status": "success", "processes": procs}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def kill_process(name: str) -> dict:
    try:
        for p in psutil.process_iter(['name']):
            if name.lower() in p.info['name'].lower():
                p.kill()
        return {"status": "success", "message": f"Killed processes matching {name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
