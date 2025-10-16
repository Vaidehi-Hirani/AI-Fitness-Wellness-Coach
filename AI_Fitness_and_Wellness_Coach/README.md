## AI Fitness & Wellness Coach

An AI-powered fitness, nutrition, and wellness coaching web app built with Flask and Google Gemini. It generates personalized workouts, offers chat-based coaching, and logs meals, workouts, and wellness metrics using simple JSON storage for an easy MVP.

### Vision Statement
Empower anyone to build sustainable healthy habits with a smart, safety-first AI coach that adapts to their goals, recovery state, and context.

### Problem & Why This Was Built
- Many beginners struggle to design safe, effective workouts and nutrition plans.
- One-size-fits-all programs ignore age, gender, equipment constraints, and physical limitations.
- Guidance is fragmented across apps; no single place ties coaching with simple logs and feedback.

**Solution:** A lightweight AI coach that creates safe plans, adapts intensity based on recent wellness, and gives concise, practical advice through a chat interface—no complex setup required.

---

### MVP Description
Deliver a functional, safety-first AI coach that:
- Registers a basic user profile (age, gender, level, goal, equipment, limitations)
- Generates a 30-minute workout tailored to the profile
- Provides chat-based coaching across fitness, nutrition, and recovery
- Logs meals, workouts, and wellness entries via simple JSON storage
- Gives instant, concise feedback after logs

This MVP prioritizes correctness, safety, and simplicity over long-term scalability.

### Core Features
- Personalized workout generator (Gemini with safety prompts)
- AI chat coach with multi-agent routing (fitness, nutrition, wellness)
- JSON-backed logs for meals, workouts, and wellness metrics
- Basic user profile and last plan retrieval
- Simple web UI with Flask templates

### User Flow
1. Visit Home → Register with basic profile
2. Generate workout → View plan → Optionally chat for refinements
3. Log meals/workouts/wellness (via API or extend UI) → Get immediate feedback

---

### Tech Stack
- Backend: Flask (Python)
- AI: Google Gemini (`google-generativeai`)
- Storage: JSON files (MVP moderate-term memory)
- Env: `python-dotenv`
- Deployment: Gunicorn, Render/Railway/Hugging Face Spaces

### Architecture (High-Level)
- `app.py`: Flask app, routes (`/`, `/register`, `/workout`, `/result`, `/chat`), registers `api` blueprint
- `api.py`: REST endpoints for `/api/log/meal|workout|wellness` with immediate AI feedback
- `chat_agent.py`: Multi-agent router (fitness, nutrition, wellness) + synthesis
- `workout_generator.py`: Safe workout generation with fallbacks
- `database.py`: JSON file helpers and aggregate stats
- `templates/`: HTML UI; `static/`: CSS

---

### Getting Started (Local)
Requirements: Python 3.10+

1) Clone and install
```bash
git clone <your-repo-url>
cd AI_Fitness_and_Wellness_Coach
python -m venv .venv && .venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
```

2) Configure environment
Create a `.env` file (see `.env.example`):
```env
GEMINI_API_KEY=your_key_here
FLASK_SECRET_KEY=change_me
```

3) Run locally
```bash
python app.py  # http://localhost:5000
```

---

### API Endpoints (MVP)
- `POST /api/log/meal` → `{ username, ...mealFields }` → stores + returns feedback
- `POST /api/log/workout` → `{ username, ...workoutFields }` → stores + returns feedback
- `POST /api/log/wellness` → `{ username, sleep_quality?, stress_level?, ... }` → stores + returns feedback

All logs are saved under `data/*.json`.

---

### Environment Variables
- `GEMINI_API_KEY` (required for AI features)
- `FLASK_SECRET_KEY` (session security)

---

### Deployment Guides

#### A) Render (recommended)
1) Push code to GitHub.
2) Create a new Render Web Service → Connect repo
3) Runtime: Python; Build command: `pip install -r requirements.txt`
4) Start command: `gunicorn app:app`
5) Add environment variables: `GEMINI_API_KEY`, `FLASK_SECRET_KEY`
6) Deploy → open the public URL

#### B) Railway
1) Push to GitHub → New Project → Deploy from Repo
2) Add variables `GEMINI_API_KEY`, `FLASK_SECRET_KEY`
3) Nixpacks or Buildpacks auto-detect Python
4) Start command: `gunicorn app:app`

#### C) Hugging Face Spaces (Gradio/Flask via `app.py`)
1) Create a Space → Type: Docker → add `Dockerfile` (optional) or use Python Space
2) For Python Space, include `requirements.txt` and set `app.py` as entry
3) Expose via `host='0.0.0.0'` if using custom server (Gunicorn not required for Spaces)

Notes:
- A `Procfile` with `web: gunicorn app:app` is included for Heroku-like platforms.
- JSON storage persists on the instance filesystem; use a persistent disk (Render) for durability.

---

### Limitations & Next Steps
- JSON storage is not ideal for multi-user concurrency → move to SQLite/Postgres
- Add authenticated user sessions
- Expand UI for meal/wellness logging
- Add analytics dashboards and reminders

---

### License
MIT (or choose your preferred license)


