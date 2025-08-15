import os, subprocess, time
from fastapi import Request, HTTPException, Depends
from .security import verify_api_key

SAFE_COMMANDS = ["git", "vercel", "supabase", "ls", "pwd"]

@app.post("/exec")
async def exec_command(request: Request, auth: bool = Depends(verify_api_key)):
    data = await request.json()
    cmd = data.get("cmd", "")
    if not any(cmd.strip().startswith(safe) for safe in SAFE_COMMANDS):
        raise HTTPException(status_code=403, detail="Command not allowed in secure mode")

    log_lines = []
    proc = subprocess.Popen(
        ["bash", "-lc", cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    for line in proc.stdout:
        log_lines.append(line.strip())
    proc.wait()

    with open("$LOG_FILE", "a") as f:
        f.write(f"[{time.ctime()}] CMD: {cmd}\n" + "\n".join(log_lines) + "\n\n")

    return {"success": proc.returncode == 0, "logs": log_lines[-20:]}
