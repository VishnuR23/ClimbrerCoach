from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    LH:int; RH:int; LF:int; RF:int
    def as_tuple(self): return (self.LH,self.RH,self.LF,self.RF)
