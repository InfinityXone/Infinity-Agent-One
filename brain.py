import os, time, logging, threading
from supabase import create_client
from executor import execute_command
from ipc_bridge import ipc_server

logging.basicConfig(filename="logs/agent_one.log", level=logging.INFO)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

def brain_loop():
    while True:
        try:
            result = supabase_client.table("agent_directives") \
                .select("*").eq("status", "pending") \
                .order("timestamp", desc=False).execute()
            for row in result.data:
                execute_command(row["command"], row["payload"])
                supabase_client.table("agent_directives") \
                    .update({"status": "done"}).eq("id", row["id"]).execute()
        except Exception as e:
            logging.error(f"Brain loop error: {str(e)}")
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=brain_loop, daemon=True).start()
    ipc_server()
