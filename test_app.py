#!/usr/bin/env python3
"""
测试重构后的应用程序
"""
import sys
import os

def test_imports():
    """测试所有模块导入"""
    print("测试模块导入...")
    
    try:
        from config.app_config import AppConfig
        print("✅ config.app_config 导入成功")
        
        from models.packer_model import PyInstallerModel
        print("✅ models.packer_model 导入成功")
        
        from services.package_service import PackageService, PyInstallerChecker
        print("✅ services.package_service 导入成功")
        
        from services.module_detector import ModuleDetector
        print("✅ services.module_detector 导入成功")
        
        from controllers.main_controller import MainController
        print("✅ controllers.main_controller 导入成功")
        
        from utils.logger import log_info, log_error, log_exception
        print("✅ utils.logger 导入成功")
        
        from utils.exceptions import PyInstallerGUIException
        print("✅ utils.exceptions 导入成功")
        
        # 测试视图组件
        from views.main_window import MainWindow
        print("✅ views.main_window 导入成功")
        
        from views.menu_bar import MenuBarManager
        print("✅ views.menu_bar 导入成功")
        
        from views.tabs.basic_tab import BasicTab
        print("✅ views.tabs.basic_tab 导入成功")
        
        from views.tabs.advanced_tab import AdvancedTab
        print("✅ views.tabs.advanced_tab 导入成功")
        
        from views.tabs.module_tab import ModuleTab
        print("✅ views.tabs.module_tab 导入成功")
        
        from views.tabs.settings_tab import SettingsTab
        print("✅ views.tabs.settings_tab 导入成功")
        
        from views.tabs.log_tab import LogTab
        print("✅ views.tabs.log_tab 导入成功")
        
        print("\n🎉 所有模块导入测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config():
    """测试配置系统"""
    print("\n测试配置系统...")
    
    try:
        from config.app_config import AppConfig
        
        config = AppConfig()
        print(f"✅ 应用名称: {config.APP_NAME}")
        print(f"✅ 应用版本: {config.APP_VERSION}")
        print(f"✅ 应用作者: {config.APP_AUTHOR}")
        
        # 测试配置读写
        config.set("test_key", "test_value")
        value = config.get("test_key")
        assert value == "test_value", "配置读写测试失败"
        print("✅ 配置读写测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置系统测试失败: {e}")
        return False

def test_model():
    """测试模型层"""
    print("\n测试模型层...")
    
    try:
        from config.app_config import AppConfig
        from models.packer_model import PyInstallerModel
        
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 测试基本属性
        model.script_path = "test.py"
        model.output_dir = "./dist"
        model.is_one_file = True
        
        print("✅ 模型属性设置成功")
        
        # 测试配置验证
        errors = model.validate_config()
        print(f"✅ 配置验证功能正常，发现 {len(errors)} 个错误")
        
        # 测试字典转换
        config_dict = model.to_dict()
        print("✅ 模型转字典功能正常")
        
        model.from_dict(config_dict)
        print("✅ 字典转模型功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型层测试失败: {e}")
        return False

def test_services():
    """测试服务层"""
    print("\n测试服务层...")
    
    try:
        from services.package_service import PyInstallerChecker
        from services.module_detector import ModuleDetector
        
        # 测试PyInstaller检查
        is_installed = PyInstallerChecker.check_pyinstaller()
        print(f"✅ PyInstaller安装状态: {'已安装' if is_installed else '未安装'}")
        
        # 测试模块检测器
        detector = ModuleDetector()
        print("✅ 模块检测器创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务层测试失败: {e}")
        return False

def test_logger():
    """测试日志系统"""
    print("\n测试日志系统...")
    
    try:
        from utils.logger import log_info, log_error, log_warning
        
        log_info("这是一条测试信息")
        log_warning("这是一条测试警告")
        log_error("这是一条测试错误")
        
        print("✅ 日志系统测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 日志系统测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("PyInstaller打包工具 - 重构测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_model,
        test_services,
        test_logger,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！重构成功！")
        return 0
    else:
        print("❌ 部分测试失败，需要修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
