from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.chart_of_account import ChartOfAccount
from app.models.journal_entry_line import JournalEntryLine


class TrialBalanceRepository:

    @staticmethod
    def get_trial_balance(db: Session):

        return (

            db.query(

                ChartOfAccount.account_code,

                ChartOfAccount.account_name,

                ChartOfAccount.account_type,

                func.coalesce(
                    func.sum(JournalEntryLine.debit),
                    0
                ).label("debit"),

                func.coalesce(
                    func.sum(JournalEntryLine.credit),
                    0
                ).label("credit")

            )

            .outerjoin(

                JournalEntryLine,

                ChartOfAccount.id
                ==
                JournalEntryLine.account_id

            )

            .filter(
                ChartOfAccount.is_active == True
            )

            .group_by(

                ChartOfAccount.id,

                ChartOfAccount.account_code,

                ChartOfAccount.account_name,

                ChartOfAccount.account_type

            )

            .order_by(

                ChartOfAccount.account_code

            )

            .all()

        )