import asyncio, json
try: import websockets
except Exception: websockets=None
try: import pyttsx3
except Exception: pyttsx3=None

class WSCoachClient:
    def __init__(self, ws_url, speak=True):
        self.url=ws_url
        self.speak = speak and (pyttsx3 is not None)
        self.engine = pyttsx3.init() if self.speak else None
        self.queue = asyncio.Queue()
        self.task=None
    async def _run(self):
        if websockets is None: return
        async with websockets.connect(self.url) as ws:
            while True:
                payload = await self.queue.get()
                await ws.send(json.dumps(payload))
                final=None
                while True:
                    msg = await ws.recv()
                    obj=json.loads(msg)
                    if "final" in obj:
                        final=obj["final"]; break
                if self.engine and final: self.engine.say(final); self.engine.runAndWait()
    def start(self):
        if websockets is None: return
        loop=asyncio.get_event_loop()
        if loop.is_running():
            self.task = asyncio.create_task(self._run())
        else:
            self.task = loop.create_task(self._run())
    def enqueue(self, payload):
        try:
            loop=asyncio.get_event_loop()
            if loop.is_running(): self.queue.put_nowait(payload)
            else: loop.run_until_complete(self.queue.put(payload))
        except Exception: pass
