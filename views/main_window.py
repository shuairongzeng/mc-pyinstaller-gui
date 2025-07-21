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
from services.package_service import PackageService, PyInstallerChecker, AsyncPackageService
from services.module_detector import ModuleDetector
from views.tabs.basic_tab import BasicTab
from views.tabs.advanced_tab import AdvancedTab
from views.tabs.module_tab import ModuleTab
from views.tabs.settings_tab import SettingsTab
from views.tabs.log_tab import LogTab
from views.menu_bar import MenuBarManager
from views.components.error_dialog import show_error_dialog
from about_dialog import AboutDialog

class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self, config=None, model=None, controller=None):
        super().__init__()
        self.config = config if config is not None else AppConfig()
        self.model = model if model is not None else PyInstallerModel(self.config)
        self.controller = controller
        self.package_service: Optional[PackageService] = None
        self.async_package_service: Optional[AsyncPackageService] = None
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
            self.basic_tab.script_selected.connect(self.on_script_selected)
        if self.advanced_tab:
            self.advanced_tab.config_changed.connect(self.on_config_changed)
        if self.settings_tab:
            self.settings_tab.config_changed.connect(self.on_config_changed)
        if self.module_tab:
            self.module_tab.silent_detection_finished.connect(self.on_silent_detection_finished)

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
            python_interpreter = self.config.get("python_interpreter", "")
            command = self.model.generate_command(python_interpreter)
            self.log_tab.update_command_preview(command)

    @pyqtSlot(str)
    def on_script_selected(self, script_path: str) -> None:
        """脚本选择完成处理"""
        self.statusBar().showMessage(f"正在分析脚本: {script_path}")

        # 1. 自动进行智能超时建议
        self._apply_smart_timeout_suggestion(script_path)

        # 2. 自动开始模块检测（静默模式）
        if self.module_tab and self.config.get("auto_detect_modules", True):
            self.statusBar().showMessage("正在后台检测模块...")
            self.module_tab.start_detection(silent=True)

    @pyqtSlot(list, dict)
    def on_silent_detection_finished(self, modules: list, analysis: dict) -> None:
        """静默检测完成处理"""
        module_count = len(modules)
        hidden_count = len(analysis.get('hidden_imports', []))

        # 更新状态栏
        self.statusBar().showMessage(f"检测完成: 发现 {module_count} 个模块，推荐 {hidden_count} 个隐藏导入", 5000)

        # 显示优化的通知对话框
        if self.config.get("show_detection_notification", True):
            self._show_detection_completion_dialog(module_count, hidden_count, analysis)

    def _apply_smart_timeout_suggestion(self, script_path: str) -> None:
        """应用智能超时建议"""
        try:
            suggested_timeout = self.config.suggest_timeout_for_project(script_path)
            current_timeout = self.config.get_package_timeout()

            if suggested_timeout != current_timeout:
                self.config.set_package_timeout(suggested_timeout)
                timeout_text = self.config.format_timeout_display(suggested_timeout)
                self.statusBar().showMessage(f"已自动设置超时时间: {timeout_text}", 3000)

                # 如果设置标签页存在，刷新UI
                if self.settings_tab:
                    self.settings_tab.refresh_ui()
        except Exception as e:
            # 静默处理错误，不影响用户体验
            print(f"智能超时建议失败: {e}")

    def _show_detection_completion_dialog(self, module_count: int, hidden_count: int, analysis: dict) -> None:
        """显示检测完成对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox

        dialog = QDialog(self)
        dialog.setWindowTitle("模块检测完成")
        dialog.setMinimumSize(400, 200)

        layout = QVBoxLayout(dialog)

        # 主要信息
        info_label = QLabel(
            f"✅ 自动检测完成！\n\n"
            f"• 发现模块: {module_count} 个\n"
            f"• 推荐隐藏导入: {hidden_count} 个\n"
            f"• 已自动应用到配置中"
        )
        info_label.setStyleSheet("font-size: 12px; padding: 10px;")
        layout.addWidget(info_label)

        # 框架信息（如果有）
        if 'framework_configs' in analysis and analysis['framework_configs']:
            frameworks = list(analysis['framework_configs'].keys())
            framework_label = QLabel(f"🔍 检测到框架: {', '.join(frameworks)}")
            framework_label.setStyleSheet("color: #2196F3; font-weight: bold;")
            layout.addWidget(framework_label)

        # 选项
        options_layout = QVBoxLayout()

        # 不再显示此通知的选项
        self.dont_show_checkbox = QCheckBox("不再显示此通知")
        options_layout.addWidget(self.dont_show_checkbox)

        layout.addLayout(options_layout)

        # 按钮
        button_layout = QHBoxLayout()

        # 查看详细信息按钮
        detail_btn = QPushButton("查看详细信息")
        detail_btn.clicked.connect(lambda: self._show_module_details(dialog))
        detail_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px 16px; border: none; border-radius: 4px; }")
        button_layout.addWidget(detail_btn)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(lambda: self._close_detection_dialog(dialog))
        close_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; }")
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec_()

    def _show_module_details(self, parent_dialog) -> None:
        """显示模块详细信息"""
        parent_dialog.accept()  # 关闭通知对话框
        # 切换到模块管理标签页
        if self.module_tab:
            self.tab_widget.setCurrentWidget(self.module_tab)

    def _close_detection_dialog(self, dialog) -> None:
        """关闭检测对话框"""
        # 保存用户选择
        if hasattr(self, 'dont_show_checkbox') and self.dont_show_checkbox.isChecked():
            self.config.set("show_detection_notification", False)
        dialog.accept()

    @pyqtSlot()
    def generate_command(self) -> None:
        """生成打包命令"""
        python_interpreter = self.config.get("python_interpreter", "")
        command = self.model.generate_command(python_interpreter)
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

        # 清空上一次的打包日志
        if self.log_tab:
            self.log_tab.clear_log()

        # 切换到日志标签页
        self.tab_widget.setCurrentWidget(self.log_tab)

        # 创建增强的异步打包服务
        python_interpreter = self.config.get("python_interpreter", "")
        timeout = self.config.get("package_timeout", 300)  # 默认5分钟超时

        self.async_package_service = AsyncPackageService(
            self.model,
            python_interpreter,
            timeout
        )

        # 先连接信号回调
        self.async_package_service.connect_signals(
            progress_callback=self.on_progress_updated,
            output_callback=self.on_output_received,  # 使用专门的输出处理方法
            error_callback=self.on_error_occurred,
            finished_callback=self.on_package_finished,
            status_callback=self.on_status_changed,
            remaining_time_callback=self.on_remaining_time_updated,
            timeout_warning_callback=self.on_timeout_warning
        )

        # 更新UI状态
        self.start_package_btn.setEnabled(False)
        self.cancel_package_btn.setEnabled(True)

        # 启动打包UI状态
        self.log_tab.start_packaging_ui()

        # 开始异步打包
        self.log_tab.append_log("正在启动异步打包服务...")
        if self.async_package_service.start_packaging():
            self.log_tab.append_log("✅ 异步打包任务已成功启动")
        else:
            self.log_tab.append_log("❌ 启动打包任务失败")
            self.on_package_finished(False, "启动打包任务失败")

    @pyqtSlot()
    def cancel_package(self) -> None:
        """取消打包"""
        if self.async_package_service:
            self.async_package_service.cancel_packaging()
            self.log_tab.cancel_packaging_ui()
        elif self.package_service:
            self.package_service.cancel()
            self.log_tab.append_log("正在取消打包...")

    @pyqtSlot(int)
    def on_progress_updated(self, progress: int) -> None:
        """进度更新处理"""
        self.log_tab.set_progress(progress)

    @pyqtSlot(str)
    def on_output_received(self, output: str) -> None:
        """输出接收处理"""
        # 确保所有输出都显示在日志中
        self.log_tab.append_log(output)

    @pyqtSlot(str)
    def on_error_occurred(self, error_message: str) -> None:
        """错误发生处理"""
        self.log_tab.log_error(error_message)

    @pyqtSlot(str)
    def on_status_changed(self, status: str) -> None:
        """状态变化处理"""
        self.log_tab.set_progress_text(status)

    @pyqtSlot(str, str, dict)
    def on_global_exception(self, error_type: str, error_message: str, solution: dict = None):
        """处理全局异常"""
        try:
            # 记录异常到日志
            self.log_tab.log_error(f"全局异常: {error_type}: {error_message}")

            # 收集上下文信息
            context = {
                'current_tab': self.tab_widget.currentIndex(),
                'script_path': self.model.script_path,
                'output_dir': self.model.output_dir,
                'is_packaging': hasattr(self, 'async_package_service') and self.async_package_service is not None
            }

            # 显示用户友好的错误对话框
            show_error_dialog(error_type, error_message, context, self)

        except Exception as e:
            # 如果异常处理本身出错，使用简单的消息框
            QMessageBox.critical(self, "系统错误", f"处理异常时出错: {e}\n\n原始错误: {error_type}: {error_message}")

    def handle_operation_error(self, operation: str, error: Exception, suggestions: list = None):
        """处理操作错误的通用方法"""
        try:
            error_type = type(error).__name__
            error_message = str(error)

            # 收集操作上下文
            context = {
                'operation': operation,
                'current_tab': self.tab_widget.currentIndex(),
                'script_path': self.model.script_path,
                'output_dir': self.model.output_dir
            }

            # 显示错误对话框
            show_error_dialog(error_type, error_message, context, self)

        except Exception as dialog_error:
            # 后备方案：使用简单消息框
            QMessageBox.critical(self, "操作失败", f"{operation}失败: {error}")

    def safe_execute_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """安全执行操作，自动处理异常"""
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            self.handle_operation_error(operation_name, e)
            return None

    @pyqtSlot(int)
    def on_remaining_time_updated(self, remaining_seconds: int):
        """剩余时间更新处理"""
        if self.config.get("timeout_show_remaining", True):
            display_time = self.config.format_timeout_display(remaining_seconds)
            status_msg = f"剩余时间: {display_time}"
            self.log_tab.set_progress_text(status_msg)

            # 在日志中显示剩余时间（每分钟显示一次）
            if remaining_seconds % 60 == 0 and remaining_seconds > 0:
                self.log_tab.log_info(f"⏰ 打包剩余时间: {display_time}")

    @pyqtSlot(int)
    def on_timeout_warning(self, remaining_seconds: int):
        """超时警告处理"""
        display_time = self.config.format_timeout_display(remaining_seconds)
        warning_msg = f"⚠️ 超时警告: 剩余时间仅 {display_time}，请耐心等待或考虑增加超时时间"

        # 在日志中显示警告
        self.log_tab.log_warning(warning_msg)

        # 可选：显示系统通知（如果支持）
        try:
            from PyQt5.QtWidgets import QSystemTrayIcon
            if QSystemTrayIcon.isSystemTrayAvailable():
                # 这里可以添加系统托盘通知
                pass
        except ImportError:
            pass

    @pyqtSlot(bool, str)
    def on_package_finished(self, success: bool, message: str) -> None:
        """打包完成处理"""
        # 恢复按钮状态
        self.start_package_btn.setEnabled(True)
        self.cancel_package_btn.setEnabled(False)

        # 更新UI状态
        self.log_tab.finish_packaging_ui(success, message)

        if success:
            if self.config.get("open_output_after_build", True):
                self.open_output_folder()
            QMessageBox.information(self, "成功", "打包完成！")
        else:
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