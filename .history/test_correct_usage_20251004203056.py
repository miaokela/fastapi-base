#!/usr/bin/env python3
"""
测试正确的 PyQueryBuilder 使用方式
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_correct_usage():
    """测试正确的使用方式"""
    
    try:
        from query_builder import PyQueryBuilder, builder
        
        # 使用正确的方式创建实例和设置路径
        qb = PyQueryBuilder()
        qb.sql_path = "./sql"
        print(f"✅ 设置 SQL 路径: {qb.sql_path}")
        
        # 加载所有模板
        qb.load_all_templates()
        print("✅ 加载模板成功")
        
        # 检查可用的模板
        templates = qb.get_template_keys()
        print(f"✅ 可用模板: {templates}")
        
        if templates:
            # 测试用户查询
            print("\n🔍 测试用户查询:")
            
            # 1. 按ID查询用户
            if "users.select_by_id" in templates:
                sql1 = qb.build("users.select_by_id", user_id=123)
                print(f"  用户ID查询: {sql1}")
            
            # 2. 查询活跃用户
            if "users.select_active" in templates:
                sql2 = qb.build("users.select_active", limit=10)
                print(f"  活跃用户查询: {sql2}")
            
            # 3. 按邮箱域名查询
            if "users.select_by_domain" in templates:
                sql3 = qb.build("users.select_by_domain", domain="gmail.com", limit=20)
                print(f"  域名查询: {sql3}")
            
            # 测试文章查询
            print("\n📝 测试文章查询:")
            
            # 4. 查询作者的文章
            if "posts.select_by_author" in templates:
                sql4 = qb.build("posts.select_by_author", author_id=456, is_published=True, limit=5)
                print(f"  作者文章查询: {sql4}")
            
            # 5. 最近文章
            if "posts.recent_posts" in templates:
                sql5 = qb.build("posts.recent_posts", days=7, limit=10)
                print(f"  最近文章查询: {sql5}")
            
            # 测试分析查询
            print("\n📊 测试分析查询:")
            
            # 6. 用户统计
            if "analytics.user_stats" in templates:
                sql6 = qb.build("analytics.user_stats", 
                               date_from="2024-01-01", 
                               date_to="2024-12-31", 
                               limit=50)
                print(f"  用户统计查询: {sql6}")
            
            # 7. 顶级作者
            if "analytics.top_authors" in templates:
                sql7 = qb.build("analytics.top_authors", days=30, min_posts=5, limit=10)
                print(f"  顶级作者查询: {sql7}")
            
            print("\n✅ 所有查询测试完成!")
        else:
            print("⚠️  没有找到任何模板")
            
            # 检查文件结构
            sql_path = Path("./sql")
            if sql_path.exists():
                print(f"SQL目录存在: {sql_path.absolute()}")
                yaml_files = list(sql_path.glob("*.yaml"))
                print(f"YAML文件: {[f.name for f in yaml_files]}")
                
                if yaml_files:
                    # 检查第一个YAML文件的内容
                    first_yaml = yaml_files[0]
                    with open(first_yaml, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"文件 {first_yaml.name} 内容预览:")
                        print(content[:200] + "..." if len(content) > 200 else content)
            else:
                print("SQL目录不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_builder_function():
    """使用 builder() 函数测试"""
    
    try:
        from query_builder import builder
        
        print("\n🔧 使用 builder() 函数测试:")
        
        # 使用 builder 函数创建实例
        qb = builder()
        qb.sql_path = "./sql"
        print(f"✅ 使用 builder() 创建实例并设置路径")
        
        # 加载模板
        qb.load_all_templates()
        templates = qb.get_template_keys()
        print(f"✅ 可用模板: {len(templates)} 个")
        
        if templates:
            # 测试一个简单的查询
            first_template = templates[0]
            print(f"测试模板: {first_template}")
            
            if "users.select_by_id" in templates:
                sql = qb.build("users.select_by_id", user_id=999)
                print(f"生成的SQL: {sql}")
            
        return True
        
    except Exception as e:
        print(f"❌ builder() 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wrapper_class():
    """测试包装类"""
    
    try:
        print("\n🎁 测试包装类:")
        
        from app.utils.query_builder import ComplexQueryBuilder
        
        # 创建包装类实例
        qb = ComplexQueryBuilder()
        print("✅ ComplexQueryBuilder 实例创建成功")
        
        # 检查模板
        templates = qb.query_builder.get_template_keys()
        print(f"✅ 可用模板: {len(templates)} 个")
        
        if templates:
            # 使用包装类的方法
            if "users.select_by_id" in templates:
                sql = qb.build_with_template("users.select_by_id", user_id=555)
                print(f"包装类生成的SQL: {sql}")
        
        return True
        
    except Exception as e:
        print(f"❌ 包装类测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 测试正确的 PyQueryBuilder 使用方式")
    print("=" * 70)
    
    # 测试基本用法
    test_correct_usage()
    
    # 测试 builder 函数
    test_with_builder_function()
    
    # 测试包装类
    test_wrapper_class()
    
    print("\n" + "="*70)
    print("🎉 测试完成!")
    print("="*70)