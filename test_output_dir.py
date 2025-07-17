#!/usr/bin/env python3
"""
测试输出目录处理
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel

def test_output_dir():
    """测试输出目录处理"""
    print("🔍 测试输出目录处理")
    print("=" * 50)
    
    # 创建配置和模型
    config = AppConfig()
    model = PyInstallerModel(config)
    
    print(f"默认输出目录: {model.output_dir}")
    print(f"是否为绝对路径: {os.path.isabs(model.output_dir)}")
    print(f"目录是否存在: {os.path.exists(model.output_dir)}")
    
    # 测试创建目录
    if not os.path.exists(model.output_dir):
        try:
            os.makedirs(model.output_dir, exist_ok=True)
            print(f"✅ 成功创建输出目录: {model.output_dir}")
        except Exception as e:
            print(f"❌ 创建输出目录失败: {e}")
    else:
        print(f"✅ 输出目录已存在: {model.output_dir}")
    
    # 测试绝对路径转换
    test_paths = ["./dist", "../output", "C:\\temp\\dist"]
    
    print(f"\n测试路径转换:")
    for path in test_paths:
        abs_path = os.path.abspath(path)
        print(f"  {path} -> {abs_path}")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_output_dir()
