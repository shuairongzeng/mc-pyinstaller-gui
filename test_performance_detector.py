"""
测试性能优化的模块检测器
"""

import os
import time
import tempfile
from services.performance_optimized_detector import PerformanceOptimizedDetector


def create_performance_test_script() -> str:
    """创建性能测试脚本"""
    test_code = '''
#!/usr/bin/env python3
"""
性能测试脚本 - 包含大量不同类型的导入
"""

# 标准库导入
import os
import sys
import json
import time
import threading
import multiprocessing
import subprocess
import socket
import ssl
import hashlib
import hmac
import base64
import binascii
import struct
import array
import queue
import heapq
import bisect
import weakref
import types
import inspect
import importlib
import pkgutil
import modulefinder
import runpy
import ast
import dis
import py_compile
import compileall
import keyword
import token
import tokenize
import tabnanny
import pyclbr
import trace
import traceback
import pdb
import profile
import pstats
import timeit
import doctest
import unittest
import bdb
import faulthandler
import warnings
import contextlib
import abc
import atexit
import tracemalloc
import gc
import site
import sysconfig
import builtins

from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter, OrderedDict, deque
from itertools import chain, combinations, permutations
from functools import wraps, lru_cache, partial
from operator import itemgetter, attrgetter
from copy import copy, deepcopy
from pickle import dumps, loads
from sqlite3 import connect
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen
from http.server import HTTPServer
from email.mime.text import MIMEText
from html.parser import HTMLParser
from xml.etree import ElementTree
from csv import reader, writer
from configparser import ConfigParser
from logging import getLogger, basicConfig

# 第三方库导入（可能不存在）
try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import scipy.stats as stats
    import sklearn.linear_model as lm
    import tensorflow as tf
    import torch
    import keras
    import flask
    import django
    import requests
    import urllib3
    import beautifulsoup4 as bs4
    import lxml
    import pillow as PIL
    import opencv as cv2
    THIRD_PARTY_AVAILABLE = True
except ImportError:
    THIRD_PARTY_AVAILABLE = False

# 条件导入
if sys.platform == 'win32':
    import winsound
    import winreg
    import msvcrt
elif sys.platform.startswith('linux'):
    import termios
    import fcntl
    import pwd
    import grp
elif sys.platform == 'darwin':
    import termios
    import fcntl

# GUI库导入
GUI_LIBS = []
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
    from PyQt5.QtCore import QThread, pyqtSignal, QTimer
    from PyQt5.QtGui import QIcon, QPixmap, QPainter
    GUI_LIBS.append('PyQt5')
except ImportError:
    pass

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
    GUI_LIBS.append('PyQt6')
except ImportError:
    pass

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    GUI_LIBS.append('tkinter')
except ImportError:
    pass

try:
    import wx
    GUI_LIBS.append('wx')
except ImportError:
    pass

# 动态导入函数
def dynamic_imports():
    """执行各种动态导入"""
    import importlib
    
    # 动态导入列表
    modules_to_import = [
        'random', 'math', 'statistics', 'decimal', 'fractions',
        'cmath', 'numbers', 'string', 'textwrap', 'unicodedata',
        'stringprep', 'readline', 'rlcompleter', 'struct', 'codecs'
    ]
    
    loaded_modules = {}
    for module_name in modules_to_import:
        try:
            loaded_modules[module_name] = importlib.import_module(module_name)
        except ImportError:
            pass
    
    # __import__ 方式
    for module_name in ['calendar', 'locale', 'gettext']:
        try:
            loaded_modules[module_name] = __import__(module_name)
        except ImportError:
            pass
    
    # exec 方式
    exec_imports = [
        "import zlib",
        "import gzip", 
        "import bz2",
        "import lzma",
        "import zipfile",
        "import tarfile"
    ]
    
    for import_stmt in exec_imports:
        try:
            exec(import_stmt)
        except ImportError:
            pass
    
    return loaded_modules

# 延迟导入函数
def lazy_imports():
    """延迟导入示例"""
    import tempfile
    import shutil
    import glob
    import fnmatch
    import linecache
    import fileinput
    import filecmp
    import stat
    import statvfs if hasattr(os, 'statvfs') else None
    
    return locals()

# 插件系统模拟
PLUGIN_CONFIG = {
    "data_processors": [
        "pandas_processor",
        "numpy_processor", 
        "csv_processor"
    ],
    "file_handlers": [
        "json_handler",
        "xml_handler",
        "yaml_handler"
    ],
    "network_clients": [
        "requests_client",
        "urllib_client",
        "socket_client"
    ]
}

def load_plugins():
    """加载插件"""
    import importlib
    loaded_plugins = {}
    
    for category, plugins in PLUGIN_CONFIG.items():
        loaded_plugins[category] = []
        for plugin_name in plugins:
            try:
                # 模拟插件加载
                module = importlib.import_module(f"plugins.{plugin_name}")
                loaded_plugins[category].append(module)
            except ImportError:
                # 插件不存在，跳过
                pass
    
    return loaded_plugins

# 复杂的类定义
class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        # 运行时导入
        import csv
        import json
        import xml.etree.ElementTree as ET
        
        self.csv = csv
        self.json = json
        self.ET = ET
        
        # 条件导入
        try:
            import yaml
            self.yaml = yaml
        except ImportError:
            self.yaml = None
    
    def process_data(self, data_type, data):
        """处理数据"""
        if data_type == 'csv':
            return self._process_csv(data)
        elif data_type == 'json':
            return self._process_json(data)
        elif data_type == 'xml':
            return self._process_xml(data)
        elif data_type == 'yaml' and self.yaml:
            return self._process_yaml(data)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    def _process_csv(self, data):
        # CSV处理逻辑
        return list(self.csv.reader(data))
    
    def _process_json(self, data):
        # JSON处理逻辑
        return self.json.loads(data)
    
    def _process_xml(self, data):
        # XML处理逻辑
        return self.ET.fromstring(data)
    
    def _process_yaml(self, data):
        # YAML处理逻辑
        return self.yaml.safe_load(data)

# 网络处理类
class NetworkManager:
    """网络管理器"""
    
    def __init__(self):
        # 尝试导入不同的网络库
        self.http_client = None
        
        try:
            import requests
            self.http_client = requests
            self.client_type = 'requests'
        except ImportError:
            try:
                import urllib.request
                self.http_client = urllib.request
                self.client_type = 'urllib'
            except ImportError:
                import socket
                self.http_client = socket
                self.client_type = 'socket'
    
    def fetch_data(self, url):
        """获取数据"""
        if self.client_type == 'requests':
            response = self.http_client.get(url)
            return response.text
        elif self.client_type == 'urllib':
            with self.http_client.urlopen(url) as response:
                return response.read().decode()
        else:
            # 使用socket实现
            return "Socket implementation"

# 主应用类
class PerformanceTestApp:
    """性能测试应用"""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.network_manager = NetworkManager()
        self.plugins = load_plugins()
        self.dynamic_modules = dynamic_imports()
        self.lazy_modules = lazy_imports()
    
    def run_tests(self):
        """运行测试"""
        print("Starting performance tests...")
        
        # 测试数据处理
        test_data = '{"test": "data"}'
        result = self.data_processor.process_data('json', test_data)
        print(f"JSON processing result: {result}")
        
        # 测试网络功能
        try:
            data = self.network_manager.fetch_data("http://example.com")
            print(f"Network data length: {len(data)}")
        except:
            print("Network test failed")
        
        # 测试动态模块
        print(f"Loaded {len(self.dynamic_modules)} dynamic modules")
        print(f"Loaded {len(self.lazy_modules)} lazy modules")
        print(f"Available GUI libraries: {GUI_LIBS}")
        
        print("Performance tests completed")

if __name__ == "__main__":
    app = PerformanceTestApp()
    app.run_tests()
'''
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        return f.name


