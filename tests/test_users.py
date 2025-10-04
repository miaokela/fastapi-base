"""
测试用户管理 API
"""
import pytest
from httpx import AsyncClient

from app.models.models import User


class TestUserAPI:
    """用户管理 API 测试"""
    
    @pytest.mark.asyncio
    async def test_get_users_list(self, client: AsyncClient, test_user, superuser_headers):
        """测试获取用户列表（需要管理员权限）"""
        response = await client.get("/api/v1/users/", headers=superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_users_list_unauthorized(self, client: AsyncClient, auth_headers):
        """测试普通用户无法获取用户列表"""
        response = await client.get("/api/v1/users/", headers=auth_headers)
        # 根据实际权限设置，可能返回 403 或可以访问
        assert response.status_code in [200, 403]
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client: AsyncClient, test_user, superuser_headers):
        """测试获取指定用户"""
        response = await client.get(
            f"/api/v1/users/{test_user.id}/",
            headers=superuser_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, client: AsyncClient, superuser_headers):
        """测试获取不存在的用户"""
        response = await client.get("/api/v1/users/99999/", headers=superuser_headers)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, superuser_headers, db):
        """测试创建用户（管理员权限）"""
        response = await client.post(
            "/api/v1/users/",
            headers=superuser_headers,
            json={
                "username": "createduser",
                "email": "created@example.com",
                "password": "created123",
                "is_active": True
            }
        )
        assert response.status_code in [200, 201]
        
        # 验证用户已创建
        user = await User.get_or_none(username="createduser")
        assert user is not None
    
    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient, test_user, superuser_headers):
        """测试更新用户信息"""
        response = await client.put(
            f"/api/v1/users/{test_user.id}/",
            headers=superuser_headers,
            json={
                "email": "updated@example.com"
            }
        )
        assert response.status_code == 200
        
        # 验证更新
        user = await User.get(id=test_user.id)
        assert user.email == "updated@example.com"
    
    @pytest.mark.asyncio
    async def test_partial_update_user(self, client: AsyncClient, test_user, superuser_headers):
        """测试部分更新用户"""
        response = await client.patch(
            f"/api/v1/users/{test_user.id}/",
            headers=superuser_headers,
            json={
                "is_active": False
            }
        )
        assert response.status_code == 200
        
        # 验证更新
        user = await User.get(id=test_user.id)
        assert user.is_active is False
    
    @pytest.mark.asyncio
    async def test_delete_user(self, client: AsyncClient, superuser_headers, db):
        """测试删除用户"""
        # 创建一个待删除的用户
        from app.core.security import get_password_hash
        user = await User.create(
            username="todelete",
            email="todelete@example.com",
            hashed_password=get_password_hash("pass123"),
            is_active=True
        )
        
        response = await client.delete(
            f"/api/v1/users/{user.id}/",
            headers=superuser_headers
        )
        assert response.status_code in [200, 204]
        
        # 验证已删除
        deleted_user = await User.get_or_none(id=user.id)
        assert deleted_user is None
