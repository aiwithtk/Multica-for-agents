#!/usr/bin/env python3
"""
Répond à un commentaire YouTube avec rate‑limiting et log.
"""

import sys
import json
import os
from typing import Dict, Any, Optional

# Gestion des imports relatifs/absolus
try:
    from .rate_limiter import quota_decorator, get_quota_status
    from .action_logger import log_action
except ImportError:
    # Ajouter le répertoire parent au path pour exécution directe
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.rate_limiter import quota_decorator, get_quota_status
    from scripts.action_logger import log_action

try:
    from .auth import get_youtube_client
except ImportError:
    from scripts.auth import get_youtube_client


@quota_decorator
def reply_to_comment(parent_id: str, text: str) -> Dict[str, Any]:
    """
    Répond à un commentaire parent.
    
    Args:
        parent_id: ID du commentaire parent (ex. "Ugzoh2L2gIZm-rzh6hp4AaABAg")
        text: texte de la réponse
        None
    
    Returns:
        Réponse de l'API ou dict d'erreur.
    """
    youtube = get_youtube_client()
    if not youtube:
        return {'success': False, 'error': 'Not authenticated'}
    
    target = {"parentId": parent_id, "textPreview": text[:50]}
    try:
        result, error = run_composio_tool(
            tool_slug="YOUTUBE_CREATE_COMMENT_REPLY",
            arguments={
                "parentId": parent_id,
                "textOriginal": text
            },
            account=account
        )
        if error:
            log_action(
                action_type="CREATE_COMMENT_REPLY",
                target=target,
                success=False,
                error=error,
                quota_used=50
            )
            return {"success": False, "error": error}
        
        log_action(
            action_type="CREATE_COMMENT_REPLY",
            target=target,
            success=True,
            response=result,
            quota_used=50
        )
        return {"success": True, "data": result.get("data", {})}
    
    except Exception as e:
        error_msg = str(e)
        log_action(
            action_type="CREATE_COMMENT_REPLY",
            target=target,
            success=False,
            error=error_msg,
            quota_used=50
        )
        return {"success": False, "error": error_msg}


def main():
    if len(sys.argv) < 3:
        print("Usage: python reply_to_comment.py <parentId> <text> [account_alias]")
        print("Example: python reply_to_comment.py Ugzoh2L2gIZm-rzh6hp4AaABAg 'Merci !'")
        sys.exit(1)
    
    parent_id = sys.argv[1]
    text = sys.argv[2]
    account = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Afficher l'état du quota avant
    status = get_quota_status()
    print(f"Quota utilisé aujourd'hui : {status['quota_used_today']}/{status['quota_daily_limit']}")
    if not status['can_perform_action']:
        print("❌ Quota insuffisant. Abandon.")
        sys.exit(2)
    
    print(f"Réponse à {parent_id} : {text[:60]}...")
    result = reply_to_comment(parent_id, text, account)
    
    if result.get("success"):
        print("✅ Réponse postée.")
        if "data" in result:
            print(f"   ID de la réponse : {result['data'].get('id', 'inconnu')}")
    else:
        print(f"❌ Erreur : {result.get('error')}")
        sys.exit(3)


if __name__ == "__main__":
    main()