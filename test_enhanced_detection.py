#!/usr/bin/env python3
"""
测试增强的模块检测功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.module_detector import ModuleDetector

def create_test_script():
    """创建一个包含多种依赖的测试脚本"""
    test_script_content = '''#!/usr/bin/env python3
"""
测试脚本 - 包含多种常见依赖
"""

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from PIL import Image
import tkinter as tk
from tkinter import messagebox
import json
import configparser
import os
import sys

def main():
    """主函数"""
    # OpenCV操作
    img = cv2.imread("test.jpg")
    
    # numpy操作
    arr = np.array([1, 2, 3, 4, 5])
    
    # pandas操作
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    
    # matplotlib操作
    plt.plot([1, 2, 3], [4, 5, 6])
    plt.show()
    
    # requests操作
    response = requests.get("https://httpbin.org/get")
    
    # PIL操作
    image = Image.new("RGB", (100, 100), "red")
    
    # tkinter操作
    root = tk.Tk()
    messagebox.showinfo("测试", "这是一个测试")
    root.destroy()
    
    # 配置文件操作
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    print("所有模块测试完成")

if __name__ == "__main__":
    main()
'''
    
    with open("test_dependencies.py", "w", encoding="utf-8") as f:
        f.write(test_script_content)
    
    return "test_dependencies.py"

def test_enhanced_detection():
    """测试增强的模块检测功能"""
    print("🔍 测试增强的模块检测功能")
    print("=" * 60)
    
    # 创建测试脚本
    test_script = create_test_script()
    print(f"✅ 创建测试脚本: {test_script}")
    
    # 创建模块检测器
    detector = ModuleDetector(use_ast=True, use_pyinstaller=False)
    
    try:
        # 检测模块
        print(f"\n🔍 检测模块...")
        detected_modules = detector.detect_modules(test_script)
        print(f"检测到 {len(detected_modules)} 个模块:")
        for module in sorted(detected_modules):
            print(f"  - {module}")
        
        # 分析缺失模块
        print(f"\n🔍 分析模块依赖...")
        analysis = detector.analyze_missing_modules(test_script)
        
        print(f"\n📋 分析结果:")
        print(f"检测到的模块: {len(analysis['detected_modules'])}")
        print(f"缺失的模块: {len(analysis['missing_modules'])}")
        print(f"推荐的隐藏导入: {len(analysis['hidden_imports'])}")
        print(f"推荐的collect-all: {len(analysis['collect_all'])}")
        
        if analysis['missing_modules']:
            print(f"\n❌ 缺失的模块:")
            for module in analysis['missing_modules']:
                print(f"  - {module}")
        
        if analysis['collect_all']:
            print(f"\n📦 推荐的collect-all参数:")
            for module in analysis['collect_all']:
                print(f"  - --collect-all={module}")
        
        print(f"\n💡 建议:")
        for suggestion in analysis['suggestions']:
            print(f"  - {suggestion}")
        
        # 生成PyInstaller参数
        print(f"\n🚀 生成PyInstaller参数...")
        args = detector.generate_pyinstaller_args(test_script)
        print(f"生成了 {len(args)} 个参数:")
        
        # 按类型分组显示
        hidden_imports = [arg for arg in args if arg.startswith("--hidden-import=")]
        collect_alls = [arg for arg in args if arg.startswith("--collect-all=")]
        collect_data = [arg for arg in args if arg.startswith("--collect-data=")]
        collect_binaries = [arg for arg in args if arg.startswith("--collect-binaries=")]
        add_data = [arg for arg in args if arg.startswith("--add-data=")]
        
        if hidden_imports:
            print(f"\n🔒 隐藏导入 ({len(hidden_imports)} 个):")
            for arg in hidden_imports[:10]:  # 只显示前10个
                print(f"  {arg}")
            if len(hidden_imports) > 10:
                print(f"  ... 还有 {len(hidden_imports) - 10} 个")
        
        if collect_alls:
            print(f"\n📦 Collect-all ({len(collect_alls)} 个):")
            for arg in collect_alls:
                print(f"  {arg}")
        
        if collect_data:
            print(f"\n📄 Collect-data ({len(collect_data)} 个):")
            for arg in collect_data:
                print(f"  {arg}")
        
        if collect_binaries:
            print(f"\n🔧 Collect-binaries ({len(collect_binaries)} 个):")
            for arg in collect_binaries:
                print(f"  {arg}")
        
        if add_data:
            print(f"\n📁 Add-data ({len(add_data)} 个):")
            for arg in add_data:
                print(f"  {arg}")
        
        print(f"\n✅ 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        if os.path.exists(test_script):
            os.remove(test_script)
            print(f"🧹 清理测试文件: {test_script}")

if __name__ == "__main__":
    test_enhanced_detection()
