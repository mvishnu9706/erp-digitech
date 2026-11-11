from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class SupplierLedgerEntry(BaseModel):
    date: date
    voucher_type: str
    voucher_number: str
    debit: Decimal
    credit: Decimal
    balance: Decimal


class SupplierLedgerResponse(BaseModel):
    supplier_name: str
    opening_balance: Decimal
    entries: list[SupplierLedgerEntry]
    closing_balance: Decimal
