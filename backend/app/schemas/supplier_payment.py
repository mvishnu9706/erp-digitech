from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Supplier Payment Invoice
# =====================================================

class SupplierPaymentInvoiceBase(BaseModel):

    purchase_invoice_id: int

    paid_amount: Decimal = Field(..., gt=0)


class SupplierPaymentInvoiceCreate(
    SupplierPaymentInvoiceBase
):
    pass


class SupplierPaymentInvoiceResponse(
    SupplierPaymentInvoiceBase
):

    id: int

    supplier_payment_id: int

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Supplier Payment
# =====================================================

class SupplierPaymentBase(BaseModel):

    supplier_id: int

    payment_date: date

    payment_mode: str

    reference_number: Optional[str] = None

    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class SupplierPaymentCreate(
    SupplierPaymentBase
):

    amount: Decimal = Field(..., gt=0)

    invoices: List[
        SupplierPaymentInvoiceCreate
    ]


# =====================================================
# Update
# =====================================================

class SupplierPaymentUpdate(BaseModel):

    payment_mode: Optional[str] = None

    reference_number: Optional[str] = None

    remarks: Optional[str] = None


# =====================================================
# Response
# =====================================================

class SupplierPaymentResponse(
    SupplierPaymentBase
):

    id: int

    payment_number: str

    amount: Decimal

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    invoices: List[
        SupplierPaymentInvoiceResponse
    ] = []

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Dashboard
# =====================================================

class SupplierPaymentDashboardResponse(
    BaseModel
):

    total_payments: int

    total_payment_amount: Decimal

    today_payment: Decimal

    monthly_payment: Decimal