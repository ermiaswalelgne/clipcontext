"""
Search API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import SearchRequest, SearchResponse, ErrorResponse
from app.services.search import SearchService, get_search_service
from app.services.transcript import TranscriptError

router = APIRouter()


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "Video or transcript not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Search within a YouTube video",
    description="""
    Search for a topic or phrase within a YouTube video's transcript.
    
    Returns timestamped results that you can click to jump directly to that 
    moment in the video.
    
    **How it works:**
    1. Fetches the video's transcript (auto-generated or manual)
    2. Chunks the transcript into searchable segments
    3. Uses semantic search to find relevant sections
    4. Returns timestamps with direct YouTube links
    
    **Example:**
    ```json
    {
        "youtube_url": "https://www.youtube.com/watch?v=abc123",
        "query": "Ethiopian dam construction",
        "max_results": 5
    }
    ```
    """,
)
async def search_video(
    request: SearchRequest,
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """
    Search for a query within a YouTube video.
    """
    try:
        result = await search_service.search(request)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": str(e),
                "error_code": "INVALID_REQUEST",
            }
        )
    except TranscriptError as e:
        status_code = 404 if e.code in ["NO_TRANSCRIPT", "VIDEO_UNAVAILABLE"] else 400
        raise HTTPException(
            status_code=status_code,
            detail={
                "success": False,
                "error": e.message,
                "error_code": e.code,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR",
                "details": {"message": str(e)} if True else None,  # Only in debug mode
            }
        )


@router.get(
    "/search/cache/stats",
    summary="Get cache statistics",
    description="Returns statistics about the transcript and embedding cache.",
)
async def cache_stats(
    search_service: SearchService = Depends(get_search_service),
):
    """Get cache statistics."""
    return {
        "transcripts_cached": len(search_service._transcript_cache),
        "embeddings_cached": len(search_service._embedding_cache),
        "video_ids": list(search_service._transcript_cache.keys()),
    }


@router.delete(
    "/search/cache",
    summary="Clear cache",
    description="Clear the transcript and embedding cache.",
)
async def clear_cache(
    video_id: str = None,
    search_service: SearchService = Depends(get_search_service),
):
    """Clear the cache."""
    search_service.clear_cache(video_id)
    return {
        "success": True,
        "message": f"Cache cleared for {video_id}" if video_id else "All cache cleared",
    }
