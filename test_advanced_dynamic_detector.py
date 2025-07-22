"""
测试高级动态模块检测器
"""

import os
import tempfile
from services.advanced_dynamic_detector import AdvancedDynamicDetector


def create_test_script() -> str:
    """创建测试脚本"""
    test_code = '''
import os
import sys
import json
from pathlib import Path

# 静态导入
import numpy as np
import pandas as pd

# 条件导入
if sys.platform == 'win32':
    import winsound
else:
    import termios

# 可选导入
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# 延迟导入
def load_data():
    import sqlite3
    import csv
    return sqlite3, csv

# 动态导入
def dynamic_import_example():
    # importlib 导入
    import importlib
    module_name = "datetime"
    datetime_module = importlib.import_module(module_name)
    
    # __import__ 导入
    requests = __import__("requests")
    
    # exec 中的导入
    exec("import random")
    
    # 字符串格式化导入
    module_to_import = "collections"
    exec(f"import {module_to_import}")

# 插件系统模拟
PLUGINS = {
    "handler": "custom_handler",
    "plugin": "my_plugin",
    "module": "extension_module"
}

def load_plugin(plugin_name):
    if plugin_name in PLUGINS:
        module_name = PLUGINS[plugin_name]
        return importlib.import_module(module_name)

# 配置驱动的导入
CONFIG = {
    "module": "yaml",
    "plugin": "custom_plugin",
    "handler": "file_handler"
}

# 字符串中的模块引用
module_list = ["pickle", "base64", "hashlib"]
for mod in module_list:
    globals()[mod] = __import__(mod)

# 高级动态导入
class ModuleLoader:
    def __init__(self):
        self.modules = {}
    
    def load_module(self, name):
        if name not in self.modules:
            self.modules[name] = importlib.import_module(name)
        return self.modules[name]

# 使用getattr的动态访问
def get_module_attr(module_name, attr_name):
    module = importlib.import_module(module_name)
    return getattr(module, attr_name)

if __name__ == "__main__":
    print("Testing dynamic imports...")
    dynamic_import_example()
    
    loader = ModuleLoader()
    time_module = loader.load_module("time")
    
    # 运行时发现的模块
    runtime_modules = ["threading", "multiprocessing"]
    for mod_name in runtime_modules:
        mod = __import__(mod_name)
        print(f"Loaded: {mod}")
'''
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        return f.name


