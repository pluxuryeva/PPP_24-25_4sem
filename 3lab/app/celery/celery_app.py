from celery import Celery
from app.core.config import settings

# Настройка для использования fakeredis
if settings.use_fakeredis:
    import fakeredis
    
    # Monkey patch redis для Celery
    import redis
    redis.Redis = fakeredis.FakeRedis
    redis.StrictRedis = fakeredis.FakeStrictRedis

celery_app = Celery(
    "bruteforce",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.celery.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "app.celery.tasks.bruteforce_task": {"queue": "bruteforce"},
    }
) 