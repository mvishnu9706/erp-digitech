from sqlalchemy.orm import Session


class SalesPostingService:

    @staticmethod
    def post(
        db: Session,
        sales_invoice,
        current_user
    ):
        """
        Sales accounting posting is currently disabled.

        The previous implementation depended on the deleted:
        - JournalEntry
        - JournalEntryLine
        - ChartOfAccount
        - ChartOfAccountRepository
        - JournalEntryRepository
        - JournalNumberGenerator

        Therefore, no accounting journal is created here.

        Sales Invoice processing itself remains handled by
        SalesInvoiceService.
        """

        return None