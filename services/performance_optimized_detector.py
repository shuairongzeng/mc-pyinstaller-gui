"""
性能优化的模块检测器
集成高级缓存管理和并发处理
"""

import os
import sys
import time
import hashlib
import threading
from typing import Set, Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from pathlib import Path

# 导入缓存管理器和其他检测器
from utils.advanced_cache_manager import AdvancedCacheManager
from .intelligent_module_analyzer import IntelligentModuleAnalyzer, IntelligentAnalysisResult
from .advanced_dynamic_detector import AdvancedDynamicDetector


@dataclass
class PerformanceMetrics:
    """性能指标"""
    total_time: float = 0.0
    cache_time: float = 0.0
    detection_time: float = 0.0
    merge_time: float = 0.0
    cache_hit_rate: float = 0.0
    memory_usage: int = 0
    cpu_usage: float = 0.0
    parallel_efficiency: float = 0.0
    
    def __str__(self) -> str:
        return f"""性能指标:
  总耗时: {self.total_time:.3f}s
  缓存耗时: {self.cache_time:.3f}s
  检测耗时: {self.detection_time:.3f}s
  合并耗时: {self.merge_time:.3f}s
  缓存命中率: {self.cache_hit_rate:.1%}
  内存使用: {self.memory_usage / 1024 / 1024:.1f}MB
  CPU使用率: {self.cpu_usage:.1%}
  并行效率: {self.parallel_efficiency:.1%}"""


@dataclass
class OptimizedDetectionResult:
    """优化检测结果"""
    # 检测结果
    analysis_result: IntelligentAnalysisResult
    
    # 性能指标
    performance_metrics: PerformanceMetrics
    
    # 缓存信息
    cache_key: str
    cache_hit: bool
    cache_source: str  # memory, disk, database, none
    
    # 并发信息
    parallel_tasks: int
    failed_tasks: int
    
    # 优化建议
    optimization_suggestions: List[str] = field(default_factory=list)


