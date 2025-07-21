"""
错误处理增强功能测试脚本
"""
import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSlot

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.exceptions import (
    setup_global_exception_handler, 
    PyInstallerGUIException,
    ConfigurationError,
    PackageError,
    ModuleDetectionError,
    handle_exception_with_dialog
)
from utils.error_diagnostics import get_error_diagnostics, diagnose_and_suggest, try_auto_fix
from utils.logger import get_error_reporter
from views.components.error_dialog import show_error_dialog


class ErrorTestWindow(QMainWindow):
    """错误处理测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("错误处理增强功能测试")
        self.setGeometry(100, 100, 600, 400)
        
        # 设置全局异常处理器
        self.exception_handler = setup_global_exception_handler()
        self.exception_handler.exception_occurred.connect(self.on_global_exception)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 测试按钮
        test_buttons = [
            ("测试模块未找到错误", self.test_module_not_found),
            ("测试文件未找到错误", self.test_file_not_found),
            ("测试权限错误", self.test_permission_error),
            ("测试配置错误", self.test_configuration_error),
            ("测试打包错误", self.test_package_error),
            ("测试未知错误", self.test_unknown_error),
            ("测试错误诊断", self.test_error_diagnosis),
            ("测试自动修复", self.test_auto_fix),
            ("测试错误报告", self.test_error_report),
            ("测试错误对话框", self.test_error_dialog)
        ]
        
        for text, handler in test_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
    
    @pyqtSlot(str, str, dict)
    def on_global_exception(self, error_type: str, error_message: str, solution: dict):
        """处理全局异常"""
        print(f"全局异常捕获: {error_type}: {error_message}")
        if solution:
            print(f"解决方案: {solution}")
    
    def test_module_not_found(self):
        """测试模块未找到错误"""
        try:
            import nonexistent_module
        except ImportError as e:
            handle_exception_with_dialog(
                type(e), e, 
                ["使用pip安装模块", "检查模块名称拼写", "确认虚拟环境已激活"]
            )
    
    def test_file_not_found(self):
        """测试文件未找到错误"""
        try:
            with open("nonexistent_file.txt", "r") as f:
                content = f.read()
        except FileNotFoundError as e:
            handle_exception_with_dialog(
                type(e), e,
                ["检查文件路径", "确认文件存在", "使用绝对路径"]
            )
    
    def test_permission_error(self):
        """测试权限错误"""
        try:
            # 尝试写入系统目录（通常会失败）
            with open("C:\\Windows\\test.txt", "w") as f:
                f.write("test")
        except PermissionError as e:
            handle_exception_with_dialog(
                type(e), e,
                ["以管理员身份运行", "检查文件权限", "使用用户目录"]
            )
        except Exception as e:
            # 在非Windows系统上可能是其他错误
            handle_exception_with_dialog(
                type(e), e,
                ["检查文件权限", "确认目录可写"]
            )
    
    def test_configuration_error(self):
        """测试配置错误"""
        error = ConfigurationError(
            "脚本路径配置无效",
            field="script_path",
            suggestions=["选择有效的Python脚本文件", "检查文件扩展名", "确认文件可读"]
        )
        handle_exception_with_dialog(type(error), error)
    
    def test_package_error(self):
        """测试打包错误"""
        error = PackageError(
            "PyInstaller执行失败",
            command="pyinstaller --onefile test.py",
            suggestions=["检查PyInstaller版本", "清理build目录", "添加隐藏导入"]
        )
        handle_exception_with_dialog(type(error), error)
    
    def test_unknown_error(self):
        """测试未知错误"""
        try:
            # 故意引发一个未处理的异常
            result = 1 / 0
        except ZeroDivisionError as e:
            # 这会被全局异常处理器捕获
            raise e
    
    def test_error_diagnosis(self):
        """测试错误诊断功能"""
        print("\n=== 错误诊断测试 ===")
        
        # 测试模块未找到错误诊断
        diagnosis = diagnose_and_suggest(
            "ModuleNotFoundError",
            "No module named 'numpy'",
            {"script_path": "test.py"}
        )
        
        print(f"错误类型: {diagnosis['error_type']}")
        print(f"严重程度: {diagnosis['severity']}")
        print(f"根本原因: {diagnosis['root_cause']}")
        print(f"解决方案: {diagnosis['solutions']}")
        print(f"自动修复可用: {diagnosis['auto_fix_available']}")
        
        # 测试文件未找到错误诊断
        diagnosis2 = diagnose_and_suggest(
            "FileNotFoundError",
            "No such file or directory: 'config.json'",
            {"file_path": "config.json"}
        )
        
        print(f"\n文件错误诊断:")
        print(f"解决方案: {diagnosis2['solutions']}")
    
    def test_auto_fix(self):
        """测试自动修复功能"""
        print("\n=== 自动修复测试 ===")
        
        # 测试模块自动安装
        success, message = try_auto_fix(
            "ModuleNotFoundError",
            "No module named 'requests'",
            {"module_name": "requests"}
        )
        
        print(f"自动修复结果: {success}")
        print(f"修复消息: {message}")
        
        # 测试文件路径修复
        success2, message2 = try_auto_fix(
            "FileNotFoundError",
            "No such file or directory: 'logs/test.log'",
            {"file_path": "logs/test.log"}
        )
        
        print(f"文件修复结果: {success2}")
        print(f"文件修复消息: {message2}")
    
    def test_error_report(self):
        """测试错误报告功能"""
        print("\n=== 错误报告测试 ===")
        
        reporter = get_error_reporter()
        
        # 生成测试错误报告
        report_id = reporter.generate_error_report(
            "TestError",
            "这是一个测试错误",
            {
                "test_context": "error_handling_test",
                "user_action": "点击测试按钮",
                "system_state": "正常"
            },
            traceback.format_exc()
        )
        
        print(f"错误报告已生成: {report_id}")
        
        # 列出所有错误报告
        reports = reporter.list_error_reports()
        print(f"总共有 {len(reports)} 个错误报告")
        
        if reports:
            latest = reports[0]
            print(f"最新报告: {latest['filename']}")
            print(f"创建时间: {latest['created']}")
            print(f"文件大小: {latest['size']} 字节")
    
    def test_error_dialog(self):
        """测试错误对话框"""
        print("\n=== 错误对话框测试 ===")
        
        # 显示带自动修复的错误对话框
        context = {
            "operation": "测试操作",
            "script_path": "test.py",
            "current_tab": 0
        }
        
        show_error_dialog(
            "ModuleNotFoundError",
            "No module named 'pandas'",
            context,
            self
        )


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = ErrorTestWindow()
    window.show()
    
    print("错误处理增强功能测试程序已启动")
    print("点击按钮测试不同的错误处理功能")
    print("查看控制台输出和错误对话框")
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
