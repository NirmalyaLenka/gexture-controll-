# Hand Gesture Control

Control your computer with hand gestures using your webcam. No special hardware required.

Built with Python, MediaPipe, and OpenCV. Works on Windows, macOS, and Linux.

---

## Gesture Reference

| Gesture | Action |
|---|---|
| Right hand — thumb and index pinch | Volume control (wider = louder) |
| Left hand — thumb and index pinch | Brightness control (wider = brighter) |
| Index and middle finger up, hand raised | Scroll up |
| Index and middle finger up, hand lowered | Scroll down |
| All 5 fingers open | Open new tab (Ctrl+T) |
| Closed fist | Close current tab (Ctrl+W) |
| Index finger pointing right | Next tab (Ctrl+Tab) |
| Index finger pointing left | Previous tab (Ctrl+Shift+Tab) |
| Thumb only up | Toggle mute |
| Index, middle, ring up | Play / Pause (Space) |
| Pinky only up | Screenshot |

---

## Requirements

- Python 3.8 to 3.12 (Python 3.11 recommended)
- A webcam
- Windows, macOS, or Linux

---

## Installation

### Option 1 — One click setup (Windows only)

Double click `setup.bat`. It installs everything automatically.

### Option 2 — Manual install

Clone the repository:

```bash
git clone https://github.com/yourusername/hand-gesture-control.git
cd hand-gesture-control
```

Create and activate a virtual environment (recommended):

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

macOS / Linux:
```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run

```bash
python gesture_control.py
```

A webcam window opens with hand landmarks drawn in real time. Press Q to quit.

---

## How It Works

MediaPipe detects 21 landmarks on each hand every frame. The code checks which fingertips are raised above their knuckles, measures the pinch distance between the thumb and index finger using Euclidean distance, and checks hand position relative to the wrist. These values map to system actions. A 0.8 second cooldown prevents accidental repeated triggers.

Volume is controlled by sending keyboard volume up/down key presses proportional to how much the pinch distance changed. Brightness uses the screen-brightness-control library. Tab and media controls use the keyboard library to send hotkeys directly to the OS.

---

## Platform Notes

**Windows**
All features work out of the box. Volume uses keyboard media keys. Brightness uses screen-brightness-control. Run as administrator if the keyboard library cannot send hotkeys.

**macOS**
Volume and media keys work natively. Brightness control may require granting accessibility permissions under System Preferences > Privacy and Security > Accessibility for Terminal or the Python process.

**Linux**
Volume uses keyboard media keys via the keyboard library. Brightness may require running with sudo depending on the display driver. If brightness fails run `sudo python gesture_control.py`. The keyboard library on Linux requires the `python3-xlib` package: `sudo apt install python3-xlib`.

---

## Troubleshooting

**ModuleNotFoundError: No module named 'cv2'**
You installed packages into a different Python version than the one running the script. Use `python -m pip install` with the same Python executable you use to run the script. Do not mix Python 3.11 and Python 3.15.

**mediapipe install fails / numpy build error**
mediapipe supports Python 3.8 to 3.12 only. Python 3.13 and above are not yet supported. Install Python 3.11 from python.org and use that.

**Network error during pip install**
If pip keeps dropping the connection, install on mobile hotspot or download `.whl` files manually from pypi.org and install with `pip install path/to/file.whl`.

**Camera opens but shows black screen**
Change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` in the script. You may have multiple cameras and index 0 is the wrong one.

**Gestures trigger too often**
Increase the `COOLDOWN` value at the top of the script. Default is 0.8 seconds. Try 1.2 or 1.5.

**Volume pinch feels too jumpy**
Increase the upper value in `np.interp(pinch, [20.0, 220.0], ...)` from 220 to 300. This requires a wider pinch to reach full volume, giving finer control.

**No hands detected**
Improve lighting on your hands. MediaPipe works best with a plain background and even, front-facing light. Avoid dark rooms or cluttered backgrounds.

---

## Project Structure

```
hand-gesture-control/
├── gesture_control.py      Main script
├── requirements.txt        Python dependencies
├── setup.bat               One-click Windows installer
├── .gitignore              Git ignore rules
└── README.md               This file
```

---

## Possible Extensions

- Add an air mouse mode that maps index finger position to cursor movement
- Map gestures to custom macros for gaming or productivity shortcuts
- Add a GUI settings panel to remap gestures without editing code
- Connect to MQTT to control smart home devices with gestures
- Add gesture recording to train custom gestures using the landmark data

---

## Dependencies

| Package | Purpose |
|---|---|
| opencv-python | Webcam capture and frame rendering |
| mediapipe | Hand landmark detection |
| numpy | Distance interpolation |
| keyboard | Hotkeys and media key presses |
| mouse | Scroll wheel control |
| screen-brightness-control | Screen brightness adjustment |

---

## License

This project is released for open use. No restrictions apply.
