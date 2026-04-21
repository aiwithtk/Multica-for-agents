#!/usr/bin/env python3
"""
Logger centralisé pour les actions d'écriture YouTube.
Écrit dans un fichier JSON structuré et sur stdout.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

LOG_DIR = "logs"
LOG_FILE_TEMPLATE = "actions_{date}.json"


def ensure_log_dir():
    """Crée le répertoire logs/ s'il n'existe pas."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def get_today_log_path() -> str:
    """Retourne le chemin du fichier journal du jour."""
    ensure_log_dir()
    today = datetime.utcnow().date().isoformat()
    filename = LOG_FILE_TEMPLATE.format(date=today)
    return os.path.join(LOG_DIR, filename)


def load_today_logs() -> list:
    """Charge les logs du jour (ou liste vide)."""
    path = get_today_log_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                # Fichier JSON lignes par lignes
                logs = []
                for line in f:
                    line = line.strip()
                    if line:
                        logs.append(json.loads(line))
                return logs
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: could not load log file {path}: {e}", file=sys.stderr)
    return []


def log_action(
    action_type: str,
    target: Dict[str, Any],
    success: bool,
    response: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    quota_used: int = 50,
    extra: Optional[Dict[str, Any]] = None
):
    """
    Journalise une action.
    
    Args:
        action_type: type d'action (ex. "CREATE_COMMENT_REPLY")
        target: dict décrivant la cible (videoId, commentId, etc.)
        success: True si l'action a réussi
        response: réponse de l'API (si succès)
        error: message d'erreur (si échec)
        quota_used: quota consommé (par défaut 50)
        extra: métadonnées supplémentaires
    """
    ensure_log_dir()
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action_type,
        "target": target,
        "success": success,
        "quota_used": quota_used,
        "response": response,
        "error": error,
        "extra": extra or {}
    }
    # Écriture en mode append, une ligne JSON par entrée
    path = get_today_log_path()
    with open(path, "a") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    # Aussi afficher sur stdout (format lisible)
    status = "✅" if success else "❌"
    print(f"{status} [{log_entry['timestamp']}] {action_type} on {target}")
    if error:
        print(f"   Error: {error}")
    return log_entry


def get_recent_logs(limit: int = 50) -> list:
    """Retourne les logs les plus récents (tous fichiers confondus)."""
    logs = []
    if os.path.exists(LOG_DIR):
        # Parcourir les fichiers logs/actions_*.json
        for fname in sorted(os.listdir(LOG_DIR), reverse=True):
            if fname.startswith("actions_") and fname.endswith(".json"):
                path = os.path.join(LOG_DIR, fname)
                try:
                    with open(path, "r") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                logs.append(json.loads(line))
                except (json.JSONDecodeError, IOError):
                    continue
            if len(logs) >= limit:
                break
    # Trier par timestamp décroissant
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return logs[:limit]


def summary_today() -> Dict[str, Any]:
    """Résumé des actions du jour."""
    logs = load_today_logs()
    total = len(logs)
    success = sum(1 for l in logs if l.get("success"))
    failed = total - success
    quota_total = sum(l.get("quota_used", 0) for l in logs)
    actions_by_type = {}
    for l in logs:
        t = l.get("action", "unknown")
        actions_by_type[t] = actions_by_type.get(t, 0) + 1
    
    return {
        "date": datetime.utcnow().date().isoformat(),
        "total_actions": total,
        "successful": success,
        "failed": failed,
        "quota_used": quota_total,
        "actions_by_type": actions_by_type
    }


if __name__ == "__main__":
    # Affiche le résumé du jour
    summary = summary_today()
    print(json.dumps(summary, indent=2))
    print(f"\nDernières actions ({len(get_recent_logs(5))}):")
    for log in get_recent_logs(5):
        ts = log.get("timestamp", "")[:19]
        status = "✅" if log.get("success") else "❌"
        print(f"  {ts} {status} {log.get('action')} -> {log.get('target')}")