import os, time, subprocess, jwt
from typing import Optional, Literal
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

HANDSHAKE = os.getenv("HANDSHAKE_HEADER", "NEO-PULSE")
SECRET    = os.getenv("INFINITY_BROKER_SECRET", "change-me")
AGENT_ID  = os.getenv("AGENT_ID", "FinSynapse")

class ExecBody(BaseModel):
    action: Literal["run_script","echo","health"] = "echo"
    payload: dict = {}

app = FastAPI(title="Infinity Broker (API AI)", version="1.0.0")

def _require_handshake(x_handshake: Optional[str]):
    if x_handshake != HANDSHAKE:
        raise HTTPException(status_code=401, detail="bad_handshake")

def _auth_ok(auth: Optional[str]) -> bool:
    if not auth or not auth.startswith("Bearer "): return False
    token = auth.split(" ",1)[1]
    if token == SECRET: return True
    try:
        jwt.decode(token, SECRET, algorithms=["HS256"])
        return True
    except Exception:
        return False

@app.get("/health")
def health(): return {"ok": True, "ts": int(time.time())}

@app.get("/token")
def token(x_handshake: Optional[str] = Header(default=None)):
    _require_handshake(x_handshake)
    now = int(time.time())
    tok = jwt.encode(
        {"iss":"infinity-agent-one","sub":AGENT_ID,"ai_role":"api-ai","iat":now,"exp":now+3600},
        SECRET, algorithm="HS256"
    )
    return {"token": tok}

@app.post("/exec")
async def exec_action(
    body: ExecBody,
    request: Request,
    x_handshake: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
    agent_id: Optional[str] = Header(default=None),
):
    _require_handshake(x_handshake)
    if not _auth_ok(authorization):
        raise HTTPException(status_code=401, detail="bad_token")

    if body.action == "health":
        return {"ok": True, "pong": "health", "ts": int(time.time())}

    if body.action == "echo":
        return {"ok": True, "echo": body.payload, "agent_id": agent_id or AGENT_ID}

    if body.action == "run_script":
        cmd = (body.payload or {}).get("cmd","")
        allow = {"whoami","uname -a","pwd"}  # expand cautiously
        if cmd not in allow:
            raise HTTPException(status_code=403, detail="cmd_not_allowed")
        out = subprocess.check_output(cmd, shell=True, text=True)
        return {"ok": True, "stdout": out}

    return {"ok": False, "error": "unknown_action"}
