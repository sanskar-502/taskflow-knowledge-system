"""
ChromaDB vector store wrapper.

This module manages the persistent ChromaDB collection where document
chunk embeddings are stored. It provides a clean interface for adding
new document chunks and searching across the knowledge base.

ChromaDB stores data on disk in the chroma_data directory, so the
vector index survives server restarts. We use cosine similarity as
the distance metric because it works well with sentence-transformer
embeddings and is robust to differences in text length.
"""

import chromadb
from typing import List, Dict
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize the persistent client. ChromaDB will create the directory
# if it doesn't exist and load existing data if it does.
_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

# Get or create the main collection for document chunks
_collection = _client.get_or_create_collection(
    name="document_chunks",
    metadata={"hnsw:space": "cosine"},
)


def add_document_chunks(
    document_id: int,
    chunks: List[str],
    embeddings: List[List[float]],
) -> int:
    """
    Store document chunks and their embeddings in the vector database.

    Each chunk gets a unique ID based on the document ID and chunk index.
    Metadata links each chunk back to its source document so we can
    display the document name in search results.

    Args:
        document_id: The MySQL document ID for reference.
        chunks: List of text chunks from the document.
        embeddings: Corresponding embedding vectors.

    Returns:
        The number of chunks added.
    """
    if not chunks:
        return 0

    ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "chunk_index": i}
        for i in range(len(chunks))
    ]

    _collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    logger.info(
        "Added %d chunks for document %d to vector store",
        len(chunks), document_id,
    )
    return len(chunks)


def search_similar(
    query_embedding: List[float],
    top_k: int = 5,
) -> List[Dict]:
    """
    Find the most semantically similar document chunks to the query.

    Args:
        query_embedding: The embedding vector of the search query.
        top_k: Maximum number of results to return.

    Returns:
        A list of dicts, each containing:
        - text: the chunk text
        - document_id: which document it came from
        - chunk_index: position within the document
        - relevance_score: cosine similarity (0 to 1, higher is better)
    """
    # Check if we have any documents in the collection
    if _collection.count() == 0:
        return []

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, _collection.count()),
    )

    # Unpack ChromaDB's nested list structure into something more usable
    search_results = []
    for i in range(len(results["documents"][0])):
        # ChromaDB returns distances, not similarities.
        # For cosine space, similarity = 1 - distance.
        distance = results["distances"][0][i]
        similarity = round(1 - distance, 4)

        search_results.append({
            "text": results["documents"][0][i],
            "document_id": results["metadatas"][0][i]["document_id"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "relevance_score": similarity,
        })

    return search_results


def delete_document_chunks(document_id: int):
    """
    Remove all chunks associated with a specific document.
    Useful if a document is re-uploaded or deleted.
    """
    # Get all chunk IDs for this document
    existing = _collection.get(
        where={"document_id": document_id},
    )
    if existing["ids"]:
        _collection.delete(ids=existing["ids"])
        logger.info("Deleted %d chunks for document %d", len(existing["ids"]), document_id)
