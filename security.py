import os
from fastapi import HTTPException, Request

API_KEY = os.getenv("API_KEY")
ROOT_ACCESS_CODE = os.getenv("ROOT_ACCESS_CODE")
IP_WHITELIST = os.getenv("IP_WHITELIST", "").split(",")

def verify_api_key(request: Request):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    client_ip = request.client.host
    if IP_WHITELIST and not any(client_ip.startswith(ip.strip()) for ip in IP_WHITELIST):
        raise HTTPException(status_code=403, detail="IP not allowed")

def verify_root_code(code: str):
    if code != ROOT_ACCESS_CODE:
        raise HTTPException(status_code=403, detail="Invalid root access code")
