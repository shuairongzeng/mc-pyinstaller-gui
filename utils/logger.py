"""
日志系统
"""
import logging
import os
import sys
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler

class Logger:
    """日志管理器"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self) -> None:
        """设置日志器"""
        self._logger = logging.getLogger("PyInstallerGUI")
        self._logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if self._logger.handlers:
            return
        
        # 创建日志目录
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 文件处理器
        log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # 添加处理器
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        """调试日志"""
        self._logger.debug(message)
    
    def info(self, message: str) -> None:
        """信息日志"""
        self._logger.info(message)
    
    def warning(self, message: str) -> None:
        """警告日志"""
        self._logger.warning(message)
    
    def error(self, message: str) -> None:
        """错误日志"""
        self._logger.error(message)
    
    def critical(self, message: str) -> None:
        """严重错误日志"""
        self._logger.critical(message)
    
    def exception(self, message: str) -> None:
        """异常日志"""
        self._logger.exception(message)

# 全局日志实例
logger = Logger()

def log_debug(message: str) -> None:
    """调试日志"""
    logger.debug(message)

def log_info(message: str) -> None:
    """信息日志"""
    logger.info(message)

def log_warning(message: str) -> None:
    """警告日志"""
    logger.warning(message)

def log_error(message: str) -> None:
    """错误日志"""
    logger.error(message)

def log_critical(message: str) -> None:
    """严重错误日志"""
    logger.critical(message)

def log_exception(message: str) -> None:
    """异常日志"""
    logger.exception(message)


class ErrorReporter:
    """错误报告系统"""

    def __init__(self):
        self.logger = logging.getLogger("ErrorReporter")
        self.error_reports_dir = "logs/error_reports"
        os.makedirs(self.error_reports_dir, exist_ok=True)

    def generate_error_report(self, error_type: str, error_message: str,
                            context: dict = None, stack_trace: str = None) -> str:
        """生成详细的错误报告"""
        import platform
        import sys
        from datetime import datetime

        context = context or {}

        # 生成报告ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = f"error_{timestamp}_{hash(error_message) % 10000:04d}"

        # 收集系统信息
        system_info = {
            'platform': platform.platform(),
            'python_version': sys.version,
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'memory': self._get_memory_info(),
            'disk_space': self._get_disk_space()
        }

        # 收集应用信息
        app_info = {
            'app_name': 'PyInstaller GUI',
            'app_version': '1.0.1',
            'working_directory': os.getcwd(),
            'python_path': sys.path[:5],  # 只取前5个路径
            'environment_variables': dict(os.environ)
        }

        # 生成报告内容
        report_content = f"""
# 错误报告 - {report_id}

## 基本信息
- 报告ID: {report_id}
- 时间: {datetime.now().isoformat()}
- 错误类型: {error_type}
- 错误消息: {error_message}

## 系统信息
- 操作系统: {system_info['platform']}
- Python版本: {system_info['python_version']}
- 系统架构: {system_info['architecture']}
- 处理器: {system_info['processor']}
- 内存信息: {system_info['memory']}
- 磁盘空间: {system_info['disk_space']}

## 应用信息
- 应用名称: {app_info['app_name']}
- 应用版本: {app_info['app_version']}
- 工作目录: {app_info['working_directory']}
- Python路径: {app_info['python_path']}

## 上下文信息
"""

        # 添加上下文信息
        for key, value in context.items():
            report_content += f"- {key}: {value}\n"

        # 添加堆栈跟踪
        if stack_trace:
            report_content += f"\n## 堆栈跟踪\n```\n{stack_trace}\n```\n"

        # 添加环境变量（敏感信息过滤）
        report_content += "\n## 环境变量\n"
        sensitive_keys = ['PASSWORD', 'TOKEN', 'KEY', 'SECRET']
        for key, value in app_info['environment_variables'].items():
            if any(sensitive in key.upper() for sensitive in sensitive_keys):
                value = "***HIDDEN***"
            report_content += f"- {key}: {value}\n"

        # 保存报告文件
        report_file = os.path.join(self.error_reports_dir, f"{report_id}.md")
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            self.logger.info(f"错误报告已生成: {report_file}")
        except Exception as e:
            self.logger.error(f"生成错误报告失败: {e}")

        return report_id

    def _get_memory_info(self) -> str:
        """获取内存信息"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return f"总内存: {memory.total // (1024**3)}GB, 可用: {memory.available // (1024**3)}GB, 使用率: {memory.percent}%"
        except ImportError:
            return "psutil未安装，无法获取内存信息"
        except Exception as e:
            return f"获取内存信息失败: {e}"

    def _get_disk_space(self) -> str:
        """获取磁盘空间信息"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            return f"总空间: {total // (1024**3)}GB, 已用: {used // (1024**3)}GB, 可用: {free // (1024**3)}GB"
        except Exception as e:
            return f"获取磁盘空间失败: {e}"

    def list_error_reports(self) -> list:
        """列出所有错误报告"""
        try:
            reports = []
            for filename in os.listdir(self.error_reports_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(self.error_reports_dir, filename)
                    stat = os.stat(filepath)
                    reports.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime)
                    })
            return sorted(reports, key=lambda x: x['created'], reverse=True)
        except Exception as e:
            self.logger.error(f"列出错误报告失败: {e}")
            return []

    def cleanup_old_reports(self, max_reports: int = 50):
        """清理旧的错误报告"""
        try:
            reports = self.list_error_reports()
            if len(reports) > max_reports:
                for report in reports[max_reports:]:
                    os.remove(report['filepath'])
                    self.logger.info(f"删除旧错误报告: {report['filename']}")
        except Exception as e:
            self.logger.error(f"清理错误报告失败: {e}")


# 全局错误报告实例
_error_reporter: Optional[ErrorReporter] = None


def get_error_reporter() -> ErrorReporter:
    """获取错误报告实例"""
    global _error_reporter
    if _error_reporter is None:
        _error_reporter = ErrorReporter()
    return _error_reporter


def report_error(error_type: str, error_message: str, context: dict = None, stack_trace: str = None) -> str:
    """报告错误并生成报告"""
    reporter = get_error_reporter()
    return reporter.generate_error_report(error_type, error_message, context, stack_trace)
