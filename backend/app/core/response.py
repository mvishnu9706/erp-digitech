from typing import Any, Optional

from fastapi.responses import JSONResponse


class ApiResponse:

    @staticmethod
    def success(

        data: Any = None,

        message: str = "Success",

        status_code: int = 200

    ):

        return JSONResponse(

            status_code=status_code,

            content={

                "success": True,

                "message": message,

                "data": data,

                "errors": None

            }

        )

    @staticmethod
    def error(

        message: str,

        status_code: int = 400,

        errors: Optional[Any] = None

    ):

        return JSONResponse(

            status_code=status_code,

            content={

                "success": False,

                "message": message,

                "data": None,

                "errors": errors

            }

        )