from typing import Sequence
from typing import Any
from be.schemas.base import Base


class PointNode(Base):
    lat: float
    lon: float


class Route(Base):
    route: Sequence[PointNode]


class AddressOption(Base):
    value: str
    score: float
    label: str
    id: int


class PointOfInterest(Base):
    latitude: float
    longitude: float
    name: str
    categories: Sequence[str]
    tags: dict[str, Any]