from celery import Celery

from src.settings import settings

celery_app = Celery(
    'notas_fiscais_worker',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=settings.APP_TIMEZONE,
    enable_utc=True,
)
