from decimal import Decimal
from datetime import date
from pydantic import BaseModel


class CashBookEntry(BaseModel):

    date: date

    voucher_type: str

    voucher_number: str | None

    description: str | None

    debit: Decimal

    credit: Decimal

    balance: Decimal


class CashBookResponse(BaseModel):

    opening_balance: Decimal

    entries: list[CashBookEntry]
