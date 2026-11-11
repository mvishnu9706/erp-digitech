from typing import Optional
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import (
    AuditLogRepository
)


class AuditService:

    @staticmethod  
    def log(

        db: Session,

        user_id: Optional[int],

        module: str,

        action: str,

        record_id: Optional[int] = None,

        old_values: Optional[str] = None,

        new_values: Optional[str] = None,

        ip_address: Optional[str] = None,

        user_agent: Optional[str] = None

    ):

        audit = AuditLog(

            user_id=user_id,

            module=module,

            action=action,

            record_id=record_id,

            old_values=old_values,

            new_values=new_values,

            ip_address=ip_address,

            user_agent=user_agent

        )

        AuditLogRepository.create(

            db,

            audit

        )

        db.commit()

        db.refresh(audit)

        return audit