"""
自定义异常类和全局异常处理器
"""
import sys
import traceback
import logging
import os
from typing import Optional, Dict, Any, List, Callable
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QObject, pyqtSignal


class PyInstallerGUIException(Exception):
    """PyInstaller GUI 基础异常类"""

    def __init__(self, message: str, error_code: str = None, suggestions: List[str] = None):
        super().__init__(message)
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.suggestions = suggestions or []


class ConfigurationError(PyInstallerGUIException):
    """配置错误异常"""

    def __init__(self, message: str, field: str = None, suggestions: List[str] = None):
        super().__init__(message, "CONFIG_ERROR", suggestions)
        self.field = field


class PackageError(PyInstallerGUIException):
    """打包错误异常"""

    def __init__(self, message: str, command: str = None, suggestions: List[str] = None):
        super().__init__(message, "PACKAGE_ERROR", suggestions)
        self.command = command


class ModuleDetectionError(PyInstallerGUIException):
    """模块检测错误异常"""

    def __init__(self, message: str, module_name: str = None, suggestions: List[str] = None):
        super().__init__(message, "MODULE_ERROR", suggestions)
        self.module_name = module_name


class FileNotFoundError(PyInstallerGUIException):
    """文件未找到异常"""

    def __init__(self, message: str, file_path: str = None, suggestions: List[str] = None):
        super().__init__(message, "FILE_NOT_FOUND", suggestions)
        self.file_path = file_path


class ValidationError(PyInstallerGUIException):
    """验证错误异常"""

    def __init__(self, message: str, field: str = None, suggestions: List[str] = None):
        super().__init__(message, "VALIDATION_ERROR", suggestions)
        self.field = field


class ServiceError(PyInstallerGUIException):
    """服务错误异常"""

    def __init__(self, message: str, service_name: str = None, suggestions: List[str] = None):
        super().__init__(message, "SERVICE_ERROR", suggestions)
        self.service_name = service_name


