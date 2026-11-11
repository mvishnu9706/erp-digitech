from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.chart_of_account import ChartOfAccount
from app.models.journal_entry_line import JournalEntryLine


class CashFlowRepository:

    @staticmethod
    def get_accounts(db: Session):

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

                ChartOfAccount.id ==
                JournalEntryLine.account_id

            )

            .group_by(

                ChartOfAccount.account_code,

                ChartOfAccount.account_name,

                ChartOfAccount.account_type

            )

            .all()

        )