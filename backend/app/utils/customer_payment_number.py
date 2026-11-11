from datetime import datetime


class CustomerPaymentNumberGenerator:

    """
    Generate Customer Payment Number

    Format:
        CPYYYYMMDD-00001

    Example:
        CP20260707-00001
    """

    PREFIX = "CP"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{CustomerPaymentNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )