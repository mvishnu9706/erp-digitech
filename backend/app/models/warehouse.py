from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    warehouse_code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    warehouse_name = Column(
        String(150),
        nullable=False,
        index=True
    )

    contact_person = Column(
        String(150),
        nullable=True
    )

    phone = Column(
        String(20),
        nullable=True
    )

    email = Column(
        String(150),
        nullable=True
    )

    address = Column(
        String(300),
        nullable=True
    )

    city = Column(
        String(100),
        nullable=True
    )

    state = Column(
        String(100),
        nullable=True
    )

    country = Column(
        String(100),
        nullable=True
    )

    pincode = Column(
        String(20),
        nullable=True
    )

    is_default = Column(
        Boolean,
        default=False
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
    inventory = relationship(
        "Inventory",
        back_populates="warehouse",
        lazy="select"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )