from fastapi import FastAPI

from src.routes.v1 import router as v1_router

app = FastAPI(
    title='Notas Fiscais API',
    version='0.1.0',
    prefix='/api',
)

app.include_router(v1_router)
