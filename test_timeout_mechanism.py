"""
超时机制测试脚本
"""
import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QTextEdit
from PyQt5.QtCore import pyqtSlot, QTimer

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel
from services.package_service import AsyncPackageWorker


class TimeoutTestWindow(QMainWindow):
    """超时机制测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("超时机制测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 初始化配置和模型
        self.config = AppConfig()
        self.model = PyInstallerModel(self.config)
        self.worker = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel("超时机制功能测试")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 测试按钮
        test_buttons = [
            ("测试配置系统超时设置", self.test_config_timeout),
            ("测试智能超时建议", self.test_smart_suggestion),
            ("测试超时时间格式化", self.test_timeout_formatting),
            ("测试项目复杂度分析", self.test_project_complexity),
            ("测试剩余时间监控", self.test_remaining_time_monitor),
            ("测试超时警告机制", self.test_timeout_warning),
            ("测试短超时（30秒）", self.test_short_timeout),
            ("测试长超时（10分钟）", self.test_long_timeout)
        ]
        
        for text, handler in test_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
        
        # 输出区域
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        # 清除按钮
        clear_btn = QPushButton("清除输出")
        clear_btn.clicked.connect(self.output_text.clear)
        layout.addWidget(clear_btn)
    
    def log(self, message: str):
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.append(f"[{timestamp}] {message}")
    
    def test_config_timeout(self):
        """测试配置系统超时设置"""
        self.log("=== 测试配置系统超时设置 ===")
        
        # 测试默认超时
        default_timeout = self.config.get_package_timeout()
        self.log(f"默认超时时间: {default_timeout}秒")
        
        # 测试设置超时
        test_timeouts = [60, 300, 600, 1800, 3600, 7200]
        for timeout in test_timeouts:
            self.config.set_package_timeout(timeout)
            actual = self.config.get_package_timeout()
            self.log(f"设置 {timeout}秒 -> 实际 {actual}秒")
        
        # 测试边界值
        self.config.set_package_timeout(30)  # 小于最小值
        self.log(f"设置30秒 -> 实际 {self.config.get_package_timeout()}秒 (应该是60)")
        
        self.config.set_package_timeout(10000)  # 大于最大值
        self.log(f"设置10000秒 -> 实际 {self.config.get_package_timeout()}秒 (应该是7200)")
        
        # 恢复默认值
        self.config.set_package_timeout(600)
        self.log("已恢复默认超时设置")
    
    def test_smart_suggestion(self):
        """测试智能超时建议"""
        self.log("=== 测试智能超时建议 ===")
        
        # 创建测试脚本文件
        test_script = "test_script.py"
        with open(test_script, "w", encoding="utf-8") as f:
            f.write("""
import os
import sys
import time
import json
import requests
import numpy as np
import pandas as pd

def main():
    print("Hello, World!")
    time.sleep(1)

if __name__ == "__main__":
    main()
""")
        
        try:
            # 测试智能建议
            suggested = self.config.suggest_timeout_for_project(test_script)
            self.log(f"测试脚本建议超时: {suggested}秒 ({self.config.format_timeout_display(suggested)})")
            
            # 测试不存在的文件
            suggested_none = self.config.suggest_timeout_for_project("nonexistent.py")
            self.log(f"不存在文件建议超时: {suggested_none}秒")
            
        finally:
            # 清理测试文件
            if os.path.exists(test_script):
                os.remove(test_script)
                self.log("已清理测试文件")
    
    def test_timeout_formatting(self):
        """测试超时时间格式化"""
        self.log("=== 测试超时时间格式化 ===")
        
        test_cases = [30, 60, 90, 300, 600, 900, 1800, 3600, 3660, 7200]
        
        for seconds in test_cases:
            formatted = self.config.format_timeout_display(seconds)
            self.log(f"{seconds}秒 -> {formatted}")
    
    def test_project_complexity(self):
        """测试项目复杂度分析"""
        self.log("=== 测试项目复杂度分析 ===")
        
        # 创建测试项目结构
        test_dir = "test_project"
        os.makedirs(test_dir, exist_ok=True)
        
        try:
            # 创建主脚本
            main_script = os.path.join(test_dir, "main.py")
            with open(main_script, "w", encoding="utf-8") as f:
                f.write("""
