import os, sys, time, json, threading, datetime
from dotenv import load_dotenv
from pathlib import Path

BASE = Path(__file__).resolve().parent
load_dotenv(BASE/"config/.env.agent_one")

MASTER_PHRASE = os.getenv("MASTER_PHRASE","Neo Pulse").strip()
ROOT_ACCESS_CODE = os.getenv("ROOT_ACCESS_CODE","").strip()

# Subsystems
from security.vault import Vault
from evolution.heartbeat import Heartbeat
from evolution.evolve import OffTimeLearner
from api.server import run_api
from senses.supabase_io import ensure_schema
from senses.supabase_io import sb_ok

LOG = BASE/"logs/agent_one.log"

def log(msg):
    ts = datetime.datetime.utcnow().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f: f.write(line+"\n")

def bootstrap():
    log("Boot: loading vault & verifying Supabase")
    v = Vault(base_dir=BASE)
    ok, why = sb_ok()
    if not ok:
        log(f"Supabase check FAILED: {why}")
    else:
        # ensure tables for metrics + directives index
        ensure_schema()
        log("Supabase schema OK")
    return v

def start_brain(vault: Vault):
    # Heartbeat = natural rhythm scheduler
    hb = Heartbeat(base_dir=BASE)
    t_hb = threading.Thread(target=hb.run, daemon=True)
    t_hb.start()

    # Off-time learner (night scraping / ingestion)
    learner = OffTimeLearner(base_dir=BASE, vault=vault)
    t_learn = threading.Thread(target=learner.run, daemon=True)
    t_learn.start()

    # Web API (chat, vault ops, evolution hooks)
    t_api = threading.Thread(target=run_api, kwargs={"base_dir":str(BASE)}, daemon=True)
    t_api.start()

    log("Brain online: heartbeat, learner, API running")
    return hb, learner

def obey_master(command: str):
    return command.strip().lower().startswith(MASTER_PHRASE.lower())

def main():
    v = bootstrap()
    start_brain(v)
    log("Agent One ready. Listening for directives…")

    # Simple stdin loop for local control (optional)
    while True:
        try:
            line = sys.stdin.readline()
            if not line: time.sleep(0.5); continue
            if obey_master(line):
                log(f"MASTER directive received: {line.strip()}")
                v.record_event("master_directive", {"text": line.strip()})
            else:
                log(f"Ignored (no master phrase): {line.strip()}")
        except Exception as e:
            log(f"Loop error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
