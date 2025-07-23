#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖检查脚本
验证项目依赖是否正确安装
"""

import sys
import importlib
import subprocess
from typing import List, Tuple, Dict, Optional

def check_python_version() -> bool:
    """检查Python版本"""
    version = sys.version_info
    min_version = (3, 8)
    
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if (version.major, version.minor) >= min_version:
        print("✅ Python版本检查通过")
        return True
    else:
        print(f"❌ Python版本过低，需要 {min_version[0]}.{min_version[1]}+")
        return False

def check_package(package_name: str, import_name: Optional[str] = None) -> Tuple[bool, str]:
    """检查单个包是否安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'Unknown')
        return True, version
    except ImportError:
        return False, "Not installed"
    except Exception as e:
        return False, f"Error: {e}"

def get_package_info(package_name: str) -> Dict[str, str]:
    """获取包的详细信息"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package_name],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            return info
        return {}
    except Exception:
        return {}

def check_core_dependencies() -> bool:
    """检查核心依赖"""
    print("\n🔧 检查核心依赖...")
    
    core_packages = [
        ('PyQt5', 'PyQt5'),
        ('pyinstaller', 'PyInstaller'),
    ]
    
    all_ok = True
    for package_name, import_name in core_packages:
        is_installed, version = check_package(package_name, import_name)
        if is_installed:
            print(f"✅ {package_name}: {version}")
        else:
            print(f"❌ {package_name}: {version}")
            all_ok = False
    
    return all_ok

def check_required_dependencies() -> bool:
    """检查必需依赖"""
    print("\n📦 检查必需依赖...")
    
    required_packages = [
        ('importlib-metadata', 'importlib_metadata'),
        ('Pillow', 'PIL'),
        ('typing-extensions', 'typing_extensions'),
    ]
    
    all_ok = True
    for package_name, import_name in required_packages:
        is_installed, version = check_package(package_name, import_name)
        if is_installed:
            print(f"✅ {package_name}: {version}")
        else:
            print(f"⚠️  {package_name}: {version} (可选，但推荐安装)")
    
    return all_ok

def check_platform_dependencies() -> bool:
    """检查平台特定依赖"""
    print("\n🖥️  检查平台特定依赖...")
    
    if sys.platform == "win32":
        is_installed, version = check_package('pywin32', 'win32api')
        if is_installed:
            print(f"✅ pywin32: {version}")
            return True
        else:
            print(f"⚠️  pywin32: {version} (Windows平台推荐安装)")
            return False
    else:
        print("ℹ️  非Windows平台，无需特殊依赖")
        return True

def check_optional_dependencies() -> None:
    """检查可选依赖"""
    print("\n🔍 检查可选依赖...")
    
    optional_packages = [
        ('requests', 'requests'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('opencv-python', 'cv2'),
        ('setuptools', 'setuptools'),
    ]
    
    for package_name, import_name in optional_packages:
        is_installed, version = check_package(package_name, import_name)
        if is_installed:
            print(f"✅ {package_name}: {version}")
        else:
            print(f"➖ {package_name}: 未安装 (可选)")

def check_project_imports() -> bool:
    """检查项目模块导入"""
    print("\n🏗️  检查项目模块...")
    
    project_modules = [
        'config.app_config',
        'models.packer_model',
        'views.main_window',
        'controllers.main_controller',
        'services.package_service',
        'utils.logger',
    ]
    
    all_ok = True
    for module_name in project_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            all_ok = False
        except Exception as e:
            print(f"⚠️  {module_name}: {e}")
    
    return all_ok

def run_basic_functionality_test() -> bool:
    """运行基本功能测试"""
    print("\n🧪 运行基本功能测试...")
    
    try:
        # 测试PyQt5基本功能
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        
        app = QApplication([])
        print("✅ PyQt5应用程序创建成功")
        
        # 测试PyInstaller导入
        import PyInstaller
        print("✅ PyInstaller导入成功")
        
        # 测试项目核心模块
        from config.app_config import AppConfig
        config = AppConfig()
        print("✅ 项目配置模块加载成功")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def generate_report() -> None:
    """生成依赖检查报告"""
    print("\n📊 生成依赖检查报告...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list'],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            with open('dependency_check_report.txt', 'w', encoding='utf-8') as f:
                f.write("PyInstaller GUI 依赖检查报告\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Python版本: {sys.version}\n")
                f.write(f"Python路径: {sys.executable}\n\n")
                f.write("已安装的包:\n")
                f.write("-" * 30 + "\n")
                f.write(result.stdout)
            
            print("✅ 报告已保存到 dependency_check_report.txt")
        else:
            print("⚠️  无法生成完整报告")
            
    except Exception as e:
        print(f"⚠️  生成报告时出错: {e}")

def main():
    """主函数"""
    print("🔍 PyInstaller GUI 依赖检查工具")
    print("=" * 50)
    
    # 检查Python版本
    python_ok = check_python_version()
    
    # 检查各类依赖
    core_ok = check_core_dependencies()
    required_ok = check_required_dependencies()
    platform_ok = check_platform_dependencies()
    
    # 检查可选依赖
    check_optional_dependencies()
    
    # 检查项目模块
    project_ok = check_project_imports()
    
    # 运行基本功能测试
    functionality_ok = run_basic_functionality_test()
    
    # 生成报告
    generate_report()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 检查总结:")
    
    if python_ok and core_ok and project_ok and functionality_ok:
        print("🎉 所有检查通过！项目可以正常运行。")
        print("\n🚀 启动命令:")
        print("   python __init__.py")
        print("   或者: python run.py")
        return 0
    else:
        print("⚠️  发现问题，请根据上述信息修复依赖。")
        print("\n🔧 建议操作:")
        if not core_ok:
            print("   pip install -r requirements.txt")
        if not project_ok:
            print("   检查项目文件是否完整")
        return 1

if __name__ == "__main__":
    sys.exit(main())
