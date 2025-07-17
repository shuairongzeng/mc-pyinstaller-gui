#!/usr/bin/env python3
"""
调试脚本路径问题
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel

def debug_script_path():
    """调试脚本路径设置"""
    print("🔍 调试脚本路径问题")
    print("=" * 50)
    
    # 创建配置和模型
    config = AppConfig()
    model = PyInstallerModel(config)
    
    print(f"初始script_path: '{model.script_path}'")
    print(f"初始script_path为空: {model.script_path == ''}")
    print(f"初始script_path长度: {len(model.script_path)}")
    
    # 测试设置脚本路径
    test_script = "test_example.py"
    model.script_path = test_script
    print(f"\n设置后script_path: '{model.script_path}'")
    
    # 测试生成命令
    command = model.generate_command()
    print(f"\n生成的命令: {command}")
    
    if command:
        print(f"命令是否包含测试脚本: {test_script in command}")
        print(f"命令是否包含__init__.py: {'__init__.py' in command}")
    else:
        print("❌ 无法生成命令")
    
    # 测试空脚本路径
    model.script_path = ""
    command_empty = model.generate_command()
    print(f"\n空脚本路径时的命令: '{command_empty}'")
    
    # 检查配置文件
    print(f"\n配置文件路径: {config.config_file}")
    print(f"配置文件存在: {os.path.exists(config.config_file)}")
    
    if os.path.exists(config.config_file):
        try:
            import json
            with open(config.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            print(f"配置文件内容: {config_data}")
            
            if 'script_path' in config_data:
                print(f"⚠️  配置文件中包含script_path: {config_data['script_path']}")
            else:
                print("✅ 配置文件中没有script_path")
        except Exception as e:
            print(f"读取配置文件失败: {e}")
    
    print("\n" + "=" * 50)
    print("调试完成")

if __name__ == "__main__":
    debug_script_path()
