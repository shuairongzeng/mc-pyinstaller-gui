# 代码质量改进方案

## 🎯 代码质量现状分析

### 发现的主要问题

1. **模块耦合度较高**
   - 部分类直接依赖具体实现而非接口
   - 循环导入的潜在风险
   - 职责边界不够清晰

2. **错误处理不够统一**
   - 异常处理方式不一致
   - 缺少统一的错误码定义
   - 用户友好的错误信息需要改进

3. **代码复用性有待提高**
   - 存在重复代码片段
   - 缺少通用工具函数
   - 配置管理分散

4. **类型注解不完整**
   - 部分函数缺少类型注解
   - 返回值类型不明确
   - 影响IDE智能提示

## 🚀 具体改进方案

### 1. 统一错误处理机制

#### 1.1 错误码定义
```python
# utils/error_codes.py
from enum import Enum

class ErrorCode(Enum):
    # 通用错误 (1000-1999)
    UNKNOWN_ERROR = (1000, "未知错误")
    INVALID_PARAMETER = (1001, "参数无效")
    PERMISSION_DENIED = (1002, "权限不足")
    
    # 文件相关错误 (2000-2999)
    FILE_NOT_FOUND = (2000, "文件未找到")
    FILE_ACCESS_DENIED = (2001, "文件访问被拒绝")
    FILE_CORRUPTED = (2002, "文件已损坏")
    
    # 打包相关错误 (3000-3999)
    PACKAGING_FAILED = (3000, "打包失败")
    DEPENDENCY_MISSING = (3001, "依赖缺失")
    PYINSTALLER_NOT_FOUND = (3002, "PyInstaller未安装")
    
    # 配置相关错误 (4000-4999)
    CONFIG_INVALID = (4000, "配置无效")
    CONFIG_LOAD_FAILED = (4001, "配置加载失败")
    
    def __init__(self, code, message):
        self.code = code
        self.message = message

class AppException(Exception):
    """应用程序基础异常类"""
    
    def __init__(self, error_code: ErrorCode, details: str = None, suggestions: list = None):
        self.error_code = error_code
        self.details = details or ""
        self.suggestions = suggestions or []
        
        message = f"[{error_code.code}] {error_code.message}"
        if details:
            message += f": {details}"
        
        super().__init__(message)
    
    def to_dict(self):
        return {
            "code": self.error_code.code,
            "message": self.error_code.message,
            "details": self.details,
            "suggestions": self.suggestions
        }

# 具体异常类
class PackagingException(AppException):
    def __init__(self, details: str = None, suggestions: list = None):
        super().__init__(ErrorCode.PACKAGING_FAILED, details, suggestions)

class ConfigurationException(AppException):
    def __init__(self, details: str = None, suggestions: list = None):
        super().__init__(ErrorCode.CONFIG_INVALID, details, suggestions)
```

#### 1.2 统一错误处理装饰器
```python
# utils/error_handler.py
import functools
import logging
from typing import Callable, Any, Optional, Type
from .error_codes import AppException, ErrorCode

logger = logging.getLogger(__name__)

def handle_exceptions(
    default_return: Any = None,
    exceptions: tuple = (Exception,),
    log_error: bool = True,
    reraise: bool = False
):
    """统一异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                
                if isinstance(e, AppException):
                    if reraise:
                        raise
                    return default_return
                else:
                    # 将普通异常转换为应用异常
                    app_exception = AppException(
                        ErrorCode.UNKNOWN_ERROR,
                        str(e),
                        ["请检查日志获取详细信息", "如果问题持续，请联系技术支持"]
                    )
                    if reraise:
                        raise app_exception
                    return default_return
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
    """安全执行函数，返回(成功标志, 结果)"""
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        logger.error(f"Safe execution failed: {str(e)}")
        return False, e
```

### 2. 类型注解完善

#### 2.1 核心类型定义
```python
# types/common_types.py
from typing import Dict, List, Optional, Union, Callable, Any, TypeVar, Generic
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# 基础类型别名
FilePath = Union[str, Path]
ConfigDict = Dict[str, Any]
ModuleSet = set[str]
CallbackFunction = Callable[[str], None]

# 打包相关类型
class PackageType(Enum):
    ONE_FILE = "onefile"
    ONE_DIR = "onedir"

class WindowType(Enum):
    CONSOLE = "console"
    WINDOWED = "windowed"

@dataclass
class PackageConfig:
    """打包配置数据类"""
    script_path: FilePath
    output_dir: FilePath
    package_type: PackageType
    window_type: WindowType
    icon_path: Optional[FilePath] = None
    additional_files: List[FilePath] = None
    hidden_imports: List[str] = None
    exclude_modules: List[str] = None
    upx_enabled: bool = False
    clean_build: bool = True
    
    def __post_init__(self):
        if self.additional_files is None:
            self.additional_files = []
        if self.hidden_imports is None:
            self.hidden_imports = []
        if self.exclude_modules is None:
            self.exclude_modules = []

@dataclass
class DetectionResult:
    """模块检测结果"""
    modules: ModuleSet
    hidden_imports: List[str]
    data_files: List[tuple[str, str]]
    collect_all: List[str]
    detection_time: float
    cache_hit: bool = False
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

# 泛型类型
T = TypeVar('T')

class Result(Generic[T]):
    """结果包装类，用于统一处理成功和失败情况"""
    
    def __init__(self, success: bool, data: Optional[T] = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error
    
    @classmethod
    def ok(cls, data: T) -> 'Result[T]':
        return cls(True, data)
    
    @classmethod
    def fail(cls, error: str) -> 'Result[T]':
        return cls(False, None, error)
    
    def is_ok(self) -> bool:
        return self.success
    
    def is_err(self) -> bool:
        return not self.success
    
    def unwrap(self) -> T:
        if not self.success:
            raise ValueError(f"Result is not ok: {self.error}")
        return self.data
    
    def unwrap_or(self, default: T) -> T:
        return self.data if self.success else default
```

