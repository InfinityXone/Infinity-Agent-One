import os
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from modules import directive_handler
from modules.logger import setup_logger

# ===== Security =====
API_KEY = os.environ.get("AGENT_ONE_API_KEY", "changeme")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Missing Supabase credentials in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===== Logging =====
setup_logger()
logger = logging.getLogger("agent_one_api")

# ===== FastAPI App =====
app = FastAPI(
    title="Agent One API",
    description="Industry-grade AI Agent API with secure directive handling.",
    version="1.0.0"
)

# ===== CORS =====
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://*.vercel.app",
    "https://*.repl.co"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== API Key Auth =====
def verify_api_key(request: Request):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        logger.warning("Unauthorized access attempt.")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

# ===== Routes =====
@app.get("/")
def root():
    return {"status": "ok", "message": "Agent One API is running"}

@app.post("/directive")
async def handle_directive(request: Request, auth: bool = Depends(verify_api_key)):
    try:
        directive = await request.json()
        logger.info(f"Directive received: {directive}")
        
        supabase.table("directives").insert({"directive": directive}).execute()
        result = directive_handler.handle(directive)
        supabase.table("results").insert({"result": result}).execute()

        return {"status": "ok", "data": result}
    except Exception as e:
        logger.error(f"Directive error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
def get_logs(auth: bool = Depends(verify_api_key)):
    log_file = os.path.join(os.path.dirname(__file__), "logs", "agent_one.log")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            return {"logs": f.read().splitlines()}
    else:
        return {"status": "error", "message": "No logs found"}

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Agent One is healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
