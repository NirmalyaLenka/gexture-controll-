import cv2                                          # Camera capture
import mediapipe as mp                              # Hand tracking
import numpy as np                                  # Math helpers
import keyboard                                     # Key presses
import mouse                                        # Mouse scroll
import math                                         # Distance calc
import time                                         # Cooldown timer
import platform                                     # OS detection
import subprocess                                   # Shell commands
from typing import List, Tuple                      # Type hints

OS = platform.system()                              # Detect OS

# ── Volume setup ────────────────────────────────────────────────────────────
# Uses Windows keyboard volume keys — works on ALL pycaw versions with zero
# COM/ctypes complexity. Holds the key longer for bigger changes.
_last_vol_level: float = 0.5                        # Track last level

def set_volume(val: float) -> None:                 # Set system volume
    global _last_vol_level
    val = max(0.0, min(1.0, val))
    diff = val - _last_vol_level                    # Change amount
    steps = int(abs(diff) * 50)                     # Steps to take
    if steps == 0:                                  # No change needed
        return
    key = "volume up" if diff > 0 else "volume down"
    for _ in range(steps):                          # Press key N times
        keyboard.press_and_release(key)
    _last_vol_level = val                           # Save new level

# ── Brightness setup ────────────────────────────────────────────────────────
def set_brightness(val: float) -> None:             # Set brightness
    level = max(0, min(100, int(val * 100)))
    try:
        import screen_brightness_control as sbc     # type: ignore
        sbc.set_brightness(level)
    except Exception:
        pass                                        # Silently skip

# ── MediaPipe setup ─────────────────────────────────────────────────────────
mp_hands = mp.solutions.hands                       # Hands module
mp_draw  = mp.solutions.drawing_utils               # Draw landmarks
mp_style = mp.solutions.drawing_styles              # Draw styles

hands = mp_hands.Hands(                             # Hand detector
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
)

# ── Camera setup ─────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)                           # Open webcam
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)             # Set width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)             # Set height

# ── Cooldown ─────────────────────────────────────────────────────────────────
COOLDOWN: float = 0.8                               # Secs between actions
last_action_time: dict[str, float] = {}             # Timestamps per action

def cooldown_ok(action: str) -> bool:               # Check cooldown
    now = time.time()
    if now - last_action_time.get(action, 0.0) > COOLDOWN:
        last_action_time[action] = now
        return True
    return False

def hotkey(*keys: str) -> None:                     # Press key combo
    for k in keys[:-1]:
        keyboard.press(k)                           # Hold modifiers
    keyboard.press_and_release(keys[-1])            # Tap last key
    for k in reversed(keys[:-1]):
        keyboard.release(k)                         # Release modifiers

# ── Hand helpers ─────────────────────────────────────────────────────────────
def point_dist(p1: Tuple[int, int],
               p2: Tuple[int, int]) -> float:       # Pixel distance
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def get_tip(landmarks: list,
            tip_id: int,
            fw: int, fh: int) -> Tuple[int, int]:   # Landmark to pixel
    p = landmarks[tip_id]
    return int(p.x * fw), int(p.y * fh)

def fingers_up(landmarks: list) -> List[bool]:      # Which fingers raised
    tips = [8, 12, 16, 20]                          # Tip landmark IDs
    pips = [6, 10, 14, 18]                          # Knuckle IDs
    raised: List[bool] = [
        landmarks[t].y < landmarks[p].y
        for t, p in zip(tips, pips)
    ]
    thumb = landmarks[4].x < landmarks[3].x         # Thumb open check
    return [thumb] + raised                         # [thumb,i,m,r,p]

# ── State ────────────────────────────────────────────────────────────────────
current_vol:    float = 0.5                         # Current volume
current_bright: float = 0.5                         # Current brightness
gesture_label:  str   = ""                          # HUD text
gesture_time:   float = 0.0                         # Label timestamp

