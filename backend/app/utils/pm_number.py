from datetime import datetime


class PMNumberGenerator:

    """
    Preventive Maintenance Number Generator

    Format:
        PMYYYYMMDD-00001

    Example:
        PM20260709-00001
    """

    PREFIX = "PM"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{PMNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )