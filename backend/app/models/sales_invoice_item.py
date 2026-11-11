from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    DateTime,
    String,
    Text
)

from sqlalchemy.sql import func

from app.database import Base


class SalesInvoiceItem(Base):
    __tablename__ = "sales_invoice_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sales_invoice_id = Column(
        Integer,
        ForeignKey("sales_invoices.id"),
        nullable=False,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    selling_price = Column(
        Numeric(12,2),
        nullable=False
    )

    discount_percentage = Column(
        Numeric(5,2),
        default=0
    )

    discount_amount = Column(
        Numeric(12,2),
        default=0
    )

    gst_percentage = Column(
        Numeric(5,2),
        default=18
    )

    gst_amount = Column(
        Numeric(12,2),
        default=0
    )

    line_total = Column(
        Numeric(12,2),
        nullable=False
    )

    product_name = Column(
        String(200),
        nullable=False
    )

    sku = Column(
        String(100)
    )

    model_no = Column(
        String(100)
    )

    remarks = Column(
        Text
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