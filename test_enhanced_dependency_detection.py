#!/usr/bin/env python3
"""
测试增强的依赖检测功能
"""

import sys
import os
import time
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_module_detector import EnhancedModuleDetector
from services.dependency_analyzer import DependencyAnalyzer
from config.framework_templates import FrameworkTemplates

def create_comprehensive_test_script():
    """创建一个包含多种依赖的综合测试脚本"""
    test_script_content = '''#!/usr/bin/env python3
"""
综合测试脚本 - 包含多种常见依赖和框架
"""

# 科学计算库
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

# 机器学习库
try:
    import sklearn
    from sklearn.model_selection import train_test_split
except ImportError:
    pass

try:
    import tensorflow as tf
except ImportError:
    pass

# 计算机视觉
try:
    import cv2
except ImportError:
    pass

# 图像处理
try:
    from PIL import Image, ImageDraw
except ImportError:
    pass

# Web框架
try:
    from flask import Flask, request, jsonify
    app = Flask(__name__)
except ImportError:
    pass

try:
    import django
    from django.conf import settings
except ImportError:
    pass

# GUI框架
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtCore import QThread, pyqtSignal
except ImportError:
    pass

try:
    import tkinter as tk
    from tkinter import messagebox, filedialog
except ImportError:
    pass

# 网络和HTTP
import requests
import urllib.request
import json

# 系统和文件操作
import os
import sys
import pathlib
import shutil
import subprocess
import configparser

# 动态导入示例
import importlib
import importlib.util

def dynamic_import_example():
    """动态导入示例"""
    # 使用importlib动态导入
    math_module = importlib.import_module('math')
    
    # 使用__import__动态导入
    datetime_module = __import__('datetime')
    
    # 字符串形式的导入（在实际代码中不推荐）
    exec("import random")

def main():
    """主函数"""
    print("综合测试脚本运行中...")
    
    # numpy操作
    arr = np.array([1, 2, 3, 4, 5])
    print(f"NumPy数组: {arr}")
    
    # pandas操作
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    print(f"Pandas DataFrame:\\n{df}")
    
    # matplotlib操作
    plt.figure(figsize=(8, 6))
    plt.plot([1, 2, 3], [4, 5, 6])
    plt.title("测试图表")
    plt.savefig("test_plot.png")
    plt.close()
    
    # requests操作
    try:
        response = requests.get("https://httpbin.org/get", timeout=5)
        print(f"HTTP请求状态: {response.status_code}")
    except Exception as e:
        print(f"HTTP请求失败: {e}")
    
    # 配置文件操作
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'debug': 'True', 'log_level': 'INFO'}
    
    with open('test_config.ini', 'w') as f:
        config.write(f)
    
    print("所有模块测试完成")

if __name__ == "__main__":
    main()
'''
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_script_content)
        return f.name

