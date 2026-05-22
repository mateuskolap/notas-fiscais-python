from fastapi import APIRouter

from src.routes.v1.auth_routes import router as auth_router
from src.routes.v1.invoice_routes import router as invoice_router
from src.routes.v1.role_routes import router as role_router
from src.routes.v1.user_role_routes import router as user_role_router
from src.routes.v1.user_routes import router as user_router

router = APIRouter(prefix='/v1')

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(invoice_router)
router.include_router(role_router)
router.include_router(user_role_router)
