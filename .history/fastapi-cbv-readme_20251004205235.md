# FastAPI CBV (Class-Based Views)

基于 FastAPI 的类视图第三方插件，完全参考 Django REST Framework 的设计理念，提供异步支持和 Tortoise ORM 集成。

## 特性

- 🚀 **完全异步**: 基于 FastAPI 和 async/await，支持高性能异步操作
- 🏗️ **Django REST Framework 风格**: 熟悉的 APIView、GenericAPIView、ViewSet 等概念
- 🔧 **Mixin 支持**: 可组合的 CreateModelMixin、ListModelMixin 等
- 🗄️ **Tortoise ORM 集成**: 深度集成 Tortoise ORM，自动序列化
- 📊 **自动分页**: 内置分页支持
- 🔍 **过滤和搜索**: 支持查询过滤和全文搜索
- 📝 **自动文档**: 完全兼容 FastAPI 的自动 API 文档生成
- 🎯 **类型安全**: 完整的类型注解支持

## 安装

```bash
pip install fastapi-cbv
```

## 快速开始

### 1. 基础 APIView

```python
from fastapi import FastAPI
from fastapi_cbv import APIView, cbv, CBVRouter

app = FastAPI()
router = CBVRouter()

@cbv(router)
class HelloView(APIView):
    async def get(self):
        return {"message": "Hello World"}
    
    async def post(self):
        data = await self.request.json()
        return {"received": data}

HelloView.add_api_route("/hello")
app.include_router(router)
```

### 2. 模型 CRUD 操作

```python
from tortoise.models import Model
from tortoise import fields
from fastapi_cbv import (
    ListCreateAPIView, 
    RetrieveUpdateDestroyAPIView,
    create_tortoise_serializer
)

# 定义模型
class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=100, unique=True)

# 自动生成序列化器
UserSerializer = create_tortoise_serializer(User)

# 列表和创建视图
class UserListView(ListCreateAPIView):
    queryset = User.all()
    serializer_class = UserSerializer

# 详情、更新和删除视图
class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.all()
    serializer_class = UserSerializer

# 注册路由
router.add_cbv_route("/users", UserListView)
router.add_cbv_route("/users/{id}", UserDetailView)
```

### 3. ViewSet 用法

```python
from fastapi_cbv import ModelViewSet, viewset_routes

class UserViewSet(ModelViewSet):
    queryset = User.all()
    serializer_class = UserSerializer
    filter_backends = [TortoiseFilterBackend]
    search_fields = ['name', 'email']
    ordering_fields = ['id', 'name']

# 自动生成所有 CRUD 路由
viewset_routes(router, UserViewSet, prefix="/users")
```

这将自动创建以下路由：
- `GET /users/` - 列表
- `POST /users/` - 创建
- `GET /users/{id}/` - 详情
- `PUT /users/{id}/` - 更新
- `PATCH /users/{id}/` - 部分更新
- `DELETE /users/{id}/` - 删除

## 高级特性

### Mixin 组合

```python
from fastapi_cbv import GenericAPIView, CreateModelMixin, ListModelMixin

class CustomView(CreateModelMixin, ListModelMixin, GenericAPIView):
    queryset = User.all()
    serializer_class = UserSerializer
    
    async def get(self, **kwargs):
        # 自定义列表逻辑
        return await self.list(**kwargs)
    
    async def post(self, **kwargs):
        # 自定义创建逻辑
        result = await self.create(**kwargs)
        # 添加额外逻辑
        return result
```

### 依赖注入

```python
from fastapi import Depends

async def get_current_user():
    return {"user_id": 1, "username": "testuser"}

@cbv(router)
class ProtectedView(APIView):
    async def get(self, current_user: dict = Depends(get_current_user)):
        return {"message": f"Hello {current_user['username']}!"}

ProtectedView.add_api_route("/protected", dependencies=[Depends(get_current_user)])
```

### 过滤和搜索

```python
class PostViewSet(ModelViewSet):
    queryset = Post.all()
    serializer_class = PostSerializer
    filter_backends = [TortoiseFilterBackend, TortoiseSearchBackend]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
```

支持的查询参数：
- `?search=keyword` - 全文搜索
- `?ordering=created_at` - 排序
- `?title__icontains=hello` - 字段过滤
- `?page=1&page_size=20` - 分页

### 默认配置

FastAPI-CBV 提供了开箱即用的默认配置，无需重复定义：

```python
class UserDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    # 以下配置已经是默认值，无需重复定义：
    # lookup_field = "id"                    # 默认使用 id 字段
    # datetime_format = "%Y-%m-%d %H:%M:%S"  # 默认日期时间格式
    # date_format = "%Y-%m-%d"               # 默认日期格式
```

**默认配置项：**
- `lookup_field = "id"` - 详情/更新/删除操作的查找字段
- `datetime_format = "%Y-%m-%d %H:%M:%S"` - DateTime 序列化格式（如：2025-10-04 15:30:45）
- `date_format = "%Y-%m-%d"` - Date 序列化格式（如：2025-10-04）

**自定义覆盖：**
```python
class CustomView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    lookup_field = "username"  # 使用 username 代替 id
    datetime_format = "%d/%m/%Y %H:%M"  # 欧洲格式
```

查看 `examples/DEFAULT_CONFIG_GUIDE.md` 了解详细配置说明。

## 项目结构

```
fastapi-cbv/
├── fastapi_cbv/
│   ├── __init__.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── base.py          # APIView, GenericAPIView
│   │   ├── mixins.py        # CreateModelMixin, ListModelMixin 等
│   │   ├── generics.py      # ListCreateAPIView 等
│   │   └── viewsets.py      # ModelViewSet, ReadOnlyModelViewSet
│   ├── decorators.py        # @cbv 装饰器
│   ├── routers.py           # CBVRouter
│   └── tortoise_integration.py  # Tortoise ORM 集成
├── examples/
│   ├── basic_usage.py
│   └── complete_example.py
├── tests/
└── README.md
```

## 与 Django REST Framework 对比

| Django REST Framework | FastAPI CBV |
|----------------------|-------------|
| `APIView` | `APIView` |
| `GenericAPIView` | `GenericAPIView` |
| `ListCreateAPIView` | `ListCreateAPIView` |
| `RetrieveUpdateDestroyAPIView` | `RetrieveUpdateDestroyAPIView` |
| `ModelViewSet` | `ModelViewSet` |
| `@api_view` | `@cbv` |
| `serializers.ModelSerializer` | `create_tortoise_serializer()` |

## 完整示例

查看 `examples/complete_example.py` 了解完整的使用示例，包括：
- 模型定义
- 自动序列化器生成
- 各种类型的视图
- 路由注册
- 依赖注入
- 过滤和分页

## 贡献

欢迎贡献代码！请查看贡献指南了解详情。

## 许可证

MIT License

