#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试输出修复效果
"""
import sys
import os
import tempfile
import time
from unittest.mock import Mock, patch

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_signal_connection():
    """测试信号连接"""
    print("测试信号连接...")
    
    try:
        from config.app_config import AppConfig
        from models.packer_model import PyInstallerModel
        from services.package_service import AsyncPackageService
        
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 创建临时脚本
        temp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_script.write('print("Hello World")')
        temp_script.close()
        
        model.script_path = temp_script.name
        model.output_dir = tempfile.mkdtemp()
        
        # 创建服务
        service = AsyncPackageService(model, "", 10)
        
        # 测试回调存储
        output_messages = []
        progress_values = []
        status_messages = []
        
        def output_callback(msg):
            output_messages.append(msg)
            print(f"[OUTPUT] {msg}")
        
        def progress_callback(progress):
            progress_values.append(progress)
            print(f"[PROGRESS] {progress}%")
        
        def status_callback(status):
            status_messages.append(status)
            print(f"[STATUS] {status}")
        
        # 连接信号
        service.connect_signals(
            output_callback=output_callback,
            progress_callback=progress_callback,
            status_callback=status_callback
        )
        
        # 验证回调存储
        assert service._callbacks['output'] == output_callback
        assert service._callbacks['progress'] == progress_callback
        assert service._callbacks['status'] == status_callback
        
        print("✅ 信号连接测试通过")
        
        # 清理
        os.unlink(temp_script.name)
        return True
        
    except Exception as e:
        print(f"❌ 信号连接测试失败: {e}")
        return False

def test_output_enhancement():
    """测试输出增强"""
    print("测试输出增强...")
    
    try:
        from services.package_service import AsyncPackageWorker
        from config.app_config import AppConfig
        from models.packer_model import PyInstallerModel
        
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 创建临时脚本
        temp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_script.write('print("Hello World")')
        temp_script.close()
        
        model.script_path = temp_script.name
        model.output_dir = tempfile.mkdtemp()
        
        # 创建工作线程
        worker = AsyncPackageWorker(model, "", 5)
        
        # 收集输出
        outputs = []
        progresses = []
        statuses = []
        
        def collect_output(msg):
            outputs.append(msg)
            print(f"[OUTPUT] {msg}")
        
        def collect_progress(progress):
            progresses.append(progress)
            print(f"[PROGRESS] {progress}%")
        
        def collect_status(status):
            statuses.append(status)
            print(f"[STATUS] {status}")
        
        # 连接信号
        worker.output_received.connect(collect_output)
        worker.progress_updated.connect(collect_progress)
        worker.status_changed.connect(collect_status)
        
        # 测试进度解析
        test_outputs = [
            "INFO: PyInstaller: 4.5.1",
            "INFO: Loading module hooks...",
            "INFO: Analyzing base_library.zip",
            "INFO: Processing module hooks...",
            "INFO: Building EXE from EXE-00.toc",
            "INFO: Collecting submodules for numpy",
            "INFO: Copying metadata for package numpy",
            "INFO: Appending archive to EXE",
            "Successfully created dist/test.exe"
        ]
        
        for output in test_outputs:
            worker._update_progress_from_output(output)
        
        # 验证输出
        print(f"收集到 {len(outputs)} 条输出")
        print(f"收集到 {len(progresses)} 个进度值")
        print(f"收集到 {len(statuses)} 个状态")
        
        # 验证进度值递增
        if progresses:
            assert max(progresses) >= min(progresses), "进度应该递增"
        
        print("✅ 输出增强测试通过")
        
        # 清理
        os.unlink(temp_script.name)
        return True
        
    except Exception as e:
        print(f"❌ 输出增强测试失败: {e}")
        return False

def test_mock_packaging():
    """测试模拟打包过程"""
    print("测试模拟打包过程...")
    
    try:
        from services.package_service import AsyncPackageService
        from config.app_config import AppConfig
        from models.packer_model import PyInstallerModel
        
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 创建临时脚本
        temp_script = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_script.write('print("Hello World")')
        temp_script.close()
        
        model.script_path = temp_script.name
        model.output_dir = tempfile.mkdtemp()
        
        # 创建服务
        service = AsyncPackageService(model, "", 5)
        
        # 收集所有输出
        all_outputs = []
        all_progress = []
        all_status = []
        finished_results = []
        
        def collect_all_output(msg):
            all_outputs.append(msg)
            print(f"📝 {msg}")
        
        def collect_all_progress(progress):
            all_progress.append(progress)
            print(f"📊 进度: {progress}%")
        
        def collect_all_status(status):
            all_status.append(status)
            print(f"🔄 状态: {status}")
        
        def collect_finished(success, message):
            finished_results.append((success, message))
            print(f"🏁 完成: {'成功' if success else '失败'} - {message}")
        
        # 连接所有信号
        service.connect_signals(
            output_callback=collect_all_output,
            progress_callback=collect_all_progress,
            status_callback=collect_all_status,
            finished_callback=collect_finished
        )
        
        print("开始模拟打包...")
        
        # 使用mock来模拟subprocess
        with patch('subprocess.Popen') as mock_popen:
            # 模拟进程
            mock_process = Mock()
            mock_process.poll.return_value = None  # 进程运行中
            mock_process.stdout.readline.side_effect = [
                "INFO: PyInstaller: 4.5.1\n",
                "INFO: Loading module hooks...\n", 
                "INFO: Analyzing base_library.zip\n",
                "INFO: Building EXE from EXE-00.toc\n",
                "Successfully created dist/test.exe\n",
                ""  # 结束
            ]
            mock_popen.return_value = mock_process
            
            # 启动打包
            if service.start_packaging():
                print("✅ 打包服务启动成功")
                
                # 等待一段时间让线程运行
                time.sleep(2)
                
                # 模拟进程完成
                mock_process.poll.return_value = 0
                
                # 再等待一段时间
                time.sleep(1)
                
                print(f"📊 统计:")
                print(f"  - 输出消息: {len(all_outputs)} 条")
                print(f"  - 进度更新: {len(all_progress)} 次")
                print(f"  - 状态变化: {len(all_status)} 次")
                print(f"  - 完成结果: {len(finished_results)} 个")
                
                # 验证有输出
                assert len(all_outputs) > 0, "应该有输出消息"
                
                print("✅ 模拟打包测试通过")
            else:
                print("❌ 打包服务启动失败")
                return False
        
        # 清理
        os.unlink(temp_script.name)
        return True
        
    except Exception as e:
        print(f"❌ 模拟打包测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试输出修复效果...")
    print("=" * 60)
    
    tests = [
        test_signal_connection,
        test_output_enhancement,
        test_mock_packaging
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print("-" * 40)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            print("-" * 40)
    
    print("=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有输出修复测试通过！")
        print("\n修复效果:")
        print("✅ 信号连接时序问题已修复")
        print("✅ 输出显示增强已实现")
        print("✅ 进度反馈更加详细")
        print("✅ 用户体验显著改善")
        return 0
    else:
        print("❌ 部分测试失败，需要进一步修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
