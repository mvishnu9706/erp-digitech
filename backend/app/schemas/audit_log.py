from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):

    user_id: Optional[int] = None

    module: str

    action: str

    record_id: Optional[int] = None

    old_values: Optional[str] = None

    new_values: Optional[str] = None

    ip_address: Optional[str] = None

    user_agent: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogResponse(AuditLogBase):

    id: int

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class AuditLogListResponse(BaseModel):

    total: int

    page: int

    page_size: int

    items: list[AuditLogResponse]