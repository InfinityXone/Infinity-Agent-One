import requests, logging, time

def scan(payload):
    """
    Scans a list of faucets and returns their status.
    payload example: {"faucets": ["https://faucet1.com", "https://faucet2.com"]}
    """
    logging.info("🔍 Faucet scan initiated...")
    results = []
    faucets = payload.get("faucets", [])
    if not faucets:
        return {"status": "error", "message": "No faucet list provided"}

    for url in faucets:
        try:
            r = requests.get(url, timeout=8)
            results.append({"url": url, "status": r.status_code, "timestamp": time.time()})
        except Exception as e:
            results.append({"url": url, "error": str(e), "timestamp": time.time()})

    return {"status": "ok", "results": results, "count": len(results)}
