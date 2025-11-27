from google.adk.agents import Agent
from app.computer.tools.control import *
from app.computer.tools.screen import capture_screen
from google.adk.tools import google_search


SYSTEM_PROMPT = """
You are an advanced Computer Use AI Agent with FULL CONTROL over:
- Windows management
- Keyboard & mouse
- Volume & brightness
- Clipboard
- Filesystem
- Media
- System Info
- Human typing
- Cursor control
- Vision (screenshots)

RULES:
1. You are blind by default — call capture_screen() when needed.
2. After calling capture_screen(), STOP the turn.
3. Never ask for coordinates. Compute them yourself.
4. When user says “switch to Chrome”, use focus_window("Chrome").
5. Only open new window if user explicitly says “open new”.
6. Use natural window arrangement:
   - "left side" → snap_left()
   - "right side" → snap_right()
   - "top half" → snap_top()
   - "bottom half" → snap_bottom()
7. For typing text realistically use type_human().
8. For system info use psutil-based tools.
9. For file operations use read_file(), write_file(), delete_file(), move_file(), etc.

Be helpful, precise, and NEVER reveal chain-of-thought.

GENERAL RULES

Never ask the user for coordinates.
Never reveal chain-of-thought.
Always use tools when performing actions.
Use google_search for questions requiring external information.
Speak naturally and helpfully when chatting.
"""


root_agent = Agent(
    name="computer_vision_agent",
    model="gemini-2.0-flash-live-001",
    description="Full-power Computer Control Agent",
    instruction=SYSTEM_PROMPT,
    tools=[

        # Vision
        capture_screen,

        # Keyboard / mouse
        type_text, type_human, press_key, click_mouse, hotkey,
        scroll, move_cursor_smooth,

        # Window control
        list_windows, window_exists, focus_window, minimize_window,
        maximize_window, restore_window, move_window, resize_window,
        close_window, get_active_window, get_window_info,

        # Snapping / tiling
        snap_left, snap_right, snap_top, snap_bottom,
        tile_two_windows, tile_four_windows,

        # Desktop & system windows
        unfocus_all, minimize_all, restore_all,

        # Volume control
        set_volume, mute, unmute, volume_up, volume_down,

        # Brightness
        set_brightness, increase_brightness, decrease_brightness,

        # Clipboard
        copy_text, paste_text,

        # File tools
        list_folder, create_folder, delete_file, delete_folder,
        rename_file, move_file, read_file, write_file,

        # Media
        play_pause, next_track, prev_track,

        # System info
        get_cpu_usage, get_ram_usage, get_battery,
        get_uptime, list_processes, kill_process,

        # Search
        google_search,
    ]
)
