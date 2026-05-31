from celery import Celery
from celery.schedules import crontab

from src.settings import settings

celery_app = Celery(
    'notas_fiscais_worker',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['src.tasks.product_normalization_task'],
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=settings.APP_TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_send_task_events=True,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    'normalize-pending-products': {
        'task': 'normalize_pending_products',
        'schedule': crontab(minute='*/5'),
    },
    'match-pending-items': {
        'task': 'match_pending_items',
        'schedule': crontab(minute='*/2'),
    },
}
