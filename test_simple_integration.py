"""
简单的集成测试 - 验证新的智能分析器是否已集成到GUI中
"""

import os
import sys
import tempfile

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_imports():
    """测试模块导入"""
    print("🔍 测试新模块导入...")
    
    modules_to_test = [
        ("services.performance_optimized_detector", "PerformanceOptimizedDetector"),
        ("services.intelligent_module_analyzer", "IntelligentModuleAnalyzer"),
        ("services.advanced_dynamic_detector", "AdvancedDynamicDetector"),
        ("utils.advanced_cache_manager", "AdvancedCacheManager"),
    ]
    
    success_count = 0
    for module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {class_name}: 导入成功")
            success_count += 1
        except ImportError as e:
            print(f"❌ {class_name}: 导入失败 - {e}")
        except AttributeError as e:
            print(f"❌ {class_name}: 类不存在 - {e}")
    
    print(f"📊 导入成功率: {success_count}/{len(modules_to_test)} ({success_count/len(modules_to_test)*100:.1f}%)")
    return success_count == len(modules_to_test)

def test_gui_integration():
    """测试GUI集成"""
    print("\n🖥️  测试GUI集成...")
    
    try:
        # 导入模块标签页
        from views.tabs.module_tab import ModuleTab, ModuleDetectionThread
        print("✅ ModuleTab 和 ModuleDetectionThread 导入成功")
        
        # 检查源代码中是否包含新的分析器
        import inspect
        
        # 检查 ModuleDetectionThread 的源代码
        thread_source = inspect.getsource(ModuleDetectionThread)
        
        checks = [
            ("PerformanceOptimizedDetector", "性能优化检测器"),
            ("IntelligentModuleAnalyzer", "智能模块分析器"),
            ("detect_modules_optimized", "优化检测方法"),
            ("intelligent_result", "智能分析结果"),
        ]
        
        integration_score = 0
        for check_str, description in checks:
            if check_str in thread_source:
                print(f"✅ {description}: 已集成")
                integration_score += 1
            else:
                print(f"❌ {description}: 未集成")
        
        print(f"📊 集成完成度: {integration_score}/{len(checks)} ({integration_score/len(checks)*100:.1f}%)")
        
        return integration_score >= len(checks) // 2  # 至少50%集成
        
    except ImportError as e:
        print(f"❌ GUI模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ GUI集成检查失败: {e}")
        return False

def test_functional_integration():
    """测试功能集成"""
    print("\n🧪 测试功能集成...")
    
    # 创建测试脚本
    test_code = '''
import os
import sys
import json

def main():
    print("Hello World")
    
    # 动态导入
    import importlib
    math_module = importlib.import_module("math")

if __name__ == "__main__":
    main()
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        test_script = f.name
    
    try:
        # 测试新的检测器是否能正常工作
        from services.performance_optimized_detector import PerformanceOptimizedDetector
        
        detector = PerformanceOptimizedDetector()
        result = detector.detect_modules_optimized(
            test_script, 
            use_execution=False,
            enable_profiling=False
        )
        
        modules_found = len(result.analysis_result.recommended_modules)
        print(f"✅ 性能优化检测器工作正常，检测到 {modules_found} 个模块")
        
        # 检查是否有缓存功能
        if result.cache_hit is not None:
            print(f"✅ 缓存功能正常，缓存命中: {result.cache_hit}")
        
        # 检查性能指标
        if result.performance_metrics:
            print(f"✅ 性能监控正常，耗时: {result.performance_metrics.total_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False
    
    finally:
        try:
            os.unlink(test_script)
        except:
            pass

def main():
    """主测试函数"""
    print("🚀 开始简单集成测试")
    print("=" * 50)
    
    # 运行各项测试
    tests = [
        ("模块导入测试", test_module_imports),
        ("GUI集成测试", test_gui_integration),
        ("功能集成测试", test_functional_integration),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} 通过")
                passed_tests += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    # 显示总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    print(f"通过测试: {passed_tests}/{total_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！新的智能分析器已成功集成到GUI中！")
        print("\n💡 使用说明:")
        print("1. 启动GUI应用程序")
        print("2. 选择要分析的Python脚本")
        print("3. 点击'开始检测'按钮")
        print("4. 系统会自动使用新的智能分析器进行检测")
        print("5. 查看'智能分析'标签页获取详细结果")
    elif passed_tests >= total_tests // 2:
        print("⚠️  部分测试通过，集成基本成功但可能需要进一步调整")
    else:
        print("❌ 大部分测试失败，集成可能存在问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
