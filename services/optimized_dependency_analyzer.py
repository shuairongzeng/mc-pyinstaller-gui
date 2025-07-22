"""
优化的依赖分析器
集成智能缓存系统，提供高性能的依赖关系分析
"""

import sys
import subprocess
import importlib.util
import hashlib
import time
import threading
from typing import Set, Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

from utils.smart_cache_manager import get_cache_manager

logger = logging.getLogger(__name__)

try:
    from packaging import version
    HAS_PACKAGING = True
except ImportError:
    HAS_PACKAGING = False


@dataclass
class DependencyInfo:
    """依赖信息"""
    name: str
    version: str
    location: str
    is_available: bool
    dependencies: List[str]
    size: int = 0
    license: str = ""
    description: str = ""


@dataclass
class DependencyAnalysisResult:
    """依赖分析结果"""
    dependencies: Dict[str, DependencyInfo]
    conflicts: List[Dict[str, Any]]
    missing: List[str]
    recommendations: List[str]
    version_issues: List[Dict[str, Any]]
    compatibility_matrix: Dict[str, Dict[str, str]]
    analysis_time: float
    cache_hit: bool = False
    total_size: int = 0


class OptimizedDependencyAnalyzer:
    """优化的依赖分析器 - 集成智能缓存系统"""
    
    def __init__(
        self,
        python_interpreter: str = "",
        cache_ttl: int = 3600,  # 1小时缓存
        enable_deep_analysis: bool = True
    ):
        self.python_interpreter = python_interpreter or sys.executable
        self.cache_ttl = cache_ttl
        self.enable_deep_analysis = enable_deep_analysis
        
        # 获取缓存管理器
        self.cache_manager = get_cache_manager()
        
        # 已知冲突和版本模式
        self.known_conflicts = self._load_known_conflicts()
        self.version_patterns = self._load_version_patterns()
        
        # 统计信息
        self.stats = {
            'total_analyses': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'analysis_times': [],
            'conflict_detections': 0
        }
        self.stats_lock = threading.Lock()
    
    def analyze_dependencies(
        self,
        modules: Set[str],
        force_refresh: bool = False
    ) -> DependencyAnalysisResult:
        """分析模块依赖关系"""
        start_time = time.time()
        
        # 生成缓存键
        cache_key = self._generate_cache_key(modules)

        # 尝试从缓存获取结果（除非强制刷新）
        cached_result = None
        if not force_refresh:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                cached_result.cache_hit = True
                self._update_stats('cache_hit')
                return cached_result
        
        # 执行实际分析
        result = self._perform_analysis(modules)
        result.analysis_time = time.time() - start_time
        result.cache_hit = False
        
        # 保存到缓存
        self._save_to_cache(cache_key, result)
        
        # 更新统计
        self._update_stats('cache_miss', result.analysis_time)
        
        return result
    
    def _generate_cache_key(self, modules: Set[str]) -> str:
        """生成缓存键"""
        modules_str = '|'.join(sorted(modules))
        config_str = f"{self.python_interpreter}_{self.enable_deep_analysis}"
        
        combined = f"{modules_str}_{config_str}"
        cache_hash = hashlib.md5(combined.encode()).hexdigest()
        
        return f"dependency_analysis_{cache_hash}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[DependencyAnalysisResult]:
        """从缓存获取分析结果"""
        try:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data and isinstance(cached_data, DependencyAnalysisResult):
                return cached_data
        except Exception as e:
            logger.error(f"Failed to get from cache: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, result: DependencyAnalysisResult):
        """保存分析结果到缓存"""
        try:
            self.cache_manager.set(
                cache_key,
                result,
                ttl=self.cache_ttl,
                tags=['dependency_analysis', 'analysis']
            )
        except Exception as e:
            logger.error(f"Failed to save to cache: {e}")
    
    def _perform_analysis(self, modules: Set[str]) -> DependencyAnalysisResult:
        """执行实际的依赖分析"""
        dependencies = {}
        total_size = 0
        
        # 获取每个模块的详细信息
        for module_name in modules:
            dep_info = self._get_dependency_info(module_name)
            dependencies[module_name] = dep_info
            total_size += dep_info.size
        
        # 检查冲突
        conflicts = self._check_conflicts(modules, dependencies)
        
        # 检查缺失模块
        missing = [name for name, info in dependencies.items() if not info.is_available]
        
        # 检查版本兼容性
        version_issues = self._check_version_compatibility(dependencies)
        
        # 生成兼容性矩阵
        compatibility_matrix = self._build_compatibility_matrix(modules, dependencies)
        
        # 生成建议
        recommendations = self._generate_recommendations({
            'dependencies': dependencies,
            'conflicts': conflicts,
            'missing': missing,
            'version_issues': version_issues
        })
        
        return DependencyAnalysisResult(
            dependencies=dependencies,
            conflicts=conflicts,
            missing=missing,
            recommendations=recommendations,
            version_issues=version_issues,
            compatibility_matrix=compatibility_matrix,
            analysis_time=0.0,  # 将在调用处设置
            total_size=total_size
        )
    
    def _get_dependency_info(self, module_name: str) -> DependencyInfo:
        """获取模块的详细依赖信息"""
        try:
            # 尝试导入模块
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                return DependencyInfo(
                    name=module_name,
                    version="unknown",
                    location="",
                    is_available=False,
                    dependencies=[]
                )
            
            # 获取模块信息
            try:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', 'unknown')
                location = getattr(module, '__file__', spec.origin or '')
            except Exception:
                version = 'unknown'
                location = spec.origin or ''
            
            # 获取依赖关系
            dependencies = self._get_module_dependencies(module_name)
            
            # 计算大小
            size = self._calculate_module_size(location)
            
            return DependencyInfo(
                name=module_name,
                version=version,
                location=location,
                is_available=True,
                dependencies=dependencies,
                size=size
            )
            
        except Exception as e:
            logger.debug(f"Failed to get dependency info for {module_name}: {e}")
            return DependencyInfo(
                name=module_name,
                version="unknown",
                location="",
                is_available=False,
                dependencies=[]
            )
    
    def _get_module_dependencies(self, module_name: str) -> List[str]:
        """获取模块的依赖关系"""
        # 已知的模块依赖关系
        known_deps = {
            'cv2': ['numpy'],
            'matplotlib': ['numpy', 'pyparsing', 'python-dateutil', 'cycler', 'kiwisolver'],
            'pandas': ['numpy', 'python-dateutil', 'pytz'],
            'sklearn': ['numpy', 'scipy', 'joblib', 'threadpoolctl'],
            'tensorflow': ['numpy', 'protobuf', 'absl-py', 'astunparse', 'gast'],
            'torch': ['numpy', 'typing-extensions'],
            'flask': ['werkzeug', 'jinja2', 'click', 'itsdangerous'],
            'django': ['sqlparse', 'pytz', 'asgiref'],
            'requests': ['urllib3', 'certifi', 'chardet', 'idna'],
            'selenium': ['urllib3'],
            'PyQt5': ['sip'],
            'PyQt6': ['sip'],
            'openpyxl': ['et-xmlfile', 'jdcal'],
            'xlsxwriter': [],
            'psutil': [],
            'pillow': [],
            'beautifulsoup4': ['soupsieve'],
            'lxml': [],
            'sqlalchemy': ['greenlet']
        }
        
        return known_deps.get(module_name, [])
    
    def _calculate_module_size(self, location: str) -> int:
        """计算模块大小"""
        if not location:
            return 0
        
        try:
            path = Path(location)
            if path.is_file():
                return path.stat().st_size
            elif path.parent.name == module_name:
                # 包目录
                total_size = 0
                for file_path in path.parent.rglob('*.py'):
                    total_size += file_path.stat().st_size
                return total_size
        except Exception:
            pass
        
        return 0
    
    def _check_conflicts(
        self,
        modules: Set[str],
        dependencies: Dict[str, DependencyInfo]
    ) -> List[Dict[str, Any]]:
        """检查模块冲突"""
        conflicts = []
        
        # 检查已知冲突
        for conflict_set in self.known_conflicts:
            conflicted_modules = [m for m in conflict_set if m in modules]
            if len(conflicted_modules) > 1:
                conflicts.append({
                    'type': 'known_conflict',
                    'modules': conflicted_modules,
                    'description': f"模块 {', '.join(conflicted_modules)} 之间存在已知冲突",
                    'severity': 'high'
                })
        
        # 检查版本冲突
        version_conflicts = self._check_version_conflicts(dependencies)
        conflicts.extend(version_conflicts)
        
        return conflicts

    def _check_version_conflicts(
        self,
        dependencies: Dict[str, DependencyInfo]
    ) -> List[Dict[str, Any]]:
        """检查版本冲突"""
        conflicts = []

        # 检查同一模块的不同版本
        module_versions = {}
        for name, info in dependencies.items():
            if info.is_available and info.version != 'unknown':
                base_name = name.split('.')[0]
                if base_name not in module_versions:
                    module_versions[base_name] = []
                module_versions[base_name].append((name, info.version))

        for base_name, versions in module_versions.items():
            if len(versions) > 1:
                unique_versions = set(v[1] for v in versions)
                if len(unique_versions) > 1:
                    conflicts.append({
                        'type': 'version_conflict',
                        'modules': [v[0] for v in versions],
                        'versions': list(unique_versions),
                        'description': f"模块 {base_name} 存在多个版本: {', '.join(unique_versions)}",
                        'severity': 'medium'
                    })

        return conflicts

    def _check_version_compatibility(
        self,
        dependencies: Dict[str, DependencyInfo]
    ) -> List[Dict[str, Any]]:
        """检查版本兼容性"""
        version_issues = []

        if not HAS_PACKAGING:
            return version_issues

        for module_name, dep_info in dependencies.items():
            if not dep_info.is_available or dep_info.version == "unknown":
                continue

            # 检查版本是否过旧
            min_version = self._get_minimum_version(module_name)
            if min_version:
                try:
                    if version.parse(dep_info.version) < version.parse(min_version):
                        version_issues.append({
                            'module': module_name,
                            'current_version': dep_info.version,
                            'minimum_version': min_version,
                            'issue': 'version_too_old',
                            'recommendation': f'升级到 {min_version} 或更高版本',
                            'severity': 'medium'
                        })
                except Exception:
                    pass

            # 检查版本是否有已知问题
            known_issues = self._get_version_issues(module_name, dep_info.version)
            version_issues.extend(known_issues)

        return version_issues

    def _get_minimum_version(self, module_name: str) -> Optional[str]:
        """获取模块的最低推荐版本"""
        min_versions = {
            'numpy': '1.19.0',
            'pandas': '1.3.0',
            'matplotlib': '3.3.0',
            'scipy': '1.7.0',
            'sklearn': '1.0.0',
            'tensorflow': '2.6.0',
            'torch': '1.9.0',
            'PyQt5': '5.15.0',
            'PyQt6': '6.2.0',
            'requests': '2.25.0',
            'flask': '2.0.0',
            'django': '3.2.0',
            'pillow': '8.0.0',
            'opencv-python': '4.5.0'
        }

        return min_versions.get(module_name)

    def _get_version_issues(self, module_name: str, version_str: str) -> List[Dict[str, Any]]:
        """获取特定版本的已知问题"""
        issues = []

        # 已知问题版本
        problematic_versions = {
            'tensorflow': {
                '2.5.0': '存在内存泄漏问题',
                '2.4.0': 'GPU支持不稳定'
            },
            'torch': {
                '1.8.0': 'CUDA兼容性问题'
            },
            'numpy': {
                '1.19.5': '某些操作性能下降'
            }
        }

        if module_name in problematic_versions:
            module_issues = problematic_versions[module_name]
            if version_str in module_issues:
                issues.append({
                    'module': module_name,
                    'version': version_str,
                    'issue': 'known_problem',
                    'description': module_issues[version_str],
                    'recommendation': '建议升级到更稳定的版本',
                    'severity': 'low'
                })

        return issues

    def _build_compatibility_matrix(
        self,
        modules: Set[str],
        dependencies: Dict[str, DependencyInfo]
    ) -> Dict[str, Dict[str, str]]:
        """构建兼容性矩阵"""
        matrix = {}

        # 已知兼容性规则
        compatibility_rules = {
            ('tensorflow', 'numpy'): 'compatible',
            ('torch', 'numpy'): 'compatible',
            ('pandas', 'numpy'): 'compatible',
            ('matplotlib', 'numpy'): 'compatible',
            ('sklearn', 'numpy'): 'compatible',
            ('sklearn', 'scipy'): 'compatible',
            ('PyQt5', 'PyQt6'): 'conflict',
            ('tensorflow', 'torch'): 'warning',  # 可能冲突
        }

        available_modules = [name for name, info in dependencies.items() if info.is_available]

        for module1 in available_modules:
            matrix[module1] = {}
            for module2 in available_modules:
                if module1 == module2:
                    matrix[module1][module2] = 'self'
                else:
                    # 检查兼容性规则
                    rule_key = tuple(sorted([module1, module2]))
                    if rule_key in compatibility_rules:
                        matrix[module1][module2] = compatibility_rules[rule_key]
                    else:
                        matrix[module1][module2] = 'unknown'

        return matrix

    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        dependencies = analysis_result['dependencies']
        conflicts = analysis_result['conflicts']
        missing = analysis_result['missing']
        version_issues = analysis_result['version_issues']

        # 缺失模块建议
        if missing:
            recommendations.append(f"发现 {len(missing)} 个缺失模块，建议安装: pip install {' '.join(missing[:5])}")

        # 冲突解决建议
        if conflicts:
            high_severity_conflicts = [c for c in conflicts if c.get('severity') == 'high']
            if high_severity_conflicts:
                recommendations.append(f"发现 {len(high_severity_conflicts)} 个高优先级冲突，需要立即解决")

        # 版本升级建议
        outdated_modules = [issue['module'] for issue in version_issues if issue['issue'] == 'version_too_old']
        if outdated_modules:
            recommendations.append(f"建议升级过旧模块: {', '.join(outdated_modules[:3])}")

        # 性能优化建议
        large_modules = [name for name, info in dependencies.items()
                        if info.size > 10 * 1024 * 1024]  # 大于10MB
        if large_modules:
            recommendations.append(f"检测到大型模块 ({', '.join(large_modules[:3])}), 考虑使用 --exclude-module 排除测试文件")

        # 科学计算库建议
        sci_modules = {'numpy', 'scipy', 'pandas', 'matplotlib', 'sklearn'}
        if any(module in dependencies for module in sci_modules):
            recommendations.append("检测到科学计算库，建议在打包时增加内存限制")

        # 机器学习库建议
        ml_modules = {'tensorflow', 'torch', 'sklearn', 'xgboost', 'lightgbm'}
        if any(module in dependencies for module in ml_modules):
            recommendations.append("检测到机器学习库，建议使用GPU版本以提高性能")

        return recommendations

    def _load_known_conflicts(self) -> List[Set[str]]:
        """加载已知冲突模块"""
        return [
            {'PyQt5', 'PyQt6'},
            {'tensorflow', 'tensorflow-gpu'},
            {'opencv-python', 'opencv-contrib-python'},
            {'pillow', 'PIL'},
        ]

    def _load_version_patterns(self) -> Dict[str, str]:
        """加载版本模式"""
        return {
            'numpy': r'^\d+\.\d+\.\d+$',
            'pandas': r'^\d+\.\d+\.\d+$',
            'matplotlib': r'^\d+\.\d+\.\d+$',
        }

    def _update_stats(self, event_type: str, analysis_time: float = None):
        """更新统计信息"""
        with self.stats_lock:
            self.stats['total_analyses'] += 1

            if event_type == 'cache_hit':
                self.stats['cache_hits'] += 1
            elif event_type == 'cache_miss':
                self.stats['cache_misses'] += 1
                if analysis_time:
                    self.stats['analysis_times'].append(analysis_time)

    def get_stats(self) -> Dict[str, Any]:
        """获取分析器统计信息"""
        with self.stats_lock:
            total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
            hit_rate = self.stats['cache_hits'] / total_requests if total_requests > 0 else 0

            avg_analysis_time = 0
            if self.stats['analysis_times']:
                avg_analysis_time = sum(self.stats['analysis_times']) / len(self.stats['analysis_times'])

            return {
                'total_analyses': self.stats['total_analyses'],
                'cache_hit_rate': f"{hit_rate:.2%}",
                'cache_hits': self.stats['cache_hits'],
                'cache_misses': self.stats['cache_misses'],
                'avg_analysis_time': f"{avg_analysis_time:.2f}s",
                'conflict_detections': self.stats['conflict_detections'],
                'cache_stats': self.cache_manager.get_stats()
            }

    def clear_cache(self, tags: List[str] = None) -> int:
        """清空缓存"""
        if tags is None:
            tags = ['dependency_analysis', 'analysis']
        return self.cache_manager.clear(tags)

    def optimize_cache(self) -> Dict[str, Any]:
        """优化缓存性能"""
        return self.cache_manager.optimize()
