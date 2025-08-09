from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from voice import router as voice_router
from voice_asr import router as asr_router

app = FastAPI(title="AI Sports Coach Backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/") 
def root():
    return {"ok": True, "service": "ai-sports-coach-backend"}

# Mount voice routes
app.include_router(voice_router, prefix="/api/voice")
app.include_router(asr_router, prefix="/api/voice")
