"""
Pydantic schemas for document management.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentOut(BaseModel):
    id: int
    filename: str
    original_name: str
    file_size: Optional[int]
    chunk_count: int
    uploaded_by: int
    uploader_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentOut]
    total: int
