from datetime import datetime


class ServiceTicketNumberGenerator:

    """
    Generate Service Ticket Number

    Format:
        DISSRYYYYMMDD-00001

    Example:
        DISSR20260709-00001
    """

    PREFIX = "DISSR"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{ServiceTicketNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )