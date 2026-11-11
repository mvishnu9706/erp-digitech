from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PMSchedule(Base):

    __tablename__ = "pm_schedules"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # PM Number
    # =====================================================

    pm_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # Relations
    # =====================================================

    amc_contract_id = Column(
        Integer,
        ForeignKey("amc_contracts.id"),
        nullable=False
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    machine_id = Column(
        Integer,
        ForeignKey("machines.id"),
        nullable=False
    )

    engineer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # =====================================================
    # PM Details
    # =====================================================

    scheduled_date = Column(
        Date,
        nullable=False,
        index=True
    )

    completed_date = Column(
        Date,
        nullable=True
    )

    frequency_days = Column(
        Integer,
        default=90
    )

    status = Column(
        String(30),
        default="PENDING",
        index=True
    )

    auto_generated = Column(
        Boolean,
        default=True
    )

    remarks = Column(
        Text
    )

    # =====================================================
    # Audit
    # =====================================================

    created_by = Column(
        Integer,
        ForeignKey("users.id")
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id")
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

    # =====================================================
    # Relationships
    # =====================================================

    contract = relationship("AMCContract")

    customer = relationship("Customer")

    machine = relationship("Machine")

    engineer = relationship(
        "User",
        foreign_keys=[engineer_id]
    )