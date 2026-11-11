from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.chart_of_account import ChartOfAccount
from app.models.journal_entry_line import JournalEntryLine


class ProfitLossRepository:

    @staticmethod
    def get_income_accounts(db: Session):

        return (

            db.query(

                ChartOfAccount.account_code,

                ChartOfAccount.account_name,

                func.coalesce(
                    func.sum(JournalEntryLine.credit),
                    0
                ).label("credit"),

                func.coalesce(
                    func.sum(JournalEntryLine.debit),
                    0
                ).label("debit")

            )

            .outerjoin(

                JournalEntryLine,

                ChartOfAccount.id
                ==
                JournalEntryLine.account_id

            )

            .filter(

                ChartOfAccount.account_type == "INCOME"

            )

            .group_by(

                ChartOfAccount.account_code,

                ChartOfAccount.account_name

            )

            .all()

        )

    @staticmethod
    def get_expense_accounts(db: Session):

        return (

            db.query(

                ChartOfAccount.account_code,

                ChartOfAccount.account_name,

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

                ChartOfAccount.account_type == "EXPENSE"

            )

            .group_by(

                ChartOfAccount.account_code,

                ChartOfAccount.account_name

            )

            .all()

        )