#!/usr/bin/env python3
"""
精准依赖分析器
提供更准确的依赖检测和分析功能
"""

import os
import sys
import ast
import json
import time
import subprocess
import importlib.util
import importlib.metadata
from typing import Set, Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import concurrent.futures
from collections import defaultdict

try:
    import pkg_resources
    HAS_PKG_RESOURCES = True
except ImportError:
    HAS_PKG_RESOURCES = False

try:
    from packaging import version
    HAS_PACKAGING = True
except ImportError:
    HAS_PACKAGING = False


@dataclass
class ModuleInfo:
    """模块信息"""
    name: str
    version: str = "unknown"
    location: str = ""
    is_standard_lib: bool = False
    is_third_party: bool = False
    is_local: bool = False
    is_available: bool = False
    size: int = 0
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class PreciseAnalysisResult:
    """精准分析结果"""
    # 检测到的模块（按类型分类）
    standard_modules: Set[str]
    third_party_modules: Set[str] 
    local_modules: Set[str]
    
    # 可用性分析
    available_modules: Set[str]
    missing_modules: Set[str]
    
    # 详细信息
    module_details: Dict[str, ModuleInfo]
    
    # PyInstaller相关
    hidden_imports: List[str]
    collect_all: List[str]
    data_files: List[str]
    
    # 分析统计
    analysis_time: float = 0.0
    cache_hit: bool = False
    environment_info: Dict[str, Any] = None
    
    # 建议和警告
    recommendations: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.warnings is None:
            self.warnings = []
        if self.environment_info is None:
            self.environment_info = {}


class EnvironmentAnalyzer:
    """环境分析器 - 分析Python环境和已安装的包"""
    
    def __init__(self, python_interpreter: str = ""):
        self.python_interpreter = python_interpreter or sys.executable
        self._cache = {}
        self._cache_lock = threading.Lock()
    
    def get_environment_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        with self._cache_lock:
            if 'env_info' in self._cache:
                return self._cache['env_info']
        
        env_info = {
            'python_version': sys.version,
            'python_executable': self.python_interpreter,
            'platform': sys.platform,
            'is_virtual_env': self._is_virtual_environment(),
            'virtual_env_path': self._get_virtual_env_path(),
            'site_packages': self._get_site_packages_paths(),
            'installed_packages': self._get_installed_packages()
        }
        
        with self._cache_lock:
            self._cache['env_info'] = env_info
        
        return env_info
    
    def _is_virtual_environment(self) -> bool:
        """检查是否在虚拟环境中"""
        return (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            'VIRTUAL_ENV' in os.environ or
            'CONDA_DEFAULT_ENV' in os.environ
        )
    
    def _get_virtual_env_path(self) -> Optional[str]:
        """获取虚拟环境路径"""
        if 'VIRTUAL_ENV' in os.environ:
            return os.environ['VIRTUAL_ENV']
        elif 'CONDA_PREFIX' in os.environ:
            return os.environ['CONDA_PREFIX']
        elif hasattr(sys, 'prefix'):
            return sys.prefix
        return None
    
    def _get_site_packages_paths(self) -> List[str]:
        """获取site-packages路径"""
        import site
        return site.getsitepackages() + [site.getusersitepackages()]
    
    def _get_installed_packages(self) -> Dict[str, str]:
        """获取已安装的包及其版本"""
        packages = {}
        
        # 使用importlib.metadata (Python 3.8+)
        try:
            import importlib.metadata as metadata
            for dist in metadata.distributions():
                packages[dist.metadata['name']] = dist.version
        except ImportError:
            # 回退到pkg_resources
            if HAS_PKG_RESOURCES:
                for dist in pkg_resources.working_set:
                    packages[dist.project_name] = dist.version
        
        return packages
    
    def is_package_available(self, package_name: str) -> Tuple[bool, str]:
        """检查包是否可用"""
        env_info = self.get_environment_info()
        installed_packages = env_info['installed_packages']
        
        # 直接匹配
        if package_name in installed_packages:
            return True, installed_packages[package_name]
        
        # 尝试导入检查
        try:
            spec = importlib.util.find_spec(package_name)
            if spec is not None:
                # 尝试获取版本
                try:
                    import importlib.metadata as metadata
                    version = metadata.version(package_name)
                    return True, version
                except:
                    return True, "unknown"
        except (ImportError, ModuleNotFoundError, ValueError):
            pass
        
        return False, ""


