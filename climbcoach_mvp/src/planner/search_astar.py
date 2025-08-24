from heapq import heappush, heappop

def reconstruct(parents, goal):
    path = []
    s = goal
    while s in parents and parents[s][1] is not None:
        g,(ps,a) = parents[s]
        path.append((a,s))
        s = ps
    return list(reversed(path))

class AStarPlanner:
    def __init__(self, successors_fn, cost_fn, heuristic_fn):
        self.succ = successors_fn; self.cost = cost_fn; self.h = heuristic_fn
    def plan(self, s0, goal_test, max_expansions=400):
        openq=[]; seen=set(); gscore={s0:0.0}; parents={s0:(0.0,(None,None))}
        heappush(openq,(self.h(s0),0.0,s0))
        exp=0
        while openq and exp<max_expansions:
            f,g,s = heappop(openq)
            if s in seen: continue
            seen.add(s); exp+=1
            if goal_test(s): return reconstruct(parents, s)
            for a,s2 in self.succ(s):
                c = self.cost(s,a,s2); g2 = g + c
                if (s2 not in gscore) or (g2 < gscore[s2]):
                    gscore[s2] = g2; parents[s2] = (g2,(s,a))
                    heappush(openq,(g2+self.h(s2), g2, s2))
        return []
