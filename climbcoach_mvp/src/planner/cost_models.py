import numpy as np
from .stability import stability_margin

def vertical_progress_cost(prev_h, next_h):
    if not any(prev_h) or not any(next_h): return 0.0
    pmin = min([p[1] for p in prev_h if p is not None])
    nmin = min([p[1] for p in next_h if p is not None])
    return -(pmin - nmin)  # reward up

def lateral_penalty(prev_h, next_h):
    pen=0.0
    for p,n in zip(prev_h, next_h):
        if p is None or n is None: continue
        pen += 0.2*abs(n[0]-p[0])
    return pen

def crossing_penalty(hands_xy, feet_xy):
    pen=0.0
    lh,rh = hands_xy
    lf,rf = feet_xy
    if lh and rh and lh[0] > rh[0]: pen+=0.5
    if lf and rf and lf[0] > rf[0]: pen+=0.2
    return pen

def matching_penalty(state):
    pen=0.0
    if state.LH>=0 and state.RH>=0 and state.LH==state.RH: pen+=0.4
    if state.LF>=0 and state.RF>=0 and state.LF==state.RF: pen+=1.0
    return pen

def com_stability_penalty(com_xy, feet_xy):
    m = stability_margin(com_xy, [p for p in feet_xy if p is not None])
    if m == float("-inf"): return 1.0
    return 0.0 if m>=0 else 1.0 + min(1.0, abs(m))

def total_cost(prev_h, next_h, com_xy, feet_xy, reach_d, next_state=None):
    c = 1.0*vertical_progress_cost(prev_h, next_h) + 1.0*lateral_penalty(prev_h, next_h) + 0.8*com_stability_penalty(com_xy, feet_xy) + 0.3*(reach_d if reach_d is not None else 0.3)
    if next_state is not None:
        lh,rh = next_h
        lf,rf = feet_xy
        c += 0.5*crossing_penalty((lh,rh),(lf,rf))
        c += matching_penalty(next_state)
    return float(c)
