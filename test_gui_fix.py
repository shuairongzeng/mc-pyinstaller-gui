#!/usr/bin/env python3
"""
测试GUI应用中的Python解释器修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
from controllers.main_controller import MainController
from config.app_config import AppConfig

def test_gui_command_generation():
    """测试GUI中的命令生成"""
    print("🔧 测试GUI中的Python解释器修复")
    print("=" * 50)
    
    # 创建QApplication（GUI测试需要）
    app = QApplication(sys.argv)
    
    try:
        # 创建配置
        config = AppConfig()
        
        # 显示配置信息
        python_interpreter = config.get("python_interpreter", "")
        print(f"配置的Python解释器: {python_interpreter}")
        print(f"当前运行的Python解释器: {sys.executable}")
        print()
        
        # 创建模型、控制器和主窗口
        from models.packer_model import PyInstallerModel
        model = PyInstallerModel(config)
        controller = MainController(config, model)
        main_window = MainWindow(config, model, controller)
        
        # 设置测试脚本
        main_window.model.script_path = "C:/Users/Administrator/PycharmProjects/PythonTuSe/automation_ui.py"
        main_window.model.output_dir = "D:\\CustomGit\\mc-pyinstaller-gui\\dist"
        main_window.model.icon_path = "C:/Users/Administrator/PycharmProjects/PythonTuSe/kwMusic.png"
        main_window.model.name = "自动点击程序22"
        main_window.model.is_one_file = True
        main_window.model.is_windowed = False
        main_window.model.clean = True
        main_window.model.log_level = "INFO"
        
        # 测试generate_command方法（这是我们修复的方法）
        print("测试GUI中的generate_command方法:")
        main_window.generate_command()
        
        # 检查日志标签页中的命令预览
        if hasattr(main_window, 'log_tab') and main_window.log_tab:
            command_preview = main_window.log_tab.command_preview.toPlainText()
            print("生成的命令预览:")
            print(command_preview[:200] + "..." if len(command_preview) > 200 else command_preview)
            print()
            
            # 分析命令
            if python_interpreter and python_interpreter in command_preview:
                print("✅ GUI修复成功！命令预览中使用了配置的Python解释器")
            elif python_interpreter:
                print("❌ GUI修复失败！命令预览中未使用配置的Python解释器")
            else:
                print("⚠️  配置中没有设置Python解释器路径")
        else:
            print("⚠️  无法获取命令预览")
            
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        app.quit()

if __name__ == "__main__":
    test_gui_command_generation()
