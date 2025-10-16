## Business Proposal: AI Fitness & Wellness Coach (MVP)

### Vision Statement
Empower individuals to build sustainable fitness, nutrition, and wellness habits with a safety-first AI coach that adapts to user context and recovery state.

### Problem
- Beginners lack personalized, safe guidance across training, nutrition, and recovery.
- Generic plans ignore age, gender, equipment, and physical limitations.
- Guidance is fragmented; users need one place to plan and get feedback.

### Solution (MVP)
Deliver a simple, production-hostable web app that:
- Captures a basic profile (age, gender, level, goal, equipment, limitations)
- Generates safe 30-minute workouts tailored to the profile
- Offers chat-based AI coaching (fitness, nutrition, wellness)
- Logs meals, workouts, and wellness metrics and returns instant feedback
- Stores data in JSON for simplicity and quick iteration

### Feature List & User Flow
1. Registration: Create/update profile
2. Workout Generation: Personalized plan with warm-up, main set, cool-down
3. Chat Coach: Intent-routed agents for fitness, nutrition, wellness
4. Logging APIs: `/api/log/meal|workout|wellness` with immediate feedback
5. History: Last workout and recent chat history persisted

User Flow:
Home → Register → Generate Workout → Review Plan → Chat for refinements → Log meals/workouts/wellness → Receive feedback

### Technical Stack
- Language: Python 3.10+
- Framework: Flask
- AI: Google Gemini (`google-generativeai`)
- Storage: JSON files (MVP)
- Deployment: Gunicorn + Render/Railway/Hugging Face Spaces

### High-Level Architecture
- `app.py`: Flask app, routes, session, blueprint registration
- `api.py`: REST endpoints for logs; integrates `CommunicationAgent`
- `chat_agent.py`: Multi-agent orchestration and synthesis
- `workout_generator.py`: Safety-focused workout generation with Gemini and fallback
- `database.py`: JSON persistence helpers, user stats aggregation
- `templates/`, `static/`: UI

### Implementation Details
- Safety-first prompts consider gender, age, and physical limitations
- Auto-intensity reduction: recent poor wellness (e.g., low sleep or high stress) triggers softer training
- Chat persistence: last 50 messages per user
- Fallback logic: if AI is unavailable, provide a sensible default workout
- Environment via `.env` using `python-dotenv`

### Assumptions & Constraints
- JSON storage is sufficient for MVP demos and single-user/low-concurrency use
- Persistence on cloud hosts may require a persistent disk for logs/data durability
- Secrets must be set via environment variables

### Risks & Mitigations
- AI availability → fallback workout and graceful error messages
- Data durability on ephemeral hosts → use Render persistent volume or move to DB
- Prompt safety & scope → explicit system prompts and constraints

### Roadmap (Post-MVP)
- Replace JSON with SQLite/Postgres
- Add authentication and multi-user dashboards
- Expand UI for meal/wellness logging and analytics
- Scheduled reminders and habit tracking

### Hosting & Access
- Recommended: Render (free tier) or Railway
- Start command: `gunicorn app:app`
- Env: `GEMINI_API_KEY`, `FLASK_SECRET_KEY`
- Public URL: Will be embedded in the submitted document after deployment


