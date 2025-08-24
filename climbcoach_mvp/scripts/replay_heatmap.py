import argparse, json
from pathlib import Path
import matplotlib.pyplot as plt

def load_session(p):
    meta=None; frames=[]
    for line in Path(p).read_text().splitlines():
        obj=json.loads(line)
        if obj.get("type")=="meta": meta=obj
        elif obj.get("type")=="frame": frames.append(obj)
    return meta, frames

def heat_counts(frames):
    c_contact={}; c_suggest={}
    for fr in frames:
        holds=fr.get("holds_wall_xy") or []
        n=len(holds)
        cons=fr.get("contacts") or {}
        for limb,h in cons.items():
            if isinstance(h,int) and 0<=h<n: c_contact[h]=c_contact.get(h,0)+1
        sug=fr.get("suggestion") or {}
        h=sug.get("hold_index")
        if isinstance(h,int) and 0<=h<n: c_suggest[h]=c_suggest.get(h,0)+1
    return c_contact, c_suggest

def timeline(frames, key):
    xs=[]; ys=[]
    for fr in frames:
        t=fr["t_rel_ms"]/1000.0; xs.append(t)
        named=fr.get("named_w") or {}
        lh=named.get("left_wrist"); rh=named.get("right_wrist")
        vals=[p[1] for p in [lh,rh] if p]
        ys.append(min(vals) if vals else None)
    xs2=[]; ys2=[]
    for x,y in zip(xs,ys):
        if y is not None: xs2.append(x); ys2.append(y)
    return xs2, ys2

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("--save_prefix", default=None)
    args=ap.parse_args()
    meta, frames = load_session(args.jsonl)
    if not frames: print("No frames"); return
    holds=frames[0]["holds_wall_xy"]
    xs=[h[0] for h in holds]; ys=[h[1] for h in holds]

    c_contact, c_suggest = heat_counts(frames)

    plt.figure(); plt.scatter(xs, ys, s=[10+6*c_contact.get(i,0) for i in range(len(holds))])
    plt.gca().invert_yaxis(); plt.title("Hold Heatmap — Contacts"); plt.xlabel("Wall X (m)"); plt.ylabel("Wall Y (m)")
    if args.save_prefix: plt.savefig(f"{args.save_prefix}_heat_contacts.png", bbox_inches="tight")

    plt.figure(); plt.scatter(xs, ys, s=[10+6*c_suggest.get(i,0) for i in range(len(holds))])
    plt.gca().invert_yaxis(); plt.title("Hold Heatmap — Suggestions"); plt.xlabel("Wall X (m)"); plt.ylabel("Wall Y (m)")
    if args.save_prefix: plt.savefig(f"{args.save_prefix}_heat_suggestions.png", bbox_inches="tight")

    t,y = timeline(frames, "handmin")
    if t:
        plt.figure(); plt.plot(t,y); plt.gca().invert_yaxis(); plt.title("Timeline — Min Hand Height"); plt.xlabel("Time (s)"); plt.ylabel("Y (m)")
        if args.save_prefix: plt.savefig(f"{args.save_prefix}_timeline.png", bbox_inches="tight")

    if not args.save_prefix:
        plt.show()

if __name__=="__main__":
    main()
