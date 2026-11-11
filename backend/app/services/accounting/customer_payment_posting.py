from sqlalchemy.orm import Session


class CustomerPaymentPostingService:

    @staticmethod
    def post(
        db: Session,
        payment,
        current_user
    ):
        """
        Customer payment accounting posting is currently disabled.

        The previous implementation depended on the deleted:
        - JournalEntry
        - JournalEntryLine
        - ChartOfAccount
        - ChartOfAccountRepository
        - JournalEntryRepository
        - JournalNumberGenerator

        Customer payments themselves are still handled by
        CustomerPaymentService.
        """

        return None