class ModuleClassifier:
    """模块分类器 - 区分标准库、第三方库和本地模块"""
    
    def __init__(self, environment_analyzer: EnvironmentAnalyzer):
        self.env_analyzer = environment_analyzer
        self._stdlib_modules = self._get_stdlib_modules()
        self._cache = {}
        self._cache_lock = threading.Lock()
    
    def _get_stdlib_modules(self) -> Set[str]:
        """获取标准库模块列表"""
        import sys
        stdlib_modules = set(sys.builtin_module_names)
        
        # 添加常见的标准库模块
        common_stdlib = {
            'os', 'sys', 'json', 'time', 'datetime', 'math', 'random',
            'collections', 'itertools', 'functools', 'operator',
            'pathlib', 'shutil', 'subprocess', 'threading', 'multiprocessing',
            'urllib', 'http', 'email', 'html', 'xml', 'csv', 'configparser',
            'logging', 'unittest', 'argparse', 'pickle', 'sqlite3',
            'hashlib', 'hmac', 'secrets', 'uuid', 'base64', 'binascii',
            'struct', 'array', 'weakref', 'copy', 'pprint', 'reprlib',
            'enum', 'types', 'inspect', 'dis', 'ast', 'keyword',
            'token', 'tokenize', 'parser', 'symbol', 'compiler',
            'importlib', 'pkgutil', 'modulefinder', 'runpy',
            'warnings', 'contextlib', 'abc', 'atexit', 'traceback',
            'gc', 'site', 'sysconfig'
        }
        
        stdlib_modules.update(common_stdlib)
        return stdlib_modules
    
    def classify_module(self, module_name: str, script_path: str = "") -> Tuple[str, ModuleInfo]:
        """
        分类模块
        返回: (分类, 模块信息)
        分类: 'standard', 'third_party', 'local'
        """
        with self._cache_lock:
            cache_key = f"{module_name}_{script_path}"
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        # 创建模块信息
        module_info = ModuleInfo(name=module_name)
        
        # 检查是否为标准库
        base_module = module_name.split('.')[0]
        if base_module in self._stdlib_modules:
            module_info.is_standard_lib = True
            module_info.is_available = True
            classification = 'standard'
        else:
            # 检查是否为第三方库
            is_available, version = self.env_analyzer.is_package_available(base_module)
            if is_available:
                module_info.is_third_party = True
                module_info.is_available = True
                module_info.version = version
                classification = 'third_party'
            else:
                # 检查是否为本地模块
                if script_path and self._is_local_module(module_name, script_path):
                    module_info.is_local = True
                    module_info.is_available = True
                    classification = 'local'
                else:
                    # 未知模块，可能缺失
                    module_info.is_available = False
                    classification = 'third_party'  # 假设为第三方库
        
        # 获取模块位置和大小
        try:
            spec = importlib.util.find_spec(module_name)
            if spec and spec.origin:
                module_info.location = spec.origin
                if os.path.exists(spec.origin):
                    module_info.size = os.path.getsize(spec.origin)
        except:
            pass
        
        result = (classification, module_info)
        
        with self._cache_lock:
            self._cache[cache_key] = result
        
        return result
    
    def _is_local_module(self, module_name: str, script_path: str) -> bool:
        """检查是否为本地模块"""
        if not script_path:
            return False
        
        script_dir = os.path.dirname(os.path.abspath(script_path))
        
        # 检查是否存在对应的.py文件
        module_file = os.path.join(script_dir, f"{module_name}.py")
        if os.path.exists(module_file):
            return True
        
        # 检查是否存在对应的包目录
        package_dir = os.path.join(script_dir, module_name)
        if os.path.isdir(package_dir) and os.path.exists(os.path.join(package_dir, "__init__.py")):
            return True
        
        return False


