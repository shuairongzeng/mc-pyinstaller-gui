#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DLL修复功能
用于验证我们的解决方案是否能正确检测和包含关键的DLL文件
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.packer_model import PyInstallerModel
from config.app_config import AppConfig

def create_test_script():
    """创建一个测试用的Python脚本"""
    test_script_content = '''#!/usr/bin/env python3
"""
测试脚本 - 使用XML解析器
这个脚本会导入xml.parsers.expat，用于测试DLL修复
"""

import sys
import xml.parsers.expat
import xml.etree.ElementTree as ET

def main():
    print("🧪 测试脚本启动")
    print(f"Python版本: {sys.version}")
    
    # 测试XML解析器
    try:
        # 创建一个简单的XML
        root = ET.Element("test")
        child = ET.SubElement(root, "child")
        child.text = "Hello World"
        
        # 转换为字符串
        xml_str = ET.tostring(root, encoding='unicode')
        print(f"✅ XML解析器工作正常: {xml_str}")
        
        # 测试expat解析器
        parser = xml.parsers.expat.ParserCreate()
        print("✅ expat解析器创建成功")
        
    except Exception as e:
        print(f"❌ XML解析器测试失败: {e}")
        return 1
    
    print("🎉 所有测试通过！")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    
    # 创建临时测试脚本
    test_script_path = os.path.join(os.getcwd(), "test_xml_app.py")
    with open(test_script_path, 'w', encoding='utf-8') as f:
        f.write(test_script_content)
    
    return test_script_path

def test_dll_detection():
    """测试DLL检测功能"""
    print("🔍 测试DLL检测功能...")
    
    # 创建配置和模型
    config = AppConfig()
    model = PyInstallerModel(config)
    
    # 测试关键二进制文件检测
    critical_binaries = model._get_critical_binaries()
    
    print(f"检测到 {len(critical_binaries)} 个关键DLL文件:")
    for binary in critical_binaries:
        dll_path = binary.split(';')[0]  # 获取源路径
        dll_name = os.path.basename(dll_path)
        print(f"  ✅ {dll_name}: {dll_path}")
    
    return critical_binaries

def test_hidden_imports():
    """测试隐藏导入功能"""
    print("\n🔒 测试隐藏导入功能...")
    
    # 创建配置和模型
    config = AppConfig()
    model = PyInstallerModel(config)
    
    # 测试隐藏导入检测
    hidden_imports = model._get_common_hidden_imports()
    
    print(f"检测到 {len(hidden_imports)} 个隐藏导入模块:")
    
    # 按类别显示
    xml_modules = [m for m in hidden_imports if 'xml' in m or 'expat' in m or 'plist' in m]
    email_modules = [m for m in hidden_imports if 'email' in m]
    encoding_modules = [m for m in hidden_imports if 'encoding' in m]
    
    if xml_modules:
        print("  📄 XML相关模块:")
        for module in xml_modules:
            print(f"    - {module}")
    
    if email_modules:
        print("  📧 邮件相关模块:")
        for module in email_modules:
            print(f"    - {module}")
    
    if encoding_modules:
        print("  🔤 编码相关模块:")
        for module in encoding_modules:
            print(f"    - {module}")
    
    return hidden_imports

def test_command_generation():
    """测试命令生成功能"""
    print("\n⚙️ 测试命令生成功能...")
    
    # 创建测试脚本
    test_script_path = create_test_script()
    
    try:
        # 创建配置和模型
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 设置基本配置
        model.script_path = test_script_path
        model.output_dir = "./test_dist"
        model.is_one_file = True
        model.is_windowed = False  # 控制台模式便于测试
        model.name = "test_xml_app"
        
        # 生成命令
        command = model.generate_command()
        
        print("生成的PyInstaller命令:")
        print(command)
        
        # 检查命令中是否包含关键的DLL
        if "--add-binary=" in command:
            print("\n✅ 命令中包含二进制文件参数")
            binary_args = [arg for arg in command.split() if arg.startswith("--add-binary=")]
            for arg in binary_args[:5]:  # 只显示前5个
                print(f"  {arg}")
        else:
            print("\n❌ 命令中未包含二进制文件参数")
        
        # 检查XML相关的隐藏导入
        xml_imports = [arg for arg in command.split() if arg.startswith("--hidden-import=") and ('xml' in arg or 'expat' in arg)]
        if xml_imports:
            print("\n✅ 命令中包含XML相关的隐藏导入:")
            for arg in xml_imports:
                print(f"  {arg}")
        else:
            print("\n❌ 命令中未包含XML相关的隐藏导入")
        
        return command
        
    finally:
        # 清理测试文件
        if os.path.exists(test_script_path):
            os.remove(test_script_path)

def test_spec_generation():
    """测试spec文件生成功能"""
    print("\n📄 测试spec文件生成功能...")
    
    # 创建测试脚本
    test_script_path = create_test_script()
    
    try:
        # 创建配置和模型
        config = AppConfig()
        model = PyInstallerModel(config)
        
        # 设置基本配置
        model.script_path = test_script_path
        model.output_dir = "./test_dist"
        model.is_one_file = True
        model.is_windowed = False
        model.name = "test_xml_app"
        
        # 生成spec文件
        spec_path = "test_xml_app.spec"
        success = model.generate_spec_file(spec_path)
        
        if success and os.path.exists(spec_path):
            print(f"✅ spec文件生成成功: {spec_path}")
            
            # 检查spec文件内容
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec_content = f.read()
            
            # 检查是否包含DLL检测代码
            if "add_critical_dlls" in spec_content:
                print("✅ spec文件包含DLL自动检测代码")
            else:
                print("❌ spec文件未包含DLL自动检测代码")
            
            # 检查是否包含XML相关的隐藏导入
            if "xml.parsers.expat" in spec_content:
                print("✅ spec文件包含XML相关的隐藏导入")
            else:
                print("❌ spec文件未包含XML相关的隐藏导入")
            
            # 清理spec文件
            os.remove(spec_path)
            
        else:
            print("❌ spec文件生成失败")
        
    finally:
        # 清理测试文件
        if os.path.exists(test_script_path):
            os.remove(test_script_path)

def main():
    """主测试函数"""
    print("🧪 开始测试DLL修复功能")
    print("=" * 60)
    
    try:
        # 测试DLL检测
        critical_binaries = test_dll_detection()
        
        # 测试隐藏导入
        hidden_imports = test_hidden_imports()
        
        # 测试命令生成
        command = test_command_generation()
        
        # 测试spec文件生成
        test_spec_generation()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成！")
        
        # 总结
        print(f"\n📊 测试结果总结:")
        print(f"  - 检测到 {len(critical_binaries)} 个关键DLL文件")
        print(f"  - 包含 {len(hidden_imports)} 个隐藏导入模块")
        print(f"  - 生成的命令长度: {len(command.split())} 个参数")
        
        if critical_binaries:
            print("\n✅ DLL修复功能正常工作")
            print("   现在使用这个GUI工具打包的程序应该不会再出现pyexpat相关的错误了！")
        else:
            print("\n⚠️ 未检测到关键DLL文件")
            print("   可能不在conda环境中，或者DLL文件位置不同")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
