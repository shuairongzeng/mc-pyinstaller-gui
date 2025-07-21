#!/usr/bin/env python3
"""
测试Python解释器配置修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.packer_model import PyInstallerModel
from config.app_config import AppConfig

def test_python_interpreter_fix():
    """测试Python解释器配置修复"""
    print("🔧 测试Python解释器配置修复")
    print("=" * 50)
    
    # 创建配置
    config = AppConfig()
    
    # 显示当前配置
    python_interpreter = config.get("python_interpreter", "")
    print(f"配置的Python解释器: {python_interpreter}")
    print(f"当前运行的Python解释器: {sys.executable}")
    print()
    
    # 创建模型
    model = PyInstallerModel(config)
    model.script_path = "C:/Users/Administrator/PycharmProjects/PythonTuSe/automation_ui.py"
    model.output_dir = "D:\\CustomGit\\mc-pyinstaller-gui\\dist"
    model.icon_path = "C:/Users/Administrator/PycharmProjects/PythonTuSe/kwMusic.png"
    model.name = "自动点击程序22"
    model.is_one_file = True
    model.is_windowed = False
    model.clean = True
    model.log_level = "INFO"
    
    # 测试1: 不传递python_interpreter参数（旧的错误方式）
    print("测试1: 不传递python_interpreter参数")
    command1 = model.generate_command()
    print(f"生成的命令: {command1}")
    print()
    
    # 测试2: 传递python_interpreter参数（修复后的方式）
    print("测试2: 传递python_interpreter参数")
    command2 = model.generate_command(python_interpreter)
    print(f"生成的命令: {command2}")
    print()
    
    # 分析差异
    print("分析:")
    if python_interpreter:
        if python_interpreter in command2:
            print("✅ 修复成功！命令中使用了配置的Python解释器")
        else:
            print("❌ 修复失败！命令中仍未使用配置的Python解释器")
            
        if sys.executable in command1:
            print("✅ 确认问题存在：不传参数时使用当前环境的Python解释器")
        else:
            print("❓ 未发现预期的问题")
    else:
        print("⚠️  配置中没有设置Python解释器路径")

if __name__ == "__main__":
    test_python_interpreter_fix()
