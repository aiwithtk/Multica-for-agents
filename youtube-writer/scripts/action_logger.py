import os
import json
import time
from typing import Dict, Any, List

LOG_FILE = "/root/.openclaw/logs/youtube_actions.json"

def log_action(action_type: str, target: Dict[str, Any], success: bool, response: Any = None, error: str = None, quota_used: int = 50):
    """Enregistre une action YouTube dans les logs."""
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": action_type,
        "target": target,
        "success": success,
        "response": response,
        "error": error,
        "quota_used": quota_used
    }
    
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    
    logs.append(log_entry)
    
    # Garder seulement les 1000 derniers logs
    if len(logs) > 1000:
        logs = logs[-1000:]
        
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

def get_recent_logs(limit: int = 10) -> List[Dict[str, Any]]:
    """Récupère les dernières actions."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, 'r') as f:
        try:
            return json.load(f)[-limit:]
        except json.JSONDecodeError:
            return []

def summary_today() -> Dict[str, Any]:
    """Calcule les stats d'utilisation du jour."""
    today = time.strftime("%Y-%m-%d")
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                return {"total_actions": 0, "successful": 0, "failed": 0, "quota_used": 0}

    today_logs = [l for l in logs if l["timestamp"].startswith(today)]
    return {
        "total_actions": len(today_logs),
        "successful": len([l for l in today_logs if l["success"]]),
        "failed": len([l for l in today_logs if not l["success"]]),
        "quota_used": sum([l.get("quota_used", 50) for l in today_logs])
    }
