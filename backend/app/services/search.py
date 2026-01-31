"""
Search service - combines transcript fetching, embedding, and similarity search.
"""

import time
from typing import List, Optional
import numpy as np
from dataclasses import dataclass

from app.config import settings
from app.services.transcript import TranscriptService, Transcript, TranscriptError
from app.services.embedding import EmbeddingService, TextChunker, EmbeddedChunk
from app.models.schemas import (
    SearchRequest,
    SearchResponse,
    TimestampResult,
    VideoMetadata,
)


@dataclass
class SearchResult:
    """Internal search result before formatting."""
    chunk: 'TextChunk'
    score: float


class SearchService:
    """
    Main search service that orchestrates:
    1. Fetching transcripts
    2. Chunking text
    3. Generating embeddings
    4. Performing similarity search
    """
    
    def __init__(self):
        self.transcript_service = TranscriptService()
        self.embedding_service = EmbeddingService()
        self.chunker = TextChunker()
        
        # In-memory cache for development
        # TODO: Replace with Redis in production
        self._transcript_cache: dict[str, Transcript] = {}
        self._embedding_cache: dict[str, List[EmbeddedChunk]] = {}
    
    async def search(self, request: SearchRequest) -> SearchResponse:
        """
        Search for a query within a YouTube video.
        
        Args:
            request: SearchRequest with youtube_url and query
            
        Returns:
            SearchResponse with matching timestamps
        """
        start_time = time.time()
        
        # Extract video ID
        video_id = self.transcript_service.extract_video_id(request.youtube_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {request.youtube_url}")
        
        # Check cache
        cached = video_id in self._transcript_cache
        
        # Get or fetch transcript
        if cached:
            transcript = self._transcript_cache[video_id]
            embedded_chunks = self._embedding_cache[video_id]
        else:
            # Fetch transcript
            transcript = await self.transcript_service.fetch_transcript(video_id)
            self._transcript_cache[video_id] = transcript
            
            # Chunk and embed
            chunks = self.chunker.chunk_transcript(transcript.segments)
            embedded_chunks = self.embedding_service.embed_chunks(chunks)
            self._embedding_cache[video_id] = embedded_chunks
        
        # Embed the query
        query_embedding = self.embedding_service.embed_text(request.query)
        
        # Find similar chunks
        results = self._similarity_search(
            query_embedding,
            embedded_chunks,
            max_results=request.max_results or settings.max_results
        )
        
        # Format results
        timestamp_results = [
            TimestampResult(
                timestamp_start=result.chunk.start_time,
                timestamp_end=result.chunk.end_time,
                timestamp_formatted=self.transcript_service.format_timestamp(
                    result.chunk.start_time
                ),
                text=result.chunk.text,
                score=float(result.score),
                youtube_link=self.transcript_service.get_youtube_link(
                    video_id,
                    result.chunk.start_time
                ),
            )
            for result in results
        ]
        
        search_time_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            success=True,
            query=request.query,
            video=VideoMetadata(
                video_id=video_id,
                title=None,  # TODO: Fetch from YouTube API
                duration=int(transcript.duration) if transcript.duration else None,
                channel=None,
            ),
            results=timestamp_results,
            search_time_ms=round(search_time_ms, 2),
            cached=cached,
        )
    
    def _similarity_search(
        self,
        query_embedding: np.ndarray,
        embedded_chunks: List[EmbeddedChunk],
        max_results: int = 5
    ) -> List[SearchResult]:
        """
        Find chunks most similar to the query using cosine similarity.
        
        Args:
            query_embedding: Query vector
            embedded_chunks: List of embedded chunks to search
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects sorted by score descending
        """
        if not embedded_chunks:
            return []
        
        # Stack all embeddings into a matrix
        chunk_embeddings = np.stack([ec.embedding for ec in embedded_chunks])
        
        # Compute cosine similarity
        # Normalize vectors
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        chunk_norms = chunk_embeddings / np.linalg.norm(
            chunk_embeddings, axis=1, keepdims=True
        )
        
        # Dot product gives cosine similarity for normalized vectors
        similarities = np.dot(chunk_norms, query_norm)
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:max_results]
        
        results = [
            SearchResult(
                chunk=embedded_chunks[idx].chunk,
                score=float(similarities[idx])
            )
            for idx in top_indices
            if similarities[idx] > 0.1  # Filter low-relevance results
        ]
        
        return results
    
    def clear_cache(self, video_id: Optional[str] = None):
        """Clear transcript and embedding cache."""
        if video_id:
            self._transcript_cache.pop(video_id, None)
            self._embedding_cache.pop(video_id, None)
        else:
            self._transcript_cache.clear()
            self._embedding_cache.clear()


# Singleton instance
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """Get or create the search service singleton."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