class PreciseDependencyAnalyzer:
    """精准依赖分析器"""

    def __init__(self, python_interpreter: str = "", cache_dir: str = ".precise_cache"):
        self.python_interpreter = python_interpreter or sys.executable
        self.cache_dir = cache_dir
        self.env_analyzer = EnvironmentAnalyzer(python_interpreter)
        self.module_classifier = ModuleClassifier(self.env_analyzer)

        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)

        # 统计信息
        self.stats = {
            'total_analyses': 0,
            'cache_hits': 0,
            'avg_analysis_time': 0.0
        }
        self._stats_lock = threading.Lock()

    def analyze_dependencies(self, script_path: str,
                           output_callback: Optional[Callable[[str], None]] = None,
                           force_refresh: bool = False) -> PreciseAnalysisResult:
        """分析脚本依赖"""
        start_time = time.time()

        if output_callback:
            output_callback("开始精准依赖分析...")

        # 检查缓存
        cache_key = self._generate_cache_key(script_path)
        if not force_refresh:
            cached_result = self._load_from_cache(cache_key)
            if cached_result:
                cached_result.cache_hit = True
                if output_callback:
                    output_callback("从缓存加载分析结果")
                return cached_result

        # 执行分析
        result = self._perform_analysis(script_path, output_callback)
        result.analysis_time = time.time() - start_time
        result.cache_hit = False

        # 保存到缓存
        self._save_to_cache(cache_key, result)

        # 更新统计
        with self._stats_lock:
            self.stats['total_analyses'] += 1
            if result.cache_hit:
                self.stats['cache_hits'] += 1

            # 更新平均分析时间
            total_time = self.stats['avg_analysis_time'] * (self.stats['total_analyses'] - 1)
            self.stats['avg_analysis_time'] = (total_time + result.analysis_time) / self.stats['total_analyses']

        if output_callback:
            output_callback(f"分析完成，耗时 {result.analysis_time:.2f}s")

        return result

    def _perform_analysis(self, script_path: str,
                         output_callback: Optional[Callable[[str], None]] = None) -> PreciseAnalysisResult:
        """执行实际的分析"""
        if output_callback:
            output_callback("正在分析脚本依赖...")

        # 1. 获取环境信息
        env_info = self.env_analyzer.get_environment_info()

        # 2. 检测所有导入的模块
        detected_modules = self._detect_imports(script_path, output_callback)

        # 3. 分类模块
        standard_modules = set()
        third_party_modules = set()
        local_modules = set()
        available_modules = set()
        missing_modules = set()
        module_details = {}

        if output_callback:
            output_callback(f"正在分类 {len(detected_modules)} 个模块...")

        for module_name in detected_modules:
            classification, module_info = self.module_classifier.classify_module(module_name, script_path)
            module_details[module_name] = module_info

            if classification == 'standard':
                standard_modules.add(module_name)
            elif classification == 'third_party':
                third_party_modules.add(module_name)
            elif classification == 'local':
                local_modules.add(module_name)

            if module_info.is_available:
                available_modules.add(module_name)
            else:
                missing_modules.add(module_name)

        # 4. 生成PyInstaller相关建议
        hidden_imports, collect_all, data_files = self._generate_pyinstaller_suggestions(
            third_party_modules, module_details, script_path, output_callback
        )

        # 5. 生成建议和警告
        recommendations, warnings = self._generate_recommendations(
            standard_modules, third_party_modules, local_modules,
            missing_modules, module_details, env_info
        )

        return PreciseAnalysisResult(
            standard_modules=standard_modules,
            third_party_modules=third_party_modules,
            local_modules=local_modules,
            available_modules=available_modules,
            missing_modules=missing_modules,
            module_details=module_details,
            hidden_imports=hidden_imports,
            collect_all=collect_all,
            data_files=data_files,
            environment_info=env_info,
            recommendations=recommendations,
            warnings=warnings
        )

    def _detect_imports(self, script_path: str,
                       output_callback: Optional[Callable[[str], None]] = None) -> Set[str]:
        """检测脚本中的导入"""
        modules = set()

        if output_callback:
            output_callback("正在解析导入语句...")

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用AST解析
            tree = ast.parse(content, filename=script_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        modules.add(module_name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        modules.add(module_name)

            # 检测动态导入
            dynamic_modules = self._detect_dynamic_imports(content)
            modules.update(dynamic_modules)

        except Exception as e:
            if output_callback:
                output_callback(f"解析导入时出错: {e}")

        return modules

    def _detect_dynamic_imports(self, content: str) -> Set[str]:
        """检测动态导入"""
        modules = set()

        # 检测 __import__ 调用
        import re

        # __import__('module_name')
        import_pattern = r'__import__\s*\(\s*[\'"]([^\'\"]+)[\'"]\s*\)'
        matches = re.findall(import_pattern, content)
        for match in matches:
            modules.add(match.split('.')[0])

        # importlib.import_module('module_name')
        importlib_pattern = r'importlib\.import_module\s*\(\s*[\'"]([^\'\"]+)[\'"]\s*\)'
        matches = re.findall(importlib_pattern, content)
        for match in matches:
            modules.add(match.split('.')[0])

        return modules

    def _generate_pyinstaller_suggestions(self, third_party_modules: Set[str],
                                        module_details: Dict[str, ModuleInfo],
                                        script_path: str,
                                        output_callback: Optional[Callable[[str], None]] = None) -> Tuple[List[str], List[str], List[str]]:
        """生成PyInstaller相关建议"""
        hidden_imports = []
        collect_all = []
        data_files = []

        if output_callback:
            output_callback("正在生成PyInstaller建议...")

        # 基于已知的框架模式生成建议
        framework_patterns = {
            'PyQt5': {
                'hidden_imports': ['PyQt5.sip'],
                'collect_all': ['PyQt5']
            },
            'PyQt6': {
                'hidden_imports': ['PyQt6.sip'],
                'collect_all': ['PyQt6']
            },
            'tkinter': {
                'hidden_imports': ['tkinter.ttk', 'tkinter.messagebox']
            },
            'matplotlib': {
                'hidden_imports': ['matplotlib.backends.backend_tkagg'],
                'collect_all': ['matplotlib']
            },
            'numpy': {
                'collect_all': ['numpy']
            },
            'pandas': {
                'collect_all': ['pandas']
            },
            'requests': {
                'hidden_imports': ['urllib3', 'certifi']
            }
        }

        for module in third_party_modules:
            if module in framework_patterns:
                pattern = framework_patterns[module]
                hidden_imports.extend(pattern.get('hidden_imports', []))
                collect_all.extend(pattern.get('collect_all', []))

        # 检查数据文件
        script_dir = os.path.dirname(script_path)
        common_data_files = ['config.json', 'config.yaml', 'config.ini', 'settings.json', '*.txt', '*.csv']

        for pattern in common_data_files:
            if '*' in pattern:
                import glob
                files = glob.glob(os.path.join(script_dir, pattern))
                for file in files:
                    if os.path.isfile(file):
                        data_files.append(f"--add-data={file};.")
            else:
                file_path = os.path.join(script_dir, pattern)
                if os.path.exists(file_path):
                    data_files.append(f"--add-data={file_path};.")

        return list(set(hidden_imports)), list(set(collect_all)), list(set(data_files))

    def _generate_recommendations(self, standard_modules: Set[str],
                                third_party_modules: Set[str],
                                local_modules: Set[str],
                                missing_modules: Set[str],
                                module_details: Dict[str, ModuleInfo],
                                env_info: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """生成建议和警告"""
        recommendations = []
        warnings = []

        # 缺失模块建议
        if missing_modules:
            missing_list = sorted(missing_modules)
            recommendations.append(f"发现 {len(missing_modules)} 个缺失模块，建议安装: {', '.join(missing_list[:5])}")
            if len(missing_list) > 5:
                recommendations.append(f"还有 {len(missing_list) - 5} 个其他缺失模块")

        # 环境建议
        if env_info.get('is_virtual_env'):
            recommendations.append("检测到虚拟环境，建议在打包时使用相同的Python解释器")
        else:
            warnings.append("未检测到虚拟环境，可能会包含不必要的系统包")

        # 大型库建议
        large_modules = []
        for module_name, info in module_details.items():
            if info.is_third_party and info.size > 10 * 1024 * 1024:  # 大于10MB
                large_modules.append(module_name)

        if large_modules:
            recommendations.append(f"检测到大型库 {', '.join(large_modules)}，建议考虑使用 --exclude-module 排除不必要的子模块")

        # 框架特定建议
        if 'numpy' in third_party_modules or 'pandas' in third_party_modules:
            recommendations.append("检测到科学计算库，建议增加 --hidden-import=numpy.core._methods")

        if 'PyQt5' in third_party_modules:
            recommendations.append("检测到PyQt5，建议使用 --windowed 参数隐藏控制台窗口")

        return recommendations, warnings

    def _generate_cache_key(self, script_path: str) -> str:
        """生成缓存键"""
        import hashlib

        # 计算文件哈希
        try:
            with open(script_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
        except:
            file_hash = "unknown"

        # 包含环境信息
        env_hash = hashlib.md5(str(self.env_analyzer.get_environment_info()).encode()).hexdigest()[:8]

        return f"{os.path.basename(script_path)}_{file_hash[:8]}_{env_hash}"

    def _load_from_cache(self, cache_key: str) -> Optional[PreciseAnalysisResult]:
        """从缓存加载结果"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 转换为结果对象
            result = PreciseAnalysisResult(
                standard_modules=set(data['standard_modules']),
                third_party_modules=set(data['third_party_modules']),
                local_modules=set(data['local_modules']),
                available_modules=set(data['available_modules']),
                missing_modules=set(data['missing_modules']),
                module_details={k: ModuleInfo(**v) for k, v in data['module_details'].items()},
                hidden_imports=data['hidden_imports'],
                collect_all=data['collect_all'],
                data_files=data['data_files'],
                environment_info=data['environment_info'],
                recommendations=data['recommendations'],
                warnings=data['warnings']
            )

            return result

        except Exception:
            return None

    def _save_to_cache(self, cache_key: str, result: PreciseAnalysisResult) -> None:
        """保存结果到缓存"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        try:
            # 转换为可序列化的格式
            data = {
                'standard_modules': list(result.standard_modules),
                'third_party_modules': list(result.third_party_modules),
                'local_modules': list(result.local_modules),
                'available_modules': list(result.available_modules),
                'missing_modules': list(result.missing_modules),
                'module_details': {k: asdict(v) for k, v in result.module_details.items()},
                'hidden_imports': result.hidden_imports,
                'collect_all': result.collect_all,
                'data_files': result.data_files,
                'environment_info': result.environment_info,
                'recommendations': result.recommendations,
                'warnings': result.warnings
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception:
            pass  # 缓存失败不影响主要功能

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._stats_lock:
            return self.stats.copy()

    def clear_cache(self) -> None:
        """清理缓存"""
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception:
            pass
