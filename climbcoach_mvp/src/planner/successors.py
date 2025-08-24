from .state_repr import State

def all_successors(state, reachable, allow_hand_match=True, allow_foot_match=False):
    occ = set([x for x in [state.LH, state.RH, state.LF, state.RF] if x is not None and x>=0])
    def can_use(j, limb):
        if j is None or j<0: return False
        if j in occ:
            if allow_hand_match and limb in ('LH','RH') and ((limb=='LH' and state.RH==j) or (limb=='RH' and state.LH==j)):
                return True
            if allow_foot_match and limb in ('LF','RF') and ((limb=='LF' and state.RF==j) or (limb=='RF' and state.LF==j)):
                return True
            return False
        return True
    out = []
    for limb in ['LH','RH','LF','RF']:
        for j in reachable.get(limb, []):
            if not can_use(j, limb): continue
            if limb=='LH': out.append(((limb,j), State(j, state.RH, state.LF, state.RF)))
            if limb=='RH': out.append(((limb,j), State(state.LH, j, state.LF, state.RF)))
            if limb=='LF': out.append(((limb,j), State(state.LH, state.RH, j, state.RF)))
            if limb=='RF': out.append(((limb,j), State(state.LH, state.RH, state.LF, j)))
    return out
