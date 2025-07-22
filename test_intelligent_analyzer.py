"""
测试智能模块分析器
"""

import os
import tempfile
from services.intelligent_module_analyzer import IntelligentModuleAnalyzer


def create_complex_test_script() -> str:
    """创建复杂的测试脚本"""
    test_code = '''
#!/usr/bin/env python3
"""
复杂的测试应用程序
包含多种导入模式和功能
"""

# 标准库导入
import os
import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 第三方库导入
try:
    import requests
    import pandas as pd
    import numpy as np
    HAS_DATA_LIBS = True
except ImportError:
    HAS_DATA_LIBS = False

# 条件导入
if sys.platform == 'win32':
    import winsound
    import winreg
elif sys.platform.startswith('linux'):
    import termios
    import fcntl

# GUI相关导入
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtCore import QThread, pyqtSignal
    GUI_AVAILABLE = True
except ImportError:
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        GUI_AVAILABLE = True
    except ImportError:
        GUI_AVAILABLE = False

# 动态导入示例
def load_plugin(plugin_name):
    """动态加载插件"""
    import importlib
    try:
        module = importlib.import_module(f"plugins.{plugin_name}")
        return module
    except ImportError:
        return None

def dynamic_import_example():
    """各种动态导入示例"""
    # importlib导入
    import importlib
    
    modules_to_load = ['sqlite3', 'csv', 'xml.etree.ElementTree']
    loaded_modules = {}
    
    for module_name in modules_to_load:
        try:
            loaded_modules[module_name] = importlib.import_module(module_name)
        except ImportError:
            pass
    
    # __import__导入
    math_module = __import__('math')
    random_module = __import__('random')
    
    # exec中的导入
    exec_code = """
import hashlib
import base64
import pickle
"""
    exec(exec_code)
    
    # 字符串格式化导入
    module_name = "urllib.parse"
    exec(f"import {module_name.replace('.', ' as ')}")
    
    return loaded_modules

# 网络功能
class NetworkManager:
    def __init__(self):
        self.session = None
        if 'requests' in globals():
            self.session = requests.Session()
    
    def fetch_data(self, url):
        """获取网络数据"""
        if self.session:
            try:
                response = self.session.get(url)
                return response.json()
            except Exception:
                return None
        return None

# 数据处理
class DataProcessor:
    def __init__(self):
        self.has_pandas = HAS_DATA_LIBS
    
    def process_csv(self, file_path):
        """处理CSV文件"""
        if self.has_pandas:
            import pandas as pd
            return pd.read_csv(file_path)
        else:
            import csv
            with open(file_path, 'r') as f:
                return list(csv.reader(f))
    
    def process_json(self, file_path):
        """处理JSON文件"""
        with open(file_path, 'r') as f:
            return json.load(f)

# 文件操作
class FileManager:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
    
    def scan_directory(self):
        """扫描目录"""
        import glob
        import shutil
        
        files = []
        for pattern in ['*.py', '*.json', '*.csv']:
            files.extend(glob.glob(str(self.base_path / pattern)))
        
        return files
    
    def backup_files(self, backup_dir):
        """备份文件"""
        import shutil
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        for file in self.scan_directory():
            shutil.copy2(file, backup_path)

# 多线程处理
class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        super().__init__()
        self.task_queue = task_queue
        self.daemon = True
    
    def run(self):
        import queue
        while True:
            try:
                task = self.task_queue.get(timeout=1)
                self.process_task(task)
                self.task_queue.task_done()
            except queue.Empty:
                break
    
    def process_task(self, task):
        """处理任务"""
        time.sleep(0.1)  # 模拟处理时间

# 数据库操作
class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """连接数据库"""
        import sqlite3
        self.connection = sqlite3.connect(self.db_path)
        return self.connection
    
    def execute_query(self, query, params=None):
        """执行查询"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor.fetchall()

# 配置管理
CONFIG = {
    "plugins": {
        "data_processor": "data_plugins.processor",
        "file_handler": "file_plugins.handler",
        "network_client": "network_plugins.client"
    },
    "modules": {
        "encryption": "cryptography",
        "compression": "gzip",
        "serialization": "pickle"
    }
}

def load_configured_modules():
    """加载配置中指定的模块"""
    import importlib
    loaded = {}
    
    for category, modules in CONFIG["modules"].items():
        try:
            loaded[category] = importlib.import_module(modules)
        except ImportError:
            loaded[category] = None
    
    return loaded

# 主应用程序
class MainApplication:
    def __init__(self):
        self.network_manager = NetworkManager()
        self.data_processor = DataProcessor()
        self.file_manager = FileManager("./data")
        self.db_manager = DatabaseManager("app.db")
        
        # 动态加载模块
        self.dynamic_modules = dynamic_import_example()
        self.configured_modules = load_configured_modules()
    
    def run(self):
        """运行应用程序"""
        print("Starting application...")
        
        # 处理数据
        if os.path.exists("data.csv"):
            data = self.data_processor.process_csv("data.csv")
            print(f"Processed {len(data)} records")
        
        # 网络请求
        api_data = self.network_manager.fetch_data("https://api.example.com/data")
        if api_data:
            print("Fetched API data")
        
        # 文件操作
        files = self.file_manager.scan_directory()
        print(f"Found {len(files)} files")
        
        # 数据库操作
        self.db_manager.connect()
        results = self.db_manager.execute_query("SELECT COUNT(*) FROM users")
        print(f"Database query result: {results}")
        
        print("Application finished")

if __name__ == "__main__":
    app = MainApplication()
    app.run()
'''
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        return f.name


def test_intelligent_analyzer():
    """测试智能分析器"""
    print("🧠 开始测试智能模块分析器")
    print("=" * 60)
    
    # 创建测试脚本
    test_script = create_complex_test_script()
    print(f"📝 创建复杂测试脚本: {test_script}")
    
    try:
        # 创建智能分析器
        analyzer = IntelligentModuleAnalyzer(timeout=30)
        
        # 执行分析
        def output_callback(message):
            print(f"  {message}")
        
        print("\n🔍 开始智能分析...")
        result = analyzer.analyze_script(
            test_script, 
            output_callback, 
            use_execution=True,
            enable_ml_scoring=True
        )
        
        # 生成并显示报告
        report = analyzer.generate_analysis_report(result, test_script)
        print("\n" + report)
        
        # 显示PyInstaller命令参数
        pyinstaller_args = analyzer.get_pyinstaller_command_args(result)
        if pyinstaller_args:
            print("\n🔧 PyInstaller 命令参数:")
            print("  " + " ".join(pyinstaller_args))
        
        # 显示置信度最高的模块
        print("\n⭐ 置信度最高的10个模块:")
        sorted_confidence = sorted(result.confidence_scores.items(), 
                                 key=lambda x: x[1], reverse=True)
        for module, score in sorted_confidence[:10]:
            sources = ", ".join(result.detection_sources.get(module, []))
            print(f"  {module}: {score:.3f} (来源: {sources})")
        
        print(f"\n✅ 智能分析测试完成!")
        
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


if __name__ == "__main__":
    test_intelligent_analyzer()
