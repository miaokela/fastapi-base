# 单元测试文档

## 📋 测试概览

本项目包含完整的单元测试套件，测试所有 API 端点的功能。

### 测试结构

```
tests/
├── __init__.py           # 测试配置
├── conftest.py           # Pytest fixtures
├── test_auth.py          # 认证 API 测试
├── test_users.py         # 用户管理 API 测试
├── test_profiles.py      # 用户资料 API 测试
├── test_posts.py         # 文章管理 API 测试
└── test_general.py       # 通用端点测试
```

## 🧪 测试覆盖

### 1. 认证 API (test_auth.py)

- ✅ `POST /auth/register` - 用户注册
  - 成功注册
  - 重复用户名
  - 重复邮箱
- ✅ `POST /auth/login` - 用户登录
  - 成功登录
  - 错误密码
  - 不存在的用户
- ✅ `GET /auth/me` - 获取当前用户信息
  - 认证用户获取信息
  - 未认证访问
  - 无效令牌

### 2. 用户管理 API (test_users.py)

- ✅ `GET /api/v1/users/` - 获取用户列表
- ✅ `POST /api/v1/users/` - 创建用户
- ✅ `GET /api/v1/users/{id}/` - 获取指定用户
- ✅ `PUT /api/v1/users/{id}/` - 更新用户
- ✅ `PATCH /api/v1/users/{id}/` - 部分更新用户
- ✅ `DELETE /api/v1/users/{id}/` - 删除用户

### 3. 用户资料 API (test_profiles.py)

- ✅ `GET /api/v1/profiles/` - 获取资料列表
- ✅ `POST /api/v1/profiles/` - 创建资料
- ✅ `GET /api/v1/profiles/{id}/` - 获取指定资料
- ✅ `PUT /api/v1/profiles/{id}/` - 更新资料
- ✅ `PATCH /api/v1/profiles/{id}/` - 部分更新资料
- ✅ `DELETE /api/v1/profiles/{id}/` - 删除资料

### 4. 文章管理 API (test_posts.py)

- ✅ `GET /api/v1/posts/` - 获取文章列表
- ✅ `POST /api/v1/posts/` - 创建文章
- ✅ `GET /api/v1/posts/{id}/` - 获取指定文章
- ✅ `PUT /api/v1/posts/{id}/` - 更新文章
- ✅ `PATCH /api/v1/posts/{id}/` - 部分更新文章
- ✅ `DELETE /api/v1/posts/{id}/` - 删除文章
- ✅ 未认证访问测试

### 5. 通用端点 (test_general.py)

- ✅ `GET /health` - 健康检查
- ✅ `GET /` - 根路径
- ✅ `GET /docs` - API 文档
- ✅ `GET /openapi.json` - OpenAPI Schema

## 🚀 运行测试

### 方法 1: 使用测试脚本

```bash
./run_tests.sh
```

### 方法 2: 直接使用 pytest

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_auth.py -v

# 运行特定测试类
pytest tests/test_auth.py::TestAuthAPI -v

# 运行特定测试方法
pytest tests/test_auth.py::TestAuthAPI::test_register_success -v

# 显示详细输出
pytest tests/ -vv

# 显示打印语句
pytest tests/ -v -s

# 仅运行失败的测试
pytest tests/ --lf

# 测试覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

## 📦 测试依赖

测试需要以下依赖包：

```toml
[project.optional-dependencies]
test = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.24.0",
]
```

安装测试依赖：

```bash
uv pip install pytest pytest-asyncio httpx
```

## 🔧 测试配置

### conftest.py

提供了以下 Fixtures：

- `event_loop` - 异步事件循环
- `db` - 测试数据库（内存 SQLite）
- `client` - 异步 HTTP 客户端
- `test_user` - 测试普通用户
- `test_superuser` - 测试超级管理员
- `auth_token` - 普通用户认证令牌
- `superuser_token` - 超级管理员令牌
- `auth_headers` - 认证请求头
- `superuser_headers` - 超级管理员请求头

### pytest.ini

配置了 pytest 的行为：

- 自动异步模式
- 测试路径: `tests/`
- 详细输出
- 简短的错误回溯

## 📝 编写新测试

### 测试模板

```python
import pytest
from httpx import AsyncClient

class TestMyAPI:
    """我的 API 测试"""
    
    @pytest.mark.asyncio
    async def test_my_endpoint(self, client: AsyncClient, auth_headers):
        """测试我的端点"""
        response = await client.get("/my-endpoint", headers=auth_headers)
        assert response.status_code == 200
        assert "expected_key" in response.json()
```

### 最佳实践

1. **使用描述性的测试名称**
   ```python
   async def test_user_can_login_with_valid_credentials(self, ...):
   ```

2. **遵循 AAA 模式** (Arrange, Act, Assert)
   ```python
   # Arrange - 准备测试数据
   user_data = {"username": "test", "password": "pass"}
   
   # Act - 执行操作
   response = await client.post("/login", json=user_data)
   
   # Assert - 验证结果
   assert response.status_code == 200
   ```

3. **测试边界情况**
   - 空值、None
   - 超长字符串
   - 无效数据类型
   - 权限不足

4. **独立性**
   - 每个测试应该独立运行
   - 不依赖其他测试的结果
   - 使用 fixtures 准备测试数据

## 🎯 测试覆盖率

查看测试覆盖率：

```bash
# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=term-missing

# 生成 HTML 报告
pytest tests/ --cov=app --cov-report=html
# 然后打开 htmlcov/index.html
```

## 🐛 调试测试

```bash
# 在失败时进入调试器
pytest tests/ --pdb

# 显示局部变量
pytest tests/ -l

# 完整的错误回溯
pytest tests/ --tb=long
```

## 📊 持续集成

测试可以集成到 CI/CD 流程中：

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      - name: Run tests
        run: ./run_tests.sh
```

## 📚 相关资源

- [Pytest 文档](https://docs.pytest.org/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
- [HTTPX 文档](https://www.python-httpx.org/)
- [FastAPI 测试文档](https://fastapi.tiangolo.com/tutorial/testing/)