import tensorflow as tf
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import datasets

def main():
    print("Complex project with heavy dependencies")

if __name__ == "__main__":
    main()
""")
            
            # 创建其他Python文件
            for i in range(5):
                with open(os.path.join(test_dir, f"module_{i}.py"), "w", encoding="utf-8") as f:
                    f.write(f"# Module {i}\nprint('Module {i}')\n")
            
            # 分析复杂度
            complexity = self.config._analyze_project_complexity(main_script)
            suggested = self.config.suggest_timeout_for_project(main_script)
            
            self.log(f"项目复杂度评分: {complexity}")
            self.log(f"建议超时时间: {suggested}秒 ({self.config.format_timeout_display(suggested)})")
            
        finally:
            # 清理测试目录
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
                self.log("已清理测试项目")
    
    def test_remaining_time_monitor(self):
        """测试剩余时间监控"""
        self.log("=== 测试剩余时间监控 ===")
        
        # 创建模拟的worker
        self.model.script_path = "test.py"
        worker = AsyncPackageWorker(self.model, timeout=30)  # 30秒超时用于测试
        
        # 连接信号
        worker.remaining_time_updated.connect(self.on_remaining_time_test)
        worker.timeout_warning.connect(self.on_timeout_warning_test)
        
        # 模拟启动监控
        worker.start_time = time.time()
        worker._start_remaining_time_monitor()
        
        self.log("已启动30秒超时的剩余时间监控，请观察输出")
        
        # 10秒后停止监控
        QTimer.singleShot(10000, lambda: self.stop_monitor_test(worker))
    
    def test_timeout_warning(self):
        """测试超时警告机制"""
        self.log("=== 测试超时警告机制 ===")
        
        # 启用超时警告
        self.config.set("timeout_warning_enabled", True)
        self.log("已启用超时警告")
        
        # 创建短超时的worker来快速触发警告
        self.model.script_path = "test.py"
        worker = AsyncPackageWorker(self.model, timeout=20)  # 20秒超时
        
        # 连接信号
        worker.timeout_warning.connect(self.on_timeout_warning_test)
        
        # 模拟已经运行了15秒
        worker.start_time = time.time() - 15
        worker._start_remaining_time_monitor()
        
        self.log("模拟已运行15秒，20秒超时，应该很快触发警告")
        
        # 8秒后停止
        QTimer.singleShot(8000, lambda: self.stop_monitor_test(worker))
    
    def test_short_timeout(self):
        """测试短超时"""
        self.log("=== 测试短超时（30秒）===")
        self.config.set_package_timeout(30)
        timeout = self.config.get_package_timeout()
        formatted = self.config.format_timeout_display(timeout)
        self.log(f"设置短超时: {timeout}秒 ({formatted})")
    
    def test_long_timeout(self):
        """测试长超时"""
        self.log("=== 测试长超时（10分钟）===")
        self.config.set_package_timeout(600)
        timeout = self.config.get_package_timeout()
        formatted = self.config.format_timeout_display(timeout)
        self.log(f"设置长超时: {timeout}秒 ({formatted})")
    
    @pyqtSlot(int)
    def on_remaining_time_test(self, remaining_seconds: int):
        """剩余时间测试回调"""
        formatted = self.config.format_timeout_display(remaining_seconds)
        self.log(f"⏰ 剩余时间: {formatted}")
    
    @pyqtSlot(int)
    def on_timeout_warning_test(self, remaining_seconds: int):
        """超时警告测试回调"""
        formatted = self.config.format_timeout_display(remaining_seconds)
        self.log(f"⚠️ 超时警告: 剩余 {formatted}")
    
    def stop_monitor_test(self, worker):
        """停止监控测试"""
        worker._stop_remaining_time_monitor()
        self.log("已停止剩余时间监控")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TimeoutTestWindow()
    window.show()
    
    print("超时机制测试程序已启动")
    print("点击按钮测试不同的超时功能")
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
