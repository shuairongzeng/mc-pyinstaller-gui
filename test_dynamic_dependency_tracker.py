#!/usr/bin/env python3
"""
测试动态依赖追踪器
"""

import sys
import os
import time
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.dynamic_dependency_tracker import DynamicDependencyTracker

def create_complex_test_script():
    """创建复杂的测试脚本，包含各种动态导入模式"""
    test_script_content = '''#!/usr/bin/env python3
"""
复杂测试脚本 - 包含各种动态导入模式
"""

import os
import sys
import json

# 条件导入
if sys.platform == 'win32':
    try:
        import winsound
    except ImportError:
        winsound = None

# 可选导入
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# 延迟导入（函数内导入）
def process_data():
    import datetime
    from pathlib import Path
    
    if HAS_NUMPY:
        data = np.array([1, 2, 3])
        return data
    else:
        return [1, 2, 3]

def make_request():
    if HAS_REQUESTS:
        import urllib.parse
        return "可以发送请求"
    else:
        return "无法发送请求"

# 动态导入
def dynamic_import_test():
    # __import__ 方式
    json_module = __import__('json')
    
    # importlib 方式
    import importlib
    math_module = importlib.import_module('math')
    
    return json_module, math_module

# 字符串中的模块引用
REQUIRED_PACKAGES = ['PyQt5', 'matplotlib', 'pandas']
OPTIONAL_PACKAGES = ['scipy', 'sklearn']

def main():
    print("开始测试...")
    
    # 调用各种函数
    data = process_data()
    print(f"处理的数据: {data}")
    
    request_result = make_request()
    print(f"请求结果: {request_result}")
    
    json_mod, math_mod = dynamic_import_test()
    print(f"动态导入成功: {json_mod.__name__}, {math_mod.__name__}")
    
    print("测试完成!")

if __name__ == "__main__":
    main()
'''
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_script_content)
        return f.name

def test_static_analysis():
    """测试静态分析"""
    print("🔍 测试静态分析...")
    
    test_script = create_complex_test_script()
    print(f"  创建测试脚本: {test_script}")
    
    try:
        tracker = DynamicDependencyTracker()
        
        def progress_callback(message):
            print(f"    📝 {message}")
        
        # 只进行静态分析
        result = tracker.analyze_dynamic_dependencies(test_script, progress_callback, use_execution=False)
        
        print(f"\n📊 静态分析结果:")
        print(f"  分析方法: {result.analysis_method}")
        print(f"  运行时模块: {len(result.runtime_modules)} 个")
        for module in sorted(result.runtime_modules):
            print(f"    🔧 {module}")
        
        print(f"\n  条件模块: {len(result.conditional_modules)} 个")
        for module in sorted(result.conditional_modules):
            print(f"    ❓ {module}")
        
        print(f"\n  延迟导入: {len(result.lazy_imports)} 个")
        for module in sorted(result.lazy_imports):
            print(f"    ⏰ {module}")
        
        print(f"\n  可选模块: {len(result.optional_modules)} 个")
        for module in sorted(result.optional_modules):
            print(f"    🔄 {module}")
        
    finally:
        try:
            os.unlink(test_script)
        except:
            pass

def test_execution_analysis():
    """测试执行分析"""
    print("\n🚀 测试执行分析...")
    
    test_script = create_complex_test_script()
    print(f"  创建测试脚本: {test_script}")
    
    try:
        tracker = DynamicDependencyTracker(timeout=10)
        
        def progress_callback(message):
            print(f"    📝 {message}")
        
        # 进行混合分析（静态+执行）
        result = tracker.analyze_dynamic_dependencies(test_script, progress_callback, use_execution=True)
        
        print(f"\n📊 混合分析结果:")
        print(f"  分析方法: {result.analysis_method}")
        print(f"  执行成功: {'是' if result.execution_successful else '否'}")
        print(f"  执行时间: {result.execution_time:.2f}s")
        
        if result.execution_error:
            print(f"  执行错误: {result.execution_error}")
        
        print(f"\n  运行时模块: {len(result.runtime_modules)} 个")
        for module in sorted(result.runtime_modules):
            print(f"    ✅ {module}")
        
        print(f"\n  条件模块: {len(result.conditional_modules)} 个")
        for module in sorted(result.conditional_modules):
            print(f"    ❓ {module}")
        
        print(f"\n  延迟导入: {len(result.lazy_imports)} 个")
        for module in sorted(result.lazy_imports):
            print(f"    ⏰ {module}")
        
        print(f"\n  可选模块: {len(result.optional_modules)} 个")
        for module in sorted(result.optional_modules):
            print(f"    🔄 {module}")
        
        print(f"\n  错误模块: {len(result.error_modules)} 个")
        for module in sorted(result.error_modules):
            print(f"    ❌ {module}")
        
        if result.execution_output:
            print(f"\n  执行输出:")
            for line in result.execution_output.split('\n')[:10]:  # 只显示前10行
                if line.strip():
                    print(f"    {line}")
        
    finally:
        try:
            os.unlink(test_script)
        except:
            pass

def test_comprehensive_analysis():
    """测试综合分析"""
    print("\n🎯 测试综合分析...")
    
    test_script = create_complex_test_script()
    print(f"  创建测试脚本: {test_script}")
    
    try:
        tracker = DynamicDependencyTracker()
        
        def progress_callback(message):
            print(f"    📝 {message}")
        
        # 获取综合分析结果
        analysis = tracker.get_comprehensive_analysis(test_script, progress_callback)
        
        print(f"\n📈 综合分析统计:")
        print(f"  总模块数: {analysis['total_modules']}")
        print(f"  运行时模块: {analysis['runtime_modules']}")
        print(f"  条件模块: {analysis['conditional_modules']}")
        print(f"  延迟导入: {analysis['lazy_imports']}")
        print(f"  可选模块: {analysis['optional_modules']}")
        print(f"  错误模块: {analysis['error_modules']}")
        print(f"  执行成功: {'是' if analysis['execution_successful'] else '否'}")
        print(f"  分析方法: {analysis['analysis_method']}")
        
        print(f"\n💡 建议 ({len(analysis['recommendations'])} 条):")
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"  {i}. {rec}")
        
    finally:
        try:
            os.unlink(test_script)
        except:
            pass

def main():
    """主函数"""
    print("🚀 测试动态依赖追踪器")
    print("=" * 60)
    
    try:
        test_static_analysis()
        test_execution_analysis()
        test_comprehensive_analysis()
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
