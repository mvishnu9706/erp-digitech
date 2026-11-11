from datetime import datetime


class ServiceVisitNumberGenerator:

    """
    Generate Service Visit Number

    Format:
        SVYYYYMMDD-00001

    Example:
        SV20260709-00001
    """

    PREFIX = "SV"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{ServiceVisitNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )