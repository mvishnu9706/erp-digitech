from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    Date,
    DateTime,
    String,
    Text,
    LargeBinary,
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class SalesOrder(Base):

    __tablename__ = "sales_orders"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # Sales Order Number
    # =====================================================

    so_number = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # Sales Reference
    # =====================================================
    #
    # Reference entered manually while creating/editing
    # the sales invoice.
    #
    # Example:
    #   Brother Printer
    #   Customer PO 12345
    #   Website Order
    #   Direct Sale
    #
    # This is displayed in the Sales table under
    # "Reference By".
    #
    # IMPORTANT:
    # reference != created_by
    #
    # created_by:
    #   Logged-in system user
    #
    # reference:
    #   Reference entered for this sale
    #
    # =====================================================

    reference = Column(
        String(150),
        nullable=True,
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
    # Warehouse
    # =====================================================

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # Dates
    # =====================================================

    # -----------------------------------------------------
    # Sales / Invoice Date
    # -----------------------------------------------------

    order_date = Column(
        Date,
        nullable=False
    )

    # -----------------------------------------------------
    # Invoice Due Date
    # -----------------------------------------------------

    due_date = Column(
        Date,
        nullable=True
    )

    # -----------------------------------------------------
    # Expected Delivery Date
    # -----------------------------------------------------
    #
    # Kept for future use.
    # Not currently used in delivery workflow.
    #
    # -----------------------------------------------------

    expected_delivery_date = Column(
        Date,
        nullable=True
    )

    # =====================================================
    # Sales Order Status
    # =====================================================

    status = Column(
        String(30),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
        index=True
    )

    # =====================================================
    # Financial
    # =====================================================

    subtotal = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        server_default="0"
    )

    discount_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        server_default="0"
    )

    gst_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        server_default="0"
    )

    other_charges = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        server_default="0"
    )

    grand_total = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        server_default="0"
    )

    # =====================================================
    # Payment Status
    # =====================================================
    #
    # Supported values:
    #
    # PENDING
    #   No payment received.
    #
    # RECEIVED_BY_HAND
    #   Full payment received by hand.
    #
    # PARTIALLY_RECEIVED_BY_HAND
    #   Partial payment received by hand.
    #
    # RECEIVED_TO_ACCOUNT
    #   Full payment received into account.
    #
    # PARTIALLY_RECEIVED_TO_ACCOUNT
    #   Partial payment received into account.
    #
    # =====================================================

    payment_status = Column(
        String(30),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
        index=True
    )

    # =====================================================
    # Payment Method
    # =====================================================

    payment_method = Column(
        String(30),
        nullable=True
    )

    # =====================================================
    # Payment Reference
    # =====================================================

    payment_reference = Column(
        String(100),
        nullable=True
    )

    # =====================================================
    # Paid Amount
    # =====================================================
    #
    # Stores the amount actually received.
    #
    # Example:
    #
    # Grand Total = ₹10,000
    #
    # PENDING
    #     paid_amount = ₹0
    #
    # PARTIALLY_RECEIVED_BY_HAND
    #     paid_amount = ₹3,000
    #
    # PARTIALLY_RECEIVED_TO_ACCOUNT
    #     paid_amount = ₹5,000
    #
    # RECEIVED_BY_HAND
    #     paid_amount = ₹10,000
    #
    # RECEIVED_TO_ACCOUNT
    #     paid_amount = ₹10,000
    #
    # =====================================================

    paid_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
        server_default="0"
    )

    # =====================================================
    # Remarks
    # =====================================================

    remarks = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # PDF DOCUMENT
    # =====================================================

    pdf_file = Column(
        LargeBinary,
        nullable=True
    )

    # =====================================================
    # PDF File Name
    # =====================================================

    pdf_file_name = Column(
        String(255),
        nullable=True
    )

    # =====================================================
    # PDF MIME Type
    # =====================================================

    pdf_content_type = Column(
        String(100),
        nullable=True,
        default="application/pdf",
        server_default="application/pdf"
    )

    # =====================================================
    # PDF Generated At
    # =====================================================

    pdf_generated_at = Column(
        DateTime(timezone=True),
        nullable=True
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

    # =====================================================
    # Relationships
    # =====================================================

    items = relationship(
        "SalesOrderItem",
        back_populates="sales_order",
        cascade="all, delete-orphan"
    )

    customer = relationship(
        "Customer",
        foreign_keys=[customer_id]
    )

    warehouse = relationship(
        "Warehouse",
        foreign_keys=[warehouse_id]
    )