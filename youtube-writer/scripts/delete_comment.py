#!/usr/bin/env python3
"""
Supprime un commentaire YouTube.
"""

import sys
import json
from typing import Dict, Any, Optional

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
def delete_comment(comment_id: str, account: Optional[str] = None) -> Dict[str, Any]:
    """Supprime un commentaire."""
    if not COMPOSIO_AVAILABLE:
        return {"success": False, "error": "Composio SDK non disponible."}
        
    try:
        result, error = run_composio_tool(
            tool_slug="YOUTUBE_DELETE_COMMENT",
            arguments={"id": comment_id},
            account=account
        )
        if error:
            return {"success": False, "error": error}
        return {"success": True, "quota_used": 50}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_comment.py <commentId>")
        sys.exit(1)
    res = delete_comment(sys.argv[1])
    print(json.dumps(res, indent=2))
