"""
序列化器定义
使用 fastapi-cbv 的 create_tortoise_serializer 自动生成序列化器
"""
from fastapi_cbv import create_tortoise_serializer
from app.models.models import (
    User, UserProfile,
    IntervalSchedule, CrontabSchedule, PeriodicTask, TaskResult
)


# 用户相关序列化器
UserSerializer = create_tortoise_serializer(User)
UserProfileSerializer = create_tortoise_serializer(UserProfile)

# Celery 定时任务相关序列化器
IntervalScheduleSerializer = create_tortoise_serializer(IntervalSchedule)
CrontabScheduleSerializer = create_tortoise_serializer(CrontabSchedule)
PeriodicTaskSerializer = create_tortoise_serializer(PeriodicTask)
TaskResultSerializer = create_tortoise_serializer(TaskResult)
