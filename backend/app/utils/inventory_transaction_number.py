from datetime import datetime


class InventoryTransactionNumberGenerator:

    """
    Inventory Transaction Number

    Format:
        ITYYYYMMDD-00001

    Example:
        IT20260709-00001
    """

    PREFIX = "IT"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{InventoryTransactionNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )