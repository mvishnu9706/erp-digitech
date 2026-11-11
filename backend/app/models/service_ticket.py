from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ServiceTicket(Base):

    __tablename__ = "service_tickets"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # TICKET DETAILS
    # =====================================================

    ticket_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    subject = Column(
        String(200),
        nullable=False
    )

    complaint = Column(
        Text,
        nullable=False
    )

    # Detailed problem submitted by customer
    problem_description = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # METER READING
    # =====================================================

    meter_reading = Column(
        Integer,
        nullable=True,
        default=0
    )

    # =====================================================
    # PRIORITY
    # =====================================================

    priority = Column(
        String(20),
        nullable=False,
        default="MEDIUM",
        index=True
    )

    # =====================================================
    # STATUS
    #
    # REQUESTED
    # ASSIGNED
    # IN_PROGRESS
    # ON_HOLD
    # PARTS_PENDING
    # COMPLETED
    # CLOSED
    # CANCELLED
    # =====================================================

    status = Column(
        String(30),
        nullable=False,
        default="REQUESTED",
        index=True
    )

    # =====================================================
    # REQUEST SOURCE
    #
    # CUSTOMER
    # ADMIN
    # =====================================================

    request_source = Column(
        String(20),
        nullable=False,
        default="CUSTOMER"
    )

    # =====================================================
    # CUSTOMER
    # =====================================================

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    # The actual login that submitted the request
    requested_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # MACHINE
    # =====================================================

    machine_id = Column(
        Integer,
        ForeignKey("machines.id"),
        nullable=False,
        index=True
    )

    serial_number = Column(
        String(100),
        nullable=True
    )

    # =====================================================
    # ENGINEER
    # =====================================================

    assigned_engineer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    # =====================================================
    # DATES
    # =====================================================

    reported_date = Column(
        Date,
        nullable=False
    )

    expected_visit_date = Column(
        Date,
        nullable=True
    )

    completed_date = Column(
        Date,
        nullable=True
    )

    # =====================================================
    # TIMELINE
    # =====================================================

    assigned_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    closed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # =====================================================
    # RESOLUTION
    # =====================================================

    resolution = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # MATERIAL USED
    # =====================================================

    material_used = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # SERVICE COST
    # =====================================================

    service_cost = Column(
        Numeric(
            12,
            2
        ),
        nullable=True
    )

    # =====================================================
    # PAYMENT STATUS
    #
    # Single source of truth for payment status.
    #
    # Values:
    #     PENDING
    #     RECEIVED
    #
    # Engineer selects the value.
    # Backend persists it in service_tickets.
    # Admin reads the same value.
    # =====================================================

    payment_status = Column(
        String(20),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
        index=True
    )

    # =====================================================
    # WARRANTY / AMC
    # =====================================================

    is_warranty = Column(
        String(5),
        default="NO"
    )

    is_amc = Column(
        String(5),
        default="NO"
    )

    # =====================================================
    # CUSTOMER PORTAL STATUS
    # =====================================================

    customer_status = Column(
        String(30),
        nullable=False,
        default="REQUESTED"
    )

    # =====================================================
    # AUDIT
    # =====================================================

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    customer = relationship(
        "Customer",
        foreign_keys=[customer_id]
    )

    machine = relationship(
        "Machine",
        foreign_keys=[machine_id]
    )

    assigned_engineer = relationship(
        "User",
        foreign_keys=[assigned_engineer_id]
    )

    requested_by = relationship(
        "User",
        foreign_keys=[requested_by_user_id]
    )

    created_user = relationship(
        "User",
        foreign_keys=[created_by]
    )

    updated_user = relationship(
        "User",
        foreign_keys=[updated_by]
    )