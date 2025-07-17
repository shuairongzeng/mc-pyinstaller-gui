"""
自定义异常类
"""

class PyInstallerGUIException(Exception):
    """PyInstaller GUI 基础异常类"""
    pass

class ConfigurationError(PyInstallerGUIException):
    """配置错误异常"""
    pass

class PackageError(PyInstallerGUIException):
    """打包错误异常"""
    pass

class ModuleDetectionError(PyInstallerGUIException):
    """模块检测错误异常"""
    pass

class FileNotFoundError(PyInstallerGUIException):
    """文件未找到异常"""
    pass

class ValidationError(PyInstallerGUIException):
    """验证错误异常"""
    pass

class ServiceError(PyInstallerGUIException):
    """服务错误异常"""
    pass
