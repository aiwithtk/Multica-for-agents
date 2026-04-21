#!/usr/bin/env python3
"""
Modère un commentaire YouTube (publish, hold, reject) avec rate‑limiting et log.
"""

import sys
import json
import os
from typing import Dict, Any, Optional, List

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
def moderate_comment(
    comment_ids: List[str],
    moderation_status: str,
    ban_author: bool = False,
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Modère un ou plusieurs commentaires.
    
    Args:
        comment_ids: liste d'IDs de commentaires (pas de threads)
        moderation_status: "published", "heldForReview", "rejected"
        ban_author: si True et status="rejected", bannit l'auteur
        None
    
    Returns:
        Réponse de l'API ou dict d'erreur.
    """
    valid_statuses = ("published", "heldForReview", "rejected")
    if moderation_status not in valid_statuses:
        raise ValueError(f"moderation_status doit être parmi {valid_statuses}")
    
    if ban_author and moderation_status != "rejected":
        raise ValueError("ban_author n'est valide qu'avec moderation_status='rejected'")
    
    youtube = get_youtube_client()
    if not youtube:
        return {'success': False, 'error': 'Not authenticated'}
    
    ids_str = ",".join(comment_ids)
    target = {
        "commentIds": comment_ids,
        "moderationStatus": moderation_status,
        "banAuthor": ban_author
    }
    try:
        arguments = {
            "id": ids_str,
            "moderationStatus": moderation_status
        }
        if moderation_status == "rejected":
            arguments["banAuthor"] = ban_author
        
        result, error = run_composio_tool(
            tool_slug="YOUTUBE_SET_COMMENT_MODERATION_STATUS",
            arguments=arguments,
            account=account
        )
        if error:
            log_action(
                action_type="SET_COMMENT_MODERATION_STATUS",
                target=target,
                success=False,
                error=error,
                quota_used=50
            )
            return {"success": False, "error": error}
        
        log_action(
            action_type="SET_COMMENT_MODERATION_STATUS",
            target=target,
            success=True,
            response=result,
            quota_used=50
        )
        return {"success": True, "data": result.get("data", {})}
    
    except Exception as e:
        error_msg = str(e)
        log_action(
            action_type="SET_COMMENT_MODERATION_STATUS",
            target=target,
            success=False,
            error=error_msg,
            quota_used=50
        )
        return {"success": False, "error": error_msg}


def main():
    if len(sys.argv) < 3:
        print("Usage: python moderate_comment.py <commentId1> [commentId2 ...] <status> [--ban] [account_alias]")
        print("       status = published, heldForReview, rejected")
        print("       --ban : bannit l'auteur (uniquement avec rejected)")
        print("Example: python moderate_comment.py UgxeL_zwJICryCEB_HR4AaABAg published")
        sys.exit(1)
    
    # Parser les arguments
    args = sys.argv[1:]
    ban = False
    if "--ban" in args:
        ban = True
        args.remove("--ban")
    
    # Dernier arg est le status, avant ça les IDs
    status = args[-1]
    comment_ids = args[:-1]
    
    # Optionnel : dernier arg pourrait être account alias si pas de --ban
    account = None
    if len(comment_ids) > 0 and comment_ids[-1].startswith("--"):
        # Pas de compte supplémentaire
        pass
    elif len(comment_ids) > 0 and comment_ids[-1] not in ("published", "heldForReview", "rejected"):
        account = comment_ids.pop()
    
    if not comment_ids:
        print("Aucun commentId fourni.")
        sys.exit(1)
    
    # Afficher l'état du quota avant
    status_quota = get_quota_status()
    print(f"Quota utilisé aujourd'hui : {status_quota['quota_used_today']}/{status_quota['quota_daily_limit']}")
    if not status_quota['can_perform_action']:
        print("❌ Quota insuffisant. Abandon.")
        sys.exit(2)
    
    print(f"Modération {status} sur {len(comment_ids)} commentaire(s)")
    if ban:
        print("   (avec bannissement de l'auteur)")
    
    result = moderate_comment(comment_ids, status, ban, account)
    
    if result.get("success"):
        print(f"✅ Modération appliquée.")
    else:
        print(f"❌ Erreur : {result.get('error')}")
        sys.exit(3)


if __name__ == "__main__":
    main()