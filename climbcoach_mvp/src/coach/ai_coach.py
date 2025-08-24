import time, threading, queue, json, os
try: import pyttsx3
except Exception: pyttsx3=None
try: import requests
except Exception: requests=None

class RateLimiter:
    def __init__(self, min_interval_sec=1.0): self.min=min_interval_sec; self.last=0.0
    def allow(self):
        now=time.time()
        if now-self.last>=self.min: self.last=now; return True
        return False

class LocalTTSCoach:
    def __init__(self, speak_interval_sec=1.0, enable=True):
        self.enable = enable and (pyttsx3 is not None)
        self.q=queue.Queue(); self.rl=RateLimiter(speak_interval_sec)
        self.engine = pyttsx3.init() if self.enable else None
        self._run=True
        if self.enable:
            threading.Thread(target=self._loop, daemon=True).start()
    def _loop(self):
        last_line=None
        while self._run:
            try: payload=self.q.get(timeout=0.1)
            except queue.Empty: continue
            if not self.rl.allow(): continue
            limb=payload.get("limb","Right hand"); target=payload.get("target_name","hold")
            dx=payload.get("dx_m",0.0); dy=payload.get("dy_m",0.0)
            tip=payload.get("micro_tip",""); grade=payload.get("est_grade",None)
            parts=[f"{limb} to {target}"]
            if abs(dy)>0.02 or abs(dx)>0.02:
                horiz = f", {abs(dx)*100:.0f} cm " + ("right" if dx>0 else "left") if abs(dx)>0.02 else ""
                parts.append(f"{abs(dy)*100:.0f} cm up{horiz}")
            if tip: parts.append(tip)
            if grade: parts.append(f"route {grade}")
            line=", ".join(parts)
            if self.engine and line!=last_line:
                last_line=line; self.engine.say(line); self.engine.runAndWait()
    def enqueue(self, payload): 
        if self.enable: self.q.put(payload)
    def stop(self): self._run=False

class APICoach:
    def __init__(self, api_url, api_key=None, speak_interval_sec=1.0, enable=True):
        self.url=api_url; self.key=api_key; self.enable=enable and (requests is not None)
        self.q=queue.Queue(); self.rl=RateLimiter(speak_interval_sec)
        self.tts=pyttsx3.init() if pyttsx3 is not None else None
        self._run=True
        if self.enable: threading.Thread(target=self._loop, daemon=True).start()
    def _headers(self):
        h={"Content-Type":"application/json"}
        if self.key: h["Authorization"]=f"Bearer {self.key}"
        return h
    def _loop(self):
        last=None
        while self._run:
            try: payload=self.q.get(timeout=0.1)
            except queue.Empty: continue
            if not self.rl.allow(): continue
            try:
                r=requests.post(self.url, headers=self._headers(), data=json.dumps(payload), timeout=5)
                text=r.json().get("text") if r.status_code==200 else None
                if text and self.tts and text!=last: last=text; self.tts.say(text); self.tts.runAndWait()
            except Exception: pass
    def enqueue(self,payload):
        if self.enable: self.q.put(payload)

def build_payload_from_suggestion(sug, meta):
    limb_map={"LH":"Left hand","RH":"Right hand","LF":"Left foot","RF":"Right foot"}
    limb=limb_map.get(sug.get("limb","RH"),"Right hand")
    return {
        "context": {"estimated_grade": meta.get("grade"), "com_margin": meta.get("com_margin"), "topk": meta.get("topk", [])},
        "prompt": "Give a concise, actionable climbing coaching cue (<=10 words).",
        "suggestion": {"limb": limb, "hold_index": sug.get("hold_index"), "confidence": sug.get("score"), "dx_m": meta.get("dx_m",0.0), "dy_m": meta.get("dy_m",0.0)},
        "micro_tip": meta.get("micro_tip",""),
        "limb": limb, "target_name": f"hold {sug.get('hold_index','?')}", "dx_m": meta.get("dx_m",0.0), "dy_m": meta.get("dy_m",0.0),
        "est_grade": meta.get("grade"), "confidence": sug.get("score")
    }
