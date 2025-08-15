import os, json, hashlib, asyncio, datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

from security.vault import Vault
from senses.supabase_io import sb_ok, sb_save_directive_meta

app = FastAPI(title="Agent One API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

BASE = None
MASTER_PHRASE = None
ROOT_ACCESS_CODE = None

def boot_env(base_dir:str):
    global BASE, MASTER_PHRASE, ROOT_ACCESS_CODE
    BASE = Path(base_dir)
    load_dotenv(BASE/"config/.env.agent_one")
    MASTER_PHRASE = os.getenv("MASTER_PHRASE","Neo Pulse").strip()
    ROOT_ACCESS_CODE = os.getenv("ROOT_ACCESS_CODE","").strip()

@app.get("/health")
async def health():
    ok, why = sb_ok()
    return {"ok": ok, "supabase": (why if not ok else "ok"), "ts": datetime.datetime.utcnow().isoformat()}

@app.post("/vault/store")
async def vault_store(req: Request, x_access_code: str = Header(default="")):
    if x_access_code != ROOT_ACCESS_CODE:
        return JSONResponse({"ok": False, "error": "access_denied"}, status_code=403)
    body = await req.json()
    title = body.get("title","untitled")
    content = body.get("content","")
    mode = body.get("mode","directive") # directive|note
    vault = Vault(base_dir=BASE)
    sealed_path, meta = vault.encrypt_and_store(title, content, mode=mode)
    sb_save_directive_meta(title, meta)
    return {"ok": True, "stored": str(sealed_path), "meta": meta}

@app.post("/vault/unlock")
async def vault_unlock(req: Request):
    # minimal unlock via code (2FA/TOTP or chain sig can be layered in security.vault)
    body = await req.json()
    code = body.get("code","")
    vault = Vault(base_dir=BASE)
    ok = vault.unlock_with_code(code)
    return {"ok": ok}

@app.post("/agent/verify_phrase")
async def verify_phrase(req: Request):
    body = await req.json()
    txt = (body.get("text","") or "").strip()
    obeys = txt.lower().startswith((MASTER_PHRASE or "Neo Pulse").lower())
    return {"ok": True, "obeys": obeys}

@app.websocket("/ws")
async def ws_chat(ws: WebSocket):
    await ws.accept()
    await ws.send_text("Agent One online. Say 'Neo Pulse <command>' for privileged ops.")
    try:
        while True:
            msg = await ws.receive_text()
            if msg.lower().startswith((MASTER_PHRASE or "Neo Pulse").lower()):
                await ws.send_text(f"✓ Master phrase accepted.\nAck: {msg}")
            else:
                await ws.send_text("…listening (non-privileged). Prefix with master phrase for root actions.")
    except WebSocketDisconnect:
        return

def run_api(base_dir:str):
    boot_env(base_dir)
    uvicorn.run(app, host="0.0.0.0", port=8787, log_level="warning")
