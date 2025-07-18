#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
用于验证打包功能是否正常
"""

import sys
import json
import configparser

def main():
    """主函数"""
    print("🚀 简单测试程序启动")
    print(f"Python版本: {sys.version}")
    
    # 测试JSON功能
    test_data = {"message": "Hello World", "version": "1.0"}
    json_str = json.dumps(test_data, ensure_ascii=False)
    print(f"JSON测试: {json_str}")
    
    # 测试配置解析
    config = configparser.ConfigParser()
    config.add_section('test')
    config.set('test', 'key', 'value')
    print("配置解析测试: 成功")
    
    print("✅ 所有测试通过！")
    input("按回车键退出...")

if __name__ == "__main__":
    main()
