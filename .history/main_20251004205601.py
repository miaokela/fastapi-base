from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.contrib.fastapi import register_tortoise
from contextlib import asynccontextmanager
import logging

from config.settings import settings
from config.database import DATABASE_CONFIG
from app.utils.redis_client import redis_client
from app.views.user_views import router as user_router, UserViewSet, UserProfileViewSet, PostViewSet
from fastapi_cbv import viewset_routes


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("FastAPI应用启动中...")
    
    # 连接Redis
    try:
        await redis_client.connect()
        logger.info("Redis连接成功")
    except Exception as e:
        logger.error(f"Redis连接失败: {e}")
    
    # 创建超级管理员账户
    try:
        await create_superuser()
    except Exception as e:
        logger.error(f"创建超级管理员失败: {e}")
    
    yield
    
    # 关闭时执行
    logger.info("FastAPI应用关闭中...")
    
    # 断开Redis连接
    try:
        await redis_client.disconnect()
        logger.info("Redis连接已断开")
    except Exception as e:
        logger.error(f"Redis断开连接失败: {e}")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    description="FastAPI基础项目，集成CBV、Celery、Redis、Tortoise ORM、JWT认证",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# 全局异常处理
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "请求数据验证失败",
            "details": exc.errors(),
            "status_code": 422
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "服务器内部错误",
            "status_code": 500
        }
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "debug": settings.DEBUG
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用 {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 注册路由
def register_routes():
    """注册所有路由"""
    
    # 认证路由
    auth_router = cbv(AuthViewSet).router
    auth_router.prefix = "/api/v1/auth"
    auth_router.tags = ["认证"]
    
    # 添加认证相关路由
    auth_router.add_api_route("/register", AuthViewSet().register, methods=["POST"], summary="用户注册")
    auth_router.add_api_route("/login", AuthViewSet().login, methods=["POST"], summary="用户登录")
    auth_router.add_api_route("/me", AuthViewSet().get_me, methods=["GET"], summary="获取当前用户信息")
    
    app.include_router(auth_router)
    
    # 用户管理路由
    user_router = cbv(UserViewSet).router
    user_router.prefix = "/api/v1/users"
    user_router.tags = ["用户管理"]
    
    user_router.add_api_route("/", UserViewSet().create_user, methods=["POST"], summary="创建用户")
    user_router.add_api_route("/", UserViewSet().get_users, methods=["GET"], summary="获取用户列表")
    user_router.add_api_route("/{user_id}", UserViewSet().get_user, methods=["GET"], summary="获取指定用户")
    user_router.add_api_route("/{user_id}", UserViewSet().update_user, methods=["PUT"], summary="更新用户")
    user_router.add_api_route("/{user_id}", UserViewSet().delete_user, methods=["DELETE"], summary="删除用户")
    
    app.include_router(user_router)
    
    # 用户资料路由
    profile_router = cbv(UserProfileViewSet).router
    profile_router.prefix = "/api/v1/profile"
    profile_router.tags = ["用户资料"]
    
    profile_router.add_api_route("/", UserProfileViewSet().get_profile, methods=["GET"], summary="获取当前用户资料")
    profile_router.add_api_route("/", UserProfileViewSet().update_profile, methods=["PUT"], summary="更新当前用户资料")
    
    app.include_router(profile_router)


# Celery任务路由
@app.post("/api/v1/tasks/send-email")
async def trigger_send_email(email: str, username: str):
    """触发发送邮件任务"""
    from celery_app.tasks.email_tasks import send_welcome_email
    
    task = send_welcome_email.delay(email, username)
    return {
        "message": "邮件发送任务已提交",
        "task_id": task.id,
        "status": "pending"
    }


@app.post("/api/v1/tasks/generate-report")
async def trigger_generate_report(report_type: str, filters: dict = None):
    """触发生成报告任务"""
    from celery_app.tasks.general_tasks import generate_report
    
    task = generate_report.delay(report_type, filters)
    return {
        "message": "报告生成任务已提交",
        "task_id": task.id,
        "status": "pending"
    }


@app.get("/api/v1/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """获取任务状态"""
    from celery_app.celery import celery_app
    
    task_result = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }


# Redis缓存示例路由
@app.get("/api/v1/cache/test")
async def test_cache():
    """测试Redis缓存"""
    key = "test_key"
    value = {"message": "Hello Redis!", "timestamp": "2024-01-01 12:00:00"}
    
    # 设置缓存
    await redis_client.set_value(key, value, expire=60)
    
    # 获取缓存
    cached_value = await redis_client.get_value(key)
    
    return {
        "cached_value": cached_value,
        "cache_exists": await redis_client.exists(key),
        "cache_ttl": await redis_client.get_ttl(key)
    }


# 复杂查询示例路由
@app.get("/api/v1/reports/user-stats")
async def get_user_stats():
    """获取用户统计报告"""
    try:
        # 这里可以添加实际的统计查询逻辑
        # 例如使用 Tortoise ORM
        stats = {
            "total_users": 0,
            "active_users": 0,
            "recent_registrations": 0,
            "message": "统计功能可用，需要实现具体的查询逻辑"
        }
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取用户统计失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def create_superuser():
    """创建超级管理员账户"""
    from app.models.models import User, UserProfile
    from app.core.security import get_password_hash
    
    # 检查是否已存在超级管理员
    existing_admin = await User.get_or_none(email=settings.ADMIN_EMAIL)
    if existing_admin:
        logger.info("超级管理员账户已存在")
        return
    
    # 创建超级管理员
    hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
    admin_user = await User.create(
        username="admin",
        email=settings.ADMIN_EMAIL,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=True
    )
    
    # 创建管理员资料
    await UserProfile.create(
        user=admin_user,
        first_name="系统",
        last_name="管理员"
    )
    
    logger.info(f"超级管理员账户创建成功: {settings.ADMIN_EMAIL}")


# 注册数据库
register_tortoise(
    app,
    config=DATABASE_CONFIG,
    generate_schemas=True,
    add_exception_handlers=True,
)

# 注册路由
register_routes()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )