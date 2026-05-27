"""
Semantic search routes.
Provides AI-powered search over the uploaded document knowledge base.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.search import SearchResponse
from app.services import search_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse)
def search_documents(
    q: str = Query(..., min_length=1, max_length=500, description="Natural language search query"),
    top_k: int = Query(default=5, ge=1, le=20, description="Number of results to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search the knowledge base using natural language.

    The query is converted to a vector embedding and compared against
    all document chunks using cosine similarity. Results are ranked
    by relevance score (higher is better).

    Example:
        GET /search?q=how to handle customer complaints&top_k=5
    """
    return search_service.semantic_search(
        query=q,
        top_k=top_k,
        user_id=current_user.id,
        db=db,
    )
