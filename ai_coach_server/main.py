import os, json, uuid, asyncio
from typing import Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

app = FastAPI(title="AI Coach Server", version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
os.makedirs("static/audio", exist_ok=True)

class LimbState(BaseModel):
    hands_xy: Optional[List[List[float]]] = None
    feet_xy: Optional[List[List[float]]] = None

class Context(BaseModel):
    estimated_grade: Optional[str] = None
    com_margin: Optional[float] = None
    dyn_factor: Optional[float] = None
    topk: Optional[list] = None
    limb_state: Optional[LimbState] = None

class Suggestion(BaseModel):
    limb: str
    hold_index: int
    confidence: Optional[float] = None
    dx_m: Optional[float] = 0.0
    dy_m: Optional[float] = 0.0

class CoachPayload(BaseModel):
    context: Optional[Context] = None
    prompt: Optional[str] = "Give a concise, actionable climbing coaching cue (<=10 words)."
    suggestion: Suggestion
    micro_tip: Optional[str] = ""
    want_audio: bool = False

def format_line(p: CoachPayload) -> str:
    limb = p.suggestion.limb
    hold = p.suggestion.hold_index
    dx = p.suggestion.dx_m or 0.0
    dy = p.suggestion.dy_m or 0.0
    tip = p.micro_tip or ""
    grade = p.context.estimated_grade if p.context else None
    parts = [f"{limb} to hold {hold}"]
    if abs(dy) > 0.02 or abs(dx) > 0.02:
        horiz = ""
        if abs(dx) > 0.02:
            horiz = f", {abs(dx)*100:.0f} cm " + ("right" if dx>0 else "left")
        parts.append(f"{abs(dy)*100:.0f} cm up{horiz}")
    if tip: parts.append(tip)
    if grade: parts.append(f"route {grade}")
    return ", ".join(parts)[:120]

def synth_audio(text: str) -> Optional[str]:
    if pyttsx3 is None or not text:
        return None
    fn = f"static/audio/{uuid.uuid4().hex}.wav"
    try:
        engine = pyttsx3.init()
        engine.save_to_file(text, fn)
        engine.runAndWait()
        return f"/{fn}"
    except Exception:
        return None

@app.post("/coach")
async def coach(payload: CoachPayload):
    text = format_line(payload)
    audio_url = synth_audio(text) if payload.want_audio else None
    return JSONResponse({"text": text, "audio_url": audio_url})

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            payload = CoachPayload(**data)
            line = format_line(payload)
            tokens = line.split(" ")
            out = ""
            for t in tokens:
                out += (t + " ")
                await ws.send_json({"partial": out.strip()})
                await asyncio.sleep(0.08)
            await ws.send_json({"final": line})
    except WebSocketDisconnect:
        return
