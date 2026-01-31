"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime


class SearchRequest(BaseModel):
    """Request body for video search."""
    
    youtube_url: str = Field(
        ...,
        description="YouTube video URL",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
    )
    query: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="What to search for in the video",
        examples=["Ethiopian dam", "machine learning explanation"]
    )
    max_results: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of results to return"
    )


class TimestampResult(BaseModel):
    """A single search result with timestamp."""
    
    timestamp_start: float = Field(
        ...,
        description="Start time in seconds"
    )
    timestamp_end: float = Field(
        ...,
        description="End time in seconds"
    )
    timestamp_formatted: str = Field(
        ...,
        description="Human-readable timestamp (e.g., '1:23:45')"
    )
    text: str = Field(
        ...,
        description="Transcript text at this timestamp"
    )
    score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Relevance score (0-1)"
    )
    youtube_link: str = Field(
        ...,
        description="Direct link to this timestamp in the video"
    )


class VideoMetadata(BaseModel):
    """Metadata about the YouTube video."""
    
    video_id: str
    title: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    channel: Optional[str] = None


class SearchResponse(BaseModel):
    """Response body for video search."""
    
    success: bool
    query: str
    video: VideoMetadata
    results: List[TimestampResult]
    search_time_ms: float = Field(
        ...,
        description="Time taken to search in milliseconds"
    )
    cached: bool = Field(
        default=False,
        description="Whether transcript was fetched from cache"
    )


class ErrorResponse(BaseModel):
    """Error response body."""
    
    success: bool = False
    error: str
    error_code: str
    details: Optional[dict] = None


# Example responses for OpenAPI docs
search_response_example = {
    "success": True,
    "query": "Ethiopian dam",
    "video": {
        "video_id": "abc123",
        "title": "Travel Documentary - Africa",
        "duration": 5400,
        "channel": "Travel Noah"
    },
    "results": [
        {
            "timestamp_start": 1845.5,
            "timestamp_end": 1920.0,
            "timestamp_formatted": "30:45",
            "text": "And here we see the Grand Ethiopian Renaissance Dam, the largest hydroelectric dam in Africa...",
            "score": 0.92,
            "youtube_link": "https://www.youtube.com/watch?v=abc123&t=1845"
        }
    ],
    "search_time_ms": 245.3,
    "cached": False
}
