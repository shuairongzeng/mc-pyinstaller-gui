#!/usr/bin/env python3
"""
专门修复PyQt5 DLL提取失败问题的脚本
解决: Failed to extract PyQt5\Qt5\bin\Qt5Gui.dll: decompression resulted in return code -1!
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

def fix_pyqt5_dll_issue():
    """修复PyQt5 DLL提取失败问题"""
    print("🔧 开始修复PyQt5 DLL提取失败问题...")
    print("=" * 60)
    
    # 1. 清理之前的构建文件
    print("1. 清理构建文件...")
    cleanup_build_files()
    
    # 2. 检查PyQt5环境
    print("2. 检查PyQt5环境...")
    if not check_pyqt5_environment():
        return False
    
    # 3. 创建PyQt5专用的spec文件
    print("3. 创建PyQt5专用配置...")
    create_pyqt5_spec()
    
    # 4. 使用修复后的参数重新打包
    print("4. 使用修复参数重新打包...")
    return repackage_with_fix()

def cleanup_build_files():
    """清理构建文件"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"   ✅ 已清理: {dir_name}")
            except Exception as e:
                print(f"   ⚠️ 清理失败 {dir_name}: {e}")
    
    # 清理spec文件
    for spec_file in Path('.').glob('*.spec'):
        try:
            spec_file.unlink()
            print(f"   ✅ 已删除: {spec_file}")
        except Exception as e:
            print(f"   ⚠️ 删除失败 {spec_file}: {e}")

def check_pyqt5_environment():
    """检查PyQt5环境"""
    # 使用目标Python环境检查PyQt5
    python_exe = r'D:\software\anaconda3\envs\paddleEnv\python.exe'

    try:
        # 检查PyQt5版本
        result = subprocess.run([
            python_exe, '-c',
            'from PyQt5 import QtCore; print(f"PyQt5版本: {QtCore.PYQT_VERSION_STR}"); print(f"Qt版本: {QtCore.QT_VERSION_STR}")'
        ], capture_output=True, text=True, check=True)

        print("   ✅ " + result.stdout.strip().replace('\n', '\n   ✅ '))

        # 检查关键模块
        modules = ['QtCore', 'QtWidgets', 'QtGui']
        for module in modules:
            try:
                result = subprocess.run([
                    python_exe, '-c', f'from PyQt5 import {module}; print("{module} 可用")'
                ], capture_output=True, text=True, check=True)
                print(f"   ✅ {result.stdout.strip()}")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ {module} 不可用: {e}")
                return False

        return True

    except subprocess.CalledProcessError as e:
        print(f"   ❌ PyQt5检查失败: {e}")
        return False

def create_pyqt5_spec():
    """创建PyQt5专用的spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
"""
PyQt5 DLL问题修复专用spec文件
解决: Failed to extract PyQt5\\Qt5\\bin\\Qt5Gui.dll 问题
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# 脚本路径
script_path = r'D:\\python\\yolov8\\ultralytics-main\\myTrain.py'
script_dir = os.path.dirname(script_path)

# 收集PyQt5相关文件
print("正在收集PyQt5文件...")
pyqt5_datas = collect_data_files('PyQt5', include_py_files=False)
pyqt5_binaries = collect_dynamic_libs('PyQt5')

print(f"收集到 {len(pyqt5_datas)} 个PyQt5数据文件")
print(f"收集到 {len(pyqt5_binaries)} 个PyQt5二进制文件")

# 隐藏导入模块
hiddenimports = [
    # PyQt5核心模块
    'PyQt5.sip',
    'sip',
    'PyQt5.QtCore',
    'PyQt5.QtWidgets', 
    'PyQt5.QtGui',
    
    # 系统模块
    'platform',
    'subprocess',
    'shutil',
    'tempfile',
    'pathlib',
    
    # 编码模块
    'encodings.utf_8',
    'encodings.cp1252',
    'encodings.ascii',
    'encodings.latin1',
    'encodings.gbk',
    
    # XML解析器
    'xml.parsers.expat',
    'xml.etree.ElementTree',
    'xml.etree.cElementTree',
    'pyexpat',
    '_elementtree',
    'plistlib',
    
    # 其他必需模块
    'json',
    'configparser',
    'logging.handlers',
    'logging.config',
    'typing_extensions',
    'importlib.util',
    'importlib.metadata',
    'pkg_resources',
    'setuptools',
]

# 数据文件
datas = []
datas.extend(pyqt5_datas)

# 二进制文件
binaries = []
binaries.extend(pyqt5_binaries)

# 添加关键DLL文件
def add_critical_dlls():
    """添加关键DLL文件"""
    critical_dlls = []
    
    # 检查conda环境
    if hasattr(sys, 'prefix'):
        dll_names = [
            'liblzma.dll',
            'sqlite3.dll',
            'libexpat.dll',
            'expat.dll',
        ]
        
        search_paths = [
            os.path.join(sys.prefix, 'Library', 'bin'),
            os.path.join(sys.prefix, 'DLLs'),
        ]
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                for dll_name in dll_names:
                    dll_path = os.path.join(search_path, dll_name)
                    if os.path.exists(dll_path):
                        critical_dlls.append((dll_path, '.'))
                        print(f"添加关键DLL: {dll_name}")
    
    return critical_dlls

binaries.extend(add_critical_dlls())

# 分析脚本
a = Analysis(
    [script_path],
    pathex=[script_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 使用目录模式，避免单文件模式的DLL提取问题
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # 关键：排除二进制文件，使用目录模式
    name='yolo打包测试1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 关键：禁用UPX压缩
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'C:\\Users\\Administrator\\PycharmProjects\\PythonTuSe\\kwMusic.png',
)

# 创建目录分发
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # 关键：禁用UPX压缩
    upx_exclude=[],
    name='yolo打包测试1'
)
'''
    
    with open('pyqt5_fixed.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("   ✅ 已创建PyQt5专用spec文件: pyqt5_fixed.spec")

def repackage_with_fix():
    """使用修复参数重新打包"""
    try:
        # 设置工作目录
        work_dir = r'D:\python\yolov8\ultralytics-main'

        # 复制spec文件到工作目录
        spec_source = os.path.join(os.getcwd(), 'pyqt5_fixed.spec')
        spec_target = os.path.join(work_dir, 'pyqt5_fixed.spec')

        if os.path.exists(spec_source):
            shutil.copy2(spec_source, spec_target)
            print(f"   ✅ 已复制spec文件到: {spec_target}")

        # 使用目标环境的Python和spec文件打包
        python_exe = r'D:\software\anaconda3\envs\paddleEnv\python.exe'
        cmd = [
            python_exe, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--distpath=D:\\CustomGit\\mc-pyinstaller-gui\\dist',
            'pyqt5_fixed.spec'
        ]

        print("执行命令:")
        print(" ".join(cmd))
        print("-" * 60)

        # 执行打包
        result = subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=False,  # 显示实时输出
            text=True
        )
        
        if result.returncode == 0:
            print("=" * 60)
            print("🎉 打包成功!")
            print("📁 输出目录: D:\\CustomGit\\mc-pyinstaller-gui\\dist\\yolo打包测试1\\")
            print("🚀 可执行文件: yolo打包测试1.exe")
            return True
        else:
            print("=" * 60)
            print("❌ 打包失败")
            return False
            
    except Exception as e:
        print(f"❌ 打包过程中出错: {e}")
        return False

if __name__ == "__main__":
    success = fix_pyqt5_dll_issue()
    if success:
        print("\n🎉 修复完成！请测试打包后的程序。")
    else:
        print("\n❌ 修复失败，请检查错误信息。")
