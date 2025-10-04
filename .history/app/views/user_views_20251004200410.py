from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.utils.cbv import cbv
from tortoise.exceptions import DoesNotExist, IntegrityError
from datetime import datetime

from app.core.deps import get_current_active_user, get_current_superuser
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import User, UserProfile
from app.schemas.schemas import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    Token,
    UserProfile as UserProfileSchema,
    UserProfileCreate,
    UserProfileUpdate,
)


@cbv
class AuthViewSet:
    """认证视图集"""
    
    async def register(self, user_data: UserCreate) -> JSONResponse:
        """用户注册"""
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
                is_active=user_data.is_active,
            )
            
            # 创建用户资料
            await UserProfile.create(user=user)
            
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "User created successfully", "user_id": user.id}
            )
        
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username or email already exists"
            )
    
    async def login(self, username: str, password: str) -> Token:
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
    
    async def get_me(
        self, current_user: User = Depends(get_current_active_user)
    ) -> UserSchema:
        """获取当前用户信息"""
        return UserSchema.from_orm(current_user)


@cbv
class UserViewSet:
    """用户视图集"""
    
    async def create_user(
        self,
        user_data: UserCreate,
        current_user: User = Depends(get_current_superuser)
    ) -> UserSchema:
        """创建用户（管理员权限）"""
        try:
            hashed_password = get_password_hash(user_data.password)
            user = await User.create(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                is_active=user_data.is_active,
            )
            await UserProfile.create(user=user)
            return UserSchema.from_orm(user)
        
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username or email already exists"
            )
    
    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_superuser)
    ) -> List[UserSchema]:
        """获取用户列表（管理员权限）"""
        users = await User.all().offset(skip).limit(limit)
        return [UserSchema.from_orm(user) for user in users]
    
    async def get_user(
        self,
        user_id: int,
        current_user: User = Depends(get_current_superuser)
    ) -> UserSchema:
        """获取指定用户（管理员权限）"""
        try:
            user = await User.get(id=user_id)
            return UserSchema.from_orm(user)
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdate,
        current_user: User = Depends(get_current_superuser)
    ) -> UserSchema:
        """更新用户信息（管理员权限）"""
        try:
            user = await User.get(id=user_id)
            
            update_data = user_update.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
            await user.update_from_dict(update_data)
            await user.save()
            
            return UserSchema.from_orm(user)
        
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    async def delete_user(
        self,
        user_id: int,
        current_user: User = Depends(get_current_superuser)
    ) -> JSONResponse:
        """删除用户（管理员权限）"""
        try:
            user = await User.get(id=user_id)
            await user.delete()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "User deleted successfully"}
            )
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )


@cbv  
class UserProfileViewSet:
    """用户资料视图集"""
    
    async def get_profile(
        self,
        current_user: User = Depends(get_current_active_user)
    ) -> UserProfileSchema:
        """获取当前用户资料"""
        try:
            profile = await UserProfile.get(user=current_user)
            return UserProfileSchema.from_orm(profile)
        except DoesNotExist:
            # 如果资料不存在，创建一个
            profile = await UserProfile.create(user=current_user)
            return UserProfileSchema.from_orm(profile)
    
    async def update_profile(
        self,
        profile_update: UserProfileUpdate,
        current_user: User = Depends(get_current_active_user)
    ) -> UserProfileSchema:
        """更新当前用户资料"""
        try:
            profile = await UserProfile.get(user=current_user)
            update_data = profile_update.dict(exclude_unset=True)
            await profile.update_from_dict(update_data)
            await profile.save()
            return UserProfileSchema.from_orm(profile)
        except DoesNotExist:
            # 如果资料不存在，创建一个
            profile_data = profile_update.dict(exclude_unset=True)
            profile = await UserProfile.create(user=current_user, **profile_data)
            return UserProfileSchema.from_orm(profile)