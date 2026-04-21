#!/usr/bin/env python3
"""
Rate limiter pour les écritures YouTube (coût 50 unités/quota).
Garde une trace des actions récentes et espace les requêtes.
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Coût en quota par action d'écriture
QUOTA_COST = 50
# Quota quotidien par défaut
DAILY_QUOTA = 10_000
# Délai minimum entre deux écritures (secondes)
MIN_DELAY = 1.0

STATE_FILE = "/tmp/youtube_writer_state.json"


def load_state() -> Dict[str, Any]:
    """Charge l'état depuis le fichier, ou crée un état vide."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "last_action_time": None,
        "quota_used_today": 0,
        "quota_reset_date": datetime.utcnow().date().isoformat(),
        "actions_log": []
    }


def save_state(state: Dict[str, Any]):
    """Sauvegarde l'état dans le fichier."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def reset_if_new_day(state: Dict[str, Any]) -> Dict[str, Any]:
    """Réinitialise le quota utilisé si on est passé à un nouveau jour."""
    today = datetime.utcnow().date().isoformat()
    if state.get("quota_reset_date") != today:
        state["quota_used_today"] = 0
        state["quota_reset_date"] = today
        # Garder seulement les logs des dernières 24h
        cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        state["actions_log"] = [
            a for a in state.get("actions_log", [])
            if a.get("timestamp", "") > cutoff
        ]
    return state


def check_quota(state: Dict[str, Any]) -> tuple[bool, int, int]:
    """
    Vérifie si l'action est possible sans dépasser le quota.
    Retourne (ok, quota_used, quota_remaining).
    """
    quota_used = state.get("quota_used_today", 0)
    remaining = DAILY_QUOTA - quota_used
    ok = remaining >= QUOTA_COST
    return ok, quota_used, remaining


def wait_if_needed(state: Dict[str, Any]):
    """Attend le délai minimum depuis la dernière action."""
    last = state.get("last_action_time")
    if last:
        elapsed = time.time() - last
        if elapsed < MIN_DELAY:
            time.sleep(MIN_DELAY - elapsed)


def record_action(state: Dict[str, Any], action_type: str, target: str):
    """
    Enregistre une action dans l'état.
    Met à jour le quota, l'heure, et ajoute un log.
    """
    state = reset_if_new_day(state)
    state["quota_used_today"] = state.get("quota_used_today", 0) + QUOTA_COST
    state["last_action_time"] = time.time()
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action_type,
        "target": target,
        "quota_cost": QUOTA_COST
    }
    state.setdefault("actions_log", []).append(log_entry)
    # Garder max 1000 logs
    if len(state["actions_log"]) > 1000:
        state["actions_log"] = state["actions_log"][-1000:]
    
    save_state(state)
    return state


def quota_decorator(func):
    """
    Décorateur à appliquer aux fonctions d'action d'écriture.
    Vérifie le quota, attend le délai, enregistre l'action.
    """
    def wrapper(*args, **kwargs):
        state = load_state()
        state = reset_if_new_day(state)
        
        ok, used, remaining = check_quota(state)
        if not ok:
            raise RuntimeError(
                f"Quota insuffisant. Utilisé : {used}/{DAILY_QUOTA}, "
                f"reste {remaining}, besoin {QUOTA_COST}."
            )
        
        wait_if_needed(state)
        
        # Exécute la fonction
        result = func(*args, **kwargs)
        
        # Enregistre l'action (simplifié : target = premier arg)
        target = str(args[0]) if args else "unknown"
        record_action(state, func.__name__, target)
        
        return result
    return wrapper


def get_quota_status() -> Dict[str, Any]:
    """Retourne l'état actuel du quota."""
    state = load_state()
    state = reset_if_new_day(state)
    ok, used, remaining = check_quota(state)
    return {
        "quota_used_today": used,
        "quota_daily_limit": DAILY_QUOTA,
        "quota_remaining": remaining,
        "can_perform_action": ok,
        "quota_reset_date": state.get("quota_reset_date"),
        "last_action_time": state.get("last_action_time"),
        "actions_today": len([
            a for a in state.get("actions_log", [])
            if a.get("timestamp", "").startswith(state.get("quota_reset_date", ""))
        ])
    }


if __name__ == "__main__":
    # Affiche l'état du quota
    status = get_quota_status()
    print(json.dumps(status, indent=2))
    print(f"Prochaine action possible : {status['can_perform_action']}")