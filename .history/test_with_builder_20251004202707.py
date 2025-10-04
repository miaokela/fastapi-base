#!/usr/bin/env python3
"""
使用 builder() 函数测试 PyQueryBuilder
"""

def test_with_builder():
    """使用 builder() 函数测试"""
    
    try:
        from query_builder import builder
        
        # 使用 builder 创建实例
        qb = builder()
        print("✅ 使用 builder() 创建 PyQueryBuilder 实例成功")
        
        # 设置模板路径
        template_dir = "/Users/kela/Program/Other/Py/fastapi-base/app/sql_templates"
        qb.sql_path = template_dir
        print(f"✅ 设置模板路径: {qb.sql_path}")
        
        # 加载模板
        qb.load_all_templates()
        print("✅ 调用 load_all_templates 成功")
        
        # 检查模板键
        keys = qb.get_template_keys()
        print(f"✅ 可用模板: {keys}")
        
        if keys:
            # 尝试使用第一个模板
            template_name = keys[0]
            context = {"test": "value"}
            
            try:
                result = qb.build(template_name, context)
                print(f"✅ 使用模板 '{template_name}' 构建成功:")
                print(f"   {result}")
            except Exception as e:
                print(f"⚠️  使用模板失败: {e}")
        else:
            print("⚠️  没有找到可用的模板")
            
            # 让我们检查模板文件是否存在
            from pathlib import Path
            template_path = Path(template_dir)
            if template_path.exists():
                files = list(template_path.glob("*.sql"))
                print(f"目录中的SQL文件: {[f.name for f in files]}")
                
                # 尝试手动检查文件内容
                if files:
                    first_file = files[0]
                    with open(first_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"文件 {first_file.name} 的内容预览:")
                        print(content[:100] + "..." if len(content) > 100 else content)
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 使用 builder() 函数测试 PyQueryBuilder")
    print("=" * 60)
    
    test_with_builder()
    
    print("\n" + "="*60)