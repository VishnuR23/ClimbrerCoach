import argparse, os, subprocess, sys, time, glob
from pathlib import Path

def run_app(video, detector, planner, topk):
    cmd = [
        sys.executable, "src/app.py",
        "--source", video,
        "--detector", detector, "--planner", planner,
        "--h_min","30","--h_max","90","--s_min","60","--s_max","255","--v_min","60","--v_max","255",
        "--topk", str(topk),
        "--log_session"
    ]
    print("Running:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=False)
    except Exception as e:
        print("App run failed:", e)

def latest_session():
    runs = sorted(Path("runs").glob("session_*.jsonl"))
    return str(runs[-1]) if runs else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--video", default="data/sample/route.mp4")
    ap.add_argument("--detector", default="hsv")
    ap.add_argument("--planner", default="beam")
    ap.add_argument("--topk", type=int, default=3)
    args=ap.parse_args()

    # If demo video is placeholder or missing, skip running; rely on synthetic demo
    if not Path(args.video).exists() or Path(args.video).stat().st_size < 1000:
        print("No real demo video found; using synthetic session in runs/.")
    else:
        run_app(args.video, args.detector, args.planner, args.topk)

    sess = latest_session()
    if not sess:
        sess = "runs/session_demo.jsonl"
    prefix = "runs/portfolio"
    # Generate heatmaps + timeline
    subprocess.run([sys.executable, "scripts/replay_heatmap.py", sess, "--save_prefix", prefix], check=False)
    # Build PDF report
    subprocess.run([sys.executable, "scripts/report_portfolio.py", "--prefix", prefix, "--session", sess], check=False)
    print("Portfolio report ready at", prefix + "_report.pdf")

if __name__=="__main__":
    main()
