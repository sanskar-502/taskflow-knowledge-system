"""
Pydantic schemas for the semantic search endpoint.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural language search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")


class SearchResult(BaseModel):
    text: str
    document_id: int
    document_name: str
    relevance_score: float
    chunk_index: int


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
