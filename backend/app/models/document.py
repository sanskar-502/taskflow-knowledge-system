"""
Document model. Tracks uploaded files and their processing state.
The chunk_count field records how many text chunks were created
during the embedding pipeline, which is useful for analytics.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    chunk_count = Column(Integer, default=0)
    upload_path = Column(String(500), nullable=False)
    uploaded_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    uploader = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}')>"
