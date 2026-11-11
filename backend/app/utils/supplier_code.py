class SupplierCodeGenerator:

    @staticmethod
    def generate(last_id: int) -> str:
        """
        Generate supplier code.

        Format:
        DisSup + DD + MM + NUMBER

        Example:
        DisSup22080001
        DisSup22080002
        DisSup22080003
        """

        from datetime import datetime

        today = datetime.now()

        day = today.strftime("%d")

        month = today.strftime("%m")

        number = f"{last_id:04d}"

        return f"DisSup{day}{month}{number}"