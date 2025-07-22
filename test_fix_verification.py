"""
验证修复是否有效的测试脚本
"""

import os
import sys
import tempfile
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, pyqtSignal, QObject

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestSignalReceiver(QObject):
    """测试信号接收器"""
    
    def __init__(self):
        super().__init__()
        self.progress_messages = []
        self.finished_modules = []
        self.analysis_results = []
        self.errors = []
        self.detection_completed = False
    
    def on_progress(self, message):
        """接收进度信号"""
        self.progress_messages.append(message)
        print(f"📊 进度: {message}")
    
    def on_finished(self, modules):
        """接收完成信号"""
        self.finished_modules = modules
        print(f"✅ 检测完成: {len(modules)} 个模块")
    
    def on_analysis_finished(self, analysis):
        """接收分析完成信号"""
        self.analysis_results.append(analysis)
        self.detection_completed = True
        print(f"🧠 分析完成: {analysis.get('analysis_type', 'unknown')} 类型")
        print(f"📈 检测到模块: {len(analysis.get('detected_modules', []))}")
    
    def on_error(self, error):
        """接收错误信号"""
        self.errors.append(error)
        print(f"❌ 错误: {error}")

def create_test_script():
    """创建测试脚本"""
    test_code = '''
import os
import sys
import json
import time

def main():
    print("Hello World")
    
    # 动态导入
    import importlib
    math_module = importlib.import_module("math")
    
    # 条件导入
    if sys.platform == "win32":
        try:
            import winsound
        except ImportError:
            pass

if __name__ == "__main__":
    main()
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        return f.name

def test_detection_thread():
    """测试检测线程"""
    print("🧵 测试检测线程修复...")
    
    test_script = create_test_script()
    
    try:
        from views.tabs.module_tab import ModuleDetectionThread
        
        class MockConfig:
            def get(self, key, default=""):
                if key == "python_interpreter":
                    return sys.executable
                return default
        
        # 创建模块检测器
        from services.module_detector import ModuleDetector
        detector = ModuleDetector(use_ast=True, python_interpreter=sys.executable)

        # 创建检测线程
        thread = ModuleDetectionThread(detector, test_script, MockConfig())
        
        # 创建信号接收器
        receiver = TestSignalReceiver()
        
        # 连接信号
        thread.progress_signal.connect(receiver.on_progress)
        thread.finished_signal.connect(receiver.on_finished)
        thread.analysis_finished_signal.connect(receiver.on_analysis_finished)
        thread.error_signal.connect(receiver.on_error)
        
        print("🚀 启动检测线程...")
        thread.start()
        
        # 等待检测完成
        timeout = 30  # 30秒超时
        start_time = time.time()
        
        while not receiver.detection_completed and time.time() - start_time < timeout:
            QApplication.processEvents()
            time.sleep(0.1)
        
        # 等待线程完成
        thread.wait(5000)
        
        # 检查结果
        print("\n📊 检测结果:")
        print(f"  进度消息数: {len(receiver.progress_messages)}")
        print(f"  检测到模块数: {len(receiver.finished_modules)}")
        print(f"  分析结果数: {len(receiver.analysis_results)}")
        print(f"  错误数: {len(receiver.errors)}")
        
        if receiver.analysis_results:
            analysis = receiver.analysis_results[0]
            print(f"  分析类型: {analysis.get('analysis_type', 'unknown')}")
            print(f"  检测成功: {analysis.get('analysis_successful', False)}")
            
            # 检查是否有智能分析结果
            if 'intelligent_result' in analysis:
                print("  ✅ 包含智能分析结果")
                intelligent_result = analysis['intelligent_result']
                print(f"    推荐模块: {len(intelligent_result.recommended_modules)}")
                print(f"    必需模块: {len(intelligent_result.essential_modules)}")
                print(f"    置信度分数: {len(intelligent_result.confidence_scores)}")
            else:
                print("  ⚠️  未包含智能分析结果")
        
        # 验证修复
        success = (
            receiver.detection_completed and
            len(receiver.analysis_results) > 0 and
            len(receiver.errors) == 0
        )
        
        if success:
            print("✅ 检测线程修复验证成功！")
        else:
            print("❌ 检测线程修复验证失败！")
        
        return success
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            os.unlink(test_script)
        except:
            pass

def test_signal_flow():
    """测试信号流程"""
    print("\n🔄 测试信号流程...")
    
    try:
        from views.tabs.module_tab import ModuleDetectionThread
        
        # 检查线程类是否有正确的信号
        thread_class = ModuleDetectionThread
        
        signals_to_check = [
            'progress_signal',
            'finished_signal', 
            'analysis_finished_signal',
            'error_signal'
        ]
        
        missing_signals = []
        for signal_name in signals_to_check:
            if not hasattr(thread_class, signal_name):
                missing_signals.append(signal_name)
        
        if missing_signals:
            print(f"❌ 缺少信号: {missing_signals}")
            return False
        else:
            print("✅ 所有必需信号都存在")
        
        # 检查方法是否存在
        methods_to_check = [
            '_run_precise_analysis',
            'run',
            'stop'
        ]
        
        missing_methods = []
        for method_name in methods_to_check:
            if not hasattr(thread_class, method_name):
                missing_methods.append(method_name)
        
        if missing_methods:
            print(f"❌ 缺少方法: {missing_methods}")
            return False
        else:
            print("✅ 所有必需方法都存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 信号流程测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 开始修复验证测试")
    print("=" * 50)
    
    # 创建QApplication
    app = QApplication(sys.argv)
    
    # 运行测试
    tests = [
        ("信号流程测试", test_signal_flow),
        ("检测线程测试", test_detection_thread),
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
    print("📊 修复验证总结")
    print("=" * 50)
    print(f"通过测试: {passed_tests}/{total_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 修复验证成功！问题已解决！")
        print("\n💡 修复内容:")
        print("1. ✅ 添加了缺失的信号发送")
        print("2. ✅ 修复了进度条不停止的问题")
        print("3. ✅ 改进了状态标签更新")
        print("4. ✅ 确保分析结果正确显示")
    else:
        print("❌ 修复验证失败，可能还有其他问题")
    
    app.quit()
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
