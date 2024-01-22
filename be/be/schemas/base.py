from pydantic import BaseModel
from typing import Self
from typing import Any


class Base(BaseModel):

    @classmethod
    def from_python(cls, record: Any) -> Self:
        return cls.model_validate(record)

    @classmethod
    def from_json(cls, record: str | bytes) -> Self:
        return cls.model_validate_json(record)

    def to_python(self) -> dict[str, Any]:
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json()

    # dict-like indexing
    def __getitem__(cls, item: Any) -> Any:
        return getattr(cls, item)
