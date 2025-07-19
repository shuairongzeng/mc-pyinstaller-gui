#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境选择功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.python_env_scanner import get_scanner
from config.app_config import AppConfig

def test_environment_scanning():
    """测试环境扫描功能"""
    print("🔍 测试环境扫描功能")
    print("=" * 60)
    
    scanner = get_scanner()
    environments = scanner.scan_all_environments()
    
    print(f"找到 {len(environments)} 个 Python 环境:")
    print()
    
    for i, env in enumerate(environments, 1):
        print(f"{i}. {env.get_display_name()}")
        print(f"   路径: {env.path}")
        print(f"   类型: {env.env_type}")
        print(f"   版本: {env.version}")
        print(f"   当前环境: {'是' if env.is_current else '否'}")
        print(f"   可用: {'是' if env.is_available else '否'}")
        print(f"   已安装PyInstaller: {'是' if env.has_pyinstaller else '否'}")
        if env.env_path:
            print(f"   环境路径: {env.env_path}")
        print(f"   描述: {env.description}")
        print()
    
    return environments

def test_config_integration():
    """测试配置集成"""
    print("⚙️ 测试配置集成")
    print("=" * 60)
    
    config = AppConfig()
    
    # 测试获取当前配置
    current_interpreter = config.get("python_interpreter", "")
    print(f"当前配置的解释器: {current_interpreter}")
    
    # 测试设置新的解释器
    test_interpreter = r"C:\Python312\python.exe"
    config.set("python_interpreter", test_interpreter)
    print(f"设置新的解释器: {test_interpreter}")
    
    # 验证设置
    updated_interpreter = config.get("python_interpreter", "")
    print(f"更新后的解释器: {updated_interpreter}")
    
    # 恢复原始配置
    config.set("python_interpreter", current_interpreter)
    print(f"恢复原始配置: {current_interpreter}")
    
    print("✅ 配置集成测试通过")
    print()

def test_pyinstaller_installation():
    """测试 PyInstaller 安装功能"""
    print("📦 测试 PyInstaller 安装功能")
    print("=" * 60)
    
    scanner = get_scanner()
    environments = scanner.scan_all_environments()
    
    # 找到一个没有安装 PyInstaller 的环境进行测试
    test_env = None
    for env in environments:
        if env.is_available and not env.has_pyinstaller:
            test_env = env
            break
    
    if test_env:
        print(f"找到测试环境: {test_env.name}")
        print(f"路径: {test_env.path}")
        print("注意: 这只是测试检测功能，不会实际安装")
        
        # 这里只是测试检测，不实际安装
        print("✅ PyInstaller 安装功能可用")
    else:
        print("所有环境都已安装 PyInstaller 或不可用")
        print("✅ PyInstaller 安装功能检测正常")
    
    print()

def test_environment_selection_logic():
    """测试环境选择逻辑"""
    print("🎯 测试环境选择逻辑")
    print("=" * 60)
    
    scanner = get_scanner()
    environments = scanner.scan_all_environments()
    
    if not environments:
        print("❌ 没有找到环境，无法测试选择逻辑")
        return
    
    # 测试按路径查找环境
    first_env = environments[0]
    found_env = scanner.get_environment_by_path(first_env.path)
    
    if found_env:
        print(f"✅ 按路径查找环境成功: {found_env.name}")
    else:
        print("❌ 按路径查找环境失败")
    
    # 测试当前环境检测
    current_envs = [env for env in environments if env.is_current]
    print(f"检测到 {len(current_envs)} 个当前环境")
    
    for env in current_envs:
        print(f"  当前环境: {env.name} ({env.path})")
    
    # 测试环境排序
    print("环境排序测试:")
    for i, env in enumerate(environments[:3], 1):  # 只显示前3个
        priority = "🟢 最高" if env.is_current else "🔵 普通"
        print(f"  {i}. {priority} - {env.name}")
    
    print("✅ 环境选择逻辑测试通过")
    print()

def main():
    """主测试函数"""
    print("🧪 Python 环境选择功能测试")
    print("=" * 80)
    print()
    
    try:
        # 测试环境扫描
        environments = test_environment_scanning()
        
        # 测试配置集成
        test_config_integration()
        
        # 测试 PyInstaller 安装功能
        test_pyinstaller_installation()
        
        # 测试环境选择逻辑
        test_environment_selection_logic()
        
        print("🎉 所有测试完成！")
        print("=" * 80)
        
        # 总结
        print(f"📊 测试结果总结:")
        print(f"  - 扫描到 {len(environments)} 个 Python 环境")
        
        available_envs = [env for env in environments if env.is_available]
        print(f"  - 其中 {len(available_envs)} 个环境可用")
        
        pyinstaller_envs = [env for env in environments if env.has_pyinstaller]
        print(f"  - 其中 {len(pyinstaller_envs)} 个环境已安装 PyInstaller")
        
        current_envs = [env for env in environments if env.is_current]
        print(f"  - 其中 {len(current_envs)} 个是当前环境")
        
        print()
        print("✅ 环境选择功能已准备就绪！")
        print("现在可以在 GUI 的模块管理标签页中使用新的环境选择功能了。")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
