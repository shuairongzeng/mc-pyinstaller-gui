#!/usr/bin/env python3
"""
简单的线程测试
"""

import sys
import os
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_analysis():
    """测试简单的分析功能"""
    print("🧪 测试简单的精准依赖分析")
    print("=" * 40)
    
    # 创建测试脚本
    test_script_content = '''
import os
import sys
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_script_content)
        test_script = f.name
    
    try:
        # 直接测试精准分析器
        from services.precise_dependency_analyzer import PreciseDependencyAnalyzer
        
        analyzer = PreciseDependencyAnalyzer()
        
        def progress_callback(message):
            print(f"  📝 {message}")
        
        print("🚀 开始分析...")
        result = analyzer.analyze_dependencies(test_script, progress_callback)
        
        print(f"✅ 分析完成!")
        print(f"  标准库模块: {len(result.standard_modules)}")
        print(f"  第三方库模块: {len(result.third_party_modules)}")
        print(f"  本地模块: {len(result.local_modules)}")
        print(f"  分析时间: {result.analysis_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            os.unlink(test_script)
        except:
            pass

def main():
    """主函数"""
    success = test_simple_analysis()
    
    if success:
        print("\n✅ 简单分析测试成功!")
        print("现在可以测试实际应用程序了")
    else:
        print("\n❌ 简单分析测试失败")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
