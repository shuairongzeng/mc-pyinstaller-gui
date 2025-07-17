"""
模块检测服务
"""
import ast
import os
import sys
import subprocess
import importlib.util
import shutil
from typing import Set, List, Tuple, Optional, Callable

class ModuleDetector:
    """模块检测器"""

    def __init__(self, use_ast: bool = True, use_pyinstaller: bool = False, python_interpreter: str = ""):
        self.use_ast = use_ast
        self.use_pyinstaller = use_pyinstaller
        self.python_interpreter = python_interpreter or sys.executable
    
    def detect_modules(self, script_path: str, 
                      output_callback: Optional[Callable[[str], None]] = None) -> Set[str]:
        """检测脚本所需的模块"""
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"脚本文件不存在: {script_path}")
        
        all_modules = set()
        
        if self.use_ast:
            ast_modules = self._detect_with_ast(script_path, output_callback)
            all_modules.update(ast_modules)
        
        if self.use_pyinstaller:
            pyinstaller_modules = self._detect_with_pyinstaller(script_path, output_callback)
            all_modules.update(pyinstaller_modules)
        
        return all_modules
    
    def _detect_with_ast(self, script_path: str, 
                        output_callback: Optional[Callable[[str], None]] = None) -> Set[str]:
        """使用AST解析检测模块"""
        modules = set()
        
        try:
            if output_callback:
                output_callback("正在使用AST解析检测模块...")
            
            with open(script_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=script_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        modules.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        modules.add(node.module.split('.')[0])
            
            if output_callback:
                output_callback(f"AST解析检测到 {len(modules)} 个模块")
                
        except Exception as e:
            if output_callback:
                output_callback(f"AST解析失败: {str(e)}")
        
        return modules
    
    def _detect_with_pyinstaller(self, script_path: str,
                                output_callback: Optional[Callable[[str], None]] = None) -> Set[str]:
        """使用PyInstaller调试模式检测模块"""
        modules = set()
        
        try:
            if output_callback:
                output_callback("正在使用PyInstaller调试模式检测模块...")
            
            temp_dir = os.path.join(os.path.dirname(script_path), "__pyinstaller_tmp__")
            os.makedirs(temp_dir, exist_ok=True)
            
            cmd = [
                self.python_interpreter, "-m", "PyInstaller",
                "--noconfirm",
                "--debug", "imports",
                "--specpath", temp_dir,
                "--workpath", os.path.join(temp_dir, "build"),
                "--distpath", os.path.join(temp_dir, "dist"),
                "--clean",
                script_path
            ]
            
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=creationflags
            )
            
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                output_lines.append(line.strip())
                if output_callback:
                    output_callback(f"[PyInstaller Debug]: {line.strip()}")
            
            process.wait()
            
            # 解析输出中的模块信息
            for line in output_lines:
                if "INFO: Analyzing" in line and ".py" in line:
                    # 提取模块名
                    parts = line.split()
                    for part in parts:
                        if part.endswith('.py'):
                            module_name = os.path.basename(part).replace('.py', '')
                            if module_name and not module_name.startswith('__'):
                                modules.add(module_name)
            
            # 清理临时目录
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                if output_callback:
                    output_callback(f"已清理临时目录: {temp_dir}")
                    
        except Exception as e:
            if output_callback:
                output_callback(f"PyInstaller调试检测失败: {str(e)}")
        
        return modules

    def _check_module_availability(self, module_name: str) -> bool:
        """检查模块是否在指定的Python解释器中可用"""
        try:
            # 如果使用的是当前解释器，直接使用importlib
            if self.python_interpreter == sys.executable:
                spec = importlib.util.find_spec(module_name)
                return spec is not None

            # 使用指定的Python解释器检查模块
            cmd = [
                self.python_interpreter, "-c",
                f"import importlib.util; import sys; "
                f"spec = importlib.util.find_spec('{module_name}'); "
                f"sys.exit(0 if spec is not None else 1)"
            ]

            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            result = subprocess.run(
                cmd,
                capture_output=True,
                creationflags=creationflags
            )
            return result.returncode == 0

        except Exception:
            return False

    def get_module_info(self, modules: Set[str]) -> List[Tuple[str, str]]:
        """获取模块详细信息"""
        module_info = []

        for module_name in sorted(modules):
            try:
                spec = importlib.util.find_spec(module_name)
                if spec and spec.origin:
                    path = os.path.dirname(spec.origin)
                    module_info.append((module_name, path))
                else:
                    module_info.append((module_name, "未找到安装路径或内置模块"))
            except Exception as e:
                module_info.append((module_name, f"加载失败: {str(e)}"))

        return module_info

    def get_common_hidden_imports(self) -> List[str]:
        """获取常见的隐藏导入模块"""
        return [
            # PyQt5 相关
            'PyQt5.sip',
            'PyQt5.QtCore',
            'PyQt5.QtGui',
            'PyQt5.QtWidgets',

            # 系统相关
            'platform',
            'subprocess',
            'shutil',
            'tempfile',
            'pathlib',

            # 编码相关
            'encodings.utf_8',
            'encodings.cp1252',
            'encodings.ascii',
            'encodings.latin1',
            'encodings.gbk',

            # JSON和配置
            'json',
            'configparser',

            # 日志
            'logging.handlers',
            'logging.config',

            # 类型检查
            'typing_extensions',

            # 导入工具
            'importlib.util',
            'importlib.metadata',

            # PyInstaller 自身可能需要的模块
            'pkg_resources',
            'setuptools',
        ]

    def get_module_specific_hidden_imports(self, modules: Set[str]) -> List[str]:
        """根据检测到的模块获取特定的隐藏导入"""
        hidden_imports = []

        # 模块映射：检测到的模块 -> 需要的隐藏导入
        module_mappings = {
            'cv2': [
                'cv2',
                'numpy',
                'numpy.core',
                'numpy.core._multiarray_umath',
                'numpy.core._multiarray_tests',
                'numpy.linalg._umath_linalg',
                'numpy.fft._pocketfft_internal',
                'numpy.random._common',
                'numpy.random.bit_generator',
                'numpy.random._bounded_integers',
                'numpy.random._mt19937',
                'numpy.random.mtrand',
                'numpy.random._philox',
                'numpy.random._pcg64',
                'numpy.random._sfc64',
                'numpy.random._generator',
            ],
            'numpy': [
                'numpy',
                'numpy.core',
                'numpy.core._multiarray_umath',
                'numpy.core._multiarray_tests',
                'numpy.linalg._umath_linalg',
                'numpy.fft._pocketfft_internal',
                'numpy.random._common',
                'numpy.random.bit_generator',
                'numpy.random._bounded_integers',
                'numpy.random._mt19937',
                'numpy.random.mtrand',
            ],
            'pandas': [
                'pandas',
                'pandas._libs.tslibs.timedeltas',
                'pandas._libs.tslibs.np_datetime',
                'pandas._libs.tslibs.nattype',
                'pandas._libs.tslibs.timestamps',
                'pandas._libs.properties',
                'pandas._libs.tslibs.base',
                'pandas._libs.tslibs.dtypes',
                'pandas._libs.tslibs.timezones',
                'pandas._libs.tslibs.fields',
                'pandas._libs.tslibs.parsing',
                'pandas._libs.tslibs.strptime',
                'pandas._libs.tslibs.conversion',
                'pandas._libs.tslibs.period',
                'pandas._libs.tslibs.offsets',
                'pandas._libs.tslibs.frequencies',
                'pandas._libs.tslibs.resolution',
                'pandas._libs.tslibs.tzconversion',
                'pandas._libs.tslibs.vectorized',
            ],
            'matplotlib': [
                'matplotlib',
                'matplotlib.backends',
                'matplotlib.backends.backend_tkagg',
                'matplotlib.backends.backend_agg',
                'matplotlib.figure',
                'matplotlib.pyplot',
                'matplotlib._path',
                'matplotlib.ft2font',
                'matplotlib._image',
                'matplotlib._tri',
                'matplotlib._qhull',
                'matplotlib.backends._backend_agg',
                'matplotlib.backends._tkagg',
            ],
            'PIL': [
                'PIL',
                'PIL._imaging',
                'PIL._imagingft',
                'PIL._imagingmath',
                'PIL._imagingmorph',
                'PIL._imagingtk',
                'PIL._webp',
            ],
            'requests': [
                'requests',
                'urllib3',
                'certifi',
                'chardet',
                'idna',
                'requests.packages.urllib3',
            ],
            'selenium': [
                'selenium',
                'selenium.webdriver',
                'selenium.webdriver.chrome',
                'selenium.webdriver.firefox',
                'selenium.webdriver.edge',
                'selenium.webdriver.common',
                'selenium.webdriver.support',
                'selenium.common.exceptions',
            ],
            'tkinter': [
                'tkinter',
                'tkinter.ttk',
                'tkinter.messagebox',
                'tkinter.filedialog',
                'tkinter.colorchooser',
                'tkinter.commondialog',
                'tkinter.simpledialog',
                '_tkinter',
            ],
            'PyQt5': [
                'PyQt5',
                'PyQt5.sip',
                'sip',
                'PyQt5.QtCore',
                'PyQt5.QtGui',
                'PyQt5.QtWidgets',
                'PyQt5.QtNetwork',
                'PyQt5.QtMultimedia',
                'PyQt5.QtWebEngineWidgets',
            ],
            'openpyxl': [
                'openpyxl',
                'openpyxl.workbook',
                'openpyxl.worksheet',
                'openpyxl.styles',
                'openpyxl.utils',
                'et_xmlfile',
            ],
            'xlsxwriter': [
                'xlsxwriter',
                'xlsxwriter.workbook',
                'xlsxwriter.worksheet',
                'xlsxwriter.format',
                'xlsxwriter.chart',
            ],
            'psutil': [
                'psutil',
                'psutil._psutil_windows',
                'psutil._psutil_posix',
            ],
            'win32api': [
                'win32api',
                'win32con',
                'win32gui',
                'win32process',
                'win32file',
                'win32pipe',
                'win32event',
                'win32security',
                'pywintypes',
                'pythoncom',
            ],
            'pyautogui': [
                'pyautogui',
                'pyscreeze',
                'pymsgbox',
                'pytweening',
                'pygetwindow',
                'mouseinfo',
            ],
        }

        # 根据检测到的模块添加对应的隐藏导入
        for module in modules:
            # 直接匹配
            if module in module_mappings:
                hidden_imports.extend(module_mappings[module])

            # 模糊匹配（处理子模块）
            for key, imports in module_mappings.items():
                if module.startswith(key + '.') or key.startswith(module + '.'):
                    hidden_imports.extend(imports)

        # 去重并返回
        return list(set(hidden_imports))

    def detect_dynamic_imports(self, script_path: str) -> Set[str]:
        """检测动态导入的模块"""
        dynamic_imports = set()

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检测 importlib.import_module 调用
            import re

            # 匹配 importlib.import_module("module_name")
            pattern1 = r'importlib\.import_module\([\'"]([^\'\"]+)[\'"]\)'
            matches1 = re.findall(pattern1, content)
            dynamic_imports.update(matches1)

            # 匹配 __import__("module_name")
            pattern2 = r'__import__\([\'"]([^\'\"]+)[\'"]\)'
            matches2 = re.findall(pattern2, content)
            dynamic_imports.update(matches2)

            # 匹配字符串形式的导入
            pattern3 = r'from\s+[\'"]([^\'\"]+)[\'"]\s+import'
            matches3 = re.findall(pattern3, content)
            dynamic_imports.update(matches3)

        except Exception as e:
            print(f"检测动态导入失败: {e}")

        return dynamic_imports

    def analyze_missing_modules(self, script_path: str) -> dict:
        """分析缺失的模块并提供修复建议"""
        result = {
            'missing_modules': [],
            'suggestions': [],
            'hidden_imports': [],
            'data_files': [],
            'collect_all': [],
            'detected_modules': []
        }

        try:
            # 检测所有模块
            detected_modules = self.detect_modules(script_path)
            dynamic_modules = self.detect_dynamic_imports(script_path)
            all_modules = detected_modules.union(dynamic_modules)

            result['detected_modules'] = list(all_modules)

            # 检查每个模块是否可用
            available_modules = set()
            for module_name in all_modules:
                if self._check_module_availability(module_name):
                    available_modules.add(module_name)
                else:
                    result['missing_modules'].append(module_name)
                    result['suggestions'].append(f"模块 '{module_name}' 未找到，请检查是否已安装")

            # 添加常见的隐藏导入
            common_hidden = self.get_common_hidden_imports()
            result['hidden_imports'].extend(common_hidden)

            # 根据检测到的模块添加特定的隐藏导入
            module_specific_hidden = self.get_module_specific_hidden_imports(available_modules)
            result['hidden_imports'].extend(module_specific_hidden)

            # 去重
            result['hidden_imports'] = list(set(result['hidden_imports']))

            # 检查是否需要特殊的数据文件和collect-all参数
            self._add_special_handling(available_modules, result)

        except Exception as e:
            result['suggestions'].append(f"分析过程中出错: {str(e)}")

        return result

    def _add_special_handling(self, modules: Set[str], result: dict) -> None:
        """添加特殊模块的处理建议"""

        # 需要collect-all的模块
        collect_all_modules = {
            'PyQt5': 'PyQt5',
            'PyQt6': 'PyQt6',
            'PySide2': 'PySide2',
            'PySide6': 'PySide6',
            'tkinter': 'tkinter',
            'matplotlib': 'matplotlib',
            'pandas': 'pandas',
            'numpy': 'numpy',
            'cv2': 'cv2',
            'PIL': 'PIL',
            'sklearn': 'sklearn',
            'scipy': 'scipy',
        }

        for module in modules:
            for key, collect_name in collect_all_modules.items():
                if module.startswith(key):
                    if collect_name not in result['collect_all']:
                        result['collect_all'].append(collect_name)
                        result['suggestions'].append(f"建议使用 --collect-all {collect_name} 参数")

        # 特殊数据文件处理
        if any(m.startswith('PyQt') for m in modules):
            result['data_files'].append("Qt库可能需要额外的DLL文件和插件")

        if any(m.startswith('matplotlib') for m in modules):
            result['data_files'].append("matplotlib可能需要字体文件和配置")

        if any(m.startswith('cv2') for m in modules):
            result['data_files'].append("OpenCV可能需要额外的DLL文件")

        if any('config' in m.lower() for m in modules):
            result['data_files'].append("检测到配置文件相关模块，可能需要包含配置文件")
            result['suggestions'].append("建议使用 --add-data 参数包含配置文件")

    def generate_pyinstaller_args(self, script_path: str) -> List[str]:
        """根据分析结果生成推荐的PyInstaller参数"""
        args = []

        try:
            analysis = self.analyze_missing_modules(script_path)

            # 添加隐藏导入
            for module in analysis['hidden_imports']:
                args.append(f"--hidden-import={module}")

            # 添加collect-all参数
            for module in analysis['collect_all']:
                args.append(f"--collect-all={module}")

            # 根据检测到的模块添加特殊参数
            detected_modules = set(analysis['detected_modules'])

            # OpenCV特殊处理
            if any('cv2' in mod for mod in detected_modules):
                args.extend([
                    "--collect-all=cv2",
                    "--collect-binaries=cv2",
                    "--hidden-import=numpy.core._multiarray_umath",
                    "--hidden-import=numpy.core._multiarray_tests",
                ])

            # numpy特殊处理
            if any('numpy' in mod for mod in detected_modules):
                args.extend([
                    "--collect-all=numpy",
                    "--hidden-import=numpy.core._multiarray_umath",
                    "--hidden-import=numpy.linalg._umath_linalg",
                ])

            # matplotlib特殊处理
            if any('matplotlib' in mod for mod in detected_modules):
                args.extend([
                    "--collect-all=matplotlib",
                    "--collect-data=matplotlib",
                ])

            # pandas特殊处理
            if any('pandas' in mod for mod in detected_modules):
                args.extend([
                    "--collect-all=pandas",
                    "--hidden-import=pandas._libs.tslibs.timedeltas",
                ])

            # PIL/Pillow特殊处理
            if any('PIL' in mod for mod in detected_modules):
                args.extend([
                    "--collect-all=PIL",
                    "--hidden-import=PIL._imaging",
                ])

            # requests特殊处理
            if any('requests' in mod for mod in detected_modules):
                args.extend([
                    "--collect-all=requests",
                    "--collect-all=urllib3",
                    "--collect-all=certifi",
                ])

            # selenium特殊处理
            if any('selenium' in mod for mod in detected_modules):
                args.extend([
                    "--collect-all=selenium",
                    "--collect-binaries=selenium",
                ])

            # 配置文件处理
            if any('config' in mod.lower() for mod in detected_modules):
                # 检查常见的配置文件
                config_files = ['config.json', 'config.yaml', 'config.ini', 'settings.json']
                script_dir = os.path.dirname(script_path)
                for config_file in config_files:
                    config_path = os.path.join(script_dir, config_file)
                    if os.path.exists(config_path):
                        args.append(f"--add-data={config_file};.")

        except Exception as e:
            print(f"生成PyInstaller参数失败: {e}")

        return args