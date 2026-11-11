from datetime import datetime


class DeliveryChallanNumberGenerator:

    """
    Generates Delivery Challan Numbers.

    Format:
        DCYYYYMMDD-00001

    Examples:
        DC20260707-00001
        DC20260707-00002
        DC20260707-00003
    """

    PREFIX = "DC"

    @staticmethod
    def generate(last_id: int) -> str:
        """
        Generate Delivery Challan Number.

        Args:
            last_id (int): Next sequence number.

        Returns:
            str: Delivery Challan Number.
        """

        today = datetime.now()

        return (
            f"{DeliveryChallanNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )