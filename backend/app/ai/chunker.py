"""
Text chunking utilities for the document processing pipeline.

When a document is uploaded, we split it into smaller chunks before
generating embeddings. This is necessary because:
1. Embedding models have a limited input size
2. Smaller chunks give more precise search results
3. Overlapping chunks prevent losing context at boundaries

The overlap ensures that if a relevant sentence happens to fall right
at the boundary between two chunks, it still appears fully in at least
one of them.
"""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Split a block of text into overlapping chunks.

    Args:
        text: The full document text.
        chunk_size: Target number of characters per chunk. We use characters
                    rather than tokens because it's simpler and good enough
                    for an MVP with sentence-transformers.
        overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        A list of text chunks. Empty or whitespace-only input returns an
        empty list.
    """
    if not text or not text.strip():
        return []

    # Clean up excessive whitespace but preserve paragraph structure
    text = text.strip()
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # If we're not at the end of the text, try to break at a sentence
        # boundary or at least a word boundary to avoid cutting mid-word
        if end < len(text):
            # Look for the last period, question mark, or newline in the chunk
            last_break = -1
            for char in [". ", "? ", "! ", "\n"]:
                pos = text.rfind(char, start, end)
                if pos > last_break:
                    last_break = pos + len(char)

            # If we found a natural break point, use it
            if last_break > start:
                end = last_break
            else:
                # Fall back to breaking at the last space
                last_space = text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward by (end - overlap) to create the overlap
        start = end - overlap
        if start <= chunks[-1] if not chunks else start <= 0:
            start = end  # Safety valve to prevent infinite loops

    return chunks
