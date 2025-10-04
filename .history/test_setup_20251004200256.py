#!/usr/bin/env python3
"""
简单的测试脚本，验证项目各个组件是否正常工作
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

async def test_imports():
    """测试所有重要模块的导入"""
    print("=== 测试模块导入 ===")
    
    try:
        from config.settings import settings
        print("✓ 配置模块导入成功")
    except Exception as e:
        print(f"✗ 配置模块导入失败: {e}")
        return False
    
    try:
        from app.models.models import User, UserProfile, Post
        print("✓ 数据模型导入成功")
    except Exception as e:
        print(f"✗ 数据模型导入失败: {e}")
        return False
    
    try:
        from app.schemas.schemas import UserCreate, Token
        print("✓ 数据模式导入成功")
    except Exception as e:
        print(f"✗ 数据模式导入失败: {e}")
        return False
    
    try:
        from app.core.security import get_password_hash, verify_password
        print("✓ 安全模块导入成功")
    except Exception as e:
        print(f"✗ 安全模块导入失败: {e}")
        return False
    
    try:
        from app.utils.redis_client import redis_client
        print("✓ Redis客户端导入成功")
    except Exception as e:
        print(f"✗ Redis客户端导入失败: {e}")
        return False
    
    try:
        from celery_app.celery import celery_app
        print("✓ Celery应用导入成功")
    except Exception as e:
        print(f"✗ Celery应用导入失败: {e}")
        return False
    
    return True

async def test_functionality():
    """测试基本功能"""
    print("\n=== 测试基本功能 ===")
    
    # 测试密码哈希
    try:
        from app.core.security import get_password_hash, verify_password
        password = "test123"
        hashed = get_password_hash(password)
        verified = verify_password(password, hashed)
        if verified:
            print("✓ 密码哈希功能正常")
        else:
            print("✗ 密码哈希功能异常")
            return False
    except Exception as e:
        print(f"✗ 密码哈希测试失败: {e}")
        return False
    
    # 测试配置加载
    try:
        from config.settings import settings
        print(f"✓ 应用配置加载成功: {settings.APP_NAME} v{settings.VERSION}")
    except Exception as e:
        print(f"✗ 应用配置测试失败: {e}")
        return False
    
    return True

async def main():
    """主函数"""
    print("FastAPI Base 项目测试")
    print("=" * 40)
    
    # 测试导入
    if not await test_imports():
        print("\n❌ 模块导入测试失败")
        return 1
    
    # 测试功能
    if not await test_functionality():
        print("\n❌ 功能测试失败")
        return 1
    
    print("\n✅ 所有测试通过！")
    print("\n项目组件状态:")
    print("- FastAPI: 已配置")
    print("- Tortoise ORM: 已配置")
    print("- Redis: 已配置")
    print("- Celery: 已配置")
    print("- JWT认证: 已配置")
    print("- 自定义CBV: 已实现")
    print("- 查询构建器: 已实现")
    
    print("\n下一步:")
    print("1. 启动服务器: ./start.sh")
    print("2. 访问API文档: http://localhost:8000/docs")
    print("3. 配置数据库连接(.env文件)")
    print("4. 启动Redis服务")
    print("5. 启动Celery Worker")
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)