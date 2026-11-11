from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import json
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)

import traceback
import logging


logger = logging.getLogger(__name__)
# =====================================================
# Success/Error Response
# =====================================================

def error_response(

    message: str,

    status_code: int,

    errors=None

):

    return JSONResponse(

        status_code=status_code,

        content={

            "success": False,

            "message": message,

            "errors": errors,

            "data": None

        }

    )
# =====================================================
# Register Exception Handlers
# =====================================================

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException
    ):
        return error_response(
            message=exc.detail,
            status_code=exc.status_code
        )
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(

        request: Request,

        exc: RequestValidationError

    ):

        return error_response(
            message="Validation Error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=[
                {
                    "field": ".".join(map(str, err["loc"])),
                    "message": err["msg"]
                }
                for err in exc.errors()
            ]
        )
    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(

        request: Request,

        exc: IntegrityError

    ):

        logger.error(str(exc))

        return error_response(

            message="Database integrity error.",

            status_code=status.HTTP_400_BAD_REQUEST

        )
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(

        request: Request,

        exc: SQLAlchemyError

    ):

        logger.error(str(exc))

        return error_response(

            message="Database error.",

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR

        )
    @app.exception_handler(Exception)
    async def general_exception_handler(

        request: Request,

        exc: Exception

    ):

        logger.error(traceback.format_exc())

        return error_response(

            message="Internal Server Error.",

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR

        )