import cv2
import numpy as np
import subprocess
import json
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "workout_history.json")
SESSION_FILE = os.path.join(BASE_DIR, "session_stats.json")
WINDOW_W, WINDOW_H = 1280, 720

EXERCISES = [
    {
        "id": "squat",
        "name": "SQUATS",
        "script": "Squat.py",
        "color": (60, 140, 255),
        "dim_color": (30, 70, 130),
        "description": "Lower body strength",
        "metric": "reps",
        "metric_key": "correct",
        "icon_type": "squat",
    },
    {
        "id": "bicep_curl",
        "name": "BICEP CURLS",
        "script": "BicepCurl.py",
        "color": (50, 210, 80),
        "dim_color": (25, 105, 40),
        "description": "Arm strength & definition",
        "metric": "reps",
        "metric_key": "correct",
        "icon_type": "curl",
    },
    {
        "id": "plank",
        "name": "PLANK HOLD",
        "script": "Plank.py",
        "color": (255, 170, 50),
        "dim_color": (130, 85, 25),
        "description": "Core stability & endurance",
        "metric": "seconds",
        "metric_key": "max_hold",
        "icon_type": "plank",
    },
    {
        "id": "side_leg_raise",
        "name": "SIDE LEG RAISE",
        "script": "SideLegRaise.py",
        "color": (220, 80, 220),
        "dim_color": (110, 40, 110),
        "description": "Hip & glute strength",
        "metric": "reps",
        "metric_key": "correct",
        "icon_type": "leg",
    },
]


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {ex["id"]: [] for ex in EXERCISES}


def draw_rounded_rect_filled(img, pt1, pt2, color, radius=10):
    x1, y1 = pt1
    x2, y2 = pt2
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    cv2.rectangle(img, (x1 + r, y1), (x2 - r, y2), color, -1)
    cv2.rectangle(img, (x1, y1 + r), (x2, y2 - r), color, -1)
    cv2.circle(img, (x1 + r, y1 + r), r, color, -1)
    cv2.circle(img, (x2 - r, y1 + r), r, color, -1)
    cv2.circle(img, (x1 + r, y2 - r), r, color, -1)
    cv2.circle(img, (x2 - r, y2 - r), r, color, -1)


def draw_rounded_rect_outline(img, pt1, pt2, color, thickness=2, radius=10):
    x1, y1 = pt1
    x2, y2 = pt2
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    cv2.line(img, (x1 + r, y1), (x2 - r, y1), color, thickness)
    cv2.line(img, (x1 + r, y2), (x2 - r, y2), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y2 - r), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y2 - r), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 0, 180, 270, color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 0, 270, 360, color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 0, 90, 180, color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)


