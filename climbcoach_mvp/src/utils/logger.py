import json, time
from pathlib import Path

class SessionLogger:
    def __init__(self, out_dir="runs", session_name=None):
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        if session_name is None:
            session_name = time.strftime("session_%Y%m%d_%H%M%S")
        self.path = Path(out_dir) / f"{session_name}.jsonl"
        self.f = open(self.path, "a", buffering=1)
        self.start = time.time()
        self.write_event({"type":"meta","session":session_name,"started":self.start})
    def write_event(self, obj): self.f.write(json.dumps(obj)+"
")
    def log_frame(self, frame_idx, timings_ms, named_w, holds_w, contacts, suggestion):
        self.write_event({
            "type":"frame","t_rel_ms": int((time.time()-self.start)*1000),"frame_idx":frame_idx,
            "timings_ms": timings_ms, "named_w": named_w, "holds_wall_xy": holds_w, "contacts": contacts, "suggestion": suggestion
        })
    def close(self):
        try: self.f.close()
        except Exception: pass
