from celery import Celery
from config.settings import settings

# 创建Celery应用
celery_app = Celery(
    "fastapi-base",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["celery_app.tasks"]
)

# Celery配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区设置
    timezone="UTC",
    enable_utc=True,
    
    # 任务路由
    task_routes={
        "celery_app.tasks.user_tasks.*": {"queue": "user_queue"},
        "celery_app.tasks.email_tasks.*": {"queue": "email_queue"},
        "celery_app.tasks.general_tasks.*": {"queue": "general_queue"},
    },
    
    # 任务过期时间
    task_time_limit=300,  # 5分钟
    task_soft_time_limit=240,  # 4分钟
    
    # 定时任务配置
    beat_schedule={
        "test-periodic-task": {
            "task": "celery_app.tasks.general_tasks.test_periodic_task",
            "schedule": 60.0,  # 每60秒执行一次
        },
        "cleanup-expired-tokens": {
            "task": "celery_app.tasks.user_tasks.cleanup_expired_tokens",
            "schedule": 3600.0,  # 每小时执行一次
        },
    },
)

# 自动发现任务
celery_app.autodiscover_tasks(["celery_app.tasks"])