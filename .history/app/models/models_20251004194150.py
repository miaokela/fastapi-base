from datetime import datetime
from tortoise.models import Model
from tortoise import fields


class TimestampMixin:
    """时间戳混入类"""
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")


class User(Model, TimestampMixin):
    """用户模型"""
    
    id = fields.IntField(pk=True, description="用户ID")
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    email = fields.CharField(max_length=100, unique=True, description="邮箱")
    hashed_password = fields.CharField(max_length=255, description="密码哈希")
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_superuser = fields.BooleanField(default=False, description="是否为超级管理员")
    last_login = fields.DatetimeField(null=True, description="最后登录时间")
    
    class Meta:
        table = "users"
        table_description = "用户表"
    
    def __str__(self):
        return self.username


class UserProfile(Model, TimestampMixin):
    """用户资料模型"""
    
    id = fields.IntField(pk=True, description="资料ID")
    user = fields.OneToOneField("models.User", related_name="profile", description="用户")
    first_name = fields.CharField(max_length=50, null=True, description="名")
    last_name = fields.CharField(max_length=50, null=True, description="姓")
    phone = fields.CharField(max_length=20, null=True, description="电话")
    avatar = fields.CharField(max_length=255, null=True, description="头像URL")
    bio = fields.TextField(null=True, description="个人简介")
    
    class Meta:
        table = "user_profiles"
        table_description = "用户资料表"


class Post(Model, TimestampMixin):
    """文章模型"""
    
    id = fields.IntField(pk=True, description="文章ID")
    title = fields.CharField(max_length=200, description="标题")
    content = fields.TextField(description="内容")
    author = fields.ForeignKeyField("models.User", related_name="posts", description="作者")
    is_published = fields.BooleanField(default=False, description="是否发布")
    published_at = fields.DatetimeField(null=True, description="发布时间")
    
    class Meta:
        table = "posts"
        table_description = "文章表"
    
    def __str__(self):
        return self.title