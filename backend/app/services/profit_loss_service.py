from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.profit_loss_repository import (
    ProfitLossRepository
)


class ProfitLossService:

    @staticmethod
    def get_profit_loss(db: Session):

        income_rows = ProfitLossRepository.get_income_accounts(db)
        expense_rows = ProfitLossRepository.get_expense_accounts(db)

        income = []
        expenses = []

        total_income = Decimal("0")
        total_expense = Decimal("0")

        for row in income_rows:

            amount = Decimal(row.credit) - Decimal(row.debit)

            total_income += amount

            income.append({

                "account_code": row.account_code,

                "account_name": row.account_name,

                "amount": amount

            })

        for row in expense_rows:

            amount = Decimal(row.debit) - Decimal(row.credit)

            total_expense += amount

            expenses.append({

                "account_code": row.account_code,

                "account_name": row.account_name,

                "amount": amount

            })

        gross_profit = total_income

        net_profit = total_income - total_expense

        return {

            "income": income,

            "expenses": expenses,

            "total_income": total_income,

            "total_expense": total_expense,

            "gross_profit": gross_profit,

            "net_profit": net_profit

        }