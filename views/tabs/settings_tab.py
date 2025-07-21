"""
打包设置标签页
"""
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QFileDialog, QCheckBox,
    QTextEdit, QMessageBox, QSpinBox, QComboBox, QSlider, QFrame
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel

class SettingsTab(QWidget):
    """打包设置标签页"""
    
    config_changed = pyqtSignal()
    
    def __init__(self, model: PyInstallerModel, config: AppConfig):
        super().__init__()
        self.model = model
        self.config = config
        self.init_ui()
        self.connect_signals()
        self.refresh_ui()
    
    def init_ui(self) -> None:
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 输出设置组
        output_group = self.create_output_group()
        layout.addWidget(output_group)
        
        # 构建选项组
        build_group = self.create_build_group()
        layout.addWidget(build_group)

        # 超时设置组
        timeout_group = self.create_timeout_group()
        layout.addWidget(timeout_group)

        # 命令预览组
        preview_group = self.create_preview_group()
        layout.addWidget(preview_group, 1)  # 给预览组分配更多空间（stretch factor = 1）

        layout.addStretch(0)  # 减少底部stretch的权重
    
    def create_output_group(self) -> QGroupBox:
        """创建输出设置组"""
        group = QGroupBox("输出设置")
        layout = QGridLayout(group)
        
        # 输出目录
        layout.addWidget(QLabel("输出目录:"), 0, 0)
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("打包文件的输出目录")
        layout.addWidget(self.output_dir_edit, 0, 1)
        
        self.browse_output_btn = QPushButton("浏览...")
        self.browse_output_btn.clicked.connect(self.browse_output_dir)
        layout.addWidget(self.browse_output_btn, 0, 2)
        
        # 打包完成后操作
        self.open_output_checkbox = QCheckBox("打包完成后打开输出文件夹")
        self.open_output_checkbox.setChecked(True)
        layout.addWidget(self.open_output_checkbox, 1, 0, 1, 3)
        
        return group
    
    def create_build_group(self) -> QGroupBox:
        """创建构建选项组"""
        group = QGroupBox("构建选项")
        layout = QVBoxLayout(group)
        
        # 清理选项
        self.clean_build_checkbox = QCheckBox("构建前清理缓存")
        self.clean_build_checkbox.setToolTip("清理PyInstaller的构建缓存和临时文件")
        layout.addWidget(self.clean_build_checkbox)
        
        # 调试选项
        self.debug_checkbox = QCheckBox("启用调试模式")
        self.debug_checkbox.setToolTip("生成详细的调试信息")
        layout.addWidget(self.debug_checkbox)
        
        # 优化选项
        self.optimize_checkbox = QCheckBox("启用Python优化")
        self.optimize_checkbox.setToolTip("启用Python字节码优化")
        layout.addWidget(self.optimize_checkbox)
        
        return group

    def create_timeout_group(self) -> QGroupBox:
        """创建超时设置组"""
        group = QGroupBox("超时设置")
        layout = QVBoxLayout(group)

        # 超时时间设置
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("打包超时时间:"))

        # 预设选择下拉框
        self.timeout_preset_combo = QComboBox()
        presets = self.config.get_timeout_presets()
        for name, seconds in presets.items():
            self.timeout_preset_combo.addItem(name, seconds)
        self.timeout_preset_combo.addItem("自定义", -1)
        timeout_layout.addWidget(self.timeout_preset_combo)

        # 自定义时间输入
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(60, 7200)  # 1分钟到2小时
        self.timeout_spinbox.setSuffix(" 秒")
        self.timeout_spinbox.setValue(self.config.get_package_timeout())
        self.timeout_spinbox.setEnabled(False)  # 默认禁用，选择自定义时启用
        timeout_layout.addWidget(self.timeout_spinbox)

        # 时间显示标签
        self.timeout_display_label = QLabel()
        self.timeout_display_label.setStyleSheet("color: #666; font-size: 10px;")
        timeout_layout.addWidget(self.timeout_display_label)

        timeout_layout.addStretch()
        layout.addLayout(timeout_layout)

        # 智能建议按钮
        suggest_layout = QHBoxLayout()
        self.suggest_timeout_btn = QPushButton("🧠 智能建议")
        self.suggest_timeout_btn.setToolTip("根据当前项目复杂度智能推荐超时时间")
        self.suggest_timeout_btn.setMaximumWidth(120)
        suggest_layout.addWidget(self.suggest_timeout_btn)
        suggest_layout.addStretch()
        layout.addLayout(suggest_layout)

        # 超时选项
        options_layout = QVBoxLayout()

        self.timeout_warning_checkbox = QCheckBox("启用超时警告")
        self.timeout_warning_checkbox.setToolTip("在接近超时时显示警告")
        self.timeout_warning_checkbox.setChecked(self.config.get("timeout_warning_enabled", True))
        options_layout.addWidget(self.timeout_warning_checkbox)

        self.show_remaining_checkbox = QCheckBox("显示剩余时间")
        self.show_remaining_checkbox.setToolTip("在打包过程中显示剩余超时时间")
        self.show_remaining_checkbox.setChecked(self.config.get("timeout_show_remaining", True))
        options_layout.addWidget(self.show_remaining_checkbox)

        layout.addLayout(options_layout)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # 说明文本
        info_label = QLabel("💡 提示：大型项目或包含重型依赖（如TensorFlow、PyTorch）的项目建议设置更长的超时时间")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        layout.addWidget(info_label)

        return group

    def create_preview_group(self) -> QGroupBox:
        """创建命令预览组"""
        group = QGroupBox("命令预览")
        layout = QVBoxLayout(group)

        # 预览文本框
        self.command_preview = QTextEdit()
        self.command_preview.setReadOnly(True)
        # 移除最大高度限制，让预览框能够充分利用父容器空间
        self.command_preview.setMinimumHeight(100)  # 设置最小高度确保基本可用性
        # 设置大小策略，让预览框能够扩展
        from PyQt5.QtWidgets import QSizePolicy
        self.command_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.command_preview.setPlaceholderText("生成的PyInstaller命令将在这里显示...")
        layout.addWidget(self.command_preview)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.refresh_preview_btn = QPushButton("刷新预览")
        self.refresh_preview_btn.clicked.connect(self.refresh_command_preview)
        btn_layout.addWidget(self.refresh_preview_btn)
        
        self.copy_command_btn = QPushButton("复制命令")
        self.copy_command_btn.clicked.connect(self.copy_command)
        btn_layout.addWidget(self.copy_command_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return group
    
    def connect_signals(self) -> None:
        """连接信号槽"""
        self.output_dir_edit.textChanged.connect(self.on_output_dir_changed)
        self.open_output_checkbox.toggled.connect(self.on_open_output_toggled)
        self.clean_build_checkbox.toggled.connect(self.on_clean_build_toggled)
        self.debug_checkbox.toggled.connect(self.on_debug_toggled)
        self.optimize_checkbox.toggled.connect(self.on_optimize_toggled)

        # 超时设置信号
        self.timeout_preset_combo.currentIndexChanged.connect(self.on_timeout_preset_changed)
        self.timeout_spinbox.valueChanged.connect(self.on_timeout_value_changed)
        self.suggest_timeout_btn.clicked.connect(self.on_suggest_timeout)
        self.timeout_warning_checkbox.toggled.connect(self.on_timeout_warning_toggled)
        self.show_remaining_checkbox.toggled.connect(self.on_show_remaining_toggled)
    
    @pyqtSlot()
    def browse_output_dir(self) -> None:
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    @pyqtSlot(str)
    def on_output_dir_changed(self, text: str) -> None:
        """输出目录变更"""
        self.model.output_dir = text
        self.config.set("output_dir", text)
        self.config_changed.emit()
    
    @pyqtSlot(bool)
    def on_open_output_toggled(self, checked: bool) -> None:
        """打开输出文件夹选项变更"""
        self.config.set("open_output_after_build", checked)
    
    @pyqtSlot(bool)
    def on_clean_build_toggled(self, checked: bool) -> None:
        """清理构建选项变更"""
        self.model.clean = checked
        self.config.set("clean", checked)
        self.config_changed.emit()
    
    @pyqtSlot(bool)
    def on_debug_toggled(self, checked: bool) -> None:
        """调试选项变更"""
        # 这里可以添加调试相关的模型属性
        self.config_changed.emit()
    
    @pyqtSlot(bool)
    def on_optimize_toggled(self, checked: bool) -> None:
        """优化选项变更"""
        # 这里可以添加优化相关的模型属性
        self.config_changed.emit()

    @pyqtSlot(int)
    def on_timeout_preset_changed(self, index: int) -> None:
        """超时预设选择变更"""
        preset_value = self.timeout_preset_combo.itemData(index)

        if preset_value == -1:  # 自定义选项
            self.timeout_spinbox.setEnabled(True)
            timeout_seconds = self.timeout_spinbox.value()
        else:
            self.timeout_spinbox.setEnabled(False)
            self.timeout_spinbox.setValue(preset_value)
            timeout_seconds = preset_value

        # 更新配置
        self.config.set_package_timeout(timeout_seconds)
        self._update_timeout_display(timeout_seconds)
        self.config_changed.emit()

    @pyqtSlot(int)
    def on_timeout_value_changed(self, value: int) -> None:
        """自定义超时时间变更"""
        if self.timeout_spinbox.isEnabled():  # 只有在自定义模式下才处理
            self.config.set_package_timeout(value)
            self._update_timeout_display(value)
            self.config_changed.emit()

    @pyqtSlot()
    def on_suggest_timeout(self) -> None:
        """智能建议超时时间"""
        try:
            script_path = self.model.script_path
            if not script_path:
                QMessageBox.information(
                    self, "提示",
                    "请先在基本设置中选择要打包的Python脚本，然后再使用智能建议功能。"
                )
                return

            suggested_timeout = self.config.suggest_timeout_for_project(script_path)

            # 找到最接近的预设选项
            presets = self.config.get_timeout_presets()
            best_match = None
            min_diff = float('inf')

            for i, (name, seconds) in enumerate(presets.items()):
                diff = abs(seconds - suggested_timeout)
                if diff < min_diff:
                    min_diff = diff
                    best_match = i

            if best_match is not None and min_diff <= 300:  # 5分钟内的差异认为匹配
                self.timeout_preset_combo.setCurrentIndex(best_match)
            else:
                # 使用自定义选项
                self.timeout_preset_combo.setCurrentIndex(self.timeout_preset_combo.count() - 1)
                self.timeout_spinbox.setValue(suggested_timeout)

            # 显示建议信息
            display_time = self.config.format_timeout_display(suggested_timeout)
            QMessageBox.information(
                self, "智能建议",
                f"根据项目分析，建议设置超时时间为：{display_time}\n\n"
                f"分析依据：\n"
                f"• 项目文件数量\n"
                f"• 依赖库复杂度\n"
                f"• 项目总体大小"
            )

        except Exception as e:
            QMessageBox.warning(self, "错误", f"智能建议功能出错：{str(e)}")

    @pyqtSlot(bool)
    def on_timeout_warning_toggled(self, checked: bool) -> None:
        """超时警告选项变更"""
        self.config.set("timeout_warning_enabled", checked)
        self.config_changed.emit()

    @pyqtSlot(bool)
    def on_show_remaining_toggled(self, checked: bool) -> None:
        """显示剩余时间选项变更"""
        self.config.set("timeout_show_remaining", checked)
        self.config_changed.emit()

    def _update_timeout_display(self, timeout_seconds: int) -> None:
        """更新超时时间显示"""
        display_text = self.config.format_timeout_display(timeout_seconds)
        self.timeout_display_label.setText(f"({display_text})")

    def _find_preset_index_by_value(self, timeout_seconds: int) -> int:
        """根据超时时间值查找预设选项索引"""
        for i in range(self.timeout_preset_combo.count() - 1):  # 排除最后的"自定义"选项
            preset_value = self.timeout_preset_combo.itemData(i)
            if preset_value == timeout_seconds:
                return i
        return self.timeout_preset_combo.count() - 1  # 返回"自定义"选项索引

    def update_timeout_ui_from_config(self) -> None:
        """从配置更新超时相关UI状态"""
        try:
            # 获取当前超时设置
            current_timeout = self.config.get_package_timeout()

            # 查找匹配的预设选项
            preset_index = self._find_preset_index_by_value(current_timeout)

            if preset_index < self.timeout_preset_combo.count() - 1:
                # 找到匹配的预设
                self.timeout_preset_combo.setCurrentIndex(preset_index)
                self.timeout_spinbox.setEnabled(False)
            else:
                # 使用自定义选项
                self.timeout_preset_combo.setCurrentIndex(self.timeout_preset_combo.count() - 1)
                self.timeout_spinbox.setEnabled(True)

            # 设置spinbox值
            self.timeout_spinbox.setValue(current_timeout)

            # 更新显示
            self._update_timeout_display(current_timeout)

            # 更新其他选项
            self.timeout_warning_checkbox.setChecked(self.config.get("timeout_warning_enabled", True))
            self.show_remaining_checkbox.setChecked(self.config.get("timeout_show_remaining", True))

        except Exception as e:
            print(f"更新超时UI状态失败: {e}")

    def refresh_ui(self) -> None:
        """刷新UI状态"""
        # 更新输出目录
        self.output_dir_edit.setText(self.config.get("output_dir", ""))

        # 更新选项状态
        self.open_output_checkbox.setChecked(self.config.get("open_output_after_build", True))
        self.clean_build_checkbox.setChecked(self.config.get("clean", False))
        self.debug_checkbox.setChecked(self.config.get("debug", False))
        self.optimize_checkbox.setChecked(self.config.get("optimize", False))

        # 更新超时设置
        self.update_timeout_ui_from_config()
    
    @pyqtSlot()
    def refresh_command_preview(self) -> None:
        """刷新命令预览"""
        command = self.model.generate_command()
        if command:
            self.command_preview.setPlainText(command)
        else:
            self.command_preview.setPlainText("无法生成命令，请检查配置")
    
    @pyqtSlot()
    def copy_command(self) -> None:
        """复制命令到剪贴板"""
        command = self.command_preview.toPlainText()
        if command and command != "无法生成命令，请检查配置":
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(command)
            QMessageBox.information(self, "完成", "命令已复制到剪贴板")
        else:
            QMessageBox.warning(self, "错误", "没有可复制的命令")
    
    def update_command_preview(self, command: str) -> None:
        """更新命令预览"""
        if command:
            self.command_preview.setPlainText(command)
        else:
            self.command_preview.setPlainText("无法生成命令，请检查配置")
    
    def refresh_ui(self) -> None:
        """刷新界面"""
        # 更新输出目录
        self.output_dir_edit.setText(self.model.output_dir)
        
        # 更新选项
        self.open_output_checkbox.setChecked(
            self.config.get("open_output_after_build", True)
        )
        self.clean_build_checkbox.setChecked(self.model.clean)
        
        # 刷新命令预览
        self.refresh_command_preview()
