from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Numeric,
    Boolean,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database import Base


class Machine(Base):
    __tablename__ = "machines"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # =====================================================
    # MACHINE INFORMATION
    # =====================================================

    machine_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    machine_name = Column(
        String(200),
        nullable=False,
    )

    serial_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    asset_tag = Column(
        String(100),
        unique=True,
        nullable=True,
    )

    # =====================================================
    # CUSTOMER AND PRODUCT
    # =====================================================

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=True,
        index=True,
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=True,
        index=True,
    )

    # =====================================================
    # INSTALLATION
    # =====================================================

    installation_date = Column(
        Date,
        nullable=True,
    )

    installation_address = Column(
        Text,
        nullable=True,
    )

    installed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    # =====================================================
    # WARRANTY
    # =====================================================

    warranty_start_date = Column(
        Date,
        nullable=True,
    )

    warranty_end_date = Column(
        Date,
        nullable=True,
    )

    # =====================================================
    # AMC
    # =====================================================

    amc_start_date = Column(
        Date,
        nullable=True,
    )

    amc_end_date = Column(
        Date,
        nullable=True,
    )

    # =====================================================
    # LEGACY AGGREGATE METER FIELDS
    # Retained for existing ERP functionality.
    # =====================================================

    opening_meter = Column(
        Integer,
        default=0,
        nullable=False,
    )

    current_meter = Column(
        Integer,
        default=0,
        nullable=False,
    )

    # =====================================================
    # INDIVIDUAL METER READINGS
    # =====================================================

    a4_bw_current_meter = Column(
        Integer,
        default=0,
        nullable=False,
    )

    a4_color_current_meter = Column(
        Integer,
        default=0,
        nullable=False,
    )

    a3_bw_current_meter = Column(
        Integer,
        default=0,
        nullable=False,
    )

    a3_color_current_meter = Column(
        Integer,
        default=0,
        nullable=False,
    )

    # =====================================================
    # RENTAL CONFIGURATION
    # =====================================================

    rental_rate = Column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    rental_advance = Column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    # Legacy common free-copy allowance.
    # Retained for backward compatibility.
    free_prints_per_month = Column(
        Integer,
        default=0,
        nullable=False,
    )

    # =====================================================
    # INDIVIDUAL MONTHLY FREE-COPY ALLOWANCES
    # =====================================================

    a4_bw_free_copies = Column(
        Integer,
        default=0,
        nullable=False,
    )

    a4_color_free_copies = Column(
        Integer,
        default=0,
        nullable=False,
    )

    a3_bw_free_copies = Column(
        Integer,
        default=0,
        nullable=False,
    )

    a3_color_free_copies = Column(
        Integer,
        default=0,
        nullable=False,
    )

    # =====================================================
    # INDIVIDUAL PER-COPY BILLING RATES
    # =====================================================

    a4_bw_rate = Column(
        Numeric(12, 4),
        default=0,
        nullable=False,
    )

    a4_color_rate = Column(
        Numeric(12, 4),
        default=0,
        nullable=False,
    )

    a3_bw_rate = Column(
        Numeric(12, 4),
        default=0,
        nullable=False,
    )

    a3_color_rate = Column(
        Numeric(12, 4),
        default=0,
        nullable=False,
    )

    # Legacy price field for older billing endpoints.
    cost_per_copy = Column(
        Numeric(12, 2),
        default=0,
        nullable=False,
    )

    # =====================================================
    # STATUS
    # =====================================================

    status = Column(
        String(50),
        default="ACTIVE",
        nullable=False,
        index=True,
    )

    service_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    remarks = Column(
        Text,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # =====================================================
    # AUDIT FIELDS
    # =====================================================

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    customer = relationship(
        "Customer",
        foreign_keys=[customer_id],
        back_populates="machines",
    )

    product = relationship(
        "Product",
        foreign_keys=[product_id],
    )

    installer = relationship(
        "User",
        foreign_keys=[installed_by],
    )

    created_user = relationship(
        "User",
        foreign_keys=[created_by],
    )

    updated_user = relationship(
        "User",
        foreign_keys=[updated_by],
    )

    # =====================================================
    # MACHINE DOCUMENTS
    # =====================================================

    documents = relationship(
        "MachineDocument",
        back_populates="machine",
        uselist=False,
        cascade="all, delete-orphan",
    )