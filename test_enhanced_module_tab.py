#!/usr/bin/env python3
"""
测试增强的模块标签页
"""

import sys
import os
import tempfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.tabs.enhanced_module_tab import EnhancedModuleTab
from models.packer_model import PyInstallerModel
from config.app_config import AppConfig

def create_test_script():
    """创建测试脚本"""
    test_script_content = '''#!/usr/bin/env python3
"""
测试脚本 - 用于测试增强模块标签页
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 第三方库导入
try:
    import PyQt5
    from PyQt5.QtWidgets import QApplication
    HAS_PYQT5 = True
except ImportError:
    HAS_PYQT5 = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# 条件导入
if sys.platform == 'win32':
    try:
        import winsound
    except ImportError:
        winsound = None

# 延迟导入
def process_data():
    import math
    import random
    return math.sqrt(random.randint(1, 100))

# 动态导入
def dynamic_import_example():
    module_name = "json"
    json_module = __import__(module_name)
    
    import importlib
    math_module = importlib.import_module("math")
    
    return json_module, math_module

def main():
    print("Hello from test script!")
    
    if HAS_PYQT5:
        print("PyQt5 is available")
    
    if HAS_REQUESTS:
        print("Requests is available")
    
    result = process_data()
    print(f"Processed data: {result}")
    
    json_mod, math_mod = dynamic_import_example()
    print(f"Dynamic imports: {json_mod.__name__}, {math_mod.__name__}")

if __name__ == "__main__":
    main()
'''
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_script_content)
        return f.name

class TestMainWindow(QMainWindow):
    """测试主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("增强模块标签页测试")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建配置和模型
        self.config = AppConfig()
        self.model = PyInstallerModel(self.config)
        
        # 设置测试脚本
        self.test_script = create_test_script()
        self.model.script_path = self.test_script
        
        print(f"创建测试脚本: {self.test_script}")
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 创建增强模块标签页
        self.enhanced_module_tab = EnhancedModuleTab(self.model, self.config)
        layout.addWidget(self.enhanced_module_tab)
        
        # 连接信号
        self.enhanced_module_tab.analysis_finished.connect(self.on_analysis_finished)
        
        # 设置定时器自动开始分析（用于演示）
        QTimer.singleShot(2000, self.auto_start_analysis)
    
    def auto_start_analysis(self):
        """自动开始分析（用于演示）"""
        print("自动开始分析...")
        self.enhanced_module_tab.start_analysis()
    
    def on_analysis_finished(self, result):
        """分析完成处理"""
        print("分析完成!")
        
        precise_result = result['precise_analysis']
        dynamic_result = result['dynamic_analysis']
        
        print(f"标准库模块: {len(precise_result.standard_modules)} 个")
        print(f"第三方库模块: {len(precise_result.third_party_modules)} 个")
        print(f"本地模块: {len(precise_result.local_modules)} 个")
        print(f"缺失模块: {len(precise_result.missing_modules)} 个")
        
        if precise_result.recommendations:
            print(f"建议: {len(precise_result.recommendations)} 条")
        
        dynamic_data = dynamic_result.get('dynamic_result')
        if dynamic_data:
            print(f"条件导入: {len(dynamic_data.conditional_modules)} 个")
            print(f"延迟导入: {len(dynamic_data.lazy_imports)} 个")
            print(f"可选模块: {len(dynamic_data.optional_modules)} 个")
    
    def closeEvent(self, event):
        """关闭事件"""
        # 清理测试文件
        try:
            if hasattr(self, 'test_script') and os.path.exists(self.test_script):
                os.unlink(self.test_script)
                print(f"清理测试脚本: {self.test_script}")
        except:
            pass
        
        event.accept()

def main():
    """主函数"""
    print("🚀 启动增强模块标签页测试")
    
    app = QApplication(sys.argv)
    app.setApplicationName("增强模块标签页测试")
    
    # 创建主窗口
    window = TestMainWindow()
    window.show()
    
    print("✅ 测试窗口已启动")
    print("💡 提示: 窗口将在2秒后自动开始分析")
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
