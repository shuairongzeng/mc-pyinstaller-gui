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
