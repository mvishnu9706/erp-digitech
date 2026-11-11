from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

from app.repositories.audit_log_repository import (
    AuditLogRepository
)

from app.schemas.audit_log import (
    AuditLogCreate
)


class AuditLogService:

    # =====================================================
    # Create
    # =====================================================

    @staticmethod
    def create(

        db: Session,

        data: AuditLogCreate

    ):

        audit = AuditLog(

            user_id=data.user_id,

            module=data.module,

            action=data.action,

            record_id=data.record_id,

            old_values=data.old_values,

            new_values=data.new_values,

            ip_address=data.ip_address,

            user_agent=data.user_agent

        )

        AuditLogRepository.create(

            db,

            audit

        )

        db.commit()

        db.refresh(audit)

        return audit

    # =====================================================
    # Get Logs
    # =====================================================

    @staticmethod
    def get_logs(

        db: Session,

        page: int = 1,

        page_size: int = 10

    ):

        skip = (page - 1) * page_size

        logs = AuditLogRepository.get_all(

            db,

            skip,

            page_size

        )

        total = AuditLogRepository.count(

            db

        )

        return {

            "total": total,

            "page": page,

            "page_size": page_size,

            "items": logs

        }

    # =====================================================
    # Get Log
    # =====================================================

    @staticmethod
    def get_log(

        db: Session,

        audit_log_id: int

    ):

        log = AuditLogRepository.get_by_id(

            db,

            audit_log_id

        )

        if not log:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Audit log not found."

            )

        return log

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(

        db: Session,

        audit_log_id: int

    ):

        log = AuditLogRepository.get_by_id(

            db,

            audit_log_id

        )

        if not log:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Audit log not found."

            )

        AuditLogRepository.delete(

            db,

            log

        )

        return {

            "success": True,

            "message": "Audit log deleted successfully."

        }