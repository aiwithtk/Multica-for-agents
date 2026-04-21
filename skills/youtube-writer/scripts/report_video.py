#!/usr/bin/env python3
"""
Signale une vidéo YouTube abusive.
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
def report_video(video_id: str, reason_id: str, comments: str = None, language: str = "en", account: Optional[str] = None) -> Dict[str, Any]:
    """Signale une vidéo."""
    if not COMPOSIO_AVAILABLE:
        return {"success": False, "error": "Composio SDK non disponible."}
        
    try:
        arguments = {"videoId": video_id, "reasonId": reason_id, "language": language}
        if comments:
            arguments["comments"] = comments
            
        result, error = run_composio_tool(
            tool_slug="YOUTUBE_REPORT_VIDEO_ABUSE",
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
        print("Usage: python report_video.py <videoId> <reasonId> [comments]")
        sys.exit(1)
    c = sys.argv[3] if len(sys.argv) > 3 else None
    res = report_video(sys.argv[1], sys.argv[2], c)
    print(json.dumps(res, indent=2))
