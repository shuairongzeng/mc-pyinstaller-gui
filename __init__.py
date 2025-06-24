"""
PyInstaller打包工具

@Description: 基于PyQt5开发的PyInstaller图形化打包工具
@Version: 1.0.1
@Author: xuyou & xiaomizha
"""
import os
import sys
import webbrowser
from datetime import datetime
import subprocess
import importlib.util
import ast
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QAction, QLabel, QLineEdit, QPushButton,
    QFileDialog, QCheckBox, QRadioButton, QButtonGroup, QTextEdit,
    QGroupBox, QGridLayout, QComboBox, QListWidget, QMessageBox,
    QProgressBar, QSplitter, QFrame, QScrollArea, QInputDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from about_dialog import AboutDialog


class PackageThread(QThread):
    """打包线程"""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=creationflags
            )

            for line in iter(self.process.stdout.readline, ''):
                self.output_signal.emit(line.strip())

            self.process.wait()
            self.finished_signal.emit(self.process.returncode == 0)
        except Exception as e:
            self.output_signal.emit(f"错误: {str(e)}")
            self.finished_signal.emit(False)

    def terminate(self):
        if self.process and self.process.poll() is None:
            if sys.platform == "win32":
                subprocess.run(f"taskkill /F /T /PID {self.process.pid}", shell=True, capture_output=True)
            else:
                import signal
                os.kill(self.process.pid, signal.SIGTERM)
                self.process.wait(timeout=5)
                if self.process.poll() is None:
                    os.kill(self.process.pid, signal.SIGKILL)
        super().terminate()


class PyInstallerPacker:
    """PyInstaller打包核心类"""

    def __init__(self):
        # 基本选项
        self.script_path = ""
        self.output_dir = "./dist"
        self.icon_path = ""
        self.additional_files = []
        self.additional_dirs = []
        self.is_one_file = True
        self.is_windowed = False
        self.enable_upx = False
        self.hidden_imports = []
        self.additional_args = ""

        # 高级选项
        self.name = ""
        self.contents_directory = ""
        self.upx_checkbox = False
        self.upx_dir = ""
        self.clean = False
        self.log_level = ""

        # 捆绑选项
        self.add_binary = ""
        self.paths = ""
        self.hidden_import = ""
        self.collect_submodules = ""
        self.collect_data = ""
        self.collect_binaries = ""
        self.collect_all = ""
        self.copy_metadata = ""
        self.recursive_copy_metadata = ""
        self.hooks_dir = ""
        self.runtime_hook = ""
        self.exclude_module = ""
        self.splash = ""

        # 生成选项
        self.debug = ""
        self.optimize = ""
        self.python_option = ""
        self.strip = False
        self.noupx = False
        self.upx_exclude = ""

        # Windows和macOS特定选项
        self.hide_console = ""
        self.disable_windowed_traceback = False

        # Windows特定选项
        self.version_file = ""
        self.manifest = ""
        self.resource = ""
        self.uac_admin = False
        self.uac_uiaccess = False

        # macOS特定选项
        self.argv_emulation = False
        self.osx_bundle_identifier = ""
        self.target_architecture = ""
        self.codesign_identity = ""
        self.osx_entitlements_file = ""

        # 特殊选项
        self.runtime_tmpdir = ""
        self.bootloader_ignore_signals = False

        # 其它选项
        self.module = ""

    def generate_command(self):
        """生成PyInstaller命令"""
        # import os
        if not self.script_path:
            return ""

        # cmd = ["pyinstaller"]
        cmd = [sys.executable, "-m", "PyInstaller"]

        # 基本选项
        if self.is_one_file:
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")

        if self.is_windowed:
            cmd.append("--windowed")
        else:
            cmd.append("--console")

        # 输出目录
        if self.output_dir:
            cmd.append(f"--distpath={os.path.abspath(self.output_dir)}")

        # 图标
        if self.icon_path:
            cmd.append(f"--icon={os.path.abspath(self.icon_path)}")

        # 附加文件
        for file_path in self.additional_files:
            if ':' not in file_path and ';' not in file_path:
                filename = os.path.basename(file_path)
                cmd.append(f"--add-data={file_path}:{filename}")
            else:
                formatted_path = file_path.replace(';', ':')
                cmd.append(f"--add-data={formatted_path}")
            # parts = file_path.split(':', 1)
            # src = os.path.abspath(parts[0])
            # dest = parts[1] if len(parts) > 1 else os.path.basename(src)
            # cmd.append(f"--add-data=\"{src}{os.pathsep}{dest}\"")

        # 附加目录
        for dir_path in self.additional_dirs:
            if ':' not in dir_path and ';' not in dir_path:
                dirname = os.path.basename(dir_path.rstrip('/\\'))
                cmd.append(f"--add-data={dir_path}:{dirname}")
            else:
                formatted_path = dir_path.replace(';', ':')
                cmd.append(f"--add-data={formatted_path}")
                # parts = dir_path.split(':', 1)
            # src = os.path.abspath(parts[0])
            # dest = parts[1] if len(parts) > 1 else os.path.basename(src.rstrip('/\\'))
            # cmd.append(f"--add-data=\"{src}{os.pathsep}{dest}\"")

        # # UPX压缩
        # if self.enable_upx:
        #     cmd.append("--upx-dir=upx")
        #
        # # 隐藏导入
        # for imp in self.hidden_imports:
        #     cmd.append(f"--hidden-import={imp}")

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

        # 捆绑选项
        if self.add_binary:
            # cmd.append(f"--add-binary={self.add_binary}")
            for entry in self.add_binary.replace(';', ',').split(','):
                entry = entry.strip()
                if entry:
                    src_dest_parts = entry.split(':', 1)
                    if len(src_dest_parts) == 2:
                        src_path = os.path.abspath(src_dest_parts[0])
                        dest_path = src_dest_parts[1]
                        cmd.append(f"--add-binary=\"{src_path}{os.pathsep}{dest_path}\"")
                    else:
                        cmd.append(f"--add-binary=\"{os.path.abspath(entry)}\"")
        if self.paths:
            # cmd.append(f"--paths={self.paths}")
            cmd.append(
                f"--paths={os.pathsep.join([os.path.abspath(p.strip()) for p in self.paths.split(';') if p.strip()])}")
        if self.hidden_import:
            for imp in self.hidden_import.split(','):
                imp = imp.strip()
                if imp:
                    cmd.append(f"--hidden-import={imp}")
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

        # 生成选项
        if self.debug:
            cmd.append(f"--debug={self.debug}")
        if self.optimize:
            cmd.append(f"--optimize={self.optimize}")
        if self.python_option:
            cmd.append(f"--python-option={self.python_option}")
        if self.strip:
            cmd.append("--strip")
        if self.noupx:
            cmd.append("--noupx")
        if self.upx_exclude:
            cmd.append(f"--upx-exclude={self.upx_exclude}")

        # Windows和macOS特定选项
        if self.hide_console:
            cmd.append(f"--hide-console={self.hide_console}")
        if self.disable_windowed_traceback:
            cmd.append("--disable-windowed-traceback")

        # Windows特定选项
        if self.version_file:
            cmd.append(f"--version-file={self.version_file}")
        if self.manifest:
            cmd.append(f"--manifest={self.manifest}")
        if self.resource:
            cmd.append(f"--resource={self.resource}")
        if self.uac_admin:
            cmd.append("--uac-admin")
        if self.uac_uiaccess:
            cmd.append("--uac-uiaccess")

        # macOS特定选项
        if self.argv_emulation:
            cmd.append("--argv-emulation")
        if self.osx_bundle_identifier:
            cmd.append(f"--osx-bundle-identifier={self.osx_bundle_identifier}")
        if self.target_architecture:
            cmd.append(f"--target-architecture={self.target_architecture}")
        if self.codesign_identity:
            cmd.append(f"--codesign-identity={self.codesign_identity}")
        if self.osx_entitlements_file:
            cmd.append(f"--osx-entitlements-file={self.osx_entitlements_file}")

        # 特殊选项
        if self.runtime_tmpdir:
            cmd.append(f"--runtime-tmpdir={self.runtime_tmpdir}")
        if self.bootloader_ignore_signals:
            cmd.append("--bootloader-ignore-signals")

        # 其它选项
        if self.module:
            # cmd.append(f"-m {self.module}")
            cmd[1:1] = ["-m", self.module]

        # 附加参数
        if self.additional_args.strip():
            cmd.extend(self.additional_args.split())

        # 脚本路径
        # cmd.append(self.script_path)
        if not self.module:
            cmd.append(os.path.abspath(self.script_path))

        # return " ".join(cmd)
        return " ".join(f'"{arg}"' if ' ' in arg and arg.startswith('--') else arg for arg in cmd)


class PyInstallerPackerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.packer = PyInstallerPacker()
        self.package_thread = None
        self.use_ast_detection = True
        self.use_pyinstaller_detection = False
        self.init_ui()
        self.center_window()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("PyInstaller打包工具 v1.0.1")
        self.setMinimumSize(800, 1000)

        self.create_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        title_label = QLabel("PyInstaller 打包工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        self.create_basic_tab()
        self.create_advanced_tab()
        self.create_module_tab()
        self.create_settings_tab()
        self.create_log_tab()

        self.create_bottom_buttons(layout)

    def create_menu_bar(self):
        """菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        new_action = QAction('新建项目(&N)', self)
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)
        open_action = QAction('打开项目(&O)', self)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)
        save_action = QAction('保存项目(&S)', self)
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+W')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu('编辑(&E)')
        clear_action = QAction('清空配置(&C)', self)
        clear_action.triggered.connect(self.clear_configuration)
        edit_menu.addAction(clear_action)

        # 选项菜单
        options_menu = menubar.addMenu('选项(&O)')
        settings_action = QAction('设置(&S)', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_settings)
        options_menu.addAction(settings_action)

        # 工具菜单
        tools_menu = menubar.addMenu('工具(&T)')
        check_pyinstaller_action = QAction('检查PyInstaller(&C)', self)
        check_pyinstaller_action.triggered.connect(self.check_pyinstaller)
        tools_menu.addAction(check_pyinstaller_action)
        install_pyinstaller_action = QAction('安装PyInstaller(&I)', self)
        install_pyinstaller_action.triggered.connect(self.install_pyinstaller)
        tools_menu.addAction(install_pyinstaller_action)
        tools_menu.addSeparator()
        detect_modules_action = QAction('检测所需模块(&D)', self)
        detect_modules_action.triggered.connect(self.detect_required_modules)
        tools_menu.addAction(detect_modules_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        donate_action = QAction('捐赠(&D)', self)
        donate_action.triggered.connect(self.open_donate_page)
        help_menu.addAction(donate_action)
        contact_action = QAction('联系(&C)', self)
        contact_action.triggered.connect(self.open_contact_page)
        help_menu.addAction(contact_action)
        homepage_action = QAction('首页(&H)', self)
        homepage_action.setShortcut('Home')
        homepage_action.triggered.connect(self.open_homepage)
        help_menu.addAction(homepage_action)
        help_menu.addSeparator()
        about_action = QAction('关于(&A)', self)
        about_action.setShortcut('Ctrl+Tab')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_basic_tab(self):
        """基本选项卡"""
        basic_widget = QWidget()
        layout = QVBoxLayout(basic_widget)

        # Python脚本路径
        script_group = QGroupBox("Python脚本")
        script_layout = QHBoxLayout(script_group)

        self.script_path_edit = QLineEdit()
        self.script_path_edit.setPlaceholderText("请选择Python脚本文件...")
        script_layout.addWidget(self.script_path_edit)

        script_browse_btn = QPushButton("浏览")
        script_browse_btn.clicked.connect(self.browse_script)
        script_layout.addWidget(script_browse_btn)

        layout.addWidget(script_group)

        # 基本打包选项
        options_group = QGroupBox("基本打包选项")
        options_layout = QGridLayout(options_group)

        # 单文件/单目录选择
        package_type_label = QLabel("打包类型:")
        options_layout.addWidget(package_type_label, 0, 0)

        self.package_type_group = QButtonGroup()
        self.onefile_radio = QRadioButton("单文件")
        self.onefile_radio.setChecked(True)
        self.onedir_radio = QRadioButton("单目录")

        self.package_type_group.addButton(self.onefile_radio)
        self.package_type_group.addButton(self.onedir_radio)

        options_layout.addWidget(self.onefile_radio, 0, 1)
        options_layout.addWidget(self.onedir_radio, 0, 2)

        # 窗口类型选择
        window_type_label = QLabel("窗口类型:")
        options_layout.addWidget(window_type_label, 1, 0)

        self.window_type_group = QButtonGroup()
        self.console_radio = QRadioButton("控制台")
        self.console_radio.setChecked(True)
        self.windowed_radio = QRadioButton("窗口")

        self.window_type_group.addButton(self.console_radio)
        self.window_type_group.addButton(self.windowed_radio)

        options_layout.addWidget(self.console_radio, 1, 1)
        options_layout.addWidget(self.windowed_radio, 1, 2)

        # 程序图标
        icon_label = QLabel("程序图标:")
        options_layout.addWidget(icon_label, 2, 0)

        self.icon_path_edit = QLineEdit()
        self.icon_path_edit.setPlaceholderText("可选: 选择图标文件...")
        options_layout.addWidget(self.icon_path_edit, 2, 1, 1, 2)

        icon_browse_btn = QPushButton("浏览")
        icon_browse_btn.clicked.connect(self.browse_icon)
        options_layout.addWidget(icon_browse_btn, 2, 3)

        detect_modules_basic_btn = QPushButton("检测所需模块")
        detect_modules_basic_btn.setToolTip("自动检测脚本中的导入模块")
        detect_modules_basic_btn.clicked.connect(self.detect_required_modules)
        options_layout.addWidget(detect_modules_basic_btn, 3, 0, 1, 4)

        layout.addWidget(options_group)

        # 附加文件
        files_group = QGroupBox("附加文件")
        files_layout = QVBoxLayout(files_group)

        files_buttons_layout = QHBoxLayout()
        add_file_btn = QPushButton("添加文件")
        add_file_btn.clicked.connect(self.add_file)
        add_dir_btn = QPushButton("添加目录")
        add_dir_btn.clicked.connect(self.add_directory)
        remove_btn = QPushButton("删除")
        remove_btn.clicked.connect(self.remove_file)

        files_buttons_layout.addWidget(add_file_btn)
        files_buttons_layout.addWidget(add_dir_btn)
        files_buttons_layout.addWidget(remove_btn)
        files_buttons_layout.addStretch()

        files_layout.addLayout(files_buttons_layout)

        self.files_list = QListWidget()
        files_layout.addWidget(self.files_list)

        layout.addWidget(files_group)

        # 完整CLI命令
        cli_group = QGroupBox("完整的CLI命令")
        cli_layout = QVBoxLayout(cli_group)

        self.cli_command_edit = QTextEdit()
        # self.cli_command_edit.setMaximumHeight(150)
        self.cli_command_edit.setReadOnly(True)
        cli_layout.addWidget(self.cli_command_edit)

        layout.addWidget(cli_group)

        self.tab_widget.addTab(basic_widget, "基本")

        self.script_path_edit.textChanged.connect(self.update_command)
        self.icon_path_edit.textChanged.connect(self.update_command)
        self.onefile_radio.toggled.connect(self.update_command)
        self.console_radio.toggled.connect(self.update_command)
        self.files_list.model().rowsInserted.connect(self.update_command)
        self.files_list.model().rowsRemoved.connect(self.update_command)

    def create_advanced_tab(self):
        """高级选项卡"""
        advanced_widget = QWidget()
        # layout = QVBoxLayout(advanced_widget)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        layout = QVBoxLayout(scroll_content_widget)

        # 高级打包选项
        advanced_group = QGroupBox("高级选项")
        advanced_layout = QGridLayout(advanced_group)

        # # UPX压缩
        # self.upx_checkbox = QCheckBox("启用UPX压缩")
        # advanced_layout.addWidget(self.upx_checkbox, 0, 0)
        #
        # # 隐藏导入
        # hidden_imports_label = QLabel("隐藏导入:")
        # advanced_layout.addWidget(hidden_imports_label, 1, 0)
        # self.hidden_imports_edit = QLineEdit()
        # self.hidden_imports_edit.setPlaceholderText("用逗号分隔多个模块名...")
        # advanced_layout.addWidget(self.hidden_imports_edit, 1, 1)
        # layout.addWidget(advanced_group)
        #
        # # 排除模块
        # exclude_group = QGroupBox("排除选项")
        # exclude_layout = QGridLayout(exclude_group)
        # exclude_label = QLabel("排除模块:")
        # exclude_layout.addWidget(exclude_label, 0, 0)
        # self.exclude_edit = QLineEdit()
        # self.exclude_edit.setPlaceholderText("用逗号分隔要排除的模块...")
        # exclude_layout.addWidget(self.exclude_edit, 0, 1)
        # layout.addWidget(exclude_group)

        # --name
        name_label = QLabel("程序名称 (--name):")
        advanced_layout.addWidget(name_label, 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("可选: 指定生成的程序名称...")
        advanced_layout.addWidget(self.name_edit, 0, 1)

        # --contents-directory
        contents_dir_label = QLabel("内容目录 (--contents-directory):")
        advanced_layout.addWidget(contents_dir_label, 1, 0)
        self.contents_dir_edit = QLineEdit()
        self.contents_dir_edit.setPlaceholderText("可选: 指定内容目录名称...")
        advanced_layout.addWidget(self.contents_dir_edit, 1, 1)

        # UPX压缩
        self.upx_checkbox = QCheckBox("启用UPX压缩")
        advanced_layout.addWidget(self.upx_checkbox, 2, 0)
        # --upx-dir
        upx_dir_label = QLabel("UPX目录 (--upx-dir):")
        advanced_layout.addWidget(upx_dir_label, 3, 0)
        self.upx_dir_edit = QLineEdit()
        self.upx_dir_edit.setPlaceholderText("可选: UPX可执行文件路径...")
        advanced_layout.addWidget(self.upx_dir_edit, 3, 1)
        upx_browse_btn = QPushButton("浏览")
        upx_browse_btn.clicked.connect(self.browse_upx_dir)
        advanced_layout.addWidget(upx_browse_btn, 3, 2)

        # --clean
        self.clean_checkbox = QCheckBox("清理缓存 (--clean)")
        advanced_layout.addWidget(self.clean_checkbox, 4, 0)

        # --log-level
        log_level_label = QLabel("日志级别 (--log-level):")
        advanced_layout.addWidget(log_level_label, 5, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["", "TRACE", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("")
        advanced_layout.addWidget(self.log_level_combo, 5, 1)

        layout.addWidget(advanced_group)

        # 捆绑选项
        bundle_group = QGroupBox("捆绑选项")
        bundle_layout = QGridLayout(bundle_group)

        # --add-binary
        add_binary_label = QLabel("添加二进制文件 (--add-binary):")
        bundle_layout.addWidget(add_binary_label, 0, 0)
        self.add_binary_edit = QLineEdit()
        self.add_binary_edit.setPlaceholderText("格式: src;dest 或 src:dest...")
        bundle_layout.addWidget(self.add_binary_edit, 0, 1)

        # --paths
        paths_label = QLabel("搜索路径 (--paths):")
        bundle_layout.addWidget(paths_label, 1, 0)
        self.paths_edit = QLineEdit()
        self.paths_edit.setPlaceholderText("用分号分隔多个路径...")
        bundle_layout.addWidget(self.paths_edit, 1, 1)

        # --hidden-import
        hidden_import_label = QLabel("隐藏导入 (--hidden-import):")
        bundle_layout.addWidget(hidden_import_label, 2, 0)
        self.hidden_import_edit = QLineEdit()
        self.hidden_import_edit.setPlaceholderText("用逗号分隔多个模块...")
        bundle_layout.addWidget(self.hidden_import_edit, 2, 1)

        # --collect-submodules
        collect_submodules_label = QLabel("收集子模块 (--collect-submodules):")
        bundle_layout.addWidget(collect_submodules_label, 3, 0)
        self.collect_submodules_edit = QLineEdit()
        self.collect_submodules_edit.setPlaceholderText("模块名...")
        bundle_layout.addWidget(self.collect_submodules_edit, 3, 1)

        # --collect-data
        collect_data_label = QLabel("收集数据 (--collect-data):")
        bundle_layout.addWidget(collect_data_label, 4, 0)
        self.collect_data_edit = QLineEdit()
        self.collect_data_edit.setPlaceholderText("模块名...")
        bundle_layout.addWidget(self.collect_data_edit, 4, 1)

        # --collect-binaries
        collect_binaries_label = QLabel("收集二进制 (--collect-binaries):")
        bundle_layout.addWidget(collect_binaries_label, 5, 0)
        self.collect_binaries_edit = QLineEdit()
        self.collect_binaries_edit.setPlaceholderText("模块名...")
        bundle_layout.addWidget(self.collect_binaries_edit, 5, 1)

        # --collect-all
        collect_all_label = QLabel("收集全部 (--collect-all):")
        bundle_layout.addWidget(collect_all_label, 6, 0)
        self.collect_all_edit = QLineEdit()
        self.collect_all_edit.setPlaceholderText("模块名...")
        bundle_layout.addWidget(self.collect_all_edit, 6, 1)

        # --copy-metadata
        copy_metadata_label = QLabel("复制元数据 (--copy-metadata):")
        bundle_layout.addWidget(copy_metadata_label, 7, 0)
        self.copy_metadata_edit = QLineEdit()
        self.copy_metadata_edit.setPlaceholderText("包名...")
        bundle_layout.addWidget(self.copy_metadata_edit, 7, 1)

        # --recursive-copy-metadata
        recursive_copy_metadata_label = QLabel("递归复制元数据 (--recursive-copy-metadata):")
        bundle_layout.addWidget(recursive_copy_metadata_label, 8, 0)
        self.recursive_copy_metadata_edit = QLineEdit()
        self.recursive_copy_metadata_edit.setPlaceholderText("包名...")
        bundle_layout.addWidget(self.recursive_copy_metadata_edit, 8, 1)

        # --additional-hooks-dir
        hooks_dir_label = QLabel("额外hooks目录 (--additional-hooks-dir):")
        bundle_layout.addWidget(hooks_dir_label, 9, 0)
        self.hooks_dir_edit = QLineEdit()
        self.hooks_dir_edit.setPlaceholderText("hooks目录路径...")
        bundle_layout.addWidget(self.hooks_dir_edit, 9, 1)

        # --runtime-hook
        runtime_hook_label = QLabel("运行时hook (--runtime-hook):")
        bundle_layout.addWidget(runtime_hook_label, 10, 0)
        self.runtime_hook_edit = QLineEdit()
        self.runtime_hook_edit.setPlaceholderText("hook文件路径...")
        bundle_layout.addWidget(self.runtime_hook_edit, 10, 1)

        # --exclude-module
        exclude_module_label = QLabel("排除模块 (--exclude-module):")
        bundle_layout.addWidget(exclude_module_label, 11, 0)
        self.exclude_module_edit = QLineEdit()
        self.exclude_module_edit.setPlaceholderText("用逗号分隔多个模块...")
        bundle_layout.addWidget(self.exclude_module_edit, 11, 1)

        # --splash
        splash_label = QLabel("启动画面 (--splash):")
        bundle_layout.addWidget(splash_label, 12, 0)
        self.splash_edit = QLineEdit()
        self.splash_edit.setPlaceholderText("启动画面图片路径...")
        bundle_layout.addWidget(self.splash_edit, 12, 1)

        layout.addWidget(bundle_group)

        # 生成选项
        generate_group = QGroupBox("生成选项")
        generate_layout = QGridLayout(generate_group)

        # --debug
        self.debug_label = QLabel("调试模式 (--debug)")
        generate_layout.addWidget(self.debug_label, 0, 0)
        self.debug_combo = QComboBox()
        self.debug_combo.addItems(["", "all", "imports", "bootloader", "noarchive"])
        generate_layout.addWidget(self.debug_combo, 0, 1)

        # --optimize
        optimize_label = QLabel("优化级别 (--optimize):")
        generate_layout.addWidget(optimize_label, 1, 0)
        self.optimize_combo = QComboBox()
        self.optimize_combo.addItems(["", "0", "1", "2", "-1"])
        generate_layout.addWidget(self.optimize_combo, 1, 1)

        # --python-option
        python_option_label = QLabel("Python选项 (--python-option):")
        generate_layout.addWidget(python_option_label, 2, 0)
        self.python_option_edit = QLineEdit()
        self.python_option_edit.setPlaceholderText("Python解释器选项...")
        generate_layout.addWidget(self.python_option_edit, 2, 1, 1, 2)

        # --strip
        self.strip_checkbox = QCheckBox("strip调试符号 (--strip)")
        generate_layout.addWidget(self.strip_checkbox, 3, 0)

        # --noupx
        self.noupx_checkbox = QCheckBox("禁用UPX (--noupx)")
        generate_layout.addWidget(self.noupx_checkbox, 4, 0)

        # --upx-exclude
        upx_exclude_label = QLabel("UPX排除 (--upx-exclude):")
        generate_layout.addWidget(upx_exclude_label, 5, 0)
        self.upx_exclude_edit = QLineEdit()
        self.upx_exclude_edit.setPlaceholderText("排除的文件模式...")
        generate_layout.addWidget(self.upx_exclude_edit, 5, 1, 1, 2)

        layout.addWidget(generate_group)

        # Windows和macOS X特定选项
        win_mac_group = QGroupBox("Windows和macOS X特定选项")
        win_mac_layout = QGridLayout(win_mac_group)

        # --hide-console
        hide_console_label = QLabel("隐藏控制台 (--hide-console):")
        win_mac_layout.addWidget(hide_console_label, 0, 0)
        self.hide_console_combo = QComboBox()
        self.hide_console_combo.addItems(["", "hide-early", "hide-late", "minimize-early", "minimize-late"])
        win_mac_layout.addWidget(self.hide_console_combo, 0, 1)

        # --disable-windowed-traceback
        self.disable_windowed_traceback_checkbox = QCheckBox("禁用窗口回溯 (--disable-windowed-traceback)")
        win_mac_layout.addWidget(self.disable_windowed_traceback_checkbox, 1, 0)

        layout.addWidget(win_mac_group)

        # Windows特定选项
        windows_group = QGroupBox("Windows特定选项")
        windows_layout = QGridLayout(windows_group)

        # --version-file
        version_file_label = QLabel("版本文件 (--version-file):")
        windows_layout.addWidget(version_file_label, 0, 0)
        self.version_file_edit = QLineEdit()
        self.version_file_edit.setPlaceholderText("版本文件路径...")
        windows_layout.addWidget(self.version_file_edit, 0, 1)

        # --manifest
        manifest_label = QLabel("清单文件 (--manifest):")
        windows_layout.addWidget(manifest_label, 1, 0)
        self.manifest_edit = QLineEdit()
        self.manifest_edit.setPlaceholderText("清单文件路径...")
        windows_layout.addWidget(self.manifest_edit, 1, 1)

        # --resource
        resource_label = QLabel("资源文件 (--resource):")
        windows_layout.addWidget(resource_label, 2, 0)
        self.resource_edit = QLineEdit()
        self.resource_edit.setPlaceholderText("资源文件路径...")
        windows_layout.addWidget(self.resource_edit, 2, 1)

        # --uac-admin
        self.uac_admin_checkbox = QCheckBox("UAC管理员 (--uac-admin)")
        windows_layout.addWidget(self.uac_admin_checkbox, 3, 0)

        # --uac-uiaccess
        self.uac_uiaccess_checkbox = QCheckBox("UAC UI访问 (--uac-uiaccess)")
        windows_layout.addWidget(self.uac_uiaccess_checkbox, 4, 0)

        layout.addWidget(windows_group)

        # macOS X特定选项
        macos_group = QGroupBox("macOS X特定选项")
        macos_layout = QGridLayout(macos_group)

        # --argv-emulation
        self.argv_emulation_checkbox = QCheckBox("ARGV模拟 (--argv-emulation)")
        macos_layout.addWidget(self.argv_emulation_checkbox, 0, 0)

        # --osx-bundle-identifier
        bundle_id_label = QLabel("Bundle标识符 (--osx-bundle-identifier):")
        macos_layout.addWidget(bundle_id_label, 1, 0)
        self.bundle_id_edit = QLineEdit()
        self.bundle_id_edit.setPlaceholderText("com.example.app...")
        macos_layout.addWidget(self.bundle_id_edit, 1, 1)

        # --target-architecture
        target_arch_label = QLabel("目标架构 (--target-architecture):")
        macos_layout.addWidget(target_arch_label, 2, 0)
        self.target_arch_combo = QComboBox()
        self.target_arch_combo.addItems(["", "x86_64", "arm64", "universal2"])
        macos_layout.addWidget(self.target_arch_combo, 2, 1)

        # --codesign-identity
        codesign_label = QLabel("代码签名身份 (--codesign-identity):")
        macos_layout.addWidget(codesign_label, 3, 0)
        self.codesign_edit = QLineEdit()
        self.codesign_edit.setPlaceholderText("代码签名身份...")
        macos_layout.addWidget(self.codesign_edit, 3, 1)

        # --osx-entitlements-file
        entitlements_label = QLabel("授权文件 (--osx-entitlements-file):")
        macos_layout.addWidget(entitlements_label, 4, 0)
        self.entitlements_edit = QLineEdit()
        self.entitlements_edit.setPlaceholderText("授权文件路径...")
        macos_layout.addWidget(self.entitlements_edit, 4, 1)

        layout.addWidget(macos_group)

        # 特殊选项
        special_group = QGroupBox("特殊选项")
        special_layout = QGridLayout(special_group)

        # --runtime-tmpdir
        runtime_tmpdir_label = QLabel("运行时临时目录 (--runtime-tmpdir):")
        special_layout.addWidget(runtime_tmpdir_label, 0, 0)
        self.runtime_tmpdir_edit = QLineEdit()
        self.runtime_tmpdir_edit.setPlaceholderText("临时目录路径...")
        special_layout.addWidget(self.runtime_tmpdir_edit, 0, 1)

        # --bootloader-ignore-signals
        self.bootloader_ignore_signals_checkbox = QCheckBox("引导加载器忽略信号 (--bootloader-ignore-signals)")
        special_layout.addWidget(self.bootloader_ignore_signals_checkbox, 1, 0, 1, 2)

        layout.addWidget(special_group)

        # 其它选项
        other_group = QGroupBox("其它选项")
        other_layout = QGridLayout(other_group)

        # -m
        module_label = QLabel("模块模式 (-m):")
        other_layout.addWidget(module_label, 0, 0)
        self.module_edit = QLineEdit()
        self.module_edit.setPlaceholderText("模块名...")
        other_layout.addWidget(self.module_edit, 0, 1)

        layout.addWidget(other_group)

        layout.addStretch()
        scroll_area.setWidget(scroll_content_widget)
        main_advanced_layout = QVBoxLayout(advanced_widget)
        main_advanced_layout.addWidget(scroll_area)
        self.tab_widget.addTab(advanced_widget, "高级")

        self.name_edit.textChanged.connect(self.update_command)
        self.contents_dir_edit.textChanged.connect(self.update_command)
        self.upx_checkbox.toggled.connect(self.update_command)
        self.upx_dir_edit.textChanged.connect(self.update_command)
        self.clean_checkbox.toggled.connect(self.update_command)
        self.log_level_combo.currentTextChanged.connect(self.update_command)

        self.add_binary_edit.textChanged.connect(self.update_command)
        self.paths_edit.textChanged.connect(self.update_command)
        self.hidden_import_edit.textChanged.connect(self.update_command)
        self.collect_submodules_edit.textChanged.connect(self.update_command)
        self.collect_data_edit.textChanged.connect(self.update_command)
        self.collect_binaries_edit.textChanged.connect(self.update_command)
        self.collect_all_edit.textChanged.connect(self.update_command)
        self.copy_metadata_edit.textChanged.connect(self.update_command)
        self.recursive_copy_metadata_edit.textChanged.connect(self.update_command)
        self.hooks_dir_edit.textChanged.connect(self.update_command)
        self.runtime_hook_edit.textChanged.connect(self.update_command)
        self.exclude_module_edit.textChanged.connect(self.update_command)
        self.splash_edit.textChanged.connect(self.update_command)

        self.debug_combo.currentTextChanged.connect(self.update_command)
        self.optimize_combo.currentTextChanged.connect(self.update_command)
        self.python_option_edit.textChanged.connect(self.update_command)
        self.strip_checkbox.toggled.connect(self.update_command)
        self.noupx_checkbox.toggled.connect(self.update_command)
        self.upx_exclude_edit.textChanged.connect(self.update_command)

        self.hide_console_combo.currentTextChanged.connect(self.update_command)
        self.disable_windowed_traceback_checkbox.toggled.connect(self.update_command)

        self.version_file_edit.textChanged.connect(self.update_command)
        self.manifest_edit.textChanged.connect(self.update_command)
        self.resource_edit.textChanged.connect(self.update_command)
        self.uac_admin_checkbox.toggled.connect(self.update_command)
        self.uac_uiaccess_checkbox.toggled.connect(self.update_command)

        self.argv_emulation_checkbox.toggled.connect(self.update_command)
        self.bundle_id_edit.textChanged.connect(self.update_command)
        self.target_arch_combo.currentTextChanged.connect(self.update_command)
        self.codesign_edit.textChanged.connect(self.update_command)
        self.entitlements_edit.textChanged.connect(self.update_command)

        self.runtime_tmpdir_edit.textChanged.connect(self.update_command)
        self.bootloader_ignore_signals_checkbox.toggled.connect(self.update_command)

        self.module_edit.textChanged.connect(self.update_command)

    def create_module_tab(self):
        """模块设置选项卡"""
        module_widget = QWidget()
        layout = QVBoxLayout(module_widget)

        # 常规
        general_settings_group = QGroupBox("常规设置")
        general_settings_layout = QVBoxLayout(general_settings_group)
        self.use_ast_checkbox = QCheckBox("使用AST检测依赖")
        self.use_ast_checkbox.setChecked(self.use_ast_detection)
        self.use_ast_checkbox.toggled.connect(lambda state: setattr(self, 'use_ast_detection', state))
        general_settings_layout.addWidget(self.use_ast_checkbox)
        self.use_pyinstaller_detection_checkbox = QCheckBox("使用PyInstaller分析检测依赖")
        self.use_pyinstaller_detection_checkbox.setChecked(self.use_pyinstaller_detection)
        self.use_pyinstaller_detection_checkbox.toggled.connect(
            lambda state: setattr(self, 'use_pyinstaller_detection', state))
        general_settings_layout.addWidget(self.use_pyinstaller_detection_checkbox)

        layout.addWidget(general_settings_group)

        # 模块检测与配置
        module_detection_group = QGroupBox("模块检测与配置")
        module_detection_layout = QVBoxLayout(module_detection_group)

        self.detected_modules_list = QListWidget()
        self.detected_modules_list.setToolTip("显示检测到的模块及其路径, 双击可添加到隐藏导入")
        self.detected_modules_list.itemDoubleClicked.connect(self.add_selected_as_hidden_import)
        module_detection_layout.addWidget(self.detected_modules_list)
        module_buttons_layout = QHBoxLayout()
        detect_modules_btn = QPushButton("检测所需模块")
        detect_modules_btn.clicked.connect(self.detect_required_modules)
        module_buttons_layout.addWidget(detect_modules_btn)
        add_hidden_import_btn = QPushButton("添加为隐藏导入")
        add_hidden_import_btn.clicked.connect(self.add_selected_as_hidden_import)
        module_buttons_layout.addWidget(add_hidden_import_btn)
        module_buttons_layout.addStretch()
        module_detection_layout.addLayout(module_buttons_layout)

        layout.addWidget(module_detection_group)

        # layout.addStretch()
        self.tab_widget.addTab(module_widget, "模块设置")

    def create_settings_tab(self):
        """打包设置选项卡"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # PyInstaller设置
        pyinstaller_settings_group = QGroupBox("PyInstaller设置")
        pyinstaller_settings_layout = QHBoxLayout(pyinstaller_settings_group)

        check_pyinstaller_btn = QPushButton("检查PyInstaller")
        check_pyinstaller_btn.clicked.connect(self.check_pyinstaller)
        pyinstaller_settings_layout.addWidget(check_pyinstaller_btn)
        install_pyinstaller_btn = QPushButton("安装PyInstaller")
        install_pyinstaller_btn.clicked.connect(self.install_pyinstaller)
        pyinstaller_settings_layout.addWidget(install_pyinstaller_btn)
        uninstall_pyinstaller_btn = QPushButton("卸载PyInstaller")
        uninstall_pyinstaller_btn.clicked.connect(self.uninstall_pyinstaller)
        pyinstaller_settings_layout.addWidget(uninstall_pyinstaller_btn)
        pyinstaller_settings_layout.addStretch()
        layout.addWidget(pyinstaller_settings_group)

        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QGridLayout(output_group)

        output_dir_label = QLabel("输出目录:")
        output_layout.addWidget(output_dir_label, 0, 0)

        self.output_dir_edit = QLineEdit("./dist")
        output_layout.addWidget(self.output_dir_edit, 0, 1)

        output_browse_btn = QPushButton("浏览")
        output_browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(output_browse_btn, 0, 2)

        self.open_output_folder_checkbox = QCheckBox("打包完成后打开输出文件夹")
        self.open_output_folder_checkbox.setChecked(True)
        output_layout.addWidget(self.open_output_folder_checkbox, 1, 0, 1, 3)

        # 附加参数
        args_label = QLabel("附加参数:")
        output_layout.addWidget(args_label, 2, 0)

        self.additional_args_edit = QLineEdit()
        self.additional_args_edit.setPlaceholderText("其他PyInstaller参数...")
        output_layout.addWidget(self.additional_args_edit, 2, 1, 1, 2)

        layout.addWidget(output_group)

        # 配置管理
        config_group = QGroupBox("配置管理")
        config_layout = QHBoxLayout(config_group)

        default_config_btn = QPushButton("恢复默认配置")
        default_config_btn.clicked.connect(self.restore_default_config)
        config_layout.addWidget(default_config_btn)
        import_config_btn = QPushButton("导入配置")
        import_config_btn.clicked.connect(self.import_config)
        config_layout.addWidget(import_config_btn)
        export_config_btn = QPushButton("导出配置")
        export_config_btn.clicked.connect(self.export_config)
        config_layout.addWidget(export_config_btn)

        config_layout.addStretch()

        layout.addWidget(config_group)

        layout.addStretch()

        self.tab_widget.addTab(settings_widget, "打包设置")

        self.output_dir_edit.textChanged.connect(self.update_command)
        self.additional_args_edit.textChanged.connect(self.update_command)

    def create_log_tab(self):
        """打包日志选项卡"""
        log_widget = QWidget()
        layout = QVBoxLayout(log_widget)

        # 日志显示
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 日志控制按钮
        log_buttons_layout = QHBoxLayout()

        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.clicked.connect(self.clear_log)
        log_buttons_layout.addWidget(clear_log_btn)

        save_log_btn = QPushButton("保存日志")
        save_log_btn.clicked.connect(self.save_log)
        log_buttons_layout.addWidget(save_log_btn)

        log_buttons_layout.addStretch()

        layout.addLayout(log_buttons_layout)

        self.tab_widget.addTab(log_widget, "打包日志")

    def create_bottom_buttons(self, layout):
        """底部按钮"""
        buttons_layout = QHBoxLayout()

        self.package_btn = QPushButton("开始打包")
        self.package_btn.clicked.connect(self.start_package)
        self.package_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.package_btn.setMinimumHeight(40)

        self.stop_btn = QPushButton("停止打包")
        self.stop_btn.clicked.connect(self.stop_package)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.stop_btn.setMinimumHeight(40)

        buttons_layout.addWidget(self.package_btn)
        buttons_layout.addWidget(self.stop_btn)

        layout.addLayout(buttons_layout)

    def center_window(self):
        """窗口居中显示"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def browse_script(self):
        """浏览脚本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Python脚本", "", "Python文件 (*.py)"
        )
        if file_path:
            self.script_path_edit.setText(file_path)

    def browse_icon(self):
        """浏览图标文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图标文件", "", "图标文件 (*.ico *.png)"
        )
        if file_path:
            self.icon_path_edit.setText(file_path)

    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir_edit.setText(dir_path)

    def browse_upx_dir(self):
        """浏览UPX目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择UPX可执行文件目录")
        if dir_path:
            self.upx_dir_edit.setText(dir_path)

    def add_file(self):
        """添加文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择要添加的文件")
        if file_path:
            # self.files_list.addItem(f"文件: {file_path}")
            reply = QMessageBox.question(self, '目标路径',
                                         '是否需要指定目标路径？\n选择"是"可以自定义文件在打包后的位置',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                dest_path, ok = QInputDialog.getText(self, '目标路径',
                                                     '请输入目标路径(相对于程序根目录): ',
                                                     text=os.path.basename(file_path))
                if ok and dest_path:
                    self.files_list.addItem(f"文件: {file_path}:{dest_path}")
                else:
                    self.files_list.addItem(f"文件: {file_path}")
            else:
                self.files_list.addItem(f"文件: {file_path}")

    def add_directory(self):
        """添加目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择要添加的目录")
        if dir_path:
            # self.files_list.addItem(f"目录: {dir_path}")
            reply = QMessageBox.question(self, '目标路径',
                                         '是否需要指定目标路径？\n选择"是"可以自定义目录在打包后的位置',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                dest_path, ok = QInputDialog.getText(self, '目标路径',
                                                     '请输入目标路径(相对于程序根目录): ',
                                                     text=os.path.basename(dir_path.rstrip('/\\')))
                if ok and dest_path:
                    self.files_list.addItem(f"目录: {dir_path}:{dest_path}")
                else:
                    self.files_list.addItem(f"目录: {dir_path}")
            else:
                self.files_list.addItem(f"目录: {dir_path}")

    def remove_file(self):
        """删除选中的文件"""
        current_row = self.files_list.currentRow()
        if current_row >= 0:
            self.files_list.takeItem(current_row)

    def update_command(self):
        """更新命令显示"""
        # 更新packer对象
        self.packer.script_path = self.script_path_edit.text()
        self.packer.icon_path = self.icon_path_edit.text()
        self.packer.output_dir = self.output_dir_edit.text()
        self.packer.additional_args = self.additional_args_edit.text()

        self.packer.is_one_file = self.onefile_radio.isChecked()
        self.packer.is_windowed = self.windowed_radio.isChecked()
        self.packer.enable_upx = self.upx_checkbox.isChecked()

        self.packer.additional_files = []
        self.packer.additional_dirs = []
        for i in range(self.files_list.count()):
            item_text = self.files_list.item(i).text()
            if item_text.startswith("文件: "):
                self.packer.additional_files.append(item_text.replace("文件: ", ""))
            elif item_text.startswith("目录: "):
                self.packer.additional_dirs.append(item_text.replace("目录: ", ""))

        self.packer.name = self.name_edit.text()
        self.packer.contents_directory = self.contents_dir_edit.text()
        self.packer.upx_dir = self.upx_dir_edit.text()
        self.packer.clean = self.clean_checkbox.isChecked()
        self.packer.log_level = self.log_level_combo.currentText()

        self.packer.add_binary = self.add_binary_edit.text()
        self.packer.paths = self.paths_edit.text()
        self.packer.hidden_import = self.hidden_import_edit.text()
        self.packer.collect_submodules = self.collect_submodules_edit.text()
        self.packer.collect_data = self.collect_data_edit.text()
        self.packer.collect_binaries = self.collect_binaries_edit.text()
        self.packer.collect_all = self.collect_all_edit.text()
        self.packer.copy_metadata = self.copy_metadata_edit.text()
        self.packer.recursive_copy_metadata = self.recursive_copy_metadata_edit.text()
        self.packer.hooks_dir = self.hooks_dir_edit.text()
        self.packer.runtime_hook = self.runtime_hook_edit.text()
        self.packer.exclude_module = self.exclude_module_edit.text()
        self.packer.splash = self.splash_edit.text()

        self.packer.debug = self.debug_combo.currentText()
        self.packer.optimize = self.optimize_combo.currentText()
        self.packer.python_option = self.python_option_edit.text()
        self.packer.strip = self.strip_checkbox.isChecked()
        self.packer.noupx = not self.noupx_checkbox.isChecked()
        self.packer.upx_exclude = self.upx_exclude_edit.text()

        self.packer.hide_console = self.hide_console_combo.currentText()
        self.packer.disable_windowed_traceback = self.disable_windowed_traceback_checkbox.isChecked()

        self.packer.version_file = self.version_file_edit.text()
        self.packer.manifest = self.manifest_edit.text()
        self.packer.resource = self.resource_edit.text()
        self.packer.uac_admin = self.uac_admin_checkbox.isChecked()
        self.packer.uac_uiaccess = self.uac_uiaccess_checkbox.isChecked()

        self.packer.argv_emulation = self.argv_emulation_checkbox.isChecked()
        self.packer.osx_bundle_identifier = self.bundle_id_edit.text()
        self.packer.target_architecture = self.target_arch_combo.currentText()
        self.packer.codesign_identity = self.codesign_edit.text()
        self.packer.osx_entitlements_file = self.entitlements_edit.text()

        self.packer.runtime_tmpdir = self.runtime_tmpdir_edit.text()
        self.packer.bootloader_ignore_signals = self.bootloader_ignore_signals_checkbox.isChecked()

        self.packer.module = self.module_edit.text()

        # 生成并显示命令
        command = self.packer.generate_command()
        self.cli_command_edit.setText(command)

    def start_package(self):
        """开始打包"""
        if not self.script_path_edit.text():
            QMessageBox.warning(self, "警告", "请先选择Python脚本文件")
            return

        if not self.check_and_install_pyinstaller():
            self.log_text.append("\nPyInstaller未安装或安装失败, 打包中止")
            QMessageBox.critical(self, "错误", "PyInstaller未安装或安装失败, 无法继续打包")
            return

        command = self.packer.generate_command()
        if not command:
            QMessageBox.warning(self, "警告", "无法生成打包命令")
            return

        self.log_text.clear()
        self.log_text.append(f"开始打包: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_text.append(f"执行命令: {command}\n")

        self.package_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        # 无限进度条
        self.progress_bar.setRange(0, 0)

        # 切换到日志选项卡
        self.tab_widget.setCurrentIndex(4)

        # 启动打包线程
        self.package_thread = PackageThread(command)
        self.package_thread.output_signal.connect(self.update_log)
        self.package_thread.finished_signal.connect(self.package_finished)
        self.package_thread.start()

    def stop_package(self):
        """停止打包"""
        if self.package_thread and self.package_thread.isRunning():
            reply = QMessageBox.question(self, '确认停止', '打包正在进行中, 确定要停止吗？',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.package_thread.terminate()
                self.package_thread.wait()
                self.package_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.progress_bar.setVisible(False)
                self.log_text.append("\n打包已停止")
            else:
                return
        else:
            self.log_text.append("\n没有正在进行的打包任务")

    def update_log(self, text):
        """更新日志显示"""
        self.log_text.append(text)
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)

    def package_finished(self, success):
        """打包完成"""
        self.package_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        if success:
            self.log_text.append("\n打包完成")
            QMessageBox.information(self, "成功", "打包完成")

            if hasattr(self, 'open_output_folder_checkbox') and self.open_output_folder_checkbox.isChecked():
                self.open_output_folder()
        else:
            self.log_text.append("\n打包失败")
            QMessageBox.warning(self, "失败", "打包失败, 请查看日志")

    def clear_log(self):
        """清空日志"""
        self.log_text.clear()

    def save_log(self):
        """保存日志"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "文本文件 (*.txt)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
            QMessageBox.information(self, "成功", "日志已保存")

    def clear_configuration(self):
        """清空配置"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有配置吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.clear_all_fields()
            self.set_default_values()
            QMessageBox.information(self, "成功", "所有配置已清空并恢复默认设置")

    def import_config(self):
        """导入配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入配置", "", "JSON文件 (*.json);;所有文件 (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.load_config(config)
                QMessageBox.information(self, "成功", "配置已成功导入")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入配置失败: {str(e)}")

    def export_config(self):
        """导出配置"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置", f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "JSON文件 (*.json);;所有文件 (*.*)"
        )
        if file_path:
            try:
                config = self.get_config()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                QMessageBox.information(self, "成功", "配置已成功导出")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出配置失败: {str(e)}")

    def get_config(self):
        """获取当前UI配置为字典"""
        config = {
            "script_path": self.script_path_edit.text(),
            "output_dir": self.output_dir_edit.text(),
            "icon_path": self.icon_path_edit.text(),
            "additional_files": [self.files_list.item(i).text() for i in range(self.files_list.count())],
            "is_one_file": self.onefile_radio.isChecked(),
            "is_windowed": self.windowed_radio.isChecked(),
            "name": self.name_edit.text(),
            "contents_directory": self.contents_dir_edit.text(),
            "enable_upx": self.upx_checkbox.isChecked(),
            "upx_dir": self.upx_dir_edit.text(),
            "clean": self.clean_checkbox.isChecked(),
            "log_level": self.log_level_combo.currentText(),
            "add_binary": self.add_binary_edit.text(),
            "paths": self.paths_edit.text(),
            "hidden_import": self.hidden_import_edit.text(),
            "collect_submodules": self.collect_submodules_edit.text(),
            "collect_data": self.collect_data_edit.text(),
            "collect_binaries": self.collect_binaries_edit.text(),
            "collect_all": self.collect_all_edit.text(),
            "copy_metadata": self.copy_metadata_edit.text(),
            "recursive_copy_metadata": self.recursive_copy_metadata_edit.text(),
            "hooks_dir": self.hooks_dir_edit.text(),
            "runtime_hook": self.runtime_hook_edit.text(),
            "exclude_module": self.exclude_module_edit.text(),
            "splash": self.splash_edit.text(),
            "debug": self.debug_combo.currentText(),
            "optimize": self.optimize_combo.currentText(),
            "python_option": self.python_option_edit.text(),
            "strip": self.strip_checkbox.isChecked(),
            "noupx": self.noupx_checkbox.isChecked(),
            "upx_exclude": self.upx_exclude_edit.text(),
            "hide_console": self.hide_console_combo.currentText(),
            "disable_windowed_traceback": self.disable_windowed_traceback_checkbox.isChecked(),
            "version_file": self.version_file_edit.text(),
            "manifest": self.manifest_edit.text(),
            "resource": self.resource_edit.text(),
            "uac_admin": self.uac_admin_checkbox.isChecked(),
            "uac_uiaccess": self.uac_uiaccess_checkbox.isChecked(),
            "argv_emulation": self.argv_emulation_checkbox.isChecked(),
            "osx_bundle_identifier": self.bundle_id_edit.text(),
            "target_architecture": self.target_arch_combo.currentText(),
            "codesign_identity": self.codesign_edit.text(),
            "osx_entitlements_file": self.entitlements_edit.text(),
            "runtime_tmpdir": self.runtime_tmpdir_edit.text(),
            "bootloader_ignore_signals": self.bootloader_ignore_signals_checkbox.isChecked(),
            "module": self.module_edit.text(),
            "additional_args": self.additional_args_edit.text(),
            "open_output_folder": self.open_output_folder_checkbox.isChecked(),
            "use_ast_detection": self.use_ast_checkbox.isChecked(),
            "use_pyinstaller_detection": self.use_pyinstaller_detection_checkbox.isChecked(),
        }
        return config

    def load_config(self, config):
        """从字典加载配置到UI"""
        self.clear_all_fields()

        self.script_path_edit.setText(config.get("script_path", ""))
        self.output_dir_edit.setText(config.get("output_dir", "./dist"))
        self.icon_path_edit.setText(config.get("icon_path", ""))

        self.files_list.clear()
        for item_text in config.get("additional_files", []):
            self.files_list.addItem(item_text)

        self.onefile_radio.setChecked(config.get("is_one_file", True))
        self.onedir_radio.setChecked(not config.get("is_one_file", True))
        self.console_radio.setChecked(not config.get("is_windowed", False))
        self.windowed_radio.setChecked(config.get("is_windowed", False))

        self.name_edit.setText(config.get("name", ""))
        self.contents_dir_edit.setText(config.get("contents_directory", ""))
        self.upx_checkbox.setChecked(config.get("enable_upx", False))
        self.upx_dir_edit.setText(config.get("upx_dir", ""))
        self.clean_checkbox.setChecked(config.get("clean", False))
        self.log_level_combo.setCurrentText(config.get("log_level", ""))

        self.add_binary_edit.setText(config.get("add_binary", ""))
        self.paths_edit.setText(config.get("paths", ""))
        self.hidden_import_edit.setText(config.get("hidden_import", ""))
        self.collect_submodules_edit.setText(config.get("collect_submodules", ""))
        self.collect_data_edit.setText(config.get("collect_data", ""))
        self.collect_binaries_edit.setText(config.get("collect_binaries", ""))
        self.collect_all_edit.setText(config.get("collect_all", ""))
        self.copy_metadata_edit.setText(config.get("copy_metadata", ""))
        self.recursive_copy_metadata_edit.setText(config.get("recursive_copy_metadata", ""))
        self.hooks_dir_edit.setText(config.get("hooks_dir", ""))
        self.runtime_hook_edit.setText(config.get("runtime_hook", ""))
        self.exclude_module_edit.setText(config.get("exclude_module", ""))
        self.splash_edit.setText(config.get("splash", ""))

        self.debug_combo.setCurrentText(config.get("debug", ""))
        self.optimize_combo.setCurrentText(config.get("optimize", ""))
        self.python_option_edit.setText(config.get("python_option", ""))
        self.strip_checkbox.setChecked(config.get("strip", False))
        self.noupx_checkbox.setChecked(config.get("noupx", False))
        self.upx_exclude_edit.setText(config.get("upx_exclude", ""))

        self.hide_console_combo.setCurrentText(config.get("hide_console", ""))
        self.disable_windowed_traceback_checkbox.setChecked(config.get("disable_windowed_traceback", False))

        self.version_file_edit.setText(config.get("version_file", ""))
        self.manifest_edit.setText(config.get("manifest", ""))
        self.resource_edit.setText(config.get("resource", ""))
        self.uac_admin_checkbox.setChecked(config.get("uac_admin", False))
        self.uac_uiaccess_checkbox.setChecked(config.get("uac_uiaccess", False))

        self.argv_emulation_checkbox.setChecked(config.get("argv_emulation", False))
        self.bundle_id_edit.setText(config.get("osx_bundle_identifier", ""))
        self.target_arch_combo.setCurrentText(config.get("target_architecture", ""))
        self.codesign_edit.setText(config.get("codesign_identity", ""))
        self.entitlements_edit.setText(config.get("osx_entitlements_file", ""))

        self.runtime_tmpdir_edit.setText(config.get("runtime_tmpdir", ""))
        self.bootloader_ignore_signals_checkbox.setChecked(config.get("bootloader_ignore_signals", False))

        self.module_edit.setText(config.get("module", ""))
        self.additional_args_edit.setText(config.get("additional_args", ""))
        self.open_output_folder_checkbox.setChecked(config.get("open_output_folder", True))

        self.use_ast_checkbox.setChecked(config.get("use_ast_detection", True))
        self.use_pyinstaller_detection_checkbox.setChecked(config.get("use_pyinstaller_detection", False))

        self.update_command()

    def restore_default_config(self):
        """恢复默认配置"""
        reply = QMessageBox.question(self, '确认', '确定要恢复默认配置吗？这将清空所有当前设置',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.clear_all_fields()
            self.set_default_values()
            QMessageBox.information(self, '成功', '已恢复默认配置')

    def set_default_values(self):
        """设置默认值"""
        self.open_output_folder_checkbox.setChecked(True)
        self.additional_args_edit.clear()
        self.detected_modules_list.clear()

        self.script_path_edit.clear()
        self.icon_path_edit.clear()
        self.output_dir_edit.setText("./dist")
        self.files_list.clear()
        self.onefile_radio.setChecked(True)
        self.console_radio.setChecked(True)
        self.upx_checkbox.setChecked(False)
        self.name_edit.clear()
        self.contents_dir_edit.clear()
        self.upx_checkbox.setChecked(False)
        self.upx_dir_edit.clear()
        self.clean_checkbox.setChecked(False)
        self.log_level_combo.setCurrentText("")

        self.add_binary_edit.clear()
        self.paths_edit.clear()
        self.hidden_import_edit.clear()
        self.collect_submodules_edit.clear()
        self.collect_data_edit.clear()
        self.collect_binaries_edit.clear()
        self.collect_all_edit.clear()
        self.copy_metadata_edit.clear()
        self.recursive_copy_metadata_edit.clear()
        self.hooks_dir_edit.clear()
        self.runtime_hook_edit.clear()
        self.exclude_module_edit.clear()
        self.splash_edit.clear()

        self.debug_combo.setCurrentText("")
        self.optimize_combo.setCurrentText("")
        self.python_option_edit.clear()
        self.strip_checkbox.setChecked(False)
        self.noupx_checkbox.setChecked(False)
        self.upx_exclude_edit.clear()

        self.hide_console_combo.setCurrentText("")
        self.disable_windowed_traceback_checkbox.setChecked(False)

        self.version_file_edit.clear()
        self.manifest_edit.clear()
        self.resource_edit.clear()
        self.uac_admin_checkbox.setChecked(False)
        self.uac_uiaccess_checkbox.setChecked(False)

        self.argv_emulation_checkbox.setChecked(False)
        self.bundle_id_edit.clear()
        self.target_arch_combo.setCurrentText("")
        self.codesign_edit.clear()
        self.entitlements_edit.clear()

        self.runtime_tmpdir_edit.clear()
        self.bootloader_ignore_signals_checkbox.setChecked(False)

        self.module_edit.clear()

        self.use_ast_checkbox.setChecked(True)
        self.use_pyinstaller_detection_checkbox.setChecked(False)

        self.update_command()

    def clear_all_fields(self):
        """清空所有字段"""
        # 基本选项
        self.script_path_edit.clear()
        self.icon_path_edit.clear()
        self.files_list.clear()

        # 设置默认单选按钮
        self.onefile_radio.setChecked(True)
        self.console_radio.setChecked(True)

        # 高级选项
        self.name_edit.clear()
        self.contents_dir_edit.clear()
        self.upx_checkbox.setChecked(False)
        self.upx_dir_edit.clear()
        self.clean_checkbox.setChecked(False)
        self.log_level_combo.setCurrentText("")

        # 捆绑选项
        self.add_binary_edit.clear()
        self.paths_edit.clear()
        self.hidden_import_edit.clear()
        self.collect_submodules_edit.clear()
        self.collect_data_edit.clear()
        self.collect_binaries_edit.clear()
        self.collect_all_edit.clear()
        self.copy_metadata_edit.clear()
        self.recursive_copy_metadata_edit.clear()
        self.hooks_dir_edit.clear()
        self.runtime_hook_edit.clear()
        self.exclude_module_edit.clear()
        self.splash_edit.clear()

        # 生成选项
        self.debug_combo.setCurrentText("")
        self.optimize_combo.setCurrentText("")
        self.python_option_edit.clear()
        self.strip_checkbox.setChecked(False)
        self.noupx_checkbox.setChecked(False)
        self.upx_exclude_edit.clear()

        # Windows和macOS选项
        self.hide_console_combo.setCurrentText("")
        self.disable_windowed_traceback_checkbox.setChecked(False)

        # Windows特定选项
        self.version_file_edit.clear()
        self.manifest_edit.clear()
        self.resource_edit.clear()
        self.uac_admin_checkbox.setChecked(False)
        self.uac_uiaccess_checkbox.setChecked(False)

        # macOS特定选项
        self.argv_emulation_checkbox.setChecked(False)
        self.bundle_id_edit.clear()
        self.target_arch_combo.setCurrentText("")
        self.codesign_edit.clear()
        self.entitlements_edit.clear()

        # 特殊选项
        self.runtime_tmpdir_edit.clear()
        self.bootloader_ignore_signals_checkbox.setChecked(False)

        # 其他选项
        self.module_edit.clear()

        # 设置选项
        self.additional_args_edit.clear()

        # 模块检测
        self.detected_modules_list.clear()
        self.use_ast_checkbox.setChecked(True)
        self.use_pyinstaller_detection_checkbox.setChecked(False)

        self.update_command()

    def open_output_folder(self):
        """打开输出文件夹"""
        import os
        import subprocess
        import platform

        output_dir = self.output_dir_edit.text() or "./dist"
        if os.path.exists(output_dir):
            try:
                # if sys.platform == "win32":
                if platform.system() == "Windows":
                    os.startfile(output_dir)
                # elif sys.platform == "darwin":
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", output_dir])
                else:
                    subprocess.Popen(["xdg-open", output_dir])
            except Exception as e:
                QMessageBox.warning(self, "警告", f"无法打开输出文件夹: {str(e)}")
        else:
            QMessageBox.warning(self, "警告", f"输出文件夹不存在: {output_dir}")

    def check_pyinstaller_installed(self):
        """检查PyInstaller是否已安装"""
        try:
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            result = subprocess.run(
                [sys.executable, "-m", "PyInstaller", "--version"],
                capture_output=True, text=True, check=True, creationflags=creationflags
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
        except Exception as e:
            self.log_text.append(f"检查PyInstaller时发生错误: {e}")
            return False

    def check_pyinstaller(self):
        """检查PyInstaller"""
        self.log_text.append(f"正在检查PyInstaller: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.check_pyinstaller_installed():
            try:
                creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                result = subprocess.run(
                    [sys.executable, "-m", "PyInstaller", "--version"],
                    capture_output=True, text=True, check=True, creationflags=creationflags
                )
                QMessageBox.information(
                    self, "PyInstaller检查",
                    f"PyInstaller已安装\n版本: {result.stdout.strip()}"
                )
                self.log_text.append(f"PyInstaller已安装, 版本: {result.stdout.strip()}")
            except Exception as e:
                QMessageBox.warning(
                    self, "PyInstaller检查",
                    f"PyInstaller已安装, 但获取版本信息失败: {str(e)}"
                )
                self.log_text.append(f"PyInstaller已安装, 但获取版本信息失败: {str(e)}")
        else:
            QMessageBox.warning(
                self, "PyInstaller检查",
                "PyInstaller未正确安装或不在当前Python环境中"
            )
            self.log_text.append("PyInstaller未正确安装或不在当前Python环境中")

    def install_pyinstaller(self):
        """安装PyInstaller"""
        if self.check_pyinstaller_installed():
            QMessageBox.information(self, "安装PyInstaller", "PyInstaller已安装")
            self.log_text.append("PyInstaller已安装, 无需再次安装")
            return

        reply = QMessageBox.question(
            self, "安装PyInstaller",
            "PyInstaller未安装, 确定要安装PyInstaller吗？这可能需要一些时间",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.log_text.append(f"尝试安装PyInstaller: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                process = subprocess.Popen(
                    [sys.executable, "-m", "pip", "install", "PyInstaller"],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=creationflags
                )
                for line in iter(process.stdout.readline, ''):
                    self.update_log(line.strip())
                process.wait()

                if process.returncode == 0:
                    QMessageBox.information(self, "安装成功", "PyInstaller已成功安装")
                    self.log_text.append("PyInstaller安装成功")
                else:
                    QMessageBox.warning(self, "安装失败", "PyInstaller安装失败, 请查看日志")
                    self.log_text.append("PyInstaller安装失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"安装过程中发生错误: {str(e)}")
                self.log_text.append(f"安装过程中发生错误: {str(e)}")

    def uninstall_pyinstaller(self):
        """卸载PyInstaller"""
        if not self.check_pyinstaller_installed():
            QMessageBox.information(self, "卸载PyInstaller", "PyInstaller未安装")
            self.log_text.append("PyInstaller未安装, 无需卸载")
            return

        reply = QMessageBox.question(
            self, "卸载PyInstaller",
            "PyInstaller已安装, 确定要卸载PyInstaller吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.log_text.append(f"尝试卸载PyInstaller: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                process = subprocess.Popen(
                    [sys.executable, "-m", "pip", "uninstall", "-y", "PyInstaller"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=creationflags
                )
                for line in iter(process.stdout.readline, ''):
                    self.update_log(line.strip())
                process.wait()

                if process.returncode == 0:
                    QMessageBox.information(self, "卸载成功", "PyInstaller已成功卸载")
                    self.log_text.append("PyInstaller卸载成功")
                else:
                    QMessageBox.warning(self, "卸载失败", "PyInstaller卸载失败, 请查看日志")
                    self.log_text.append("PyInstaller卸载失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"卸载过程中发生错误: {str(e)}")
                self.log_text.append(f"卸载过程中发生错误: {str(e)}")

    def check_and_install_pyinstaller(self):
        """在打包前检查并安装PyInstaller"""
        if self.check_pyinstaller_installed():
            self.log_text.append("PyInstaller已安装, 继续打包")
            return True
        else:
            self.log_text.append("PyInstaller未安装, 尝试安装...")
            self.install_pyinstaller()
            if self.check_pyinstaller_installed():
                self.log_text.append("PyInstaller安装成功")
                return True
            else:
                self.log_text.append("PyInstaller无法安装")
                return False

    def detect_required_modules(self):
        """
        尝试检测Python脚本所需的模块
        """
        script_path = self.script_path_edit.text()
        if not script_path or not os.path.exists(script_path):
            QMessageBox.warning(self, "警告", "请先选择一个有效的Python脚本文件")
            return

        if not self.use_ast_detection and not self.use_pyinstaller_detection:
            QMessageBox.warning(self, "警告", "请至少选择一种模块检测方法(AST或PyInstaller)")
            return

        self.detected_modules_list.clear()
        self.log_text.append(f"正在检测 '{os.path.basename(script_path)}' 的所需模块...")

        all_detected_modules = set()

        # AST
        if self.use_ast_detection:
            try:
                self.log_text.append("正在使用AST解析检测模块...")
                with open(script_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=script_path)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            all_detected_modules.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            all_detected_modules.add(node.module.split('.')[0])
                self.log_text.append(f"AST解析检测到 {len(all_detected_modules)} 个模块")
            except Exception as e:
                self.log_text.append(f"AST解析模块时发生错误: {e}")

        # PyInstaller
        if self.use_pyinstaller_detection:
            try:
                self.log_text.append("正在尝试运行 PyInstaller --debug imports 获取更多依赖信息...")
                temp_spec_dir = os.path.join(os.path.dirname(script_path), "__pyinstaller_tmp__")
                os.makedirs(temp_spec_dir, exist_ok=True)
                # temp_spec_file = os.path.join(temp_spec_dir, "temp_spec.spec")

                pyinstaller_cmd = [
                    sys.executable, "-m", "PyInstaller",
                    "--noconfirm",
                    "--debug", "imports",
                    "--specpath", temp_spec_dir,
                    "--workpath", os.path.join(temp_spec_dir, "build"),
                    "--distpath", os.path.join(temp_spec_dir, "dist"),
                    "--clean",
                    script_path
                ]
                creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                process = subprocess.Popen(
                    pyinstaller_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=creationflags
                )
                pyinstaller_output = []
                for line in iter(process.stdout.readline, ''):
                    pyinstaller_output.append(line.strip())
                    self.update_log(f"[PyInstaller Debug]: {line.strip()}")
                process.wait()

                for line in pyinstaller_output:
                    if "Imported module:" in line:
                        try:
                            parts = line.split("Imported module:", 1)
                            if len(parts) > 1:
                                module_info = parts[1].strip().split(' ')[0]
                                module_name = module_info.split('(')[0].strip()
                                if module_name and not module_name.startswith('_pyi_'):
                                    all_detected_modules.add(module_name.split('.')[0])
                        except Exception as e:
                            self.log_text.append(f"解析PyInstaller调试输出时错误: {e}, Line: {line}")

                import shutil
                if os.path.exists(temp_spec_dir):
                    shutil.rmtree(temp_spec_dir)
                    self.log_text.append(f"已清理临时目录: {temp_spec_dir}")
            except Exception as e:
                self.log_text.append(f"运行 PyInstaller --debug imports 时发生错误: {str(e)}")
                if "No module named PyInstaller" in str(e):
                    self.log_text.append("PyInstaller可能未安装, 请尝试安装")
                QMessageBox.warning(self, "错误", f"检测模块时发生错误: {str(e)}\n请检查PyInstaller是否安装")
                return

        if not all_detected_modules:
            self.log_text.append("未检测到明显的导入模块")
            QMessageBox.information(self, "模块检测", "未检测到明显的导入模块")
            return
        self.log_text.append("检测到以下模块: ")
        self.detected_modules_list.clear()
        for module_name in sorted(list(all_detected_modules)):
            try:
                spec = importlib.util.find_spec(module_name)
                if spec and spec.origin:
                    self.detected_modules_list.addItem(f"{module_name} (路径: {os.path.dirname(spec.origin)})")
                    self.log_text.append(f"  - {module_name} (路径: {os.path.dirname(spec.origin)})")
                else:
                    self.detected_modules_list.addItem(f"{module_name} (未找到安装路径或内置模块)")
                    self.log_text.append(f"  - {module_name} (未找到安装路径或内置模块)")
            except Exception as e:
                self.detected_modules_list.addItem(f"{module_name} (加载失败: {e})")
                self.log_text.append(f"  - {module_name} (加载失败: {e})")

        QMessageBox.information(self, "模块检测", "模块检测完成, 请查看\"模块检测与配置\"列表和日志")
        self.tab_widget.setCurrentIndex(2)

    def add_selected_as_hidden_import(self):
        """将选中的模块添加到隐藏导入列表"""
        selected_items = self.detected_modules_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先在列表中选择要添加的模块")
            return

        current_hidden_imports = self.hidden_import_edit.text().split(',')
        if current_hidden_imports == ['']:
            current_hidden_imports = []

        new_hidden_imports = []
        for item in selected_items:
            module_name = item.text().split(' ')[0]
            if module_name not in current_hidden_imports:
                new_hidden_imports.append(module_name)

        if new_hidden_imports:
            updated_hidden_imports = current_hidden_imports + new_hidden_imports
            self.hidden_import_edit.setText(",".join(filter(None, updated_hidden_imports)))
            QMessageBox.information(self, "成功", "选中的模块已添加到隐藏导入")
        else:
            QMessageBox.information(self, "提示", "所有选中的模块都已在隐藏导入列表中")

    def show_settings(self):
        """显示设置对话框"""
        QMessageBox.information(self, "设置", "设置对话框功能待实现")

    def show_about(self):
        """显示关于对话框"""
        try:
            about_dialog = AboutDialog(self)
            about_dialog.exec_()
        except ImportError:
            QMessageBox.information(
                self, "关于",
                "PyInstaller打包工具 v1.0.1\n\n"
                "作者: xuyou & xiaomizha\n"
                "基于PyQt5开发"
            )

    def open_donate_page(self):
        webbrowser.open("https://github.com/xuyouer")

    def open_contact_page(self):
        webbrowser.open("https://github.com/xuyouer")

    def open_homepage(self):
        webbrowser.open("https://github.com/xuyouer")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("PyInstaller打包工具")
    app.setApplicationVersion("1.0.1")
    app.setOrganizationName("xuyou & xiaomizha")

    window = PyInstallerPackerGUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
