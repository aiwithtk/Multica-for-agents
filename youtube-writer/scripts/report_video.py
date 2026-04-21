#!/usr/bin/env python3
"""
Signale une vidéo YouTube abusive avec rate‑limiting et log.
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
def report_video(
    video_id: str,
    reason_id: str,
    comments: Optional[str] = None,
    language: str = "en",
    secondary_reason_id: Optional[str] = None,
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Signale une vidéo pour contenu abusif.
    
    Args:
        video_id: ID de la vidéo (11 caractères)
        reason_id: code raison (N, V, C, M, E, H)
        comments: texte explicatif (optionnel)
        language: code langue (ex. "fr")
        secondary_reason_id: sous‑raison (optionnel)
        None
    
    Returns:
        Réponse de l'API ou dict d'erreur.
    """
    valid_reasons = ("N", "V", "C", "M", "E", "H")
    if reason_id not in valid_reasons:
        raise ValueError(f"reason_id doit être parmi {valid_reasons}")
    
    youtube = get_youtube_client()
    if not youtube:
        return {'success': False, 'error': 'Not authenticated'}
    
    target = {
        "videoId": video_id,
        "reasonId": reason_id,
        "secondaryReasonId": secondary_reason_id,
        "language": language
    }
    try:
        arguments = {
            "videoId": video_id,
            "reasonId": reason_id,
            "language": language
        }
        if comments:
            arguments["comments"] = comments
        if secondary_reason_id:
            arguments["secondaryReasonId"] = secondary_reason_id
        
        result, error = run_composio_tool(
            tool_slug="YOUTUBE_REPORT_VIDEO_ABUSE",
            arguments=arguments,
            account=account
        )
        if error:
            log_action(
                action_type="REPORT_VIDEO_ABUSE",
                target=target,
                success=False,
                error=error,
                quota_used=50
            )
            return {"success": False, "error": error}
        
        log_action(
            action_type="REPORT_VIDEO_ABUSE",
            target=target,
            success=True,
            response=result,
            quota_used=50
        )
        return {"success": True, "data": result.get("data", {})}
    
    except Exception as e:
        error_msg = str(e)
        log_action(
            action_type="REPORT_VIDEO_ABUSE",
            target=target,
            success=False,
            error=error_msg,
            quota_used=50
        )
        return {"success": False, "error": error_msg}


def main():
    if len(sys.argv) < 3:
        print("Usage: python report_video.py <videoId> <reasonId> [comments] [language] [secondaryReasonId] [account_alias]")
        print("       reasonId = N (Sex/nudity), V (Violent/hateful), C (Child abuse),")
        print("                  M (Medical misinformation), E (Violent extremism), H (Harassment/bullying)")
        print("Example: python report_video.py dQw4w9WgXcQ H 'Contenu harcelant' fr")
        sys.exit(1)
    
    video_id = sys.argv[1]
    reason_id = sys.argv[2]
    comments = sys.argv[3] if len(sys.argv) > 3 else None
    language = sys.argv[4] if len(sys.argv) > 4 else "en"
    secondary_reason_id = sys.argv[5] if len(sys.argv) > 5 else None
    account = sys.argv[6] if len(sys.argv) > 6 else None
    
    # Afficher l'état du quota avant
    status = get_quota_status()
    print(f"Quota utilisé aujourd'hui : {status['quota_used_today']}/{status['quota_daily_limit']}")
    if not status['can_perform_action']:
        print("❌ Quota insuffisant. Abandon.")
        sys.exit(2)
    
    print(f"Signalement de {video_id} pour raison {reason_id}")
    if comments:
        print(f"   Commentaire : {comments[:80]}...")
    
    result = report_video(video_id, reason_id, comments, language, secondary_reason_id, account)
    
    if result.get("success"):
        print("✅ Vidéo signalée.")
    else:
        print(f"❌ Erreur : {result.get('error')}")
        sys.exit(3)


if __name__ == "__main__":
    main()