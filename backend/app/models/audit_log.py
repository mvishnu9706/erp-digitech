from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func

from app.database import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    module = Column(
        String(100),
        nullable=False
    )

    action = Column(
        String(50),
        nullable=False
    )

    record_id = Column(
        Integer,
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    ip_address = Column(
        String(50)
    )

    user_agent = Column(
        Text
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )