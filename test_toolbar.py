#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的工具栏布局
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
from config.app_config import AppConfig

def test_toolbar_layout():
    """测试工具栏布局"""
    app = QApplication(sys.argv)
    
    # 创建配置
    config = AppConfig()
    
    # 创建主窗口
    window = MainWindow(config=config)
    window.show()
    
    print("🎨 新的工具栏布局测试")
    print("=" * 50)
    print("✅ 界面特点：")
    print("   • 四个操作按钮移动到了顶部工具栏")
    print("   • 按钮带有图标和颜色区分")
    print("   • 工具栏有边框和背景色")
    print("   • 右侧显示状态指示器")
    print("   • 按钮有悬停和点击效果")
    print()
    print("🔧 按钮说明：")
    print("   • 🔧 生成命令 (绿色) - 根据配置生成PyInstaller命令")
    print("   • ▶️ 开始打包 (蓝色) - 开始执行打包过程")
    print("   • ⏹️ 取消打包 (橙色) - 取消正在进行的打包")
    print("   • 🗑️ 清空配置 (红色) - 清空所有配置项")
    print()
    print("💡 设计优势：")
    print("   • 更符合工作流程 - 从上到下的操作顺序")
    print("   • 更容易访问 - 不需要滚动到底部")
    print("   • 视觉层次清晰 - 重要操作更突出")
    print("   • 现代化界面 - 类似IDE的工具栏设计")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(test_toolbar_layout())
