from pydantic import TypeAdapter
from fastapi import Request
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from be.schemas.http import ValidationError
from be.exc.api import APIError


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        content=exc.content.to_python(),
        status_code=exc.status_code,
        headers=exc.headers
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:

    errors = exc.errors()
    error_dicts = [err for err in errors if isinstance(err, dict)]

    ta = TypeAdapter(list[ValidationError])
    try:
        validation_errors = ta.validate_python(error_dicts)
        errors = [err.to_error_item() for err in validation_errors]
    except Exception as e:
        errors = []

    api_error = APIError(
        message='validation error',
        errors=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )

    return JSONResponse(
        content=api_error.content.to_python(),
        status_code=api_error.status_code,
        headers=api_error.headers
    )
