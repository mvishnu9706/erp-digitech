import logging
import time

from fastapi import Request
from starlette.responses import Response


# =====================================================
# Logger Configuration
# =====================================================

logger = logging.getLogger("digitech_erp")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =====================================================
# Request Logging Middleware
# =====================================================

async def log_requests(
    request: Request,
    call_next
):

    start_time = time.time()

    method = request.method

    path = request.url.path

    ip = request.client.host if request.client else "Unknown"

    user_agent = request.headers.get(
        "User-Agent",
        "Unknown"
    )

    try:

        response: Response = await call_next(request)

        process_time = round(

            (time.time() - start_time) * 1000,

            2

        )

        logger.info(

            f"{method} | "
            f"{path} | "
            f"{response.status_code} | "
            f"{process_time} ms | "
            f"IP={ip} | "
            f"UA={user_agent}"

        )

        response.headers["X-Process-Time"] = str(process_time)

        return response

    except Exception as e:

        process_time = round(

            (time.time() - start_time) * 1000,

            2

        )

        logger.exception(

            f"{method} | "
            f"{path} | "
            f"500 | "
            f"{process_time} ms | "
            f"IP={ip} | "
            f"{e}"

        )

        raise