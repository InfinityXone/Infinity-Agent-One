from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse
import os, jwt, time, subprocess, base64

app = FastAPI()

SECRET = os.getenv("INFINITY_BROKER_SECRET", "dev-secret")
ALG = "HS256"

def verify_token(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        return False
    token = authorization.split(" ",1)[1]
    try:
        jwt.decode(token, SECRET, algorithms=[ALG])
        return True
    except:
        return False

@app.get("/token")
async def issue_token(x_handshake: str = Header(None)):
    if x_handshake != "NEO-PULSE":
        return JSONResponse({"error": "invalid handshake"}, status_code=403)
    payload = {"iat": int(time.time()), "exp": int(time.time()) + 3600}
    token = jwt.encode(payload, SECRET, algorithm=ALG)
    return {"token": token}

@app.post("/exec")
async def exec_cmd(req: Request, authorization: str = Header(None)):
    if not verify_token(authorization):
        return JSONResponse({"error": "unauthorized"}, status_code=403)

    if action == "supabase_push":
        url = os.getenv("SUPABASE_URL"); key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not (url and key):
            return {"error":"SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set"}
        cmd = "supabase db push || true"
        out = subprocess.getoutput(cmd)
        return {"ok": True, "out": out}

    if action == "supabase_storage":
        bucket = payload.get("bucket"); path = payload.get("path"); data = payload.get("data")
        if not (bucket and path and data):
            return {"error":"missing bucket/path/data"}
        os.makedirs("/tmp/supa", exist_ok=True)
        fpath = f"/tmp/supa/{os.path.basename(path)}"
        with open(fpath,"w") as f: f.write(data)
        cmd = f"supabase storage upload {bucket}/{path} {fpath} --bucket-id {bucket} --replace"
        out = subprocess.getoutput(cmd)
        return {"ok": True, "out": out}

    body = await req.json()
    action = body.get("action")
    payload = body.get("payload", {})

    # --- Gateway actions ---
    if action == "run_script":
        cmd = payload.get("cmd")
        if not cmd: return {"error": "missing cmd"}
        out = subprocess.getoutput(cmd)
        return {"ok": True, "cmd": cmd, "out": out}

    if action == "git_clone":
        repo = payload.get("repo"); path = payload.get("path","./repo")
        if not repo: return {"error":"missing repo"}
        out = subprocess.getoutput(f"git clone {repo} {path}")
        return {"ok": True, "out": out}

    if action == "git_push":
        path = payload.get("path",".")
        cmds = [
            f"cd {path} && git add -A",
            f"cd {path} && git commit -m 'auto-commit' || true",
            f"cd {path} && git push || true"
        ]
        out = "\n".join(subprocess.getoutput(c) for c in cmds)
        return {"ok": True, "out": out}

    if action == "vercel_deploy":
        path = payload.get("path",".")
        token = os.getenv("VERCEL_TOKEN","")
        if not token: return {"error":"VERCEL_TOKEN not set"}
        cmd = f"cd {path} && vercel --prod --confirm --token {token}"
        out = subprocess.getoutput(cmd)
        return {"ok": True, "out": out}

    if action == "write_file":
        path = payload.get("path"); data = payload.get("data")
        if not path or data is None: return {"error":"missing path or data"}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path,"w") as f: f.write(data)
        return {"ok": True, "path": path, "size": len(data)}

    if action == "read_file":
        path = payload.get("path")
        if not path or not os.path.exists(path): return {"error":"missing or not found"}
        with open(path,"r") as f: data=f.read()
        return {"ok": True, "path": path, "data": data}

    return {"error": f"unknown action {action}"}
