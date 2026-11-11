from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Boolean
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    # ==================================
    # Primary Key
    # ==================================

    id = Column(Integer, primary_key=True, index=True)

    # ==================================
    # Basic Information
    # ==================================

    product_name = Column(
        String(200),
        nullable=False,
        index=True
    )

    model_no = Column(
        String(100),
        nullable=True
    )

    sku = Column(
        String(100),
        unique=True,
        nullable=True
    )

    barcode = Column(
        String(100),
        unique=True,
        nullable=True
    )

    # ==================================
    # Foreign Keys
    # ==================================

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    brand_id = Column(
        Integer,
        ForeignKey("brands.id"),
        nullable=False
    )

    unit_id = Column(
        Integer,
        ForeignKey("units.id"),
        nullable=False
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )

    # ==================================
    # Pricing
    # ==================================

    cost_price = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    dtp_price = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    retail_price = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    margin_percentage = Column(
        Numeric(5, 2),
        nullable=False,
        default=0
    )

    gst_percentage = Column(
        Numeric(5, 2),
        nullable=False,
        default=18
    )

    hsn_code = Column(
        String(30),
        nullable=True
    )

    # ==================================
    # Inventory
    # ==================================

    minimum_stock = Column(
        Integer,
        nullable=False,
        default=0
    )

    # ==================================
    # Status
    # ==================================

    status = Column(
        String(20),
        nullable=False,
        default="Active"
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    # ==================================
    # Audit
    # ==================================

    created_by = Column(
        Integer,
        nullable=True
    )

    updated_by = Column(
        Integer,
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

    # ==================================
    # Relationships
    # ==================================

    category = relationship(
        "Category",
        lazy="joined"
    )

    brand = relationship(
        "Brand",
        lazy="joined"
    )

    unit = relationship(
        "Unit",
        lazy="joined"
    )

    warehouse = relationship(
        "Warehouse",
        lazy="joined"
    )

    inventory = relationship(
        "Inventory",
        back_populates="product",
        lazy="joined"
    )