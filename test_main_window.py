#!/usr/bin/env python3
"""
测试主窗口，专门检查按钮显示问题
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QMessageBox, QPushButton, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel

class TestMainWindow(QMainWindow):
    """测试主窗口类"""

    def __init__(self):
        super().__init__()
        self.config = AppConfig()
        self.model = PyInstallerModel(self.config)
        
        self.init_ui()

    def init_ui(self) -> None:
        """初始化用户界面"""
        self.setWindowTitle(f"测试窗口 - {AppConfig.APP_NAME} v{AppConfig.APP_VERSION}")
        self.setMinimumSize(800, 600)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 添加一些说明文字
        layout.addWidget(QLabel("这是一个测试窗口"))
        layout.addWidget(QLabel("请检查底部是否显示了四个按钮："))
        layout.addWidget(QLabel("1. 生成命令"))
        layout.addWidget(QLabel("2. 开始打包"))
        layout.addWidget(QLabel("3. 取消打包"))
        layout.addWidget(QLabel("4. 清空配置"))

        # 创建标签页（简化版）
        self.tab_widget = QTabWidget()
        
        # 添加一个简单的标签页
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.addWidget(QLabel("基本设置标签页"))
        tab1_layout.addWidget(QLabel("这里应该有脚本选择等功能"))
        self.tab_widget.addTab(tab1, "基本设置")
        
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QLabel("打包日志标签页"))
        tab2_layout.addWidget(QLabel("这里应该显示打包日志"))
        self.tab_widget.addTab(tab2, "打包日志")
        
        layout.addWidget(self.tab_widget)

        # 创建底部按钮
        self.create_bottom_buttons(layout)

    def create_bottom_buttons(self, layout: QVBoxLayout) -> None:
        """创建底部按钮"""
        print("正在创建底部按钮...")
        
        button_layout = QHBoxLayout()

        # 生成命令按钮
        self.generate_cmd_btn = QPushButton("生成命令")
        self.generate_cmd_btn.clicked.connect(self.test_generate_command)
        button_layout.addWidget(self.generate_cmd_btn)
        print("✅ 生成命令按钮已创建")

        # 开始打包按钮
        self.start_package_btn = QPushButton("开始打包")
        self.start_package_btn.clicked.connect(self.test_start_package)
        button_layout.addWidget(self.start_package_btn)
        print("✅ 开始打包按钮已创建")

        # 取消打包按钮
        self.cancel_package_btn = QPushButton("取消打包")
        self.cancel_package_btn.clicked.connect(self.test_cancel_package)
        self.cancel_package_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_package_btn)
        print("✅ 取消打包按钮已创建")

        # 清空配置按钮
        self.clear_config_btn = QPushButton("清空配置")
        self.clear_config_btn.clicked.connect(self.test_clear_config)
        button_layout.addWidget(self.clear_config_btn)
        print("✅ 清空配置按钮已创建")

        layout.addLayout(button_layout)
        print("✅ 所有按钮已添加到布局")

    @pyqtSlot()
    def test_generate_command(self) -> None:
        """测试生成命令"""
        QMessageBox.information(self, "测试", "生成命令按钮被点击了！")

    @pyqtSlot()
    def test_start_package(self) -> None:
        """测试开始打包"""
        QMessageBox.information(self, "测试", "开始打包按钮被点击了！")

    @pyqtSlot()
    def test_cancel_package(self) -> None:
        """测试取消打包"""
        QMessageBox.information(self, "测试", "取消打包按钮被点击了！")

    @pyqtSlot()
    def test_clear_config(self) -> None:
        """测试清空配置"""
        QMessageBox.information(self, "测试", "清空配置按钮被点击了！")

def main():
    """主函数"""
    try:
        print("启动测试程序...")
        
        # 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName("测试程序")
        
        print("创建测试窗口...")
        
        # 创建主窗口
        main_window = TestMainWindow()
        main_window.show()
        
        print("测试窗口已显示")
        print("请检查窗口底部是否有四个按钮")
        
        # 运行应用程序
        return app.exec_()
        
    except Exception as e:
        print(f"测试程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
