from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text
)

from sqlalchemy.sql import func

from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Supplier Information
    # =====================================================

    supplier_code = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    company_name = Column(
        String(400),
        nullable=False,
        index=True
    )

    contact_person = Column(
        String(150),
        nullable=True
    )

    # =====================================================
    # Contact Details
    # =====================================================

    phone = Column(
        String(27),
        nullable=True
    )

    alternate_phone = Column(
        String(25),
        nullable=True
    )

    contact_designation = Column(
        String(100),
        nullable=True
    )

    email = Column(
        String(150),
        nullable=True
    )

    website = Column(
        String(255),
        nullable=True
    )

    # =====================================================
    # Tax Information
    # =====================================================

    gstin = Column(
        String(20),
        unique=True,
        nullable=True
    )

    pan = Column(
        String(20),
        unique=True,
        nullable=True
    )

    # =====================================================
    # Address
    # =====================================================

    address = Column(
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
    # Financial
    # =====================================================

    credit_limit = Column(
        Numeric(12,2),
        default=0
    )

    credit_days = Column(
        Integer,
        default=0
    )

    opening_balance = Column(
        Numeric(12,2),
        default=0
    )

    current_balance = Column(
        Numeric(12,2),
        default=0
    )

    # =====================================================
    # Remarks
    # =====================================================

    remarks = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # Status
    # =====================================================

    is_active = Column(
        Boolean,
        default=True
    )

    # =====================================================
    # Audit
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