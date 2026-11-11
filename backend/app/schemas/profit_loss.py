from decimal import Decimal
from pydantic import BaseModel


class ProfitLossItem(BaseModel):

    account_code: str

    account_name: str

    amount: Decimal


class ProfitLossResponse(BaseModel):

    income: list[ProfitLossItem]

    expenses: list[ProfitLossItem]

    total_income: Decimal

    total_expense: Decimal

    gross_profit: Decimal

    net_profit: Decimal