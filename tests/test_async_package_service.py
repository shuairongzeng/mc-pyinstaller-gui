#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步打包服务测试
"""
import sys
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel
from services.package_service import AsyncPackageWorker, AsyncPackageService


class TestAsyncPackageWorker(unittest.TestCase):
    """异步打包工作线程测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """设置测试"""
        self.config = AppConfig()
        self.model = PyInstallerModel(self.config)
        
        # 创建临时测试脚本
        self.temp_script = tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        )
        self.temp_script.write('print("Hello World")')
        self.temp_script.close()
        
        self.model.script_path = self.temp_script.name
        self.model.output_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试"""
        try:
            os.unlink(self.temp_script.name)
        except:
            pass

    def test_worker_initialization(self):
        """测试工作线程初始化"""
        worker = AsyncPackageWorker(self.model, "", 60)
        
        self.assertEqual(worker.model, self.model)
        self.assertEqual(worker.python_interpreter, "")
        self.assertEqual(worker.timeout, 60)
        self.assertFalse(worker._cancelled)
        self.assertIsNone(worker.process)

    def test_worker_signals(self):
        """测试工作线程信号"""
        worker = AsyncPackageWorker(self.model)
        
        # 检查信号是否存在
        self.assertTrue(hasattr(worker, 'progress_updated'))
        self.assertTrue(hasattr(worker, 'output_received'))
        self.assertTrue(hasattr(worker, 'error_occurred'))
        self.assertTrue(hasattr(worker, 'finished_signal'))
        self.assertTrue(hasattr(worker, 'status_changed'))

    def test_cancel_functionality(self):
        """测试取消功能"""
        worker = AsyncPackageWorker(self.model)
        
        # 模拟进程
        mock_process = Mock()
        worker.process = mock_process
        
        # 取消操作
        worker.cancel()
        
        self.assertTrue(worker._cancelled)
        mock_process.terminate.assert_called_once()

    @patch('subprocess.Popen')
    def test_progress_update_from_output(self, mock_popen):
        """测试从输出更新进度"""
        worker = AsyncPackageWorker(self.model)
        
        # 测试不同的输出内容
        test_cases = [
            ("INFO: Building", 40),
            ("INFO: Collecting", 60),
            ("INFO: Building EXE", 80),
            ("successfully created", 95)
        ]
        
        for output, expected_progress in test_cases:
            with patch.object(worker, 'progress_updated') as mock_signal:
                worker._update_progress_from_output(output)
                mock_signal.emit.assert_called_with(expected_progress)


class TestAsyncPackageService(unittest.TestCase):
    """异步打包服务测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """设置测试"""
        self.config = AppConfig()
        self.model = PyInstallerModel(self.config)
        
        # 创建临时测试脚本
        self.temp_script = tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        )
        self.temp_script.write('print("Hello World")')
        self.temp_script.close()
        
        self.model.script_path = self.temp_script.name
        self.model.output_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试"""
        try:
            os.unlink(self.temp_script.name)
        except:
            pass

    def test_service_initialization(self):
        """测试服务初始化"""
        service = AsyncPackageService(self.model, "", 120)
        
        self.assertEqual(service.model, self.model)
        self.assertEqual(service.python_interpreter, "")
        self.assertEqual(service.timeout, 120)
        self.assertIsNone(service.worker)

    def test_start_packaging(self):
        """测试开始打包"""
        service = AsyncPackageService(self.model)
        
        with patch('services.package_service.AsyncPackageWorker') as MockWorker:
            mock_worker = Mock()
            MockWorker.return_value = mock_worker
            
            result = service.start_packaging()
            
            self.assertTrue(result)
            MockWorker.assert_called_once()
            mock_worker.start.assert_called_once()

    def test_start_packaging_already_running(self):
        """测试重复启动打包"""
        service = AsyncPackageService(self.model)
        
        # 模拟已有工作线程在运行
        mock_worker = Mock()
        mock_worker.isRunning.return_value = True
        service.worker = mock_worker
        
        result = service.start_packaging()
        
        self.assertFalse(result)

    def test_cancel_packaging(self):
        """测试取消打包"""
        service = AsyncPackageService(self.model)
        
        # 模拟工作线程
        mock_worker = Mock()
        service.worker = mock_worker
        
        service.cancel_packaging()
        
        mock_worker.cancel.assert_called_once()

    def test_is_running(self):
        """测试运行状态检查"""
        service = AsyncPackageService(self.model)
        
        # 无工作线程时
        self.assertFalse(service.is_running())
        
        # 有工作线程但未运行
        mock_worker = Mock()
        mock_worker.isRunning.return_value = False
        service.worker = mock_worker
        self.assertFalse(service.is_running())
        
        # 有工作线程且正在运行
        mock_worker.isRunning.return_value = True
        self.assertTrue(service.is_running())

    def test_connect_signals(self):
        """测试信号连接"""
        service = AsyncPackageService(self.model)
        
        # 创建模拟工作线程
        mock_worker = Mock()
        service.worker = mock_worker
        
        # 创建回调函数
        progress_callback = Mock()
        output_callback = Mock()
        error_callback = Mock()
        finished_callback = Mock()
        status_callback = Mock()
        
        # 连接信号
        service.connect_signals(
            progress_callback=progress_callback,
            output_callback=output_callback,
            error_callback=error_callback,
            finished_callback=finished_callback,
            status_callback=status_callback
        )
        
        # 验证信号连接
        mock_worker.progress_updated.connect.assert_called_with(progress_callback)
        mock_worker.output_received.connect.assert_called_with(output_callback)
        mock_worker.error_occurred.connect.assert_called_with(error_callback)
        mock_worker.finished_signal.connect.assert_called_with(finished_callback)
        mock_worker.status_changed.connect.assert_called_with(status_callback)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_full_workflow(self):
        """测试完整工作流程"""
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 创建临时测试脚本
        temp_script = tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        )
        temp_script.write('print("Hello World")')
        temp_script.close()
        
        try:
            model.script_path = temp_script.name
            model.output_dir = tempfile.mkdtemp()
            
            # 创建服务
            service = AsyncPackageService(model, "", 10)  # 短超时用于测试
            
            # 连接信号
            progress_values = []
            output_messages = []
            error_messages = []
            finished_results = []
            status_messages = []
            
            service.connect_signals(
                progress_callback=lambda p: progress_values.append(p),
                output_callback=lambda m: output_messages.append(m),
                error_callback=lambda e: error_messages.append(e),
                finished_callback=lambda s, m: finished_results.append((s, m)),
                status_callback=lambda st: status_messages.append(st)
            )
            
            # 启动打包（这会失败，因为没有真正的PyInstaller环境）
            result = service.start_packaging()
            self.assertTrue(result)
            
            # 等待一段时间让工作线程运行
            QTest.qWait(1000)
            
            # 验证至少有一些输出
            self.assertGreater(len(output_messages), 0)
            
        finally:
            try:
                os.unlink(temp_script.name)
            except:
                pass


if __name__ == '__main__':
    unittest.main()