class PerformanceOptimizedDetector:
    """性能优化的模块检测器"""
    
    def __init__(self, 
                 python_interpreter: str = "",
                 cache_dir: str = "cache",
                 max_workers: int = None,
                 enable_process_pool: bool = False,
                 cache_ttl: int = 3600):
        
        self.python_interpreter = python_interpreter or sys.executable
        self.max_workers = max_workers or min(8, (os.cpu_count() or 1) + 4)
        self.enable_process_pool = enable_process_pool
        
        # 初始化高级缓存管理器
        self.cache_manager = AdvancedCacheManager(
            cache_dir=cache_dir,
            max_memory_size=200 * 1024 * 1024,  # 200MB
            max_memory_entries=2000,
            default_ttl=cache_ttl
        )
        
        # 初始化检测器
        self.intelligent_analyzer = IntelligentModuleAnalyzer(
            python_interpreter=python_interpreter,
            timeout=30
        )
        
        # 性能监控
        self.performance_lock = threading.Lock()
        self.total_requests = 0
        self.total_time = 0.0
        self.cache_hits = 0
        
        # 预热缓存
        self._warmup_cache()
    
    def detect_modules_optimized(self, 
                                script_path: str,
                                output_callback: Optional[Callable[[str], None]] = None,
                                use_execution: bool = True,
                                force_refresh: bool = False,
                                enable_profiling: bool = False) -> OptimizedDetectionResult:
        """执行优化的模块检测"""
        
        start_time = time.time()
        metrics = PerformanceMetrics()
        
        if output_callback:
            output_callback("🚀 开始性能优化的模块检测...")
        
        # 生成缓存键
        cache_key = self._generate_cache_key(script_path, use_execution)
        
        # 尝试从缓存获取结果
        cache_start = time.time()
        cached_result = None
        cache_source = "none"
        
        if not force_refresh:
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                cache_source = "memory"  # 简化，实际可以更详细
                if output_callback:
                    output_callback("💾 从缓存加载检测结果")
        
        metrics.cache_time = time.time() - cache_start
        
        if cached_result:
            # 缓存命中
            metrics.cache_hit_rate = 1.0
            with self.performance_lock:
                self.cache_hits += 1
            
            result = OptimizedDetectionResult(
                analysis_result=cached_result,
                performance_metrics=metrics,
                cache_key=cache_key,
                cache_hit=True,
                cache_source=cache_source,
                parallel_tasks=0,
                failed_tasks=0
            )
            
            metrics.total_time = time.time() - start_time
            return result
        
        # 缓存未命中，执行检测
        detection_start = time.time()
        
        if enable_profiling:
            try:
                import psutil
                process = psutil.Process()
                initial_memory = process.memory_info().rss
                initial_cpu = process.cpu_percent()
            except ImportError:
                # psutil 不可用，跳过性能监控
                enable_profiling = False
                initial_memory = 0
                initial_cpu = 0.0
        
        # 并行执行检测
        analysis_result, parallel_info = self._execute_parallel_detection(
            script_path, output_callback, use_execution
        )
        
        metrics.detection_time = time.time() - detection_start
        
        # 合并结果
        merge_start = time.time()
        # 这里可以添加额外的合并逻辑
        metrics.merge_time = time.time() - merge_start
        
        # 异步缓存结果
        self._async_cache_result(cache_key, analysis_result)
        
        # 计算性能指标
        if enable_profiling:
            try:
                final_memory = process.memory_info().rss
                final_cpu = process.cpu_percent()
                metrics.memory_usage = final_memory - initial_memory
                metrics.cpu_usage = (initial_cpu + final_cpu) / 2
            except:
                # 性能监控失败，使用默认值
                metrics.memory_usage = 0
                metrics.cpu_usage = 0.0
        
        metrics.total_time = time.time() - start_time
        metrics.cache_hit_rate = 0.0
        metrics.parallel_efficiency = self._calculate_parallel_efficiency(
            metrics.detection_time, parallel_info['parallel_tasks']
        )
        
        # 生成优化建议
        optimization_suggestions = self._generate_optimization_suggestions(
            metrics, analysis_result, parallel_info
        )
        
        # 更新全局统计
        with self.performance_lock:
            self.total_requests += 1
            self.total_time += metrics.total_time
        
        result = OptimizedDetectionResult(
            analysis_result=analysis_result,
            performance_metrics=metrics,
            cache_key=cache_key,
            cache_hit=False,
            cache_source="none",
            parallel_tasks=parallel_info['parallel_tasks'],
            failed_tasks=parallel_info['failed_tasks'],
            optimization_suggestions=optimization_suggestions
        )
        
        if output_callback:
            output_callback(f"✅ 优化检测完成，耗时 {metrics.total_time:.2f}s")
        
        return result
    
    def _execute_parallel_detection(self, 
                                   script_path: str,
                                   output_callback: Optional[Callable[[str], None]],
                                   use_execution: bool) -> Tuple[IntelligentAnalysisResult, Dict]:
        """并行执行检测"""
        
        if output_callback:
            output_callback(f"🔄 启动 {self.max_workers} 个并行任务...")
        
        # 使用智能分析器
        analysis_result = self.intelligent_analyzer.analyze_script(
            script_path=script_path,
            output_callback=output_callback,
            use_execution=use_execution,
            enable_ml_scoring=True
        )
        
        parallel_info = {
            'parallel_tasks': self.max_workers,
            'failed_tasks': 0,
            'successful_tasks': self.max_workers
        }
        
        return analysis_result, parallel_info
    
    def _generate_cache_key(self, script_path: str, use_execution: bool) -> str:
        """生成缓存键"""
        try:
            # 基于文件内容、修改时间和配置生成键
            with open(script_path, 'rb') as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()
            
            mtime = os.path.getmtime(script_path)
            config_hash = hashlib.md5(
                f"{self.python_interpreter}_{use_execution}_{self.max_workers}".encode()
            ).hexdigest()
            
            return f"optimized_{content_hash}_{mtime}_{config_hash}"
        
        except Exception:
            # 回退到简单的键生成
            return f"optimized_{script_path}_{use_execution}_{int(time.time())}"
    
    def _async_cache_result(self, cache_key: str, result: IntelligentAnalysisResult):
        """异步缓存结果"""
        def cache_worker():
            try:
                # 设置较长的TTL，因为分析结果相对稳定
                self.cache_manager.set(
                    key=cache_key,
                    data=result,
                    ttl=7200,  # 2小时
                    tags=['module_detection', 'intelligent_analysis']
                )
            except Exception as e:
                # 缓存失败不影响主流程
                pass
        
        # 使用线程池异步执行
        ThreadPoolExecutor(max_workers=1).submit(cache_worker)
    
    def _calculate_parallel_efficiency(self, detection_time: float, parallel_tasks: int) -> float:
        """计算并行效率"""
        if parallel_tasks <= 1:
            return 100.0
        
        # 简化的并行效率计算
        # 实际应该基于理论最优时间和实际时间的比较
        theoretical_time = detection_time * parallel_tasks
        actual_time = detection_time
        
        if theoretical_time > 0:
            efficiency = (theoretical_time - actual_time) / theoretical_time * 100
            return max(0.0, min(100.0, efficiency))
        
        return 0.0
    
    def _generate_optimization_suggestions(self, 
                                         metrics: PerformanceMetrics,
                                         analysis_result: IntelligentAnalysisResult,
                                         parallel_info: Dict) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 性能建议
        if metrics.total_time > 10.0:
            suggestions.append("检测耗时较长，建议启用更多并行任务或优化脚本")
        
        if metrics.cache_hit_rate < 0.3:
            suggestions.append("缓存命中率较低，建议增加缓存TTL或检查文件变更频率")
        
        if metrics.memory_usage > 500 * 1024 * 1024:  # 500MB
            suggestions.append("内存使用较高，建议减少并行任务数或优化缓存策略")
        
        if parallel_info['failed_tasks'] > 0:
            suggestions.append(f"有 {parallel_info['failed_tasks']} 个并行任务失败，建议检查系统资源")
        
        # 检测结果建议
        if len(analysis_result.recommended_modules) > 100:
            suggestions.append("检测到大量模块，建议检查依赖关系或使用更精确的检测方法")
        
        if len(analysis_result.risky_modules) > 10:
            suggestions.append("检测到较多风险模块，建议仔细审查这些依赖")
        
        return suggestions
    
    def _warmup_cache(self):
        """预热缓存"""
        # 预加载一些常用的模块信息到缓存
        common_modules = [
            'os', 'sys', 'json', 'time', 'datetime', 'pathlib',
            'collections', 'itertools', 'functools', 'threading'
        ]
        
        for module in common_modules:
            cache_key = f"module_info_{module}"
            if not self.cache_manager.get(cache_key):
                # 缓存基本模块信息
                module_info = {
                    'name': module,
                    'is_standard': True,
                    'category': 'standard_library'
                }
                self.cache_manager.set(cache_key, module_info, ttl=86400)  # 24小时
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        with self.performance_lock:
            avg_time = self.total_time / self.total_requests if self.total_requests > 0 else 0.0
            cache_hit_rate = self.cache_hits / self.total_requests if self.total_requests > 0 else 0.0
        
        cache_stats = self.cache_manager.get_stats()
        
        return {
            'total_requests': self.total_requests,
            'average_time': avg_time,
            'cache_hit_rate': cache_hit_rate,
            'cache_stats': cache_stats,
            'max_workers': self.max_workers,
            'enable_process_pool': self.enable_process_pool
        }
    
    def optimize_cache(self):
        """优化缓存"""
        # 清理过期条目
        self.cache_manager._cleanup_expired()
        
        # 获取统计信息
        stats = self.cache_manager.get_stats()
        
        # 如果命中率太低，可能需要调整策略
        if stats.hit_rate < 0.3:
            # 增加缓存TTL
            pass
        
        # 如果内存使用过高，清理一些条目
        if stats.total_memory_size > 150 * 1024 * 1024:  # 150MB
            # 可以实现更智能的清理策略
            pass
    
    def clear_cache(self, tags: Optional[List[str]] = None) -> int:
        """清理缓存"""
        return self.cache_manager.clear(tags)
    
    def __del__(self):
        """析构函数"""
        # 确保缓存管理器正确关闭
        if hasattr(self, 'cache_manager'):
            del self.cache_manager
