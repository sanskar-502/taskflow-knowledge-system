"""
Analytics routes.
Provides aggregated data for the dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get aggregated analytics for the dashboard.

    Returns:
    - Task breakdown (total, pending, in progress, completed, completion rate)
    - Document stats (total documents, total chunks)
    - Search trends (total searches, most searched queries)
    - Recent activity feed
    """
    return analytics_service.get_analytics(db)
