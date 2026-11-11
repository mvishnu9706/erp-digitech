from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Sales Invoice Item
# =====================================================

class SalesInvoiceItemBase(BaseModel):

    product_id: int

    quantity: int = Field(..., gt=0)

    selling_price: Decimal = Field(..., ge=0)

    discount_percentage: Decimal = Field(default=0, ge=0)

    gst_percentage: Decimal = Field(default=18, ge=0)

    remarks: Optional[str] = None


class SalesInvoiceItemCreate(SalesInvoiceItemBase):
    pass


class SalesInvoiceItemResponse(SalesInvoiceItemBase):

    id: int

    sales_invoice_id: int

    discount_amount: Decimal

    gst_amount: Decimal

    line_total: Decimal

    product_name: str

    sku: Optional[str] = None

    model_no: Optional[str] = None

    created_at: datetime

    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Sales Invoice
# =====================================================

class SalesInvoiceBase(BaseModel):

    delivery_challan_id: int

    invoice_date: date

    due_date: Optional[date] = None

    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class SalesInvoiceCreate(SalesInvoiceBase):
    pass


# =====================================================
# Update
# =====================================================

class SalesInvoiceUpdate(BaseModel):

    due_date: Optional[date] = None

    remarks: Optional[str] = None

    status: Optional[str] = None


# =====================================================
# Response
# =====================================================

class SalesInvoiceResponse(SalesInvoiceBase):

    id: int

    invoice_number: str

    status: str

    payment_status: str

    subtotal: Decimal

    discount_amount: Decimal

    gst_amount: Decimal

    other_charges: Decimal

    grand_total: Decimal

    paid_amount: Decimal

    balance_amount: Decimal

    created_by: Optional[int] = None

    updated_by: Optional[int] = None

    created_at: datetime

    updated_at: Optional[datetime] = None

    items: List[SalesInvoiceItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Dashboard
# =====================================================

class SalesInvoiceDashboardResponse(BaseModel):

    total_invoices: int

    unpaid_invoices: int

    partially_paid_invoices: int

    paid_invoices: int

    cancelled_invoices: int

    total_sales: Decimal