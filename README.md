# ClimbrerCoach — Real‑time Computer Vision Coach for Climbing

ClimbCoach uses **MediaPipe Pose** + **hold detection** + **stability‑aware planning (A*/beam)** + **AI** to give **live beta**:
- which limb to move, to which hold,
- with an **AR overlay**, **top‑k suggestions**, **voice coach**, and **auto‑grade estimation**.
- Summary heatmap of moves performed
- All with an AI coach assistant

  
It logs sessions and produces **heatmaps + timelines + a PDF report** for your portfolio.

## Quick start (Docker Compose)
```bash
docker compose up --build
```
- Coach API docs: http://localhost:8000/docs
- Client logs & plots land in `climbcoach_mvp/runs/`

## Quick start (local, app only)
```bash
cd climbcoach_mvp
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/app.py --source 0 --planner greedy --detector hsv   --h_min 30 --h_max 90 --s_min 60 --s_max 255 --v_min 60 --v_max 255   --topk 3 --ai_coach local
```

## Portfolio demo (auto report)
```bash
cd climbcoach_mvp
python scripts/portfolio_demo.py --video data/sample/route.mp4 --detector hsv --planner beam --topk 3
```
Artifacts go to `runs/portfolio_*` (heatmaps, timelines, **PDF report**). If the video is missing, it will fall back to the synthetic log.

## Repo layout
- `docker-compose.yml` — run app + AI coach server together
- `climbcoach_mvp/` — CV + planning app (MediaPipe, homography, holds, A*/beam, overlay, TTS, logging, replay)
- `ai_coach_server/` — FastAPI reference server (HTTP + WebSocket) generating short coaching lines (+ optional TTS)
- `docs/` — system diagram + sample demo report