#### 2.2 改进现有类的类型注解
```python
# 示例：改进 PackageService 类
from typing import Optional, Callable, Dict, Any
from PyQt5.QtCore import QThread, pyqtSignal
from .types.common_types import PackageConfig, Result, CallbackFunction

class PackageService(QThread):
    """打包服务类 - 类型注解完善版"""
    
    # 信号定义
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal(int)
    
    def __init__(
        self, 
        config: PackageConfig,
        python_interpreter: Optional[str] = None,
        timeout: int = 600
    ) -> None:
        super().__init__()
        self.config = config
        self.python_interpreter = python_interpreter
        self.timeout = timeout
        self._is_cancelled = False
    
    def start_packaging(self) -> Result[bool]:
        """开始打包过程"""
        try:
            validation_result = self._validate_config()
            if not validation_result.is_ok():
                return Result.fail(validation_result.error)
            
            self.start()
            return Result.ok(True)
        except Exception as e:
            return Result.fail(str(e))
    
    def _validate_config(self) -> Result[bool]:
        """验证配置"""
        if not self.config.script_path:
            return Result.fail("脚本路径不能为空")
        
        if not Path(self.config.script_path).exists():
            return Result.fail(f"脚本文件不存在: {self.config.script_path}")
        
        return Result.ok(True)
    
    def cancel(self) -> None:
        """取消打包"""
        self._is_cancelled = True
        self.terminate()
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "is_running": self.isRunning(),
            "is_cancelled": self._is_cancelled,
            "config": self.config.__dict__
        }
```

### 3. 代码复用性改进

#### 3.1 通用工具函数库
```python
# utils/common_utils.py
import os
import hashlib
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from .types.common_types import FilePath, Result

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_dir(path: FilePath) -> Result[Path]:
        """确保目录存在"""
        try:
            dir_path = Path(path)
            dir_path.mkdir(parents=True, exist_ok=True)
            return Result.ok(dir_path)
        except Exception as e:
            return Result.fail(f"创建目录失败: {str(e)}")
    
    @staticmethod
    def calculate_file_hash(file_path: FilePath, algorithm: str = 'md5') -> Result[str]:
        """计算文件哈希值"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return Result.ok(hash_obj.hexdigest())
        except Exception as e:
            return Result.fail(f"计算文件哈希失败: {str(e)}")
    
    @staticmethod
    def copy_file_safe(src: FilePath, dst: FilePath) -> Result[Path]:
        """安全复制文件"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.exists():
                return Result.fail(f"源文件不存在: {src}")
            
            # 确保目标目录存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, dst_path)
            return Result.ok(dst_path)
        except Exception as e:
            return Result.fail(f"复制文件失败: {str(e)}")
    
    @staticmethod
    def get_file_size_human(file_path: FilePath) -> str:
        """获取人类可读的文件大小"""
        try:
            size = Path(file_path).stat().st_size
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} PB"
        except:
            return "Unknown"

class StringUtils:
    """字符串处理工具类"""
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """截断字符串"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名中的非法字符"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化时间长度"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分钟"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小时"

class ValidationUtils:
    """验证工具类"""
    
    @staticmethod
    def is_valid_python_file(file_path: FilePath) -> bool:
        """检查是否为有效的Python文件"""
        try:
            path = Path(file_path)
            return path.exists() and path.suffix.lower() == '.py'
        except:
            return False
    
    @staticmethod
    def is_valid_icon_file(file_path: FilePath) -> bool:
        """检查是否为有效的图标文件"""
        try:
            path = Path(file_path)
            valid_extensions = {'.ico', '.png', '.jpg', '.jpeg', '.bmp'}
            return path.exists() and path.suffix.lower() in valid_extensions
        except:
            return False
    
    @staticmethod
    def validate_output_dir(dir_path: FilePath) -> Result[Path]:
        """验证输出目录"""
        try:
            path = Path(dir_path)
            
            # 检查父目录是否存在
            if not path.parent.exists():
                return Result.fail(f"父目录不存在: {path.parent}")
            
            # 检查是否有写权限
            if path.exists() and not os.access(path, os.W_OK):
                return Result.fail(f"没有写权限: {path}")
            
            return Result.ok(path)
        except Exception as e:
            return Result.fail(f"验证输出目录失败: {str(e)}")
```

## 🎯 实施建议

### 立即行动项
1. **添加类型注解**: 从核心模块开始，逐步完善类型注解
2. **统一错误处理**: 实现错误码系统和统一异常处理
3. **提取通用工具**: 识别重复代码，提取为通用工具函数

### 工具配置
```bash
# 安装代码质量工具
pip install mypy black pylint pytest-cov

# 配置 mypy (mypy.ini)
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

# 配置 pylint (.pylintrc)
[MESSAGES CONTROL]
disable = C0111,R0903,R0913

# 配置 black (pyproject.toml)
[tool.black]
line-length = 88
target-version = ['py38']
```

这些改进将显著提升代码质量，使项目更易维护和扩展。
