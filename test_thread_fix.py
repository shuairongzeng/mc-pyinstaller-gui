#!/usr/bin/env python3
"""
测试线程修复 - 验证精准依赖分析在后台线程中运行
"""

import sys
import os
import tempfile
import time

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_thread_functionality():
    """测试线程功能"""
    print("🧪 测试精准依赖分析线程功能")
    print("=" * 50)
    
    # 创建测试脚本
    test_script_content = '''
import os
import sys
import json
try:
    import PyQt5
except ImportError:
    pass
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_script_content)
        test_script = f.name
    
    try:
        # 测试线程类导入
        from views.tabs.module_tab import ModuleDetectionThread
        from services.module_detector import ModuleDetector
        from config.app_config import AppConfig
        
        print("✅ 成功导入ModuleDetectionThread")
        
        # 创建配置和检测器
        config = AppConfig()
        detector = ModuleDetector()
        
        print("✅ 成功创建配置和检测器")
        
        # 创建线程
        thread = ModuleDetectionThread(
            detector=detector,
            script_path=test_script,
            config=config,
            use_precise_analysis=True
        )
        
        print("✅ 成功创建检测线程")
        
        # 测试信号连接
        results = {'finished': False, 'analysis_finished': False, 'error': None}
        
        def on_progress(message):
            print(f"  📝 进度: {message}")
        
        def on_finished(modules):
            print(f"  ✅ 检测完成: {len(modules)} 个模块")
            results['finished'] = True
        
        def on_analysis_finished(analysis):
            print(f"  🎯 分析完成: {len(analysis.get('detected_modules', []))} 个模块")
            if 'precise_result' in analysis:
                precise_result = analysis['precise_result']
                print(f"    - 标准库: {len(precise_result.standard_modules)}")
                print(f"    - 第三方库: {len(precise_result.third_party_modules)}")
                print(f"    - 本地模块: {len(precise_result.local_modules)}")
                print(f"    - 缓存命中: {'是' if precise_result.cache_hit else '否'}")
                print(f"    - 分析时间: {precise_result.analysis_time:.2f}s")
            results['analysis_finished'] = True
        
        def on_error(error):
            print(f"  ❌ 错误: {error}")
            results['error'] = error
        
        # 连接信号
        thread.progress_signal.connect(on_progress)
        thread.finished_signal.connect(on_finished)
        thread.analysis_finished_signal.connect(on_analysis_finished)
        thread.error_signal.connect(on_error)
        
        print("✅ 成功连接信号")
        
        # 启动线程
        print("\n🚀 启动分析线程...")
        thread.start()
        
        # 等待完成 - 需要QApplication来处理信号
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # 使用QTimer来检查状态
        start_time = time.time()
        timeout = 30  # 30秒超时

        while thread.isRunning() and (time.time() - start_time) < timeout:
            app.processEvents()  # 处理信号
            time.sleep(0.1)
        
        if thread.isRunning():
            print("⚠️ 线程运行超时，尝试停止...")
            thread.stop()
            thread.wait(5000)
            if thread.isRunning():
                thread.terminate()
                thread.wait(1000)
            print("⚠️ 线程已强制停止")
            return False
        
        # 检查结果
        elapsed_time = time.time() - start_time
        print(f"\n📊 测试结果 (耗时: {elapsed_time:.2f}s):")
        print(f"  检测完成: {'是' if results['finished'] else '否'}")
        print(f"  分析完成: {'是' if results['analysis_finished'] else '否'}")
        print(f"  发生错误: {'是' if results['error'] else '否'}")
        
        if results['error']:
            print(f"  错误信息: {results['error']}")
        
        success = (results['finished'] or results['analysis_finished']) and not results['error']
        
        if success:
            print("✅ 线程功能测试成功！")
        else:
            print("❌ 线程功能测试失败")
        
        return success
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            os.unlink(test_script)
            print(f"🧹 清理测试脚本: {test_script}")
        except:
            pass

def main():
    """主函数"""
    print("🚀 测试精准依赖分析线程修复")
    print("=" * 60)
    
    success = test_thread_functionality()
    
    if success:
        print("\n🎉 线程修复测试成功！")
        print("\n💡 现在的功能:")
        print("  ✅ 精准依赖分析在后台线程中运行")
        print("  ✅ UI界面不会卡死")
        print("  ✅ 支持进度显示和错误处理")
        print("  ✅ 支持优雅停止分析")
        print("\n📋 使用方法:")
        print("  1. 启动应用程序: python run.py")
        print("  2. 选择Python脚本")
        print("  3. 点击'开始检测'按钮")
        print("  4. 界面保持响应，后台进行精准分析")
        return 0
    else:
        print("\n❌ 线程修复测试失败")
        print("请检查代码修改是否正确")
        return 1

if __name__ == "__main__":
    sys.exit(main())
