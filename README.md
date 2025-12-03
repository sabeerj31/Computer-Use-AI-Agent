# Computer-Use-AI-Agent – AI-Powered Computer Control Agent (Concierge Agent)
### *An AI agent that can see your screen, understand UI elements, click, type, control your system, and even talk to you—built with Google ADK.*

---

## Overview

**Computer-Use-AI-Agent** is a multi-agent AI system that provides **full OS-level control** using natural language or **voice commands**.  
It uses:

- **Vision models** to “see” your computer screen  
- **System control tools** to click, type, scroll, open apps, manage windows  
- **Voice input + AI-generated voice output**  
- **Google ADK** to run the agent live in a browser  
- A **multi-agent architecture** combining perception + action + voice  

This project was built as part of the **Kaggle 5-Day AI Agents Intensive**, and showcases how agents can act as a **personal concierge assistant** for everyday computer tasks.

---

## Key Features

### Screen Understanding
- Takes live screenshots  
- Uses Gemini Vision to analyze UI  
- Detects buttons, text fields, menus, popups, and layout  

### Autonomous Computer Control
The agent can:
- Move and click the mouse  
- Type like a human  
- Press hotkeys  
- Scroll pages  
- Open apps  
- Manage windows (focus, minimize, maximize, snap)  
- Control volume and brightness  
- Read/write files  

### Full Voice Mode  
- Speak to the agent  
- Realtime streaming audio (PCM)  
- AI-generated voice responses (“Puck”)  
- Fully browser-based  
- Hands-free control  

### Multi-Agent Architecture  
- **Interactive Orchestrator Agent**  
- **Vision Agent**  
- **System Control Agent**  
- **Voice Interface Agent**  
- **Task Validator Agent**

### Modern Web UI  
Built using:
- HTML  
- CSS  
- JavaScript  
- WebSockets  
- Audio Worklets  

---

## Architecture

Computer-Use-AI-Agent uses the **Google Agent Development Kit (ADK)** to run a live, tool-augmented conversational agent with full system control.

### 1. Main Orchestrator Agent
Responsible for:
- Planning tasks  
- Calling tools  
- Verifying results with screen analysis  
- Managing multi-step workflows  

### 2. Vision Agent (`analyze_screen`)
- Captures screenshot  
- Sends to Gemini Vision model  
- Returns detailed UI understanding  

### 3. System Control Tools (`control.py`)
Provide:
- Keyboard automation  
- Mouse control  
- Window management  
- File operations  
- System information  
- Chrome automation  
- Volume & brightness control  

### 4. Voice Pipeline
- Browser microphone → PCM stream → WebSocket  
- ADK Live Session receives audio  
- Gemini produces streaming PCM audio  
- Played using AudioWorklets  

### 5. FastAPI Backend
- WebSocket endpoint  
- Manages live agent sessions  
- Tool call execution  
- Event streaming  

---

## File Structure

```
app/
 ├── server/
 │    ├── main.py
 │    ├── __init__.py
 │    └── __pycache__/
 └── computer/
      ├── agent.py
      ├── __init__.py
      ├── tools/
      │    ├── control.py
      │    ├── vision.py
      │    ├── __init__.py
      │    └── __pycache__/
      └── __pycache__/
static/
 ├── index.html
 └── js/
      ├── app.js
      ├── audio-player.js
      ├── audio-recorder.js
      ├── pcm-player-processor.js
      └── pcm-recorder-processor.js
requirements.txt
```
---

## Tech Stack

VisionDesk is powered by a combination of AI tools, automation libraries, and modern web technologies.


### AI & Agent Framework
- **Google Agent Development Kit (ADK)** – Live agent orchestration, tool calling, streaming execution  
- **Gemini 2.0 Flash / Flash Live** – Vision reasoning, natural language, and voice output  
- **Google GenAI Python SDK** – Multimodal model integration

---

### Vision & Perception
- **PyAutoGUI** – Screenshot capture + basic automation  
- **Pillow (PIL)** – Image processing before sending to Gemini  
- **Gemini Vision API** – Screen understanding, UI interpretation, layout detection

---

### Desktop Automation
- **PyAutoGUI** – Keyboard & mouse control  
- **PyGetWindow** – Window lookup & focus  
- **PyWin32** – Windows-level interactions  
- **PyCaw** – System volume control  
- **PyWinauto** – Advanced window operations  
- **Screen Brightness Control** – Brightness adjustments  
- **Psutil** – CPU, RAM, process, and battery info  
- **Pyperclip** – Clipboard read/write

