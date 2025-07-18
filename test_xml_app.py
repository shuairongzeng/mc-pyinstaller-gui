#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试XML应用程序
这个程序会使用xml.parsers.expat，用于验证DLL修复是否有效
"""

import sys
import xml.parsers.expat
import xml.etree.ElementTree as ET
import json
import platform

def test_xml_parsing():
    """测试XML解析功能"""
    print("🧪 测试XML解析功能...")
    
    try:
        # 创建一个简单的XML
        root = ET.Element("application")
        root.set("name", "test_xml_app")
        root.set("version", "1.0")
        
        # 添加子元素
        info = ET.SubElement(root, "info")
        info.text = "这是一个测试XML解析的应用程序"
        
        platform_elem = ET.SubElement(root, "platform")
        platform_elem.text = platform.system()
        
        python_elem = ET.SubElement(root, "python")
        python_elem.text = sys.version
        
        # 转换为字符串
        xml_str = ET.tostring(root, encoding='unicode')
        print(f"✅ XML创建成功:")
        print(xml_str)
        
        # 解析XML字符串
        parsed_root = ET.fromstring(xml_str)
        print(f"✅ XML解析成功: {parsed_root.get('name')} v{parsed_root.get('version')}")
        
        return True
        
    except Exception as e:
        print(f"❌ XML解析测试失败: {e}")
        return False

def test_expat_parser():
    """测试expat解析器"""
    print("\n🔍 测试expat解析器...")
    
    try:
        # 创建expat解析器
        parser = xml.parsers.expat.ParserCreate()
        print("✅ expat解析器创建成功")
        
        # 设置处理函数
        elements = []
        
        def start_element(name, attrs):
            elements.append(f"开始元素: {name}")
            if attrs:
                elements.append(f"  属性: {attrs}")
        
        def end_element(name):
            elements.append(f"结束元素: {name}")
        
        def char_data(data):
            data = data.strip()
            if data:
                elements.append(f"  内容: {data}")
        
        parser.StartElementHandler = start_element
        parser.EndElementHandler = end_element
        parser.CharacterDataHandler = char_data
        
        # 解析XML
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<test>
    <message>Hello from expat parser!</message>
    <status>working</status>
</test>"""
        
        parser.Parse(xml_data, True)
        
        print("✅ expat解析完成:")
        for element in elements:
            print(f"  {element}")
        
        return True
        
    except Exception as e:
        print(f"❌ expat解析器测试失败: {e}")
        return False

def test_json_functionality():
    """测试JSON功能（确保其他功能也正常）"""
    print("\n📄 测试JSON功能...")
    
    try:
        # 创建测试数据
        test_data = {
            "app_name": "test_xml_app",
            "version": "1.0",
            "features": ["xml_parsing", "expat_support", "json_support"],
            "platform": platform.system(),
            "python_version": sys.version_info[:3]
        }
        
        # 序列化
        json_str = json.dumps(test_data, indent=2, ensure_ascii=False)
        print("✅ JSON序列化成功:")
        print(json_str)
        
        # 反序列化
        parsed_data = json.loads(json_str)
        print(f"✅ JSON反序列化成功: {parsed_data['app_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 测试XML应用程序启动")
    print("=" * 50)
    print(f"Python版本: {sys.version}")
    print(f"平台: {platform.system()} {platform.release()}")
    print(f"架构: {platform.architecture()[0]}")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        ("XML解析", test_xml_parsing),
        ("expat解析器", test_expat_parser),
        ("JSON功能", test_json_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！DLL修复功能工作正常！")
        return 0
    else:
        print("⚠️ 部分测试失败，可能存在DLL问题")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        input("\n按回车键退出...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 程序异常: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)
