"""
Search service.
Ties together the embedding model and vector store to provide
semantic search over the uploaded document knowledge base.

Also handles logging search queries to the activity_logs table
so we can track popular queries in analytics.
"""

import logging
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.activity_log import ActivityLog
from app.schemas.search import SearchResponse, SearchResult
from app.ai.embeddings import encode_query
from app.ai.vector_store import search_similar

logger = logging.getLogger(__name__)


def semantic_search(
    query: str,
    top_k: int,
    user_id: int,
    db: Session,
) -> SearchResponse:
    """
    Perform semantic search across the knowledge base.

    Steps:
    1. Convert the query text to an embedding vector
    2. Search ChromaDB for the most similar document chunks
    3. Enrich results with document names from MySQL
    4. Log the search query for analytics
    """
    # Step 1: Embed the query using the same model that embedded the documents
    query_vector = encode_query(query)

    # Step 2: Find similar chunks in the vector store
    raw_results = search_similar(query_vector, top_k=top_k)

    # Step 3: Look up document names for the results
    results = []
    for item in raw_results:
        doc = db.query(Document).filter(Document.id == item["document_id"]).first()
        doc_name = doc.original_name if doc else "Unknown"

        results.append(SearchResult(
            text=item["text"],
            document_id=item["document_id"],
            document_name=doc_name,
            relevance_score=item["relevance_score"],
            chunk_index=item["chunk_index"],
        ))

    # Step 4: Log this search action for analytics tracking
    log_entry = ActivityLog(
        user_id=user_id,
        action="SEARCH",
        details={"query": query, "results_count": len(results)},
    )
    db.add(log_entry)
    db.commit()

    return SearchResponse(
        query=query,
        results=results,
        total_results=len(results),
    )
