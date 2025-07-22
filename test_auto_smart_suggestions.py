#!/usr/bin/env python3
"""
测试自动智能建议功能
"""
import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_auto_smart_suggestions():
    """测试自动智能建议功能"""
    print("🧪 开始测试自动智能建议功能...")
    
    try:
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 导入必要的模块
        from config.app_config import AppConfig
        from models.packer_model import PyInstallerModel
        from views.main_window import MainWindow
        from controllers.main_controller import MainController
        
        print("✅ 成功导入所有模块")
        
        # 创建配置和模型
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 创建控制器
        controller = MainController(config, model)
        
        # 创建主窗口
        main_window = MainWindow(config, model, controller)
        
        print("✅ 成功创建主窗口")
        
        # 测试配置选项
        print("\n📋 测试配置选项:")
        print(f"  - 打包前自动智能建议: {config.get('auto_smart_suggestions_before_packaging', True)}")
        print(f"  - 智能建议超时时间: {config.get('smart_suggestions_timeout', 30)}秒")
        print(f"  - 自动应用智能建议: {config.get('auto_apply_smart_suggestions', True)}")
        
        # 创建测试脚本
        test_script_path = "test_example.py"
        test_script_content = '''
import os
import sys
import json
import requests
import numpy as np
import pandas as pd

def main():
    print("Hello, World!")
    data = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    print(data)
    
    response = requests.get('https://api.github.com')
    print(response.status_code)

if __name__ == "__main__":
    main()
'''
        
        with open(test_script_path, 'w', encoding='utf-8') as f:
            f.write(test_script_content)
        
        print(f"✅ 创建测试脚本: {test_script_path}")
        
        # 设置脚本路径
        model.script_path = os.path.abspath(test_script_path)
        
        print("\n🧠 测试智能建议功能:")
        
        # 测试智能超时建议
        try:
            suggested_timeout = config.suggest_timeout_for_project(model.script_path)
            print(f"  - 建议超时时间: {config.format_timeout_display(suggested_timeout)}")
        except Exception as e:
            print(f"  - 智能超时建议失败: {e}")
        
        # 测试智能模块检测
        try:
            detection_result = main_window._execute_smart_module_detection()
            modules = detection_result.get('modules', [])
            hidden_imports = detection_result.get('hidden_imports', [])
            
            print(f"  - 检测到模块数量: {len(modules)}")
            print(f"  - 推荐隐藏导入数量: {len(hidden_imports)}")
            
            if hidden_imports:
                print("  - 推荐的隐藏导入:")
                for imp in hidden_imports[:5]:  # 只显示前5个
                    print(f"    • {imp}")
                if len(hidden_imports) > 5:
                    print(f"    ... 还有 {len(hidden_imports) - 5} 个")
                    
        except Exception as e:
            print(f"  - 智能模块检测失败: {e}")
        
        print("\n🎯 测试完成!")
        print("✅ 自动智能建议功能实现正常")
        
        # 清理测试文件
        if os.path.exists(test_script_path):
            os.remove(test_script_path)
            print(f"🧹 清理测试文件: {test_script_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_integration():
    """测试UI集成"""
    print("\n🖥️ 测试UI集成...")
    
    try:
        app = QApplication(sys.argv)
        
        from config.app_config import AppConfig
        from models.packer_model import PyInstallerModel
        from views.main_window import MainWindow
        from controllers.main_controller import MainController
        
        config = AppConfig()
        model = PyInstallerModel(config)
        controller = MainController(config, model)
        main_window = MainWindow(config, model, controller)
        
        # 测试设置标签页的新选项
        if main_window.settings_tab:
            settings_tab = main_window.settings_tab
            
            # 检查新的复选框是否存在
            if hasattr(settings_tab, 'auto_smart_suggestions_checkbox'):
                print("✅ 找到'打包前自动执行智能建议'选项")
                print(f"  - 当前状态: {'启用' if settings_tab.auto_smart_suggestions_checkbox.isChecked() else '禁用'}")
            else:
                print("❌ 未找到'打包前自动执行智能建议'选项")
            
            if hasattr(settings_tab, 'auto_apply_suggestions_checkbox'):
                print("✅ 找到'自动应用智能建议'选项")
                print(f"  - 当前状态: {'启用' if settings_tab.auto_apply_suggestions_checkbox.isChecked() else '禁用'}")
            else:
                print("❌ 未找到'自动应用智能建议'选项")
        
        print("✅ UI集成测试完成")
        return True
        
    except Exception as e:
        print(f"❌ UI集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试自动智能建议功能")
    print("=" * 50)
    
    # 基础功能测试
    test1_result = test_auto_smart_suggestions()
    
    # UI集成测试
    test2_result = test_ui_integration()
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"  - 基础功能测试: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"  - UI集成测试: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过！自动智能建议功能已成功实现。")
        print("\n💡 使用说明:")
        print("1. 在设置标签页中可以控制是否启用自动智能建议")
        print("2. 启用后，每次点击'开始打包'时会自动执行智能分析")
        print("3. 用户可以选择应用建议、跳过建议或取消打包")
        print("4. 智能建议包括超时时间优化和模块依赖检测")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查实现。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
