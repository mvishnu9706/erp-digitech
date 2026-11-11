from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Customer Payment Invoice
# =====================================================

class CustomerPaymentInvoiceBase(BaseModel):

    sales_invoice_id: int

    paid_amount: Decimal = Field(..., gt=0)


class CustomerPaymentInvoiceCreate(CustomerPaymentInvoiceBase):
    pass


class CustomerPaymentInvoiceResponse(CustomerPaymentInvoiceBase):

    id: int

    customer_payment_id: int

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Customer Payment
# =====================================================

class CustomerPaymentBase(BaseModel):

    customer_id: int

    payment_date: date

    payment_mode: str

    reference_number: Optional[str] = None

    remarks: Optional[str] = None


# =====================================================
# Create
# =====================================================

class CustomerPaymentCreate(CustomerPaymentBase):

    amount: Decimal = Field(..., gt=0)

    invoices: List[CustomerPaymentInvoiceCreate]


# =====================================================
# Update
# =====================================================

class CustomerPaymentUpdate(BaseModel):

    payment_mode: Optional[str] = None

    reference_number: Optional[str] = None

    remarks: Optional[str] = None


# =====================================================
# Response
# =====================================================

class CustomerPaymentResponse(CustomerPaymentBase):

    id: int

    payment_number: str

    amount: Decimal

    created_by: Optional[int]

    updated_by: Optional[int]

    created_at: datetime

    updated_at: Optional[datetime]

    invoices: List[CustomerPaymentInvoiceResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Dashboard
# =====================================================

class CustomerPaymentDashboardResponse(BaseModel):

    total_payments: int

    total_collection: Decimal

    today_collection: Decimal

    monthly_collection: Decimal