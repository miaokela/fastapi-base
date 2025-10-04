"""
用户相关视图
使用 fastapi-cbv 实现基于类的视图
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi_cbv import APIView, ModelViewSet, cbv, CBVRouter
from datetime import datetime

from app.core.deps import get_current_active_user, get_current_superuser
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import User, UserProfile, Post
from app.serializers import UserSerializer, UserProfileSerializer, PostSerializer
from app.schemas.schemas import (
    UserCreate,
    Token,
)


# 创建路由
router = CBVRouter()


@cbv(router)
class AuthViewSet(APIView):
    """认证视图集"""
    
    async def post(self, user_data: UserCreate = Body(...)):
        """用户注册 - POST /auth/register"""
        try:
            # 检查用户是否已存在
            existing_user = await User.get_or_none(username=user_data.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            
            existing_email = await User.get_or_none(email=user_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # 创建新用户
            hashed_password = get_password_hash(user_data.password)
            user = await User.create(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                is_active=getattr(user_data, 'is_active', True),
            )
            
            # 创建用户资料
            await UserProfile.create(user=user)
            
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "User created successfully", "user_id": user.id}
            )
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def get(self, current_user: User = Depends(get_current_active_user)):
        """获取当前用户信息 - GET /auth/me"""
        return await UserSerializer.from_tortoise_orm(current_user)


# 手动注册认证路由
router.add_api_route("/auth/register", AuthViewSet.post, methods=["POST"], summary="用户注册", tags=["认证"])
router.add_api_route("/auth/me", AuthViewSet.get, methods=["GET"], summary="获取当前用户信息", tags=["认证"])


# 单独的登录路由（不在 AuthViewSet 类中）
@router.post("/auth/login", summary="用户登录", tags=["认证"])
async def login(username: str = Body(...), password: str = Body(...)) -> Token:
    """用户登录"""
    user = await User.get_or_none(username=username)
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    await user.save()
    
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


class UserViewSet(ModelViewSet):
    """用户视图集 - 使用 ModelViewSet 自动生成 CRUD"""
    queryset = User.all()
    serializer_class = UserSerializer
    # 默认配置（无需重复定义）:
    # lookup_field = "id"
    # datetime_format = "%Y-%m-%d %H:%M:%S"


class UserProfileViewSet(ModelViewSet):
    """用户资料视图集 - 使用 ModelViewSet 自动生成 CRUD"""
    queryset = UserProfile.all()
    serializer_class = UserProfileSerializer
    # 使用默认配置


class PostViewSet(ModelViewSet):
    """文章视图集 - 使用 ModelViewSet 自动生成 CRUD"""
    queryset = Post.all()
    serializer_class = PostSerializer
    # 使用默认配置，支持过滤和搜索
    # filter_backends = [TortoiseFilterBackend, TortoiseSearchBackend]
    # search_fields = ['title', 'content']
    # ordering_fields = ['created_at', 'title']
    # ordering = ['-created_at']
