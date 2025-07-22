"""
优化的模块检测器
集成智能缓存系统，提供高性能的模块检测和依赖分析
"""

import ast
import os
import sys
import time
import hashlib
import threading
from pathlib import Path
from typing import Set, List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from utils.smart_cache_manager import get_cache_manager, CacheItem
from config.framework_templates import FrameworkTemplates

logger = logging.getLogger(__name__)


@dataclass
class ModuleDetectionResult:
    """模块检测结果"""
    detected_modules: Set[str]
    hidden_imports: List[str]
    collect_all: List[str]
    data_files: List[Tuple[str, str]]
    missing_modules: List[str]
    framework_configs: Dict[str, Any]
    recommendations: List[str]
    detection_time: float
    cache_hit: bool = False
    detection_methods: Dict[str, int] = None
    
    def __post_init__(self):
        if self.detection_methods is None:
            self.detection_methods = {}


class OptimizedModuleDetector:
    """优化的模块检测器 - 集成智能缓存系统"""
    
    def __init__(
        self,
        use_ast: bool = True,
        use_dynamic_analysis: bool = True,
        use_framework_detection: bool = True,
        max_workers: int = 4,
        cache_ttl: int = 7200,  # 2小时缓存
        enable_parallel: bool = True
    ):
        self.use_ast = use_ast
        self.use_dynamic_analysis = use_dynamic_analysis
        self.use_framework_detection = use_framework_detection
        self.max_workers = max_workers
        self.cache_ttl = cache_ttl
        self.enable_parallel = enable_parallel
        
        # 获取缓存管理器
        self.cache_manager = get_cache_manager()
        
        # 框架配置
        self.framework_templates = FrameworkTemplates()
        self.framework_configs = self.framework_templates.get_all_templates()
        
        # 统计信息
        self.stats = {
            'total_detections': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'detection_times': [],
            'framework_matches': {},
            'method_performance': {}
        }
        self.stats_lock = threading.Lock()
    
    def detect_modules(
        self,
        script_path: str,
        output_callback: Optional[Callable[[str], None]] = None,
        force_refresh: bool = False
    ) -> ModuleDetectionResult:
        """主要的模块检测接口"""
        start_time = time.time()
        
        if output_callback:
            output_callback("开始优化模块检测...")
        
        # 生成缓存键
        cache_key = self._generate_cache_key(script_path)

        # 尝试从缓存获取结果（除非强制刷新）
        cached_result = None
        if not force_refresh:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                cached_result.cache_hit = True
                self._update_stats('cache_hit')
                if output_callback:
                    output_callback(f"从缓存加载检测结果 (耗时: {time.time() - start_time:.2f}s)")
                return cached_result
        
        # 执行实际检测
        if output_callback:
            output_callback("执行模块检测分析...")
        
        result = self._perform_detection(script_path, output_callback)
        result.detection_time = time.time() - start_time
        result.cache_hit = False
        
        # 保存到缓存
        self._save_to_cache(cache_key, result)
        
        # 更新统计
        self._update_stats('cache_miss', result.detection_time)
        
        if output_callback:
            output_callback(f"检测完成 (耗时: {result.detection_time:.2f}s)")
        
        return result
    
    def _generate_cache_key(self, script_path: str) -> str:
        """生成缓存键"""
        try:
            # 计算文件哈希
            with open(script_path, 'rb') as f:
                file_content = f.read()
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # 包含检测配置信息
            config_str = f"{self.use_ast}_{self.use_dynamic_analysis}_{self.use_framework_detection}"
            config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
            
            return f"module_detection_{file_hash}_{config_hash}"
        except Exception as e:
            logger.error(f"Failed to generate cache key: {e}")
            return f"module_detection_{abs(hash(script_path))}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[ModuleDetectionResult]:
        """从缓存获取检测结果"""
        try:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data and isinstance(cached_data, ModuleDetectionResult):
                return cached_data
        except Exception as e:
            logger.error(f"Failed to get from cache: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, result: ModuleDetectionResult):
        """保存检测结果到缓存"""
        try:
            self.cache_manager.set(
                cache_key,
                result,
                ttl=self.cache_ttl,
                tags=['module_detection', 'analysis']
            )
        except Exception as e:
            logger.error(f"Failed to save to cache: {e}")
    
    def _perform_detection(
        self,
        script_path: str,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> ModuleDetectionResult:
        """执行实际的模块检测"""
        detected_modules = set()
        detection_methods = {}
        
        # 准备检测任务
        detection_tasks = []
        
        if self.use_ast:
            detection_tasks.append(('ast', self._ast_detection))
        
        if self.use_dynamic_analysis:
            detection_tasks.append(('dynamic', self._dynamic_detection))
        
        if self.use_framework_detection:
            detection_tasks.append(('framework', self._framework_detection))
        
        # 执行检测任务
        if self.enable_parallel and len(detection_tasks) > 1:
            # 并行执行
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(task_func, script_path, output_callback): task_name
                    for task_name, task_func in detection_tasks
                }
                
                for future in as_completed(futures):
                    task_name = futures[future]
                    try:
                        modules = future.result(timeout=30)
                        detected_modules.update(modules)
                        detection_methods[task_name] = len(modules)
                        
                        if output_callback:
                            output_callback(f"{task_name}检测完成，发现 {len(modules)} 个模块")
                    except Exception as e:
                        logger.error(f"{task_name} detection failed: {e}")
                        detection_methods[task_name] = 0
                        if output_callback:
                            output_callback(f"{task_name}检测失败: {e}")
        else:
            # 串行执行
            for task_name, task_func in detection_tasks:
                try:
                    modules = task_func(script_path, output_callback)
                    detected_modules.update(modules)
                    detection_methods[task_name] = len(modules)
                    
                    if output_callback:
                        output_callback(f"{task_name}检测完成，发现 {len(modules)} 个模块")
                except Exception as e:
                    logger.error(f"{task_name} detection failed: {e}")
                    detection_methods[task_name] = 0
                    if output_callback:
                        output_callback(f"{task_name}检测失败: {e}")
        
        # 分析检测结果
        return self._analyze_detection_result(
            detected_modules, script_path, detection_methods, output_callback
        )
    
    def _ast_detection(
        self,
        script_path: str,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> Set[str]:
        """AST静态分析检测"""
        modules = set()
        
        try:
            if output_callback:
                output_callback("执行AST静态分析...")
            
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=script_path)
            
            # 遍历AST节点
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
                elif isinstance(node, ast.Call):
                    if (isinstance(node.func, ast.Name) and 
                        node.func.id == '__import__' and 
                        node.args):
                        if isinstance(node.args[0], ast.Str):
                            module_name = node.args[0].s.split('.')[0]
                            modules.add(module_name)
                        elif isinstance(node.args[0], ast.Constant):
                            module_name = str(node.args[0].value).split('.')[0]
                            modules.add(module_name)
            
            # 递归检测导入的本地模块
            local_modules = self._detect_local_imports(script_path, tree)
            modules.update(local_modules)
            
        except Exception as e:
            logger.error(f"AST detection failed: {e}")
            if output_callback:
                output_callback(f"AST分析失败: {e}")
        
        return modules

    def _detect_local_imports(self, script_path: str, tree: ast.AST) -> Set[str]:
        """检测本地模块导入"""
        local_modules = set()
        script_dir = Path(script_path).parent

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level > 0:  # 相对导入
                    continue

                if node.module:
                    # 检查是否为本地模块
                    module_parts = node.module.split('.')
                    potential_file = script_dir / f"{module_parts[0]}.py"
                    potential_dir = script_dir / module_parts[0] / "__init__.py"

                    if potential_file.exists() or potential_dir.exists():
                        # 递归分析本地模块
                        try:
                            if potential_file.exists():
                                sub_modules = self._analyze_local_module(potential_file)
                            else:
                                sub_modules = self._analyze_local_module(potential_dir)
                            local_modules.update(sub_modules)
                        except Exception as e:
                            logger.debug(f"Failed to analyze local module {node.module}: {e}")

        return local_modules

    def _analyze_local_module(self, module_path: Path) -> Set[str]:
        """分析本地模块的依赖"""
        modules = set()

        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=str(module_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        modules.add(module_name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and not node.module.startswith('.'):
                        module_name = node.module.split('.')[0]
                        modules.add(module_name)

        except Exception as e:
            logger.debug(f"Failed to analyze local module {module_path}: {e}")

        return modules

    def _dynamic_detection(
        self,
        script_path: str,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> Set[str]:
        """动态导入检测"""
        modules = set()

        try:
            if output_callback:
                output_callback("执行动态导入检测...")

            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检测常见的动态导入模式
            dynamic_patterns = [
                r'importlib\.import_module\([\'"]([^\'\"]+)[\'"]',
                r'__import__\([\'"]([^\'\"]+)[\'"]',
                r'exec\([\'"]import\s+([^\'\"]+)[\'"]',
                r'eval\([\'"]import\s+([^\'\"]+)[\'"]',
            ]

            import re
            for pattern in dynamic_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    module_name = match.split('.')[0]
                    modules.add(module_name)

            # 检测字符串中的模块引用
            string_modules = self._detect_string_modules(content)
            modules.update(string_modules)

        except Exception as e:
            logger.error(f"Dynamic detection failed: {e}")
            if output_callback:
                output_callback(f"动态导入检测失败: {e}")

        return modules

    def _detect_string_modules(self, content: str) -> Set[str]:
        """检测字符串中可能的模块引用"""
        modules = set()

        # 常见的Python标准库模块
        common_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'collections',
            'itertools', 'functools', 'operator', 'math', 'random', 'string',
            'urllib', 'http', 'socket', 'threading', 'multiprocessing',
            'subprocess', 'logging', 'argparse', 'configparser', 'sqlite3',
            'csv', 'xml', 'html', 'email', 'base64', 'hashlib', 'hmac',
            'pickle', 'shelve', 'gzip', 'zipfile', 'tarfile', 'shutil',
            'tempfile', 'glob', 'fnmatch', 'linecache', 'fileinput'
        }

        # 在字符串中查找可能的模块名
        import re
        for module in common_modules:
            if re.search(rf'\b{module}\b', content):
                modules.add(module)

        return modules

    def _framework_detection(
        self,
        script_path: str,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> Set[str]:
        """框架特定检测"""
        modules = set()

        try:
            if output_callback:
                output_callback("执行框架特定检测...")

            # 首先进行基本的AST分析获取导入的模块
            basic_modules = self._ast_detection(script_path)

            # 根据检测到的模块匹配框架
            matched_frameworks = []
            for framework_name, config in self.framework_configs.items():
                indicators = config.get('indicators', [])
                if any(indicator in basic_modules for indicator in indicators):
                    matched_frameworks.append((framework_name, config))

                    # 添加框架相关的隐藏导入
                    hidden_imports = config.get('hidden_imports', [])
                    modules.update(hidden_imports)

                    if output_callback:
                        output_callback(f"检测到 {framework_name} 框架")

            # 更新统计信息
            with self.stats_lock:
                for framework_name, _ in matched_frameworks:
                    self.stats['framework_matches'][framework_name] = (
                        self.stats['framework_matches'].get(framework_name, 0) + 1
                    )

        except Exception as e:
            logger.error(f"Framework detection failed: {e}")
            if output_callback:
                output_callback(f"框架检测失败: {e}")

        return modules

    def _analyze_detection_result(
        self,
        detected_modules: Set[str],
        script_path: str,
        detection_methods: Dict[str, int],
        output_callback: Optional[Callable[[str], None]] = None
    ) -> ModuleDetectionResult:
        """分析检测结果并生成完整的结果对象"""

        if output_callback:
            output_callback("分析检测结果...")

        # 检查模块可用性
        missing_modules = []
        available_modules = set()

        for module_name in detected_modules:
            if self._is_module_available(module_name):
                available_modules.add(module_name)
            else:
                missing_modules.append(module_name)

        # 生成隐藏导入建议
        hidden_imports = self._generate_hidden_imports(available_modules)

        # 生成collect_all建议
        collect_all = self._generate_collect_all(available_modules)

        # 生成数据文件建议
        data_files = self._generate_data_files(available_modules, script_path)

        # 匹配框架配置
        framework_configs = self._match_framework_configs(available_modules)

        # 生成建议
        recommendations = self._generate_recommendations(
            available_modules, missing_modules, framework_configs
        )

        if output_callback:
            output_callback(f"检测完成: 发现 {len(available_modules)} 个可用模块")

        return ModuleDetectionResult(
            detected_modules=available_modules,
            hidden_imports=hidden_imports,
            collect_all=collect_all,
            data_files=data_files,
            missing_modules=missing_modules,
            framework_configs=framework_configs,
            recommendations=recommendations,
            detection_time=0.0,  # 将在调用处设置
            detection_methods=detection_methods
        )

    def _is_module_available(self, module_name: str) -> bool:
        """检查模块是否可用"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
        except Exception:
            return False

    def _generate_hidden_imports(self, modules: Set[str]) -> List[str]:
        """生成隐藏导入建议"""
        hidden_imports = []

        # 模块到隐藏导入的映射
        module_mappings = {
            'cv2': ['cv2', 'numpy'],
            'PIL': ['PIL._imaging', 'PIL._imagingmath', 'PIL._imagingft'],
            'matplotlib': ['matplotlib.backends.backend_tkagg'],
            'pandas': ['pandas._libs.tslibs.timedeltas'],
            'numpy': ['numpy.core._multiarray_umath'],
            'scipy': ['scipy.sparse.csgraph._validation'],
            'sklearn': ['sklearn.utils._cython_blas'],
            'tensorflow': ['tensorflow.python.eager.context'],
            'torch': ['torch._C'],
            'PyQt5': ['PyQt5.sip'],
            'PyQt6': ['PyQt6.sip'],
            'tkinter': ['tkinter.ttk', 'tkinter.messagebox'],
            'requests': ['urllib3.util.retry'],
            'selenium': ['selenium.webdriver.chrome.service'],
            'openpyxl': ['openpyxl.cell._writer'],
            'xlsxwriter': ['xlsxwriter.workbook'],
            'psutil': ['psutil._psutil_windows', 'psutil._psutil_posix'],
            'win32api': ['win32api', 'win32con', 'pywintypes'],
            'pyautogui': ['pyscreeze', 'pymsgbox', 'pytweening']
        }

        for module in modules:
            if module in module_mappings:
                hidden_imports.extend(module_mappings[module])

            # 模糊匹配
            for key, imports in module_mappings.items():
                if module.startswith(key + '.') or key.startswith(module + '.'):
                    hidden_imports.extend(imports)

        return list(set(hidden_imports))

    def _generate_collect_all(self, modules: Set[str]) -> List[str]:
        """生成collect_all建议"""
        collect_all_modules = []

        # 需要collect_all的模块
        collect_all_candidates = {
            'django', 'flask', 'fastapi', 'tornado',
            'numpy', 'scipy', 'pandas', 'matplotlib',
            'tensorflow', 'torch', 'sklearn',
            'PyQt5', 'PyQt6', 'tkinter',
            'requests', 'urllib3', 'aiohttp',
            'sqlalchemy', 'pymongo', 'redis'
        }

        for module in modules:
            if module in collect_all_candidates:
                collect_all_modules.append(module)

        return collect_all_modules

    def _generate_data_files(self, modules: Set[str], script_path: str) -> List[Tuple[str, str]]:
        """生成数据文件建议"""
        data_files = []
        script_dir = Path(script_path).parent

        # 检查常见的数据文件目录
        common_data_dirs = ['templates', 'static', 'data', 'assets', 'resources', 'config']

        for dir_name in common_data_dirs:
            data_dir = script_dir / dir_name
            if data_dir.exists() and data_dir.is_dir():
                data_files.append((str(data_dir), dir_name))

        # 框架特定的数据文件
        if 'django' in modules:
            for dir_name in ['templates', 'static', 'locale', 'media']:
                data_dir = script_dir / dir_name
                if data_dir.exists():
                    data_files.append((str(data_dir), dir_name))

        if 'flask' in modules:
            for dir_name in ['templates', 'static']:
                data_dir = script_dir / dir_name
                if data_dir.exists():
                    data_files.append((str(data_dir), dir_name))

        return data_files

    def _match_framework_configs(self, modules: Set[str]) -> Dict[str, Any]:
        """匹配框架配置"""
        matched_configs = {}

        for framework_name, config in self.framework_configs.items():
            indicators = config.get('indicators', [])
            if any(indicator in modules for indicator in indicators):
                matched_configs[framework_name] = config

        return matched_configs

    def _generate_recommendations(
        self,
        available_modules: Set[str],
        missing_modules: List[str],
        framework_configs: Dict[str, Any]
    ) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 缺失模块建议
        if missing_modules:
            recommendations.append(f"发现 {len(missing_modules)} 个缺失模块，建议安装: {', '.join(missing_modules[:5])}")

        # 框架特定建议
        for framework_name, config in framework_configs.items():
            framework_recommendations = config.get('recommendations', [])
            recommendations.extend(framework_recommendations)

        # 性能优化建议
        if any('numpy' in module for module in available_modules):
            recommendations.append("检测到科学计算库，建议使用 --exclude-module matplotlib.tests 减小体积")

        if any('tensorflow' in module or 'torch' in module for module in available_modules):
            recommendations.append("检测到机器学习库，建议使用 --exclude-module tests 减小体积")

        if len(available_modules) > 50:
            recommendations.append("检测到大量模块，建议使用虚拟环境减少不必要的依赖")

        return recommendations

    def _update_stats(self, event_type: str, detection_time: float = None):
        """更新统计信息"""
        with self.stats_lock:
            self.stats['total_detections'] += 1

            if event_type == 'cache_hit':
                self.stats['cache_hits'] += 1
            elif event_type == 'cache_miss':
                self.stats['cache_misses'] += 1
                if detection_time:
                    self.stats['detection_times'].append(detection_time)

    def get_stats(self) -> Dict[str, Any]:
        """获取检测器统计信息"""
        with self.stats_lock:
            total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
            hit_rate = self.stats['cache_hits'] / total_requests if total_requests > 0 else 0

            avg_detection_time = 0
            if self.stats['detection_times']:
                avg_detection_time = sum(self.stats['detection_times']) / len(self.stats['detection_times'])

            return {
                'total_detections': self.stats['total_detections'],
                'cache_hit_rate': f"{hit_rate:.2%}",
                'cache_hits': self.stats['cache_hits'],
                'cache_misses': self.stats['cache_misses'],
                'avg_detection_time': f"{avg_detection_time:.2f}s",
                'framework_matches': dict(self.stats['framework_matches']),
                'cache_stats': self.cache_manager.get_stats()
            }

    def clear_cache(self, tags: List[str] = None) -> int:
        """清空缓存"""
        if tags is None:
            tags = ['module_detection', 'analysis']
        return self.cache_manager.clear(tags)

    def optimize_cache(self) -> Dict[str, Any]:
        """优化缓存性能"""
        return self.cache_manager.optimize()
