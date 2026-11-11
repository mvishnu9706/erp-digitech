from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey
)

from sqlalchemy.sql import func

from app.database import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False,
        unique=True
    )

    code = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    logo = Column(
        String(255),
        nullable=True
    )

    website = Column(
        String(255),
        nullable=True
    )

    email = Column(
        String(150),
        nullable=True
    )

    phone = Column(
        String(20),
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )