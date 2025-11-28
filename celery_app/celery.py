from celery import Celery
from config.settings import settings

# 创建Celery应用
celery_app = Celery(
    "fastapi-base",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["celery_app.tasks.test_tasks"]
)

# Celery配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区设置
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务路由（使用默认 celery 队列）
    task_routes={
        "celery_app.tasks.test_tasks.*": {"queue": "celery"},
    },
    
    # 任务过期时间
    task_time_limit=300,  # 5分钟
    task_soft_time_limit=240,  # 4分钟
    
    # 使用数据库调度器（类似 django-celery-beat）
    # 启动 beat 时使用: celery -A celery_app.celery beat -S celery_app.scheduler:DatabaseScheduler
    beat_scheduler="celery_app.scheduler:DatabaseScheduler",
    
    # 默认定时任务配置（仅在不使用数据库调度器时生效）
    # 使用数据库调度器后，这些配置将被忽略，所有定时任务通过 Admin 管理
    beat_schedule={},
)

# 自动发现任务
celery_app.autodiscover_tasks(["celery_app.tasks"])