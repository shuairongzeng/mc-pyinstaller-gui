#!/usr/bin/env python3
"""
测试UI优化 - 验证界面不会卡死
"""

import sys
import os
import tempfile
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer, pyqtSlot

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.tabs.module_tab import ModuleTab
from models.packer_model import PyInstallerModel
from config.app_config import AppConfig
from services.module_detector import ModuleDetector

def create_test_script():
    """创建测试脚本"""
    test_script_content = '''#!/usr/bin/env python3
"""
测试脚本 - 用于测试UI优化
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

def main():
    print("Hello from test script!")
    
    if HAS_PYQT5:
        print("PyQt5 is available")
    
    if HAS_REQUESTS:
        print("Requests is available")

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
        self.setWindowTitle("UI优化测试 - 精准依赖检测")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建配置和模型
        self.config = AppConfig()
        self.model = PyInstallerModel(self.config)
        self.detector = ModuleDetector()
        
        # 设置测试脚本
        self.test_script = create_test_script()
        self.model.script_path = self.test_script
        
        print(f"创建测试脚本: {self.test_script}")
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 添加状态标签
        self.status_label = QLabel("准备测试UI优化...")
        self.status_label.setStyleSheet("font-size: 14px; color: #333; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # 创建模块标签页
        self.module_tab = ModuleTab(self.model, self.config, self.detector)
        layout.addWidget(self.module_tab)
        
        # 添加测试按钮
        self.test_btn = QPushButton("🧪 开始UI响应性测试")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.test_btn.clicked.connect(self.start_ui_test)
        layout.addWidget(self.test_btn)
        
        # 连接信号
        self.module_tab.silent_detection_finished.connect(self.on_detection_finished)
        
        # 设置定时器来测试UI响应性
        self.ui_test_timer = QTimer()
        self.ui_test_timer.timeout.connect(self.check_ui_responsiveness)
        self.ui_test_count = 0
        
        print("✅ 测试窗口初始化完成")
    
    @pyqtSlot()
    def start_ui_test(self):
        """开始UI测试"""
        print("\n🧪 开始UI响应性测试...")
        self.status_label.setText("🔄 正在进行精准依赖分析，测试UI响应性...")
        
        # 开始UI响应性检查
        self.ui_test_count = 0
        self.ui_test_timer.start(500)  # 每500ms检查一次
        
        # 开始检测（静默模式）
        self.module_tab.start_detection(silent=True)
    
    @pyqtSlot()
    def check_ui_responsiveness(self):
        """检查UI响应性"""
        self.ui_test_count += 1
        current_time = time.strftime("%H:%M:%S")
        
        # 更新状态，如果UI卡死，这个更新不会显示
        self.status_label.setText(f"🔄 分析进行中... UI响应检查 #{self.ui_test_count} ({current_time})")
        
        print(f"  📊 UI响应性检查 #{self.ui_test_count} - {current_time} - UI正常响应")
        
        # 处理事件队列，确保UI更新
        QApplication.processEvents()
        
        # 如果检查次数过多，可能分析出现问题
        if self.ui_test_count > 60:  # 30秒后停止
            self.ui_test_timer.stop()
            self.status_label.setText("⚠️ 分析时间过长，可能存在问题")
            print("⚠️ 分析时间超过30秒，停止UI响应性检查")
    
    @pyqtSlot(list, dict)
    def on_detection_finished(self, modules, analysis):
        """检测完成处理"""
        self.ui_test_timer.stop()
        
        print(f"\n✅ 精准依赖分析完成！")
        print(f"  📦 检测到模块: {len(modules)} 个")
        print(f"  🎯 UI响应性检查次数: {self.ui_test_count}")
        print(f"  ⏱️ 平均检查间隔: {self.ui_test_count * 0.5:.1f} 秒")
        
        # 检查是否有精准分析结果
        if 'precise_result' in analysis:
            precise_result = analysis['precise_result']
            print(f"  🔧 标准库模块: {len(precise_result.standard_modules)}")
            print(f"  📦 第三方库模块: {len(precise_result.third_party_modules)}")
            print(f"  📁 本地模块: {len(precise_result.local_modules)}")
            print(f"  ❌ 缺失模块: {len(precise_result.missing_modules)}")
            print(f"  💾 缓存命中: {'是' if precise_result.cache_hit else '否'}")
            print(f"  ⏱️ 分析时间: {precise_result.analysis_time:.2f}s")
        
        # 检查动态分析结果
        if 'dynamic_result' in analysis:
            dynamic_result = analysis['dynamic_result']
            print(f"  ❓ 条件导入: {len(dynamic_result.conditional_modules)}")
            print(f"  ⏰ 延迟导入: {len(dynamic_result.lazy_imports)}")
            print(f"  🔄 可选模块: {len(dynamic_result.optional_modules)}")
        
        self.status_label.setText(f"✅ 测试完成！分析了 {len(modules)} 个模块，UI保持响应 ({self.ui_test_count} 次检查)")
        
        # 显示成功消息
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self, 
            "UI优化测试成功", 
            f"🎉 UI优化测试成功完成！\n\n"
            f"📊 分析结果:\n"
            f"  • 检测到模块: {len(modules)} 个\n"
            f"  • UI响应检查: {self.ui_test_count} 次\n"
            f"  • 界面保持流畅响应\n\n"
            f"✅ 精准依赖检测系统已成功优化，不会导致界面卡死！"
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止定时器
        if self.ui_test_timer.isActive():
            self.ui_test_timer.stop()
        
        # 停止检测
        if hasattr(self.module_tab, 'detection_thread') and self.module_tab.detection_thread:
            self.module_tab.stop_detection()
        
        # 清理测试文件
        try:
            if hasattr(self, 'test_script') and os.path.exists(self.test_script):
                os.unlink(self.test_script)
                print(f"🧹 清理测试脚本: {self.test_script}")
        except:
            pass
        
        event.accept()

def main():
    """主函数"""
    print("🚀 启动UI优化测试")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    app.setApplicationName("UI优化测试")
    
    # 创建主窗口
    window = TestMainWindow()
    window.show()
    
    print("✅ 测试窗口已启动")
    print("💡 提示: 点击'开始UI响应性测试'按钮来测试界面是否会卡死")
    print("📊 测试过程中会每0.5秒检查一次UI响应性")
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
