import argparse, json
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from datetime import datetime

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prefix", required=True, help="runs/... prefix used by replay_heatmap")
    ap.add_argument("--session", required=True, help="path to session jsonl")
    ap.add_argument("--out", default=None)
    args=ap.parse_args()

    out = args.out or (args.prefix + "_report.pdf")
    with PdfPages(out) as pdf:
        # Cover
        plt.figure(figsize=(8.5,11))
        plt.axis('off')
        plt.title("ClimbCoach — Session Report", fontsize=20)
        plt.text(0.1, 0.9, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", fontsize=12)
        plt.text(0.1, 0.86, f"Session: {Path(args.session).name}", fontsize=12)
        # add thumbnails if exist
        for i,(name,y) in enumerate([("heat_contacts",0.65),("heat_suggestions",0.4),("timeline",0.15)]):
            p = Path(args.prefix + f"_{name}.png")
            if p.exists():
                img = plt.imread(p)
                plt.imshow(img, extent=(0.1,0.9,y, y+0.2))
        pdf.savefig(); plt.close()

        # Full-size pages
        for name,title in [("heat_contacts","Hold Heatmap — Contacts"), ("heat_suggestions","Hold Heatmap — Suggestions"), ("timeline","Timeline — Min Hand Height")]:
            p = Path(args.prefix + f"_{name}.png")
            if p.exists():
                plt.figure(figsize=(8.5,11)); plt.imshow(plt.imread(p)); plt.axis('off'); plt.title(title)
                pdf.savefig(); plt.close()

    print("Saved", out)

if __name__=="__main__":
    main()
