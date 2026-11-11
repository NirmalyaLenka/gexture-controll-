# Hand Gesture Control

[![Python](https://img.shields.io/badge/Python-3.11%20recommended-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Computer Vision](https://img.shields.io/badge/Vision-OpenCV-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Hand Tracking](https://img.shields.io/badge/Hand%20Tracking-MediaPipe-4285F4?logo=google&logoColor=white)](https://developers.google.com/mediapipe)

A webcam-based desktop experiment that detects hand landmarks with MediaPipe and maps selected poses to keyboard, scrolling, volume-key and screen-brightness actions. It displays a mirrored camera feed with hand landmarks and a small status HUD.

**Read before running:** this script can close the active browser tab, open tabs, send media/keyboard shortcuts, change volume and attempt to change display brightness. Test it with non-critical windows open and unsaved work safely stored.

## Gesture reference

The recognition logic is heuristic and depends on camera framing, lighting and hand orientation.

| Gesture / condition in the current code | Action |
|---|---|
| Right hand, thumb and index raised, with at most two non-thumb fingers raised; pinch distance controls the target | Send volume-up/down media-key presses |
| Left hand, similar pinch pose | Set brightness target through `screen-brightness-control` |
| Index and middle raised, ring and pinky lowered; index fingertip above/below the frame midpoint | Scroll up/down |
| All five fingers detected as raised | Open a new tab (`Ctrl+T`) |
| No fingers detected as raised | Close the current tab (`Ctrl+W`) |
| Index finger raised, other non-thumb fingers lowered; index tip more than 60 px to one side of wrist | Next/previous tab |
| Thumb only | Toggle mute |
| Index, middle and ring raised, thumb and pinky lowered | Send Space (often play/pause in media players) |
| Pinky only | Send a platform-specific screenshot shortcut |

The code mirrors the camera frame before processing. Handedness and gesture thresholds can still vary with camera placement and pose. The pinch distance is measured in pixels and mapped from 20 to 220 px; it is not normalized to the user's hand size or camera distance.

## Requirements

- Python **3.11 recommended**; choose a Python release supported by the MediaPipe wheel available for your platform.
- A webcam accessible to OpenCV.
- Windows is the most straightforward target for the included keyboard shortcuts. Linux behavior depends on input-device permissions and the desktop environment. macOS behavior is **not verified**; the current code uses Ctrl-style tab shortcuts and a non-standard screenshot combination for macOS.
- Packages listed in [`requirements.txt`](./requirements.txt).

| Package | Use |
|---|---|
| `opencv-python` | Webcam capture, image processing and display |
| `mediapipe` | Hand landmark detection |
| `numpy` | Pinch-distance interpolation |
| `keyboard` | Keyboard and media-key events |
| `mouse` | Scroll events |
| `screen-brightness-control` | Attempt to set display brightness |

No separate model file is checked into the repository; MediaPipe's installed package provides the hand-tracking solution used by the script.

## Installation

### Windows: setup script

1. Install Python 3.11 and make sure `python` is available on PATH.
2. Clone or download this repository.
3. Run `setup.bat`. It creates a local `.venv`, installs packages from `requirements.txt`, and checks that their imports succeed.
4. Start the app using the command printed by the setup script.

### Manual setup

Clone the actual repository:

```bash
git clone https://github.com/NirmalyaLenka/gexture-controll-.git
cd gexture-controll-
python -m venv .venv
```

Activate the environment:

**Windows Command Prompt**
```bat
.venv\Scripts\activate
```

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install and run:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python gesture_control.py
```

The application opens a webcam window. Press **Q while that window is focused** to quit. If the camera does not open, close other camera applications and check the camera privacy permissions.

## Safe first-run checklist

Before testing gestures for the first time:

1. Save work and close documents that contain unsaved changes.
2. Keep only a disposable blank browser tab open; the fist gesture can send `Ctrl+W` to the active window.
3. Avoid testing near forms, terminals, admin tools or applications where keyboard shortcuts could trigger consequential actions.
4. Run the program as a normal user, not with administrator/root privileges.
5. Keep the gesture-control window visible and press **Q** while it is focused to stop the app.
6. Test one gesture at a time in good lighting. Treat the HUD as a recognition estimate, not proof that the intended system action succeeded.

This is a testing procedure only. It does not disable keyboard or mouse actions, add confirmation prompts, or make recognition safer in software.

## How it works

1. OpenCV reads camera index `0` at a requested resolution of 1280×720 and mirrors each frame.
2. MediaPipe detects up to two hands and returns 21 landmarks per detected hand.
3. The code estimates raised fingers by comparing fingertip and joint Y-coordinates. It calculates the thumb-to-index pixel distance for pinch gestures.
4. Recognized gestures trigger keyboard or mouse events, or call the brightness-control package.
5. The app draws landmarks, a volume/brightness target display and a short-lived gesture label over the camera feed.

## Important behavior and limitations

- **Volume is approximate, not absolute.** The script sends repeated media-key presses based on a virtual starting level of 50%; it does not read the operating system's actual volume. The HUD shows the gesture's target estimate, not a verified system volume.
- **Brightness errors are hidden.** The current code catches and discards exceptions from the brightness library. If brightness does not change, the display/driver may be unsupported or permissions may be missing, and the app may not show an error.
- **Actions have different safeguards.** Discrete gestures use a per-action 0.8-second cooldown. Volume and brightness are handled continuously while their pinch pose is recognized.
- **No user confirmation is requested.** A false fist detection can send Ctrl+W; other false detections can switch tabs, scroll or send Space.
- **Operating-system shortcuts vary.** The tab shortcuts are Ctrl-based. The macOS screenshot branch uses Ctrl+Shift+3 rather than the standard Command+Shift+3 shortcut, and the `keyboard` package has platform limitations. Cross-platform operation is not guaranteed.
- **Camera selection is fixed.** The source opens camera index 0. If the wrong camera is selected, change `cv2.VideoCapture(0)` in `gesture_control.py` to the correct index.
- **Lighting and background matter.** Low light, occlusion, busy backgrounds, fast motion and unusual hand angles can produce missed or incorrect gestures.
- **No automated tests or CI workflow are present.** The repository currently has no test suite for gesture classification or OS actions.

## Troubleshooting

| Problem | What to check |
|---|---|
| `ModuleNotFoundError: cv2` or `mediapipe` | Activate the project's `.venv`, then use `python -m pip install -r requirements.txt` with the same Python used to run the script. |
| MediaPipe cannot be installed | Check the installed Python version against the current MediaPipe wheel support for your OS/architecture; Python 3.11 is the suggested starting point, not a guarantee for every environment. |
| Camera window is black or closes immediately | Check camera permissions and whether another app owns the camera. Change the source's camera index from 0 if needed. |
| Volume appears inaccurate | The code assumes a virtual 50% starting level and sends relative media-key presses. Compare the actual system volume and recalibrate the behavior if needed. |
| Brightness does not change | Confirm the display supports software brightness control. Errors are currently swallowed by the source, so check the platform's permissions and library support. |
| Keyboard actions fail on Linux | Check input-device permissions and the desktop environment. Avoid running with elevated privileges unless you understand and need them. |
| Gestures trigger too frequently | Increase `COOLDOWN` in `gesture_control.py` for discrete actions and improve lighting/framing. Continuous volume/brightness actions do not use that cooldown. |
| Wrong direction for scroll or tab switching | Adjust the frame-midpoint and wrist-offset conditions after observing the mirrored camera feed. |

## Repository layout

```text
.
├── .gitignore
├── gesture_control.py
├── requirements.txt
├── setup.bat
└── README.md
```

## License and maintenance

- **License:** no `LICENSE` file is present, so reuse and redistribution terms are not formally declared. Add a license file if you want to grant explicit permissions.
- **Verification:** repository/source review only. Dependency installation, webcam operation and system-level actions were not executed during this maintenance pass.
- **Last updated:** 11 November 2026 — corrected script paths, activated Git ignore rules, improved Windows setup isolation, and documented OS and action-safety limitations.
- **Maintenance:** update `requirements.txt`, `setup.bat`, the gesture table and platform notes together whenever packages, shortcuts or gesture rules change.
