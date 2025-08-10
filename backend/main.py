from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
from voice import router as voice_router
from voice_asr import router as asr_router
from readiness import router as readiness_router
from routers.api import me, readiness as api_readiness, metrics, goals, diary
from routers.tools import get_readiness_score, get_current_metrics
from deps import create_access_token, get_current_user
from db import create_db_and_tables
from config import settings

app = FastAPI(
    title="AI Sports Coach Backend",
    description="Full-stack fitness coaching platform with AI agent tools",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting AI Sports Coach Backend...")
    create_db_and_tables()
    print("✅ Database tables created")
    
    # Run startup script for seeding
    try:
        from startup import seed_database
        seed_database()
        print("✅ Database seeded with demo data")
    except Exception as e:
        print(f"⚠️  Warning: Could not seed database: {e}")
    
    print("🎉 Backend ready to serve requests!")

@app.get("/") 
def root():
    return {"ok": True, "service": "ai-sports-coach-backend"}

# Development login endpoint
@app.post("/dev/login")
def dev_login():
    """Development endpoint to get a JWT token for testing"""
    # Create a demo user token
    access_token = create_access_token(
        data={"sub": 1, "email": "demo@example.com"}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Mount API routes (JWT protected)
app.include_router(me.router, prefix="/api", tags=["Frontend API"])
app.include_router(api_readiness.router, prefix="/api", tags=["Frontend API"])
app.include_router(metrics.router, prefix="/api", tags=["Frontend API"])
app.include_router(goals.router, prefix="/api", tags=["Frontend API"])
app.include_router(diary.router, prefix="/api", tags=["Frontend API"])

# Mount voice routes (existing)
app.include_router(voice_router, prefix="/api/voice", tags=["Voice"])
app.include_router(asr_router, prefix="/api/voice", tags=["Voice"])

# Mount readiness routes (existing)
app.include_router(readiness_router, prefix="/api/readiness", tags=["Readiness"])

# Mount tool routes (agent token protected)
app.include_router(get_readiness_score.router, prefix="/tools", tags=["Agent Tools"])
app.include_router(get_current_metrics.router, prefix="/tools", tags=["Agent Tools"])
