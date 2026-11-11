from datetime import datetime


class AMCContractNumberGenerator:

    """
    Generate AMC Contract Number

    Format:
        AMCYYYYMMDD-00001

    Example:
        AMC20260709-00001
    """

    PREFIX = "AMC"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{AMCContractNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )