"""
Transcript Service - Fetches YouTube video transcripts

Uses SerpAPI for production (avoids IP blocking), falls back to youtube-transcript-api for local dev.
"""

import os
import re
import httpx
from typing import Optional, List
from dataclasses import dataclass


class TranscriptError(Exception):
    """Custom exception for transcript-related errors."""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

@dataclass
class TranscriptSegment:
    """A single segment of a transcript with text and timing."""
    text: str
    start: float
    duration: float


@dataclass
class Transcript:
    """Complete transcript for a video."""
    video_id: str
    segments: List[TranscriptSegment]
    source: str  # "serpapi" or "youtube-transcript-api"
    
    @property
    def full_text(self) -> str:
        """Get the full transcript as a single string."""
        return " ".join(seg.text for seg in self.segments)
    
    def to_dict_list(self) -> List[dict]:
        """Convert segments to list of dicts for backward compatibility."""
        return [
            {"text": seg.text, "start": seg.start, "duration": seg.duration}
            for seg in self.segments
        ]


class TranscriptService:
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.use_serpapi = bool(self.serpapi_key)
        
        # Only import youtube-transcript-api if needed (for local fallback)
        if not self.use_serpapi:
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                self.ytt_api = YouTubeTranscriptApi()
            except ImportError:
                self.ytt_api = None

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def fetch_transcript(self, youtube_url: str) -> dict:
        """
        Fetch transcript for a YouTube video.
        Returns dict with 'segments' (list of text + timestamps) and 'video_id'.
        """
        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            raise TranscriptError(f"Could not extract video ID from URL: {youtube_url}")

        if self.use_serpapi:
            return await self._fetch_via_serpapi(video_id)
        else:
            return await self._fetch_via_youtube_transcript_api(video_id)

    async def _fetch_via_serpapi(self, video_id: str) -> dict:
        """Fetch transcript using SerpAPI (works from cloud servers)."""
        params = {
            "api_key": self.serpapi_key,
            "engine": "youtube_video_transcript",
            "v": video_id,
            "type": "asr",  # Auto-generated speech recognition
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://serpapi.com/search",
                params=params,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise TranscriptError(f"SerpAPI request failed: {response.status_code}")
            
            data = response.json()
            
            # Check for errors
            if "error" in data:
                raise TranscriptError(f"SerpAPI error: {data['error']}")
            
            transcript_data = data.get("transcript", [])
            
            if not transcript_data:
                raise TranscriptError("No transcript available for this video")
            
            # Convert SerpAPI format to our format
            segments = []
            for item in transcript_data:
                # SerpAPI returns start_ms and end_ms in milliseconds
                start_ms = item.get("start_ms", 0)
                start_seconds = start_ms / 1000.0
                
                # Calculate duration from start_ms and end_ms
                end_ms = item.get("end_ms", start_ms)
                duration = (end_ms - start_ms) / 1000.0
                
                segments.append({
                    "text": item.get("snippet", ""),
                    "start": start_seconds,
                    "duration": duration
                })
            
            return {
                "video_id": video_id,
                "segments": segments,
                "source": "serpapi"
            }

    async def _fetch_via_youtube_transcript_api(self, video_id: str) -> dict:
        """Fetch transcript using youtube-transcript-api (local development)."""
        if self.ytt_api is None:
            raise TranscriptError(
                "youtube-transcript-api not available and SERPAPI_API_KEY not set. "
                "Please set SERPAPI_API_KEY environment variable for production use."
            )
        
        try:
            # New API syntax (v1.2.4+)
            fetched = self.ytt_api.fetch(video_id)
            
            segments = []
            for snippet in fetched.snippets:
                segments.append({
                    "text": snippet.text,
                    "start": snippet.start,
                    "duration": snippet.duration
                })
            
            return {
                "video_id": video_id,
                "segments": segments,
                "source": "youtube-transcript-api"
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's an IP blocking issue
            if "IP" in error_msg or "blocked" in error_msg.lower():
                raise TranscriptError(
                    "YouTube is blocking requests from this IP. "
                    "This typically happens with cloud provider IPs. "
                    "Please set SERPAPI_API_KEY for production use."
                )
            raise TranscriptError(f"Failed to fetch transcript: {error_msg}")

    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to human-readable timestamp (MM:SS or HH:MM:SS)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    def get_youtube_link_with_timestamp(self, video_id: str, seconds: float) -> str:
        """Generate YouTube URL that starts at a specific timestamp."""
        return f"https://www.youtube.com/watch?v={video_id}&t={int(seconds)}"
