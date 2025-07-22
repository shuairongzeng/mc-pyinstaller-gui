#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能缓存系统使用示例
展示如何在实际项目中使用优化的模块检测和依赖分析功能
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.smart_cache_manager import SmartCacheManager, get_cache_manager, set_cache_manager
from services.optimized_module_detector import OptimizedModuleDetector
from services.optimized_dependency_analyzer import OptimizedDependencyAnalyzer


def setup_cache_system():
    """设置缓存系统"""
    print("🚀 初始化智能缓存系统...")
    
    # 创建自定义缓存管理器
    cache_manager = SmartCacheManager(
        cache_dir="cache",
        memory_max_size=500,      # 内存最多缓存500个项目
        memory_max_mb=200,        # 内存最多使用200MB
        disk_max_mb=1000,         # 磁盘最多使用1GB
        default_ttl=7200,         # 默认缓存2小时
        enable_compression=False   # 暂不启用压缩
    )
    
    # 设置为全局缓存管理器
    set_cache_manager(cache_manager)
    
    print("✅ 缓存系统初始化完成")
    return cache_manager


def demonstrate_module_detection():
    """演示模块检测功能"""
    print("\n" + "="*60)
    print("📦 模块检测功能演示")
    print("="*60)
    
    # 创建优化的模块检测器
    detector = OptimizedModuleDetector(
        use_ast=True,
        use_dynamic_analysis=True,
        use_framework_detection=True,
        max_workers=4,
        cache_ttl=7200,
        enable_parallel=True
    )
    
    # 检测当前脚本的模块依赖
    current_script = __file__
    print(f"分析脚本: {current_script}")
    
    # 第一次检测（无缓存）
    print("\n🔍 首次检测（无缓存）...")
    start_time = time.time()
    result1 = detector.detect_modules(current_script, force_refresh=True)
    first_time = time.time() - start_time
    
    print(f"⏱️  检测耗时: {first_time:.3f}秒")
    print(f"📋 检测到模块: {len(result1.detected_modules)} 个")
    print(f"🔧 隐藏导入: {len(result1.hidden_imports)} 个")
    print(f"📁 数据文件: {len(result1.data_files)} 个")
    print(f"💡 建议: {len(result1.recommendations)} 条")
    
    # 显示检测到的模块
    if result1.detected_modules:
        print(f"\n检测到的模块:")
        for i, module in enumerate(sorted(result1.detected_modules), 1):
            print(f"  {i:2d}. {module}")
            if i >= 10:  # 只显示前10个
                print(f"     ... 还有 {len(result1.detected_modules) - 10} 个模块")
                break
    
    # 第二次检测（有缓存）
    print(f"\n🚀 第二次检测（有缓存）...")
    start_time = time.time()
    result2 = detector.detect_modules(current_script)
    second_time = time.time() - start_time
    
    print(f"⏱️  检测耗时: {second_time:.3f}秒")
    speedup = first_time/second_time if second_time > 0.001 else float('inf')
    if speedup == float('inf'):
        print(f"📈 性能提升: 极大提升 (缓存几乎瞬间完成)")
    else:
        print(f"📈 性能提升: {speedup:.1f}x")
    print(f"💾 缓存命中: {'是' if result2.cache_hit else '否'}")
    
    # 显示建议
    if result1.recommendations:
        print(f"\n💡 优化建议:")
        for i, recommendation in enumerate(result1.recommendations, 1):
            print(f"  {i}. {recommendation}")
    
    return detector


