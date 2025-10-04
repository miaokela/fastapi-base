#!/usr/bin/env python3
"""
测试更新后的查询构建器功能
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_query_builder():
    """测试查询构建器功能"""
    
    print("🔍 测试 query-builder-tool 集成...")
    
    try:
        # 测试导入 PyQueryBuilder
        from query_builder import PyQueryBuilder
        print("✅ PyQueryBuilder 导入成功")
        
        # 测试基础查询构建
        qb = PyQueryBuilder()
        qb.select(["id", "username", "email"])
        qb.from_table("users")
        qb.where("is_active", "=", True)
        qb.order_by("created_at", "DESC")
        qb.limit(10)
        
        sql = qb.build()
        print(f"✅ 基础SQL构建成功: {sql}")
        
        # 测试复杂查询
        complex_qb = PyQueryBuilder()
        complex_qb.select(["u.username", "up.first_name", "up.last_name"])
        complex_qb.from_table("users u")
        complex_qb.left_join("user_profiles up", "u.id = up.user_id")
        complex_qb.where("u.is_active", "=", True)
        complex_qb.where_like("u.email", "%@gmail.com")
        complex_qb.order_by("u.created_at", "DESC")
        
        complex_sql = complex_qb.build()
        print(f"✅ 复杂SQL构建成功: {complex_sql}")
        
        # 测试模板功能
        template_dir = str(Path(__file__).parent / "app" / "sql_templates")
        template_qb = PyQueryBuilder(template_dir=template_dir)
        
        # 检查模板文件是否存在
        user_stats_template = Path(template_dir) / "user_stats.sql"
        if user_stats_template.exists():
            print(f"✅ 找到模板文件: {user_stats_template}")
            
            # 测试模板渲染
            context = {
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "limit": 5
            }
            
            try:
                template_sql = template_qb.build_with_template("user_stats", context)
                print(f"✅ 模板SQL构建成功: {template_sql}")
            except Exception as e:
                print(f"⚠️  模板渲染失败: {e}")
        else:
            print(f"⚠️  模板文件不存在: {user_stats_template}")
        
        print("\n📊 测试我们的包装类...")
        
        # 导入我们的包装类
        from app.utils.query_builder import ComplexQueryBuilder, UserQueryBuilder, PostQueryBuilder
        print("✅ 包装类导入成功")
        
        # 测试用户查询构建器
        user_qb = ComplexQueryBuilder()
        user_qb.from_table("users")
        user_qb.select(["id", "username", "email"])
        user_qb.where("is_active", "=", True)
        user_qb.order_by("created_at", "DESC")
        user_qb.limit(20)
        
        user_sql = user_qb.build()
        print(f"✅ 用户查询SQL: {user_sql}")
        
        # 测试复杂查询构建器的 join 功能
        complex_wrapper = ComplexQueryBuilder()
        complex_wrapper.from_table("users")
        complex_wrapper.select([
            "users.id", 
            "users.username", 
            "user_profiles.first_name"
        ])
        complex_wrapper.left_join("user_profiles", "users.id = user_profiles.user_id")
        complex_wrapper.where("users.is_active", "=", True)
        complex_wrapper.order_by("users.created_at", "DESC")
        complex_wrapper.limit(10)
        
        join_sql = complex_wrapper.build()
        print(f"✅ 关联查询SQL: {join_sql}")
        
        # 测试模板查询
        if user_stats_template.exists():
            template_context = {
                "date_from": "2024-01-01",
                "date_to": "2024-12-31", 
                "limit": 10
            }
            
            template_wrapper = ComplexQueryBuilder()
            template_sql = template_wrapper.build_with_template("user_stats", template_context)
            print(f"✅ 包装器模板SQL: {template_sql}")
        
        print("\n🎉 query-builder-tool 集成测试完成!")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保已安装 query-builder-tool: uv add query-builder-tool")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_import_only():
    """仅测试导入功能"""
    
    print("🔍 测试包导入...")
    
    try:
        # 测试 query-builder-tool 导入
        from query_builder import PyQueryBuilder
        print("✅ PyQueryBuilder 导入成功")
        
        # 创建基础实例
        qb = PyQueryBuilder()
        print("✅ PyQueryBuilder 实例创建成功")
        
        # 测试基础方法
        qb.select(["id", "name"])
        qb.from_table("test")
        sql = qb.build()
        print(f"✅ 基础SQL构建: {sql}")
        
        # 测试我们的包装器导入
        from app.utils.query_builder import ComplexQueryBuilder
        print("✅ ComplexQueryBuilder 导入成功")
        
        wrapper = ComplexQueryBuilder()
        print("✅ ComplexQueryBuilder 实例创建成功")
        
        print("\n🎉 所有导入测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 FastAPI 项目 query-builder-tool 集成测试")
    print("=" * 60)
    
    # 先测试导入
    if test_import_only():
        print("\n" + "="*60)
        print("🔬 运行完整功能测试")
        print("=" * 60)
        
        # 运行完整测试
        result = asyncio.run(test_query_builder())
        
        if result:
            print("\n🎊 所有测试通过! query-builder-tool 集成成功!")
        else:
            print("\n💥 部分测试失败，请检查配置")
    else:
        print("\n💥 基础导入测试失败")
    
    print("\n" + "="*60)