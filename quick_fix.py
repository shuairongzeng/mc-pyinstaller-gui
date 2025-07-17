#!/usr/bin/env python3
"""
快速修复PyQt5打包问题
"""

import subprocess
import sys
import os
import shutil

def quick_fix():
    """快速修复方案"""
    print("快速修复PyQt5打包问题...")
    
    # 清理构建文件
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理: {dir_name}")
    
    # 使用优化参数重新打包
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onedir',  # 使用目录模式而不是单文件
        '--windowed',  # 窗口模式
        '--clean',
        '--noconfirm',
        '--noupx',  # 明确禁用UPX
        '--add-data', 'icon.png;.',
        '--add-data', 'config.json;.',
        '--hidden-import', 'PyQt5.sip',
        '--hidden-import', 'sip',
        'main.py'
    ]
    
    print("执行命令:", ' '.join(cmd))
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("打包成功! 请检查 dist/main/ 目录")
    else:
        print("打包失败，请查看错误信息")

if __name__ == "__main__":
    quick_fix()
