from typing import Any


class ResponseHandler:

    @staticmethod
    def success(
        message: str,
        data: Any = None
    ):
        return {
            "success": True,
            "message": message,
            "data": data
        }

    @staticmethod
    def error(
        message: str
    ):
        return {
            "success": False,
            "message": message
        }