#!/usr/bin/env python3
import os, sys, json, requests
from pathlib import Path
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parents[1]
load_dotenv(BASE/"config/.env.agent_one")
ACCESS = os.getenv("ROOT_ACCESS_CODE","")

API = "http://127.0.0.1:8787"

def main():
    if len(sys.argv)<3:
        print("Usage: neo directive \"Title\" \"content...\"")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd != "directive":
        print("Only 'directive' supported here.")
        sys.exit(1)
    title = sys.argv[2]
    content = " ".join(sys.argv[3:]) if len(sys.argv)>3 else ""
    r = requests.post(f"{API}/vault/store", headers={"x_access_code": ACCESS}, json={"title": title, "content": content, "mode":"directive"})
    print(r.json())

if __name__ == "__main__":
    main()
