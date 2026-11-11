from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Purchase Invoice Item
# =====================================================

class PurchaseInvoiceItemBase(BaseModel):

    product_id: int
    
    warehouse_id: int
    
    unit_id: int

    quantity: int = Field(..., gt=0)

    purchase_price: Decimal = Field(..., ge=0)

    discount_percentage: Decimal = Field(default=0, ge=0)

    gst_percentage: Decimal = Field(default=18, ge=0)
    
    hsn_code: Optional[str] = None
    
    serial_number: Optional[str] = None

    remarks: Optional[str] = None


class PurchaseInvoiceItemCreate(PurchaseInvoiceItemBase):
    pass


class PurchaseInvoiceItemResponse(PurchaseInvoiceItemBase):

    id: int
    
    warehouse_id: int
    
    unit_id: int

    purchase_invoice_id: int

    discount_amount: Decimal

    gst_amount: Decimal

    line_total: Decimal

    product_name: str

    sku: Optional[str] = None

    model_no: Optional[str] = None
    
    hsn_code: Optional[str] = None
    
    serial_number: Optional[str] = None

    created_at: datetime

    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Purchase Invoice
# =====================================================

class PurchaseInvoiceBase(BaseModel):

    purchase_order_id: int

    goods_receipt_id: Optional[int] = None

    supplier_id: int

    warehouse_id: int

    invoice_date: date

    due_date: Optional[date] = None

    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class PurchaseInvoiceCreate(PurchaseInvoiceBase):

    items: List[PurchaseInvoiceItemCreate]


# =====================================================
# Update
# =====================================================

class PurchaseInvoiceUpdate(BaseModel):

    due_date: Optional[date] = None

    remarks: Optional[str] = None

    status: Optional[str] = None


# =====================================================
# Response
# =====================================================

class PurchaseInvoiceResponse(PurchaseInvoiceBase):

    id: int

    invoice_number: str

    status: str

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

    items: List[PurchaseInvoiceItemResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Dashboard
# =====================================================

class PurchaseInvoiceDashboardResponse(BaseModel):

    total_invoices: int

    unpaid_invoices: int

    partially_paid_invoices: int

    paid_invoices: int

    cancelled_invoices: int

    total_purchase_amount: Decimal

    total_outstanding: Decimal

    this_month_purchase: Decimal