#!/usr/bin/env python3
"""
Poste un commentaire top‑level sur une vidéo YouTube avec rate‑limiting et log.
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
def post_comment(video_id: str, channel_id: str, text: str) -> Dict[str, Any]:
    """
    Poste un commentaire sur une vidéo.
    
    Args:
        video_id: ID de la vidéo
        channel_id: ID de la chaîne qui a uploadé la vidéo
        text: texte du commentaire
        None
    
    Returns:
        Réponse de l'API ou dict d'erreur.
    """
    youtube = get_youtube_client()
    if not youtube:
        return {'success': False, 'error': 'Not authenticated'}
    
    target = {"videoId": video_id, "channelId": channel_id, "textPreview": text[:50]}
    try:
        result, error = run_composio_tool(
            tool_slug="YOUTUBE_POST_COMMENT",
            arguments={
                "videoId": video_id,
                "channelId": channel_id,
                "textOriginal": text
            },
            account=account
        )
        if error:
            log_action(
                action_type="POST_COMMENT",
                target=target,
                success=False,
                error=error,
                quota_used=50
            )
            return {"success": False, "error": error}
        
        log_action(
            action_type="POST_COMMENT",
            target=target,
            success=True,
            response=result,
            quota_used=50
        )
        return {"success": True, "data": result.get("data", {})}
    
    except Exception as e:
        error_msg = str(e)
        log_action(
            action_type="POST_COMMENT",
            target=target,
            success=False,
            error=error_msg,
            quota_used=50
        )
        return {"success": False, "error": error_msg}


def main():
    if len(sys.argv) < 4:
        print("Usage: python post_comment.py <videoId> <channelId> <text> [account_alias]")
        print("Example: python post_comment.py dQw4w9WgXcQ UC_x5XG1OV2P6uZZ5FSM9Ttw 'Super vidéo !'")
        sys.exit(1)
    
    video_id = sys.argv[1]
    channel_id = sys.argv[2]
    text = sys.argv[3]
    account = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Afficher l'état du quota avant
    status = get_quota_status()
    print(f"Quota utilisé aujourd'hui : {status['quota_used_today']}/{status['quota_daily_limit']}")
    if not status['can_perform_action']:
        print("❌ Quota insuffisant. Abandon.")
        sys.exit(2)
    
    print(f"Poste un commentaire sur {video_id} (chaîne {channel_id})")
    print(f"Texte : {text[:80]}...")
    result = post_comment(video_id, channel_id, text, account)
    
    if result.get("success"):
        print("✅ Commentaire posté.")
        if "data" in result:
            print(f"   ID du commentaire : {result['data'].get('id', 'inconnu')}")
    else:
        print(f"❌ Erreur : {result.get('error')}")
        sys.exit(3)


if __name__ == "__main__":
    main()