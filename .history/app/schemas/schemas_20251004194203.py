from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    """创建用户模型"""
    password: str


class UserUpdate(BaseModel):
    """更新用户模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    """数据库用户模型"""
    id: int
    hashed_password: str
    is_superuser: bool = False
    
    class Config:
        from_attributes = True


class User(UserBase):
    """用户响应模型"""
    id: int
    is_superuser: bool = False
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None


class UserProfileBase(BaseModel):
    """用户资料基础模型"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    """创建用户资料模型"""
    pass


class UserProfileUpdate(UserProfileBase):
    """更新用户资料模型"""
    pass


class UserProfile(UserProfileBase):
    """用户资料响应模型"""
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


class PostBase(BaseModel):
    """文章基础模型"""
    title: str
    content: str
    is_published: bool = False


class PostCreate(PostBase):
    """创建文章模型"""
    pass


class PostUpdate(BaseModel):
    """更新文章模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None


class Post(PostBase):
    """文章响应模型"""
    id: int
    author_id: int
    published_at: Optional[str] = None
    
    class Config:
        from_attributes = True