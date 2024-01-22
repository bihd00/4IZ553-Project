from fastapi import FastAPI
from fastapi.openapi import utils as openapi_utils
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from be.config import settings
from be.exc.api import APIError
from be.schemas.http import ResponseBody
from be.schemas.http import ErrorResponseBody
from be.exc import handlers
from be.api.api_v1 import api


# 'patch' fastapi to use custom validation errors
openapi_utils.validation_error_response_definition = {
    "title": "HTTPValidationError",
    "$ref": openapi_utils.REF_PREFIX + APIError.model.__name__,  # type: ignore [attr-defined]
}

app = FastAPI(
    openapi_url=\
        f'{settings.API_V1_PREFIX}/openapi.json' \
        if settings.API_ALLOW_DOCS else None,
    docs_url='/docs' if settings.API_ALLOW_DOCS else None,
    redoc_url='/redoc' if settings.API_ALLOW_DOCS else None,
    title='api',
    exception_handlers={
        APIError: handlers.api_error_handler,
        RequestValidationError: handlers.validation_error_handler
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root() -> ResponseBody[None]:
    return ResponseBody(message='running')

@app.get('/err')
def err() -> ErrorResponseBody:
    raise APIError()

app.include_router(
    router=api.router,
    prefix=settings.API_V1_PREFIX
)