from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.chart_of_account import ChartOfAccount
from app.models.journal_entry_line import JournalEntryLine


class BalanceSheetRepository:

    @staticmethod
    def get_accounts(db: Session, account_type: str):

        return (

            db.query(

                ChartOfAccount.account_code,

                ChartOfAccount.account_name,

                ChartOfAccount.account_nature,

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

                ChartOfAccount.account_type == account_type,

                ChartOfAccount.is_active == True

            )

            .group_by(

                ChartOfAccount.id,

                ChartOfAccount.account_code,

                ChartOfAccount.account_name,

                ChartOfAccount.account_nature

            )

            .order_by(

                ChartOfAccount.account_code

            )

            .all()

        )