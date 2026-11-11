from datetime import datetime


class MachineNumberGenerator:
    """
    Machine Number Generator

    Format:
        MCYYYYMMDD-00001

    Example:
        MC20260708-00001
    """

    PREFIX = "MC"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{MachineNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )