from sqlalchemy.orm import Session


class PurchasePostingService:

    @staticmethod
    def post(
        db: Session,
        purchase_invoice,
        current_user
    ):
        """
        Purchase accounting posting is currently disabled.

        The previous implementation depended on:
        - ChartOfAccount
        - JournalEntry
        - JournalEntryLine
        - ChartOfAccountRepository
        - JournalEntryRepository
        - JournalNumberGenerator

        Those accounting modules have been removed from the project,
        so this service intentionally performs no journal posting.

        The purchase invoice itself is still handled by the
        Purchase Invoice service.
        """

        return None