import numpy as np

def infer_contacts(extremities_w, holds_xy, max_dist_m=0.35):
    # extremities_w: {'LH':(x,y), 'RH':..., 'LF':..., 'RF':...}
    out = {}
    for limb, p in extremities_w.items():
        if p is None:
            out[limb] = None
            continue
        best = None; best_d = 1e9
        for i, h in enumerate(holds_xy):
            if h is None: 
                continue
            d = np.linalg.norm(np.array(p)-np.array(h))
            if d < best_d:
                best_d = d; best = i
        out[limb] = best if best is not None and best_d <= max_dist_m else None
    return out
