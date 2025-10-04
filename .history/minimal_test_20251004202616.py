#!/usr/bin/env python3
"""
最简单的 PyQueryBuilder 测试
"""
import sys
from pathlib import Path

def minimal_test():
    """最简单的测试"""
    
    try:
        from query_builder import PyQueryBuilder
        
        # 创建简单实例
        qb = PyQueryBuilder()
        print(f"PyQueryBuilder 实例创建成功")
        print(f"sql_path 初始值: {qb.sql_path}")
        
        # 尝试不设置模板直接build
        try:
            simple_result = qb.build("test", {"name": "value"})
            print(f"直接build成功: {simple_result}")
        except Exception as e:
            print(f"直接build失败: {e}")
        
        # 尝试设置模板路径
        template_dir = str(Path(__file__).parent / "app" / "sql_templates")
        qb.sql_path = template_dir
        print(f"设置模板路径: {qb.sql_path}")
        
        # 尝试加载模板
        try:
            qb.load_all_templates()
            print("load_all_templates 调用成功")
        except Exception as e:
            print(f"load_all_templates 失败: {e}")
        
        # 检查加载的模板
        try:
            keys = qb.get_template_keys()
            print(f"模板键: {keys}")
        except Exception as e:
            print(f"get_template_keys 失败: {e}")
        
        # 检查是否有其他可用的方法
        print(f"\nPyQueryBuilder 的所有方法:")
        for attr in dir(qb):
            if not attr.startswith('_'):
                print(f"  {attr}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🧪 最简单的 PyQueryBuilder 测试")
    print("=" * 50)
    
    minimal_test()
    
    print("\n" + "="*50)