def demonstrate_dependency_analysis():
    """演示依赖分析功能"""
    print("\n" + "="*60)
    print("🔗 依赖分析功能演示")
    print("="*60)
    
    # 创建优化的依赖分析器
    analyzer = OptimizedDependencyAnalyzer(
        cache_ttl=3600,
        enable_deep_analysis=True
    )
    
    # 分析一组常见模块的依赖关系
    test_modules = {
        "os", "sys", "json", "time", "datetime", "pathlib",
        "collections", "itertools", "functools", "logging"
    }
    
    print(f"分析模块集合: {', '.join(sorted(test_modules))}")
    
    # 第一次分析（无缓存）
    print(f"\n🔍 首次分析（无缓存）...")
    start_time = time.time()
    result1 = analyzer.analyze_dependencies(test_modules, force_refresh=True)
    first_time = time.time() - start_time
    
    print(f"⏱️  分析耗时: {first_time:.3f}秒")
    print(f"📦 依赖模块: {len(result1.dependencies)} 个")
    print(f"⚠️  冲突检测: {len(result1.conflicts)} 个")
    print(f"❌ 缺失模块: {len(result1.missing)} 个")
    print(f"🔄 版本问题: {len(result1.version_issues)} 个")
    print(f"💾 总大小: {result1.total_size / (1024*1024):.2f} MB")
    
    # 第二次分析（有缓存）
    print(f"\n🚀 第二次分析（有缓存）...")
    start_time = time.time()
    result2 = analyzer.analyze_dependencies(test_modules)
    second_time = time.time() - start_time
    
    print(f"⏱️  分析耗时: {second_time:.3f}秒")
    speedup = first_time/second_time if second_time > 0.001 else float('inf')
    if speedup == float('inf'):
        print(f"📈 性能提升: 极大提升 (缓存几乎瞬间完成)")
    else:
        print(f"📈 性能提升: {speedup:.1f}x")
    print(f"💾 缓存命中: {'是' if result2.cache_hit else '否'}")
    
    # 显示依赖详情
    print(f"\n📋 依赖详情:")
    available_deps = {name: info for name, info in result1.dependencies.items() if info.is_available}
    for name, info in list(available_deps.items())[:5]:  # 只显示前5个
        print(f"  📦 {name}")
        print(f"     版本: {info.version}")
        print(f"     位置: {info.location[:60]}..." if len(info.location) > 60 else f"     位置: {info.location}")
        print(f"     大小: {info.size / 1024:.1f} KB")
    
    if len(available_deps) > 5:
        print(f"     ... 还有 {len(available_deps) - 5} 个依赖")
    
    # 显示建议
    if result1.recommendations:
        print(f"\n💡 优化建议:")
        for i, recommendation in enumerate(result1.recommendations, 1):
            print(f"  {i}. {recommendation}")
    
    return analyzer


def demonstrate_cache_management():
    """演示缓存管理功能"""
    print("\n" + "="*60)
    print("💾 缓存管理功能演示")
    print("="*60)
    
    cache_manager = get_cache_manager()
    
    # 显示缓存统计
    stats = cache_manager.get_stats()
    print("📊 缓存统计信息:")
    print(f"  命中率: {stats.get('hit_rate', 'N/A')}")
    print(f"  总命中: {stats.get('hits', 0)}")
    print(f"  总未命中: {stats.get('misses', 0)}")
    print(f"  内存项目: {stats.get('memory', {}).get('items', 0)}")
    print(f"  磁盘项目: {stats.get('disk', {}).get('items', 0)}")
    print(f"  总大小: {stats.get('total_size_mb', 0):.2f} MB")
    
    # 缓存效率评估
    efficiency = stats.get('cache_efficiency', {})
    if efficiency:
        print(f"\n🎯 缓存效率评估:")
        print(f"  效率评分: {efficiency.get('efficiency_score', 0):.1f}%")
        print(f"  建议: {efficiency.get('recommendation', 'N/A')}")
    
    # 执行缓存优化
    print(f"\n🔧 执行缓存优化...")
    optimization_result = cache_manager.optimize()
    
    print("优化结果:")
    for action in optimization_result.get('actions_taken', []):
        print(f"  ✅ {action}")
    
    if optimization_result.get('space_freed_mb', 0) > 0:
        print(f"  💾 释放空间: {optimization_result['space_freed_mb']:.2f} MB")
        print(f"  🗑️  清理项目: {optimization_result['items_removed']} 个")