class GlobalExceptionHandler(QObject):
    """全局异常处理器"""

    exception_occurred = pyqtSignal(str, str, dict)  # 异常类型, 异常信息, 解决方案

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.error_solutions = self._load_error_solutions()
        self._original_excepthook = sys.excepthook

        # 设置全局异常处理
        sys.excepthook = self.handle_exception

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 允许Ctrl+C正常退出
            self._original_excepthook(exc_type, exc_value, exc_traceback)
            return

        # 格式化异常信息
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        error_type = exc_type.__name__

        # 记录日志
        self.logger.error(f"未处理的异常: {error_type}\n{error_msg}")

        # 查找解决方案
        solution = self._find_solution(error_type, str(exc_value))

        # 发送信号
        self.exception_occurred.emit(error_type, str(exc_value), solution or {})

        # 显示用户友好的错误对话框
        self._show_error_dialog(error_type, str(exc_value), solution)

    def _load_error_solutions(self) -> Dict[str, Dict[str, Any]]:
        """加载错误解决方案"""
        return {
            'ModuleNotFoundError': {
                'pattern': 'No module named',
                'solution': '缺少必要的Python模块',
                'actions': [
                    '检查requirements.txt文件',
                    '运行: pip install -r requirements.txt',
                    '确认虚拟环境已激活',
                    '检查模块名称拼写是否正确'
                ],
                'severity': 'high'
            },
            'FileNotFoundError': {
                'pattern': 'No such file or directory',
                'solution': '找不到指定的文件或目录',
                'actions': [
                    '检查文件路径是否正确',
                    '确认文件是否存在',
                    '检查文件权限',
                    '使用绝对路径而非相对路径'
                ],
                'severity': 'high'
            },
            'PermissionError': {
                'pattern': 'Permission denied',
                'solution': '权限不足',
                'actions': [
                    '以管理员身份运行程序',
                    '检查文件/目录权限',
                    '确认文件未被其他程序占用',
                    '检查防病毒软件是否阻止访问'
                ],
                'severity': 'medium'
            },
            'ImportError': {
                'pattern': 'cannot import name',
                'solution': '模块导入错误',
                'actions': [
                    '检查模块是否正确安装',
                    '确认Python版本兼容性',
                    '检查模块版本是否匹配',
                    '重新安装相关模块'
                ],
                'severity': 'high'
            },
            'AttributeError': {
                'pattern': 'has no attribute',
                'solution': '属性或方法不存在',
                'actions': [
                    '检查对象类型是否正确',
                    '确认属性名称拼写',
                    '检查模块版本兼容性',
                    '查看相关文档确认API'
                ],
                'severity': 'medium'
            },
            'TypeError': {
                'pattern': 'argument',
                'solution': '参数类型或数量错误',
                'actions': [
                    '检查函数调用参数',
                    '确认参数类型正确',
                    '检查参数数量是否匹配',
                    '查看函数文档确认用法'
                ],
                'severity': 'medium'
            },
            'ValueError': {
                'pattern': 'invalid literal',
                'solution': '数值转换或格式错误',
                'actions': [
                    '检查输入数据格式',
                    '确认数值范围有效',
                    '添加数据验证',
                    '处理异常输入情况'
                ],
                'severity': 'low'
            },
            'OSError': {
                'pattern': 'WinError',
                'solution': '操作系统相关错误',
                'actions': [
                    '检查系统资源使用情况',
                    '确认文件路径长度限制',
                    '检查磁盘空间是否充足',
                    '重启程序或系统'
                ],
                'severity': 'high'
            }
        }

    def _find_solution(self, error_type: str, error_message: str) -> Optional[Dict[str, Any]]:
        """查找错误解决方案"""
        # 精确匹配错误类型
        if error_type in self.error_solutions:
            solution = self.error_solutions[error_type]
            if solution['pattern'] in error_message:
                return solution

        # 模糊匹配错误信息
        for solution_type, solution in self.error_solutions.items():
            if solution['pattern'].lower() in error_message.lower():
                return solution

        return None

    def _show_error_dialog(self, error_type: str, error_message: str, solution: Optional[Dict]):
        """显示错误对话框"""
        try:
            app = QApplication.instance()
            if not app:
                return

            # 创建错误对话框
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("程序错误")

            # 设置主要信息
            msg_box.setText(f"程序遇到了一个错误：{error_type}")

            # 设置详细信息
            if solution:
                detail_text = f"错误描述：{error_message}\n\n"
                detail_text += f"可能的解决方案：{solution['solution']}\n\n"
                detail_text += "建议操作：\n"
                for i, action in enumerate(solution['actions'], 1):
                    detail_text += f"{i}. {action}\n"
            else:
                detail_text = f"错误详情：{error_message}\n\n"
                detail_text += "建议：\n1. 重启程序\n2. 检查日志文件\n3. 联系技术支持"

            msg_box.setDetailedText(detail_text)

            # 添加按钮
            msg_box.addButton("确定", QMessageBox.AcceptRole)
            if solution and 'auto_fix' in solution:
                msg_box.addButton("自动修复", QMessageBox.ActionRole)

            msg_box.exec_()

        except Exception as e:
            # 异常处理器本身出错时的后备方案
            print(f"异常处理器错误: {e}")
            print(f"原始错误: {error_type}: {error_message}")

    def restore_original_excepthook(self):
        """恢复原始的异常处理"""
        sys.excepthook = self._original_excepthook


# 全局异常处理器实例
_global_exception_handler: Optional[GlobalExceptionHandler] = None


def setup_global_exception_handler() -> GlobalExceptionHandler:
    """设置全局异常处理器"""
    global _global_exception_handler
    if _global_exception_handler is None:
        _global_exception_handler = GlobalExceptionHandler()
    return _global_exception_handler


def get_global_exception_handler() -> Optional[GlobalExceptionHandler]:
    """获取全局异常处理器实例"""
    return _global_exception_handler


def handle_exception_with_dialog(exc_type, exc_value, suggestions: List[str] = None):
    """处理异常并显示用户友好的对话框"""
    try:
        app = QApplication.instance()
        if not app:
            print(f"异常: {exc_type.__name__}: {exc_value}")
            return

        # 创建自定义异常实例
        if issubclass(exc_type, PyInstallerGUIException):
            exception = exc_value
        else:
            exception = PyInstallerGUIException(str(exc_value), suggestions=suggestions or [])

        # 显示错误对话框
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("操作失败")
        msg_box.setText(f"操作失败：{exception}")

        if exception.suggestions:
            detail_text = "建议的解决方案：\n"
            for i, suggestion in enumerate(exception.suggestions, 1):
                detail_text += f"{i}. {suggestion}\n"
            msg_box.setDetailedText(detail_text)

        msg_box.exec_()

    except Exception as e:
        print(f"异常处理失败: {e}")
        print(f"原始异常: {exc_type.__name__}: {exc_value}")


def safe_execute(func: Callable, *args, error_message: str = "操作失败", suggestions: List[str] = None, **kwargs):
    """安全执行函数，自动处理异常"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_exception_with_dialog(type(e), e, suggestions)
        return None
