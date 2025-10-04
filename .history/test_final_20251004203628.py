#!/usr/bin/env python3
"""
简单测试项目基础功能是否正常
"""

def test_basic_structure():
    """测试基础结构"""
    
    try:
        print("测试配置导入...")
        from config.settings import settings
        print("✓ 配置导入成功")
    except Exception as e:
        print(f"✗ 配置导入失败: {e}")
        return False
    
    try:
        print("测试模型导入...")
        from app.models.models import User, UserProfile
        print("✓ 模型导入成功")
    except Exception as e:
        print(f"✗ 模型导入失败: {e}")
        return False
    
    try:
        print("测试视图导入...")
        from app.views.user_views import AuthViewSet, UserViewSet
        print("✓ 视图导入成功")
    except Exception as e:
        print(f"✗ 视图导入失败: {e}")
        return False
    
    try:
        print("测试Redis客户端导入...")
        from app.utils.redis_client import redis_client
        print("✓ Redis客户端导入成功")
    except Exception as e:
        print(f"✗ Redis客户端导入失败: {e}")
        return False
    
    try:
        print("测试CBV工具导入...")
        from app.utils.cbv import class_based_view
        print("✓ CBV工具导入成功")
    except Exception as e:
        print(f"✗ CBV工具导入失败: {e}")
        return False
    
    print("\n🎉 所有基础组件导入正常!")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 FastAPI 项目基础测试")
    print("=" * 50)
    
    success = test_basic_structure()
    
    if success:
        print("\n✅ 项目结构完整，可以正常使用")
        print("📝 现在可以根据需要添加具体的业务逻辑")
        print("🔧 如需复杂查询功能，可以:")
        print("   - 直接使用 Tortoise ORM")
        print("   - 或者根据需要集成其他查询构建器")
    else:
        print("\n❌ 项目存在问题，需要修复")
        exit(1)