# AI Sports Coach – Competition Build

End-to-end demo with **React (Vite)** frontend and **FastAPI** backend exposing **ElevenLabs TTS + realtime ASR** relays. Frontend runs fully client-side with dummy data; backend is only used for voice.

## Monorepo layout
```
frontend/   # React + Vite app (uses window.__VITE_API__ to call backend)
backend/    # FastAPI: /api/voice/tts and /api/voice/asr relays
```

## Local dev
### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill ELEVENLABS_* values
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# In the browser console, set the API (or set in src/main.jsx):
# window.__VITE_API__ = "http://localhost:8000"
```

## Deploy quickly
- **Frontend (Vercel/Netlify):** Deploy `frontend/` as a static SPA build (`npm run build`).
- **Backend (Render/Fly/DO App Platform):**
  - Build from `backend/` with `Dockerfile` or `uvicorn` command.
  - Add environment variables: `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `ELEVENLABS_MODEL`.
  - Expose port `8000`.

## Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: AI Sports Coach (frontend + FastAPI voice relays)"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## Notes
- The frontend does **not** send your ElevenLabs API key. All calls go through the backend relay.
- Realtime ASR payloads from ElevenLabs can change; adjust `voice_asr.py` parsing if needed.
- The UI integrates goals/diary/readiness context into the Ask Coach answers and provides the requested workflow.
