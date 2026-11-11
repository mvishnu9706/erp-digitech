from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogger:

    @staticmethod
    def log(
        db: Session,
        user=None,
        module: str = "",
        action: str = "",
        record_id: Optional[int] = None,
        description: Optional[str] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Generic Audit Logger

        Example:

        AuditLogger.log(
            db=db,
            user=current_user,
            module="Sales Invoice",
            action="CREATE",
            record_id=invoice.id,
            description=f"Created {invoice.invoice_number}"
        )
        """

        audit = AuditLog(

            user_id=user.id if user else None,

            module=module,

            action=action,

            record_id=record_id,

            description=description,

            ip_address=ip,

            user_agent=user_agent

        )

        db.add(audit)

        db.commit()

        db.refresh(audit)

        return audit

    # ====================================================
    # CREATE
    # ====================================================

    @staticmethod
    def create(
        db: Session,
        user,
        module: str,
        record_id: int,
        description: str,
        ip: str = None,
        user_agent: str = None,
    ):

        return AuditLogger.log(

            db=db,

            user=user,

            module=module,

            action="CREATE",

            record_id=record_id,

            description=description,

            ip=ip,

            user_agent=user_agent

        )

    # ====================================================
    # UPDATE
    # ====================================================

    @staticmethod
    def update(
        db: Session,
        user,
        module: str,
        record_id: int,
        description: str,
        ip: str = None,
        user_agent: str = None,
    ):

        return AuditLogger.log(

            db=db,

            user=user,

            module=module,

            action="UPDATE",

            record_id=record_id,

            description=description,

            ip=ip,

            user_agent=user_agent

        )

    # ====================================================
    # DELETE
    # ====================================================

    @staticmethod
    def delete(
        db: Session,
        user,
        module: str,
        record_id: int,
        description: str,
        ip: str = None,
        user_agent: str = None,
    ):

        return AuditLogger.log(

            db=db,

            user=user,

            module=module,

            action="DELETE",

            record_id=record_id,

            description=description,

            ip=ip,

            user_agent=user_agent

        )

    # ====================================================
    # LOGIN
    # ====================================================

    @staticmethod
    def login(
        db: Session,
        user,
        ip: str = None,
        user_agent: str = None,
    ):

        return AuditLogger.log(

            db=db,

            user=user,

            module="Authentication",

            action="LOGIN",

            description=f"{user.full_name} logged in.",

            ip=ip,

            user_agent=user_agent

        )

    # ====================================================
    # LOGOUT
    # ====================================================

    @staticmethod
    def logout(
        db: Session,
        user,
        ip: str = None,
        user_agent: str = None,
    ):

        return AuditLogger.log(

            db=db,

            user=user,

            module="Authentication",

            action="LOGOUT",

            description=f"{user.full_name} logged out.",

            ip=ip,

            user_agent=user_agent

        )

    # ====================================================
    # APPROVE
    # ====================================================

    @staticmethod
    def approve(
        db: Session,
        user,
        module: str,
        record_id: int,
        description: str,
        ip: str = None,
        user_agent: str = None,
    ):

        return AuditLogger.log(

            db=db,

            user=user,

            module=module,

            action="APPROVE",

            record_id=record_id,

            description=description,

            ip=ip,

            user_agent=user_agent

        )

    # ====================================================
    # REJECT
    # ====================================================

    @staticmethod
    def reject(
        db: Session,
        user,
        module: str,
        record_id: int,
        description: str,
        ip: str = None,
        user_agent: str = None,
    ):

        return AuditLogger.log(

            db=db,

            user=user,

            module=module,

            action="REJECT",

            record_id=record_id,

            description=description,

            ip=ip,

            user_agent=user_agent

        )