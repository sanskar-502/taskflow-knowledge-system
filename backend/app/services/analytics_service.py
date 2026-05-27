"""
Analytics service.
Aggregates data from multiple tables to provide a dashboard overview.
"""

from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.task import Task
from app.models.document import Document
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsResponse,
    TaskAnalytics,
    DocumentAnalytics,
    SearchAnalytics,
    QueryCount,
    RecentActivity,
)


def get_analytics(db: Session) -> AnalyticsResponse:
    """
    Build the analytics dashboard data.
    This runs several queries across different tables and assembles
    the results into a single response.
    """

    # -- Task analytics --
    total_tasks = db.query(func.count(Task.id)).scalar() or 0
    pending = db.query(func.count(Task.id)).filter(Task.status == "Pending").scalar() or 0
    in_progress = db.query(func.count(Task.id)).filter(Task.status == "In Progress").scalar() or 0
    completed = db.query(func.count(Task.id)).filter(Task.status == "Completed").scalar() or 0
    completion_rate = round((completed / total_tasks * 100), 1) if total_tasks > 0 else 0.0

    task_analytics = TaskAnalytics(
        total=total_tasks,
        pending=pending,
        in_progress=in_progress,
        completed=completed,
        completion_rate=completion_rate,
    )

    # -- Document analytics --
    total_docs = db.query(func.count(Document.id)).scalar() or 0
    total_chunks = db.query(func.coalesce(func.sum(Document.chunk_count), 0)).scalar()

    document_analytics = DocumentAnalytics(
        total=total_docs,
        total_chunks=total_chunks,
    )

    # -- Search analytics --
    # Pull all search logs and count query frequencies
    search_logs = (
        db.query(ActivityLog)
        .filter(ActivityLog.action == "SEARCH")
        .all()
    )

    total_searches = len(search_logs)

    # Extract query strings from the JSON details column and count them
    query_texts = []
    for log in search_logs:
        if log.details and isinstance(log.details, dict):
            q = log.details.get("query", "")
            if q:
                query_texts.append(q.lower().strip())

    query_counts = Counter(query_texts)
    top_queries = [
        QueryCount(query=q, count=c)
        for q, c in query_counts.most_common(10)
    ]

    search_analytics = SearchAnalytics(
        total_searches=total_searches,
        top_queries=top_queries,
    )

    # -- Recent activity --
    recent_logs = (
        db.query(ActivityLog)
        .order_by(ActivityLog.timestamp.desc())
        .limit(20)
        .all()
    )

    recent_activity = []
    for log in recent_logs:
        user_name = None
        if log.user_id:
            user = db.query(User).filter(User.id == log.user_id).first()
            user_name = user.name if user else None

        recent_activity.append(RecentActivity(
            user_name=user_name,
            action=log.action,
            details=log.details,
            timestamp=log.timestamp,
        ))

    return AnalyticsResponse(
        tasks=task_analytics,
        documents=document_analytics,
        search=search_analytics,
        recent_activity=recent_activity,
    )
