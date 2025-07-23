#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖安装脚本
根据用户需求安装不同级别的依赖包
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 错误：需要Python 3.8或更高版本")
        print(f"   当前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本检查通过：{version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """检查pip是否可用"""
    success, stdout, stderr = run_command("pip --version")
    if success:
        print(f"✅ pip可用：{stdout.strip()}")
        return True
    else:
        print("❌ pip不可用，请先安装pip")
        return False

def install_requirements(requirements_file):
    """安装requirements文件中的依赖"""
    if not os.path.exists(requirements_file):
        print(f"❌ 文件不存在：{requirements_file}")
        return False
    
    print(f"📦 正在安装 {requirements_file} 中的依赖...")
    success, stdout, stderr = run_command(f"pip install -r {requirements_file}")
    
    if success:
        print(f"✅ {requirements_file} 安装成功")
        return True
    else:
        print(f"❌ {requirements_file} 安装失败")
        print(f"错误信息：{stderr}")
        return False

def main():
    """主函数"""
    print("🚀 PyInstaller GUI 依赖安装脚本")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 检查pip
    if not check_pip():
        return 1
    
    # 显示安装选项
    print("\n📋 请选择安装级别：")
    print("1. 最小安装（仅核心功能）")
    print("2. 标准安装（推荐）")
    print("3. 完整安装（包含开发工具）")
    print("4. 自定义安装")
    
    try:
        choice = input("\n请输入选择 (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n\n用户取消安装")
        return 0
    
    if choice == "1":
        # 最小安装
        success = install_requirements("requirements-minimal.txt")
    elif choice == "2":
        # 标准安装
        success = install_requirements("requirements.txt")
    elif choice == "3":
        # 完整安装
        success = install_requirements("requirements-dev.txt")
    elif choice == "4":
        # 自定义安装
        print("\n📋 可用的requirements文件：")
        requirements_files = [
            ("requirements-minimal.txt", "最小依赖"),
            ("requirements.txt", "标准依赖"),
            ("requirements-dev.txt", "开发依赖")
        ]
        
        for i, (file, desc) in enumerate(requirements_files, 1):
            if os.path.exists(file):
                print(f"{i}. {file} - {desc}")
        
        try:
            file_choice = input("\n请输入文件编号: ").strip()
            file_index = int(file_choice) - 1
            if 0 <= file_index < len(requirements_files):
                success = install_requirements(requirements_files[file_index][0])
            else:
                print("❌ 无效选择")
                return 1
        except (ValueError, KeyboardInterrupt):
            print("❌ 无效输入或用户取消")
            return 1
    else:
        print("❌ 无效选择")
        return 1
    
    if success:
        print("\n🎉 依赖安装完成！")
        print("\n📝 下一步：")
        print("   运行应用程序：python run.py")
        print("   或者：python __init__.py")
        return 0
    else:
        print("\n❌ 依赖安装失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
