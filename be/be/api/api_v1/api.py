from fastapi import APIRouter
from be.api.api_v1.endpoints import address
from be.api.api_v1.endpoints import poi


router = APIRouter()

router.include_router(
    router=address.router,
    prefix='/address',
    tags=['address'],
)

router.include_router(
    router=poi.router,
    prefix='/poi',
    tags=['poi'],
)