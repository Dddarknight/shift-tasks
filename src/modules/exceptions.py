from typing import Any

from fastapi import HTTPException


class HTTPNotFoundError(HTTPException):

    def __init__(
        self,
        status_code: int = 404,
        detail: Any = "Not found",
    ):
        super().__init__(
            status_code=status_code, detail=detail)


class HTTPBadRequestError(HTTPException):

    def __init__(
        self,
        status_code: int = 400,
        detail: Any = "Bad request",
    ):
        super().__init__(
            status_code=status_code, detail=detail)
