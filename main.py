#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境调试脚本
用于检查当前 Python 环境的详细信息
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f" {title} ")
    print("="*60)

def get_conda_info():
    """获取 conda 环境信息"""
    try:
        result = subprocess.run(['conda', 'info', '--json'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        else:
            return None
    except Exception as e:
        print(f"获取 conda 信息时出错：{e}")
        return None

def main():
    print_separator("Python 环境调试信息")
    
    # 基本 Python 信息
    print(f"Python 版本：{sys.version}")
    print(f"Python 可执行文件路径：{sys.executable}")
    print(f"Python 安装路径：{sys.prefix}")
    print(f"Python 库路径：{sys.path[0] if sys.path else 'N/A'}")
    
    # 平台信息
    print_separator("系统平台信息")
    print(f"操作系统：{platform.system()}")
    print(f"系统版本：{platform.version()}")
    print(f"架构：{platform.architecture()}")
    print(f"处理器：{platform.processor()}")
    
    # 环境变量
    print_separator("重要环境变量")
    important_vars = ['CONDA_DEFAULT_ENV', 'CONDA_PREFIX', 'VIRTUAL_ENV', 'PATH']
    for var in important_vars:
        value = os.environ.get(var, 'Not Set')
        if var == 'PATH':
            # PATH 太长，只显示前几个路径
            paths = value.split(os.pathsep)[:5] if value != 'Not Set' else []
            print(f"{var}: {os.pathsep.join(paths)}{'...' if len(paths) == 5 else ''}")
        else:
            print(f"{var}: {value}")
    
    # 当前工作目录
    print_separator("目录信息")
    print(f"当前工作目录：{os.getcwd()}")
    print(f"脚本所在目录：{Path(__file__).parent.absolute()}")
    
    # 检查是否在虚拟环境中
    print_separator("虚拟环境检测")
    
    # 方法 1: 检查 sys.prefix
    in_venv_sys = sys.prefix != sys.base_prefix
    print(f"sys.prefix 检测：{'是' if in_venv_sys else '否'} (在虚拟环境中)")
    print(f"  sys.prefix: {sys.prefix}")
    print(f"  sys.base_prefix: {sys.base_prefix}")
    
    # 方法 2: 检查 VIRTUAL_ENV 环境变量
    virtual_env = os.environ.get('VIRTUAL_ENV')
    print(f"VIRTUAL_ENV 变量：{'设置' if virtual_env else '未设置'}")
    if virtual_env:
        print(f"  VIRTUAL_ENV: {virtual_env}")
    
    # 方法 3: 检查 CONDA 环境
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    conda_prefix = os.environ.get('CONDA_PREFIX')
    print(f"CONDA 环境检测：{'是' if conda_env else '否'} (在 conda 环境中)")
    if conda_env:
        print(f"  CONDA_DEFAULT_ENV: {conda_env}")
    if conda_prefix:
        print(f"  CONDA_PREFIX: {conda_prefix}")
    
    # 获取详细的 conda 信息
    print_separator("Conda 详细信息")
    conda_info = get_conda_info()
    if conda_info:
        print(f"Conda 版本：{conda_info.get('conda_version', 'Unknown')}")
        print(f"当前环境：{conda_info.get('active_prefix_name', 'Unknown')}")
        print(f"环境路径：{conda_info.get('active_prefix', 'Unknown')}")
        print(f"默认环境：{conda_info.get('default_prefix', 'Unknown')}")
    else:
        print("无法获取 conda 信息")
    
    # 检查已安装的包
    print_separator("已安装的重要包")
    important_packages = ['pip', 'wheel', 'numpy', 'pandas', 'requests']

    for package in important_packages:
        try:
            __import__(package)
            module = sys.modules[package]
            version = getattr(module, '__version__', 'Unknown')
            location = getattr(module, '__file__', 'Unknown')
            print(f"{package}: {version}")
            print(f"  位置：{location}")
        except ImportError:
            print(f"{package}: 未安装")
        except Exception as e:
            print(f"{package}: 导入错误 - {e}")

    # 检查 setuptools 单独处理
    try:
        import setuptools
        print(f"setuptools: {setuptools.__version__}")
        print(f"  位置：{setuptools.__file__}")
    except Exception as e:
        print(f"setuptools: 错误 - {e}")
    
    # 总结
    print_separator("环境总结")
    if conda_env and conda_prefix:
        print("✓ 当前正在使用 Conda 虚拟环境")
        print(f"  环境名称：{conda_env}")
        print(f"  环境路径：{conda_prefix}")
        
        # 检查是否是项目本地环境
        current_dir = Path.cwd()
        if conda_prefix and str(current_dir) in conda_prefix:
            print("✓ 这是项目本地的虚拟环境")
        else:
            print("! 这是全局的 conda 环境")
            
    elif virtual_env:
        print("✓ 当前正在使用 Python 虚拟环境")
        print(f"  环境路径：{virtual_env}")
    elif in_venv_sys:
        print("✓ 检测到虚拟环境（通过 sys.prefix）")
    else:
        print("! 当前可能在使用系统 Python 环境")
    
    print(f"\nPython 可执行文件：{sys.executable}")

if __name__ == "__main__":
    main()
