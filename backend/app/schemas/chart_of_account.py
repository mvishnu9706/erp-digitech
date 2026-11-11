from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Base
# =====================================================

class ChartOfAccountBase(BaseModel):

    account_code: str = Field(..., max_length=20)

    account_name: str = Field(..., max_length=150)

    parent_account_id: Optional[int] = None

    account_type: str

    account_nature: str

    description: Optional[str] = None

    is_active: bool = True


# =====================================================
# Create
# =====================================================

class ChartOfAccountCreate(ChartOfAccountBase):
    pass


# =====================================================
# Update
# =====================================================

class ChartOfAccountUpdate(BaseModel):

    account_name: Optional[str] = None

    parent_account_id: Optional[int] = None

    account_type: Optional[str] = None

    account_nature: Optional[str] = None

    description: Optional[str] = None

    is_active: Optional[bool] = None


# =====================================================
# Response
# =====================================================

class ChartOfAccountResponse(ChartOfAccountBase):

    id: int

    created_at: datetime

    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Dashboard
# =====================================================

class ChartOfAccountDashboardResponse(BaseModel):

    total_accounts: int

    asset_accounts: int

    liability_accounts: int

    equity_accounts: int

    income_accounts: int

    expense_accounts: int