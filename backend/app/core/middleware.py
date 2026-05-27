"""
Middleware for automatic activity logging.

This intercepts every request and logs meaningful actions to the
activity_logs table. It maps specific route+method combinations to
action types, so individual endpoints don't need to handle logging.

Some actions (like search queries) are logged at the service layer
instead, because we need access to the query text which isn't
available from the request path alone.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.activity_log import ActivityLog
from app.core.security import decode_access_token

# Map specific route patterns to action names.
# Only these routes get logged automatically; everything else is ignored.
ROUTE_ACTION_MAP = {
    ("POST", "/api/auth/login"): "LOGIN",
    ("POST", "/api/auth/register"): "REGISTER",
    ("POST", "/api/tasks"): "TASK_CREATE",
    ("PATCH", "/api/tasks"): "TASK_UPDATE",
    ("DELETE", "/api/tasks"): "TASK_DELETE",
    ("POST", "/api/documents"): "DOCUMENT_UPLOAD",
}


class ActivityLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Only log successful requests for tracked routes
        if response.status_code < 400:
            self._log_if_tracked(request, response)

        return response

    def _log_if_tracked(self, request: Request, response: Response):
        """Check if this request matches a tracked route and log it."""
        method = request.method
        path = request.url.path

        action = None
        for (route_method, route_path), action_name in ROUTE_ACTION_MAP.items():
            if method == route_method and path.startswith(route_path):
                action = action_name
                break

        if action is None:
            return

        # Try to extract the user ID from the JWT token
        user_id = self._extract_user_id(request)

        # Get the client IP address
        client_ip = request.client.host if request.client else None

        # Build a details dict with some context about the request
        details = {"path": path, "method": method}

        # Write the log entry in its own session
        try:
            db = SessionLocal()
            log_entry = ActivityLog(
                user_id=user_id,
                action=action,
                details=details,
                ip_address=client_ip,
            )
            db.add(log_entry)
            db.commit()
        except Exception:
            # Logging should never break the actual request
            db.rollback()
        finally:
            db.close()

    def _extract_user_id(self, request: Request):
        """Pull the user ID out of the Authorization header if present."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_access_token(token)
            return int(payload.get("sub"))
        except Exception:
            return None
