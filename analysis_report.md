"""
主窗口视图
"""
from typing import Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QMessageBox, QProgressBar, QTextEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QIcon

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel
from services.package_service import PackageService, PyInstallerChecker
from services.module_detector import ModuleDetector
from views.tabs.basic_tab import BasicTab
from views.tabs.advanced_tab import AdvancedTab
from views.tabs.module_tab import ModuleTab
from views.tabs.settings_tab import SettingsTab
from views.tabs.log_tab import LogTab
from views.menu_bar import MenuBarManager
from about_dialog import AboutDialog

class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.config = AppConfig()
        self.model = PyInstallerModel(self.config)
        self.package_service: Optional[PackageService] = None
        self.module_detector = ModuleDetector(
            use_ast=self.config.get("use_ast_detection", True),
            use_pyinstaller=self.config.get("use_pyinstaller_detection", False)
        )

        # 标签页组件
        self.basic_tab: Optional[BasicTab] = None
        self.advanced_tab: Optional[AdvancedTab] = None
        self.module_tab: Optional[ModuleTab] = None
        self.settings_tab: Optional[SettingsTab] = None
        self.log_tab: Optional[LogTab] = None

        self.init_ui()
        self.center_window()
        self.connect_signals()

    def init_ui(self) -> None:
        """初始化用户界面"""
        self.setWindowTitle(f"{AppConfig.APP_NAME} v{AppConfig.APP_VERSION}")
        self.setMinimumSize(800, 1000)

        # 设置图标
        if hasattr(self, 'setWindowIcon'):
            try:
                self.setWindowIcon(QIcon("icon.png"))
            except:
                pass

        # 创建菜单栏
        self.menu_manager = MenuBarManager(self)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 创建各个标签页
        self.create_tabs()

        # 创建底部按钮
        self.create_bottom_buttons(layout)

    def create_tabs(self) -> None:
        """创建标签页"""
        # 基本设置标签页
        self.basic_tab = BasicTab(self.model, self.config)
        self.tab_widget.addTab(self.basic_tab, "基本设置")

        # 高级设置标签页
        self.advanced_tab = AdvancedTab(self.model, self.config)
        self.tab_widget.addTab(self.advanced_tab, "高级设置")

        # 模块管理标签页
        self.module_tab = ModuleTab(self.model, self.config, self.module_detector)
        self.tab_widget.addTab(self.module_tab, "模块管理")

        # 打包设置标签页
        self.settings_tab = SettingsTab(self.model, self.config)
        self.tab_widget.addTab(self.settings_tab, "打包设置")

        # 打包日志标签页
        self.log_tab = LogTab()
        self.tab_widget.addTab(self.log_tab, "打包日志")

    def create_bottom_buttons(self, layout: QVBoxLayout) -> None:
        """创建底部按钮"""
        button_layout = QHBoxLayout()

        # 生成命令按钮
        self.generate_cmd_btn = QPushButton("生成命令")
        self.generate_cmd_btn.clicked.connect(self.generate_command)
        button_layout.addWidget(self.generate_cmd_btn)

        # 开始打包按钮
        self.start_package_btn = QPushButton("开始打包")
        self.start_package_btn.clicked.connect(self.start_package)
        button_layout.addWidget(self.start_package_btn)

        # 取消打包按钮
        self.cancel_package_btn = QPushButton("取消打包")
        self.cancel_package_btn.clicked.connect(self.cancel_package)
        self.cancel_package_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_package_btn)

        # 清空配置按钮
        self.clear_config_btn = QPushButton("清空配置")
        self.clear_config_btn.clicked.connect(self.clear_config)
        button_layout.addWidget(self.clear_config_btn)

        layout.addLayout(button_layout)

    def connect_signals(self) -> None:
        """连接信号槽"""
        if self.basic_tab:
            self.basic_tab.config_changed.connect(self.on_config_changed)
        if self.advanced_tab:
            self.advanced_tab.config_changed.connect(self.on_config_changed)
        if self.settings_tab:
            self.settings_tab.config_changed.connect(self.on_config_changed)

    def center_window(self) -> None:
        """窗口居中显示"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    @pyqtSlot()
    def on_config_changed(self) -> None:
        """配置变更处理"""
        # 更新命令预览
        if hasattr(self, 'log_tab') and self.log_tab:
            command = self.model.generate_command()
            self.log_tab.update_command_preview(command)

    @pyqtSlot()
    def generate_command(self) -> None:
        """生成打包命令"""
        command = self.model.generate_command()
        if command and self.log_tab:
            self.log_tab.update_command_preview(command)
            QMessageBox.information(self, "命令生成", "打包命令已生成，请查看日志标签页")
        else:
            QMessageBox.warning(self, "错误", "无法生成打包命令，请检查配置")

    @pyqtSlot()
    def start_package(self) -> None:
        """开始打包"""
        # 验证配置
        if not self.model.script_path:
            QMessageBox.warning(self, "错误", "请选择要打包的 Python 脚本")
            return

        # 检查 PyInstaller
        if not PyInstallerChecker.check_pyinstaller():
            reply = QMessageBox.question(
                self, "PyInstaller 未安装",
                "PyInstaller 未安装，是否现在安装？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.install_pyinstaller()
            return

        # 切换到日志标签页
        self.tab_widget.setCurrentWidget(self.log_tab)

        # 创建打包服务
        self.package_service = PackageService(self.model)
        self.package_service.output_signal.connect(self.log_tab.append_log)
        self.package_service.finished_signal.connect(self.on_package_finished)

        # 更新按钮状态
        self.start_package_btn.setEnabled(False)
        self.cancel_package_btn.setEnabled(True)

        # 开始打包
        self.package_service.start()
        self.log_tab.append_log("开始打包...")

    @pyqtSlot()
    def cancel_package(self) -> None:
        """取消打包"""
        if self.package_service:
            self.package_service.cancel()
            self.log_tab.append_log("正在取消打包...")

    @pyqtSlot(bool, str)
    def on_package_finished(self, success: bool, message: str) -> None:
        """打包完成处理"""
        self.start_package_btn.setEnabled(True)
        self.cancel_package_btn.setEnabled(False)

        if success:
            self.log_tab.append_log("打包完成！")
            if self.config.get("open_output_after_build", True):
                self.open_output_folder()
            QMessageBox.information(self, "成功", "打包完成！")
        else:
            self.log_tab.append_log(f"打包失败：{message}")
            QMessageBox.critical(self, "失败", f"打包失败：{message}")

    def install_pyinstaller(self) -> None:
        """安装 PyInstaller"""
        self.tab_widget.setCurrentWidget(self.log_tab)
        success = PyInstallerChecker.install_pyinstaller(self.log_tab.append_log)
        if success:
            QMessageBox.information(self, "成功", "PyInstaller 安装成功！")
        else:
            QMessageBox.critical(self, "失败", "PyInstaller 安装失败！")

    def open_output_folder(self) -> None:
        """打开输出文件夹"""
        import os
        import subprocess
        import platform

        output_dir = self.model.output_dir
        if os.path.exists(output_dir):
            system = platform.system()
            if system == "Windows":
                os.startfile(output_dir)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", output_dir])
            else:  # Linux
                subprocess.run(["xdg-open", output_dir])

    @pyqtSlot()
    def clear_config(self) -> None:
        """清空配置"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有配置吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.model.reset_to_defaults()
            # 刷新所有标签页
            if self.basic_tab:
                self.basic_tab.refresh_ui()
            if self.advanced_tab:
                self.advanced_tab.refresh_ui()
            if self.settings_tab:
                self.settings_tab.refresh_ui()
            if self.log_tab:
                self.log_tab.clear_log()
            QMessageBox.information(self, "完成", "配置已清空")

    def closeEvent(self, event) -> None:
        """窗口关闭事件"""
        # 保存配置
        self.config.save_config()

        # 取消正在进行的打包
        if self.package_service and self.package_service.isRunning():
            self.package_service.cancel()
            self.package_service.wait(3000)  # 等待 3 秒

        event.accept()
</augment_code_snippet>