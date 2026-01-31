"""
Text embedding service using sentence-transformers.
"""

from typing import List, Optional
import numpy as np
from dataclasses import dataclass

from app.config import settings


@dataclass
class TextChunk:
    """A chunk of text with metadata for embedding."""
    text: str
    start_time: float
    end_time: float
    chunk_index: int


@dataclass  
class EmbeddedChunk:
    """A text chunk with its embedding vector."""
    chunk: TextChunk
    embedding: np.ndarray


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
                       Defaults to config setting.
        """
        self.model_name = model_name or settings.embedding_model
        self._model = None
    
    @property
    def model(self):
        """Lazy load the model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            print(f"📥 Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            print(f"✅ Model loaded successfully")
        return self._model
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Array of embedding vectors
        """
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    
    def embed_chunks(self, chunks: List[TextChunk]) -> List[EmbeddedChunk]:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of TextChunk objects
            
        Returns:
            List of EmbeddedChunk objects with embeddings
        """
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embed_texts(texts)
        
        return [
            EmbeddedChunk(chunk=chunk, embedding=embedding)
            for chunk, embedding in zip(chunks, embeddings)
        ]
    
    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        # all-MiniLM-L6-v2 produces 384-dimensional vectors
        return self.model.get_sentence_embedding_dimension()


class TextChunker:
    """Utility for chunking transcript text."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Number of words per chunk
            chunk_overlap: Number of overlapping words between chunks
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def chunk_transcript(
        self,
        segments: List['TranscriptSegment']
    ) -> List[TextChunk]:
        """
        Chunk transcript segments into overlapping text chunks.
        
        This preserves timing information so we can link back to
        the exact timestamp in the video.
        
        Args:
            segments: List of TranscriptSegment objects
            
        Returns:
            List of TextChunk objects
        """
        if not segments:
            return []
        
        chunks = []
        current_words = []
        current_start = segments[0].start
        segment_idx = 0
        word_to_time = []  # Track which time each word belongs to
        
        # Build word-to-time mapping
        for segment in segments:
            words = segment.text.split()
            word_duration = segment.duration / max(len(words), 1)
            
            for i, word in enumerate(words):
                word_time = segment.start + (i * word_duration)
                word_to_time.append((word, word_time, segment.start + segment.duration))
        
        # Create chunks with overlap
        i = 0
        chunk_index = 0
        
        while i < len(word_to_time):
            # Get chunk_size words
            chunk_end = min(i + self.chunk_size, len(word_to_time))
            chunk_words = word_to_time[i:chunk_end]
            
            if chunk_words:
                text = " ".join(w[0] for w in chunk_words)
                start_time = chunk_words[0][1]
                end_time = chunk_words[-1][2]
                
                chunks.append(TextChunk(
                    text=text,
                    start_time=start_time,
                    end_time=end_time,
                    chunk_index=chunk_index,
                ))
                chunk_index += 1
            
            # Move forward by (chunk_size - overlap)
            i += max(self.chunk_size - self.chunk_overlap, 1)
        
        return chunks
