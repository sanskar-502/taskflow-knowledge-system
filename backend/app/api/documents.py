"""
Document management routes.
Admin can upload documents; both roles can list them.
"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.document import DocumentOut, DocumentListResponse
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(..., description="A .txt file to upload"),
    current_user: User = Depends(require_role("Admin")),
    db: Session = Depends(get_db),
):
    """
    Upload a .txt document to the knowledge base.
    The document is automatically processed through the AI pipeline:
    text is chunked, embedded, and stored in the vector database.
    Admin only.
    """
    return await document_service.upload_document(file, current_user.id, db)


@router.get("", response_model=DocumentListResponse)
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all uploaded documents with metadata."""
    return document_service.get_documents(db)


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details for a specific document."""
    return document_service.get_document_by_id(document_id, db)
