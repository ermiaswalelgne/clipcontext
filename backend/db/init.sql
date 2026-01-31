-- Initialize ClipContext database with pgvector extension

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create videos table
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(11) UNIQUE NOT NULL,
    title TEXT,
    channel TEXT,
    duration INTEGER,
    language VARCHAR(10),
    is_generated BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create transcript chunks table with vector embeddings
CREATE TABLE IF NOT EXISTS transcript_chunks (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(11) NOT NULL REFERENCES videos(video_id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    embedding vector(384),  -- all-MiniLM-L6-v2 produces 384-dim vectors
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(video_id, chunk_index)
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_transcript_chunks_embedding 
ON transcript_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for video lookups
CREATE INDEX IF NOT EXISTS idx_transcript_chunks_video_id 
ON transcript_chunks(video_id);

-- Create search history table (for analytics)
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(11) NOT NULL,
    query TEXT NOT NULL,
    results_count INTEGER,
    search_time_ms FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for analytics queries
CREATE INDEX IF NOT EXISTS idx_search_history_created_at 
ON search_history(created_at);
