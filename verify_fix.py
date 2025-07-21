#!/usr/bin/env python3
"""
验证Python解释器修复是否有效
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def verify_fix():
    """验证修复"""
    print("🔧 验证Python解释器修复")
    print("=" * 50)
    
    # 导入必要的模块
    from config.app_config import AppConfig
    from models.packer_model import PyInstallerModel
    
    # 创建配置和模型
    config = AppConfig()
    model = PyInstallerModel(config)
    
    # 显示配置信息
    python_interpreter = config.get("python_interpreter", "")
    print(f"配置的Python解释器: {python_interpreter}")
    print(f"当前运行的Python解释器: {sys.executable}")
    print()
    
    # 设置测试脚本
    model.script_path = "C:/Users/Administrator/PycharmProjects/PythonTuSe/automation_ui.py"
    model.output_dir = "D:\\CustomGit\\mc-pyinstaller-gui\\dist"
    model.icon_path = "C:/Users/Administrator/PycharmProjects/PythonTuSe/kwMusic.png"
    model.name = "自动点击程序22"
    model.is_one_file = True
    model.is_windowed = False
    model.clean = True
    model.log_level = "INFO"
    
    print("生成命令对比:")
    print("-" * 30)
    
    # 测试1: 不传递python_interpreter参数（旧方式）
    print("1. 不传递python_interpreter参数:")
    command1 = model.generate_command()
    print(f"   Python解释器: {command1.split()[0]}")
    
    # 查找--add-binary参数
    parts = command1.split()
    binary_paths = [part for part in parts if part.startswith("--add-binary=")]
    if binary_paths:
        print(f"   二进制文件示例: {binary_paths[0]}")
    print()
    
    # 测试2: 传递python_interpreter参数（新方式）
    print("2. 传递python_interpreter参数:")
    command2 = model.generate_command(python_interpreter)
    print(f"   Python解释器: {command2.split()[0]}")
    
    # 查找--add-binary参数
    parts = command2.split()
    binary_paths = [part for part in parts if part.startswith("--add-binary=")]
    if binary_paths:
        print(f"   二进制文件示例: {binary_paths[0]}")
    print()
    
    # 分析结果
    print("修复验证结果:")
    print("-" * 30)
    
    if python_interpreter:
        # 检查Python解释器
        if python_interpreter in command2:
            print("✅ Python解释器修复成功")
        else:
            print("❌ Python解释器修复失败")
            
        # 检查二进制文件路径
        if binary_paths:
            binary_path = binary_paths[0].split("=")[1].split(";")[0]
            if python_interpreter.replace("python.exe", "") in binary_path:
                print("✅ 二进制文件路径修复成功")
            else:
                print("❌ 二进制文件路径修复失败")
        
        # 检查是否有差异
        if command1 != command2:
            print("✅ 修复有效：两个命令不同")
        else:
            print("❌ 修复无效：两个命令相同")
    else:
        print("⚠️  配置中没有设置Python解释器路径")
    
    print()
    print("修复总结:")
    print("- 修复了views/main_window.py中generate_command和on_config_changed方法")
    print("- 修复了models/packer_model.py中_get_critical_binaries方法")
    print("- 现在会正确使用配置中指定的Python解释器")
    print("- 二进制文件也会从指定的Python环境中查找")

if __name__ == "__main__":
    verify_fix()
