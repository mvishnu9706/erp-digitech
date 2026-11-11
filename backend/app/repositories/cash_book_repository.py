from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry
from app.models.journal_entry_line import JournalEntryLine
from app.models.chart_of_account import ChartOfAccount


class CashBookRepository:

    @staticmethod
    def get_entries(db: Session, from_date=None, to_date=None):

        query = (

            db.query(

                JournalEntry,

                JournalEntryLine,

                ChartOfAccount

            )

            .join(

                JournalEntryLine,

                JournalEntry.id == JournalEntryLine.journal_entry_id

            )

            .join(

                ChartOfAccount,

                ChartOfAccount.id == JournalEntryLine.account_id

            )

            .filter(

                ChartOfAccount.account_code.startswith("10")

            )

        )

        if from_date:

            query = query.filter(

                JournalEntry.journal_date >= from_date

            )

        if to_date:

            query = query.filter(

                JournalEntry.journal_date <= to_date

            )

        return query.order_by(

            JournalEntry.journal_date,

            JournalEntry.id

        ).all()
