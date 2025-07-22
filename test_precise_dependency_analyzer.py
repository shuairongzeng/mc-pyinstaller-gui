#!/usr/bin/env python3
"""
测试精准依赖分析器
"""

import sys
import os
import time
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.precise_dependency_analyzer import PreciseDependencyAnalyzer, EnvironmentAnalyzer, ModuleClassifier

def create_test_script():
    """创建测试脚本"""
    test_script_content = '''#!/usr/bin/env python3
"""
测试脚本 - 包含各种类型的导入
"""

# 标准库导入
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 第三方库导入
try:
    import PyQt5
    from PyQt5.QtWidgets import QApplication
except ImportError:
    pass

try:
    import requests
    import numpy as np
    import pandas as pd
except ImportError:
    pass

# 动态导入
module_name = "json"
json_module = __import__(module_name)

import importlib
math_module = importlib.import_module("math")

def main():
    print("Hello World!")
    
if __name__ == "__main__":
    main()
'''
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_script_content)
        return f.name

def test_environment_analyzer():
    """测试环境分析器"""
    print("🔧 测试环境分析器...")
    
    analyzer = EnvironmentAnalyzer()
    env_info = analyzer.get_environment_info()
    
    print(f"  Python版本: {env_info['python_version'][:20]}...")
    print(f"  Python可执行文件: {env_info['python_executable']}")
    print(f"  平台: {env_info['platform']}")
    print(f"  虚拟环境: {'是' if env_info['is_virtual_env'] else '否'}")
    print(f"  虚拟环境路径: {env_info['virtual_env_path']}")
    print(f"  已安装包数量: {len(env_info['installed_packages'])}")
    
    # 测试包可用性检查
    test_packages = ['PyQt5', 'numpy', 'requests', 'nonexistent_package']
    print("\n  包可用性检查:")
    for package in test_packages:
        is_available, version = analyzer.is_package_available(package)
        status = "✅" if is_available else "❌"
        print(f"    {status} {package}: {version if is_available else '不可用'}")

def test_module_classifier():
    """测试模块分类器"""
    print("\n🏷️  测试模块分类器...")
    
    env_analyzer = EnvironmentAnalyzer()
    classifier = ModuleClassifier(env_analyzer)
    
    test_modules = [
        'os',           # 标准库
        'sys',          # 标准库
        'PyQt5',        # 第三方库
        'numpy',        # 第三方库（可能不存在）
        'requests',     # 第三方库（可能不存在）
        'nonexistent'   # 不存在的模块
    ]
    
    for module in test_modules:
        classification, module_info = classifier.classify_module(module)
        status = "✅" if module_info.is_available else "❌"
        print(f"    {status} {module}: {classification} ({module_info.version})")

def test_precise_analyzer():
    """测试精准依赖分析器"""
    print("\n🎯 测试精准依赖分析器...")
    
    # 创建测试脚本
    test_script = create_test_script()
    print(f"  创建测试脚本: {test_script}")
    
    try:
        # 创建分析器
        analyzer = PreciseDependencyAnalyzer(cache_dir=".test_precise_cache")
        
        def progress_callback(message):
            print(f"    📝 {message}")
        
        # 执行分析
        start_time = time.time()
        result = analyzer.analyze_dependencies(test_script, progress_callback)
        analysis_time = time.time() - start_time
        
        print(f"\n📊 分析结果 (耗时: {analysis_time:.2f}s):")
        print(f"  标准库模块: {len(result.standard_modules)} 个")
        for module in sorted(result.standard_modules):
            print(f"    ✅ {module}")
        
        print(f"\n  第三方库模块: {len(result.third_party_modules)} 个")
        for module in sorted(result.third_party_modules):
            info = result.module_details[module]
            status = "✅" if info.is_available else "❌"
            print(f"    {status} {module} ({info.version})")
        
        print(f"\n  本地模块: {len(result.local_modules)} 个")
        for module in sorted(result.local_modules):
            print(f"    📁 {module}")
        
        print(f"\n  可用模块: {len(result.available_modules)} 个")
        print(f"  缺失模块: {len(result.missing_modules)} 个")
        
        if result.missing_modules:
            print("  缺失的模块:")
            for module in sorted(result.missing_modules):
                print(f"    ❌ {module}")
        
        print(f"\n💡 建议 ({len(result.recommendations)} 条):")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")
        
        if result.warnings:
            print(f"\n⚠️  警告 ({len(result.warnings)} 条):")
            for i, warning in enumerate(result.warnings, 1):
                print(f"  {i}. {warning}")
        
        print(f"\n🔧 PyInstaller建议:")
        if result.hidden_imports:
            print(f"  隐藏导入: {', '.join(result.hidden_imports)}")
        if result.collect_all:
            print(f"  收集全部: {', '.join(result.collect_all)}")
        if result.data_files:
            print(f"  数据文件: {len(result.data_files)} 个")
        
        # 测试缓存功能
        print(f"\n🔄 测试缓存功能...")
        cache_start = time.time()
        cached_result = analyzer.analyze_dependencies(test_script, progress_callback)
        cache_time = time.time() - cache_start
        
        print(f"  缓存检测耗时: {cache_time:.3f}s")
        print(f"  缓存命中: {'是' if cached_result.cache_hit else '否'}")
        if cached_result.cache_hit:
            performance_gain = ((analysis_time - cache_time) / analysis_time) * 100
            print(f"  性能提升: {performance_gain:.1f}%")
        
        # 显示统计信息
        stats = analyzer.get_stats()
        print(f"\n📈 统计信息:")
        print(f"  总分析次数: {stats['total_analyses']}")
        print(f"  缓存命中次数: {stats['cache_hits']}")
        print(f"  平均分析时间: {stats['avg_analysis_time']:.3f}s")
        
    finally:
        # 清理测试文件
        try:
            os.unlink(test_script)
            print(f"\n🧹 清理测试文件: {test_script}")
        except:
            pass
        
        # 清理缓存
        try:
            analyzer.clear_cache()
            print("🧹 清理测试缓存")
        except:
            pass

def main():
    """主函数"""
    print("🚀 测试精准依赖分析器")
    print("=" * 60)
    
    try:
        test_environment_analyzer()
        test_module_classifier()
        test_precise_analyzer()
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
