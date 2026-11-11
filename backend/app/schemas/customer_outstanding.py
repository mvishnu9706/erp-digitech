from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class CustomerOutstandingEntry(BaseModel):
    customer_id: int
    customer_name: str
    invoice_number: str
    invoice_date: date
    due_date: date | None = None
    invoice_total: Decimal
    outstanding_amount: Decimal
    days_overdue: int
