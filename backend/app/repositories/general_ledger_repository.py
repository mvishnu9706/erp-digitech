from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry
from app.models.journal_entry_line import JournalEntryLine


class GeneralLedgerRepository:

    @staticmethod
    def get_transactions(

        db: Session,

        account_id: int,

        from_date=None,

        to_date=None

    ):

        query = (

            db.query(

                JournalEntry,

                JournalEntryLine

            )

            .join(

                JournalEntryLine,

                JournalEntry.id
                ==
                JournalEntryLine.journal_entry_id

            )

            .filter(

                JournalEntryLine.account_id
                ==
                account_id

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

    @staticmethod
    def get_opening_balance(
        db: Session,
        account_id: int,
        account_nature: str,
        from_date
    ):

        if not from_date:
            return Decimal("0")

        transactions = (
            db.query(
                JournalEntry,
                JournalEntryLine
            )
            .join(
                JournalEntryLine,
                JournalEntry.id == JournalEntryLine.journal_entry_id
            )
            .filter(
                JournalEntryLine.account_id == account_id,
                JournalEntry.journal_date < from_date
            )
            .order_by(
                JournalEntry.journal_date,
                JournalEntry.id
            )
            .all()
        )

        balance = Decimal("0")

        for _, line in transactions:

            if account_nature == "DEBIT":
                balance += Decimal(line.debit)
                balance -= Decimal(line.credit)
            else:
                balance += Decimal(line.credit)
                balance -= Decimal(line.debit)

        return balance