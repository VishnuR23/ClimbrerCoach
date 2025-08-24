from collections import deque

class ContactSmoother:
    def __init__(self, switch_patience=3):
        self.switch_patience = int(switch_patience)
        self.prev = {'LH': None, 'RH': None, 'LF': None, 'RF': None}
        self.cand = {'LH': None, 'RH': None, 'LF': None, 'RF': None}
        self.counter = {'LH': 0, 'RH': 0, 'LF': 0, 'RF': 0}

    def _stick(self, limb, raw):
        if raw == self.prev[limb]:
            self.cand[limb] = None; self.counter[limb] = 0
            return self.prev[limb]
        if raw != self.cand[limb]:
            self.cand[limb] = raw; self.counter[limb] = 1
            return self.prev[limb]
        self.counter[limb] += 1
        if self.counter[limb] >= self.switch_patience:
            self.prev[limb] = raw; self.cand[limb] = None; self.counter[limb] = 0
            return raw
        return self.prev[limb]

    def update(self, raw_contacts):
        s = {}
        for limb in ['LH','RH','LF','RF']:
            s[limb] = self._stick(limb, raw_contacts.get(limb, None))
        # resolve conflicts (allow LH/RH matching; discourage feet matching)
        owners = {}
        for limb in ['LH','RH','LF','RF']:
            h = s[limb]
            if h is None: continue
            if h not in owners:
                owners[h] = limb
            else:
                if {owners[h], limb} == {'LH','RH'}:
                    continue  # allow hand match
                s[limb] = self.prev[limb]
        self.prev.update(s)
        return s
