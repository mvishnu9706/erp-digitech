from datetime import datetime


class SupplierPaymentNumberGenerator:

    PREFIX = "SP"

    @staticmethod
    def generate(last_id: int) -> str:

        today = datetime.now()

        return (
            f"{SupplierPaymentNumberGenerator.PREFIX}"
            f"{today.strftime('%Y%m%d')}"
            f"-{last_id:05d}"
        )