def draw_exercise_icon(img, cx, cy, size, icon_type, color, bright_color):
    s = size
    h = s // 5  # head radius

    if icon_type == "squat":
        head_c = (cx, cy - s // 2 + h)
        cv2.circle(img, head_c, h, bright_color, 2, cv2.LINE_AA)
        torso_top = (cx, cy - s // 2 + 2 * h + 2)
        torso_bot = (cx - s // 5, cy - s // 10)
        cv2.line(img, torso_top, torso_bot, color, 2, cv2.LINE_AA)
        # Left leg bent
        cv2.line(img, torso_bot, (cx - s // 2, cy + s // 4), color, 2, cv2.LINE_AA)
        cv2.line(img, (cx - s // 2, cy + s // 4), (cx - s // 3, cy + s // 2), color, 2, cv2.LINE_AA)
        # Right leg bent
        cv2.line(img, torso_bot, (cx + s // 8, cy + s // 4), color, 2, cv2.LINE_AA)
        cv2.line(img, (cx + s // 8, cy + s // 4), (cx + s // 4, cy + s // 2), color, 2, cv2.LINE_AA)

    elif icon_type == "curl":
        head_c = (cx, cy - s // 2 + h)
        cv2.circle(img, head_c, h, bright_color, 2, cv2.LINE_AA)
        cv2.line(img, (cx, cy - s // 2 + 2 * h), (cx, cy), color, 2, cv2.LINE_AA)
        # Raised arm
        cv2.line(img, (cx, cy - s // 4), (cx - s // 3, cy - s // 4), color, 2, cv2.LINE_AA)
        cv2.line(img, (cx - s // 3, cy - s // 4), (cx - s // 2, cy - s // 2 + h + 4), bright_color, 3, cv2.LINE_AA)
        # Other arm
        cv2.line(img, (cx, cy - s // 4), (cx + s // 3, cy + s // 8), color, 2, cv2.LINE_AA)
        # Legs
        cv2.line(img, (cx, cy), (cx - s // 4, cy + s // 2), color, 2, cv2.LINE_AA)
        cv2.line(img, (cx, cy), (cx + s // 4, cy + s // 2), color, 2, cv2.LINE_AA)

    elif icon_type == "plank":
        body_y = cy
        cv2.line(img, (cx - s // 2, body_y), (cx + s // 3, body_y), bright_color, 3, cv2.LINE_AA)
        head_c = (cx + s // 2 - h, body_y - h // 2)
        cv2.circle(img, head_c, h, bright_color, 2, cv2.LINE_AA)
        # Support arms
        cv2.line(img, (cx - s // 2, body_y), (cx - s // 2, body_y + s // 3), color, 2, cv2.LINE_AA)
        cv2.line(img, (cx - s // 8, body_y), (cx - s // 8, body_y + s // 3), color, 2, cv2.LINE_AA)
        cv2.line(img, (cx - s // 2, body_y + s // 3), (cx - s // 8, body_y + s // 3), color, 1, cv2.LINE_AA)
        # Feet
        cv2.line(img, (cx + s // 3, body_y), (cx + s // 3, body_y + s // 4), color, 2, cv2.LINE_AA)

    elif icon_type == "leg":
        head_c = (cx, cy - s // 2 + h)
        cv2.circle(img, head_c, h, bright_color, 2, cv2.LINE_AA)
        cv2.line(img, (cx, cy - s // 2 + 2 * h), (cx, cy), color, 2, cv2.LINE_AA)
        # Standing leg
        cv2.line(img, (cx, cy), (cx - s // 8, cy + s // 2), color, 2, cv2.LINE_AA)
        # Raised leg
        cv2.line(img, (cx, cy), (cx + s // 2, cy - s // 4), bright_color, 3, cv2.LINE_AA)
        cv2.line(img, (cx + s // 2, cy - s // 4), (cx + s // 2 + s // 6, cy), color, 2, cv2.LINE_AA)


def draw_mini_chart(img, x, y, w, h, sessions, metric_key, color):
    if not sessions:
        cv2.line(img, (x, y + h), (x + w, y + h), (50, 52, 65), 1)
        return

    recent = sessions[-10:]
    values = [max(0, s.get(metric_key, 0)) for s in recent]
    max_val = max(values) if max(values) > 0 else 1

    n = len(values)
    bar_gap = 3
    bar_w = max(3, (w - (n - 1) * bar_gap) // n)

    for i, val in enumerate(values):
        bar_h = max(2, int((val / max_val) * (h - 2)))
        bx = x + i * (bar_w + bar_gap)
        by = y + h - bar_h
        alpha = 0.35 + 0.65 * ((i + 1) / n)
        bc = tuple(int(c * alpha) for c in color)
        cv2.rectangle(img, (bx, by), (bx + bar_w - 1, y + h - 1), bc, -1)

    cv2.line(img, (x, y + h), (x + w, y + h), (60, 62, 75), 1)


def draw_card(img, x, y, w, h, exercise, history, hover=False):
    ex_id = exercise["id"]
    color = exercise["color"]
    dim = exercise["dim_color"]

    # Background
    bg = (36, 38, 50) if hover else (28, 30, 40)
    draw_rounded_rect_filled(img, (x, y), (x + w, y + h), bg, radius=14)

    # Border
    bord = color if hover else dim
    bord_t = 2 if hover else 1
    draw_rounded_rect_outline(img, (x, y), (x + w, y + h), bord, bord_t, radius=14)

    # Top accent bar
    bar_color = color if hover else dim
    draw_rounded_rect_filled(img, (x + 2, y + 2), (x + w - 2, y + 8), bar_color, radius=8)

    # Icon (right side, vertically centered in stats area)
    bright = tuple(min(255, int(c * 1.35)) for c in color)
    icon_color = color if hover else dim
    icon_bright = bright if hover else tuple(int(c * 0.7) for c in bright)
    draw_exercise_icon(img, x + w - 72, y + 95, 60, exercise["icon_type"], icon_color, icon_bright)

    # Exercise name
    name_color = bright if hover else (210, 215, 230)
    cv2.putText(img, exercise["name"], (x + 16, y + 38),
                cv2.FONT_HERSHEY_DUPLEX, 0.68, name_color, 1, cv2.LINE_AA)

    # Description
    cv2.putText(img, exercise["description"], (x + 16, y + 56),
                cv2.FONT_HERSHEY_SIMPLEX, 0.37, (120, 122, 145), 1, cv2.LINE_AA)

    # Divider
    cv2.line(img, (x + 16, y + 67), (x + w - 16, y + 67), (48, 50, 65), 1)

    # Stats
    sessions = history.get(ex_id, [])
    metric_key = exercise["metric_key"]
    metric_unit = exercise["metric"]

    if sessions:
        last = sessions[-1]
        val = last.get(metric_key, 0)
        val_str = f"{val}s" if metric_unit == "seconds" else f"{val} reps"
        date_str = last.get("date", "")[:10]

        cv2.putText(img, "LAST SESSION", (x + 16, y + 84),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.33, (90, 92, 115), 1, cv2.LINE_AA)

        val_color = bright if hover else (230, 235, 255)
        cv2.putText(img, val_str, (x + 16, y + 110),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, val_color, 1, cv2.LINE_AA)

        cv2.putText(img, date_str, (x + 16, y + 128),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (95, 97, 120), 1, cv2.LINE_AA)

        cv2.putText(img, f"{len(sessions)} total sessions", (x + 16, y + 145),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.34, (85, 87, 110), 1, cv2.LINE_AA)

        draw_mini_chart(img, x + 16, y + 155, w - 110, 32, sessions, metric_key, color)
    else:
        cv2.putText(img, "No sessions yet", (x + 16, y + 98),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (90, 92, 115), 1, cv2.LINE_AA)
        cv2.putText(img, "Start your first workout!", (x + 16, y + 122),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.37, (75, 77, 100), 1, cv2.LINE_AA)

    # START button
    btn_x1 = x + 16
    btn_y1 = y + h - 58
    btn_x2 = x + w - 16
    btn_y2 = y + h - 16

    btn_bg = color if hover else (40, 42, 58)
    draw_rounded_rect_filled(img, (btn_x1, btn_y1), (btn_x2, btn_y2), btn_bg, radius=8)

    if hover:
        draw_rounded_rect_outline(img, (btn_x1, btn_y1), (btn_x2, btn_y2),
                                  bright, 1, radius=8)

    btn_text = "START WORKOUT"
    (tw, th), _ = cv2.getTextSize(btn_text, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
    tx = btn_x1 + (btn_x2 - btn_x1 - tw) // 2
    ty = btn_y1 + (btn_y2 - btn_y1 + th) // 2
    txt_col = (15, 15, 20) if hover else (140, 142, 170)
    cv2.putText(img, btn_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.52, txt_col, 1, cv2.LINE_AA)

    return (btn_x1, btn_y1, btn_x2, btn_y2)


def draw_header(img, history):
    cv2.rectangle(img, (0, 0), (WINDOW_W, 88), (20, 22, 30), -1)
    cv2.line(img, (0, 88), (WINDOW_W, 88), (48, 50, 68), 1)

    # Logo mark
    cv2.circle(img, (32, 44), 12, (60, 140, 255), -1)
    cv2.circle(img, (32, 44), 7, (20, 22, 30), -1)
    cv2.circle(img, (32, 44), 3, (60, 140, 255), -1)

    # Title
    cv2.putText(img, "FitForm AI", (54, 56),
                cv2.FONT_HERSHEY_DUPLEX, 1.25, (240, 242, 255), 1, cv2.LINE_AA)
    cv2.putText(img, "Exercise Monitoring Dashboard", (57, 76),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (110, 112, 145), 1, cv2.LINE_AA)

    # Right side stats
    total_sessions = sum(len(history.get(ex["id"], [])) for ex in EXERCISES)
    today = datetime.now().strftime("%b %d, %Y  %H:%M")

    cv2.putText(img, today, (WINDOW_W - 185, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.44, (130, 132, 158), 1, cv2.LINE_AA)

    sessions_text = f"Total Sessions: {total_sessions}"
    cv2.putText(img, sessions_text, (WINDOW_W - 185, 62),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (110, 112, 140), 1, cv2.LINE_AA)

    # Best streak or summary
    all_dates = []
    for ex in EXERCISES:
        for s in history.get(ex["id"], []):
            d = s.get("date", "")[:10]
            if d:
                all_dates.append(d)
    unique_days = len(set(all_dates))
    cv2.putText(img, f"Active Days: {unique_days}", (WINDOW_W - 185, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (95, 97, 125), 1, cv2.LINE_AA)


def draw_footer(img, hover_card):
    fy = WINDOW_H - 40
    cv2.rectangle(img, (0, fy), (WINDOW_W, WINDOW_H), (18, 20, 28), -1)
    cv2.line(img, (0, fy), (WINDOW_W, fy), (48, 50, 68), 1)

    hint = "Hover a card to preview  |  Click START WORKOUT to begin  |  Press Q to quit"
    cv2.putText(img, hint, (20, fy + 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (85, 87, 108), 1, cv2.LINE_AA)

    cv2.putText(img, "v2.0", (WINDOW_W - 45, fy + 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.36, (65, 67, 88), 1, cv2.LINE_AA)


def draw_dashboard(history, hover_card=-1):
    img = np.zeros((WINDOW_H, WINDOW_W, 3), dtype=np.uint8)
    img[:] = (22, 24, 32)

    draw_header(img, history)
    draw_footer(img, hover_card)

    margin = 28
    gap = 16
    header_h = 92
    footer_h = 42
    avail_h = WINDOW_H - header_h - footer_h - 10
    avail_w = WINDOW_W - 2 * margin

    card_w = (avail_w - gap) // 2
    card_h = (avail_h - gap) // 2
    start_y = header_h + 5

    buttons = []
    for i, exercise in enumerate(EXERCISES):
        col = i % 2
        row = i // 2
        cx = margin + col * (card_w + gap)
        cy = start_y + row * (card_h + gap)
        hover = (i == hover_card)
        btn_rect = draw_card(img, cx, cy, card_w, card_h, exercise, history, hover)
        buttons.append((cx, cy, cx + card_w, cy + card_h, i, btn_rect))

    return img, buttons


def show_launching_screen(exercise):
    img = np.zeros((WINDOW_H, WINDOW_W, 3), dtype=np.uint8)
    img[:] = (22, 24, 32)

    color = exercise["color"]
    bright = tuple(min(255, int(c * 1.35)) for c in color)
    name = exercise["name"]

    # Center card
    cw, ch = 500, 200
    cx = (WINDOW_W - cw) // 2
    cy = (WINDOW_H - ch) // 2
    draw_rounded_rect_filled(img, (cx, cy), (cx + cw, cy + ch), (30, 32, 42), radius=16)
    draw_rounded_rect_outline(img, (cx, cy), (cx + cw, cy + ch), color, 2, radius=16)
    draw_rounded_rect_filled(img, (cx + 2, cy + 2), (cx + cw - 2, cy + 8), color, radius=10)

    cv2.putText(img, "Launching...", (cx + 30, cy + 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (170, 172, 195), 1, cv2.LINE_AA)
    cv2.putText(img, name, (cx + 30, cy + 100),
                cv2.FONT_HERSHEY_DUPLEX, 0.9, bright, 1, cv2.LINE_AA)
    cv2.putText(img, exercise["description"], (cx + 30, cy + 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (110, 112, 140), 1, cv2.LINE_AA)
    cv2.putText(img, "Press Q in the exercise window to stop and return",
                (cx + 30, cy + 162),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (85, 87, 110), 1, cv2.LINE_AA)

    cv2.imshow("FitForm AI", img)
    cv2.waitKey(900)


def update_history_from_session(ex_id):
    if not os.path.exists(SESSION_FILE):
        return
    try:
        with open(SESSION_FILE, 'r') as f:
            session = json.load(f)
        if session.get("exercise_id") == ex_id:
            history = load_history()
            if ex_id not in history:
                history[ex_id] = []
            session["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            history[ex_id].append(session)
            history[ex_id] = history[ex_id][-100:]
            with open(HISTORY_FILE, 'w') as f:
                json.dump(history, f, indent=2)
        os.remove(SESSION_FILE)
    except Exception:
        pass


def launch_exercise(exercise):
    script_path = os.path.join(BASE_DIR, exercise["script"])
    show_launching_screen(exercise)
    subprocess.run([sys.executable, script_path])
    update_history_from_session(exercise["id"])


def main():
    history = load_history()
    hover_card = -1

    cv2.namedWindow("FitForm AI", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("FitForm AI", WINDOW_W, WINDOW_H)
    cv2.setWindowProperty("FitForm AI", cv2.WND_PROP_TOPMOST, 1)

    mouse_pos = [0, 0]
    clicked = [False]

    def on_mouse(event, x, y, flags, param):
        mouse_pos[0] = x
        mouse_pos[1] = y
        if event == cv2.EVENT_LBUTTONDOWN:
            clicked[0] = True

    cv2.setMouseCallback("FitForm AI", on_mouse)

    while True:
        mx, my = mouse_pos
        img, buttons = draw_dashboard(history, hover_card)

        new_hover = -1
        launched = False
        for (x1, y1, x2, y2, idx, btn_rect) in buttons:
            if x1 <= mx <= x2 and y1 <= my <= y2:
                new_hover = idx

            bx1, by1, bx2, by2 = btn_rect
            if clicked[0] and bx1 <= mx <= bx2 and by1 <= my <= by2:
                clicked[0] = False
                launched = True
                cv2.destroyWindow("FitForm AI")
                launch_exercise(EXERCISES[idx])
                history = load_history()
                cv2.namedWindow("FitForm AI", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("FitForm AI", WINDOW_W, WINDOW_H)
                cv2.setWindowProperty("FitForm AI", cv2.WND_PROP_TOPMOST, 1)
                cv2.setMouseCallback("FitForm AI", on_mouse)
                new_hover = -1
                break

        if not launched:
            clicked[0] = False

        hover_card = new_hover
        cv2.imshow("FitForm AI", img)
        key = cv2.waitKey(25) & 0xFF
        if key == ord('q'):
            break
        try:
            if cv2.getWindowProperty("FitForm AI", cv2.WND_PROP_VISIBLE) < 1:
                break
        except Exception:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
