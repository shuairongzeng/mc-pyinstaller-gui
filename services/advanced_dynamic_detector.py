"""
高级动态模块检测器
提供更准确的动态导入检测功能
"""

import ast
import os
import re
import sys
import time
import tempfile
import subprocess
import threading
from typing import Set, Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class AdvancedDetectionResult:
    """高级检测结果"""
    # 基础模块分类
    static_imports: Set[str]           # 静态导入
    dynamic_imports: Set[str]          # 动态导入
    conditional_imports: Set[str]      # 条件导入
    lazy_imports: Set[str]             # 延迟导入
    optional_imports: Set[str]         # 可选导入
    
    # 高级检测结果
    string_references: Set[str]        # 字符串引用
    plugin_modules: Set[str]           # 插件模块
    config_driven: Set[str]            # 配置驱动
    runtime_discovered: Set[str]       # 运行时发现
    
    # 元数据
    detection_methods: Dict[str, Any]  # 检测方法详情
    confidence_scores: Dict[str, float] # 置信度分数
    execution_time: float              # 执行时间
    cache_hit: bool = False            # 缓存命中


class AdvancedDynamicDetector:
    """高级动态模块检测器"""
    
    def __init__(self, python_interpreter: str = "", timeout: int = 30):
        self.python_interpreter = python_interpreter or sys.executable
        self.timeout = timeout
        self._analysis_cache = {}
        self._cache_lock = threading.Lock()
        
        # 已知模块数据库
        self.known_modules = self._build_known_modules_db()
        
        # 检测策略权重
        self.strategy_weights = {
            'static_ast': 0.9,
            'string_analysis': 0.7,
            'runtime_execution': 0.95,
            'pattern_matching': 0.6,
            'heuristic': 0.5
        }
    
    def detect_modules(self, script_path: str, 
                      output_callback: Optional[Callable[[str], None]] = None,
                      use_execution: bool = True) -> AdvancedDetectionResult:
        """执行高级模块检测"""
        start_time = time.time()
        
        if output_callback:
            output_callback("开始高级动态模块检测...")
        
        # 检查缓存
        cache_key = self._generate_cache_key(script_path, use_execution)
        with self._cache_lock:
            if cache_key in self._analysis_cache:
                cached_result = self._analysis_cache[cache_key]
                cached_result.cache_hit = True
                if output_callback:
                    output_callback("从缓存加载检测结果")
                return cached_result
        
        # 读取脚本内容
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            if output_callback:
                output_callback(f"读取脚本失败: {e}")
            return self._create_empty_result()
        
        # 并行执行多种检测策略
        detection_methods = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                'static_ast': executor.submit(self._static_ast_analysis, content, script_path),
                'string_analysis': executor.submit(self._string_pattern_analysis, content),
                'pattern_matching': executor.submit(self._advanced_pattern_matching, content),
                'heuristic': executor.submit(self._heuristic_analysis, content, script_path)
            }
            
            # 如果启用执行分析
            if use_execution:
                futures['runtime_execution'] = executor.submit(
                    self._runtime_execution_analysis, script_path, output_callback
                )
            
            # 收集结果
            for method_name, future in futures.items():
                try:
                    result = future.result(timeout=self.timeout)
                    detection_methods[method_name] = result
                    if output_callback:
                        output_callback(f"{method_name} 检测完成")
                except Exception as e:
                    detection_methods[method_name] = {'error': str(e)}
                    if output_callback:
                        output_callback(f"{method_name} 检测失败: {e}")
        
        # 合并和评分结果
        final_result = self._merge_and_score_results(detection_methods)
        final_result.execution_time = time.time() - start_time
        
        # 缓存结果
        with self._cache_lock:
            self._analysis_cache[cache_key] = final_result
        
        if output_callback:
            output_callback(f"高级检测完成，耗时 {final_result.execution_time:.2f}s")
        
        return final_result
    
    def _static_ast_analysis(self, content: str, script_path: str) -> Dict[str, Set[str]]:
        """静态AST分析"""
        result = {
            'static_imports': set(),
            'conditional_imports': set(),
            'lazy_imports': set(),
            'optional_imports': set()
        }
        
        try:
            tree = ast.parse(content, filename=script_path)
            
            # 分析不同上下文中的导入
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    modules = self._extract_modules_from_import(node)
                    
                    # 判断导入的上下文
                    context = self._get_import_context(node, tree)
                    
                    if context == 'try_except':
                        result['optional_imports'].update(modules)
                    elif context == 'if_statement':
                        result['conditional_imports'].update(modules)
                    elif context == 'function_or_method':
                        result['lazy_imports'].update(modules)
                    else:
                        result['static_imports'].update(modules)
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _string_pattern_analysis(self, content: str) -> Dict[str, Set[str]]:
        """字符串模式分析"""
        result = {
            'string_references': set(),
            'dynamic_imports': set()
        }
        
        # 高级字符串模式
        patterns = {
            'importlib_patterns': [
                r'importlib\.import_module\s*\(\s*[\'"]([^\'\"]+)[\'"]',
                r'importlib\.util\.spec_from_file_location\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            ],
            'import_patterns': [
                r'__import__\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            ],
            'exec_patterns': [
                r'exec\s*\(\s*[\'"].*?import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
                r'eval\s*\(\s*[\'"].*?import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
            ],
            'plugin_patterns': [
                r'load_plugin\s*\(\s*[\'"]([^\'\"]+)[\'"]',
                r'get_plugin\s*\(\s*[\'"]([^\'\"]+)[\'"]',
            ]
        }
        
        for pattern_group, pattern_list in patterns.items():
            for pattern in pattern_list:
                try:
                    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                    for match in matches:
                        if self._is_valid_module_name(match):
                            top_module = match.split('.')[0]
                            result['string_references'].add(top_module)
                            if pattern_group in ['importlib_patterns', 'import_patterns', 'exec_patterns']:
                                result['dynamic_imports'].add(top_module)
                except re.error:
                    continue
        
        return result
    
    def _advanced_pattern_matching(self, content: str) -> Dict[str, Set[str]]:
        """高级模式匹配"""
        result = {
            'plugin_modules': set(),
            'config_driven': set()
        }
        
        # 插件系统模式
        plugin_indicators = [
            'plugin', 'extension', 'addon', 'module', 'handler',
            'driver', 'backend', 'engine', 'provider', 'factory'
        ]
        
        # 配置驱动模式
        config_patterns = [
            r'[\'"]module[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
            r'[\'"]plugin[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
            r'[\'"]handler[\'"]:\s*[\'"]([^\'\"]+)[\'"]',
        ]
        
        for pattern in config_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if self._is_valid_module_name(match):
                    result['config_driven'].add(match.split('.')[0])
        
        return result
    
    def _heuristic_analysis(self, content: str, script_path: str) -> Dict[str, Set[str]]:
        """启发式分析"""
        result = {'heuristic_modules': set()}
        
        # 基于文件名和路径的启发式
        script_dir = os.path.dirname(script_path)
        script_name = os.path.basename(script_path)
        
        # 检查同目录下的Python文件
        try:
            for file in os.listdir(script_dir):
                if file.endswith('.py') and file != script_name:
                    module_name = file[:-3]
                    if module_name in content:
                        result['heuristic_modules'].add(module_name)
        except:
            pass
        
        return result
    
    def _runtime_execution_analysis(self, script_path: str, 
                                   output_callback: Optional[Callable[[str], None]] = None) -> Dict[str, Set[str]]:
        """运行时执行分析"""
        result = {'runtime_discovered': set()}
        
        # 创建监控脚本
        monitor_script = self._create_enhanced_monitor_script(script_path)
        
        try:
            # 执行监控脚本
            process = subprocess.run(
                [self.python_interpreter, monitor_script],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.path.dirname(script_path)
            )
            
            if process.stdout:
                # 解析输出
                for line in process.stdout.strip().split('\n'):
                    if line.startswith('IMPORTED_MODULE:'):
                        module_name = line.replace('IMPORTED_MODULE:', '').strip()
                        if module_name:
                            result['runtime_discovered'].add(module_name.split('.')[0])
        
        except subprocess.TimeoutExpired:
            if output_callback:
                output_callback(f"运行时分析超时 ({self.timeout}s)")
        except Exception as e:
            if output_callback:
                output_callback(f"运行时分析失败: {e}")
        finally:
            # 清理监控脚本
            try:
                os.unlink(monitor_script)
            except:
                pass
        
        return result
    
    def _build_known_modules_db(self) -> Set[str]:
        """构建已知模块数据库"""
        return {
            # Python标准库
            'os', 'sys', 'json', 'time', 'datetime', 'random', 'math',
            'collections', 'itertools', 'functools', 'operator', 'copy',
            'pickle', 'sqlite3', 'urllib', 'http', 'email', 'html',
            'xml', 'csv', 'configparser', 'logging', 'unittest',
            'threading', 'multiprocessing', 'subprocess', 'socket',
            'ssl', 'hashlib', 'hmac', 'base64', 'binascii', 'struct',
            'array', 'queue', 'heapq', 'bisect', 'weakref', 'types',
            'inspect', 'importlib', 'pkgutil', 'modulefinder', 'runpy',
            'ast', 'dis', 'py_compile', 'compileall', 'keyword',
            
            # 常见第三方库
            'numpy', 'pandas', 'matplotlib', 'scipy', 'sklearn',
            'tensorflow', 'torch', 'keras', 'flask', 'django',
            'requests', 'urllib3', 'beautifulsoup4', 'lxml', 'pillow',
            'opencv', 'pyqt5', 'pyqt6', 'tkinter', 'wx', 'kivy',
            'pytest', 'nose', 'mock', 'coverage', 'tox', 'sphinx',
            'setuptools', 'pip', 'wheel', 'twine', 'virtualenv',
        }

    def _is_valid_module_name(self, name: str) -> bool:
        """验证模块名是否有效"""
        if not name or len(name) < 2 or len(name) > 100:
            return False

        # 基本命名规则
        if not name[0].isalpha() and name[0] != '_':
            return False

        if not all(c.isalnum() or c in '_.' for c in name):
            return False

        # 排除明显的非模块名
        excluded = {
            'main', 'name', 'file', 'path', 'version', 'true', 'false',
            'none', 'null', 'self', 'cls', 'args', 'kwargs', 'data',
            'value', 'key', 'item', 'result', 'config', 'settings'
        }

        if name.lower() in excluded:
            return False

        # 如果是已知模块，直接返回True
        if name.lower() in self.known_modules:
            return True

        # 检查命名模式
        import re
        patterns = [
            r'^[a-z][a-z0-9_]*$',      # 小写+下划线
            r'^[A-Z][a-zA-Z0-9]*$',    # 大写开头
        ]

        return any(re.match(pattern, name) for pattern in patterns)

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

    def _get_import_context(self, import_node: ast.AST, tree: ast.AST) -> str:
        """获取导入语句的上下文"""
        # 遍历AST找到导入节点的父节点
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if child is import_node:
                    if isinstance(node, ast.Try):
                        return 'try_except'
                    elif isinstance(node, ast.If):
                        return 'if_statement'
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        return 'function_or_method'
                    elif isinstance(node, ast.ClassDef):
                        return 'class_method'

        return 'module_level'

    def _create_enhanced_monitor_script(self, original_script: str) -> str:
        """创建增强的监控脚本"""
        monitor_code = f'''
import sys
import importlib.util
import traceback

# 保存原始的import函数
original_import = __builtins__['__import__'] if isinstance(__builtins__, dict) else __builtins__.__import__

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

    compiled = compile(code, r"{original_script}", "exec")
    exec(compiled)

except Exception as e:
    print(f"EXECUTION_ERROR:{{str(e)}}")
'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(monitor_code)
            return f.name

    def _merge_and_score_results(self, detection_methods: Dict[str, Dict]) -> AdvancedDetectionResult:
        """合并和评分检测结果"""
        # 初始化结果集合
        static_imports = set()
        dynamic_imports = set()
        conditional_imports = set()
        lazy_imports = set()
        optional_imports = set()
        string_references = set()
        plugin_modules = set()
        config_driven = set()
        runtime_discovered = set()

        confidence_scores = {}

        # 合并各种检测方法的结果
        for method_name, method_result in detection_methods.items():
            if 'error' in method_result:
                continue

            weight = self.strategy_weights.get(method_name, 0.5)

            # 合并不同类型的模块
            for result_type, modules in method_result.items():
                if isinstance(modules, set):
                    for module in modules:
                        if result_type == 'static_imports':
                            static_imports.add(module)
                            confidence_scores[module] = confidence_scores.get(module, 0) + weight * 0.9
                        elif result_type == 'dynamic_imports':
                            dynamic_imports.add(module)
                            confidence_scores[module] = confidence_scores.get(module, 0) + weight * 0.8
                        elif result_type == 'conditional_imports':
                            conditional_imports.add(module)
                            confidence_scores[module] = confidence_scores.get(module, 0) + weight * 0.7
                        elif result_type == 'lazy_imports':
                            lazy_imports.add(module)
                            confidence_scores[module] = confidence_scores.get(module, 0) + weight * 0.7
                        elif result_type == 'optional_imports':
                            optional_imports.add(module)
                            confidence_scores[module] = confidence_scores.get(module, 0) + weight * 0.6
                        elif result_type == 'string_references':
                            string_references.add(module)
                            confidence_scores[module] = confidence_scores.get(module, 0) + weight * 0.5
                        elif result_type == 'plugin_modules':
                            plugin_modules.add(module)
                            confidence_scores[module] = confidence_scores.get(module, 0) + weight * 0.6
                        elif result_type == 'config_driven':
                            config_driven.add(module)
                            confidence_scores[module] = confidence_scores.get(module, 0) + weight * 0.6
                        elif result_type == 'runtime_discovered':
                            runtime_discovered.add(module)
                            confidence_scores[module] = confidence_scores.get(module, 0) + weight * 0.95

        # 标准化置信度分数
        max_score = max(confidence_scores.values()) if confidence_scores else 1.0
        confidence_scores = {k: min(v / max_score, 1.0) for k, v in confidence_scores.items()}

        return AdvancedDetectionResult(
            static_imports=static_imports,
            dynamic_imports=dynamic_imports,
            conditional_imports=conditional_imports,
            lazy_imports=lazy_imports,
            optional_imports=optional_imports,
            string_references=string_references,
            plugin_modules=plugin_modules,
            config_driven=config_driven,
            runtime_discovered=runtime_discovered,
            detection_methods=detection_methods,
            confidence_scores=confidence_scores,
            execution_time=0.0
        )

    def _create_empty_result(self) -> AdvancedDetectionResult:
        """创建空的检测结果"""
        return AdvancedDetectionResult(
            static_imports=set(),
            dynamic_imports=set(),
            conditional_imports=set(),
            lazy_imports=set(),
            optional_imports=set(),
            string_references=set(),
            plugin_modules=set(),
            config_driven=set(),
            runtime_discovered=set(),
            detection_methods={},
            confidence_scores={},
            execution_time=0.0
        )

    def _generate_cache_key(self, script_path: str, use_execution: bool) -> str:
        """生成缓存键"""
        import hashlib

        try:
            # 基于文件内容和修改时间生成缓存键
            with open(script_path, 'rb') as f:
                content_hash = hashlib.md5(f.read()).hexdigest()

            mtime = os.path.getmtime(script_path)
            cache_key = f"{content_hash}_{mtime}_{use_execution}"
            return cache_key
        except:
            return f"{script_path}_{use_execution}"

    def get_all_detected_modules(self, result: AdvancedDetectionResult) -> Set[str]:
        """获取所有检测到的模块"""
        all_modules = set()
        all_modules.update(result.static_imports)
        all_modules.update(result.dynamic_imports)
        all_modules.update(result.conditional_imports)
        all_modules.update(result.lazy_imports)
        all_modules.update(result.optional_imports)
        all_modules.update(result.string_references)
        all_modules.update(result.plugin_modules)
        all_modules.update(result.config_driven)
        all_modules.update(result.runtime_discovered)
        return all_modules

    def get_high_confidence_modules(self, result: AdvancedDetectionResult,
                                   threshold: float = 0.7) -> Set[str]:
        """获取高置信度的模块"""
        return {module for module, score in result.confidence_scores.items()
                if score >= threshold}
