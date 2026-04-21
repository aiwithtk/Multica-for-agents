import os
import json
import time
from typing import Dict, Any, Callable, TypeVar

T = TypeVar("T")

QUOTA_FILE = "/root/.openclaw/logs/youtube_quota.json"
DAILY_LIMIT = 10000

def get_quota_status() -> Dict[str, Any]:
    """Lit l'état actuel du quota journalier."""
    today = time.strftime("%Y-%m-%d")
    if not os.path.exists(QUOTA_FILE):
        return {"date": today, "quota_used": 0, "quota_remaining": DAILY_LIMIT}
    
    try:
        with open(QUOTA_FILE, 'r') as f:
            data = json.load(f)
            if data.get("date") != today:
                return {"date": today, "quota_used": 0, "quota_remaining": DAILY_LIMIT}
            return data
    except (json.JSONDecodeError, KeyError):
        return {"date": today, "quota_used": 0, "quota_remaining": DAILY_LIMIT}

def update_quota(cost: int):
    """Met à jour le quota après une action."""
    status = get_quota_status()
    status["quota_used"] += cost
    status["quota_remaining"] = max(0, DAILY_LIMIT - status["quota_used"])
    
    os.makedirs(os.path.dirname(QUOTA_FILE), exist_ok=True)
    with open(QUOTA_FILE, 'w') as f:
        json.dump(status, f)

def quota_decorator(func: Callable[..., Dict[str, Any]]) -> Callable[..., Dict[str, Any]]:
    """Décorateur pour vérifier le quota avant exécution."""
    def wrapper(*args, **kwargs):
        status = get_quota_status()
        if status["quota_remaining"] < 50:
            return {"success": False, "error": "Quota YouTube Data API épuisé pour aujourd'hui."}
        
        result = func(*args, **kwargs)
        if result.get("success"):
            update_quota(result.get("quota_used", 50))
        return result
    return wrapper
