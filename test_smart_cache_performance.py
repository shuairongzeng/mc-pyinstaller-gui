#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能缓存系统性能测试脚本
测试缓存系统的性能提升和功能正确性
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.smart_cache_manager import SmartCacheManager, get_cache_manager, set_cache_manager
from services.optimized_module_detector import OptimizedModuleDetector
from services.optimized_dependency_analyzer import OptimizedDependencyAnalyzer

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CachePerformanceTester:
    """缓存性能测试器"""
    
    def __init__(self):
        self.temp_dir = None
        self.test_scripts = []
        self.results = {}
    
    def setup(self):
        """设置测试环境"""
        logger.info("设置测试环境...")
        
        # 创建临时目录
        self.temp_dir = Path(tempfile.mkdtemp(prefix="cache_test_"))
        logger.info(f"临时目录: {self.temp_dir}")
        
        # 创建测试脚本
        self._create_test_scripts()
        
        # 设置独立的缓存管理器
        cache_manager = SmartCacheManager(
            cache_dir=self.temp_dir / "cache",
            memory_max_size=100,
            memory_max_mb=50,
            disk_max_mb=100,
            default_ttl=3600
        )
        set_cache_manager(cache_manager)
        
        logger.info("测试环境设置完成")
    
    def teardown(self):
        """清理测试环境"""
        logger.info("清理测试环境...")
        
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        
        logger.info("测试环境清理完成")
    
    def _create_test_scripts(self):
        """创建测试脚本"""
        test_scripts_content = {
            "simple_script.py": """
import os
import sys
import json
import time
from pathlib import Path

def main():
    print("Hello, World!")
    data = {"message": "test"}
    print(json.dumps(data))

if __name__ == "__main__":
    main()
""",
            "complex_script.py": """
import os
import sys
import json
import time
import datetime
import pathlib
import collections
import itertools
import functools
import operator
import math
import random
import string
import urllib.request
import http.client
import socket
import threading
import multiprocessing
import subprocess
import logging
import argparse
import configparser
import sqlite3
import csv
import xml.etree.ElementTree
import html
import email
import base64
import hashlib
import hmac
import pickle
import shelve
import gzip
import zipfile
import tarfile
import shutil
import tempfile
import glob
import fnmatch

def main():
    print("Complex script with many imports")
    
    # 使用一些导入的模块
    now = datetime.datetime.now()
    path = pathlib.Path(".")
    data = collections.defaultdict(list)
    
    print(f"Current time: {now}")
    print(f"Current path: {path}")
    print(f"Data: {data}")

if __name__ == "__main__":
    main()
""",
            "framework_script.py": """
# 模拟使用多个框架的脚本
import os
import sys

# Web框架
try:
    import flask
    from flask import Flask, request, jsonify
except ImportError:
    pass

try:
    import django
    from django.conf import settings
except ImportError:
    pass

# 数据处理
try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError:
    pass

# 机器学习
try:
    import sklearn
    from sklearn.model_selection import train_test_split
except ImportError:
    pass

try:
    import tensorflow as tf
except ImportError:
    pass

# GUI
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
except ImportError:
    pass

def main():
    print("Framework script")

if __name__ == "__main__":
    main()
"""
        }
        
        for filename, content in test_scripts_content.items():
            script_path = self.temp_dir / filename
            script_path.write_text(content, encoding='utf-8')
            self.test_scripts.append(script_path)
            logger.info(f"创建测试脚本: {filename}")
    
    def test_cache_basic_functionality(self):
        """测试缓存基本功能"""
        logger.info("测试缓存基本功能...")
        
        cache_manager = get_cache_manager()
        
        # 测试设置和获取
        test_data = {"test": "data", "number": 42, "list": [1, 2, 3]}
        cache_manager.set("test_key", test_data, ttl=60)
        
        retrieved_data = cache_manager.get("test_key")
        assert retrieved_data == test_data, "缓存数据不匹配"
        
        # 测试不存在的键
        non_existent = cache_manager.get("non_existent_key", "default")
        assert non_existent == "default", "默认值不正确"
        
        # 测试删除
        cache_manager.delete("test_key")
        deleted_data = cache_manager.get("test_key")
        assert deleted_data is None, "删除后仍能获取数据"
        
        logger.info("✅ 缓存基本功能测试通过")
        return True
    
    def test_module_detection_performance(self):
        """测试模块检测性能"""
        logger.info("测试模块检测性能...")
        
        detector = OptimizedModuleDetector(
            use_ast=True,
            use_dynamic_analysis=True,
            use_framework_detection=True,
            cache_ttl=3600
        )
        
        performance_results = {}
        
        for script_path in self.test_scripts:
            script_name = script_path.name
            logger.info(f"测试脚本: {script_name}")

            # 清空缓存确保第一次检测无缓存
            detector.clear_cache()

            # 第一次检测（无缓存）
            start_time = time.time()
            result1 = detector.detect_modules(str(script_path), force_refresh=True)
            first_time = time.time() - start_time
            
            # 第二次检测（有缓存）
            start_time = time.time()
            result2 = detector.detect_modules(str(script_path))
            second_time = time.time() - start_time
            
            # 验证结果一致性
            assert result1.detected_modules == result2.detected_modules, f"检测结果不一致: {script_name}"
            assert not result1.cache_hit, "第一次检测不应该命中缓存"
            assert result2.cache_hit, "第二次检测应该命中缓存"
            
            # 计算性能提升
            speedup = first_time / second_time if second_time > 0 else float('inf')
            
            performance_results[script_name] = {
                'first_time': first_time,
                'second_time': second_time,
                'speedup': speedup,
                'modules_count': len(result1.detected_modules),
                'cache_hit': result2.cache_hit
            }
            
            logger.info(f"  首次检测: {first_time:.3f}s")
            logger.info(f"  缓存检测: {second_time:.3f}s")
            logger.info(f"  性能提升: {speedup:.1f}x")
            logger.info(f"  检测模块: {len(result1.detected_modules)} 个")
        
        self.results['module_detection'] = performance_results
        logger.info("✅ 模块检测性能测试完成")
        return performance_results
    
    def test_dependency_analysis_performance(self):
        """测试依赖分析性能"""
        logger.info("测试依赖分析性能...")
        
        analyzer = OptimizedDependencyAnalyzer(cache_ttl=3600)
        
        # 测试不同规模的模块集合
        test_module_sets = [
            {"os", "sys", "json"},  # 小规模
            {"os", "sys", "json", "time", "datetime", "pathlib", "collections"},  # 中规模
            {"os", "sys", "json", "time", "datetime", "pathlib", "collections",
             "itertools", "functools", "operator", "math", "random", "string",
             "urllib", "http", "socket", "threading", "subprocess", "logging"}  # 大规模
        ]
        
        performance_results = {}
        
        for i, modules in enumerate(test_module_sets):
            test_name = f"module_set_{i+1} ({len(modules)} modules)"
            logger.info(f"测试模块集合: {test_name}")

            # 清空缓存确保第一次分析无缓存
            analyzer.clear_cache()

            # 第一次分析（无缓存）
            start_time = time.time()
            result1 = analyzer.analyze_dependencies(modules, force_refresh=True)
            first_time = time.time() - start_time
            
            # 第二次分析（有缓存）
            start_time = time.time()
            result2 = analyzer.analyze_dependencies(modules)
            second_time = time.time() - start_time
            
            # 验证结果一致性
            assert len(result1.dependencies) == len(result2.dependencies), f"依赖数量不一致: {test_name}"
            assert not result1.cache_hit, "第一次分析不应该命中缓存"
            assert result2.cache_hit, "第二次分析应该命中缓存"
            
            # 计算性能提升
            speedup = first_time / second_time if second_time > 0 else float('inf')
            
            performance_results[test_name] = {
                'first_time': first_time,
                'second_time': second_time,
                'speedup': speedup,
                'dependencies_count': len(result1.dependencies),
                'conflicts_count': len(result1.conflicts),
                'cache_hit': result2.cache_hit
            }
            
            logger.info(f"  首次分析: {first_time:.3f}s")
            logger.info(f"  缓存分析: {second_time:.3f}s")
            logger.info(f"  性能提升: {speedup:.1f}x")
            logger.info(f"  依赖数量: {len(result1.dependencies)} 个")
        
        self.results['dependency_analysis'] = performance_results
        logger.info("✅ 依赖分析性能测试完成")
        return performance_results
    
    def test_cache_statistics(self):
        """测试缓存统计功能"""
        logger.info("测试缓存统计功能...")
        
        cache_manager = get_cache_manager()
        detector = OptimizedModuleDetector()
        analyzer = OptimizedDependencyAnalyzer()
        
        # 执行一些操作以生成统计数据
        for script_path in self.test_scripts:
            detector.detect_modules(str(script_path))
        
        analyzer.analyze_dependencies({"os", "sys", "json", "time"})
        
        # 获取统计信息
        cache_stats = cache_manager.get_stats()
        detector_stats = detector.get_stats()
        analyzer_stats = analyzer.get_stats()
        
        logger.info("缓存管理器统计:")
        for key, value in cache_stats.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("模块检测器统计:")
        for key, value in detector_stats.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("依赖分析器统计:")
        for key, value in analyzer_stats.items():
            logger.info(f"  {key}: {value}")
        
        self.results['statistics'] = {
            'cache_manager': cache_stats,
            'module_detector': detector_stats,
            'dependency_analyzer': analyzer_stats
        }
        
        logger.info("✅ 缓存统计功能测试完成")
        return True

    def test_cache_optimization(self):
        """测试缓存优化功能"""
        logger.info("测试缓存优化功能...")

        cache_manager = get_cache_manager()

        # 添加一些测试数据
        for i in range(50):
            cache_manager.set(f"test_key_{i}", f"test_data_{i}", ttl=60)

        # 获取优化前的统计
        stats_before = cache_manager.get_stats()

        # 执行优化
        optimization_result = cache_manager.optimize()

        # 获取优化后的统计
        stats_after = cache_manager.get_stats()

        logger.info("优化结果:")
        for key, value in optimization_result.items():
            logger.info(f"  {key}: {value}")

        logger.info("优化前后对比:")
        logger.info(f"  优化前内存项: {stats_before['memory']['items']}")
        logger.info(f"  优化后内存项: {stats_after['memory']['items']}")

        self.results['optimization'] = {
            'before': stats_before,
            'after': stats_after,
            'optimization_result': optimization_result
        }

        logger.info("✅ 缓存优化功能测试完成")
        return True

    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始运行智能缓存系统性能测试...")

        try:
            self.setup()

            # 运行各项测试
            tests = [
                ("基本功能测试", self.test_cache_basic_functionality),
                ("模块检测性能测试", self.test_module_detection_performance),
                ("依赖分析性能测试", self.test_dependency_analysis_performance),
                ("缓存统计测试", self.test_cache_statistics),
                ("缓存优化测试", self.test_cache_optimization)
            ]

            passed_tests = 0
            total_tests = len(tests)

            for test_name, test_func in tests:
                try:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"运行测试: {test_name}")
                    logger.info(f"{'='*60}")

                    result = test_func()
                    if result:
                        passed_tests += 1
                        logger.info(f"✅ {test_name} - 通过")
                    else:
                        logger.error(f"❌ {test_name} - 失败")

                except Exception as e:
                    logger.error(f"❌ {test_name} - 异常: {e}")
                    import traceback
                    traceback.print_exc()

            # 生成测试报告
            self._generate_report(passed_tests, total_tests)

        finally:
            self.teardown()

    def _generate_report(self, passed_tests: int, total_tests: int):
        """生成测试报告"""
        logger.info(f"\n{'='*60}")
        logger.info("测试报告")
        logger.info(f"{'='*60}")

        logger.info(f"总测试数: {total_tests}")
        logger.info(f"通过测试: {passed_tests}")
        logger.info(f"失败测试: {total_tests - passed_tests}")
        logger.info(f"通过率: {passed_tests/total_tests*100:.1f}%")

        # 性能提升总结
        if 'module_detection' in self.results:
            logger.info(f"\n模块检测性能提升:")
            for script_name, result in self.results['module_detection'].items():
                logger.info(f"  {script_name}: {result['speedup']:.1f}x 提升")

        if 'dependency_analysis' in self.results:
            logger.info(f"\n依赖分析性能提升:")
            for test_name, result in self.results['dependency_analysis'].items():
                logger.info(f"  {test_name}: {result['speedup']:.1f}x 提升")

        # 缓存效率
        if 'statistics' in self.results:
            cache_stats = self.results['statistics']['cache_manager']
            logger.info(f"\n缓存效率:")
            logger.info(f"  命中率: {cache_stats.get('hit_rate', 'N/A')}")
            logger.info(f"  总大小: {cache_stats.get('total_size_mb', 'N/A')} MB")

        logger.info(f"\n{'='*60}")

        if passed_tests == total_tests:
            logger.info("🎉 所有测试通过！智能缓存系统工作正常。")
        else:
            logger.warning(f"⚠️  有 {total_tests - passed_tests} 个测试失败，请检查相关功能。")


def main():
    """主函数"""
    print("智能缓存系统性能测试")
    print("=" * 60)

    tester = CachePerformanceTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
