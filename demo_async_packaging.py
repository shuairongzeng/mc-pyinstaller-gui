#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步打包功能演示脚本
"""
import sys
import os
import tempfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QProgressBar, QLabel
from PyQt5.QtCore import pyqtSlot

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel
from services.package_service import AsyncPackageService


class AsyncPackagingDemo(QMainWindow):
    """异步打包演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("异步打包功能演示")
        self.setGeometry(100, 100, 800, 600)
        
        # 初始化组件
        self.config = AppConfig()
        self.model = PyInstallerModel(self.config)
        self.async_service = None
        
        self.init_ui()
        self.setup_test_script()
    
    def init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 按钮
        self.start_btn = QPushButton("开始异步打包")
        self.start_btn.clicked.connect(self.start_packaging)
        layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("取消打包")
        self.cancel_btn.clicked.connect(self.cancel_packaging)
        self.cancel_btn.setEnabled(False)
        layout.addWidget(self.cancel_btn)
        
        # 日志输出
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
    
    def setup_test_script(self):
        """设置测试脚本"""
        # 创建临时测试脚本
        self.temp_script = tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        )
        self.temp_script.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本
"""
import time
import sys

def main():
    print("Hello from test script!")
    print("Python version:", sys.version)
    print("Script is running...")
    
    # 模拟一些工作
    for i in range(5):
        print(f"Working... {i+1}/5")
        time.sleep(1)
    
    print("Test script completed!")

if __name__ == "__main__":
    main()
''')
        self.temp_script.close()
        
        # 配置模型
        self.model.script_path = self.temp_script.name
        self.model.output_dir = tempfile.mkdtemp()
        self.model.is_one_file = True
        self.model.is_windowed = False
        
        self.log_text.append(f"测试脚本: {self.temp_script.name}")
        self.log_text.append(f"输出目录: {self.model.output_dir}")
    
    @pyqtSlot()
    def start_packaging(self):
        """开始打包"""
        if self.async_service and self.async_service.is_running():
            self.log_text.append("打包任务已在运行中...")
            return
        
        # 创建异步服务
        self.async_service = AsyncPackageService(
            self.model, 
            python_interpreter="",
            timeout=60  # 1分钟超时
        )
        
        # 连接信号
        self.async_service.connect_signals(
            progress_callback=self.on_progress_updated,
            output_callback=self.on_output_received,
            error_callback=self.on_error_occurred,
            finished_callback=self.on_finished,
            status_callback=self.on_status_changed
        )
        
        # 启动打包
        if self.async_service.start_packaging():
            self.log_text.append("异步打包任务已启动...")
            self.start_btn.setEnabled(False)
            self.cancel_btn.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)
        else:
            self.log_text.append("启动打包任务失败")
    
    @pyqtSlot()
    def cancel_packaging(self):
        """取消打包"""
        if self.async_service:
            self.async_service.cancel_packaging()
            self.log_text.append("正在取消打包...")
    
    @pyqtSlot(int)
    def on_progress_updated(self, progress):
        """进度更新"""
        self.progress_bar.setValue(progress)
        self.log_text.append(f"进度: {progress}%")
    
    @pyqtSlot(str)
    def on_output_received(self, output):
        """输出接收"""
        self.log_text.append(f"[OUTPUT] {output}")
    
    @pyqtSlot(str)
    def on_error_occurred(self, error):
        """错误发生"""
        self.log_text.append(f"[ERROR] {error}")
    
    @pyqtSlot(bool, str)
    def on_finished(self, success, message):
        """打包完成"""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("打包完成")
            self.log_text.append(f"[SUCCESS] {message}")
        else:
            self.status_label.setText("打包失败")
            self.log_text.append(f"[FAILED] {message}")
    
    @pyqtSlot(str)
    def on_status_changed(self, status):
        """状态变化"""
        self.status_label.setText(status)
        self.log_text.append(f"[STATUS] {status}")
    
    def closeEvent(self, event):
        """关闭事件"""
        # 清理临时文件
        try:
            if hasattr(self, 'temp_script'):
                os.unlink(self.temp_script.name)
        except:
            pass
        
        # 取消正在运行的任务
        if self.async_service and self.async_service.is_running():
            self.async_service.cancel_packaging()
        
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建演示窗口
    demo = AsyncPackagingDemo()
    demo.show()
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
