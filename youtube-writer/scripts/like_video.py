#!/usr/bin/env python3
"""
Like ou dislike une vidéo YouTube.
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
def like_video(video_id: str, rating: str = "like", account: Optional[str] = None) -> Dict[str, Any]:
    """Note une vidéo (like, dislike, none)."""
    if rating not in ("like", "dislike", "none"):
        raise ValueError("Rating invalide.")
        
    if not COMPOSIO_AVAILABLE:
        return {"success": False, "error": "Composio SDK non disponible."}
        
    try:
        result, error = run_composio_tool(
            tool_slug="YOUTUBE_RATE_VIDEO",
            arguments={"id": video_id, "rating": rating},
            account=account
        )
        if error:
            return {"success": False, "error": error}
        return {"success": True, "quota_used": 50}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python like_video.py <videoId> [like|dislike|none]")
        sys.exit(1)
    rating_val = sys.argv[2] if len(sys.argv) > 2 else "like"
    res = like_video(sys.argv[1], rating_val)
    print(json.dumps(res, indent=2))
