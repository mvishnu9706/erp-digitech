from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry
from app.models.journal_entry_line import JournalEntryLine

from app.repositories.chart_of_account_repository import (
    ChartOfAccountRepository
)

from app.repositories.journal_entry_repository import (
    JournalEntryRepository
)

from app.schemas.journal_entry import (
    JournalEntryCreate
)

from app.utils.journal_number import (
    JournalNumberGenerator
)


class JournalEntryService:

    # =====================================================
    # Create Journal Entry
    # =====================================================

    @staticmethod
    def create_journal_entry(
        db: Session,
        data: JournalEntryCreate,
        current_user
    ):

        try:

            # ============================================
            # Validate Journal Lines
            # ============================================

            if len(data.lines) < 2:

                raise HTTPException(

                    status_code=400,

                    detail="Journal Entry requires at least two lines."

                )

            total_debit = Decimal("0")

            total_credit = Decimal("0")

            journal_lines = []

            # ============================================
            # Validate Accounts
            # ============================================

            for line in data.lines:

                account = ChartOfAccountRepository.get_by_id(

                    db,

                    line.account_id

                )

                if not account:

                    raise HTTPException(

                        status_code=404,

                        detail=f"Account {line.account_id} not found."

                    )

                if line.debit < 0 or line.credit < 0:

                    raise HTTPException(

                        status_code=400,

                        detail="Negative values are not allowed."

                    )

                if line.debit > 0 and line.credit > 0:

                    raise HTTPException(

                        status_code=400,

                        detail="A journal line cannot have both debit and credit."

                    )

                if line.debit == 0 and line.credit == 0:

                    raise HTTPException(

                        status_code=400,

                        detail="Debit or Credit amount is required."

                    )

                total_debit += line.debit

                total_credit += line.credit

                journal_line = JournalEntryLine(

                    account_id=line.account_id,

                    debit=line.debit,

                    credit=line.credit,

                    description=line.description

                )

                journal_lines.append(journal_line)

            # ============================================
            # Double Entry Validation
            # ============================================

            if total_debit != total_credit:

                raise HTTPException(

                    status_code=400,

                    detail="Total Debit must equal Total Credit."

                )

            # ============================================
            # Generate Journal Number
            # ============================================

            last_journal = JournalEntryRepository.last_journal(db)

            if last_journal:

                journal_number = JournalNumberGenerator.generate(

                    last_journal.id + 1

                )

            else:

                journal_number = JournalNumberGenerator.generate(1)

            # ============================================
            # Create Journal Header
            # ============================================

            journal = JournalEntry(

                journal_number=journal_number,

                voucher_type=data.voucher_type,

                reference_id=data.reference_id,

                reference_number=data.reference_number,

                journal_date=data.journal_date,

                remarks=data.remarks,

                created_by=current_user.id,

                updated_by=current_user.id

            )
                        # ============================================
            # Save Journal Entry
            # ============================================

            journal = JournalEntryRepository.create(

                db,

                journal,

                journal_lines

            )

            db.commit()

            db.refresh(journal)

            return journal

        except HTTPException:

            db.rollback()

            raise

        except Exception as e:

            db.rollback()

            raise HTTPException(

                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=f"Journal Entry Creation Failed : {str(e)}"

            )
            # =====================================================
    # Get Journal Entries
    # =====================================================

    @staticmethod
    def get_journal_entries(

        db: Session,

        search=None,

        voucher_type=None,

        page=1,

        page_size=20

    ):

        skip = (page - 1) * page_size

        return JournalEntryRepository.get_all(

            db=db,

            search=search,

            voucher_type=voucher_type,

            skip=skip,

            limit=page_size

        )
        # =====================================================
    # Get Journal Entry
    # =====================================================

    @staticmethod
    def get_journal_entry(

        db: Session,

        journal_id: int

    ):

        journal = JournalEntryRepository.get_by_id(

            db,

            journal_id

        )

        if not journal:

            raise HTTPException(

                status_code=404,

                detail="Journal Entry not found."

            )

        return journal
        # =====================================================
    # Update Journal Entry
    # =====================================================

    @staticmethod
    def update_journal_entry(

        db: Session,

        journal_id: int,

        data,

        current_user

    ):

        journal = JournalEntryRepository.get_by_id(

            db,

            journal_id

        )

        if not journal:

            raise HTTPException(

                status_code=404,

                detail="Journal Entry not found."

            )

        update_data = data.model_dump(

            exclude_unset=True

        )

        for key, value in update_data.items():

            setattr(

                journal,

                key,

                value

            )

        journal.updated_by = current_user.id

        JournalEntryRepository.update(

            db,

            journal

        )

        return journal
        # =====================================================
    # Delete Journal Entry
    # =====================================================

    @staticmethod
    def delete_journal_entry(

        db: Session,

        journal_id: int

    ):

        journal = JournalEntryRepository.get_by_id(

            db,

            journal_id

        )

        if not journal:

            raise HTTPException(

                status_code=404,

                detail="Journal Entry not found."

            )

        JournalEntryRepository.delete(

            db,

            journal

        )

        return {

            "success": True,

            "message": "Journal Entry deleted successfully."

        }
        # =====================================================
    # Dashboard
    # =====================================================

    @staticmethod
    def dashboard(
        db: Session
    ):

        return JournalEntryRepository.dashboard(db)