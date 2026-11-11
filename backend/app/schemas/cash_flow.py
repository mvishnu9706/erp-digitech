from decimal import Decimal
from pydantic import BaseModel


class CashFlowItem(BaseModel):

    account_code: str

    account_name: str

    amount: Decimal


class CashFlowResponse(BaseModel):

    operating: list[CashFlowItem]

    investing: list[CashFlowItem]

    financing: list[CashFlowItem]

    operating_cash_flow: Decimal

    investing_cash_flow: Decimal

    financing_cash_flow: Decimal

    net_cash_flow: Decimal