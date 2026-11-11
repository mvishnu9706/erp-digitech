from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Numeric,
    Boolean,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class AMCContract(Base):

    __tablename__ = "amc_contracts"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Contract Number
    # =====================================================

    contract_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # Customer
    # =====================================================

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Machine
    # =====================================================

    machine_id = Column(
        Integer,
        ForeignKey("machines.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Contract Details
    # =====================================================

    contract_type = Column(
        String(30),
        nullable=False,
        default="AMC"
    )

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
        nullable=False
    )

    amount = Column(
        Numeric(12,2),
        default=0
    )

    gst_percentage = Column(
        Numeric(5,2),
        default=18
    )

    free_black_copies = Column(
        Integer,
        default=0
    )

    free_color_copies = Column(
        Integer,
        default=0
    )

    black_cost_per_copy = Column(
        Numeric(12,4),
        default=0
    )

    color_cost_per_copy = Column(
        Numeric(12,4),
        default=0
    )

    included_service_visits = Column(
        Integer,
        default=12
    )

    used_service_visits = Column(
        Integer,
        default=0
    )

    # =====================================================
    # Renewal
    # =====================================================

    auto_renew = Column(
        Boolean,
        default=False
    )

    renewal_reminder_days = Column(
        Integer,
        default=30
    )

    # =====================================================
    # Status
    # =====================================================

    status = Column(
        String(20),
        default="ACTIVE",
        index=True
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

    customer = relationship("Customer")

    machine = relationship("Machine")

    creator = relationship(
        "User",
        foreign_keys=[created_by]
    )

    updater = relationship(
        "User",
        foreign_keys=[updated_by]
    )