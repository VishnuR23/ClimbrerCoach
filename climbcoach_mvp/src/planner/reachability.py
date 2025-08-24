import numpy as np

class ReachModel:
    def __init__(self, arm_reach_m, foot_reach_m=None, dyn_factor=0.15):
        self.arm = float(arm_reach_m)
        self.foot = float(foot_reach_m if foot_reach_m is not None else arm_reach_m*0.8)
        self.dyn = float(dyn_factor)
    def _ok(self, a, b, r):
        if a is None or b is None: return (False, None)
        d = np.linalg.norm(np.array(a)-np.array(b))
        return (d <= r*(1+self.dyn), d)
    def hand_within_reach(self, a, b): return self._ok(a,b,self.arm)
    def foot_within_reach(self, a, b): return self._ok(a,b,self.foot)