def test_performance_detector():
    """测试性能优化检测器"""
    print("🚀 开始测试性能优化模块检测器")
    print("=" * 60)
    
    # 创建测试脚本
    test_script = create_performance_test_script()
    print(f"📝 创建性能测试脚本: {test_script}")
    
    try:
        # 创建性能优化检测器
        detector = PerformanceOptimizedDetector(
            cache_dir="performance_cache",
            max_workers=4,
            enable_process_pool=False,
            cache_ttl=1800  # 30分钟
        )
        
        def output_callback(message):
            print(f"  {message}")
        
        # 第一次检测（无缓存）
        print("\n🔍 第一次检测（无缓存）...")
        start_time = time.time()
        
        result1 = detector.detect_modules_optimized(
            script_path=test_script,
            output_callback=output_callback,
            use_execution=True,
            force_refresh=True,
            enable_profiling=True
        )
        
        first_time = time.time() - start_time
        print(f"第一次检测完成，耗时: {first_time:.2f}s")
        
        # 显示第一次检测结果
        print("\n📊 第一次检测结果:")
        print(f"  缓存命中: {result1.cache_hit}")
        print(f"  缓存来源: {result1.cache_source}")
        print(f"  并行任务: {result1.parallel_tasks}")
        print(f"  失败任务: {result1.failed_tasks}")
        print(f"  检测模块数: {len(result1.analysis_result.recommended_modules)}")
        
        print("\n📈 性能指标:")
        print(result1.performance_metrics)
        
        if result1.optimization_suggestions:
            print("\n💡 优化建议:")
            for suggestion in result1.optimization_suggestions:
                print(f"  • {suggestion}")
        
        # 第二次检测（有缓存）
        print("\n🔍 第二次检测（有缓存）...")
        start_time = time.time()
        
        result2 = detector.detect_modules_optimized(
            script_path=test_script,
            output_callback=output_callback,
            use_execution=True,
            force_refresh=False,
            enable_profiling=True
        )
        
        second_time = time.time() - start_time
        print(f"第二次检测完成，耗时: {second_time:.2f}s")
        
        # 显示第二次检测结果
        print("\n📊 第二次检测结果:")
        print(f"  缓存命中: {result2.cache_hit}")
        print(f"  缓存来源: {result2.cache_source}")
        print(f"  性能提升: {((first_time - second_time) / first_time * 100):.1f}%")
        
        # 显示性能统计
        print("\n📈 总体性能统计:")
        stats = detector.get_performance_stats()
        for key, value in stats.items():
            if key == 'cache_stats':
                print(f"  {key}:")
                for k, v in value.__dict__.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")
        
        # 测试缓存优化
        print("\n🔧 测试缓存优化...")
        detector.optimize_cache()
        print("缓存优化完成")
        
        # 清理部分缓存
        cleared = detector.clear_cache(['module_detection'])
        print(f"清理了 {cleared} 个缓存条目")
        
        print(f"\n✅ 性能测试完成!")
        
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


