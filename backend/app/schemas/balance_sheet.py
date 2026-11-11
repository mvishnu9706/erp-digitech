from decimal import Decimal
from pydantic import BaseModel


class BalanceSheetItem(BaseModel):

    account_code: str

    account_name: str

    amount: Decimal


class BalanceSheetResponse(BaseModel):

    assets: list[BalanceSheetItem]

    liabilities: list[BalanceSheetItem]

    equity: list[BalanceSheetItem]

    total_assets: Decimal

    total_liabilities: Decimal

    total_equity: Decimal

    total_liabilities_equity: Decimal

    is_balanced: bool