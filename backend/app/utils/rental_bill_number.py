from datetime import datetime


class RentalBillNumberGenerator:

    """
    Rental Bill Number Generator

    Format:
        RBYYYYMMDD-00001

    Example:
        RB20260711-00001
    """

    PREFIX = "RB"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{RentalBillNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )