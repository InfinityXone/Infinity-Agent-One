import logging
from .faucet_scanner import scan

def handle(directive):
    """
    Handles incoming directives.
    Example: {"action": "scan_faucets", "faucets": [...]}
    """
    action = directive.get("action")
    logging.info(f"Processing action: {action}")

    if action == "scan_faucets":
        return scan(directive)
    else:
        return {"status": "error", "message": "Unknown action"}
