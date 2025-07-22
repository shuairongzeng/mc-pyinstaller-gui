"""
测试新的智能分析器是否已集成到GUI中
"""

import os
import sys
import tempfile

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_script():
    """创建测试脚本"""
    test_code = '''
import os
import sys
import json
import requests
import numpy as np

def main():
    print("Hello World")
    
    # 动态导入
    import importlib
    math_module = importlib.import_module("math")
    
    # 条件导入
    if sys.platform == "win32":
        import winsound
    
    # 延迟导入
    def process_data():
        import pandas as pd
        return pd.DataFrame()

if __name__ == "__main__":
    main()
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        return f.name

def test_integration():
    """测试集成"""
    print("🧪 测试新的智能分析器集成")
    print("=" * 50)
    
    # 创建测试脚本
    test_script = create_test_script()
    print(f"📝 创建测试脚本: {test_script}")
    
    try:
        # 测试导入新的分析器
        print("\n🔍 测试导入新的分析器...")
        
        try:
            from services.performance_optimized_detector import PerformanceOptimizedDetector
            print("✅ PerformanceOptimizedDetector 导入成功")
            
            detector = PerformanceOptimizedDetector()
            result = detector.detect_modules_optimized(test_script, use_execution=False)
            print(f"✅ 性能优化检测器工作正常，检测到 {len(result.analysis_result.recommended_modules)} 个模块")
            
        except Exception as e:
            print(f"❌ PerformanceOptimizedDetector 测试失败: {e}")
        
        try:
            from services.intelligent_module_analyzer import IntelligentModuleAnalyzer
            print("✅ IntelligentModuleAnalyzer 导入成功")
            
            analyzer = IntelligentModuleAnalyzer()
            result = analyzer.analyze_script(test_script, use_execution=False)
            print(f"✅ 智能分析器工作正常，检测到 {len(result.recommended_modules)} 个模块")
            
        except Exception as e:
            print(f"❌ IntelligentModuleAnalyzer 测试失败: {e}")
        
        # 测试GUI集成
        print("\n🖥️  测试GUI集成...")
        
        try:
            from views.tabs.module_tab import ModuleTab
            print("✅ ModuleTab 导入成功")
            
            # 检查是否包含新的分析器调用
            import inspect
            source = inspect.getsource(ModuleTab)
            
            if 'PerformanceOptimizedDetector' in source:
                print("✅ GUI已集成PerformanceOptimizedDetector")
            else:
                print("⚠️  GUI未找到PerformanceOptimizedDetector引用")
            
            if 'IntelligentModuleAnalyzer' in source:
                print("✅ GUI已集成IntelligentModuleAnalyzer")
            else:
                print("⚠️  GUI未找到IntelligentModuleAnalyzer引用")
                
            if 'intelligent_result' in source:
                print("✅ GUI已支持智能分析结果显示")
            else:
                print("⚠️  GUI未找到智能分析结果显示支持")
            
        except Exception as e:
            print(f"❌ GUI集成测试失败: {e}")
        
        # 测试检测线程
        print("\n🧵 测试检测线程...")
        
        try:
            from views.tabs.module_tab import DetectionThread
            print("✅ DetectionThread 导入成功")
            
            # 检查检测线程是否使用新的分析器
            source = inspect.getsource(DetectionThread)
            
            if 'PerformanceOptimizedDetector' in source:
                print("✅ DetectionThread已集成PerformanceOptimizedDetector")
            else:
                print("⚠️  DetectionThread未找到PerformanceOptimizedDetector引用")
            
            if 'detect_modules_optimized' in source:
                print("✅ DetectionThread已使用优化检测方法")
            else:
                print("⚠️  DetectionThread未使用优化检测方法")
            
        except Exception as e:
            print(f"❌ DetectionThread测试失败: {e}")
        
        print(f"\n✅ 集成测试完成!")
        
        # 显示集成状态总结
        print("\n📊 集成状态总结:")
        print("=" * 30)
        
        components = [
            ("性能优化检测器", "PerformanceOptimizedDetector"),
            ("智能模块分析器", "IntelligentModuleAnalyzer"),
            ("高级动态检测器", "AdvancedDynamicDetector"),
            ("高级缓存管理器", "AdvancedCacheManager")
        ]
        
        for name, module_name in components:
            try:
                exec(f"from services.{module_name.lower().replace('detector', '_detector').replace('analyzer', '_analyzer').replace('manager', '_manager')} import {module_name}")
                print(f"✅ {name}: 可用")
            except ImportError:
                try:
                    # 尝试其他可能的路径
                    if 'Detector' in module_name:
                        exec(f"from services.{module_name.lower().replace('detector', '_detector')} import {module_name}")
                    elif 'Analyzer' in module_name:
                        exec(f"from services.{module_name.lower().replace('analyzer', '_analyzer')} import {module_name}")
                    elif 'Manager' in module_name:
                        exec(f"from utils.{module_name.lower().replace('manager', '_manager')} import {module_name}")
                    print(f"✅ {name}: 可用")
                except ImportError:
                    print(f"❌ {name}: 不可用")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试文件
        try:
            os.unlink(test_script)
            print(f"🗑️  清理测试文件: {test_script}")
        except:
            pass

def test_detection_workflow():
    """测试完整的检测工作流程"""
    print("\n🔄 测试完整检测工作流程...")
    
    test_script = create_test_script()
    
    try:
        # 模拟GUI检测流程
        from views.tabs.module_tab import DetectionThread
        from PyQt5.QtCore import QObject
        
        class MockConfig:
            def get(self, key, default=""):
                return default
        
        # 创建检测线程
        thread = DetectionThread(test_script, MockConfig())
        
        # 连接信号
        results = []
        errors = []
        
        def on_progress(msg):
            print(f"  📊 {msg}")
        
        def on_finished(analysis):
            results.append(analysis)
            print(f"  ✅ 检测完成，发现 {len(analysis.get('detected_modules', []))} 个模块")
        
        def on_error(error):
            errors.append(error)
            print(f"  ❌ 检测错误: {error}")
        
        thread.progress_signal.connect(on_progress)
        thread.analysis_finished_signal.connect(on_finished)
        thread.error_signal.connect(on_error)
        
        # 运行检测
        thread.run()
        
        if results:
            analysis = results[0]
            print(f"  📈 检测结果类型: {analysis.get('analysis_type', 'unknown')}")
            
            if 'intelligent_result' in analysis:
                print("  🧠 使用了智能分析器")
            elif 'precise_result' in analysis:
                print("  🎯 使用了精准分析器")
            else:
                print("  📊 使用了传统分析器")
        
        if errors:
            print(f"  ⚠️  检测过程中有 {len(errors)} 个错误")
        
    except Exception as e:
        print(f"❌ 工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            os.unlink(test_script)
        except:
            pass

if __name__ == "__main__":
    test_integration()
    test_detection_workflow()
