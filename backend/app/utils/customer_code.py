from datetime import datetime
import re


class CustomerCodeGenerator:

    @staticmethod
    def generate(last_code: str = None):

        # =========================================
        # Current creation date
        # Format: YYYYMMDD
        # Example: 20260811
        # =========================================

        today = datetime.now().strftime("%Y%m%d")


        # =========================================
        # First customer
        # =========================================

        if not last_code:
            return f"Dis{today}-00001"


        # =========================================
        # New format
        # Dis20260811-00005
        # =========================================

        match = re.match(
            r"^Dis\d{8}-(\d+)$",
            last_code
        )

        if match:

            last_number = int(
                match.group(1)
            )

            next_number = last_number + 1

            return (
                f"Dis{today}-{next_number:05d}"
            )


        # =========================================
        # Old format
        # Dis000005
        # =========================================

        match = re.match(
            r"^Dis(\d+)$",
            last_code
        )

        if match:

            last_number = int(
                match.group(1)
            )

            next_number = last_number + 1

            return (
                f"Dis{today}-{next_number:05d}"
            )


        # =========================================
        # Fallback
        # =========================================

        return f"Dis{today}-00001"