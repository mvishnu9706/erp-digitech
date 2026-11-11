from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Boolean
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ServiceVisit(Base):

    __tablename__ = "service_visits"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Visit Number
    # =====================================================

    visit_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # Relations
    # =====================================================

    ticket_id = Column(
        Integer,
        ForeignKey("service_tickets.id"),
        nullable=False,
        index=True
    )

    machine_id = Column(
        Integer,
        ForeignKey("machines.id"),
        nullable=False,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    engineer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Visit Details
    # =====================================================

    visit_date = Column(
        Date,
        nullable=False
    )

    start_time = Column(
        DateTime,
        nullable=True
    )

    end_time = Column(
        DateTime,
        nullable=True
    )

    # =====================================================
    # Meter
    # =====================================================

    previous_meter = Column(
        Integer,
        default=0
    )

    current_meter = Column(
        Integer,
        default=0
    )

    # =====================================================
    # Work Details
    # =====================================================

    work_done = Column(
        Text,
        nullable=True
    )

    problem_found = Column(
        Text,
        nullable=True
    )

    solution = Column(
        Text,
        nullable=True
    )

    recommendations = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # Customer Signature
    # =====================================================

    customer_name = Column(
        String(100)
    )

    signature_path = Column(
        String(255)
    )

    # =====================================================
    # Status
    # =====================================================

    status = Column(
        String(30),
        default="OPEN",
        index=True
    )

    remarks = Column(
        Text
    )

    is_active = Column(
        Boolean,
        default=True
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

    ticket = relationship(
        "ServiceTicket"
    )

    machine = relationship(
        "Machine"
    )

    customer = relationship(
        "Customer"
    )

    engineer = relationship(
        "User",
        foreign_keys=[engineer_id]
    )