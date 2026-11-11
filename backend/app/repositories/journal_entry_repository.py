from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry
from app.models.journal_entry_line import JournalEntryLine


class JournalEntryRepository:

    # =====================================================
    # Create Journal Entry
    # =====================================================

    @staticmethod
    def create(
        db: Session,
        journal: JournalEntry,
        lines: list[JournalEntryLine]
    ):

        db.add(journal)

        db.flush()

        for line in lines:

            line.journal_entry_id = journal.id

            db.add(line)

        return journal

    # =====================================================
    # Get All Journal Entries
    # =====================================================

    @staticmethod
    def get_all(

        db: Session,

        search: str = None,

        voucher_type: str = None,

        skip: int = 0,

        limit: int = 10

    ):

        query = db.query(JournalEntry)

        if search:

            query = query.filter(

                JournalEntry.journal_number.ilike(
                    f"%{search}%"
                )

            )

        if voucher_type:

            query = query.filter(
                JournalEntry.voucher_type == voucher_type
            )

        return (

            query

            .order_by(
                JournalEntry.id.desc()
            )

            .offset(skip)

            .limit(limit)

            .all()

        )

    # =====================================================
    # Get By ID
    # =====================================================

    @staticmethod
    def get_by_id(
        db: Session,
        journal_id: int
    ):

        return (

            db.query(JournalEntry)

            .filter(
                JournalEntry.id == journal_id
            )

            .first()

        )

    # =====================================================
    # Get Journal Lines
    # =====================================================

    @staticmethod
    def get_lines(
        db: Session,
        journal_id: int
    ):

        return (

            db.query(JournalEntryLine)

            .filter(
                JournalEntryLine.journal_entry_id == journal_id
            )

            .all()

        )

    # =====================================================
    # Last Journal
    # =====================================================

    @staticmethod
    def last_journal(
        db: Session
    ):

        return (

            db.query(JournalEntry)

            .order_by(
                JournalEntry.id.desc()
            )

            .first()

        )

    # =====================================================
    # Update
    # =====================================================

    @staticmethod
    def update(
        db: Session,
        journal: JournalEntry
    ):

        db.commit()

        db.refresh(journal)

        return journal

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete(
        db: Session,
        journal: JournalEntry
    ):

        db.delete(journal)

        db.commit()

        return True

    # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        total_debit = (

            db.query(

                func.coalesce(

                    func.sum(
                        JournalEntryLine.debit
                    ),

                    0

                )

            )

            .scalar()

        )

        total_credit = (

            db.query(

                func.coalesce(

                    func.sum(
                        JournalEntryLine.credit
                    ),

                    0

                )

            )

            .scalar()

        )

        return {

            "total_entries":

                db.query(
                    JournalEntry
                ).count(),

            "today_entries":

                db.query(
                    JournalEntry
                )
                .filter(
                    func.current_date() == JournalEntry.journal_date
                )
                .count(),

            "monthly_entries":

                db.query(
                    JournalEntry
                )
                .filter(

                    func.extract(
                        "month",
                        JournalEntry.journal_date
                    ) == func.extract(
                        "month",
                        func.current_date()
                    ),

                    func.extract(
                        "year",
                        JournalEntry.journal_date
                    ) == func.extract(
                        "year",
                        func.current_date()
                    )

                )
                .count(),

            "total_debit": total_debit,

            "total_credit": total_credit

        }