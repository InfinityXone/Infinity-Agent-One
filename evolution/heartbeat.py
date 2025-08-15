import time, math, datetime, os
from pathlib import Path

class Heartbeat:
    """
    Natural rhythm: we approximate Schumann resonance cycles into a gentle cadence.
    We'll tick every ~7.83 seconds (not 7.83 Hz!) to avoid CPU burn, with day/night modulation.
    """
    def __init__(self, base_dir:Path):
        self.base = Path(base_dir)
        self.log  = self.base/"logs/heartbeat.log"

    def tick(self):
        ts = datetime.datetime.utcnow().isoformat()
        with open(self.log,"a") as f: f.write(f"[{ts}] ♥ heartbeat\n")

    def run(self):
        while True:
            # simple day/night modulation
            hour = datetime.datetime.utcnow().hour
            delay = 6.5 if (hour>=6 and hour<=18) else 9.1
            self.tick()
            time.sleep(delay)
