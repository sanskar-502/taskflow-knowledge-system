"""
Pydantic schemas for the analytics dashboard endpoint.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TaskAnalytics(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    completion_rate: float


class DocumentAnalytics(BaseModel):
    total: int
    total_chunks: int


class QueryCount(BaseModel):
    query: str
    count: int


class SearchAnalytics(BaseModel):
    total_searches: int
    top_queries: List[QueryCount]


class RecentActivity(BaseModel):
    user_name: Optional[str]
    action: str
    details: Optional[dict]
    timestamp: datetime


class AnalyticsResponse(BaseModel):
    tasks: TaskAnalytics
    documents: DocumentAnalytics
    search: SearchAnalytics
    recent_activity: List[RecentActivity]
