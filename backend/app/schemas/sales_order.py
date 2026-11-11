from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# =====================================================
# Sales Order Item Base
# =====================================================

class SalesOrderItemBase(BaseModel):

    product_id: int

    quantity: int = Field(
        ...,
        gt=0
    )

    # =================================================
    # Pricing
    # =================================================

    selling_price: Optional[Decimal] = Field(
        default=None,
        ge=0
    )

    discount_percentage: Decimal = Field(
        default=Decimal("0.00"),
        ge=0
    )

    gst_percentage: Optional[Decimal] = Field(
        default=None,
        ge=0
    )

    # =================================================
    # Serial Numbers
    # =================================================

    serial_numbers: List[str] = Field(
        default_factory=list
    )

    # =================================================
    # Remarks
    # =================================================

    remarks: Optional[str] = None


# =====================================================
# Sales Order Item Create
# =====================================================

class SalesOrderItemCreate(
    SalesOrderItemBase
):
    pass


# =====================================================
# Sales Order Item Response
# =====================================================

class SalesOrderItemResponse(BaseModel):

    id: int

    sales_order_id: int

    product_id: int

    quantity: int

    delivered_quantity: int

    pending_quantity: int

    # =================================================
    # Final Pricing
    # =================================================

    selling_price: Decimal

    discount_percentage: Decimal

    discount_amount: Decimal

    gst_percentage: Decimal

    gst_amount: Decimal

    line_total: Decimal

    # =================================================
    # Product Snapshot
    # =================================================

    product_name: str

    sku: Optional[str]

    model_no: Optional[str]

    # =================================================
    # Serial Numbers
    # =================================================

    serial_numbers: List[str] = Field(
        default_factory=list
    )

    # =================================================
    # Remarks
    # =================================================

    remarks: Optional[str] = None

    # =================================================
    # Audit
    # =================================================

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Sales Order Header
# =====================================================

class SalesOrderBase(BaseModel):

    customer_id: int

    warehouse_id: int

    # =================================================
    # Sales Reference
    #
    # This is the reference entered by the user
    # while creating the sale.
    #
    # Example:
    #   Website
    #   Dealer
    #   John
    #   PO-12345
    #   Referral
    # =================================================

    reference: Optional[str] = Field(
        default=None,
        max_length=100
    )

    order_date: date

    # =================================================
    # Invoice Due Date
    # =================================================

    due_date: Optional[date] = None

    # =================================================
    # Expected Delivery Date
    # =================================================

    expected_delivery_date: Optional[date] = None

    # =================================================
    # Remarks
    # =================================================

    remarks: Optional[str] = None


# =====================================================
# Payment Status
# =====================================================

PaymentStatus = Literal[
    "PENDING",
    "RECEIVED_BY_HAND",
    "PARTIALLY_RECEIVED_BY_HAND",
    "RECEIVED_TO_ACCOUNT",
    "PARTIALLY_RECEIVED_TO_ACCOUNT",
]


# =====================================================
# Create Sales Order
# =====================================================

class SalesOrderCreate(
    SalesOrderBase
):

    # =================================================
    # Payment
    # =================================================

    payment_status: PaymentStatus = Field(
        default="PENDING"
    )

    payment_method: Optional[str] = None

    payment_reference: Optional[str] = None

    paid_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0
    )

    # =================================================
    # Items
    # =================================================

    items: List[
        SalesOrderItemCreate
    ] = Field(
        ...,
        min_length=1
    )


# =====================================================
# Update Sales Order
# =====================================================

class SalesOrderUpdate(BaseModel):

    # =================================================
    # Customer
    # =================================================

    customer_id: Optional[int] = None

    # =================================================
    # Warehouse
    # =================================================

    warehouse_id: Optional[int] = None

    # =================================================
    # Sales Reference
    #
    # Allows the reference to be edited later.
    # =================================================

    reference: Optional[str] = Field(
        default=None,
        max_length=100
    )

    # =================================================
    # Sales / Invoice Date
    # =================================================

    order_date: Optional[date] = None

    # =================================================
    # Invoice Due Date
    # =================================================

    due_date: Optional[date] = None

    # =================================================
    # Expected Delivery Date
    # =================================================

    expected_delivery_date: Optional[date] = None

    # =================================================
    # Remarks
    # =================================================

    remarks: Optional[str] = None

    # =================================================
    # Payment Status
    # =================================================

    payment_status: Optional[
        PaymentStatus
    ] = None

    # =================================================
    # Payment Method
    # =================================================

    payment_method: Optional[str] = None

    # =================================================
    # Payment Reference
    # =================================================

    payment_reference: Optional[str] = None

    # =================================================
    # Paid Amount
    # =================================================

    paid_amount: Optional[Decimal] = Field(
        default=None,
        ge=0
    )

    # =================================================
    # Updated Sales Items
    #
    # None:
    #   Do not change existing items.
    #
    # Supplied list:
    #   Replace/update the existing sales items.
    #
    # Inventory is handled by the service.
    #
    # IMPORTANT:
    # Stock is changed only when a sale is
    # completed.
    # =================================================

    items: Optional[
        List[SalesOrderItemCreate]
    ] = None


# =====================================================
# Sales Order Response
# =====================================================

class SalesOrderResponse(
    SalesOrderBase
):

    id: int

    so_number: str

    # =================================================
    # Sales Order Status
    #
    # PENDING
    #   Sale created but not completed.
    #
    # COMPLETED
    #   Sale completed and inventory stock deducted.
    #
    # CANCELLED
    #   Sale cancelled. If stock was already deducted,
    #   the stock is restored.
    # =================================================

    status: str

    # =================================================
    # Financial
    # =================================================

    subtotal: Decimal

    discount_amount: Decimal

    gst_amount: Decimal

    other_charges: Decimal

    grand_total: Decimal

    # =================================================
    # Payment
    # =================================================

    payment_status: Optional[
        PaymentStatus
    ] = None

    payment_method: Optional[str] = None

    payment_reference: Optional[str] = None

    paid_amount: Decimal = Decimal(
        "0.00"
    )

    # =================================================
    # Audit
    # =================================================

    created_by: Optional[int] = None

    updated_by: Optional[int] = None

    created_at: datetime

    updated_at: Optional[datetime] = None

    # =================================================
    # Items
    # =================================================

    items: List[
        SalesOrderItemResponse
    ] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Sales Dashboard
# =====================================================

class SalesDashboardResponse(BaseModel):

    # =================================================
    # Sales Orders
    # =================================================

    total_sales_orders: int

    pending_orders: int

    sales_value: Decimal

    # =================================================
    # Today's Sales
    # =================================================

    todays_sales: Decimal

    # Number of sales orders CREATED today.
    todays_sales_entries: int

    # Backward-compatible alias.
    todays_orders: int

    # Total quantity of products in today's sales entries.
    todays_sales_count: int

    # =================================================
    # Payment
    # =================================================

    unpaid_invoices: int

    pending_payment_amount: Decimal

    # =================================================
    # Monthly Revenue
    # =================================================

    monthly_revenue: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )