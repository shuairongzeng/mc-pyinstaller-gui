#!/usr/bin/env python3
"""
优化的PyInstaller打包脚本
"""

import subprocess
import sys
import os

def build_app():
    """构建应用程序"""
    print("🚀 开始打包...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=PyInstaller-GUI",
        "--onefile",
        "--windowed",
        "--icon=icon.png",
        "--add-data=config.json;.",
        "--add-data=icon.png;.",
        "--add-data=images;images",
        "--add-data=templates;templates",
        "--additional-hooks-dir=hooks",
        "--collect-all=PyQt5",
        "--hidden-import=PyQt5.sip",
        "--hidden-import=sip",
        "--hidden-import=encodings.utf_8",
        "--hidden-import=encodings.cp1252",
        "--hidden-import=encodings.ascii",
        "--hidden-import=platform",
        "--hidden-import=subprocess",
        "--hidden-import=json",
        "--hidden-import=configparser",
        "--hidden-import=importlib.util",
        "--hidden-import=importlib.metadata",
        "--clean",
        "--noconfirm",
        "__init__.py"
    ]
    
    print("执行命令:")
    print(" ".join(cmd))
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ 打包完成!")
        print("📁 输出目录: dist/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        return False

if __name__ == "__main__":
    build_app()
