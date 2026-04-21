#!/usr/bin/env python3
"""
Fetch YouTube comments for a video, extract mentions, and detect pending replies.
Uses Composio tools via the run_composio_tool helper (when run in Composio sandbox).
Can also be adapted for direct API calls.
"""

import sys
import json
import re
from typing import Dict, List, Any, Optional

MENTION_PATTERN = r'@(\w+)'


def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from comment text."""
    return re.findall(MENTION_PATTERN, text)


def fetch_comments(video_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch comment threads for a video using YOUTUBE_LIST_COMMENT_THREADS2.
    Returns list of comment objects with added fields: mentions, has_pending_reply.
    """
    # This function is designed to be called from within a Composio workbench.
    # It uses run_composio_tool helper if available.
    try:
        # Try to import the workbench helper
        from composio_sdk import run_composio_tool
        result, error = run_composio_tool(
            tool_slug="YOUTUBE_LIST_COMMENT_THREADS2",
            arguments={
                "videoId": video_id,
                "part": "snippet,replies",
                "order": "time",
                "maxResults": max_results,
                "textFormat": "plainText"
            }
        )
        if error:
            print(f"Error fetching comments: {error}")
            data = {}
        else:
            data = result.get("data", {})
    except ImportError:
        # Fallback: assume we're in a sandbox without the helper
        # You may need to call the tool via COMPOSIO_MULTI_EXECUTE_TOOL
        data = {}

    items = data.get("items", [])
    comments = []
    for item in items:
        snippet = item.get("snippet", {})
        top_level = snippet.get("topLevelComment", {})
        top_snippet = top_level.get("snippet", {})
        text = top_snippet.get("textDisplay") or top_snippet.get("textOriginal", "")
        comment_id = top_level.get("id")
        author = top_snippet.get("authorDisplayName")
        like_count = top_snippet.get("likeCount", 0)
        published_at = top_snippet.get("publishedAt")
        replies = item.get("replies", {}).get("comments", [])
        
        # Determine if there's a pending reply (no reply or no reply from channel owner)
        # Simplified: pending if replies list empty
        has_pending_reply = len(replies) == 0
        
        comments.append({
            "id": comment_id,
            "author": author,
            "text": text,
            "mentions": extract_mentions(text),
            "like_count": like_count,
            "published_at": published_at,
            "has_pending_reply": has_pending_reply,
            "reply_count": len(replies)
        })
    return comments


def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_comments.py <videoId> [maxResults]")
        sys.exit(1)
    video_id = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    comments = fetch_comments(video_id, max_results)
    print(json.dumps(comments, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
