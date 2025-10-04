"""
序列化器定义
使用 fastapi-cbv 的 create_tortoise_serializer 自动生成序列化器
"""
from fastapi_cbv import create_tortoise_serializer
from app.models.models import User, UserProfile, Post


# 自动生成序列化器
UserSerializer = create_tortoise_serializer(User)
UserProfileSerializer = create_tortoise_serializer(UserProfile)
PostSerializer = create_tortoise_serializer(Post)