def benchmark_detectors():
    """基准测试不同检测器的性能"""
    print("\n" + "=" * 60)
    print("🏁 基准测试不同检测器性能")
    print("=" * 60)
    
    test_script = create_performance_test_script()
    
    try:
        # 测试性能优化检测器
        print("测试性能优化检测器...")
        detector = PerformanceOptimizedDetector(max_workers=4)
        
        start_time = time.time()
        result = detector.detect_modules_optimized(test_script, use_execution=False)
        optimized_time = time.time() - start_time
        optimized_modules = len(result.analysis_result.recommended_modules)
        
        print(f"  耗时: {optimized_time:.3f}s")
        print(f"  检测模块数: {optimized_modules}")
        print(f"  缓存命中: {result.cache_hit}")
        
        # 测试智能分析器
        print("\n测试智能分析器...")
        from services.intelligent_module_analyzer import IntelligentModuleAnalyzer
        
        analyzer = IntelligentModuleAnalyzer()
        start_time = time.time()
        analysis_result = analyzer.analyze_script(test_script, use_execution=False)
        analyzer_time = time.time() - start_time
        analyzer_modules = len(analysis_result.recommended_modules)
        
        print(f"  耗时: {analyzer_time:.3f}s")
        print(f"  检测模块数: {analyzer_modules}")
        
        # 性能对比
        print(f"\n📊 性能对比:")
        print(f"  性能优化检测器: {optimized_time:.3f}s ({optimized_modules} 模块)")
        print(f"  智能分析器: {analyzer_time:.3f}s ({analyzer_modules} 模块)")
        
        if analyzer_time > 0:
            speedup = analyzer_time / optimized_time
            print(f"  性能提升: {speedup:.2f}x")
        
        print(f"\n✅ 基准测试完成!")
        
    except Exception as e:
        print(f"❌ 基准测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            os.unlink(test_script)
        except:
            pass


if __name__ == "__main__":
    test_performance_detector()
    benchmark_detectors()
