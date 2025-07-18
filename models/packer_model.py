"""
PyInstaller打包模型
"""
from typing import List, Optional
import os
import sys
from config.app_config import AppConfig

class PyInstallerModel:
    """PyInstaller打包配置模型"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.reset_to_defaults()
    
    def reset_to_defaults(self) -> None:
        """重置为默认配置"""
        # 基本选项
        self.script_path: str = ""
        # 确保输出目录是绝对路径
        output_dir = self.config.get("output_dir", "./dist")
        self.output_dir: str = os.path.abspath(output_dir)
        self.icon_path: str = ""
        self.additional_files: List[str] = []
        self.additional_dirs: List[str] = []
        self.is_one_file: bool = self.config.get("is_one_file", True)
        self.is_windowed: bool = self.config.get("is_windowed", False)
        self.enable_upx: bool = self.config.get("enable_upx", False)
        self.hidden_imports: List[str] = []
        self.additional_args: str = ""
        
        # 高级选项
        self.name: str = ""
        self.contents_directory: str = ""
        self.upx_dir: str = ""
        self.clean: bool = self.config.get("clean", False)
        self.log_level: str = self.config.get("log_level", "INFO")
        
        # 捆绑选项
        self.add_binary: str = ""
        self.paths: str = ""
        self.hidden_import: str = ""
        self.collect_submodules: str = ""
        self.collect_data: str = ""
        self.collect_binaries: str = ""
        self.collect_all: str = ""
        self.copy_metadata: str = ""
        self.recursive_copy_metadata: str = ""
        self.hooks_dir: str = ""
        self.runtime_hook: str = ""
        self.exclude_module: str = ""
        self.splash: str = ""
    
    def generate_command(self, python_interpreter: str = "") -> str:
        """生成PyInstaller命令"""
        if not self.script_path:
            return ""

        # 使用指定的Python解释器，如果没有指定则使用当前环境
        python_exe = python_interpreter or sys.executable
        cmd = [python_exe, "-m", "PyInstaller"]
        
        # 基本选项
        cmd.append("--onefile" if self.is_one_file else "--onedir")
        cmd.append("--windowed" if self.is_windowed else "--console")
        
        # 输出目录
        if self.output_dir:
            cmd.append(f"--distpath={os.path.abspath(self.output_dir)}")
        
        # 图标
        if self.icon_path:
            cmd.append(f"--icon={os.path.abspath(self.icon_path)}")
        
        # 高级选项
        if self.name:
            cmd.append(f"--name={self.name}")
        if self.contents_directory:
            cmd.append(f"--contents-directory={self.contents_directory}")
        if self.enable_upx and self.upx_dir:
            cmd.append(f"--upx-dir={os.path.abspath(self.upx_dir)}")
        if self.clean:
            cmd.append("--clean")
        if self.log_level:
            cmd.append(f"--log-level={self.log_level}")

        # 隐藏导入
        for module in self.hidden_imports:
            cmd.append(f"--hidden-import={module}")

        # 添加常见的隐藏导入
        common_hidden_imports = self._get_common_hidden_imports()
        for module in common_hidden_imports:
            if module not in self.hidden_imports:  # 避免重复
                cmd.append(f"--hidden-import={module}")

        # 添加关键的二进制文件（DLL）
        critical_binaries = self._get_critical_binaries()
        for binary_path in critical_binaries:
            cmd.append(f"--add-binary={binary_path}")

        # 智能检测并添加脚本特定的隐藏导入
        if self.script_path and os.path.exists(self.script_path):
            try:
                from services.module_detector import ModuleDetector
                detector = ModuleDetector(use_ast=True, use_pyinstaller=False)
                smart_args = detector.generate_pyinstaller_args(self.script_path)

                # 过滤掉已经存在的参数，避免重复
                existing_args = set(cmd)
                for arg in smart_args:
                    if arg not in existing_args:
                        cmd.append(arg)

            except Exception as e:
                print(f"智能模块检测失败: {e}")

        # 捆绑选项
        if self.add_binary:
            cmd.append(f"--add-binary={self.add_binary}")
        if self.paths:
            cmd.append(f"--paths={self.paths}")
        if self.hidden_import:
            cmd.append(f"--hidden-import={self.hidden_import}")
        if self.collect_submodules:
            cmd.append(f"--collect-submodules={self.collect_submodules}")
        if self.collect_data:
            cmd.append(f"--collect-data={self.collect_data}")
        if self.collect_binaries:
            cmd.append(f"--collect-binaries={self.collect_binaries}")
        if self.collect_all:
            cmd.append(f"--collect-all={self.collect_all}")
        if self.copy_metadata:
            cmd.append(f"--copy-metadata={self.copy_metadata}")
        if self.recursive_copy_metadata:
            cmd.append(f"--recursive-copy-metadata={self.recursive_copy_metadata}")
        if self.hooks_dir:
            cmd.append(f"--additional-hooks-dir={self.hooks_dir}")
        if self.runtime_hook:
            cmd.append(f"--runtime-hook={self.runtime_hook}")
        if self.exclude_module:
            for mod in self.exclude_module.split(','):
                mod = mod.strip()
                if mod:
                    cmd.append(f"--exclude-module={mod}")
        if self.splash:
            cmd.append(f"--splash={self.splash}")
        
        # 附加文件和目录
        for file_path in self.additional_files:
            cmd.append(f"--add-data={file_path}")
        for dir_path in self.additional_dirs:
            cmd.append(f"--add-data={dir_path}")
        
        # 附加参数
        if self.additional_args:
            # 按行分割参数，每行一个参数
            args_lines = self.additional_args.strip().split('\n')
            for line in args_lines:
                line = line.strip()
                if line and not line.startswith('#'):  # 忽略空行和注释
                    cmd.append(line)
        
        # 脚本文件
        cmd.append(os.path.abspath(self.script_path))
        
        return " ".join(cmd)

    def generate_spec_file(self, spec_path: str) -> bool:
        """生成PyInstaller spec文件"""
        try:
            # 读取模板文件
            template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'pyinstaller_spec_template.py')
            if not os.path.exists(template_path):
                return False

            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # 替换模板变量
            app_name = self.name if self.name else os.path.splitext(os.path.basename(self.script_path))[0]

            replacements = {
                '{{SCRIPT_PATH}}': self.script_path.replace('\\', '/'),
                '{{APP_NAME}}': app_name,
                '{{UPX_ENABLED}}': str(self.enable_upx).lower(),
                '{{CONSOLE_MODE}}': str(not self.is_windowed).lower(),
                '{{ICON_PATH}}': self.icon_path.replace('\\', '/') if self.icon_path else '',
            }

            # 处理COLLECT部分（目录模式）
            if not self.is_one_file:
                collect_section = """
