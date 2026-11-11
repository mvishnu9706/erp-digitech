from datetime import date
import re


class SalesOrderNumberGenerator:

    PREFIX = "DISSO"

    @staticmethod
    def generate(last_so_number: str | None = None) -> str:

        today = date.today().strftime("%Y%m%d")

        # =====================================================
        # First Sales Order
        # =====================================================

        if not last_so_number:
            next_number = 1

        else:

            # Expected format:
            # DISSO20260811-00001

            pattern = (
                rf"^{SalesOrderNumberGenerator.PREFIX}"
                rf"\d{{8}}-(\d+)$"
            )

            match = re.match(
                pattern,
                last_so_number
            )

            if match:

                last_number = int(
                    match.group(1)
                )

                next_number = last_number + 1

            else:

                next_number = 1

        # =====================================================
        # Final Sales Order Number
        # =====================================================

        return (
            f"{SalesOrderNumberGenerator.PREFIX}"
            f"{today}-"
            f"{next_number:05d}"
        )