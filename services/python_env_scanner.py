#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 环境扫描服务
自动扫描和检测系统中的 Python 解释器和虚拟环境
"""

import os
import sys
import json
import subprocess
import platform
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class PythonEnvironment:
    """Python 环境信息"""
    name: str                    # 环境名称
    path: str                   # Python 解释器路径
    version: str                # Python 版本
    env_type: str              # 环境类型：system, conda, venv, virtualenv
    is_current: bool           # 是否为当前环境
    is_available: bool         # 是否可用
    has_pyinstaller: bool      # 是否安装了 PyInstaller
    env_path: Optional[str]    # 环境根目录路径
    description: str           # 描述信息
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        status_icons = []
        if self.is_current:
            status_icons.append("🟢")
        if not self.is_available:
            status_icons.append("❌")
        elif not self.has_pyinstaller:
            status_icons.append("⚠️")
        else:
            status_icons.append("✅")
        
        status = " ".join(status_icons)
        return f"{status} {self.name} ({self.version}) - {self.env_type}"


class PythonEnvironmentScanner:
    """Python 环境扫描器"""
    
    def __init__(self):
        self.current_python = sys.executable
        self.environments: List[PythonEnvironment] = []
    
    def scan_all_environments(self) -> List[PythonEnvironment]:
        """扫描所有 Python 环境"""
        self.environments = []
        
        # 扫描系统 Python
        self._scan_system_python()
        
        # 扫描 conda 环境
        self._scan_conda_environments()
        
        # 扫描 venv/virtualenv 环境
        self._scan_venv_environments()
        
        # 排序：当前环境优先，然后按类型和版本排序
        self.environments.sort(key=self._sort_key)
        
        return self.environments
    
    def _sort_key(self, env: PythonEnvironment) -> Tuple:
        """排序键"""
        # 当前环境优先级最高
        current_priority = 0 if env.is_current else 1
        
        # 环境类型优先级
        type_priority = {
            'current': 0,
            'conda': 1,
            'venv': 2,
            'virtualenv': 3,
            'system': 4
        }.get(env.env_type, 5)
        
        # 版本排序（降序）
        try:
            version_parts = [int(x) for x in env.version.split('.')]
            version_key = tuple([-x for x in version_parts])  # 负数实现降序
        except:
            version_key = (0,)
        
        return (current_priority, type_priority, version_key, env.name)
    
    def _scan_system_python(self):
        """扫描系统 Python"""
        try:
            # Windows 系统 Python 路径
            if platform.system() == "Windows":
                possible_paths = [
                    r"C:\Python*\python.exe",
                    r"C:\Program Files\Python*\python.exe",
                    r"C:\Program Files (x86)\Python*\python.exe",
                ]
                
                import glob
                for pattern in possible_paths:
                    for path in glob.glob(pattern):
                        if os.path.exists(path):
                            env = self._create_environment_info(
                                path, "system", f"System Python ({os.path.dirname(path)})"
                            )
                            if env:
                                self.environments.append(env)
            
            # 检查 PATH 中的 python
            try:
                result = subprocess.run(['where', 'python'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        path = line.strip()
                        if path and os.path.exists(path):
                            env = self._create_environment_info(
                                path, "system", f"System Python (PATH)"
                            )
                            if env and not any(e.path == env.path for e in self.environments):
                                self.environments.append(env)
            except:
                pass
                
        except Exception as e:
            print(f"扫描系统 Python 失败: {e}")
    
    def _scan_conda_environments(self):
        """扫描 conda 环境"""
        try:
            # 尝试多种方式调用 conda 命令
            conda_commands = ['conda', 'conda.exe']
            conda_result = None

            # 首先尝试从环境变量中获取 conda 路径
            conda_exe = os.environ.get('CONDA_EXE')
            if conda_exe and os.path.exists(conda_exe):
                conda_commands.insert(0, conda_exe)

            # 尝试从常见安装路径查找 conda
            common_conda_paths = [
                r'D:\software\anaconda3\Scripts\conda.exe',
                r'C:\ProgramData\Anaconda3\Scripts\conda.exe',
                r'C:\Users\{}\Anaconda3\Scripts\conda.exe'.format(os.environ.get('USERNAME', '')),
                r'C:\Users\{}\Miniconda3\Scripts\conda.exe'.format(os.environ.get('USERNAME', '')),
            ]

            for path in common_conda_paths:
                if os.path.exists(path):
                    conda_commands.append(path)

            for conda_cmd in conda_commands:
                try:
                    result = subprocess.run([conda_cmd, 'info', '--envs', '--json'],
                                          capture_output=True, text=True, timeout=15)

                    if result.returncode == 0:
                        conda_result = result
                        break
                except FileNotFoundError:
                    continue
                except Exception as e:
                    continue

            if conda_result:
                try:
                    info = json.loads(conda_result.stdout)
                    envs = info.get('envs', [])



                    for env_path in envs:
                        try:
                            # 标准化路径
                            env_path = os.path.normpath(env_path)

                            if platform.system() == "Windows":
                                python_path = os.path.join(env_path, 'python.exe')
                            else:
                                python_path = os.path.join(env_path, 'bin', 'python')

                            if os.path.exists(python_path):
                                env_name = os.path.basename(env_path)

                                # 特殊处理 base 环境和根环境
                                if env_name == 'base' or env_path.endswith('anaconda3') or env_path.endswith('miniconda3'):
                                    env_name = 'conda (base)'
                                elif env_name == '.conda':
                                    # 本地 conda 环境
                                    parent_name = os.path.basename(os.path.dirname(env_path))
                                    env_name = f'conda (local-{parent_name})'
                                else:
                                    env_name = f'conda ({env_name})'

                                # 检查是否已经添加过这个环境
                                if not any(os.path.normpath(e.path) == os.path.normpath(python_path) for e in self.environments):
                                    env = self._create_environment_info(
                                        python_path, "conda", env_name, env_path
                                    )
                                    if env:
                                        self.environments.append(env)
                        except Exception as e:
                            continue

                except json.JSONDecodeError as e:
                    pass
                except Exception as e:
                    pass
            else:
                self._scan_local_conda()

        except Exception as e:
            self._scan_local_conda()
    
    def _scan_local_conda(self):
        """扫描本地 .conda 目录"""
        try:
            # 查找当前目录及父目录中的 .conda
            current_dir = Path.cwd()
            for parent in [current_dir] + list(current_dir.parents):
                conda_dir = parent / '.conda'
                if conda_dir.exists():
                    if platform.system() == "Windows":
                        python_path = conda_dir / 'python.exe'
                    else:
                        python_path = conda_dir / 'bin' / 'python'
                    
                    if python_path.exists():
                        env = self._create_environment_info(
                            str(python_path), "conda", f"Local conda ({parent.name})", str(conda_dir)
                        )
                        if env:
                            self.environments.append(env)
                        break
        except Exception as e:
            print(f"扫描本地 conda 环境失败: {e}")
    
    def _scan_venv_environments(self):
        """扫描 venv/virtualenv 环境"""
        try:
            # 常见的虚拟环境目录
            common_venv_dirs = [
                os.path.expanduser('~/.virtualenvs'),  # virtualenvwrapper
                os.path.expanduser('~/venvs'),         # 常见目录
                os.path.expanduser('~/envs'),          # 常见目录
                './venv',                              # 项目本地
                './env',                               # 项目本地
                './.venv',                             # 项目本地
            ]
            
            for venv_dir in common_venv_dirs:
                if os.path.exists(venv_dir):
                    self._scan_venv_directory(venv_dir)
                    
        except Exception as e:
            print(f"扫描 venv 环境失败: {e}")
    
    def _scan_venv_directory(self, venv_dir: str):
        """扫描指定目录中的虚拟环境"""
        try:
            if os.path.isfile(venv_dir):
                return
                
            for item in os.listdir(venv_dir):
                item_path = os.path.join(venv_dir, item)
                if os.path.isdir(item_path):
                    # 检查是否为虚拟环境
                    if platform.system() == "Windows":
                        python_path = os.path.join(item_path, 'Scripts', 'python.exe')
                        if not os.path.exists(python_path):
                            python_path = os.path.join(item_path, 'python.exe')
                    else:
                        python_path = os.path.join(item_path, 'bin', 'python')
                    
                    if os.path.exists(python_path):
                        env_type = "venv" if self._is_venv(item_path) else "virtualenv"
                        env = self._create_environment_info(
                            python_path, env_type, f"{env_type} ({item})", item_path
                        )
                        if env:
                            self.environments.append(env)
                            
        except Exception as e:
            print(f"扫描虚拟环境目录 {venv_dir} 失败: {e}")
    
    def _is_venv(self, env_path: str) -> bool:
        """判断是否为 venv 创建的环境"""
        pyvenv_cfg = os.path.join(env_path, 'pyvenv.cfg')
        return os.path.exists(pyvenv_cfg)
    
    def _create_environment_info(self, python_path: str, env_type: str, 
                                name: str, env_path: Optional[str] = None) -> Optional[PythonEnvironment]:
        """创建环境信息对象"""
        try:
            # 检查解释器是否可用
            result = subprocess.run([python_path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return None
            
            version = result.stdout.strip().replace('Python ', '')
            is_current = os.path.normpath(python_path) == os.path.normpath(self.current_python)
            
            # 检查是否安装了 PyInstaller
            has_pyinstaller = self._check_pyinstaller(python_path)
            
            # 生成描述
            description = f"{env_type.title()} Python {version}"
            if env_path:
                description += f" at {env_path}"
            
            return PythonEnvironment(
                name=name,
                path=python_path,
                version=version,
                env_type=env_type,
                is_current=is_current,
                is_available=True,
                has_pyinstaller=has_pyinstaller,
                env_path=env_path,
                description=description
            )
            
        except Exception as e:
            print(f"创建环境信息失败 {python_path}: {e}")
            return None
    
    def _check_pyinstaller(self, python_path: str) -> bool:
        """检查是否安装了 PyInstaller"""
        try:
            result = subprocess.run([python_path, '-m', 'PyInstaller', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def install_pyinstaller(self, python_path: str) -> bool:
        """在指定环境中安装 PyInstaller"""
        try:
            result = subprocess.run([python_path, '-m', 'pip', 'install', 'pyinstaller'], 
                                  capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except Exception as e:
            print(f"安装 PyInstaller 失败: {e}")
            return False
    
    def get_environment_by_path(self, path: str) -> Optional[PythonEnvironment]:
        """根据路径获取环境信息"""
        for env in self.environments:
            if os.path.normpath(env.path) == os.path.normpath(path):
                return env
        return None


# 全局扫描器实例
_scanner = None

def get_scanner() -> PythonEnvironmentScanner:
    """获取全局扫描器实例"""
    global _scanner
    if _scanner is None:
        _scanner = PythonEnvironmentScanner()
    return _scanner


if __name__ == "__main__":
    # 测试代码
    scanner = PythonEnvironmentScanner()
    environments = scanner.scan_all_environments()
    
    print(f"找到 {len(environments)} 个 Python 环境:")
    for env in environments:
        print(f"  {env.get_display_name()}")
        print(f"    路径: {env.path}")
        print(f"    描述: {env.description}")
        print()
