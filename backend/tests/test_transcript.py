"""
Tests for transcript service.
"""

import pytest
from app.services.transcript import TranscriptService


class TestTranscriptService:
    """Tests for TranscriptService."""
    
    def setup_method(self):
        self.service = TranscriptService()
    
    def test_extract_video_id_standard_url(self):
        """Test extracting video ID from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert self.service.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_short_url(self):
        """Test extracting video ID from short YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert self.service.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_embed_url(self):
        """Test extracting video ID from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert self.service.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_with_timestamp(self):
        """Test extracting video ID from URL with timestamp."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123"
        assert self.service.extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self):
        """Test that invalid URL returns None."""
        url = "https://example.com/video"
        assert self.service.extract_video_id(url) is None
    
    def test_extract_video_id_just_id(self):
        """Test extracting when just the ID is provided."""
        video_id = "dQw4w9WgXcQ"
        assert self.service.extract_video_id(video_id) == "dQw4w9WgXcQ"
    
    def test_format_timestamp_seconds(self):
        """Test formatting timestamp under a minute."""
        assert self.service.format_timestamp(45) == "0:45"
    
    def test_format_timestamp_minutes(self):
        """Test formatting timestamp in minutes."""
        assert self.service.format_timestamp(125) == "2:05"
    
    def test_format_timestamp_hours(self):
        """Test formatting timestamp with hours."""
        assert self.service.format_timestamp(3725) == "1:02:05"
    
    def test_get_youtube_link(self):
        """Test generating YouTube link with timestamp."""
        link = self.service.get_youtube_link("dQw4w9WgXcQ", 125.5)
        assert link == "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=125"
