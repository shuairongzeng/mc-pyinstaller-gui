#!/usr/bin/env python3
"""
动态依赖追踪器
通过模拟执行和静态分析更准确地识别运行时实际需要的模块
"""

import os
import sys
import ast
import subprocess
import tempfile
import json
import time
import threading
from typing import Set, Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
import importlib.util
import traceback


@dataclass
class DynamicAnalysisResult:
    """动态分析结果"""
    runtime_modules: Set[str]  # 运行时实际使用的模块
    conditional_modules: Set[str]  # 条件导入的模块
    lazy_imports: Set[str]  # 延迟导入的模块
    optional_modules: Set[str]  # 可选模块
    error_modules: Set[str]  # 导入失败的模块
    
    execution_successful: bool = False
    execution_time: float = 0.0
    execution_output: str = ""
    execution_error: str = ""
    
    analysis_method: str = "static"  # static, execution, hybrid


class DynamicDependencyTracker:
    """动态依赖追踪器"""
    
    def __init__(self, python_interpreter: str = "", timeout: int = 30):
        self.python_interpreter = python_interpreter or sys.executable
        self.timeout = timeout
        self._analysis_cache = {}
        self._cache_lock = threading.Lock()
    
    def analyze_dynamic_dependencies(self, script_path: str,
                                   output_callback: Optional[Callable[[str], None]] = None,
                                   use_execution: bool = True) -> DynamicAnalysisResult:
        """分析动态依赖"""
        if output_callback:
            output_callback("开始动态依赖分析...")
        
        # 检查缓存
        cache_key = self._generate_cache_key(script_path, use_execution)
        with self._cache_lock:
            if cache_key in self._analysis_cache:
                if output_callback:
                    output_callback("从缓存加载动态分析结果")
                return self._analysis_cache[cache_key]
        
        start_time = time.time()
        
        # 静态分析
        static_result = self._static_analysis(script_path, output_callback)
        
        # 动态执行分析（如果启用）
        if use_execution:
            execution_result = self._execution_analysis(script_path, output_callback)
            # 合并结果
            result = self._merge_results(static_result, execution_result)
            result.analysis_method = "hybrid"
        else:
            result = static_result
            result.analysis_method = "static"
        
        result.execution_time = time.time() - start_time
        
        # 缓存结果
        with self._cache_lock:
            self._analysis_cache[cache_key] = result
        
        if output_callback:
            output_callback(f"动态分析完成，耗时 {result.execution_time:.2f}s")
        
        return result
    
    def _static_analysis(self, script_path: str,
                        output_callback: Optional[Callable[[str], None]] = None) -> DynamicAnalysisResult:
        """静态分析 - 分析代码结构识别动态导入模式"""
        if output_callback:
            output_callback("正在进行静态分析...")
        
        runtime_modules = set()
        conditional_modules = set()
        lazy_imports = set()
        optional_modules = set()
        error_modules = set()
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=script_path)
            
            # 分析AST节点
            for node in ast.walk(tree):
                # 检测try-except中的导入（可选模块）
                if isinstance(node, ast.Try):
                    for child in ast.walk(node):
                        if isinstance(child, (ast.Import, ast.ImportFrom)):
                            modules = self._extract_modules_from_import(child)
                            optional_modules.update(modules)
                
                # 检测if语句中的导入（条件模块）
                elif isinstance(node, ast.If):
                    for child in ast.walk(node):
                        if isinstance(child, (ast.Import, ast.ImportFrom)):
                            modules = self._extract_modules_from_import(child)
                            conditional_modules.update(modules)
                
                # 检测函数内的导入（延迟导入）
                elif isinstance(node, ast.FunctionDef):
                    for child in ast.walk(node):
                        if isinstance(child, (ast.Import, ast.ImportFrom)):
                            modules = self._extract_modules_from_import(child)
                            lazy_imports.update(modules)
                
                # 检测动态导入
                elif isinstance(node, ast.Call):
                    if (isinstance(node.func, ast.Name) and node.func.id == '__import__') or \
                       (isinstance(node.func, ast.Attribute) and 
                        isinstance(node.func.value, ast.Name) and 
                        node.func.value.id == 'importlib' and 
                        node.func.attr == 'import_module'):
                        
                        # 尝试提取模块名
                        if node.args and isinstance(node.args[0], ast.Str):
                            module_name = node.args[0].s.split('.')[0]
                            runtime_modules.add(module_name)
                        elif node.args and isinstance(node.args[0], ast.Constant):
                            module_name = str(node.args[0].value).split('.')[0]
                            runtime_modules.add(module_name)
                
                # 普通导入
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    # 检查是否在特殊上下文中
                    parent_types = [type(parent).__name__ for parent in ast.walk(tree) 
                                  if any(child is node for child in ast.walk(parent))]
                    
                    modules = self._extract_modules_from_import(node)
                    if not any(ptype in ['Try', 'If', 'FunctionDef'] for ptype in parent_types):
                        runtime_modules.update(modules)
            
            # 检测字符串中的模块引用
            string_modules = self._detect_string_module_references(content)
            runtime_modules.update(string_modules)

            # 检测高级动态导入模式
            advanced_modules = self._detect_advanced_dynamic_imports(content)
            runtime_modules.update(advanced_modules)
            
        except Exception as e:
            if output_callback:
                output_callback(f"静态分析出错: {e}")
        
        return DynamicAnalysisResult(
            runtime_modules=runtime_modules,
            conditional_modules=conditional_modules,
            lazy_imports=lazy_imports,
            optional_modules=optional_modules,
            error_modules=error_modules,
            execution_successful=True
        )
    
    def _execution_analysis(self, script_path: str,
                          output_callback: Optional[Callable[[str], None]] = None) -> DynamicAnalysisResult:
        """执行分析 - 通过实际执行脚本来检测运行时依赖"""
        if output_callback:
            output_callback("正在进行执行分析...")
        
        runtime_modules = set()
        error_modules = set()
        execution_successful = False
        execution_output = ""
        execution_error = ""
        
        try:
            # 创建监控脚本
            monitor_script = self._create_monitor_script(script_path)
            
            # 执行监控脚本
            result = subprocess.run(
                [self.python_interpreter, monitor_script],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.path.dirname(script_path)
            )
            
            execution_output = result.stdout
            execution_error = result.stderr
            execution_successful = result.returncode == 0
            
            # 解析监控结果
            if execution_successful and execution_output:
                try:
                    lines = execution_output.strip().split('\n')
                    for line in lines:
                        if line.startswith('IMPORTED_MODULE:'):
                            module_name = line.replace('IMPORTED_MODULE:', '').strip()
                            if module_name:
                                runtime_modules.add(module_name.split('.')[0])
                        elif line.startswith('IMPORT_ERROR:'):
                            module_name = line.replace('IMPORT_ERROR:', '').strip()
                            if module_name:
                                error_modules.add(module_name.split('.')[0])
                except Exception as e:
                    if output_callback:
                        output_callback(f"解析执行结果失败: {e}")
            
            # 清理监控脚本
            try:
                os.unlink(monitor_script)
            except:
                pass
                
        except subprocess.TimeoutExpired:
            if output_callback:
                output_callback(f"脚本执行超时 ({self.timeout}s)")
            execution_error = f"执行超时 ({self.timeout}s)"
        except Exception as e:
            if output_callback:
                output_callback(f"执行分析失败: {e}")
            execution_error = str(e)
        
        return DynamicAnalysisResult(
            runtime_modules=runtime_modules,
            conditional_modules=set(),
            lazy_imports=set(),
            optional_modules=set(),
            error_modules=error_modules,
            execution_successful=execution_successful,
            execution_output=execution_output,
            execution_error=execution_error
        )
    
    def _create_monitor_script(self, original_script: str) -> str:
        """创建监控脚本"""
        monitor_code = f'''
import sys
import importlib.util
import traceback

# 保存原始的import函数
if isinstance(__builtins__, dict):
    original_import = __builtins__['__import__']
else:
    original_import = __builtins__.__import__

def monitor_import(name, globals=None, locals=None, fromlist=(), level=0):
    """监控导入的模块"""
    try:
        result = original_import(name, globals, locals, fromlist, level)
        print(f"IMPORTED_MODULE:{{name}}")
        return result
    except ImportError as e:
        print(f"IMPORT_ERROR:{{name}}")
        raise

# 替换import函数
if isinstance(__builtins__, dict):
    __builtins__['__import__'] = monitor_import
else:
    __builtins__.__import__ = monitor_import

# 执行原始脚本
try:
    with open(r"{original_script}", "r", encoding="utf-8") as f:
        code = f.read()
    
    # 编译并执行
    compiled = compile(code, r"{original_script}", "exec")
    exec(compiled)
    
except Exception as e:
    print(f"EXECUTION_ERROR:{{str(e)}}")
    traceback.print_exc()
'''
        
        # 创建临时监控脚本
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(monitor_code)
            return f.name

    def _extract_modules_from_import(self, node: ast.AST) -> Set[str]:
        """从导入节点提取模块名"""
        modules = set()

        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split('.')[0])

        return modules

    def _detect_string_module_references(self, content: str) -> Set[str]:
        """检测字符串中的模块引用"""
        modules = set()

        import re

        # 增强的字符串模块引用模式检测
        patterns = [
            # importlib 相关
            r'importlib\.import_module\([\'"]([^\'\"]+)[\'"]\)',
            r'importlib\.util\.spec_from_file_location\([\'"]([^\'\"]+)[\'"]\)',
            r'importlib\.util\.module_from_spec\([\'"]([^\'\"]+)[\'"]\)',

            # __import__ 调用
            r'__import__\([\'"]([^\'\"]+)[\'"]\)',

            # exec/eval 中的导入
            r'exec\([\'"].*?import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
            r'eval\([\'"].*?import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',

            # 字符串格式化的导入
            r'f[\'"].*?import\s+\{([^}]+)\}',
            r'[\'"].*?import\s+\{([^}]+)\}[\'"]\.format\(',

            # pkg_resources 相关
            r'pkg_resources\.require\([\'"]([^\'\"]+)[\'"]\)',
            r'pkg_resources\.get_distribution\([\'"]([^\'\"]+)[\'"]\)',
            r'pkg_resources\.load_entry_point\([\'"]([^\'\"]+)[\'"]\)',

            # setuptools 相关
            r'setuptools\.find_packages\([\'"]([^\'\"]+)[\'"]\)',

            # 插件系统常见模式
            r'load_plugin\([\'"]([^\'\"]+)[\'"]\)',
            r'get_plugin\([\'"]([^\'\"]+)[\'"]\)',

            # 配置文件中的模块引用
            r'[\'"]module[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
            r'[\'"]plugin[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
            r'[\'"]handler[\'"]:\s*[\'"]([^\'\"]+)[\'"]',

            # 动态属性访问
            r'getattr\([^,]+,\s*[\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]',
            r'hasattr\([^,]+,\s*[\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]',

            # 简单字符串（更严格的过滤）
            r'[\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]',
        ]

        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match else ""

                    # 过滤掉明显不是模块名的字符串
                    if self._is_likely_module_name(match):
                        # 提取顶级模块名
                        top_module = match.split('.')[0]
                        if top_module:
                            modules.add(top_module)
            except re.error:
                # 忽略正则表达式错误
                continue

        return modules

    def _is_likely_module_name(self, name: str) -> bool:
        """判断字符串是否可能是模块名"""
        if not name or len(name) < 2:
            return False

        # 基本的模块名规则
        if not name[0].isalpha() and name[0] != '_':
            return False

        if not all(c.isalnum() or c in '_.' for c in name):
            return False

        # 排除过短或过长的名称
        if len(name) < 2 or len(name) > 100:
            return False

        # 排除常见的非模块字符串
        excluded = {
            # 常见的配置项
            'main', 'name', 'file', 'path', 'version', 'author', 'email',
            'description', 'license', 'url', 'download_url', 'classifiers',
            'keywords', 'platforms', 'requires', 'provides', 'obsoletes',
            'home_page', 'download_url', 'author_email', 'maintainer',
            'maintainer_email', 'long_description', 'zip_safe',

            # 常见的变量名和属性名
            'self', 'cls', 'args', 'kwargs', 'result', 'data', 'value',
            'key', 'item', 'index', 'count', 'size', 'length', 'width',
            'height', 'x', 'y', 'z', 'i', 'j', 'k', 'n', 'm',

            # 常见的方法名
            'get', 'set', 'add', 'remove', 'delete', 'update', 'create',
            'read', 'write', 'open', 'close', 'start', 'stop', 'run',
            'init', 'setup', 'cleanup', 'reset', 'clear', 'load', 'save',

            # 常见的字符串值
            'true', 'false', 'none', 'null', 'undefined', 'empty',
            'default', 'auto', 'manual', 'debug', 'info', 'warning',
            'error', 'critical', 'success', 'failure', 'ok', 'cancel',

            # 文件扩展名和格式
            'txt', 'csv', 'json', 'xml', 'html', 'css', 'js', 'py',
            'exe', 'dll', 'so', 'dylib', 'zip', 'tar', 'gz', 'bz2',

            # 常见的单词
            'test', 'demo', 'example', 'sample', 'temp', 'tmp', 'cache',
            'config', 'settings', 'options', 'params', 'arguments',
        }

        if name.lower() in excluded:
            return False

        # 排除看起来像文件路径的字符串
        if '/' in name or '\\' in name or name.endswith(('.py', '.txt', '.json', '.xml')):
            return False

        # 排除看起来像URL的字符串
        if name.startswith(('http://', 'https://', 'ftp://', 'file://')):
            return False

        # 排除纯数字字符串
        if name.isdigit():
            return False

        # 检查是否是已知的Python模块
        known_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'random', 'math',
            'collections', 'itertools', 'functools', 'operator', 'copy',
            'pickle', 'sqlite3', 'urllib', 'http', 'email', 'html',
            'xml', 'csv', 'configparser', 'logging', 'unittest',
            'threading', 'multiprocessing', 'subprocess', 'socket',
            'ssl', 'hashlib', 'hmac', 'base64', 'binascii', 'struct',
            'array', 'queue', 'heapq', 'bisect', 'weakref', 'types',
            'inspect', 'importlib', 'pkgutil', 'modulefinder', 'runpy',
            'ast', 'dis', 'py_compile', 'compileall', 'keyword',
            'token', 'tokenize', 'tabnanny', 'pyclbr', 'trace',
            'traceback', 'pdb', 'profile', 'pstats', 'timeit',
            'doctest', 'unittest', 'test', 'bdb', 'faulthandler',
            'warnings', 'contextlib', 'abc', 'atexit', 'tracemalloc',
            'gc', 'site', 'sysconfig', 'builtins', 'main',
            # 常见第三方模块
            'numpy', 'pandas', 'matplotlib', 'scipy', 'sklearn',
            'tensorflow', 'torch', 'keras', 'flask', 'django',
            'requests', 'urllib3', 'beautifulsoup4', 'lxml', 'pillow',
            'opencv', 'pyqt5', 'pyqt6', 'tkinter', 'wx', 'kivy',
            'pytest', 'nose', 'mock', 'coverage', 'tox', 'sphinx',
            'setuptools', 'pip', 'wheel', 'twine', 'virtualenv',
            'conda', 'poetry', 'pipenv', 'black', 'flake8', 'pylint',
            'mypy', 'isort', 'autopep8', 'yapf', 'bandit', 'safety'
        }

        # 如果是已知模块，直接返回True
        if name.lower() in known_modules:
            return True

        # 检查是否符合Python模块命名规范
        # 模块名通常是小写，可能包含下划线
        if name.islower() and '_' in name:
            return True

        # 检查是否是常见的模块命名模式
        common_patterns = [
            r'^[a-z][a-z0-9_]*$',  # 小写字母开头，包含数字和下划线
            r'^[A-Z][a-zA-Z0-9]*$',  # 大写字母开头的类名风格
            r'^[a-z]+[A-Z][a-zA-Z0-9]*$',  # 驼峰命名
        ]

        import re
        for pattern in common_patterns:
            if re.match(pattern, name):
                return True

        return False

    def _detect_advanced_dynamic_imports(self, content: str) -> Set[str]:
        """检测高级动态导入模式"""
        modules = set()

        import re

        # 检测 importlib 的各种用法
        importlib_patterns = [
            # importlib.import_module 的各种形式
            r'importlib\.import_module\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            r'importlib\.import_module\s*\(\s*f[\'"]([^\'\"]+)[\'"]',
            r'importlib\.import_module\s*\(\s*[\'"]([^\'\"]+)[\'"]\.format\(',
            r'importlib\.import_module\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)',

            # importlib.util 相关
            r'importlib\.util\.spec_from_file_location\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            r'importlib\.util\.module_from_spec\s*\(\s*[\'"]([^\'\"]+)[\'"]',

            # importlib.machinery 相关
            r'importlib\.machinery\.SourceFileLoader\s*\(\s*[\'"]([^\'\"]+)[\'"]',
        ]

        # 检测 __import__ 的各种用法
        import_patterns = [
            r'__import__\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            r'__import__\s*\(\s*f[\'"]([^\'\"]+)[\'"]',
            r'__import__\s*\(\s*[\'"]([^\'\"]+)[\'"]\.format\(',
            r'__import__\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)',
        ]

        # 检测 exec/eval 中的导入语句
        exec_patterns = [
            r'exec\s*\(\s*[\'"].*?import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
            r'eval\s*\(\s*[\'"].*?import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
            r'exec\s*\(\s*f[\'"].*?import\s+\{([^}]+)\}',
            r'eval\s*\(\s*f[\'"].*?import\s+\{([^}]+)\}',
        ]

        # 检测动态属性访问可能的模块
        attr_patterns = [
            r'getattr\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*[\'"]([^\'\"]+)[\'"]',
            r'hasattr\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*[\'"]([^\'\"]+)[\'"]',
            r'setattr\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*[\'"]([^\'\"]+)[\'"]',
        ]

        # 检测插件系统和工厂模式
        plugin_patterns = [
            r'load_plugin\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            r'get_plugin\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            r'create_plugin\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            r'register_plugin\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            r'factory\.create\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            r'Factory\.get\s*\(\s*[\'"]([^\'\"]+)[\'"]',
        ]

        # 检测配置驱动的导入
        config_patterns = [
            r'[\'"]module[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
            r'[\'"]plugin[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
            r'[\'"]handler[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
            r'[\'"]driver[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
            r'[\'"]backend[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
            r'[\'"]engine[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
        ]

        all_patterns = (importlib_patterns + import_patterns + exec_patterns +
                       attr_patterns + plugin_patterns + config_patterns)

        for pattern in all_patterns:
            try:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        # 对于有多个捕获组的模式，取第一个非空的
                        match = next((m for m in match if m), "")

                    if match and self._is_likely_module_name(match):
                        # 提取顶级模块名
                        top_module = match.split('.')[0]
                        if top_module:
                            modules.add(top_module)
            except re.error:
                continue

        return modules

    def _merge_results(self, static_result: DynamicAnalysisResult,
                      execution_result: DynamicAnalysisResult) -> DynamicAnalysisResult:
        """合并静态分析和执行分析的结果"""
        return DynamicAnalysisResult(
            runtime_modules=static_result.runtime_modules | execution_result.runtime_modules,
            conditional_modules=static_result.conditional_modules,
            lazy_imports=static_result.lazy_imports,
            optional_modules=static_result.optional_modules,
            error_modules=static_result.error_modules | execution_result.error_modules,
            execution_successful=execution_result.execution_successful,
            execution_output=execution_result.execution_output,
            execution_error=execution_result.execution_error
        )

    def _generate_cache_key(self, script_path: str, use_execution: bool) -> str:
        """生成缓存键"""
        import hashlib

        try:
            with open(script_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[:8]
        except:
            file_hash = "unknown"

        execution_flag = "exec" if use_execution else "static"
        return f"{os.path.basename(script_path)}_{file_hash}_{execution_flag}"

    def get_comprehensive_analysis(self, script_path: str,
                                 output_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """获取综合分析结果"""
        if output_callback:
            output_callback("开始综合动态依赖分析...")

        # 执行动态分析
        dynamic_result = self.analyze_dynamic_dependencies(script_path, output_callback, use_execution=True)

        # 分析结果统计
        all_modules = (dynamic_result.runtime_modules |
                      dynamic_result.conditional_modules |
                      dynamic_result.lazy_imports |
                      dynamic_result.optional_modules)

        # 生成建议
        recommendations = []

        if dynamic_result.conditional_modules:
            recommendations.append(f"发现 {len(dynamic_result.conditional_modules)} 个条件导入模块，建议测试不同执行路径")

        if dynamic_result.lazy_imports:
            recommendations.append(f"发现 {len(dynamic_result.lazy_imports)} 个延迟导入模块，这些模块可能在特定功能触发时才需要")

        if dynamic_result.optional_modules:
            recommendations.append(f"发现 {len(dynamic_result.optional_modules)} 个可选模块，这些模块缺失时程序仍可运行")

        if dynamic_result.error_modules:
            recommendations.append(f"发现 {len(dynamic_result.error_modules)} 个导入失败的模块，需要检查安装情况")

        if not dynamic_result.execution_successful:
            recommendations.append("脚本执行失败，建议检查脚本是否有语法错误或缺少依赖")

        return {
            'dynamic_result': dynamic_result,
            'total_modules': len(all_modules),
            'runtime_modules': len(dynamic_result.runtime_modules),
            'conditional_modules': len(dynamic_result.conditional_modules),
            'lazy_imports': len(dynamic_result.lazy_imports),
            'optional_modules': len(dynamic_result.optional_modules),
            'error_modules': len(dynamic_result.error_modules),
            'execution_successful': dynamic_result.execution_successful,
            'recommendations': recommendations,
            'analysis_method': dynamic_result.analysis_method
        }

    def clear_cache(self) -> None:
        """清理缓存"""
        with self._cache_lock:
            self._analysis_cache.clear()
