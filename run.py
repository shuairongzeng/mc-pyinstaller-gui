#!/usr/bin/env python3
"""
PyInstaller打包工具启动脚本
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """启动应用程序"""
    try:
        print("正在启动PyInstaller打包工具...")
        
        # 检查依赖
        try:
            import PyQt5
            print("✅ PyQt5 已安装")
        except ImportError:
            print("❌ PyQt5 未安装，请运行: pip install -r requirements.txt")
            return 1
        
        try:
            import pyinstaller
            print("✅ PyInstaller 已安装")
        except ImportError:
            print("❌ PyInstaller 未安装，请运行: pip install -r requirements.txt")
            return 1
        
        # 启动应用程序
        from __init__ import main as app_main
        return app_main()
        
    except KeyboardInterrupt:
        print("\n用户中断，程序退出")
        return 0
    except Exception as e:
        print(f"启动失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
