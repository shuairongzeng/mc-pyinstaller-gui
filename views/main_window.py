"""
主窗口视图
"""
import os
import subprocess
import platform
from typing import Optional
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QMessageBox, QProgressBar, QTextEdit, QPushButton, QHBoxLayout,
    QApplication, QDesktopWidget, QFrame, QLabel
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

    def __init__(self, config=None, model=None, controller=None):
        super().__init__()
        self.config = config if config is not None else AppConfig()
        self.model = model if model is not None else PyInstallerModel(self.config)
        self.controller = controller
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

        # 创建顶部工具栏
        self.create_toolbar(layout)

        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 创建各个标签页
        self.create_tabs()

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

    def create_toolbar(self, layout: QVBoxLayout) -> None:
        """创建顶部工具栏"""
        # 创建工具栏容器
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        toolbar_frame.setLineWidth(1)
        toolbar_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                margin: 2px;
                padding: 4px;
            }
        """)

        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(8, 6, 8, 6)
        toolbar_layout.setSpacing(8)

        # 生成命令按钮
        self.generate_cmd_btn = QPushButton("🔧 生成命令")
        self.generate_cmd_btn.clicked.connect(self.generate_command)
        self.generate_cmd_btn.setToolTip("根据当前配置生成PyInstaller命令")
        self.generate_cmd_btn.setStyleSheet(self._get_button_style("#4CAF50"))
        toolbar_layout.addWidget(self.generate_cmd_btn)

        # 开始打包按钮
        self.start_package_btn = QPushButton("▶️ 开始打包")
        self.start_package_btn.clicked.connect(self.start_package)
        self.start_package_btn.setToolTip("开始执行打包过程")
        self.start_package_btn.setStyleSheet(self._get_button_style("#2196F3"))
        toolbar_layout.addWidget(self.start_package_btn)

        # 取消打包按钮
        self.cancel_package_btn = QPushButton("⏹️ 取消打包")
        self.cancel_package_btn.clicked.connect(self.cancel_package)
        self.cancel_package_btn.setEnabled(False)
        self.cancel_package_btn.setToolTip("取消正在进行的打包过程")
        self.cancel_package_btn.setStyleSheet(self._get_button_style("#FF9800"))
        toolbar_layout.addWidget(self.cancel_package_btn)

        # 清空配置按钮
        self.clear_config_btn = QPushButton("🗑️ 清空配置")
        self.clear_config_btn.clicked.connect(self.clear_config)
        self.clear_config_btn.setToolTip("清空所有配置项，恢复默认设置")
        self.clear_config_btn.setStyleSheet(self._get_button_style("#f44336"))
        toolbar_layout.addWidget(self.clear_config_btn)

        # 添加弹性空间，让按钮靠左对齐
        toolbar_layout.addStretch()

        # 添加状态指示器（可选）
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 4px 8px;
                background-color: #e8e8e8;
                border-radius: 10px;
            }
        """)
        toolbar_layout.addWidget(self.status_label)

        layout.addWidget(toolbar_frame)

    def _get_button_style(self, color: str) -> str:
        """获取按钮样式"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.8)};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """

    def _darken_color(self, color: str, factor: float = 0.9) -> str:
        """使颜色变暗"""
        # 简单的颜色变暗处理
        color_map = {
            "#4CAF50": "#45a049" if factor == 0.9 else "#3d8b40",
            "#2196F3": "#1976D2" if factor == 0.9 else "#1565C0",
            "#FF9800": "#F57C00" if factor == 0.9 else "#E65100",
            "#f44336": "#d32f2f" if factor == 0.9 else "#c62828"
        }
        return color_map.get(color, color)

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
        desktop = QDesktopWidget()
        screen = desktop.screenGeometry()
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
            QMessageBox.warning(self, "错误", "请选择要打包的Python脚本")
            return

        # 检查PyInstaller
        if self.controller and not self.controller.check_pyinstaller_installation():
            python_interpreter = self.config.get("python_interpreter", "")
            env_info = f"在环境 {python_interpreter}" if python_interpreter else "在当前环境"
            reply = QMessageBox.question(
                self, "PyInstaller未安装",
                f"PyInstaller{env_info}中未安装，是否现在安装？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.install_pyinstaller()
            return

        # 切换到日志标签页
        self.tab_widget.setCurrentWidget(self.log_tab)

        # 创建打包服务
        if self.controller:
            self.package_service = self.controller.create_package_service()
        else:
            # 如果没有controller，使用默认方式创建
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
            self.log_tab.append_log(f"打包失败: {message}")
            QMessageBox.critical(self, "失败", f"打包失败: {message}")

    def install_pyinstaller(self) -> None:
        """安装PyInstaller"""
        self.tab_widget.setCurrentWidget(self.log_tab)
        if self.controller:
            success = self.controller.install_pyinstaller(self.log_tab.append_log)
        else:
            # 如果没有controller，使用默认方式安装
            success = PyInstallerChecker.install_pyinstaller(self.log_tab.append_log)

        if success:
            QMessageBox.information(self, "成功", "PyInstaller安装成功！")
        else:
            QMessageBox.critical(self, "失败", "PyInstaller安装失败！")

    def open_output_folder(self) -> None:
        """打开输出文件夹"""
        output_dir = self.model.output_dir

        # 转换为绝对路径
        abs_output_dir = os.path.abspath(output_dir)

        # 检查目录是否存在
        if not os.path.exists(abs_output_dir):
            # 如果目录不存在，尝试创建它
            try:
                os.makedirs(abs_output_dir, exist_ok=True)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "警告",
                    f"无法创建输出目录：{abs_output_dir}\n错误：{str(e)}"
                )
                return

        # 打开文件夹
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(abs_output_dir)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", abs_output_dir])
            else:  # Linux
                subprocess.run(["xdg-open", abs_output_dir])
        except Exception as e:
            QMessageBox.warning(
                self,
                "警告",
                f"无法打开输出文件夹：{abs_output_dir}\n错误：{str(e)}\n\n您可以手动打开此路径。"
            )

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
            self.package_service.wait(3000)  # 等待3秒

        event.accept()