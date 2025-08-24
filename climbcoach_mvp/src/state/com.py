import numpy as np

def com_proxy(named_w):
    lh = named_w.get('left_hip'); rh = named_w.get('right_hip')
    ls = named_w.get('left_shoulder'); rs = named_w.get('right_shoulder')
    pts = [p for p in [lh,rh,ls,rs] if p is not None]
    if not pts: 
        return None
    arr = np.array(pts, dtype=np.float32)
    return float(arr[:,0].mean()), float(arr[:,1].mean())
