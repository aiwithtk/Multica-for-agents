#!/usr/bin/env python3
"""
Supprime un commentaire YouTube avec rate‑limiting et log.
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
def delete_comment(comment_id: str) -> Dict[str, Any]:
    """
    Supprime un commentaire (doit appartenir à l'utilisateur authentifié).
    
    Args:
        comment_id: ID du commentaire à supprimer
        None
    
    Returns:
        Réponse de l'API ou dict d'erreur.
    """
    youtube = get_youtube_client()
    if not youtube:
        return {'success': False, 'error': 'Not authenticated'}
    
    target = {"commentId": comment_id}
    try:
        res = youtube.comments().delete(id=comment_id).execute()
        result, error = {"data": res}, None
        if error:
            log_action(
                action_type="DELETE_COMMENT",
                target=target,
                success=False,
                error=error,
                quota_used=50
            )
            return {"success": False, "error": error}
        
        log_action(
            action_type="DELETE_COMMENT",
            target=target,
            success=True,
            response=result,
            quota_used=50
        )
        return {"success": True, "data": result.get("data", {})}
    
    except Exception as e:
        error_msg = str(e)
        log_action(
            action_type="DELETE_COMMENT",
            target=target,
            success=False,
            error=error_msg,
            quota_used=50
        )
        return {"success": False, "error": error_msg}


def main():
    if len(sys.argv) < 2:
        print("Usage: python delete_comment.py <commentId> [account_alias]")
        print("Example: python delete_comment.py UgxeL_zwJICryCEB_HR4AaABAg")
        sys.exit(1)
    
    comment_id = sys.argv[1]
    account = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Afficher l'état du quota avant
    status = get_quota_status()
    print(f"Quota utilisé aujourd'hui : {status['quota_used_today']}/{status['quota_daily_limit']}")
    if not status['can_perform_action']:
        print("❌ Quota insuffisant. Abandon.")
        sys.exit(2)
    
    print(f"Suppression du commentaire {comment_id}")
    result = delete_comment(comment_id, account)
    
    if result.get("success"):
        print("✅ Commentaire supprimé.")
    else:
        print(f"❌ Erreur : {result.get('error')}")
        sys.exit(3)


if __name__ == "__main__":
    main()