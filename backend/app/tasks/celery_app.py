from celery import Celery

from app.config import settings

celery = Celery(
    "fakenews",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    worker_concurrency=3,
    task_default_retry_delay=10,
    task_max_retries=3,
)

celery.autodiscover_tasks(["app.tasks"])