---

### Backend
- **Python 3.11+**  
- **FastAPI** – API + WebSocket server  
- **Uvicorn** – ASGI server  
- **WebSockets** – Live streaming of text & audio  
- **InMemorySessionService (ADK)** – Session/state management

---

### Audio Pipeline
- **Web Audio API**  
- **AudioWorklets** (PCM recorder + PCM player)  
- **Browser microphone input → PCM stream → Agent → PCM output → Playback**  

---

### Frontend
- **HTML5 / CSS3 / JavaScript**  
- **Custom Chat UI**  
- **Real-time typing indicator**  
- **Voice mode (enable/disable)**  
- **Auto-scrolling message feed**  
- **Live status indicators (connected, recording)**

---

### Utilities & Others
- **dotenv** – Environment variable loader  
- **Pydantic** – Data and type validation  
- **Subprocess / OS** – Launch apps, manage files  
- **Google Search Tool (ADK)** – External information retrieval

---

## Installation

### 1. Clone the repository
```sh
git clone https://github.com/sabeerj31/Computer-Use-AI-Agent
cd Computer-Use-AI-Agent
```

### 2. Create & activate the virtual environment
```sh
python -m venv .venv
.venv/Scripts/Activate.ps1
```

### 3. Install dependencies
```sh
pip install -r requirements.txt
```

### 4. Add your Gemini API Key
Create a `.env` file:
```
GOOGLE_API_KEY=YOUR_KEY_HERE

**Note: gemini-2.0-flash-live-001 will be deprecated on December 09, 2025**
```

---

## Run the Project

Start the FastAPI server:
```sh
uvicorn app.server.main:app --reload
```

Then open your browser at:

```
http://localhost:8000
```

You will see the chat UI with:
- Text mode  
- Voice mode  
- Live agent reasoning  
- Vision analysis notifications  
- Tool execution messages  

---

## Available Tools

### Keyboard & Mouse
- type_text  
- type_human  
- press_key  
- hotkey  
- click_mouse  
- scroll  
- move_cursor_smooth  

### Window Management
- focus_window  
- list_windows  
- maximize_window  
- minimize_window  
- snap_left / snap_right  
- tile_two_windows  

### System Controls
- Volume functions  
- Brightness functions  
- Clipboard functions  

### File System
- read_file  
- write_file  
- move_file  
- delete_file  
- create_folder  

### Chrome Automation
- open_chrome_guest  
- open_chrome_profile  
- Detect installed apps  

### Vision Tool
- analyze_screen(question="...")

---

## How Vision Works

analyze_screen() performs:
1. Screenshot capture  
2. Optional resizing for speed  
3. Gemini Vision model call  
4. UI description returned to agent  

Used for:
- Checking if a page loaded  
- Finding buttons  
- Understanding layout  
- Confirming tool actions  

---

## Voice Mode

VisionDesk supports bi-directional voice streaming:

### How it works:
| Component | Function |
|----------|----------|
| audio-recorder.js | Captures microphone PCM |
| WebSockets | Streams realtime PCM |
| ADK Live Session | Converts audio → text |
| Gemini | Streams AI response |
| audio-player.js | Plays PCM audio |

Voice responses use the **“Puck”** prebuilt voice.

---
## Images & Videos:

## Demo Video
https://www.youtube.com/watch?v=xXHwVtG8E9g

<img width="1339" height="595" alt="image" src="https://github.com/user-attachments/assets/62e4757d-4705-4106-b946-cd5131a3d90a" /> 

<img width="807" height="595" alt="image" src="https://github.com/user-attachments/assets/960a8bc3-7d60-47ee-a537-fb0a046f4a87" />

---

## Future Enhancements

If more time is available, the next features planned are:

### 1. Mobile Support  
Run VisionDesk on mobile browsers or as a mobile app.

### 2. Bounding Box Detection  
Detect UI elements with exact bounding boxes for robust targeting.

### 3. Pixel-Perfect Coordinates  
Automatically compute exact clickable coordinates for any UI component.

### 4. Long-Term Memory  
Allow the agent to:
- Learn habits  
- Remember previous actions  
- Personalize workflows  
- Store recurring tasks  

---

## Acknowledgements

Special thanks to **Kaggle** for hosting the **5-Day AI Agents Intensive Course**.  
The concepts covered—ADK, multi-agent patterns, MCP tools, and live agent orchestration—were instrumental in building this project.

Without that program, this project would not have been possible.

---

## Contributions

PRs and issues are welcome!  
Feel free to contribute, request features, or report bugs.
