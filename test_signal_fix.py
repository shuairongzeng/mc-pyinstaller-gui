#!/usr/bin/env python3
"""
测试信号修复
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from services.module_detector import ModuleDetector

class TestThread(QThread):
    """测试线程"""
    
    finished_signal = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.detector = ModuleDetector(use_ast=True, use_pyinstaller=False)
    
    def run(self):
        """运行测试"""
        try:
            # 创建一个简单的测试脚本
            test_script = "test_simple.py"
            with open(test_script, "w", encoding="utf-8") as f:
                f.write("import os\nimport sys\nimport json\n")
            
            # 检测模块
            modules = self.detector.detect_modules(test_script)
            print(f"检测到的模块类型: {type(modules)}")
            print(f"检测到的模块: {modules}")
            
            # 转换为list
            modules_list = list(modules) if isinstance(modules, set) else modules
            print(f"转换后的类型: {type(modules_list)}")
            
            # 发送信号
            self.finished_signal.emit(modules_list)
            
            # 清理
            if os.path.exists(test_script):
                os.remove(test_script)
                
        except Exception as e:
            print(f"测试失败: {e}")
            import traceback
            traceback.print_exc()

def test_signal_fix():
    """测试信号修复"""
    print("🔍 测试信号修复")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    def on_finished(modules):
        print(f"✅ 信号接收成功!")
        print(f"接收到的模块类型: {type(modules)}")
        print(f"接收到的模块: {modules}")
        app.quit()
    
    thread = TestThread()
    thread.finished_signal.connect(on_finished)
    thread.start()
    
    app.exec_()
    print("✅ 测试完成")

if __name__ == "__main__":
    test_signal_fix()
