"""
依赖分析器
分析模块依赖关系、版本冲突和兼容性问题
"""
import sys
import subprocess
import importlib.util
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
import re

# 尝试导入可选依赖
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
class DependencyInfo:
    """依赖信息"""
    name: str
    version: str
    location: str
    dependencies: List[str]
    is_available: bool
    conflicts: List[str]

@dataclass
class ConflictInfo:
    """冲突信息"""
    module1: str
    module2: str
    conflict_type: str
    description: str
    resolution: str

class DependencyAnalyzer:
    """依赖分析器"""
    
    def __init__(self, python_interpreter: str = ""):
        self.python_interpreter = python_interpreter or sys.executable
        self.known_conflicts = self._load_known_conflicts()
        self.version_patterns = self._load_version_patterns()
    
    def analyze_dependencies(self, modules: Set[str]) -> Dict[str, Any]:
        """分析模块依赖关系"""
        result = {
            'dependencies': {},
            'conflicts': [],
            'missing': [],
            'recommendations': [],
            'version_issues': [],
            'compatibility_matrix': {}
        }
        
        # 获取每个模块的详细信息
        for module_name in modules:
            dep_info = self._get_dependency_info(module_name)
            result['dependencies'][module_name] = dep_info
            
            if not dep_info.is_available:
                result['missing'].append(module_name)
        
        # 检查冲突
        conflicts = self._check_conflicts(modules)
        result['conflicts'] = conflicts
        
        # 检查版本兼容性
        version_issues = self._check_version_compatibility(result['dependencies'])
        result['version_issues'] = version_issues
        
        # 生成兼容性矩阵
        result['compatibility_matrix'] = self._build_compatibility_matrix(modules)
        
        # 生成建议
        result['recommendations'] = self._generate_recommendations(result)
        
        return result
    
    def _get_dependency_info(self, module_name: str) -> DependencyInfo:
        """获取模块依赖信息"""
        try:
            # 检查模块是否可用
            spec = importlib.util.find_spec(module_name)
            is_available = spec is not None
            
            if not is_available:
                return DependencyInfo(
                    name=module_name,
                    version="",
                    location="",
                    dependencies=[],
                    is_available=False,
                    conflicts=[]
                )
            
            # 获取版本信息
            version_info = self._get_module_version(module_name)
            location = spec.origin if spec.origin else ""
            
            # 获取依赖关系
            dependencies = self._get_module_dependencies(module_name)
            
            # 检查已知冲突
            conflicts = self._get_module_conflicts(module_name)
            
            return DependencyInfo(
                name=module_name,
                version=version_info,
                location=location,
                dependencies=dependencies,
                is_available=True,
                conflicts=conflicts
            )
            
        except Exception as e:
            return DependencyInfo(
                name=module_name,
                version="",
                location="",
                dependencies=[],
                is_available=False,
                conflicts=[f"获取信息失败: {e}"]
            )
    
    def _get_module_version(self, module_name: str) -> str:
        """获取模块版本"""
        try:
            # 尝试使用pkg_resources
            if HAS_PKG_RESOURCES:
                try:
                    dist = pkg_resources.get_distribution(module_name)
                    return dist.version
                except pkg_resources.DistributionNotFound:
                    pass
            
            # 尝试导入模块并获取版本属性
            try:
                module = importlib.import_module(module_name)
                for attr in ['__version__', 'version', 'VERSION']:
                    if hasattr(module, attr):
                        version_attr = getattr(module, attr)
                        if isinstance(version_attr, str):
                            return version_attr
                        elif hasattr(version_attr, '__str__'):
                            return str(version_attr)
            except ImportError:
                pass
            
            # 使用subprocess查询
            try:
                cmd = [self.python_interpreter, "-c", 
                       f"import {module_name}; print(getattr({module_name}, '__version__', 'unknown'))"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_str = result.stdout.strip()
                    if version_str != 'unknown':
                        return version_str
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass
            
            return "unknown"
            
        except Exception:
            return "unknown"
    
    def _get_module_dependencies(self, module_name: str) -> List[str]:
        """获取模块依赖"""
        dependencies = []
        
        try:
            # 使用pkg_resources获取依赖
            if HAS_PKG_RESOURCES:
                try:
                    dist = pkg_resources.get_distribution(module_name)
                    for req in dist.requires():
                        dependencies.append(req.project_name)
                except pkg_resources.DistributionNotFound:
                    pass
            
            # 添加已知的依赖关系
            known_deps = self._get_known_dependencies(module_name)
            dependencies.extend(known_deps)
            
        except Exception:
            pass
        
        return list(set(dependencies))  # 去重
    
    def _get_known_dependencies(self, module_name: str) -> List[str]:
        """获取已知的模块依赖关系"""
        known_deps = {
            'cv2': ['numpy'],
            'matplotlib': ['numpy', 'pyparsing', 'python-dateutil', 'cycler'],
            'pandas': ['numpy', 'python-dateutil', 'pytz'],
            'sklearn': ['numpy', 'scipy', 'joblib'],
            'tensorflow': ['numpy', 'protobuf', 'absl-py'],
            'torch': ['numpy'],
            'flask': ['werkzeug', 'jinja2', 'click', 'itsdangerous'],
            'django': ['sqlparse', 'pytz'],
            'requests': ['urllib3', 'certifi', 'chardet', 'idna'],
            'selenium': ['urllib3'],
            'PIL': [],
            'PyQt5': ['sip'],
            'PyQt6': ['sip']
        }
        
        return known_deps.get(module_name, [])
    
    def _get_module_conflicts(self, module_name: str) -> List[str]:
        """获取模块冲突信息"""
        conflicts = []
        
        for conflict_pair, info in self.known_conflicts.items():
            if module_name in conflict_pair:
                other_module = conflict_pair[0] if conflict_pair[1] == module_name else conflict_pair[1]
                conflicts.append(f"与 {other_module} 冲突: {info['description']}")
        
        return conflicts
    
    def _check_conflicts(self, modules: Set[str]) -> List[ConflictInfo]:
        """检查模块冲突"""
        conflicts = []
        
        for conflict_pair, info in self.known_conflicts.items():
            module1, module2 = conflict_pair
            if module1 in modules and module2 in modules:
                conflicts.append(ConflictInfo(
                    module1=module1,
                    module2=module2,
                    conflict_type=info['type'],
                    description=info['description'],
                    resolution=info['resolution']
                ))
        
        return conflicts
    
    def _check_version_compatibility(self, dependencies: Dict[str, DependencyInfo]) -> List[Dict[str, Any]]:
        """检查版本兼容性"""
        version_issues = []
        
        for module_name, dep_info in dependencies.items():
            if not dep_info.is_available or dep_info.version == "unknown":
                continue
            
            # 检查版本是否过旧
            min_version = self._get_minimum_version(module_name)
            if min_version and dep_info.version != "unknown" and HAS_PACKAGING:
                try:
                    if version.parse(dep_info.version) < version.parse(min_version):
                        version_issues.append({
                            'module': module_name,
                            'current_version': dep_info.version,
                            'minimum_version': min_version,
                            'issue': 'version_too_old',
                            'recommendation': f'升级到 {min_version} 或更高版本'
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
            'pandas': '1.0.0',
            'matplotlib': '3.0.0',
            'opencv-python': '4.0.0',
            'tensorflow': '2.0.0',
            'torch': '1.7.0',
            'PyQt5': '5.12.0',
            'PyQt6': '6.0.0',
            'requests': '2.20.0',
            'flask': '1.0.0',
            'django': '3.0.0'
        }
        
        return min_versions.get(module_name)
    
    def _get_version_issues(self, module_name: str, version_str: str) -> List[Dict[str, Any]]:
        """获取特定版本的已知问题"""
        issues = []
        
        # 已知的版本问题
        known_issues = {
            'tensorflow': {
                '2.0.0': '初始版本，可能存在稳定性问题',
                '2.1.0': '某些GPU配置下可能出现问题'
            },
            'numpy': {
                '1.16.0': '与某些科学计算库不兼容'
            }
        }
        
        if module_name in known_issues and version_str in known_issues[module_name]:
            issues.append({
                'module': module_name,
                'version': version_str,
                'issue': 'known_issue',
                'description': known_issues[module_name][version_str],
                'recommendation': '考虑升级到更稳定的版本'
            })
        
        return issues
    
    def _build_compatibility_matrix(self, modules: Set[str]) -> Dict[str, Dict[str, str]]:
        """构建兼容性矩阵"""
        matrix = {}
        
        for module1 in modules:
            matrix[module1] = {}
            for module2 in modules:
                if module1 == module2:
                    matrix[module1][module2] = 'self'
                else:
                    compatibility = self._check_module_compatibility(module1, module2)
                    matrix[module1][module2] = compatibility
        
        return matrix
    
    def _check_module_compatibility(self, module1: str, module2: str) -> str:
        """检查两个模块的兼容性"""
        # 检查已知冲突
        for conflict_pair, info in self.known_conflicts.items():
            if (module1 in conflict_pair and module2 in conflict_pair):
                return 'conflict'
        
        # 检查已知的良好兼容性
        good_combinations = {
            ('numpy', 'pandas'),
            ('numpy', 'matplotlib'),
            ('numpy', 'opencv-python'),
            ('flask', 'jinja2'),
            ('django', 'psycopg2'),
            ('requests', 'urllib3')
        }
        
        if (module1, module2) in good_combinations or (module2, module1) in good_combinations:
            return 'compatible'
        
        return 'unknown'
    
    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 缺失模块建议
        if analysis_result['missing']:
            recommendations.append(
                f"发现 {len(analysis_result['missing'])} 个缺失模块，"
                f"建议安装: pip install {' '.join(analysis_result['missing'])}"
            )
        
        # 冲突解决建议
        for conflict in analysis_result['conflicts']:
            recommendations.append(f"冲突解决: {conflict.resolution}")
        
        # 版本升级建议
        for issue in analysis_result['version_issues']:
            if issue.get('issue') == 'version_too_old':
                recommendations.append(
                    f"建议升级 {issue['module']} 从 {issue['current_version']} "
                    f"到 {issue['minimum_version']} 或更高版本"
                )
        
        # 性能优化建议
        deps = analysis_result['dependencies']
        if any('numpy' in name for name in deps.keys()):
            recommendations.append("检测到科学计算库，建议增加内存限制参数")
        
        if any('tensorflow' in name or 'torch' in name for name in deps.keys()):
            recommendations.append("检测到机器学习库，建议使用GPU版本以提高性能")
        
        return recommendations
    
    def _load_known_conflicts(self) -> Dict[Tuple[str, str], Dict[str, str]]:
        """加载已知的模块冲突"""
        return {
            ('tensorflow', 'tensorflow-gpu'): {
                'type': 'mutual_exclusive',
                'description': 'TensorFlow和TensorFlow-GPU不能同时安装',
                'resolution': '只安装其中一个版本'
            },
            ('opencv-python', 'opencv-contrib-python'): {
                'type': 'redundant',
                'description': 'opencv-contrib-python包含opencv-python的所有功能',
                'resolution': '建议只安装opencv-contrib-python'
            },
            ('pillow', 'PIL'): {
                'type': 'replacement',
                'description': 'Pillow是PIL的现代替代品',
                'resolution': '使用Pillow替代PIL'
            },
            ('PyQt5', 'PyQt6'): {
                'type': 'version_conflict',
                'description': 'PyQt5和PyQt6可能存在兼容性问题',
                'resolution': '选择其中一个版本使用'
            },
            ('PySide2', 'PySide6'): {
                'type': 'version_conflict',
                'description': 'PySide2和PySide6可能存在兼容性问题',
                'resolution': '选择其中一个版本使用'
            }
        }
    
    def _load_version_patterns(self) -> Dict[str, str]:
        """加载版本模式"""
        return {
            'semantic': r'^\d+\.\d+\.\d+',
            'date': r'^\d{4}\.\d{2}\.\d{2}',
            'simple': r'^\d+\.\d+'
        }
