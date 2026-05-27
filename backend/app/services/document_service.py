"""
Document management service.
Handles file uploads, text extraction, and triggers the AI embedding pipeline.
"""

import os
import uuid
import logging
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from app.models.document import Document
from app.schemas.document import DocumentOut, DocumentListResponse
from app.ai.chunker import chunk_text
from app.ai.embeddings import encode_texts
from app.ai.vector_store import add_document_chunks
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def upload_document(
    file: UploadFile,
    uploader_id: int,
    db: Session,
) -> DocumentOut:
    """
    Process an uploaded document through the full pipeline:
    1. Validate the file type
    2. Save to disk
    3. Read and chunk the text
    4. Generate embeddings for each chunk
    5. Store embeddings in ChromaDB
    6. Record metadata in MySQL
    """
    # Only allow .txt files (as per the assignment requirements)
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt files are supported",
        )

    # Read the file content
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty",
        )

    # Generate a unique filename to prevent collisions
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_name)

    # Save the file to disk
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Create the database record first so we have an ID for the chunks
    document = Document(
        filename=unique_name,
        original_name=file.filename,
        file_size=len(content),
        upload_path=file_path,
        uploaded_by=uploader_id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Run the AI pipeline: chunk -> embed -> store
    try:
        chunks = chunk_text(text)
        if chunks:
            embeddings = encode_texts(chunks)
            chunk_count = add_document_chunks(document.id, chunks, embeddings)
            document.chunk_count = chunk_count
            db.commit()
            db.refresh(document)
            logger.info(
                "Processed document '%s': %d chunks created",
                file.filename, chunk_count,
            )
    except Exception as e:
        # If the AI pipeline fails, we still keep the document record
        # but log the error. The document can be reprocessed later.
        logger.error("Failed to process document %d: %s", document.id, str(e))

    return _document_to_response(document)


def get_documents(db: Session) -> DocumentListResponse:
    """List all uploaded documents with their metadata."""
    documents = db.query(Document).order_by(Document.created_at.desc()).all()
    return DocumentListResponse(
        documents=[_document_to_response(doc) for doc in documents],
        total=len(documents),
    )


def get_document_by_id(document_id: int, db: Session) -> DocumentOut:
    """Fetch a single document by its ID."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return _document_to_response(document)


def _document_to_response(doc: Document) -> DocumentOut:
    """Convert a Document ORM object to a response schema."""
    return DocumentOut(
        id=doc.id,
        filename=doc.filename,
        original_name=doc.original_name,
        file_size=doc.file_size,
        chunk_count=doc.chunk_count,
        uploaded_by=doc.uploaded_by,
        uploader_name=doc.uploader.name if doc.uploader else None,
        created_at=doc.created_at,
    )
