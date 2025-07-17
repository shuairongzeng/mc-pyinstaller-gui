"""
打包设置标签页
"""
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QFileDialog, QCheckBox, 
    QTextEdit, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot

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
