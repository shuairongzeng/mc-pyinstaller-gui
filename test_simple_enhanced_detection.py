#!/usr/bin/env python3
"""
简化的增强依赖检测测试
"""

import sys
import os
import time
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_simple_test_script():
    """创建一个简单的测试脚本"""
    test_script_content = '''#!/usr/bin/env python3
"""
简单测试脚本
"""

import os
import sys
import json
import configparser
import subprocess

# 尝试导入一些常见库
try:
    import numpy as np
except ImportError:
    pass

try:
    import requests
except ImportError:
    pass

try:
    from PyQt5.QtWidgets import QApplication
except ImportError:
    pass

def main():
    """主函数"""
    print("简单测试脚本运行中...")
    
    # 基本操作
    data = {"test": "data"}
    json_str = json.dumps(data)
    print(f"JSON数据: {json_str}")
    
    # 配置文件操作
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'debug': 'True'}
    
    print("测试完成")

if __name__ == "__main__":
    main()
'''
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_script_content)
        return f.name

def test_basic_detection():
    """测试基本的模块检测功能"""
    print("🚀 测试基本的智能依赖检测功能")
    print("=" * 60)
    
    # 创建测试脚本
    test_script = create_simple_test_script()
    print(f"✅ 创建简单测试脚本: {test_script}")
    
    try:
        # 导入增强的模块检测器
        from services.enhanced_module_detector import EnhancedModuleDetector
        
        # 创建检测器
        print(f"\n🔧 初始化增强模块检测器...")
        detector = EnhancedModuleDetector(cache_dir=".simple_test_cache", max_workers=2)
        
        # 定义输出回调函数
        def output_callback(message):
            print(f"  📝 {message}")
        
        # 执行检测
        print(f"\n🔍 开始智能模块检测...")
        start_time = time.time()
        
        result = detector.detect_modules_with_cache(test_script, output_callback)
        
        detection_time = time.time() - start_time
        print(f"\n⏱️  检测完成，总耗时: {detection_time:.2f}s")
        
        # 显示检测结果
        print(f"\n📊 检测结果统计:")
        print(f"  - 检测到的模块: {len(result.detected_modules)}")
        print(f"  - 缺失的模块: {len(result.missing_modules)}")
        print(f"  - 冲突的模块: {len(result.conflicted_modules)}")
        print(f"  - 推荐的隐藏导入: {len(result.hidden_imports)}")
        print(f"  - 推荐的collect-all: {len(result.collect_all)}")
        print(f"  - 框架配置: {len(result.framework_configs)}")
        print(f"  - 缓存命中: {'是' if result.cache_hit else '否'}")
        
        # 显示检测到的模块
        if result.detected_modules:
            print(f"\n📦 检测到的模块:")
            for module in sorted(result.detected_modules):
                print(f"  - {module}")
        
        # 显示缺失的模块
        if result.missing_modules:
            print(f"\n❌ 缺失的模块:")
            for module in sorted(result.missing_modules):
                print(f"  - {module}")
        
        # 显示框架配置
        if result.framework_configs:
            print(f"\n🎯 检测到的框架:")
            for framework, config in result.framework_configs.items():
                print(f"  - {framework}: {config.get('name', framework)}")
        
        # 显示建议
        if result.recommendations:
            print(f"\n💡 优化建议:")
            for i, recommendation in enumerate(result.recommendations, 1):
                print(f"  {i}. {recommendation}")
        
        # 测试缓存功能
        print(f"\n🔄 测试缓存功能...")
        cache_start_time = time.time()
        cached_result = detector.detect_modules_with_cache(test_script, output_callback)
        cache_time = time.time() - cache_start_time
        
        print(f"  缓存检测耗时: {cache_time:.3f}s")
        print(f"  缓存命中: {'是' if cached_result.cache_hit else '否'}")
        if detection_time > 0:
            print(f"  性能提升: {((detection_time - cache_time) / detection_time * 100):.1f}%")
        
        # 显示缓存统计
        cache_stats = detector.get_cache_stats()
        print(f"\n📈 缓存统计信息:")
        print(f"  - 内存缓存数量: {cache_stats['memory_cache_count']}")
        print(f"  - 磁盘缓存数量: {cache_stats['disk_cache_count']}")
        print(f"  - 总检测次数: {cache_stats['total_detections']}")
        print(f"  - 缓存命中次数: {cache_stats['cache_hits']}")
        print(f"  - 缓存命中率: {cache_stats['cache_hit_rate']:.1%}")
        print(f"  - 平均检测时间: {cache_stats['avg_detection_time']:.3f}s")
        
        # 生成PyInstaller参数
        print(f"\n🚀 生成PyInstaller参数...")
        pyinstaller_args = detector.generate_pyinstaller_args(test_script, output_callback)
        
        print(f"  生成了 {len(pyinstaller_args)} 个参数")
        
        if pyinstaller_args:
            print(f"\n📋 生成的参数:")
            for arg in pyinstaller_args:
                print(f"  {arg}")
        
        print(f"\n✅ 基本依赖检测测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_script):
                os.remove(test_script)
                print(f"🧹 清理测试文件: {test_script}")
            
            # 清理测试缓存
            import shutil
            if os.path.exists('.simple_test_cache'):
                shutil.rmtree('.simple_test_cache')
                print(f"🧹 清理测试缓存目录")
                
        except Exception as e:
            print(f"⚠️  清理文件时出错: {e}")

def test_framework_templates():
    """测试框架模板功能"""
    print(f"\n🎯 测试框架模板功能")
    print("-" * 40)
    
    try:
        from config.framework_templates import FrameworkTemplates
        
        templates = FrameworkTemplates.get_all_templates()
        print(f"加载了 {len(templates)} 个框架模板:")
        
        for name, template in templates.items():
            print(f"  - {name}: {template.get('description', 'No description')}")
            print(f"    指示器: {len(template.get('indicators', []))} 个")
            print(f"    隐藏导入: {len(template.get('hidden_imports', []))} 个")
            print(f"    建议: {len(template.get('recommendations', []))} 条")
    
    except Exception as e:
        print(f"❌ 框架模板测试失败: {e}")

if __name__ == "__main__":
    test_basic_detection()
    test_framework_templates()
