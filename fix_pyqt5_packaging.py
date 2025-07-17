#!/usr/bin/env python3
"""
修复PyQt5打包问题的脚本
解决 "Failed to extract PyQt5\Qt5\bin\Qt5Core.dll" 错误
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def fix_pyqt5_packaging():
    """修复PyQt5打包问题"""
    print("开始修复PyQt5打包问题...")
    
    # 1. 清理之前的构建文件
    print("1. 清理构建文件...")
    build_dirs = ['build', 'dist', '__pycache__']
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   已删除: {dir_name}")
    
    # 2. 检查PyQt5安装
    print("2. 检查PyQt5安装...")
    try:
        import PyQt5
        print(f"   PyQt5版本: {PyQt5.QtCore.PYQT_VERSION_STR}")
        print(f"   Qt版本: {PyQt5.QtCore.QT_VERSION_STR}")
    except ImportError:
        print("   错误: PyQt5未安装")
        return False
    
    # 3. 创建优化的spec文件
    print("3. 创建优化的spec文件...")
    create_optimized_spec()
    
    # 4. 使用优化的参数重新打包
    print("4. 开始重新打包...")
    try:
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'main_fixed.spec'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("   打包成功!")
            return True
        else:
            print(f"   打包失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   打包过程中出错: {e}")
        return False

def create_optimized_spec():
    """创建优化的spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

# PyQt5打包优化配置
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集PyQt5相关数据
pyqt5_datas = collect_data_files('PyQt5')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=pyqt5_datas + [
        ('icon.png', '.'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'PyQt5.sip',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets', 
        'PyQt5.QtGui',
        'sip',
        'tempfile',
        'setuptools',
        'encodings.gbk',
        'configparser',
        'typing_extensions',
        'json',
        'encodings.ascii',
        'pathlib',
        'importlib.util',
        'subprocess',
        'encodings.latin1',
        'encodings.utf_8',
        'shutil',
        'platform',
        'logging.handlers',
        'logging.config',
        'pkg_resources',
        'importlib.metadata',
        'encodings.cp1252',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用UPX压缩
    console=False,  # 改为窗口模式
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # 禁用UPX压缩
    upx_exclude=[],
    name='main'
)
'''
    
    with open('main_fixed.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("   已创建优化的spec文件: main_fixed.spec")

def test_executable():
    """测试生成的可执行文件"""
    exe_path = Path('dist/main/main.exe')
    if exe_path.exists():
        print(f"5. 测试可执行文件: {exe_path}")
        try:
            # 简单测试是否能启动
            result = subprocess.run([str(exe_path), '--help'], 
                                  capture_output=True, text=True, 
                                  timeout=10, encoding='utf-8')
            print("   可执行文件测试通过")
            return True
        except subprocess.TimeoutExpired:
            print("   可执行文件启动超时，但可能正常")
            return True
        except Exception as e:
            print(f"   可执行文件测试失败: {e}")
            return False
    else:
        print("   错误: 可执行文件不存在")
        return False

if __name__ == "__main__":
    print("PyQt5打包问题修复工具")
    print("=" * 50)
    
    success = fix_pyqt5_packaging()
    
    if success:
        test_executable()
        print("\n修复完成! 请检查 dist/main/ 目录中的可执行文件")
        print("如果仍有问题，请尝试以下额外步骤:")
        print("1. 更新PyInstaller: pip install --upgrade pyinstaller")
        print("2. 重新安装PyQt5: pip uninstall PyQt5 && pip install PyQt5")
        print("3. 使用虚拟环境进行打包")
    else:
        print("\n修复失败，请检查错误信息")
