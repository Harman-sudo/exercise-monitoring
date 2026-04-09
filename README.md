# FitForm AI — Exercise Monitoring

AI-powered exercise monitoring app that tracks your workout form in real time using pose detection.

---

## Two Components

| Component | File | Where it runs |
|-----------|------|---------------|
| **Web App** | `app.py` | Render (online), any browser including mobile |
| **Desktop App** | `main.py` | Your local PC only (needs webcam) |

> **Important:** `main.py` requires a webcam and screen. It will NOT work on Render. Render runs `app.py` only (via Procfile).

---

## Live Demo (Render Deployment)

The web app provides a login-protected dashboard with exercise guides accessible from any browser — including mobile.

### Deploy on Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add these Environment Variables in the Render dashboard:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret | `any-random-string-here` |
| `ADMIN_USER` | Login username | `admin` |
| `ADMIN_PASS` | Login password | `yourpassword` |

6. Click **Deploy**

---

## Desktop App (Local Use — Webcam Required)

The desktop app opens a GUI dashboard and runs real-time pose detection using your webcam.

### Requirements

- Python 3.9+
- Webcam
- Windows / macOS / Linux with display

### Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd exercise-monitoring

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install all dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

Use the dashboard to select an exercise. Press **Q** to quit any exercise window.

---

## Exercises

| Exercise | Detection |
|----------|-----------|
| Squats | Knee & hip angle tracking |
| Bicep Curls | Elbow & shoulder angle |
| Plank Hold | Duration timer with posture check |
| Side Leg Raise | Hip abduction angle |

---

## Project Structure

```
exercise-monitoring/
├── app.py              # Flask web app (Render deployment)
├── main.py             # Desktop GUI dashboard (local only)
├── Squat.py            # Squat pose detection
├── BicepCurl.py        # Bicep curl detection
├── Plank.py            # Plank hold detection
├── SideLegRaise.py     # Side leg raise detection
├── templates/          # HTML pages for web app
├── static/             # CSS and images
├── workout_history.json# Local workout data
├── requirements.txt    # Python dependencies
└── Procfile            # Render start command
```

---

## Tech Stack

- **Python** — Flask, OpenCV, NumPy, MediaPipe
- **Pose Detection** — MediaPipe Pose
- **Web Server** — Gunicorn
- **Deployment** — Render
