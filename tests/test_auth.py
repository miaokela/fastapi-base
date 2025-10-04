"""
测试认证相关 API
"""
import pytest
from httpx import AsyncClient

from app.models.models import User


class TestAuthAPI:
    """认证 API 测试"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, db):
        """测试用户注册成功"""
        response = await client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpass123",
                "is_active": True
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"
        assert "user_id" in data
        
        # 验证用户已创建
        user = await User.get(username="newuser")
        assert user.email == "newuser@example.com"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """测试注册重复用户名"""
        response = await client.post(
            "/auth/register",
            json={
                "username": "testuser",  # 已存在
                "email": "another@example.com",
                "password": "pass123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """测试注册重复邮箱"""
        response = await client.post(
            "/auth/register",
            json={
                "username": "anotheruser",
                "email": "test@example.com",  # 已存在
                "password": "pass123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """测试登录成功"""
        response = await client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """测试登录错误密码"""
        response = await client.post(
            "/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpass"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient, db):
        """测试登录不存在的用户"""
        response = await client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": "pass123"
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_me_success(self, client: AsyncClient, test_user, auth_headers):
        """测试获取当前用户信息成功"""
        response = await client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_me_unauthorized(self, client: AsyncClient, db):
        """测试未认证获取用户信息"""
        response = await client.get("/auth/me")
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client: AsyncClient, db):
        """测试无效令牌"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code in [401, 403]
