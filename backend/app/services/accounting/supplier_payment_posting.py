from sqlalchemy.orm import Session


class SupplierPaymentPostingService:

    @staticmethod
    def post(
        db: Session,
        payment,
        current_user
    ):
        """
        Supplier payment accounting posting is currently disabled.

        The previous implementation depended on the deleted:
        - JournalEntry
        - JournalEntryLine
        - ChartOfAccount
        - ChartOfAccountRepository
        - JournalEntryRepository
        - JournalNumberGenerator

        Supplier payments themselves remain handled by
        SupplierPaymentService.
        """

        return None