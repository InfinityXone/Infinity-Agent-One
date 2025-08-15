import os, json, time, base64, secrets, datetime
from pathlib import Path
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class Vault:
    def __init__(self, base_dir:Path):
        self.base = Path(base_dir)
        load_dotenv(self.base/"config/.env.agent_one")
        self.dir = self.base/"vault"
        self.kv  = self.dir/"keyvault"
        self.log = self.dir/"logs"/"vault.log"
        self.master_phrase = os.getenv("MASTER_PHRASE","Neo Pulse").strip()
        self.root_code = os.getenv("ROOT_ACCESS_CODE","").strip()
        self.session_key_path = self.kv/"session.key"
        self.session_key = None

    def _log(self, msg:str):
        ts = datetime.datetime.utcnow().isoformat()
        self.log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log,"a") as f: f.write(f"[{ts}] {msg}\n")

    def _ensure_session(self):
        self.kv.mkdir(parents=True, exist_ok=True)
        if self.session_key and len(self.session_key)==32: return
        if self.session_key_path.exists():
            self.session_key = self.session_key_path.read_bytes()
        else:
            self.session_key = secrets.token_bytes(32) # AES-256 key
            self.session_key_path.write_bytes(self.session_key)
            os.chmod(self.session_key_path, 0o600)

    def unlock_with_code(self, code:str)->bool:
        ok = (code.strip() == self.root_code and len(code.strip())>=8)
        self._log(f"unlock attempt: {'ok' if ok else 'fail'}")
        return ok

    def encrypt_and_store(self, title:str, content:str, mode:str="directive"):
        self._ensure_session()
        aead = AESGCM(self.session_key)
        nonce = secrets.token_bytes(12)
        ct = aead.encrypt(nonce, content.encode("utf-8"), None)
        blob = base64.b64encode(nonce+ct).decode("ascii")
        ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        fn = f"{mode}_{ts}_{title.replace(' ','_')}.enc"
        outp = self.base/"vault"/"directives"/fn
        outp.write_text(blob)
        meta = {"title": title, "mode": mode, "file": fn, "ts": ts, "bytes": len(blob)}
        self._log(f"store: {meta}")
        return outp, meta

    def record_event(self, kind:str, data:dict):
        self._log(f"event::{kind}::{json.dumps(data)[:500]}")