def test_advanced_detector():
    """测试高级检测器"""
    print("🚀 开始测试高级动态模块检测器")
    print("=" * 50)
    
    # 创建测试脚本
    test_script = create_test_script()
    print(f"📝 创建测试脚本: {test_script}")
    
    try:
        # 创建检测器
        detector = AdvancedDynamicDetector(timeout=10)
        
        # 执行检测
        def output_callback(message):
            print(f"  📊 {message}")
        
        print("\n🔍 开始检测...")
        result = detector.detect_modules(test_script, output_callback, use_execution=True)
        
        print(f"\n⏱️  检测耗时: {result.execution_time:.2f}s")
        print(f"💾 缓存命中: {result.cache_hit}")
        
        # 显示检测结果
        print("\n📋 检测结果详情:")
        print("-" * 30)
        
        if result.static_imports:
            print(f"🔹 静态导入 ({len(result.static_imports)}): {sorted(result.static_imports)}")
        
        if result.dynamic_imports:
            print(f"🔹 动态导入 ({len(result.dynamic_imports)}): {sorted(result.dynamic_imports)}")
        
        if result.conditional_imports:
            print(f"🔹 条件导入 ({len(result.conditional_imports)}): {sorted(result.conditional_imports)}")
        
        if result.lazy_imports:
            print(f"🔹 延迟导入 ({len(result.lazy_imports)}): {sorted(result.lazy_imports)}")
        
        if result.optional_imports:
            print(f"🔹 可选导入 ({len(result.optional_imports)}): {sorted(result.optional_imports)}")
        
        if result.string_references:
            print(f"🔹 字符串引用 ({len(result.string_references)}): {sorted(result.string_references)}")
        
        if result.plugin_modules:
            print(f"🔹 插件模块 ({len(result.plugin_modules)}): {sorted(result.plugin_modules)}")
        
        if result.config_driven:
            print(f"🔹 配置驱动 ({len(result.config_driven)}): {sorted(result.config_driven)}")
        
        if result.runtime_discovered:
            print(f"🔹 运行时发现 ({len(result.runtime_discovered)}): {sorted(result.runtime_discovered)}")
        
        # 显示置信度分数
        print(f"\n📊 置信度分数 (前10个):")
        sorted_scores = sorted(result.confidence_scores.items(), key=lambda x: x[1], reverse=True)
        for module, score in sorted_scores[:10]:
            print(f"  {module}: {score:.2f}")
        
        # 获取所有模块和高置信度模块
        all_modules = detector.get_all_detected_modules(result)
        high_confidence = detector.get_high_confidence_modules(result, threshold=0.7)
        
        print(f"\n📈 统计信息:")
        print(f"  总检测模块数: {len(all_modules)}")
        print(f"  高置信度模块数: {len(high_confidence)}")
        print(f"  检测方法数: {len(result.detection_methods)}")
        
        # 显示检测方法详情
        print(f"\n🔧 检测方法详情:")
        for method, details in result.detection_methods.items():
            if 'error' in details:
                print(f"  ❌ {method}: {details['error']}")
            else:
                total_found = sum(len(modules) for modules in details.values() if isinstance(modules, set))
                print(f"  ✅ {method}: 发现 {total_found} 个模块")
        
        print(f"\n🎯 所有检测到的模块:")
        print(f"  {sorted(all_modules)}")
        
        print(f"\n⭐ 高置信度模块:")
        print(f"  {sorted(high_confidence)}")
        
        # 测试缓存功能
        print(f"\n🔄 测试缓存功能...")
        result2 = detector.detect_modules(test_script, output_callback, use_execution=False)
        print(f"  第二次检测缓存命中: {result2.cache_hit}")
        print(f"  第二次检测耗时: {result2.execution_time:.2f}s")
        
        print(f"\n✅ 测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        try:
            os.unlink(test_script)
            print(f"🗑️  清理测试文件: {test_script}")
        except:
            pass


def test_comparison_with_existing():
    """与现有检测器对比测试"""
    print("\n" + "=" * 50)
    print("🔄 与现有检测器对比测试")
    print("=" * 50)
    
    test_script = create_test_script()
    
    try:
        # 测试现有的检测器
        from services.dynamic_dependency_tracker import DynamicDependencyTracker
        from services.enhanced_module_detector import EnhancedModuleDetector
        
        print("📊 现有检测器结果:")
        
        # 动态依赖追踪器
        tracker = DynamicDependencyTracker(timeout=10)
        tracker_result = tracker.analyze_dynamic_dependencies(test_script, use_execution=True)
        
        all_tracker_modules = (tracker_result.runtime_modules | 
                              tracker_result.conditional_modules |
                              tracker_result.lazy_imports |
                              tracker_result.optional_modules)
        
        print(f"  DynamicDependencyTracker: {len(all_tracker_modules)} 个模块")
        
        # 增强模块检测器
        enhanced_detector = EnhancedModuleDetector()
        enhanced_result = enhanced_detector.detect_modules_with_cache(test_script)
        
        print(f"  EnhancedModuleDetector: {len(enhanced_result.detected_modules)} 个模块")
        
        # 新的高级检测器
        advanced_detector = AdvancedDynamicDetector(timeout=10)
        advanced_result = advanced_detector.detect_modules(test_script, use_execution=True)
        advanced_modules = advanced_detector.get_all_detected_modules(advanced_result)
        
        print(f"  AdvancedDynamicDetector: {len(advanced_modules)} 个模块")
        
        # 对比分析
        print(f"\n📈 对比分析:")
        print(f"  传统检测器总数: {len(all_tracker_modules)}")
        print(f"  增强检测器总数: {len(enhanced_result.detected_modules)}")
        print(f"  高级检测器总数: {len(advanced_modules)}")
        
        # 找出高级检测器独有的模块
        unique_to_advanced = advanced_modules - all_tracker_modules - enhanced_result.detected_modules
        if unique_to_advanced:
            print(f"  高级检测器独有: {sorted(unique_to_advanced)}")
        
        print(f"\n✅ 对比测试完成!")
        
    except Exception as e:
        print(f"❌ 对比测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            os.unlink(test_script)
        except:
            pass


if __name__ == "__main__":
    test_advanced_detector()
    test_comparison_with_existing()
