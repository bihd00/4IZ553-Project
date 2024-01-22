from pydantic import Field
from datetime import datetime
from typing import Generic
from typing import TypeVar
from typing import Literal
from typing import Any
from be.schemas.base import Base


T = TypeVar('T')


class ErrorItem(Base):
    message: str
    type: str


class BaseResponseBody(Base):

    success: bool
    error: bool
    message: str | None = None
    errors: list[ErrorItem] | None = None
    data: Any | None = None
    timestamp: float = Field(
        default_factory=lambda: datetime.utcnow().timestamp() * 1000.0
    )


class ResponseBody(BaseResponseBody, Generic[T]):

    success: Literal[True] = True
    error: Literal[False] = False
    errors: Literal[None] = None
    data: T | None = None


class ErrorResponseBody(BaseResponseBody):

    success: Literal[False] = False
    error: Literal[True] = True
    data: None = None


class ValidationError(Base):
    """
    pydantic wrapper of fastapi.RequestValidationError.errors()
    """

    msg: str
    type: str
    loc: list[Any] | tuple[Any] | None = None
    input: str | int | float | list[Any] | dict[str, Any] | None = None
    url: str | None = None
    ctx: dict[str, Any] | None = None

    def to_error_item(self) -> ErrorItem:
        loc = [str(x) for x in self.loc] if self.loc else []
        loc_info = f'({".".join(loc)})' if loc else ''
        return ErrorItem(
            message=self.msg + ' ' + loc_info,
            type=self.type
        )
