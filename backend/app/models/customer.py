from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):

    __tablename__ = "customers"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # CUSTOMER CODE
    # =====================================================

    customer_code = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # CUSTOMER INFORMATION
    # =====================================================

    customer_name = Column(
        String(200),
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
        nullable=True,
        unique=True
    )

    website = Column(
        String(255),
        nullable=True
    )

    # =====================================================
    # TAX DETAILS
    # =====================================================

    gstin = Column(
        String(20),
        nullable=True,
        unique=True
    )

    pan = Column(
        String(20),
        nullable=True,
        unique=True
    )

    # =====================================================
    # ADDRESS
    # =====================================================

    billing_address = Column(
        Text,
        nullable=True
    )

    shipping_address = Column(
        Text,
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

    # =====================================================
    # FINANCIAL INFORMATION
    # =====================================================

    credit_limit = Column(
        Numeric(12, 2),
        default=0
    )

    credit_days = Column(
        Integer,
        default=0
    )

    opening_balance = Column(
        Numeric(12, 2),
        default=0
    )

    current_balance = Column(
        Numeric(12, 2),
        default=0
    )

    # =====================================================
    # SERVICE PORTAL
    # =====================================================

    service_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    # =====================================================
    # REMARKS
    # =====================================================

    remarks = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # STATUS
    # =====================================================

    is_active = Column(
        Boolean,
        default=True
    )

    # =====================================================
    # AUDIT
    # =====================================================

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

    # =====================================================
    # CUSTOMER → MACHINES
    # =====================================================
    #
    # One customer can have:
    #
    # Customer
    #    ├── Machine 1
    #    ├── Machine 2
    #    └── Machine 3
    #
    # Machine.customer_id points to customers.id.
    #
    # This is the reverse side of:
    #
    # Machine.customer
    #
    # =====================================================

    machines = relationship(
        "Machine",
        foreign_keys="Machine.customer_id",
        back_populates="customer",
    )

    # =====================================================
    # CUSTOMER PORTAL USER
    # =====================================================
    #
    # One customer -> one CUSTOMER login.
    #
    # Reverse side of:
    #
    # User.customer_id -> customers.id
    #
    # User.customer_id is UNIQUE, so this relationship
    # is one-to-one from the customer side.
    #
    # =====================================================

    portal_user = relationship(
        "User",
        foreign_keys="User.customer_id",
        back_populates="customer",
        uselist=False,
    )