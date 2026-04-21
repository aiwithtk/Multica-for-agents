import argparse
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeConversationReader:
    """
    Implements high-signal YouTube conversation reading logic.
    Features logic for thread flattening, role annotation, intent detection,
    and a 5-state business lifecycle engine.
    """

    def __init__(self, api_key, channel_id):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.channel_id = channel_id
        self.conversations = []

    def fetch_video_stats(self, video_id):
        """Retrieves core metrics for the video."""
        try:
            request = self.youtube.videos().list(
                part="statistics,snippet",
                id=video_id
            )
            response = request.execute()
            if not response['items']:
                return None
            return response['items'][0]['statistics']
        except HttpError as e:
            print(f"Error fetching stats: {e}")
            return None

    def get_full_thread(self, parent_id):
        """Recursively fetches all replies for a given parent comment."""
        replies = []
        try:
            request = self.youtube.comments().list(
                part="snippet",
                parentId=parent_id,
                maxResults=100
            )
            while request:
                response = request.execute()
                replies.extend(response.get('items', []))
                request = self.youtube.comments().list_next(request, response)
        except HttpError as e:
            # Some threads might not have replies or access
            pass
        return replies

    def flatten_conversation(self, thread_resource):
        """
        Transforms fragmented API responses into a linear chronological list.
        Annotates roles: ME, PROSPECT, OTHER.
        """
        top_comment = thread_resource['snippet']['topLevelComment']
        parent_id = top_comment['id']
        
        # Get all replies
        raw_replies = self.get_full_thread(parent_id)
        
        # Combine and sort by date
        all_messages = [top_comment] + raw_replies
        all_messages.sort(key=lambda x: x['snippet']['publishedAt'])
        
        linear_thread = []
        for msg in all_messages:
            snippet = msg['snippet']
            author_id = snippet.get('authorChannelId', {}).get('value', 'unknown')
            
            # Identify Role
            if author_id == self.channel_id:
                role = "ME"
            elif self._detect_intent_signals(snippet['textDisplay']):
                role = "PROSPECT"
            else:
                role = "OTHER"
                
            linear_thread.append({
                "timestamp": snippet['publishedAt'],
                "author": snippet['authorDisplayName'],
                "role": role,
                "text": snippet['textDisplay'],
                "id": msg['id']
            })
            
        return linear_thread

    def _detect_intent_signals(self, text):
        """Identify if a user shows high-engagement intent (Questions, Objections, Mentions)."""
        text = text.lower()
        signals = ["?", "@", "combien", "prix", "cher", "pourquoi", "comment", "merci", "aide", "objection"]
        return any(s in text for s in signals)

    def calculate_state(self, flattened_thread):
        """
        Assigns one of the 5 business states based on the conversation dynamic.
        States: OPEN, ACTIVE, PENDING, CONVERTED, DEAD.
        """
        if not flattened_thread:
            return "UNKNOWN"

        last_msg = flattened_thread[-1]
        history_roles = [m['role'] for m in flattened_thread]
        
        # 1. CONVERTED: Objective keywords detected
        conversion_keywords = ["merci je regarde", "lien", "dm", "contact", "pris rendez-vous"]
        all_text = " ".join([m['text'].lower() for m in flattened_thread])
        if any(k in all_text for k in conversion_keywords):
            return "CONVERTED"

        # 2. DEAD: Last message is old (simulated logic)
        last_date = datetime.strptime(last_msg['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
        if datetime.utcnow() - last_date > timedelta(days=14):
            return "DEAD"

        # 3. PENDING: Creator (ME) was the last to speak
        if last_msg['role'] == "ME":
            return "PENDING"

        # 4. ACTIVE: Reciprocal exchange (both participated)
        if "ME" in history_roles and last_msg['role'] != "ME":
            return "ACTIVE"

        # 5. OPEN: No response from ME yet
        if "ME" not in history_roles:
            return "OPEN"

        return "ACTIVE"

    def run_ingestion(self, video_id):
        """Main entry point for reading and triaging comments."""
        print(f"--- Starting Ingestion for Video: {video_id} ---")
        
        stats = self.fetch_video_stats(video_id)
        print(f"Stats: {stats}")

        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                order="time",
                maxResults=50
            )
            response = request.execute()
            
            for item in response.get('items', []):
                flattened = self.flatten_conversation(item)
                state = self.calculate_state(flattened)
                
                # Filter/Triage
                is_priority = any(m['role'] == "PROSPECT" for m in flattened)
                
                conversation = {
                    "thread_id": item['id'],
                    "state": state,
                    "is_priority": is_priority,
                    "messages": flattened
                }
                self.conversations.append(conversation)
                
                print(f"Thread {item['id']} | State: {state} | Priority: {is_priority}")

        except HttpError as e:
            print(f"Error listing threads: {e}")

    def export_json(self, filename="youtube_reader_output.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        print(f"Ingestion complete. Exported to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Reader Execution Script")
    parser.add_argument("--api_key", default=os.getenv("YOUTUBE_API_KEY"), required=not bool(os.getenv("YOUTUBE_API_KEY")), help="YouTube Data API v3 Key")
    parser.add_argument("--channel_id", default=os.getenv("YOUTUBE_CHANNEL_ID"), required=not bool(os.getenv("YOUTUBE_CHANNEL_ID")), help="Your Channel ID to identify 'ME'")
    parser.add_argument("--video_id", required=True, help="Video ID to analyze")
    
    args = parser.parse_args()
    
    reader = YouTubeConversationReader(args.api_key, args.channel_id)
    reader.run_ingestion(args.video_id)
    reader.export_json()
