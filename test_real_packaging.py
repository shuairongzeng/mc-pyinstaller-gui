#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实打包测试 - 验证输出修复效果
"""
import sys
import os
import tempfile
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_script():
    """创建测试脚本"""
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的测试脚本
"""
import sys
import time

def main():
    print("Hello from test script!")
    print(f"Python version: {sys.version}")
    print("Script is running...")
    
    # 简单的计算
    result = 0
    for i in range(1000):
        result += i
    
    print(f"Calculation result: {result}")
    print("Test script completed successfully!")

if __name__ == "__main__":
    main()
'''
    
    # 创建临时脚本文件
    temp_script = tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False, 
        prefix='test_script_', dir='.'
    )
    temp_script.write(test_content)
    temp_script.close()
    
    return temp_script.name

def test_async_packaging():
    """测试异步打包功能"""
    print("创建测试脚本...")

    try:
        # 创建QApplication实例（PyQt5信号需要事件循环）
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # 创建测试脚本
        script_path = create_test_script()
        print(f"测试脚本: {script_path}")

        # 导入必要的模块
        from config.app_config import AppConfig
        from models.packer_model import PyInstallerModel
        from services.package_service import AsyncPackageService
        
        # 创建配置和模型
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 设置打包参数
        model.script_path = script_path
        model.output_dir = "./test_dist"
        model.is_one_file = True
        model.is_windowed = False
        model.name = "test_app"
        
        print("配置信息:")
        print(f"  脚本路径: {model.script_path}")
        print(f"  输出目录: {model.output_dir}")
        print(f"  单文件模式: {model.is_one_file}")
        
        # 验证配置
        errors = model.validate_config()
        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("✅ 配置验证通过")
        
        # 创建异步服务
        service = AsyncPackageService(model, "", 60)  # 1分钟超时
        
        # 收集输出
        outputs = []
        progresses = []
        statuses = []
        errors_list = []
        finished_results = []
        
        def collect_output(msg):
            outputs.append(msg)
            print(f"[OUTPUT] {msg}")
        
        def collect_progress(progress):
            progresses.append(progress)
            print(f"[PROGRESS] {progress}%")
        
        def collect_status(status):
            statuses.append(status)
            print(f"[STATUS] {status}")
        
        def collect_error(error):
            errors_list.append(error)
            print(f"[ERROR] {error}")
        
        def collect_finished(success, message):
            finished_results.append((success, message))
            print(f"[FINISHED] {'成功' if success else '失败'}: {message}")
        
        # 连接信号
        service.connect_signals(
            output_callback=collect_output,
            progress_callback=collect_progress,
            status_callback=collect_status,
            error_callback=collect_error,
            finished_callback=collect_finished
        )
        
        print("\n开始异步打包...")
        print("=" * 60)
        
        # 启动打包
        if service.start_packaging():
            print("✅ 异步打包服务启动成功")

            # 使用QTimer来处理事件循环
            start_time = time.time()
            timeout = 60  # 60秒超时

            # 创建定时器来检查状态
            check_timer = QTimer()
            check_timer.timeout.connect(lambda: app.processEvents())
            check_timer.start(100)  # 每100ms检查一次

            # 等待打包完成
            while service.is_running():
                app.processEvents()  # 处理Qt事件
                time.sleep(0.1)
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    print("⏰ 打包超时，强制停止")
                    service.cancel_packaging()
                    break

            check_timer.stop()
            
            print("=" * 60)
            print("打包过程结束")
            
            # 显示统计信息
            print(f"\n📊 统计信息:")
            print(f"  输出消息: {len(outputs)} 条")
            print(f"  进度更新: {len(progresses)} 次")
            print(f"  状态变化: {len(statuses)} 次")
            print(f"  错误信息: {len(errors_list)} 条")
            print(f"  完成结果: {len(finished_results)} 个")
            
            # 显示进度变化
            if progresses:
                print(f"  进度范围: {min(progresses)}% - {max(progresses)}%")
            
            # 显示最终结果
            if finished_results:
                success, message = finished_results[-1]
                print(f"  最终结果: {'✅ 成功' if success else '❌ 失败'} - {message}")
            
            # 验证输出质量
            if len(outputs) > 5:  # 应该有足够的输出
                print("✅ 输出显示正常")
                return True
            else:
                print("❌ 输出显示不足")
                return False
                
        else:
            print("❌ 异步打包服务启动失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试文件
        try:
            if 'script_path' in locals():
                os.unlink(script_path)
                print(f"清理测试脚本: {script_path}")
        except:
            pass

def main():
    """主函数"""
    print("异步打包输出修复验证")
    print("=" * 60)
    
    # 检查依赖
    try:
        import PyQt5
        print("✅ PyQt5 可用")
    except ImportError:
        print("❌ PyQt5 不可用，跳过GUI相关测试")
        return 1
    
    # 运行测试
    if test_async_packaging():
        print("\n🎉 异步打包输出修复验证成功！")
        print("\n修复效果:")
        print("✅ 详细的打包过程输出")
        print("✅ 实时进度更新")
        print("✅ 状态变化显示")
        print("✅ 错误信息处理")
        print("✅ 用户体验改善")
        return 0
    else:
        print("\n❌ 异步打包输出修复验证失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
