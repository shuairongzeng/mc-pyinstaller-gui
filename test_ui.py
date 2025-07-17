#!/usr/bin/env python3
"""
测试UI界面，检查按钮是否正确显示
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

def test_buttons():
    """测试按钮显示"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("按钮测试")
    window.setMinimumSize(600, 400)
    
    # 创建中央部件
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # 添加一些内容
    layout.addWidget(QLabel("这是一个测试窗口"))
    layout.addWidget(QLabel("检查底部按钮是否显示"))
    
    # 添加弹性空间
    layout.addStretch()
    
    # 创建底部按钮
    button_layout = QHBoxLayout()
    
    # 生成命令按钮
    generate_cmd_btn = QPushButton("生成命令")
    button_layout.addWidget(generate_cmd_btn)
    
    # 开始打包按钮
    start_package_btn = QPushButton("开始打包")
    button_layout.addWidget(start_package_btn)
    
    # 取消打包按钮
    cancel_package_btn = QPushButton("取消打包")
    cancel_package_btn.setEnabled(False)
    button_layout.addWidget(cancel_package_btn)
    
    # 清空配置按钮
    clear_config_btn = QPushButton("清空配置")
    button_layout.addWidget(clear_config_btn)
    
    layout.addLayout(button_layout)
    
    # 显示窗口
    window.show()
    
    print("测试窗口已启动，请检查是否能看到底部的四个按钮：")
    print("1. 生成命令")
    print("2. 开始打包")
    print("3. 取消打包 (应该是灰色的)")
    print("4. 清空配置")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(test_buttons())
