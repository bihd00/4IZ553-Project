from fastapi import HTTPException
from typing import Type
from be.schemas.http import ErrorResponseBody


class APIError(HTTPException):

    model: Type[ErrorResponseBody] = ErrorResponseBody

    def __init__(
        self,
        message: str | None = None,
        errors: list[str] | None = None,
        internal_errors: list[str] | None = None,
        status_code: int = 500,
        headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(status_code, None, headers)
        self.content = self.model(message=message, errors=errors)
        self.internal_errors = internal_errors
