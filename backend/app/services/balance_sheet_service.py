from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.balance_sheet_repository import (
    BalanceSheetRepository
)


class BalanceSheetService:

    @staticmethod
    def get_balance_sheet(db: Session):

        assets_rows = BalanceSheetRepository.get_accounts(
            db,
            "ASSET"
        )

        liabilities_rows = BalanceSheetRepository.get_accounts(
            db,
            "LIABILITY"
        )

        equity_rows = BalanceSheetRepository.get_accounts(
            db,
            "EQUITY"
        )

        assets = []
        liabilities = []
        equity = []

        total_assets = Decimal("0")
        total_liabilities = Decimal("0")
        total_equity = Decimal("0")

        # -----------------------------
        # Assets
        # -----------------------------

        for row in assets_rows:

            amount = Decimal(row.debit) - Decimal(row.credit)

            total_assets += amount

            if amount != 0:

                assets.append({

                    "account_code": row.account_code,

                    "account_name": row.account_name,

                    "amount": amount

                })

        # -----------------------------
        # Liabilities
        # -----------------------------

        for row in liabilities_rows:

            amount = Decimal(row.credit) - Decimal(row.debit)

            total_liabilities += amount

            if amount != 0:

                liabilities.append({

                    "account_code": row.account_code,

                    "account_name": row.account_name,

                    "amount": amount

                })

        # -----------------------------
        # Equity
        # -----------------------------

        for row in equity_rows:

            amount = Decimal(row.credit) - Decimal(row.debit)

            total_equity += amount

            if amount != 0:

                equity.append({

                    "account_code": row.account_code,

                    "account_name": row.account_name,

                    "amount": amount

                })

        total_liabilities_equity = (
            total_liabilities + total_equity
        )

        return {

            "assets": assets,

            "liabilities": liabilities,

            "equity": equity,

            "total_assets": total_assets,

            "total_liabilities": total_liabilities,

            "total_equity": total_equity,

            "total_liabilities_equity": total_liabilities_equity,

            "is_balanced":
                total_assets == total_liabilities_equity

        }