# AI Sports Coach Backend

A full-stack FastAPI backend for the AI Sports Coach application with JWT authentication and ElevenLabs agent tools.

## Features

- **JWT Authentication** for frontend API endpoints
- **Agent Token Authentication** for tool endpoints
- **SQLModel/SQLAlchemy** with SQLite (switchable to PostgreSQL)
- **OpenAPI Documentation** at `/docs`
- **CORS Support** for frontend integration
- **Voice Integration** with ElevenLabs TTS/ASR
- **Comprehensive Data Models** for fitness tracking

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./fitness_coach.db

# Authentication
JWT_SECRET=your-secret-key-change-in-production
AGENT_TOKEN=your-agent-token-change-in-production

# Server
PORT=8000

# CORS
FRONTEND_ORIGIN=http://localhost:5173

# ElevenLabs (optional)
ELEVENLABS_API_KEY=your-api-key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_multilingual_v2
```

### 3. Seed Database

```bash
python seed.py
```

### 4. Run Server

```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

### Authentication

- `POST /dev/login` - Get JWT token for development

### Frontend API (JWT Protected)

#### User Profile
- `GET /api/me` - Get current user profile with goals summary

#### Readiness
- `GET /api/readiness/today` - Get today's readiness score
- `GET /api/readiness/getReadinessScore` - Get readiness score (existing endpoint)

#### Metrics
- `GET /api/metrics/timeline?period=week|month` - Get metrics timeline
- `POST /api/metrics/import` - Import metrics from CSV

#### Goals
- `GET /api/goals` - Get all goals
- `POST /api/goals` - Create new goal
- `DELETE /api/goals/{goal_id}` - Delete goal

#### Diary
- `GET /api/diary?from&to` - Get diary entries
- `POST /api/diary` - Create diary entry

#### Voice
- `POST /api/voice/tts` - Text-to-speech
- `WS /api/voice/asr` - Speech recognition

### Agent Tools (Agent Token Protected)

#### Readiness
- `POST /tools/getReadinessScore` - Get readiness score for agent

## Data Models

### User
- `id`, `email`, `name`, `height_cm`, `weight_kg`, `created_at`

### MetricSample
- `id`, `user_id`, `date`, `sleep_h`, `stress`, `steps`, `cardio`, `active_min`, `distance_km`, `calories`

### ReadinessSnapshot
- `id`, `user_id`, `date`, `score`, `status`, `factors_json`, `recommendation`

### WorkoutPlan
- `id`, `user_id`, `week_start`, `plan_json`

### WorkoutSession
- `id`, `user_id`, `date`, `activity`, `notes`, `data_json`

### Goal
- `id`, `user_id`, `category`, `text`, `created_at`

### DiaryEntry
- `id`, `user_id`, `date`, `type`, `text`

### ToolLog
- `id`, `tool`, `user_id`, `session_id`, `request_id`, `payload_json`, `created_at`

## Testing

### Run API Tests

```bash
python test_api.py
```

### Manual Testing

1. **Get JWT Token:**
   ```bash
   curl -X POST http://localhost:8000/dev/login
   ```

2. **Test Protected Endpoint:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/me
   ```

3. **Test Tool Endpoint:**
   ```bash
   curl -X POST http://localhost:8000/tools/getReadinessScore \
     -H "Authorization: Bearer your-agent-token-change-in-production" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "demo@example.com"}'
   ```

## Development

### Project Structure

```
backend/
├── main.py                 # FastAPI app with all routers
├── config.py              # Settings and environment variables
├── db.py                  # Database configuration
├── deps.py                # Dependencies and authentication
├── models.py              # SQLModel data models
├── seed.py                # Database seeding script
├── test_api.py            # API testing script
├── voice.py               # ElevenLabs TTS integration
├── voice_asr.py           # ElevenLabs ASR integration
├── readiness.py           # Readiness calculation logic
├── requirements.txt       # Python dependencies
├── schemas/
│   ├── api.py            # Pydantic models for API
│   └── tools.py          # Pydantic models for tools
└── routers/
    ├── api/              # Frontend API endpoints
    │   ├── me.py
    │   ├── readiness.py
    │   ├── metrics.py
    │   ├── goals.py
    │   └── diary.py
    └── tools/            # Agent tool endpoints
        └── get_readiness_score.py
```

### Adding New Endpoints

1. **Create router file** in `routers/api/` or `routers/tools/`
2. **Add Pydantic schemas** in `schemas/api.py` or `schemas/tools.py`
3. **Import and mount router** in `main.py`
4. **Add tests** in `test_api.py`

### Database Migrations

Currently using `create_all()` for simplicity. For production:

1. Use Alembic for migrations
2. Switch to PostgreSQL with `DATABASE_URL`
3. Add migration scripts

## Production Deployment

### Environment Variables

- Set strong `JWT_SECRET`
- Set unique `AGENT_TOKEN`
- Configure `DATABASE_URL` for PostgreSQL
- Set `FRONTEND_ORIGIN` to production domain

### Security

- Use HTTPS in production
- Implement rate limiting
- Add request validation
- Use secure session management

### Monitoring

- Add logging middleware
- Implement health checks
- Add metrics collection
- Set up error tracking

## Integration with Frontend

The frontend can connect to this backend by:

1. **Setting the API URL:**
   ```javascript
   window.__VITE_API__ = "http://localhost:8000"
   ```

2. **Getting JWT token:**
   ```javascript
   const response = await fetch('/dev/login', { method: 'POST' });
   const { access_token } = await response.json();
   ```

3. **Using protected endpoints:**
   ```javascript
   const response = await fetch('/api/me', {
     headers: { 'Authorization': `Bearer ${access_token}` }
   });
   ```

## ElevenLabs Integration

The backend provides voice capabilities through ElevenLabs:

- **TTS (Text-to-Speech):** `POST /api/voice/tts`
- **ASR (Speech Recognition):** `WS /api/voice/asr`

Configure with environment variables:
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`
- `ELEVENLABS_MODEL`
