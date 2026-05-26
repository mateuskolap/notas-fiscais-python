from fastapi import FastAPI

from src.exceptions.handlers import register_exception_handlers
from src.middleware import RequestIdMiddleware
from src.routes.v1 import router as v1_router

app = FastAPI(
    title='Notas Fiscais API',
    version='0.1.0',
    prefix='/api',
)

app.add_middleware(RequestIdMiddleware)

app.include_router(v1_router)

register_exception_handlers(app)
