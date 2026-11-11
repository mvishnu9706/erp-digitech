from datetime import datetime


class GRNNumberGenerator:

    @staticmethod
    def generate(last_id: int):

        today = datetime.now()

        return (
            f"GRN"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )