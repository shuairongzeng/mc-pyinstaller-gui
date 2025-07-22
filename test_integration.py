#!/usr/bin/env python3
"""
集成测试脚本 - 测试精准依赖检测系统的集成
"""

import sys
import os
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入"""
    print("🔍 测试模块导入...")
    
    try:
        from services.precise_dependency_analyzer import PreciseDependencyAnalyzer
        print("  ✅ 精准依赖分析器导入成功")
    except ImportError as e:
        print(f"  ❌ 精准依赖分析器导入失败: {e}")
        return False
    
    try:
        from services.dynamic_dependency_tracker import DynamicDependencyTracker
        print("  ✅ 动态依赖追踪器导入成功")
    except ImportError as e:
        print(f"  ❌ 动态依赖追踪器导入失败: {e}")
        return False
    
    try:
        from views.tabs.enhanced_module_tab import EnhancedModuleTab
        print("  ✅ 增强模块标签页导入成功")
    except ImportError as e:
        print(f"  ❌ 增强模块标签页导入失败: {e}")
        return False
    
    return True

def test_functionality():
    """测试功能"""
    print("\n⚙️  测试基本功能...")
    
    # 创建测试脚本
    test_script_content = '''
import os
import sys
import json
try:
    import PyQt5
except ImportError:
    pass
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_script_content)
        test_script = f.name
    
    try:
        # 测试精准分析器
        from services.precise_dependency_analyzer import PreciseDependencyAnalyzer
        analyzer = PreciseDependencyAnalyzer()
        
        result = analyzer.analyze_dependencies(test_script)
        print(f"  ✅ 精准分析完成: 发现 {len(result.standard_modules | result.third_party_modules | result.local_modules)} 个模块")
        
        # 测试动态追踪器
        from services.dynamic_dependency_tracker import DynamicDependencyTracker
        tracker = DynamicDependencyTracker()
        
        dynamic_result = tracker.analyze_dynamic_dependencies(test_script, use_execution=False)
        print(f"  ✅ 动态分析完成: 发现 {len(dynamic_result.runtime_modules)} 个运行时模块")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            os.unlink(test_script)
        except:
            pass

def test_gui_components():
    """测试GUI组件"""
    print("\n🖥️  测试GUI组件...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from models.packer_model import PyInstallerModel
        from config.app_config import AppConfig
        from views.tabs.enhanced_module_tab import EnhancedModuleTab
        
        # 创建应用程序（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建配置和模型
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 创建增强模块标签页
        enhanced_tab = EnhancedModuleTab(model, config)
        print("  ✅ 增强模块标签页创建成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ GUI组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 精准依赖检测系统集成测试")
    print("=" * 50)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_functionality():
        success = False
    
    if not test_gui_components():
        success = False
    
    if success:
        print("\n✅ 所有测试通过！精准依赖检测系统集成成功")
        print("\n💡 建议:")
        print("  1. 可以启动应用程序测试: python run.py")
        print("  2. 在模块管理标签页中测试新的精准分析功能")
        print("  3. 对比传统分析和精准分析的结果差异")
        return 0
    else:
        print("\n❌ 测试失败！请检查集成过程")
        return 1

if __name__ == "__main__":
    sys.exit(main())
