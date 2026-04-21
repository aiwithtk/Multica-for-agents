#!/usr/bin/env python3
"""
Publie une réponse à un commentaire (thread) sur YouTube.
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
def reply_to_comment(parent_id: str, text: str, account: Optional[str] = None) -> Dict[str, Any]:
    """Publie une réponse à un commentaire thread."""
    if not COMPOSIO_AVAILABLE:
        return {"success": False, "error": "Composio SDK non disponible."}
        
    try:
        result, error = run_composio_tool(
            tool_slug="YOUTUBE_INSERT_COMMENT_REPLY",
            arguments={"parentId": parent_id, "text": text},
            account=account
        )
        if error:
            return {"success": False, "error": error}
        return {"success": True, "data": result, "quota_used": 50}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python reply_to_comment.py <parentId> <text>")
        sys.exit(1)
    res = reply_to_comment(sys.argv[1], sys.argv[2])
    print(json.dumps(res, indent=2))
