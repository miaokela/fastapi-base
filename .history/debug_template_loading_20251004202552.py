#!/usr/bin/env python3
"""
测试 PyQueryBuilder 模板加载机制
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_template_loading():
    """测试模板加载"""
    
    try:
        from query_builder import PyQueryBuilder
        
        # 测试不同的模板目录配置
        template_dir = str(Path(__file__).parent / "app" / "sql_templates")
        print(f"模板目录: {template_dir}")
        
        # 检查目录中的文件
        template_path = Path(template_dir)
        if template_path.exists():
            files = list(template_path.glob("*"))
            print(f"目录中的文件: {[f.name for f in files]}")
        else:
            print("模板目录不存在")
            return False
        
        # 方法1: 通过构造函数传递
        print("\n方法1: 构造函数")
        try:
            qb1 = PyQueryBuilder()
            qb1.sql_path = template_dir
            print(f"设置 sql_path: {qb1.sql_path}")
            qb1.load_all_templates()
            keys1 = qb1.get_template_keys()
            print(f"加载的模板: {keys1}")
        except Exception as e:
            print(f"方法1失败: {e}")
        
        # 方法2: 直接测试build方法
        print("\n方法2: 直接调用build")
        try:
            qb2 = PyQueryBuilder()
            qb2.sql_path = template_dir
            # 尝试使用一个简单的上下文
            simple_context = {"test": "value"}
            result = qb2.build("user_stats", simple_context)
            print(f"Build结果: {result}")
        except Exception as e:
            print(f"方法2失败: {e}")
        
        # 方法3: 检查实际的模板文件格式
        print("\n方法3: 检查模板文件内容")
        user_stats_file = template_path / "user_stats.sql"
        if user_stats_file.exists():
            with open(user_stats_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"user_stats.sql 内容:")
                print(content[:200] + "..." if len(content) > 200 else content)
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 测试 PyQueryBuilder 模板加载机制")
    print("=" * 60)
    
    test_template_loading()
    
    print("\n" + "="*60)