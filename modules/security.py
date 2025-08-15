import os
from fastapi import Request, HTTPException

API_KEY = os.environ.get("AGENT_ONE_API_KEY", "changeme")

def verify_api_key(request: Request):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True
