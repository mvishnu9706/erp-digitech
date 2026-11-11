from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.core.dependencies import get_current_admin

from app.schemas.audit_log import (
    AuditLogCreate,
    AuditLogResponse,
    AuditLogListResponse
)

from app.services.audit_log_service import (
    AuditLogService
)

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)