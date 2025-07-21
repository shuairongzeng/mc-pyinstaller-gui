#!/usr/bin/env python3
"""
测试集成后的智能依赖检测功能
"""

import sys
import os
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel

def create_test_script():
    """创建测试脚本"""
    test_script_content = '''#!/usr/bin/env python3
"""
集成测试脚本
"""

import os
import sys
import json
import configparser

# 尝试导入一些库
try:
    import numpy as np
    import pandas as pd
except ImportError:
    pass

try:
    import requests
except ImportError:
    pass

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QThread
except ImportError:
    pass

def main():
    """主函数"""
    print("集成测试脚本运行中...")
    
    # 基本操作
    data = {"test": "integration"}
    json_str = json.dumps(data)
    print(f"JSON数据: {json_str}")
    
    # 配置文件操作
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'mode': 'test'}
    
    print("集成测试完成")

if __name__ == "__main__":
    main()
'''
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_script_content)
        return f.name

def test_integrated_detection():
    """测试集成后的智能依赖检测功能"""
    print("🚀 测试集成后的智能依赖检测功能")
    print("=" * 70)
    
    # 创建测试脚本
    test_script = create_test_script()
    print(f"✅ 创建集成测试脚本: {test_script}")
    
    try:
        # 创建配置和模型
        print(f"\n🔧 初始化配置和模型...")
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 设置脚本路径
        model.script_path = test_script
        model.output_dir = "./test_dist"
        model.is_one_file = True
        model.is_windowed = False
        
        print(f"  - 脚本路径: {model.script_path}")
        print(f"  - 输出目录: {model.output_dir}")
        print(f"  - 单文件模式: {model.is_one_file}")
        
        # 验证配置
        print(f"\n🔍 验证配置...")
        errors = model.validate_config()
        if errors:
            print(f"  ❌ 配置错误:")
            for error in errors:
                print(f"    - {error}")
        else:
            print(f"  ✅ 配置验证通过")
        
        # 生成命令
        print(f"\n🚀 生成PyInstaller命令...")
        command = model.generate_command()
        
        if command:
            print(f"  ✅ 命令生成成功")
            print(f"  📝 命令长度: {len(command)} 字符")
            
            # 分析命令参数
            args = command.split()
            print(f"  📊 参数统计:")
            print(f"    - 总参数数量: {len(args)}")
            
            # 统计不同类型的参数
            hidden_imports = [arg for arg in args if arg.startswith("--hidden-import=")]
            collect_alls = [arg for arg in args if arg.startswith("--collect-all=")]
            collect_data = [arg for arg in args if arg.startswith("--collect-data=")]
            add_data = [arg for arg in args if arg.startswith("--add-data=")]
            
            print(f"    - 隐藏导入: {len(hidden_imports)} 个")
            print(f"    - Collect-all: {len(collect_alls)} 个")
            print(f"    - Collect-data: {len(collect_data)} 个")
            print(f"    - Add-data: {len(add_data)} 个")
            
            # 显示关键参数
            if hidden_imports:
                print(f"\n🔒 隐藏导入参数:")
                for arg in hidden_imports[:5]:  # 只显示前5个
                    print(f"    {arg}")
                if len(hidden_imports) > 5:
                    print(f"    ... 还有 {len(hidden_imports) - 5} 个")
            
            if collect_alls:
                print(f"\n📦 Collect-all参数:")
                for arg in collect_alls:
                    print(f"    {arg}")
            
            if collect_data:
                print(f"\n📄 Collect-data参数:")
                for arg in collect_data:
                    print(f"    {arg}")
            
            if add_data:
                print(f"\n📁 Add-data参数:")
                for arg in add_data:
                    print(f"    {arg}")
            
            # 显示完整命令（截断显示）
            print(f"\n📋 生成的完整命令:")
            if len(command) > 200:
                print(f"  {command[:200]}...")
                print(f"  ... (命令太长，已截断)")
            else:
                print(f"  {command}")
        else:
            print(f"  ❌ 命令生成失败")
        
        # 测试字典转换
        print(f"\n🔄 测试配置序列化...")
        config_dict = model.to_dict()
        print(f"  ✅ 配置转换为字典成功，包含 {len(config_dict)} 个字段")
        
        # 测试从字典加载
        new_model = PyInstallerModel(config)
        new_model.from_dict(config_dict)
        print(f"  ✅ 从字典加载配置成功")
        
        # 验证加载的配置
        if new_model.script_path == model.script_path:
            print(f"  ✅ 配置加载验证通过")
        else:
            print(f"  ❌ 配置加载验证失败")
        
        print(f"\n✅ 集成测试完成！")
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_script):
                os.remove(test_script)
                print(f"🧹 清理测试文件: {test_script}")
                
        except Exception as e:
            print(f"⚠️  清理文件时出错: {e}")

def test_performance_comparison():
    """测试性能对比"""
    print(f"\n⚡ 性能对比测试")
    print("-" * 40)
    
    # 创建测试脚本
    test_script = create_test_script()
    
    try:
        import time
        
        # 测试原始检测器
        print(f"🔍 测试原始模块检测器...")
        try:
            from services.module_detector import ModuleDetector
            
            start_time = time.time()
            detector = ModuleDetector(use_ast=True, use_pyinstaller=False)
            modules = detector.detect_modules(test_script)
            original_time = time.time() - start_time
            
            print(f"  - 检测时间: {original_time:.3f}s")
            print(f"  - 检测到模块: {len(modules)} 个")
            
        except Exception as e:
            print(f"  ❌ 原始检测器测试失败: {e}")
            original_time = 0
        
        # 测试增强检测器
        print(f"🚀 测试增强模块检测器...")
        try:
            from services.enhanced_module_detector import EnhancedModuleDetector
            
            start_time = time.time()
            detector = EnhancedModuleDetector(cache_dir=".perf_test_cache", max_workers=2)
            result = detector.detect_modules_with_cache(test_script)
            enhanced_time = time.time() - start_time
            
            print(f"  - 检测时间: {enhanced_time:.3f}s")
            print(f"  - 检测到模块: {len(result.detected_modules)} 个")
            print(f"  - 缓存命中: {'是' if result.cache_hit else '否'}")
            
            # 测试缓存性能
            start_time = time.time()
            cached_result = detector.detect_modules_with_cache(test_script)
            cache_time = time.time() - start_time
            
            print(f"  - 缓存检测时间: {cache_time:.3f}s")
            print(f"  - 缓存命中: {'是' if cached_result.cache_hit else '否'}")
            
            if enhanced_time > 0 and cache_time > 0:
                print(f"  - 缓存性能提升: {((enhanced_time - cache_time) / enhanced_time * 100):.1f}%")
            
        except Exception as e:
            print(f"  ❌ 增强检测器测试失败: {e}")
            enhanced_time = 0
        
        # 性能对比
        if original_time > 0 and enhanced_time > 0:
            if enhanced_time < original_time:
                improvement = ((original_time - enhanced_time) / original_time * 100)
                print(f"  🎯 增强检测器比原始检测器快 {improvement:.1f}%")
            else:
                degradation = ((enhanced_time - original_time) / original_time * 100)
                print(f"  ⚠️  增强检测器比原始检测器慢 {degradation:.1f}%")
        
    except Exception as e:
        print(f"❌ 性能对比测试失败: {e}")
    
    finally:
        # 清理
        try:
            if os.path.exists(test_script):
                os.remove(test_script)
            
            import shutil
            if os.path.exists('.perf_test_cache'):
                shutil.rmtree('.perf_test_cache')
        except Exception:
            pass

if __name__ == "__main__":
    test_integrated_detection()
    test_performance_comparison()
