#!/usr/bin/env python3
"""
快速集成测试
"""

import sys
import os
import tempfile

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 快速集成测试开始")
    print("=" * 50)
    
    try:
        # 测试导入
        print("📦 测试模块导入...")
        from config.app_config import AppConfig
        from models.packer_model import PyInstallerModel
        from services.enhanced_module_detector import EnhancedModuleDetector
        print("  ✅ 所有模块导入成功")
        
        # 创建简单测试脚本
        test_content = '''
import os
import sys
import json

def main():
    print("Hello World")

if __name__ == "__main__":
    main()
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_script = f.name
        
        print(f"📝 创建测试脚本: {test_script}")
        
        # 测试配置
        print("🔧 测试配置...")
        config = AppConfig()
        model = PyInstallerModel(config)
        model.script_path = test_script
        model.output_dir = "./quick_test_dist"
        print("  ✅ 配置创建成功")
        
        # 测试增强检测器
        print("🔍 测试增强检测器...")
        detector = EnhancedModuleDetector(cache_dir=".quick_cache", max_workers=1)
        result = detector.detect_modules_with_cache(test_script)
        print(f"  ✅ 检测完成，发现 {len(result.detected_modules)} 个模块")
        
        # 测试命令生成
        print("🚀 测试命令生成...")
        command = model.generate_command()
        if command:
            print(f"  ✅ 命令生成成功，长度: {len(command)} 字符")
            
            # 统计参数
            args = command.split()
            hidden_imports = [arg for arg in args if arg.startswith("--hidden-import=")]
            print(f"  📊 隐藏导入参数: {len(hidden_imports)} 个")
        else:
            print("  ❌ 命令生成失败")
        
        print("\n✅ 快速集成测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理
        try:
            if 'test_script' in locals() and os.path.exists(test_script):
                os.remove(test_script)
                print("🧹 清理测试文件")
            
            import shutil
            if os.path.exists('.quick_cache'):
                shutil.rmtree('.quick_cache')
                print("🧹 清理缓存目录")
        except Exception:
            pass

if __name__ == "__main__":
    main()