# 目录模式收集
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx={upx_enabled},
    upx_exclude=[],
    name='{app_name}',
)""".format(upx_enabled=str(self.enable_upx).lower(), app_name=app_name)
            else:
                collect_section = "# 单文件模式，不需要COLLECT"

            replacements['{{COLLECT_SECTION}}'] = collect_section

            # 应用替换
            spec_content = template_content
            for placeholder, value in replacements.items():
                spec_content = spec_content.replace(placeholder, value)

            # 写入spec文件
            with open(spec_path, 'w', encoding='utf-8') as f:
                f.write(spec_content)

            return True

        except Exception as e:
            print(f"生成spec文件失败: {e}")
            return False

    def _get_common_hidden_imports(self) -> List[str]:
        """获取常见的隐藏导入模块"""
        return [
            # PyQt5 相关
            'PyQt5.sip',
            'sip',

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

            # XML 解析器相关（解决 pyexpat 问题）
            'xml.parsers.expat',
            'xml.etree.ElementTree',
            'xml.etree.cElementTree',
            'pyexpat',
            '_elementtree',
            'plistlib',

            # 邮件和MIME类型
            'email.mime',
            'email.mime.text',
            'email.mime.multipart',
            'email.mime.base',

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
            'pkg_resources',

            # 常见的第三方库
            'setuptools',
        ]

    def _get_critical_binaries(self) -> List[str]:
        """获取关键的二进制文件（DLL）路径"""
        import sys
        import os

        critical_binaries = []

        # 检查是否在conda环境中
        if hasattr(sys, 'prefix'):
            # 常见的关键DLL文件
            dll_names = [
                'libexpat.dll',     # XML解析器
                'expat.dll',        # XML解析器备用
                'liblzma.dll',      # LZMA压缩
                'LIBBZ2.dll',       # BZ2压缩
                'ffi.dll',          # FFI库
                'libffi.dll',       # FFI库备用
                'sqlite3.dll',      # SQLite数据库
                'libssl.dll',       # SSL库
                'libcrypto.dll',    # 加密库
            ]

            # 搜索路径
            search_paths = [
                os.path.join(sys.prefix, 'Library', 'bin'),  # conda环境
                os.path.join(sys.prefix, 'DLLs'),            # Python DLLs
                os.path.join(sys.prefix, 'bin'),             # 通用bin目录
            ]

            for search_path in search_paths:
                if os.path.exists(search_path):
                    for dll_name in dll_names:
                        dll_path = os.path.join(search_path, dll_name)
                        if os.path.exists(dll_path):
                            # 格式：源路径;目标路径
                            critical_binaries.append(f"{dll_path};.")

        return critical_binaries

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "script_path": self.script_path,
            "output_dir": self.output_dir,
            "icon_path": self.icon_path,
            "additional_files": self.additional_files,
            "additional_dirs": self.additional_dirs,
            "is_one_file": self.is_one_file,
            "is_windowed": self.is_windowed,
            "enable_upx": self.enable_upx,
            "hidden_imports": self.hidden_imports,
            "additional_args": self.additional_args,
            "name": self.name,
            "contents_directory": self.contents_directory,
            "upx_dir": self.upx_dir,
            "clean": self.clean,
            "log_level": self.log_level,
            "add_binary": self.add_binary,
            "paths": self.paths,
            "hidden_import": self.hidden_import,
            "collect_submodules": self.collect_submodules,
            "collect_data": self.collect_data,
            "collect_binaries": self.collect_binaries,
            "collect_all": self.collect_all,
            "copy_metadata": self.copy_metadata,
            "recursive_copy_metadata": self.recursive_copy_metadata,
            "hooks_dir": self.hooks_dir,
            "runtime_hook": self.runtime_hook,
            "exclude_module": self.exclude_module,
            "splash": self.splash,
        }
    
    def from_dict(self, data: dict) -> None:
        """从字典加载配置"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def validate_config(self) -> List[str]:
        """验证配置，返回错误信息列表"""
        errors = []

        if not self.script_path:
            errors.append("请选择要打包的Python脚本文件")
        elif not os.path.exists(self.script_path):
            errors.append(f"脚本文件不存在: {self.script_path}")

        if self.icon_path and not os.path.exists(self.icon_path):
            errors.append(f"图标文件不存在: {self.icon_path}")

        if not self.output_dir:
            errors.append("请设置输出目录")

        return errors