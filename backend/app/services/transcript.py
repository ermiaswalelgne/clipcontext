"""
YouTube transcript fetching service.
"""

import re
from typing import List, Optional
from dataclasses import dataclass

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)


@dataclass
class TranscriptSegment:
    """A segment of transcript with timing information."""
    text: str
    start: float  # seconds
    duration: float  # seconds
    
    @property
    def end(self) -> float:
        return self.start + self.duration


@dataclass
class Transcript:
    """Complete transcript with metadata."""
    video_id: str
    segments: List[TranscriptSegment]
    language: str
    is_generated: bool  # Auto-generated vs manual
    
    @property
    def full_text(self) -> str:
        return " ".join(seg.text for seg in self.segments)
    
    @property
    def duration(self) -> float:
        if not self.segments:
            return 0
        return self.segments[-1].end


class TranscriptService:
    """Service for fetching YouTube transcripts."""
    
    def __init__(self):
        self.ytt_api = YouTubeTranscriptApi()
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.
        
        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        - https://www.youtube.com/watch?v=VIDEO_ID&t=123
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$',  # Just the ID itself
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Convert seconds to human-readable timestamp."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
    
    @staticmethod
    def get_youtube_link(video_id: str, timestamp: float) -> str:
        """Generate a YouTube link that starts at a specific timestamp."""
        return f"https://www.youtube.com/watch?v={video_id}&t={int(timestamp)}"
    
    async def fetch_transcript(
        self,
        video_id: str,
        languages: List[str] = ["en"]
    ) -> Transcript:
        """
        Fetch transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            languages: Preferred languages in order of preference
            
        Returns:
            Transcript object with segments
            
        Raises:
            ValueError: If video ID is invalid
            TranscriptError: If transcript cannot be fetched
        """
        if not video_id or len(video_id) != 11:
            raise ValueError(f"Invalid video ID: {video_id}")
        
        try:
            # New API: use fetch() method
            transcript = self.ytt_api.fetch(video_id, languages=languages)
            
            # Convert snippets to our format
            segments = [
                TranscriptSegment(
                    text=snippet.text,
                    start=snippet.start,
                    duration=snippet.duration
                )
                for snippet in transcript.snippets
            ]
            
            return Transcript(
                video_id=video_id,
                segments=segments,
                language=transcript.language_code if hasattr(transcript, 'language_code') else 'en',
                is_generated=transcript.is_generated if hasattr(transcript, 'is_generated') else False,
            )
            
        except TranscriptsDisabled:
            raise TranscriptError(
                "Transcripts are disabled for this video",
                code="TRANSCRIPTS_DISABLED"
            )
        except VideoUnavailable:
            raise TranscriptError(
                "Video is unavailable or does not exist",
                code="VIDEO_UNAVAILABLE"
            )
        except NoTranscriptFound:
            raise TranscriptError(
                "No transcript found for this video",
                code="NO_TRANSCRIPT"
            )
        except Exception as e:
            raise TranscriptError(
                f"Failed to fetch transcript: {str(e)}",
                code="FETCH_ERROR"
            )


class TranscriptError(Exception):
    """Custom exception for transcript-related errors."""
    
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)