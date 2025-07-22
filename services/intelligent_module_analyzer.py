"""
智能模块分析器
整合多种检测方法，提供最准确的模块分析结果
"""

import os
import sys
import time
import logging
from typing import Set, Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入各种检测器
from .advanced_dynamic_detector import AdvancedDynamicDetector, AdvancedDetectionResult
from .dynamic_dependency_tracker import DynamicDependencyTracker
from .enhanced_module_detector import EnhancedModuleDetector
from .precise_dependency_analyzer import PreciseDependencyAnalyzer
from .module_detector import ModuleDetector


@dataclass
class IntelligentAnalysisResult:
    """智能分析结果"""
    # 最终推荐的模块集合
    recommended_modules: Set[str] = field(default_factory=set)
    essential_modules: Set[str] = field(default_factory=set)      # 必需模块
    optional_modules: Set[str] = field(default_factory=set)       # 可选模块
    risky_modules: Set[str] = field(default_factory=set)          # 风险模块
    
    # 详细分类
    static_imports: Set[str] = field(default_factory=set)
    dynamic_imports: Set[str] = field(default_factory=set)
    conditional_imports: Set[str] = field(default_factory=set)
    lazy_imports: Set[str] = field(default_factory=set)
    plugin_modules: Set[str] = field(default_factory=set)
    
    # 分析元数据
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    detection_sources: Dict[str, List[str]] = field(default_factory=dict)  # 每个模块的检测来源
    analysis_methods: Dict[str, Any] = field(default_factory=dict)
    
    # 性能指标
    total_execution_time: float = 0.0
    cache_hit_rate: float = 0.0
    detection_accuracy: float = 0.0
    
    # PyInstaller 建议
    hidden_imports: List[str] = field(default_factory=list)
    collect_all: List[str] = field(default_factory=list)
    data_files: List[Tuple[str, str]] = field(default_factory=list)
    
    # 警告和建议
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class IntelligentModuleAnalyzer:
    """智能模块分析器"""
    
    def __init__(self, python_interpreter: str = "", timeout: int = 60):
        self.python_interpreter = python_interpreter or sys.executable
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # 初始化各种检测器
        self.detectors = {
            'advanced_dynamic': AdvancedDynamicDetector(python_interpreter, timeout//2),
            'dynamic_tracker': DynamicDependencyTracker(python_interpreter, timeout//3),
            'enhanced_detector': EnhancedModuleDetector(),
            'precise_analyzer': PreciseDependencyAnalyzer(python_interpreter),
            'basic_detector': ModuleDetector(use_ast=True, python_interpreter=python_interpreter)
        }
        
        # 检测器权重配置
        self.detector_weights = {
            'advanced_dynamic': 0.35,
            'dynamic_tracker': 0.25,
            'enhanced_detector': 0.20,
            'precise_analyzer': 0.15,
            'basic_detector': 0.05
        }
        
        # 模块分类规则
        self.classification_rules = self._build_classification_rules()
    
    def analyze_script(self, script_path: str, 
                      output_callback: Optional[Callable[[str], None]] = None,
                      use_execution: bool = True,
                      enable_ml_scoring: bool = False) -> IntelligentAnalysisResult:
        """执行智能模块分析"""
        start_time = time.time()
        
        if output_callback:
            output_callback("🧠 开始智能模块分析...")
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"脚本文件不存在: {script_path}")
        
        # 并行执行所有检测器
        detection_results = self._run_all_detectors(script_path, output_callback, use_execution)
        
        # 智能合并和评分
        merged_result = self._intelligent_merge(detection_results, output_callback)
        
        # 应用机器学习评分（如果启用）
        if enable_ml_scoring:
            merged_result = self._apply_ml_scoring(merged_result, script_path)
        
        # 生成PyInstaller建议
        self._generate_pyinstaller_suggestions(merged_result, script_path)
        
        # 生成警告和建议
        self._generate_warnings_and_recommendations(merged_result, detection_results)
        
        merged_result.total_execution_time = time.time() - start_time
        
        if output_callback:
            output_callback(f"🎯 智能分析完成，耗时 {merged_result.total_execution_time:.2f}s")
        
        return merged_result
    
    def _run_all_detectors(self, script_path: str, 
                          output_callback: Optional[Callable[[str], None]],
                          use_execution: bool) -> Dict[str, Any]:
        """并行运行所有检测器"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(self.detectors)) as executor:
            # 提交所有检测任务
            futures = {}
            
            for name, detector in self.detectors.items():
                if name == 'advanced_dynamic':
                    future = executor.submit(
                        detector.detect_modules, script_path, None, use_execution
                    )
                elif name == 'dynamic_tracker':
                    future = executor.submit(
                        detector.analyze_dynamic_dependencies, script_path, None, use_execution
                    )
                elif name == 'enhanced_detector':
                    future = executor.submit(
                        detector.detect_modules_with_cache, script_path
                    )
                elif name == 'precise_analyzer':
                    future = executor.submit(
                        detector.analyze_dependencies, script_path, None, False
                    )
                elif name == 'basic_detector':
                    future = executor.submit(
                        detector.detect_modules, script_path
                    )
                
                futures[name] = future
            
            # 收集结果
            for name, future in futures.items():
                try:
                    result = future.result(timeout=self.timeout)
                    results[name] = {
                        'success': True,
                        'result': result,
                        'error': None
                    }
                    if output_callback:
                        output_callback(f"  ✅ {name} 检测完成")
                except Exception as e:
                    results[name] = {
                        'success': False,
                        'result': None,
                        'error': str(e)
                    }
                    if output_callback:
                        output_callback(f"  ❌ {name} 检测失败: {e}")
                    self.logger.warning(f"Detector {name} failed: {e}")
        
        return results
    
    def _intelligent_merge(self, detection_results: Dict[str, Any],
                          output_callback: Optional[Callable[[str], None]]) -> IntelligentAnalysisResult:
        """智能合并检测结果"""
        if output_callback:
            output_callback("🔄 智能合并检测结果...")
        
        result = IntelligentAnalysisResult()
        module_votes = {}  # 模块投票系统
        module_sources = {}  # 模块来源追踪
        
        # 处理每个检测器的结果
        for detector_name, detection_data in detection_results.items():
            if not detection_data['success']:
                continue
            
            weight = self.detector_weights.get(detector_name, 0.1)
            detector_result = detection_data['result']
            
            # 提取模块并投票
            modules = self._extract_modules_from_result(detector_result, detector_name)
            
            for module in modules:
                if module not in module_votes:
                    module_votes[module] = 0.0
                    module_sources[module] = []
                
                module_votes[module] += weight
                module_sources[module].append(detector_name)
        
        # 基于投票结果分类模块
        vote_threshold_essential = 0.6  # 必需模块阈值
        vote_threshold_recommended = 0.3  # 推荐模块阈值
        vote_threshold_optional = 0.1   # 可选模块阈值
        
        for module, vote_score in module_votes.items():
            # 标准化投票分数
            normalized_score = min(vote_score, 1.0)
            result.confidence_scores[module] = normalized_score
            result.detection_sources[module] = module_sources[module]
            
            # 分类模块
            if normalized_score >= vote_threshold_essential:
                result.essential_modules.add(module)
                result.recommended_modules.add(module)
            elif normalized_score >= vote_threshold_recommended:
                result.recommended_modules.add(module)
            elif normalized_score >= vote_threshold_optional:
                result.optional_modules.add(module)
            else:
                result.risky_modules.add(module)
        
        # 应用分类规则
        self._apply_classification_rules(result)
        
        # 计算缓存命中率
        cache_hits = sum(1 for data in detection_results.values() 
                        if data['success'] and hasattr(data['result'], 'cache_hit') 
                        and data['result'].cache_hit)
        result.cache_hit_rate = cache_hits / len(detection_results) if detection_results else 0.0
        
        return result
    
    def _extract_modules_from_result(self, result: Any, detector_name: str) -> Set[str]:
        """从检测结果中提取模块"""
        modules = set()
        
        try:
            if detector_name == 'advanced_dynamic':
                if isinstance(result, AdvancedDetectionResult):
                    modules.update(result.static_imports)
                    modules.update(result.dynamic_imports)
                    modules.update(result.conditional_imports)
                    modules.update(result.lazy_imports)
                    modules.update(result.optional_imports)
                    modules.update(result.string_references)
                    modules.update(result.plugin_modules)
                    modules.update(result.config_driven)
                    modules.update(result.runtime_discovered)
            
            elif detector_name == 'dynamic_tracker':
                if hasattr(result, 'runtime_modules'):
                    modules.update(result.runtime_modules)
                    modules.update(result.conditional_modules)
                    modules.update(result.lazy_imports)
                    modules.update(result.optional_modules)
            
            elif detector_name == 'enhanced_detector':
                if hasattr(result, 'detected_modules'):
                    modules.update(result.detected_modules)
            
            elif detector_name == 'precise_analyzer':
                if hasattr(result, 'third_party_modules'):
                    modules.update(result.third_party_modules)
                    modules.update(result.local_modules)
            
            elif detector_name == 'basic_detector':
                if isinstance(result, set):
                    modules.update(result)
        
        except Exception as e:
            self.logger.warning(f"Failed to extract modules from {detector_name}: {e}")
        
        return modules
    
    def _build_classification_rules(self) -> Dict[str, Any]:
        """构建模块分类规则"""
        return {
            'essential_patterns': [
                # 基础运行时模块
                r'^(os|sys|json|time|datetime|re|math|random)$',
                # 常用标准库
                r'^(collections|itertools|functools|operator|copy)$',
                # 文件和网络
                r'^(pathlib|urllib|http|socket)$',
            ],
            'optional_patterns': [
                # 开发和测试工具
                r'^(pytest|unittest|mock|coverage)$',
                # 可选的GUI库
                r'^(tkinter|wx|kivy)$',
                # 可选的数据处理库
                r'^(pandas|numpy|matplotlib|scipy)$',
            ],
            'risky_patterns': [
                # 系统级模块
                r'^(ctypes|subprocess|multiprocessing)$',
                # 网络相关
                r'^(ssl|hashlib|hmac)$',
            ]
        }
    
    def _apply_classification_rules(self, result: IntelligentAnalysisResult):
        """应用分类规则"""
        import re
        
        rules = self.classification_rules
        
        # 检查每个模块
        all_modules = (result.recommended_modules | result.optional_modules | result.risky_modules)
        
        for module in all_modules:
            # 检查是否匹配必需模式
            for pattern in rules['essential_patterns']:
                if re.match(pattern, module):
                    if module in result.optional_modules:
                        result.optional_modules.remove(module)
                    if module in result.risky_modules:
                        result.risky_modules.remove(module)
                    result.essential_modules.add(module)
                    result.recommended_modules.add(module)
                    break
            
            # 检查是否匹配可选模式
            for pattern in rules['optional_patterns']:
                if re.match(pattern, module) and module not in result.essential_modules:
                    if module in result.risky_modules:
                        result.risky_modules.remove(module)
                    result.optional_modules.add(module)
                    break
            
            # 检查是否匹配风险模式
            for pattern in rules['risky_patterns']:
                if re.match(pattern, module) and module not in result.essential_modules:
                    result.risky_modules.add(module)
                    break

    def _apply_ml_scoring(self, result: IntelligentAnalysisResult,
                         script_path: str) -> IntelligentAnalysisResult:
        """应用机器学习评分（简化版）"""
        # 这里可以集成更复杂的ML模型
        # 目前使用基于规则的启发式评分

        script_features = self._extract_script_features(script_path)

        # 基于脚本特征调整置信度分数
        for module in result.confidence_scores:
            base_score = result.confidence_scores[module]

            # 特征加权
            feature_bonus = 0.0

            # 如果脚本使用了GUI框架
            if script_features.get('has_gui', False):
                if module in ['tkinter', 'pyqt5', 'pyqt6', 'wx', 'kivy']:
                    feature_bonus += 0.2

            # 如果脚本处理数据
            if script_features.get('processes_data', False):
                if module in ['pandas', 'numpy', 'csv', 'json', 'sqlite3']:
                    feature_bonus += 0.15

            # 如果脚本有网络功能
            if script_features.get('has_network', False):
                if module in ['requests', 'urllib', 'http', 'socket']:
                    feature_bonus += 0.15

            # 如果脚本有文件操作
            if script_features.get('file_operations', False):
                if module in ['os', 'pathlib', 'shutil', 'glob']:
                    feature_bonus += 0.1

            # 更新分数
            result.confidence_scores[module] = min(base_score + feature_bonus, 1.0)

        return result

    def _extract_script_features(self, script_path: str) -> Dict[str, bool]:
        """提取脚本特征"""
        features = {
            'has_gui': False,
            'processes_data': False,
            'has_network': False,
            'file_operations': False,
            'uses_threading': False,
            'has_database': False
        }

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            # GUI框架检测
            gui_keywords = ['tkinter', 'pyqt', 'wx', 'kivy', 'gui', 'window', 'dialog']
            features['has_gui'] = any(keyword in content for keyword in gui_keywords)

            # 数据处理检测
            data_keywords = ['pandas', 'numpy', 'dataframe', 'csv', 'excel', 'json']
            features['processes_data'] = any(keyword in content for keyword in data_keywords)

            # 网络功能检测
            network_keywords = ['requests', 'urllib', 'http', 'socket', 'api', 'url']
            features['has_network'] = any(keyword in content for keyword in network_keywords)

            # 文件操作检测
            file_keywords = ['open(', 'file', 'path', 'directory', 'folder', 'read', 'write']
            features['file_operations'] = any(keyword in content for keyword in file_keywords)

            # 多线程检测
            thread_keywords = ['threading', 'thread', 'multiprocessing', 'concurrent']
            features['uses_threading'] = any(keyword in content for keyword in thread_keywords)

            # 数据库检测
            db_keywords = ['sqlite', 'mysql', 'postgresql', 'database', 'db', 'sql']
            features['has_database'] = any(keyword in content for keyword in db_keywords)

        except Exception:
            pass

        return features

    def _generate_pyinstaller_suggestions(self, result: IntelligentAnalysisResult,
                                        script_path: str):
        """生成PyInstaller建议"""
        # 隐藏导入建议
        for module in result.essential_modules:
            if module not in ['os', 'sys', 'json']:  # 排除标准库
                result.hidden_imports.append(module)

        # collect-all 建议（对于复杂的包）
        complex_packages = {'numpy', 'pandas', 'matplotlib', 'scipy', 'tensorflow', 'torch'}
        for module in result.recommended_modules:
            if module in complex_packages:
                result.collect_all.append(module)

        # 数据文件建议
        script_dir = os.path.dirname(script_path)
        common_data_extensions = ['.json', '.yaml', '.yml', '.txt', '.csv', '.xml']

        try:
            for file in os.listdir(script_dir):
                if any(file.endswith(ext) for ext in common_data_extensions):
                    src_path = os.path.join(script_dir, file)
                    result.data_files.append((src_path, '.'))
        except:
            pass

    def _generate_warnings_and_recommendations(self, result: IntelligentAnalysisResult,
                                             detection_results: Dict[str, Any]):
        """生成警告和建议"""
        # 检查风险模块
        if result.risky_modules:
            result.warnings.append(
                f"发现 {len(result.risky_modules)} 个风险模块，可能影响打包稳定性: "
                f"{', '.join(sorted(result.risky_modules))}"
            )

        # 检查检测器失败
        failed_detectors = [name for name, data in detection_results.items()
                           if not data['success']]
        if failed_detectors:
            result.warnings.append(
                f"以下检测器执行失败: {', '.join(failed_detectors)}"
            )

        # 生成建议
        if len(result.recommended_modules) > 50:
            result.recommendations.append(
                "检测到大量模块，建议检查是否有不必要的依赖"
            )

        if result.cache_hit_rate < 0.5:
            result.recommendations.append(
                "缓存命中率较低，建议清理缓存或检查文件变更"
            )

        if len(result.essential_modules) < 5:
            result.recommendations.append(
                "检测到的必需模块较少，可能存在遗漏，建议启用执行时分析"
            )

        # 性能建议
        if result.total_execution_time > 30:
            result.recommendations.append(
                "分析耗时较长，建议优化脚本或减少检测范围"
            )

    def get_pyinstaller_command_args(self, result: IntelligentAnalysisResult) -> List[str]:
        """生成PyInstaller命令参数"""
        args = []

        # 隐藏导入
        for module in result.hidden_imports:
            args.extend(['--hidden-import', module])

        # collect-all
        for module in result.collect_all:
            args.extend(['--collect-all', module])

        # 数据文件
        for src, dst in result.data_files:
            args.extend(['--add-data', f"{src}{os.pathsep}{dst}"])

        return args

    def generate_analysis_report(self, result: IntelligentAnalysisResult,
                               script_path: str) -> str:
        """生成分析报告"""
        report = []
        report.append("=" * 60)
        report.append("🧠 智能模块分析报告")
        report.append("=" * 60)
        report.append(f"📄 分析脚本: {script_path}")
        report.append(f"⏱️  分析耗时: {result.total_execution_time:.2f}s")
        report.append(f"💾 缓存命中率: {result.cache_hit_rate:.1%}")
        report.append("")

        # 模块统计
        report.append("📊 模块统计:")
        report.append(f"  必需模块: {len(result.essential_modules)}")
        report.append(f"  推荐模块: {len(result.recommended_modules)}")
        report.append(f"  可选模块: {len(result.optional_modules)}")
        report.append(f"  风险模块: {len(result.risky_modules)}")
        report.append("")

        # 详细模块列表
        if result.essential_modules:
            report.append("🔹 必需模块:")
            report.append(f"  {', '.join(sorted(result.essential_modules))}")
            report.append("")

        if result.recommended_modules:
            report.append("🔹 推荐模块:")
            report.append(f"  {', '.join(sorted(result.recommended_modules))}")
            report.append("")

        if result.risky_modules:
            report.append("⚠️  风险模块:")
            report.append(f"  {', '.join(sorted(result.risky_modules))}")
            report.append("")

        # PyInstaller建议
        if result.hidden_imports or result.collect_all:
            report.append("🔧 PyInstaller 建议:")
            if result.hidden_imports:
                report.append(f"  隐藏导入: {', '.join(result.hidden_imports)}")
            if result.collect_all:
                report.append(f"  完整收集: {', '.join(result.collect_all)}")
            report.append("")

        # 警告和建议
        if result.warnings:
            report.append("⚠️  警告:")
            for warning in result.warnings:
                report.append(f"  • {warning}")
            report.append("")

        if result.recommendations:
            report.append("💡 建议:")
            for recommendation in result.recommendations:
                report.append(f"  • {recommendation}")
            report.append("")

        report.append("=" * 60)

        return "\n".join(report)
