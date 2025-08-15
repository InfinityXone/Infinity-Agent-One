import logging, subprocess

logging.basicConfig(filename="logs/executor.log", level=logging.INFO)

def execute_command(command, payload):
    logging.info(f"Executing command: {command} with payload: {payload}")
    try:
        if command == "scan_faucets":
            from modules.faucet_scanner import scan
            return scan(payload)
        elif command == "crawl_web":
            from modules.web_crawler import crawl
            return crawl(payload)
        elif command == "shell":
            return subprocess.check_output(payload, shell=True).decode()
        else:
            return {"status": "unknown_command"}
    except Exception as e:
        logging.error(f"Execution error: {str(e)}")
        return {"status": "error", "error": str(e)}
