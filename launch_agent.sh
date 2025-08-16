#!/bin/bash
set -euo pipefail

BASE_DIR="$HOME/Infinity-Agent-One"
DROPIN="$BASE_DIR/AgentOne_DropIn_Prod_Full.zip"
VENV="$BASE_DIR/.venv"
LOG_DIR="$BASE_DIR/logs"

echo "=== 🚀 Infinity Agent One Advanced Launch ==="

mkdir -p "$BASE_DIR" "$LOG_DIR"

# Unpack drop-in if available
if [ -f "$DROPIN" ]; then
  echo "--- 📦 Unpacking drop-in ---"
  unzip -o "$DROPIN" -d "$BASE_DIR"
fi

# Virtualenv setup
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"

# Install deps
pip install --upgrade pip wheel
pip install groq openai supabase web3 scrapy httpx loguru python-dotenv

### === agent.py ===
cat > "$BASE_DIR/agent.py" <<'PYCODE'
#!/usr/bin/env python3
import os, sys, time, json, asyncio, logging
from loguru import logger
from dotenv import load_dotenv
from supabase import create_client, Client
import httpx
from wallet_manager import WalletManager
from scraper_spider import FaucetSpider

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BROKER_URL = os.getenv("BROKER_URL", "http://localhost:8001/chat")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def query_llm(prompt: str):
    try:
        headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}
        async with httpx.AsyncClient() as client:
            r = await client.post("https://api.groq.com/v1/chat/completions", 
                headers=headers, json={
                    "model": "mixtral-8x7b-32768",
                    "messages": [{"role": "user", "content": prompt}]
                })
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning(f"Groq failed, fallback to OpenAI: {e}")
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

async def broker_loop():
    logger.info("Infinity Agent One online. Listening for broker tasks...")
    wm = WalletManager()
    spider = FaucetSpider()

    while True:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(BROKER_URL, timeout=30)
                if r.status_code == 200:
                    msg = r.json().get("message")
                    if msg:
                        logger.info(f"📥 Broker says: {msg}")
                        if "wallet" in msg.lower():
                            out = wm.rotate_wallets()
                        elif "scrape" in msg.lower():
                            out = await spider.run()
                        else:
                            out = await query_llm(msg)
                        logger.info(f"🤖 Response: {out}")
        except Exception as e:
            logger.error(f"Broker loop error: {e}")
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(broker_loop())
    except KeyboardInterrupt:
        sys.exit(0)
PYCODE

### === wallet_manager.py ===
cat > "$BASE_DIR/wallet_manager.py" <<'PYCODE'
import os, json
class WalletManager:
    def __init__(self):
        self.wallets = json.loads(os.getenv("WALLETS", "[]"))
        self.index = 0
    def rotate_wallets(self):
        if not self.wallets:
            return "⚠️ No wallets configured"
        self.index = (self.index + 1) % len(self.wallets)
        active = self.wallets[self.index]
        return f"🔄 Using wallet {self.index+1}/{len(self.wallets)}: {active['address']}"
    def collect_fees(self, target):
        return f"💰 Fees collected to {target}"
PYCODE

### === scraper_spider.py ===
cat > "$BASE_DIR/scraper_spider.py" <<'PYCODE'
import scrapy, asyncio
from scrapy.crawler import CrawlerProcess

class FaucetSpider(scrapy.Spider):
    name = "faucets"
    start_urls = ["https://faucetpay.io/faucet-list"]

    def parse(self, response):
        for link in response.css("a::attr(href)").getall():
            yield {"link": link}

    async def run(self):
        loop = asyncio.get_event_loop()
        process = CrawlerProcess(settings={"LOG_ENABLED": False})
        process.crawl(FaucetSpider)
        loop.run_in_executor(None, process.start, True)
        return "🕷️ Faucet spider executed"
PYCODE

echo "--- 🚀 Starting orchestrator ---"
python "$BASE_DIR/agent.py" 2>&1 | tee -a "$LOG_DIR/agent_one.log"
