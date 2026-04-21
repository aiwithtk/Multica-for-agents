#!/usr/bin/env python3
"""
Like/dislike une vidéo YouTube avec rate‑limiting et log.
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
def like_video(video_id: str, rating: str = "like") -> Dict[str, Any]:
    """
    Like, dislike ou retire le rating d'une vidéo.
    
    Args:
        video_id: ID de la vidéo (11 caractères)
        rating: "like", "dislike", ou "none" (pour retirer)
        None
    
    Returns:
        Réponse de l'API ou dict d'erreur.
    """
    if rating not in ("like", "dislike", "none"):
        raise ValueError("rating doit être 'like', 'dislike' ou 'none'")
    
    youtube = get_youtube_client()
    if not youtube:
        return {'success': False, 'error': 'Not authenticated'}
    
    target = {"videoId": video_id, "rating": rating}
    try:
        res = youtube.videos().rate(id=video_id, rating=rating).execute()
        result, error = {"data": res}, None
        if error:
            log_action(
                action_type="RATE_VIDEO",
                target=target,
                success=False,
                error=error,
                quota_used=50
            )
            return {"success": False, "error": error}
        
        log_action(
            action_type="RATE_VIDEO",
            target=target,
            success=True,
            response=result,
            quota_used=50
        )
        return {"success": True, "data": result.get("data", {})}
    
    except Exception as e:
        error_msg = str(e)
        log_action(
            action_type="RATE_VIDEO",
            target=target,
            success=False,
            error=error_msg,
            quota_used=50
        )
        return {"success": False, "error": error_msg}


def main():
    if len(sys.argv) < 2:
        print("Usage: python like_video.py <videoId> [rating] [account_alias]")
        print("       rating = like (défaut), dislike, none")
        print("Example: python like_video.py dQw4w9WgXcQ like")
        sys.exit(1)
    
    video_id = sys.argv[1]
    rating = sys.argv[2] if len(sys.argv) > 2 else "like"
    account = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Afficher l'état du quota avant
    status = get_quota_status()
    print(f"Quota utilisé aujourd'hui : {status['quota_used_today']}/{status['quota_daily_limit']}")
    if not status['can_perform_action']:
        print("❌ Quota insuffisant. Abandon.")
        sys.exit(2)
    
    print(f"Rating {rating} sur la vidéo {video_id}")
    result = like_video(video_id, rating, account)
    
    if result.get("success"):
        print(f"✅ Rating '{rating}' appliqué.")
    else:
        print(f"❌ Erreur : {result.get('error')}")
        sys.exit(3)


if __name__ == "__main__":
    main()