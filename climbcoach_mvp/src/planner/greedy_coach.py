import numpy as np

def choose_next_move(holds_w, contacts, named_w, reach_model):
    # very simple: for each hand, pick the reachable hold that gains the most up (min y)
    best=None; best_score=1e9; best_why=None
    for limb, joint in [('LH','left_wrist'),('RH','right_wrist')]:
        p = named_w.get(joint)
        if p is None: continue
        for i,h in enumerate(holds_w):
            ok, d = reach_model.hand_within_reach(p, h)
            if not ok: continue
            score = h[1] + 0.2*abs(h[0]-p[0]) + 0.3*(d or 0.2)  # lower y means higher up (better)
            if score < best_score:
                best_score = score; best={'limb':limb, 'hold_index':i, 'target_xy':h, 'score': 1.0/(1.0+score)}
                best_why = f"upward gain, dist={d:.2f}m"
    return best, best_why
