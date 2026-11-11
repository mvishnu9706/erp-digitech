from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.trial_balance_repository import (
    TrialBalanceRepository
)


class TrialBalanceService:

    @staticmethod
    def get_trial_balance(db: Session):

        rows = TrialBalanceRepository.get_trial_balance(db)

        accounts = []

        total_debit = Decimal("0")
        total_credit = Decimal("0")

        for row in rows:

            debit = Decimal(row.debit)
            credit = Decimal(row.credit)

            balance = debit - credit

            if balance >= 0:
                debit = balance
                credit = Decimal("0")
            else:
                debit = Decimal("0")
                credit = abs(balance)

            total_debit += debit
            total_credit += credit

            accounts.append(

                {

                    "account_code": row.account_code,

                    "account_name": row.account_name,

                    "account_type": row.account_type,

                    "debit": debit,

                    "credit": credit

                }

            )

        return {

            "accounts": accounts,

            "total_debit": total_debit,

            "total_credit": total_credit,

            "is_balanced": total_debit == total_credit

        }