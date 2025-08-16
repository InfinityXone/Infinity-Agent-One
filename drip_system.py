import time, requests, os, json, traceback
from modules import faucet_scanner
import wallet_manager

API = "http://127.0.0.1:8001"
HANDSHAKE = {"x-handshake":"NEO-PULSE"}

def get_token():
    try:
        r = requests.get(f"{API}/token", headers=HANDSHAKE, timeout=5)
        return r.json()["token"]
    except Exception as e:
        print("❌ Token error:", e)
        return None

def exec_cmd(token, action, payload):
    try:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        r = requests.post(f"{API}/exec", headers=headers, json={"action":action,"payload":payload}, timeout=20)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def drip_loop():
    while True:
        try:
            token = get_token()
            if not token:
                time.sleep(10)
                continue

            # 1. Scan for faucets
            faucets = faucet_scanner.scan()
            print(f"🔎 Found {len(faucets)} faucets")

            # 2. Rotate wallet
            wallet = wallet_manager.get_next_wallet()
            print(f"💳 Using wallet {wallet['address']}")

            # 3. Attempt to claim from each faucet
            for f in faucets:
                try:
                    res = faucet_scanner.claim(f, wallet)
                    log_entry = {
                        "faucet": f,
                        "wallet": wallet["address"],
                        "result": res,
                        "time": time.ctime()
                    }
                    print("✅ Claim:", log_entry)

                    # write to broker logs
                    exec_cmd(token, "write_file", {
                        "path": "/home/infinity-x-one/Infinity-Agent-One/logs/drip_claims.log",
                        "data": json.dumps(log_entry) + "\n"
                    })
                except Exception as e:
                    print("⚠️ Claim error:", e)
                    continue

            time.sleep(300)  # wait 5 min before next sweep
        except Exception as e:
            print("🔥 Drip loop error:", traceback.format_exc())
            time.sleep(30)

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    print("🚀 Infinity Agent One — Drip System Started")
    drip_loop()
