import os, httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
HEADERS = {"xi-api-key": API_KEY} if API_KEY else {}

@router.post("/tts")
async def tts(text: str):
    if not API_KEY or not VOICE_ID:
        raise HTTPException(500, "ElevenLabs not configured")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    payload = {"text": text, "model_id": MODEL, "voice_settings": {"stability": 0.4, "similarity_boost": 0.7}}
    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.post(url, headers=HEADERS, json=payload)
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, await resp.aread())
        async def gen():
            async for chunk in resp.aiter_bytes():
                yield chunk
        return StreamingResponse(gen(), media_type="audio/mpeg")
