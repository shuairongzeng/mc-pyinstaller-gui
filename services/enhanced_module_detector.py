"""
增强的模块检测器
实现智能依赖检测优化，包括缓存机制、框架预设配置、冲突检测等功能
"""
import ast
import os
import sys
import json
import hashlib
import time
import threading
from typing import Set, Dict, List, Optional, Tuple, Any, Callable
from pathlib import Path
import importlib.util
import concurrent.futures
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class DetectionResult:
    """检测结果数据类"""
    detected_modules: Set[str]
    missing_modules: Set[str]
    conflicted_modules: Set[str]
    recommendations: List[str]
    hidden_imports: List[str]
    collect_all: List[str]
    data_files: List[str]
    framework_configs: Dict[str, Any]
    detection_time: float
    cache_hit: bool = False

class EnhancedModuleDetector:
    """增强的模块检测器"""

    def __init__(self, cache_dir: str = ".cache", max_workers: int = 4):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_workers = max_workers
        self.framework_configs = self._load_framework_configs()
        self._detection_cache: Dict[str, DetectionResult] = {}
        self._cache_lock = threading.Lock()
        
        # 性能统计
        self.stats = {
            'total_detections': 0,
            'cache_hits': 0,
            'avg_detection_time': 0.0,
            'framework_matches': defaultdict(int)
        }

    def detect_modules_with_cache(self, script_path: str, 
                                 output_callback: Optional[Callable[[str], None]] = None) -> DetectionResult:
        """带缓存的模块检测"""
        start_time = time.time()
        
        if output_callback:
            output_callback("开始智能模块检测...")
        
        # 计算文件哈希
        file_hash = self._calculate_file_hash(script_path)
        cache_key = f"{script_path}_{file_hash}"
        
        # 尝试从内存缓存加载
        with self._cache_lock:
            if cache_key in self._detection_cache:
                result = self._detection_cache[cache_key]
                result.cache_hit = True
                self.stats['cache_hits'] += 1
                if output_callback:
                    output_callback("从内存缓存加载检测结果")
                return result
        
        # 尝试从磁盘缓存加载
        cache_file = self.cache_dir / f"modules_{file_hash}.json"
        if cache_file.exists():
            try:
                cached_result = self._load_from_disk_cache(cache_file, script_path)
                if cached_result:
                    cached_result.cache_hit = True
                    with self._cache_lock:
                        self._detection_cache[cache_key] = cached_result
                    self.stats['cache_hits'] += 1
                    if output_callback:
                        output_callback("从磁盘缓存加载检测结果")
                    return cached_result
            except Exception as e:
                if output_callback:
                    output_callback(f"缓存加载失败，重新检测: {e}")
        
        # 执行检测
        if output_callback:
            output_callback("执行增强模块检测...")
        
        result = self._detect_modules_enhanced(script_path, output_callback)
        result.detection_time = time.time() - start_time
        result.cache_hit = False
        
        # 保存到缓存
        self._save_to_cache(cache_key, cache_file, result, script_path)
        
        # 更新统计信息
        self.stats['total_detections'] += 1
        self.stats['avg_detection_time'] = (
            (self.stats['avg_detection_time'] * (self.stats['total_detections'] - 1) + 
             result.detection_time) / self.stats['total_detections']
        )
        
        if output_callback:
            output_callback(f"检测完成，耗时 {result.detection_time:.2f}s")
        
        return result

    def _detect_modules_enhanced(self, script_path: str, 
                               output_callback: Optional[Callable[[str], None]] = None) -> DetectionResult:
        """增强的模块检测逻辑"""
        detected_modules = set()
        
        # 并行执行多种检测方法
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                'ast': executor.submit(self._ast_analysis, script_path, output_callback),
                'dynamic': executor.submit(self._detect_dynamic_imports, script_path, output_callback),
                'framework': executor.submit(self._detect_framework_specific, script_path, output_callback)
            }
            
            for name, future in futures.items():
                try:
                    modules = future.result(timeout=30)  # 30秒超时
                    detected_modules.update(modules)
                    if output_callback:
                        output_callback(f"{name}检测完成，发现 {len(modules)} 个模块")
                except Exception as e:
                    if output_callback:
                        output_callback(f"{name}检测失败: {e}")
        
        # 分析结果
        return self._analyze_detection_result(detected_modules, script_path, output_callback)

    def _ast_analysis(self, script_path: str, 
                     output_callback: Optional[Callable[[str], None]] = None) -> Set[str]:
        """增强的AST静态分析"""
        modules = set()
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=script_path)
            
            # 递归分析所有节点
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        modules.add(module_name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        modules.add(module_name)
                        
                # 检测字符串中的模块引用
                elif isinstance(node, ast.Str):
                    potential_modules = self._extract_modules_from_string(node.s)
                    modules.update(potential_modules)
                    
        except Exception as e:
            if output_callback:
                output_callback(f"AST分析失败: {e}")
        
        return modules

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
        except Exception:
            # 如果文件读取失败，使用文件路径和修改时间作为哈希
            hasher.update(file_path.encode())
            if os.path.exists(file_path):
                hasher.update(str(os.path.getmtime(file_path)).encode())
        return hasher.hexdigest()

    def _load_framework_configs(self) -> Dict[str, Dict[str, Any]]:
        """加载框架配置"""
        return {
            'django': {
                'indicators': ['django', 'django.core', 'django.conf'],
                'hidden_imports': [
                    'django.core.management',
                    'django.contrib.auth',
                    'django.contrib.contenttypes',
                    'django.contrib.sessions',
                    'django.contrib.messages',
                    'django.contrib.staticfiles'
                ],
                'collect_all': ['django'],
                'data_files': ['templates', 'static', 'locale'],
                'recommendations': [
                    '建议使用 --collect-all django',
                    '确保包含模板和静态文件目录'
                ]
            },
            'flask': {
                'indicators': ['flask', 'flask.app'],
                'hidden_imports': [
                    'flask.json',
                    'flask.logging',
                    'jinja2.ext',
                    'werkzeug.serving',
                    'werkzeug.middleware'
                ],
                'collect_all': ['flask', 'jinja2'],
                'data_files': ['templates', 'static'],
                'recommendations': [
                    '建议使用 --collect-all flask',
                    '包含模板和静态文件目录'
                ]
            },
            'opencv': {
                'indicators': ['cv2'],
                'hidden_imports': [
                    'numpy.core._multiarray_umath',
                    'numpy.core._multiarray_tests',
                    'numpy.linalg._umath_linalg',
                    'numpy.fft._pocketfft_internal'
                ],
                'collect_all': ['cv2'],
                'collect_binaries': ['cv2'],
                'recommendations': [
                    '建议使用 --collect-all cv2',
                    '可能需要额外的DLL文件'
                ]
            },
            'matplotlib': {
                'indicators': ['matplotlib', 'matplotlib.pyplot'],
                'hidden_imports': [
                    'matplotlib.backends.backend_tkagg',
                    'matplotlib.backends.backend_qt5agg',
                    'matplotlib.figure',
                    'matplotlib.font_manager'
                ],
                'collect_all': ['matplotlib'],
                'collect_data': ['matplotlib'],
                'data_files': ['matplotlib/mpl-data'],
                'recommendations': [
                    '建议使用 --collect-all matplotlib',
                    '包含字体和配置文件'
                ]
            },
            'numpy': {
                'indicators': ['numpy', 'np'],
                'hidden_imports': [
                    'numpy.core._multiarray_umath',
                    'numpy.core._multiarray_tests',
                    'numpy.linalg._umath_linalg',
                    'numpy.fft._pocketfft_internal',
                    'numpy.random._common',
                    'numpy.random.bit_generator'
                ],
                'collect_all': ['numpy'],
                'recommendations': [
                    '建议使用 --collect-all numpy',
                    '科学计算库，建议增加内存限制'
                ]
            },
            'pandas': {
                'indicators': ['pandas', 'pd'],
                'hidden_imports': [
                    'pandas._libs.tslibs.timedeltas',
                    'pandas._libs.tslibs.np_datetime',
                    'pandas._libs.tslibs.nattype',
                    'pandas._libs.properties'
                ],
                'collect_all': ['pandas'],
                'recommendations': [
                    '建议使用 --collect-all pandas',
                    '数据分析库，建议增加内存限制'
                ]
            }
        }

    def _detect_dynamic_imports(self, script_path: str,
                              output_callback: Optional[Callable[[str], None]] = None) -> Set[str]:
        """检测动态导入的模块"""
        modules = set()

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            import re

            # 检测各种动态导入模式
            patterns = [
                r'importlib\.import_module\([\'"]([^\'\"]+)[\'"]\)',
                r'__import__\([\'"]([^\'\"]+)[\'"]\)',
                r'from\s+[\'"]([^\'\"]+)[\'"]\s+import',
                r'exec\([\'"]import\s+([^\'\"]+)[\'"]\)',
                r'eval\([\'"]import\s+([^\'\"]+)[\'"]\)'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    module_name = match.split('.')[0]
                    modules.add(module_name)

        except Exception as e:
            if output_callback:
                output_callback(f"动态导入检测失败: {e}")

        return modules

    def _detect_framework_specific(self, script_path: str,
                                 output_callback: Optional[Callable[[str], None]] = None) -> Set[str]:
        """检测框架特定的模块"""
        modules = set()

        try:
            # 首先进行基本的AST分析
            basic_modules = self._ast_analysis(script_path)

            # 根据检测到的模块匹配框架
            for framework, config in self.framework_configs.items():
                indicators = config.get('indicators', [])
                if any(indicator in basic_modules for indicator in indicators):
                    # 记录框架匹配
                    self.stats['framework_matches'][framework] += 1

                    # 添加框架相关的隐藏导入
                    hidden_imports = config.get('hidden_imports', [])
                    modules.update(hidden_imports)

                    if output_callback:
                        output_callback(f"检测到 {framework} 框架，添加 {len(hidden_imports)} 个相关模块")

        except Exception as e:
            if output_callback:
                output_callback(f"框架特定检测失败: {e}")

        return modules

    def _extract_modules_from_string(self, string_content: str) -> Set[str]:
        """从字符串中提取可能的模块名"""
        modules = set()

        # 检测字符串中的模块引用模式
        import re
        patterns = [
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.(py|pyd|so)\b',  # 文件扩展名
            r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',         # import语句
            r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',  # from import语句
        ]

        for pattern in patterns:
            matches = re.findall(pattern, string_content)
            for match in matches:
                if isinstance(match, tuple):
                    module_name = match[0]
                else:
                    module_name = match

                # 只取顶级模块名
                top_level = module_name.split('.')[0]
                if len(top_level) > 1 and top_level.isidentifier():
                    modules.add(top_level)

        return modules

    def _analyze_detection_result(self, detected_modules: Set[str], script_path: str,
                                output_callback: Optional[Callable[[str], None]] = None) -> DetectionResult:
        """分析检测结果"""
        missing_modules = set()
        conflicted_modules = set()
        recommendations = []
        hidden_imports = []
        collect_all = []
        data_files = []
        framework_configs = {}

        # 检查模块可用性
        available_modules = set()
        for module_name in detected_modules:
            if self._is_module_available(module_name):
                available_modules.add(module_name)
            else:
                missing_modules.add(module_name)
                recommendations.append(f"模块 '{module_name}' 未找到，请检查是否已安装")

        # 检查版本冲突
        conflicts = self._check_version_conflicts(available_modules)
        conflicted_modules.update(conflicts)

        # 生成框架特定的建议
        for framework, config in self.framework_configs.items():
            indicators = config.get('indicators', [])
            if any(indicator in available_modules for indicator in indicators):
                framework_configs[framework] = config

                # 添加隐藏导入
                hidden_imports.extend(config.get('hidden_imports', []))

                # 添加collect-all
                collect_all.extend(config.get('collect_all', []))

                # 添加数据文件建议
                data_files.extend(config.get('data_files', []))

                # 添加框架特定建议
                recommendations.extend(config.get('recommendations', []))

        # 去重
        hidden_imports = list(set(hidden_imports))
        collect_all = list(set(collect_all))
        data_files = list(set(data_files))

        # 生成通用建议
        if missing_modules:
            recommendations.append(f"发现 {len(missing_modules)} 个缺失模块，建议安装")

        if conflicted_modules:
            recommendations.append(f"发现 {len(conflicted_modules)} 个冲突模块，建议检查版本兼容性")

        return DetectionResult(
            detected_modules=detected_modules,
            missing_modules=missing_modules,
            conflicted_modules=conflicted_modules,
            recommendations=recommendations,
            hidden_imports=hidden_imports,
            collect_all=collect_all,
            data_files=data_files,
            framework_configs=framework_configs,
            detection_time=0.0  # 将在调用处设置
        )

    def _is_module_available(self, module_name: str) -> bool:
        """检查模块是否可用"""
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            return False

    def _check_version_conflicts(self, modules: Set[str]) -> Set[str]:
        """检查版本冲突"""
        conflicts = set()

        # 已知的冲突组合
        known_conflicts = {
            ('tensorflow', 'tensorflow-gpu'): "TensorFlow和TensorFlow-GPU不能同时安装",
            ('opencv-python', 'opencv-contrib-python'): "建议只安装opencv-contrib-python",
            ('pillow', 'PIL'): "Pillow是PIL的替代品，不应同时安装",
            ('PyQt5', 'PyQt6'): "PyQt5和PyQt6可能存在冲突",
            ('PySide2', 'PySide6'): "PySide2和PySide6可能存在冲突"
        }

        for conflict_pair, message in known_conflicts.items():
            if all(module in modules for module in conflict_pair):
                conflicts.update(conflict_pair)

        return conflicts

    def _load_from_disk_cache(self, cache_file: Path, script_path: str) -> Optional[DetectionResult]:
        """从磁盘缓存加载检测结果"""
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查缓存是否过期（24小时）
            cache_time = cache_data.get('timestamp', 0)
            if time.time() - cache_time > 24 * 3600:
                return None

            # 检查文件是否被修改
            file_mtime = os.path.getmtime(script_path)
            if file_mtime > cache_time:
                return None

            # 重构DetectionResult
            result_data = cache_data.get('result', {})
            return DetectionResult(
                detected_modules=set(result_data.get('detected_modules', [])),
                missing_modules=set(result_data.get('missing_modules', [])),
                conflicted_modules=set(result_data.get('conflicted_modules', [])),
                recommendations=result_data.get('recommendations', []),
                hidden_imports=result_data.get('hidden_imports', []),
                collect_all=result_data.get('collect_all', []),
                data_files=result_data.get('data_files', []),
                framework_configs=result_data.get('framework_configs', {}),
                detection_time=result_data.get('detection_time', 0.0)
            )

        except Exception:
            return None

    def _save_to_cache(self, cache_key: str, cache_file: Path,
                      result: DetectionResult, script_path: str) -> None:
        """保存检测结果到缓存"""
        try:
            # 保存到内存缓存
            with self._cache_lock:
                self._detection_cache[cache_key] = result

            # 保存到磁盘缓存
            cache_data = {
                'timestamp': time.time(),
                'script_path': script_path,
                'file_hash': self._calculate_file_hash(script_path),
                'result': {
                    'detected_modules': list(result.detected_modules),
                    'missing_modules': list(result.missing_modules),
                    'conflicted_modules': list(result.conflicted_modules),
                    'recommendations': result.recommendations,
                    'hidden_imports': result.hidden_imports,
                    'collect_all': result.collect_all,
                    'data_files': result.data_files,
                    'framework_configs': result.framework_configs,
                    'detection_time': result.detection_time
                }
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            # 缓存保存失败不影响主功能
            print(f"保存缓存失败: {e}")

    def clear_cache(self) -> None:
        """清理缓存"""
        # 清理内存缓存
        with self._cache_lock:
            self._detection_cache.clear()

        # 清理磁盘缓存
        try:
            for cache_file in self.cache_dir.glob("modules_*.json"):
                cache_file.unlink()
        except Exception as e:
            print(f"清理磁盘缓存失败: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        disk_cache_count = len(list(self.cache_dir.glob("modules_*.json")))
        memory_cache_count = len(self._detection_cache)

        cache_hit_rate = 0.0
        if self.stats['total_detections'] > 0:
            cache_hit_rate = self.stats['cache_hits'] / self.stats['total_detections']

        return {
            'memory_cache_count': memory_cache_count,
            'disk_cache_count': disk_cache_count,
            'total_detections': self.stats['total_detections'],
            'cache_hits': self.stats['cache_hits'],
            'cache_hit_rate': cache_hit_rate,
            'avg_detection_time': self.stats['avg_detection_time'],
            'framework_matches': dict(self.stats['framework_matches'])
        }

    def generate_pyinstaller_args(self, script_path: str,
                                output_callback: Optional[Callable[[str], None]] = None) -> List[str]:
        """根据检测结果生成PyInstaller参数"""
        result = self.detect_modules_with_cache(script_path, output_callback)
        args = []

        # 添加隐藏导入
        for module in result.hidden_imports:
            args.append(f"--hidden-import={module}")

        # 添加collect-all参数
        for module in result.collect_all:
            args.append(f"--collect-all={module}")

        # 根据框架配置添加特殊参数
        for framework, config in result.framework_configs.items():
            # 添加collect-data
            if 'collect_data' in config:
                for data in config['collect_data']:
                    args.append(f"--collect-data={data}")

            # 添加collect-binaries
            if 'collect_binaries' in config:
                for binary in config['collect_binaries']:
                    args.append(f"--collect-binaries={binary}")

        # 检查常见的配置文件
        script_dir = os.path.dirname(script_path)
        config_files = ['config.json', 'config.yaml', 'config.ini', 'settings.json']
        for config_file in config_files:
            config_path = os.path.join(script_dir, config_file)
            if os.path.exists(config_path):
                args.append(f"--add-data={os.path.abspath(config_path)};.")

        return args

    def analyze_dependencies(self, script_path: str,
                           output_callback: Optional[Callable[[str], None]] = None) -> DetectionResult:
        """分析依赖关系和冲突（公共接口）"""
        return self.detect_modules_with_cache(script_path, output_callback)
