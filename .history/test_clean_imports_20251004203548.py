#!/usr/bin/env python3
"""
简单的导入测试
"""

def test_basic_imports():
    """测试基础导入"""
    
    try:
        print("测试 Tortoise 导入...")
        from tortoise.models import Model
        from tortoise import fields
        print("✓ Tortoise 基础组件导入成功")
    except Exception as e:
        print(f"✗ Tortoise 导入失败: {e}")
        return False
    
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
    
    print("\n🎉 所有基础导入测试通过!")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 基础导入测试")
    print("=" * 50)
    
    success = test_basic_imports()
    
    if success:
        print("\n✅ 项目基础组件导入正常")
    else:
        print("\n❌ 项目存在导入问题")
        exit(1)