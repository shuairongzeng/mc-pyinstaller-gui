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

    # XML 解析器相关（解决 pyexpat 问题）
    'xml.parsers.expat',
    'xml.etree.ElementTree',
    'xml.etree.cElementTree',
    'pyexpat',
    '_elementtree',
    'plistlib',

    # 邮件和MIME类型
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'email.mime.base',

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

# 二进制文件收集（自动检测关键DLL）
binaries = []

# 自动添加关键的DLL文件（解决常见的conda环境问题）
def add_critical_dlls():
    """添加关键的DLL文件到二进制列表"""
    import sys
    import os

    critical_dlls = []

    # 检查是否在conda环境中
    if hasattr(sys, 'prefix'):
        # 常见的关键DLL文件
        dll_names = [
            'libexpat.dll',     # XML解析器
            'expat.dll',        # XML解析器备用
            'liblzma.dll',      # LZMA压缩
            'LIBBZ2.dll',       # BZ2压缩
            'ffi.dll',          # FFI库
            'libffi.dll',       # FFI库备用
            'sqlite3.dll',      # SQLite数据库
            'libssl.dll',       # SSL库
            'libcrypto.dll',    # 加密库
        ]

        # 搜索路径
        search_paths = [
            os.path.join(sys.prefix, 'Library', 'bin'),  # conda环境
            os.path.join(sys.prefix, 'DLLs'),            # Python DLLs
            os.path.join(sys.prefix, 'bin'),             # 通用bin目录
        ]

        for search_path in search_paths:
            if os.path.exists(search_path):
                for dll_name in dll_names:
                    dll_path = os.path.join(search_path, dll_name)
                    if os.path.exists(dll_path):
                        critical_dlls.append((dll_path, '.'))
                        print(f"✅ 找到关键DLL: {dll_name}")

    return critical_dlls

# 添加关键DLL到二进制列表
binaries.extend(add_critical_dlls())

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
