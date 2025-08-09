import os, asyncio, json, websockets
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

ELEVEN_ASR_URL = "wss://api.elevenlabs.io/v1/convai/realtime"
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY" )

@router.websocket("/asr")
async def asr_ws(ws: WebSocket):
    await ws.accept()
    if not ELEVEN_API_KEY:
        await ws.send_text(json.dumps({"error":"Missing ELEVENLABS_API_KEY"}))
        await ws.close(); return

    try:
        async with websockets.connect(f"{ELEVEN_ASR_URL}?model_id=eleven_turbo_v2", extra_headers={"xi-api-key": ELEVEN_API_KEY}) as eleven:
            async def client_to_eleven():
                try:
                    while True:
                        buf = await ws.receive_bytes()
                        await eleven.send(buf)
                except WebSocketDisconnect:
                    await eleven.close()
                except Exception:
                    pass

            async def eleven_to_client():
                try:
                    async for msg in eleven:
                        try:
                            data = json.loads(msg)
                            # NOTE: Adjust this to match ElevenLabs realtime payloads
                            if "transcript" in data:
                                await ws.send_text(json.dumps({"text": data["transcript"]}))
                        except Exception:
                            pass
                except Exception:
                    pass

            await asyncio.gather(client_to_eleven(), eleven_to_client())
    except Exception as e:
        await ws.send_text(json.dumps({"error": f"ASR relay error: {str(e)}"}))
        await ws.close()
