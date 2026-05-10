from fastapi import APIRouter

from src.routes.v1.auth_routes import router as auth_router
from src.routes.v1.user_routes import router as user_router
from src.routes.v1.nfce_routes import router as nfce_router

router = APIRouter(prefix='/v1')

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(nfce_router)