def test_enhanced_detection():
    """测试增强的模块检测功能"""
    print("🚀 测试增强的智能依赖检测功能")
    print("=" * 80)
    
    # 创建测试脚本
    test_script = create_comprehensive_test_script()
    print(f"✅ 创建综合测试脚本: {test_script}")
    
    try:
        # 创建增强的模块检测器
        print(f"\n🔧 初始化增强模块检测器...")
        detector = EnhancedModuleDetector(cache_dir=".test_cache", max_workers=4)
        
        # 定义输出回调函数
        def output_callback(message):
            print(f"  📝 {message}")
        
        # 执行检测
        print(f"\n🔍 开始智能模块检测...")
        start_time = time.time()
        
        result = detector.detect_modules_with_cache(test_script, output_callback)
        
        detection_time = time.time() - start_time
        print(f"\n⏱️  检测完成，总耗时: {detection_time:.2f}s")
        
        # 显示检测结果
        print(f"\n📊 检测结果统计:")
        print(f"  - 检测到的模块: {len(result.detected_modules)}")
        print(f"  - 缺失的模块: {len(result.missing_modules)}")
        print(f"  - 冲突的模块: {len(result.conflicted_modules)}")
        print(f"  - 推荐的隐藏导入: {len(result.hidden_imports)}")
        print(f"  - 推荐的collect-all: {len(result.collect_all)}")
        print(f"  - 框架配置: {len(result.framework_configs)}")
        print(f"  - 缓存命中: {'是' if result.cache_hit else '否'}")
        
        # 显示检测到的模块
        if result.detected_modules:
            print(f"\n📦 检测到的模块 ({len(result.detected_modules)} 个):")
            for module in sorted(result.detected_modules):
                print(f"  - {module}")
        
        # 显示缺失的模块
        if result.missing_modules:
            print(f"\n❌ 缺失的模块 ({len(result.missing_modules)} 个):")
            for module in sorted(result.missing_modules):
                print(f"  - {module}")
        
        # 显示冲突的模块
        if result.conflicted_modules:
            print(f"\n⚠️  冲突的模块 ({len(result.conflicted_modules)} 个):")
            for module in sorted(result.conflicted_modules):
                print(f"  - {module}")
        
        # 显示框架配置
        if result.framework_configs:
            print(f"\n🎯 检测到的框架 ({len(result.framework_configs)} 个):")
            for framework, config in result.framework_configs.items():
                print(f"  - {framework}: {config.get('name', framework)}")
        
        # 显示推荐的collect-all参数
        if result.collect_all:
            print(f"\n📦 推荐的collect-all参数 ({len(result.collect_all)} 个):")
            for module in result.collect_all:
                print(f"  - --collect-all={module}")
        
        # 显示建议
        if result.recommendations:
            print(f"\n💡 优化建议 ({len(result.recommendations)} 条):")
            for i, recommendation in enumerate(result.recommendations, 1):
                print(f"  {i}. {recommendation}")
        
        # 测试缓存功能
        print(f"\n🔄 测试缓存功能...")
        cache_start_time = time.time()
        cached_result = detector.detect_modules_with_cache(test_script, output_callback)
        cache_time = time.time() - cache_start_time
        
        print(f"  缓存检测耗时: {cache_time:.3f}s")
        print(f"  缓存命中: {'是' if cached_result.cache_hit else '否'}")
        print(f"  性能提升: {((detection_time - cache_time) / detection_time * 100):.1f}%")
        
        # 显示缓存统计
        cache_stats = detector.get_cache_stats()
        print(f"\n📈 缓存统计信息:")
        print(f"  - 内存缓存数量: {cache_stats['memory_cache_count']}")
        print(f"  - 磁盘缓存数量: {cache_stats['disk_cache_count']}")
        print(f"  - 总检测次数: {cache_stats['total_detections']}")
        print(f"  - 缓存命中次数: {cache_stats['cache_hits']}")
        print(f"  - 缓存命中率: {cache_stats['cache_hit_rate']:.1%}")
        print(f"  - 平均检测时间: {cache_stats['avg_detection_time']:.3f}s")
        
        if cache_stats['framework_matches']:
            print(f"  - 框架匹配统计:")
            for framework, count in cache_stats['framework_matches'].items():
                print(f"    * {framework}: {count} 次")
        
        # 测试依赖分析器
        print(f"\n🔬 测试依赖分析器...")
        analyzer = DependencyAnalyzer()
        dep_analysis = analyzer.analyze_dependencies(result.detected_modules)
        
        print(f"  - 分析的依赖: {len(dep_analysis['dependencies'])}")
        print(f"  - 发现的冲突: {len(dep_analysis['conflicts'])}")
        print(f"  - 版本问题: {len(dep_analysis['version_issues'])}")
        print(f"  - 分析建议: {len(dep_analysis['recommendations'])}")
        
        if dep_analysis['conflicts']:
            print(f"\n⚠️  依赖冲突:")
            for conflict in dep_analysis['conflicts']:
                print(f"  - {conflict.module1} vs {conflict.module2}: {conflict.description}")
                print(f"    解决方案: {conflict.resolution}")
        
        if dep_analysis['recommendations']:
            print(f"\n💡 依赖分析建议:")
            for i, rec in enumerate(dep_analysis['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # 生成PyInstaller参数
        print(f"\n🚀 生成PyInstaller参数...")
        pyinstaller_args = detector.generate_pyinstaller_args(test_script, output_callback)
        
        print(f"  生成了 {len(pyinstaller_args)} 个参数")
        
        # 按类型分组显示参数
        hidden_imports = [arg for arg in pyinstaller_args if arg.startswith("--hidden-import=")]
        collect_alls = [arg for arg in pyinstaller_args if arg.startswith("--collect-all=")]
        collect_data = [arg for arg in pyinstaller_args if arg.startswith("--collect-data=")]
        add_data = [arg for arg in pyinstaller_args if arg.startswith("--add-data=")]
        
        if hidden_imports:
            print(f"\n🔒 隐藏导入参数 ({len(hidden_imports)} 个):")
            for arg in hidden_imports[:5]:  # 只显示前5个
                print(f"  {arg}")
            if len(hidden_imports) > 5:
                print(f"  ... 还有 {len(hidden_imports) - 5} 个")
        
        if collect_alls:
            print(f"\n📦 Collect-all参数 ({len(collect_alls)} 个):")
            for arg in collect_alls:
                print(f"  {arg}")
        
        if collect_data:
            print(f"\n📄 Collect-data参数 ({len(collect_data)} 个):")
            for arg in collect_data:
                print(f"  {arg}")
        
        if add_data:
            print(f"\n📁 Add-data参数 ({len(add_data)} 个):")
            for arg in add_data:
                print(f"  {arg}")
        
        print(f"\n✅ 增强依赖检测测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_script):
                os.remove(test_script)
                print(f"🧹 清理测试文件: {test_script}")
            
            # 清理生成的文件
            for file in ['test_plot.png', 'test_config.ini']:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"🧹 清理生成文件: {file}")
            
            # 清理测试缓存
            import shutil
            if os.path.exists('.test_cache'):
                shutil.rmtree('.test_cache')
                print(f"🧹 清理测试缓存目录")
                
        except Exception as e:
            print(f"⚠️  清理文件时出错: {e}")

def test_framework_templates():
    """测试框架模板功能"""
    print(f"\n🎯 测试框架模板功能")
    print("-" * 40)
    
    templates = FrameworkTemplates.get_all_templates()
    print(f"加载了 {len(templates)} 个框架模板:")
    
    for name, template in templates.items():
        print(f"  - {name}: {template.get('description', 'No description')}")
        print(f"    指示器: {len(template.get('indicators', []))} 个")
        print(f"    隐藏导入: {len(template.get('hidden_imports', []))} 个")
        print(f"    建议: {len(template.get('recommendations', []))} 条")

if __name__ == "__main__":
    test_enhanced_detection()
    test_framework_templates()
