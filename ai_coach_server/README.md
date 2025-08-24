# AI Coach Server

Tiny FastAPI service turning ClimbCoach suggestions into short coaching lines.
- POST `/coach` → `{"text": "...", "audio_url": "/static/audio/....wav"}`
- WS `/ws` → streams partial text then a final line.
