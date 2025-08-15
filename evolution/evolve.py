import os, time, datetime, asyncio, aiohttp, json
from pathlib import Path

SOURCES = [
    "https://news.ycombinator.com/",
    "https://github.com/trending",
    "https://www.coindesk.com/",
    "https://defillama.com/news"
]

class OffTimeLearner:
    """
    Runs when you're likely offline/asleep (local night hours).
    Scrapes a few sources and stores snapshots into vault logs for later ingestion.
    """
    def __init__(self, base_dir:Path, vault):
        self.base = Path(base_dir)
        self.vault = vault
        self.log = self.base/"logs/learner.log"

    def asleep_window(self)->bool:
        # Rough guess: 02:00 - 07:00 local
        hour = datetime.datetime.now().hour
        return 2 <= hour <= 7

    async def fetch(self, url:str):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=15) as r:
                    return url, (await r.text())[:50000]
        except Exception as e:
            return url, f"ERR:{e}"

    async def run_once(self):
        tasks = [self.fetch(u) for u in SOURCES]
        res = await asyncio.gather(*tasks)
        stamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        bundle = {"ts": stamp, "items":[{"url":u, "snippet":txt[:4000]} for u,txt in res]}
        self.vault.record_event("night_learning", {"count": len(res)})
        # store encrypted snapshot
        self.vault.encrypt_and_store(f"nightlearn_{stamp}", json.dumps(bundle), mode="note")

    def run(self):
        while True:
            try:
                if self.asleep_window():
                    asyncio.run(self.run_once())
                time.sleep(300)  # check every 5 mins
            except Exception as e:
                with open(self.log,"a") as f: f.write(f"[{datetime.datetime.utcnow().isoformat()}] learn_err {e}\n")
                time.sleep(60)
