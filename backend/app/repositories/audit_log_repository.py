from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:

    # =====================================================
    # Create
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        audit_log: AuditLog
    ):

        db.add(audit_log)

        return audit_log

    # =====================================================
    # Get All
    # =====================================================

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 10
    ):

        return (

            db.query(AuditLog)

            .order_by(
                AuditLog.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # Count
    # =====================================================

    @staticmethod
    def count(
        db: Session
    ):

        return db.query(AuditLog).count()

    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        audit_log_id: int
    ):

        return (

            db.query(AuditLog)

            .filter(
                AuditLog.id == audit_log_id
            )

            .first()

        )

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        audit_log: AuditLog
    ):

        db.delete(audit_log)

        db.commit()

        return True