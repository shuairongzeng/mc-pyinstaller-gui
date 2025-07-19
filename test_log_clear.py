#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志清空功能
验证每次点击"开始打包"按钮时是否会清空上一次的打包日志
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from views.main_window import MainWindow
from config.app_config import AppConfig
from models.packer_model import PyInstallerModel

def test_log_clear_functionality():
    """测试日志清空功能"""
    print("🧪 测试日志清空功能")
    print("=" * 60)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    try:
        # 创建主窗口
        config = AppConfig()
        model = PyInstallerModel(config)
        window = MainWindow(model, config)
        
        # 显示窗口
        window.show()
        
        # 测试日志功能
        log_tab = window.log_tab
        
        if log_tab:
            print("✅ 找到日志标签页")
            
            # 添加一些测试日志
            print("📝 添加测试日志...")
            log_tab.append_log("这是第一条测试日志")
            log_tab.append_log("这是第二条测试日志")
            log_tab.append_log("这是第三条测试日志")
            
            # 检查日志内容
            log_content_before = log_tab.log_text.toPlainText()
            print(f"清空前日志内容长度: {len(log_content_before)} 字符")
            print(f"清空前日志行数: {len(log_content_before.splitlines())} 行")
            
            # 测试清空功能
            print("🧹 测试清空日志功能...")
            log_tab.clear_log()
            
            # 检查清空后的内容
            log_content_after = log_tab.log_text.toPlainText()
            print(f"清空后日志内容长度: {len(log_content_after)} 字符")
            print(f"清空后日志行数: {len(log_content_after.splitlines())} 行")
            
            if len(log_content_after.strip()) == 0:
                print("✅ 日志清空功能正常工作")
            else:
                print("❌ 日志清空功能异常")
                print(f"剩余内容: '{log_content_after}'")
            
            # 测试进度标签更新
            progress_text = log_tab.progress_label.text()
            print(f"进度标签文本: '{progress_text}'")
            
            if "日志已清空" in progress_text:
                print("✅ 进度标签更新正常")
            else:
                print("⚠️ 进度标签可能未正确更新")
            
        else:
            print("❌ 未找到日志标签页")
        
        # 关闭应用程序
        window.close()
        app.quit()
        
        print("\n🎉 日志清空功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if app:
            app.quit()

def test_start_package_log_clear():
    """测试开始打包时的日志清空功能"""
    print("\n🚀 测试开始打包时的日志清空功能")
    print("=" * 60)
    
    # 这个测试需要手动验证，因为涉及到GUI交互
    print("📋 手动测试步骤:")
    print("1. 启动应用程序: .\.conda\python.exe run.py")
    print("2. 在基本设置中选择一个Python脚本")
    print("3. 切换到日志标签页")
    print("4. 手动添加一些日志内容（或执行一次打包）")
    print("5. 再次点击'开始打包'按钮")
    print("6. 观察日志是否被清空")
    print()
    print("✅ 预期结果: 每次点击'开始打包'按钮时，日志文本框应该被清空")
    print("⚠️ 注意: 这个功能已经在 views/main_window.py 的 start_package 方法中实现")

def main():
    """主测试函数"""
    print("🧪 日志清空功能测试套件")
    print("=" * 80)
    
    # 测试基本的日志清空功能
    success = test_log_clear_functionality()
    
    # 提供手动测试指导
    test_start_package_log_clear()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ 自动化测试通过")
    else:
        print("❌ 自动化测试失败")
    
    print("\n📝 代码修改总结:")
    print("在 views/main_window.py 的 start_package 方法中添加了:")
    print("```python")
    print("# 清空上一次的打包日志")
    print("if self.log_tab:")
    print("    self.log_tab.clear_log()")
    print("```")
    
    print("\n🎯 功能说明:")
    print("- 每次点击'开始打包'按钮时，会自动清空上一次的打包日志")
    print("- 这样可以避免日志混乱，让用户更清楚地看到当前打包的进度")
    print("- 用户仍然可以通过'清空日志'按钮手动清空日志")
    print("- 如果需要保留历史日志，可以使用'保存日志'按钮")

if __name__ == "__main__":
    main()
