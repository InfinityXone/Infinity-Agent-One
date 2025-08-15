import os, datetime
from dotenv import load_dotenv

try:
    from supabase import create_client
except Exception:
    create_client = None

load_dotenv(os.path.expanduser("~/Downloads/agent_one/config/.env.agent_one"))

URL = os.getenv("SUPABASE_URL","")
KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY","")

def _cli():
    if not (URL and KEY) or (create_client is None):
        return None, "missing_url_or_key"
    try:
        return create_client(URL, KEY), None
    except Exception as e:
        return None, str(e)

def sb_ok():
    cli, err = _cli()
    if not cli:
        return False, err
    try:
        cli.table("directives_meta").select("*").limit(1).execute()
        return True, "ok"
    except Exception:
        # might not exist yet
        return True, "ok_but_tables_missing"

def ensure_schema():
    cli, err = _cli()
    if not cli: return
    try:
        cli.table("directives_meta").select("*").limit(1).execute()
    except Exception:
        # create via RPC helper if you have one; else ignore (manual SQL recommended)
        pass

def sb_save_directive_meta(title:str, meta:dict):
    cli, err = _cli()
    if not cli: return
    try:
        row = {"title": title, "ts": datetime.datetime.utcnow().isoformat(), "meta": meta}
        cli.table("directives_meta").insert(row).execute()
    except Exception:
        pass
