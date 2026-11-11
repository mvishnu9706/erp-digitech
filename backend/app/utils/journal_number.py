from datetime import datetime


class JournalNumberGenerator:

    """
    Generate Journal Voucher Number

    Format:
        JVYYYYMMDD-00001

    Example:
        JV20260707-00001
    """

    PREFIX = "JV"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{JournalNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )