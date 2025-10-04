"""
测试文章管理 API
"""
import pytest
from httpx import AsyncClient

from app.models.models import Post, User


class TestPostAPI:
    """文章管理 API 测试"""
    
    @pytest.mark.asyncio
    async def test_get_posts_list(self, client: AsyncClient, test_user, auth_headers):
        """测试获取文章列表"""
        response = await client.get("/api/v1/posts/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_create_post(self, client: AsyncClient, test_user, auth_headers):
        """测试创建文章"""
        response = await client.post(
            "/api/v1/posts/",
            headers=auth_headers,
            json={
                "title": "Test Post",
                "content": "This is a test post content",
                "author_id": test_user.id
            }
        )
        assert response.status_code in [200, 201]
        
        # 验证文章已创建
        post = await Post.get_or_none(title="Test Post")
        assert post is not None
        assert post.content == "This is a test post content"
    
    @pytest.mark.asyncio
    async def test_get_post_by_id(self, client: AsyncClient, test_user, auth_headers):
        """测试获取指定文章"""
        # 先创建一篇文章
        post = await Post.create(
            title="Get Test Post",
            content="Content for get test",
            author=test_user
        )
        
        response = await client.get(
            f"/api/v1/posts/{post.id}/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Get Test Post"
        assert data["content"] == "Content for get test"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_post(self, client: AsyncClient, auth_headers):
        """测试获取不存在的文章"""
        response = await client.get("/api/v1/posts/99999/", headers=auth_headers)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_post(self, client: AsyncClient, test_user, auth_headers):
        """测试更新文章"""
        # 创建文章
        post = await Post.create(
            title="Update Test",
            content="Original content",
            author=test_user
        )
        
        response = await client.put(
            f"/api/v1/posts/{post.id}/",
            headers=auth_headers,
            json={
                "title": "Updated Title",
                "content": "Updated content"
            }
        )
        assert response.status_code == 200
        
        # 验证更新
        updated_post = await Post.get(id=post.id)
        assert updated_post.title == "Updated Title"
        assert updated_post.content == "Updated content"
    
    @pytest.mark.asyncio
    async def test_partial_update_post(self, client: AsyncClient, test_user, auth_headers):
        """测试部分更新文章"""
        post = await Post.create(
            title="Partial Update Test",
            content="Original content",
            author=test_user
        )
        
        response = await client.patch(
            f"/api/v1/posts/{post.id}/",
            headers=auth_headers,
            json={
                "title": "Partially Updated Title"
            }
        )
        assert response.status_code == 200
        
        # 验证更新
        updated_post = await Post.get(id=post.id)
        assert updated_post.title == "Partially Updated Title"
        assert updated_post.content == "Original content"  # 未修改字段保持不变
    
    @pytest.mark.asyncio
    async def test_delete_post(self, client: AsyncClient, test_user, auth_headers):
        """测试删除文章"""
        post = await Post.create(
            title="Delete Test",
            content="Content to delete",
            author=test_user
        )
        
        response = await client.delete(
            f"/api/v1/posts/{post.id}/",
            headers=auth_headers
        )
        assert response.status_code in [200, 204]
        
        # 验证已删除
        deleted_post = await Post.get_or_none(id=post.id)
        assert deleted_post is None
    
    @pytest.mark.asyncio
    async def test_create_post_unauthorized(self, client: AsyncClient):
        """测试未认证创建文章"""
        response = await client.post(
            "/api/v1/posts/",
            json={
                "title": "Unauthorized Post",
                "content": "This should fail"
            }
        )
        assert response.status_code in [401, 403]
