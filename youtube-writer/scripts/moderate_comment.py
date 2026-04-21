#!/usr/bin/env python3
"""
Modère un ou plusieurs commentaires YouTube (approuver, rejeter, bannir).
"""

import sys
import json
from typing import List, Dict, Any, Optional

try:
    from .rate_limiter import quota_decorator
    from .action_logger import log_action
except ImportError:
    from scripts.rate_limiter import quota_decorator
    from scripts.action_logger import log_action

try:
    from composio_sdk import run_composio_tool
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False

@quota_decorator
def moderate_comment(comment_ids: List[str], status: str, ban: bool = False, account: Optional[str] = None) -> Dict[str, Any]:
    """Change le statut de modération d'un commentaire."""
    if status not in ("published", "rejected", "heldForReview"):
        raise ValueError("Status invalide.")
        
    if not COMPOSIO_AVAILABLE:
        return {"success": False, "error": "Composio SDK non disponible."}
        
    try:
        arguments = {
            "id": ",".join(comment_ids),
            "moderationStatus": status
        }
        if status == "rejected" and ban:
            arguments["banAuthor"] = True
            
        result, error = run_composio_tool(
            tool_slug="YOUTUBE_SET_COMMENT_MODERATION_STATUS",
            arguments=arguments,
            account=account
        )
        if error:
            return {"success": False, "error": error}
        return {"success": True, "quota_used": 50}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python moderate_comment.py <status:published|rejected|heldForReview> <commentId1> [commentId2...]")
        sys.exit(1)
    status_arg = sys.argv[1]
    ids = sys.argv[2:]
    res = moderate_comment(ids, status_arg)
    print(json.dumps(res, indent=2))