def demonstrate_integration_example():
    """演示集成使用示例"""
    print("\n" + "="*60)
    print("🔗 集成使用示例")
    print("="*60)
    
    # 模拟一个完整的打包分析流程
    script_path = __file__
    print(f"分析脚本: {Path(script_path).name}")
    
    # 1. 模块检测
    print(f"\n1️⃣ 执行模块检测...")
    detector = OptimizedModuleDetector()
    detection_result = detector.detect_modules(script_path)
    
    print(f"   检测到 {len(detection_result.detected_modules)} 个模块")
    print(f"   缓存命中: {'是' if detection_result.cache_hit else '否'}")
    
    # 2. 依赖分析
    print(f"\n2️⃣ 执行依赖分析...")
    analyzer = OptimizedDependencyAnalyzer()
    analysis_result = analyzer.analyze_dependencies(detection_result.detected_modules)
    
    print(f"   分析了 {len(analysis_result.dependencies)} 个依赖")
    print(f"   发现 {len(analysis_result.conflicts)} 个冲突")
    print(f"   缓存命中: {'是' if analysis_result.cache_hit else '否'}")
    
    # 3. 生成PyInstaller参数建议
    print(f"\n3️⃣ 生成打包建议...")
    
    # 合并所有建议
    all_recommendations = []
    all_recommendations.extend(detection_result.recommendations)
    all_recommendations.extend(analysis_result.recommendations)
    
    if detection_result.hidden_imports:
        hidden_imports_str = " ".join(f"--hidden-import {imp}" for imp in detection_result.hidden_imports[:5])
        print(f"   隐藏导入参数: {hidden_imports_str}")
    
    if detection_result.collect_all:
        collect_all_str = " ".join(f"--collect-all {mod}" for mod in detection_result.collect_all[:3])
        print(f"   收集全部参数: {collect_all_str}")
    
    if all_recommendations:
        print(f"   优化建议:")
        for i, rec in enumerate(all_recommendations[:3], 1):
            print(f"     {i}. {rec}")
    
    # 4. 显示性能统计
    print(f"\n4️⃣ 性能统计...")
    detector_stats = detector.get_stats()
    analyzer_stats = analyzer.get_stats()
    
    print(f"   模块检测缓存命中率: {detector_stats.get('cache_hit_rate', 'N/A')}")
    print(f"   依赖分析缓存命中率: {analyzer_stats.get('cache_hit_rate', 'N/A')}")
    print(f"   平均检测时间: {detector_stats.get('avg_detection_time', 'N/A')}")
    print(f"   平均分析时间: {analyzer_stats.get('avg_analysis_time', 'N/A')}")


def main():
    """主函数"""
    print("🎯 智能缓存系统使用示例")
    print("=" * 60)
    
    try:
        # 1. 设置缓存系统
        cache_manager = setup_cache_system()
        
        # 2. 演示模块检测
        detector = demonstrate_module_detection()
        
        # 3. 演示依赖分析
        analyzer = demonstrate_dependency_analysis()
        
        # 4. 演示缓存管理
        demonstrate_cache_management()
        
        # 5. 演示集成使用
        demonstrate_integration_example()
        
        print("\n" + "="*60)
        print("🎉 演示完成！智能缓存系统运行正常。")
        print("="*60)
        
        # 最终统计
        final_stats = cache_manager.get_stats()
        print(f"\n📊 最终缓存统计:")
        print(f"   总命中率: {final_stats.get('hit_rate', 'N/A')}")
        print(f"   缓存效率: {final_stats.get('cache_efficiency', {}).get('efficiency_score', 0):.1f}%")
        print(f"   总缓存大小: {final_stats.get('total_size_mb', 0):.2f} MB")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
