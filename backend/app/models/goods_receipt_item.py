from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    DateTime,
    Text
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class GoodsReceiptItem(Base):
    __tablename__ = "goods_receipt_items"

    # =====================================
    # Primary Key
    # =====================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================
    # Goods Receipt
    # =====================================

    goods_receipt_id = Column(
        Integer,
        ForeignKey("goods_receipts.id"),
        nullable=False,
        index=True
    )

    # =====================================
    # Purchase Order Item
    # =====================================

    purchase_order_item_id = Column(
        Integer,
        ForeignKey("purchase_order_items.id"),
        nullable=False,
        index=True
    )

    # =====================================
    # Product
    # =====================================

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    # =====================================
    # Received Quantity
    # =====================================

    received_quantity = Column(
        Integer,
        nullable=False
    )

    # =====================================
    # Purchase Price
    # =====================================

    purchase_price = Column(
        Numeric(12,2),
        nullable=False
    )

    # =====================================
    # Remarks
    # =====================================

    remarks = Column(
        Text,
        nullable=True
    )

    # =====================================
    # Audit
    # =====================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    goods_receipt = relationship("GoodsReceipt")

    purchase_order_item = relationship("PurchaseOrderItem")

    product = relationship("Product")