# ── Main loop ────────────────────────────────────────────────────────────────
while True:
    ret, frame = cap.read()                         # Read frame
    if not ret:
        break

    frame   = cv2.flip(frame, 1)                    # Mirror
    fh, fw  = frame.shape[:2]                       # Frame size
    rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # To RGB
    results = hands.process(rgb)                    # Detect

    overlay = frame.copy()                          # Top bar
    cv2.rectangle(overlay, (0, 0), (fw, 60), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

    if results.multi_hand_landmarks:
        for hand_idx, hand_lm in enumerate(results.multi_hand_landmarks):

            mp_draw.draw_landmarks(                 # Draw skeleton
                frame, hand_lm,
                mp_hands.HAND_CONNECTIONS,
                mp_style.get_default_hand_landmarks_style(),
                mp_style.get_default_hand_connections_style(),
            )

            lm     = hand_lm.landmark               # Landmarks
            raised = fingers_up(lm)                 # Finger states
            count  = sum(raised[1:])                # Fingers up

            hand_label = (
                results.multi_handedness[hand_idx]
                .classification[0].label
            )
            hand = "Right" if hand_label == "Right" else "Left"

            thumb_tip = get_tip(lm, 4, fw, fh)     # Thumb tip
            index_tip = get_tip(lm, 8, fw, fh)     # Index tip
            wrist     = get_tip(lm, 0, fw, fh)     # Wrist

            pinch: float = point_dist(thumb_tip, index_tip)

            # VOLUME — right hand pinch
            if hand == "Right" and raised[0] and raised[1] and count <= 2:
                current_vol = float(
                    np.interp(pinch, [20.0, 220.0], [0.0, 1.0])
                )
                set_volume(current_vol)
                gesture_label = f"Volume: {int(current_vol * 100)}%"
                gesture_time  = time.time()
                bar_x = int(np.interp(current_vol, [0.0, 1.0],
                                      [50.0, float(fw - 50)]))
                cv2.rectangle(frame, (50, fh-40), (fw-50, fh-20),
                              (40, 40, 40), -1)
                cv2.rectangle(frame, (50, fh-40), (bar_x, fh-20),
                              (0, 200, 255), -1)
                cv2.circle(frame, thumb_tip, 8, (0, 200, 255), -1)
                cv2.circle(frame, index_tip, 8, (0, 200, 255), -1)
                cv2.line(frame, thumb_tip, index_tip, (0, 200, 255), 2)

            # BRIGHTNESS — left hand pinch
            elif hand == "Left" and raised[0] and raised[1] and count <= 2:
                current_bright = float(
                    np.interp(pinch, [20.0, 220.0], [0.0, 1.0])
                )
                set_brightness(current_bright)
                gesture_label = f"Brightness: {int(current_bright * 100)}%"
                gesture_time  = time.time()
                cv2.circle(frame, thumb_tip, 8, (0, 255, 200), -1)
                cv2.circle(frame, index_tip, 8, (0, 255, 200), -1)
                cv2.line(frame, thumb_tip, index_tip, (0, 255, 200), 2)

            # SCROLL — index + middle up
            elif raised[1] and raised[2] and not raised[3] and not raised[4]:
                if index_tip[1] < fh // 2 and cooldown_ok("scroll_up"):
                    mouse.wheel(3)                  # Scroll up
                    gesture_label = "Scroll Up"
                    gesture_time  = time.time()
                elif index_tip[1] >= fh // 2 and cooldown_ok("scroll_dn"):
                    mouse.wheel(-3)                 # Scroll down
                    gesture_label = "Scroll Down"
                    gesture_time  = time.time()

            # NEW TAB — all 5 fingers open
            elif all(raised) and cooldown_ok("new_tab"):
                hotkey("ctrl", "t")                 # Open new tab
                gesture_label = "New Tab"
                gesture_time  = time.time()

            # CLOSE TAB — closed fist
            elif not any(raised) and cooldown_ok("close_tab"):
                hotkey("ctrl", "w")                 # Close tab
                gesture_label = "Close Tab"
                gesture_time  = time.time()

            # NEXT / PREV TAB — index pointing sideways
            elif raised[1] and not raised[2] and not raised[3] and not raised[4]:
                if index_tip[0] > wrist[0] + 60 and cooldown_ok("next_tab"):
                    hotkey("ctrl", "tab")           # Next tab
                    gesture_label = "Next Tab"
                    gesture_time  = time.time()
                elif index_tip[0] < wrist[0] - 60 and cooldown_ok("prev_tab"):
                    hotkey("ctrl", "shift", "tab")  # Prev tab
                    gesture_label = "Previous Tab"
                    gesture_time  = time.time()

            # MUTE — thumb only
            elif raised[0] and not any(raised[1:]) and cooldown_ok("mute"):
                keyboard.press_and_release("volume mute")  # Mute
                gesture_label = "Mute Toggle"
                gesture_time  = time.time()

            # PLAY / PAUSE — index + middle + ring
            elif (raised[1] and raised[2] and raised[3]
                  and not raised[4] and not raised[0]
                  and cooldown_ok("play_pause")):
                keyboard.press_and_release("space") # Space
                gesture_label = "Play / Pause"
                gesture_time  = time.time()

            # SCREENSHOT — pinky only
            elif raised[4] and not any(raised[:4]) and cooldown_ok("screenshot"):
                if OS == "Windows":
                    hotkey("win", "shift", "s")     # Snip tool
                elif OS == "Darwin":
                    hotkey("ctrl", "shift", "3")    # macOS
                else:
                    hotkey("ctrl", "shift", "print")
                gesture_label = "Screenshot"
                gesture_time  = time.time()

    # ── HUD ──────────────────────────────────────────────────────────────────
    cv2.putText(frame, f"Vol: {int(current_vol * 100)}%",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (0, 200, 255), 2)
    cv2.putText(frame, f"Bri: {int(current_bright * 100)}%",
                (170, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (0, 255, 200), 2)
    if time.time() - gesture_time < 1.5:
        cv2.putText(frame, gesture_label,
                    (fw // 2 - 150, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.85, (255, 255, 255), 2)
    cv2.putText(frame, "Q = Quit",
                (fw - 120, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (120, 120, 120), 1)

    cv2.imshow("Hand Gesture Control", frame)       # Show window
    if cv2.waitKey(1) & 0xFF == ord("q"):           # Q to quit
        break

cap.release()                                       # Free camera
cv2.destroyAllWindows()                             # Close window
