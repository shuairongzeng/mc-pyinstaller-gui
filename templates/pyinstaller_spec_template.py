# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec文件模板
用于更精确地控制打包过程和依赖收集
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 获取脚本目录
script_dir = os.path.dirname(os.path.abspath(SPECPATH))

# 分析配置
block_cipher = None

# 隐藏导入 - 这些模块在运行时需要但PyInstaller可能检测不到
hiddenimports = [
    # PyQt5 核心模块
    'PyQt5.sip',
    'sip',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    
    # 系统模块
    'platform',
    'subprocess',
    'shutil',
    'tempfile',
    'pathlib',
    'os.path',
    
    # 编码模块
    'encodings.utf_8',
    'encodings.cp1252',
    'encodings.ascii',
    'encodings.latin1',
    'encodings.gbk',
    
    # JSON和配置
    'json',
    'configparser',
    
    # 日志模块
    'logging.handlers',
    'logging.config',
    
    # 类型检查
    'typing_extensions',
    
    # 导入工具
    'importlib.util',
    'importlib.metadata',
    'pkg_resources',
    
    # 常见第三方库
    'setuptools',
]

# 数据文件收集
datas = [
    # 配置文件
    ('config.json', '.'),
    # 图标文件
    ('icon.png', '.'),
    # 其他资源文件
    ('images', 'images'),
]

# 二进制文件收集（如果需要）
binaries = []

# 排除的模块
excludes = [
    # 开发工具
    'pytest',
    'unittest',
    'doctest',
    
    # 不需要的GUI框架
    'tkinter',
    'matplotlib',
    
    # 大型库（如果不需要）
    'numpy',
    'pandas',
    'scipy',
]

# 分析主脚本
a = Analysis(
    ['{{SCRIPT_PATH}}'],  # 将被替换为实际脚本路径
    pathex=[script_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 处理PYZ文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{{APP_NAME}}',  # 将被替换为实际应用名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx={{UPX_ENABLED}},  # 将被替换为UPX设置
    upx_exclude=[],
    runtime_tmpdir=None,
    console={{CONSOLE_MODE}},  # 将被替换为控制台模式设置
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{{ICON_PATH}}',  # 将被替换为图标路径
)

# 如果是目录模式，创建COLLECT
{{COLLECT_SECTION}}
