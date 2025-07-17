#!/usr/bin/env python3
"""
PyInstaller打包问题自动修复脚本
解决打包后运行时缺少模块的问题
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """检查必要的依赖是否已安装"""
    print("🔍 检查依赖...")
    
    required_packages = [
        ('PyQt5', 'PyQt5'),
        ('pyinstaller', 'pyinstaller'),
        ('importlib_metadata', 'importlib-metadata'),
    ]
    
    missing_packages = []
    
    for package_name, pip_name in required_packages:
        try:
            __import__(package_name)
            print(f"✅ {package_name} 已安装")
        except ImportError:
            print(f"❌ {package_name} 未安装")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n📦 需要安装以下包: {', '.join(missing_packages)}")
        install = input("是否现在安装? (y/n): ").lower().strip()
        if install == 'y':
            for package in missing_packages:
                print(f"正在安装 {package}...")
                subprocess.run([sys.executable, "-m", "pip", "install", package])
        else:
            print("请手动安装缺失的依赖包")
            return False
    
    return True

def create_pyinstaller_hook():
    """创建PyInstaller hook文件来处理隐藏导入"""
    print("🔧 创建PyInstaller hook文件...")
    
    hook_content = '''"""
PyInstaller hook for this application
"""

hiddenimports = [
    # PyQt5 相关
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
    'setuptools',
    
    # 项目特定模块
    'config.app_config',
    'models.packer_model',
    'views.main_window',
    'controllers.main_controller',
    'services.package_service',
    'services.module_detector',
    'utils.logger',
    'utils.exceptions',
]

# 数据文件
datas = [
    ('config.json', '.'),
    ('icon.png', '.'),
    ('images', 'images'),
    ('templates', 'templates'),
]
'''
    
    hooks_dir = Path("hooks")
    hooks_dir.mkdir(exist_ok=True)
    
    hook_file = hooks_dir / "hook-__init__.py"
    with open(hook_file, 'w', encoding='utf-8') as f:
        f.write(hook_content)
    
    print(f"✅ Hook文件已创建: {hook_file}")
    return str(hooks_dir)

def generate_build_script():
    """生成优化的打包脚本"""
    print("📝 生成打包脚本...")
    
    hooks_dir = create_pyinstaller_hook()
    
    build_script = f'''#!/usr/bin/env python3
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
        "--additional-hooks-dir={hooks_dir}",
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
        print(f"❌ 打包失败: {{e}}")
        return False

if __name__ == "__main__":
    build_app()
'''
    
    with open("build_optimized.py", 'w', encoding='utf-8') as f:
        f.write(build_script)
    
    print("✅ 打包脚本已生成: build_optimized.py")

def main():
    """主函数"""
    print("🔧 PyInstaller打包问题自动修复工具")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 生成构建脚本
    generate_build_script()
    
    print("\n✅ 修复完成!")
    print("\n📋 使用说明:")
    print("1. 运行 'python build_optimized.py' 进行打包")
    print("2. 如果仍有问题，请检查 hooks/ 目录中的hook文件")
    print("3. 打包完成后，可执行文件在 dist/ 目录中")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
