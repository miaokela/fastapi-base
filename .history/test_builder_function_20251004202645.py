#!/usr/bin/env python3
"""
测试 query_builder.builder 函数
"""

def test_builder_function():
    """测试 builder 函数"""
    
    try:
        from query_builder import builder
        
        print("✅ builder 函数导入成功")
        print(f"builder 类型: {type(builder)}")
        
        # 尝试调用 builder 函数
        try:
            result = builder()
            print(f"builder() 结果: {result}")
            print(f"结果类型: {type(result)}")
            
            # 检查返回结果的方法
            if hasattr(result, '__dict__'):
                print(f"结果属性: {result.__dict__}")
                
            print(f"结果方法: {[m for m in dir(result) if not m.startswith('_')]}")
            
        except Exception as e:
            print(f"builder() 调用失败: {e}")
        
        # 尝试带参数调用
        try:
            template_dir = "/Users/kela/Program/Other/Py/fastapi-base/app/sql_templates"
            result_with_path = builder(template_dir)
            print(f"builder(path) 结果: {result_with_path}")
        except Exception as e:
            print(f"builder(path) 失败: {e}")
            
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_builder_module():
    """测试整个模块"""
    
    try:
        import query_builder
        
        print("✅ query_builder 模块导入成功")
        
        # 检查模块的所有属性
        attrs = [attr for attr in dir(query_builder) if not attr.startswith('_')]
        print(f"模块属性: {attrs}")
        
        # 检查每个属性的类型
        for attr in attrs:
            obj = getattr(query_builder, attr)
            print(f"  {attr}: {type(obj)}")
            
            if callable(obj):
                try:
                    # 尝试调用
                    if attr == 'builder':
                        print(f"    尝试调用 {attr}()")
                        result = obj()
                        print(f"    结果: {type(result)}")
                except Exception as e:
                    print(f"    调用 {attr} 失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔬 测试 query_builder 模块和 builder 函数")
    print("=" * 60)
    
    print("1️⃣ 测试模块")
    test_query_builder_module()
    
    print("\n" + "="*60)
    print("2️⃣ 测试 builder 函数")
    test_builder_function()
    
    print("\n" + "="*60)