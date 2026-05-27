"""
Embedding model management.

We load the sentence-transformers model once at startup and reuse it
for all embedding operations. This avoids the overhead of loading a
~90MB model on every request.

The model runs entirely locally -- no API calls to OpenAI or anyone else.
This is a deliberate choice to satisfy the assignment requirement of
implementing core AI logic rather than relying on external services.
"""

from sentence_transformers import SentenceTransformer
from typing import List
import logging

logger = logging.getLogger(__name__)

# Module-level variable to hold the loaded model
_model = None


def get_model() -> SentenceTransformer:
    """
    Load and return the embedding model, downloading it on first use.
    Subsequent calls return the cached instance.
    """
    global _model
    if _model is None:
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded successfully")
    return _model


def encode_texts(texts: List[str]) -> List[List[float]]:
    """
    Convert a list of text strings into embedding vectors.

    Each text is converted to a 384-dimensional float vector that
    captures its semantic meaning. Texts with similar meanings will
    have vectors that are close together in this space.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (each is a list of 384 floats).
    """
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def encode_query(query: str) -> List[float]:
    """
    Encode a single search query into an embedding vector.
    This is a convenience wrapper around encode_texts for the
    common case of embedding just one string.
    """
    results = encode_texts([query])
    return results[0]
