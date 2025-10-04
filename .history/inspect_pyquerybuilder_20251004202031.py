#!/usr/bin/env python3
"""
检查 PyQueryBuilder 的实际 API
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def inspect_pyquerybuilder():
    """检查 PyQueryBuilder 的方法和属性"""
    
    try:
        from query_builder import PyQueryBuilder
        print("✅ PyQueryBuilder 导入成功")
        
        # 创建实例
        qb = PyQueryBuilder()
        print("✅ PyQueryBuilder 实例创建成功")
        
        # 检查所有方法和属性
        print("\n📋 PyQueryBuilder 可用的方法和属性:")
        methods = [attr for attr in dir(qb) if not attr.startswith('_')]
        for method in sorted(methods):
            attr = getattr(qb, method)
            if callable(attr):
                print(f"  🔧 方法: {method}()")
            else:
                print(f"  📝 属性: {method} = {attr}")
        
        # 检查文档字符串
        print(f"\n📖 PyQueryBuilder 文档:")
        print(qb.__doc__ or "无文档")
        
        # 尝试查看类信息
        print(f"\n🏷️  类信息:")
        print(f"  类名: {qb.__class__.__name__}")
        print(f"  模块: {qb.__class__.__module__}")
        print(f"  类型: {type(qb)}")
        
        # 检查是否有help信息
        try:
            help_info = help(qb)
            print(f"\n📚 Help信息: {help_info}")
        except:
            print("\n📚 无help信息")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_package_info():
    """检查包信息"""
    
    try:
        import query_builder
        print(f"✅ query_builder 包导入成功")
        print(f"  包路径: {query_builder.__file__}")
        
        # 检查包中的所有内容
        print("\n📦 query_builder 包内容:")
        for attr in sorted(dir(query_builder)):
            if not attr.startswith('_'):
                obj = getattr(query_builder, attr)
                if callable(obj):
                    print(f"  🔧 {attr}: {type(obj)}")
                else:
                    print(f"  📝 {attr}: {obj}")
        
        # 检查版本信息
        try:
            version = getattr(query_builder, '__version__', 'Unknown')
            print(f"\n🏷️  包版本: {version}")
        except:
            print("\n🏷️  无版本信息")
            
        return True
        
    except Exception as e:
        print(f"❌ 包检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 检查 query-builder-tool 的 PyQueryBuilder API")
    print("=" * 60)
    
    # 检查包信息
    print("1️⃣ 检查包信息")
    check_package_info()
    
    print("\n" + "="*60)
    print("2️⃣ 检查 PyQueryBuilder 类")
    inspect_pyquerybuilder()
    
    print("\n" + "="*60)