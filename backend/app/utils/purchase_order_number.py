from datetime import date


class PurchaseOrderNumberGenerator:

    @staticmethod
    def generate(
        purchase_date: date,
        sequence_number: int
    ):

        return (
            f"DISPO"
            f"{purchase_date.strftime('%d%m%Y')}"
            f"-{sequence_number:05d}"
        )