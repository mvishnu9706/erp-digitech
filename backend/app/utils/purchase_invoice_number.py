from datetime import datetime


class PurchaseInvoiceNumberGenerator:

    """
    Generate Purchase Invoice Number

    Format:
        PINVYYYYMMDD-00001

    Example:
        PINV20260707-00001
    """

    PREFIX = "PINV"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{PurchaseInvoiceNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )