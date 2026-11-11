from datetime import datetime


class SalesInvoiceNumberGenerator:

    """
    Generate Sales Invoice Number

    Format:
        INVYYYYMMDD-00001

    Example:
        INV20260707-00001
    """

    PREFIX = "INV"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{SalesInvoiceNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )