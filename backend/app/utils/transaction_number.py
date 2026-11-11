from datetime import datetime


class TransactionNumberGenerator:

    @staticmethod
    def generate():

        now = datetime.now()

        return (
            f"ST"
            f"{now.strftime('%Y%m%d%H%M%S%f')}"
        )