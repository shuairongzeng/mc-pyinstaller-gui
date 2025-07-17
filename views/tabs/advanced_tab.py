"""
高级设置标签页
"""
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QFileDialog, QCheckBox, 
    QComboBox, QTextEdit, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel

class AdvancedTab(QWidget):
    """高级设置标签页"""
    
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
        
        # 基本高级选项组
        basic_group = self.create_basic_advanced_group()
        layout.addWidget(basic_group)
        
        # UPX压缩组
        upx_group = self.create_upx_group()
        layout.addWidget(upx_group)
        
        # 模块选项组
        module_group = self.create_module_group()
        layout.addWidget(module_group)
        
        # 附加参数组
        args_group = self.create_args_group()
        layout.addWidget(args_group)
        
        layout.addStretch()
    
    def create_basic_advanced_group(self) -> QGroupBox:
        """创建基本高级选项组"""
        group = QGroupBox("基本高级选项")
        layout = QGridLayout(group)
        
        # 应用程序名称
        layout.addWidget(QLabel("应用程序名称:"), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("自定义应用程序名称（可选）")
        layout.addWidget(self.name_edit, 0, 1)
        
        # 内容目录
        layout.addWidget(QLabel("内容目录:"), 1, 0)
        self.contents_dir_edit = QLineEdit()
        self.contents_dir_edit.setPlaceholderText("指定内容目录名称（可选）")
        layout.addWidget(self.contents_dir_edit, 1, 1)
        
        # 清理构建
        self.clean_checkbox = QCheckBox("清理构建缓存")
        self.clean_checkbox.setToolTip("在构建前清理PyInstaller缓存和临时文件")
        layout.addWidget(self.clean_checkbox, 2, 0, 1, 2)
        
        # 日志级别
        layout.addWidget(QLabel("日志级别:"), 3, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        layout.addWidget(self.log_level_combo, 3, 1)
        
        return group
    
    def create_upx_group(self) -> QGroupBox:
        """创建UPX压缩组"""
        group = QGroupBox("UPX压缩")
        layout = QGridLayout(group)
        
        # 启用UPX
        self.upx_checkbox = QCheckBox("启用UPX压缩")
        self.upx_checkbox.setToolTip("使用UPX压缩可执行文件以减小体积")
        layout.addWidget(self.upx_checkbox, 0, 0, 1, 2)
        
        # UPX目录
        layout.addWidget(QLabel("UPX目录:"), 1, 0)
        self.upx_dir_edit = QLineEdit()
        self.upx_dir_edit.setPlaceholderText("UPX可执行文件所在目录（可选）")
        layout.addWidget(self.upx_dir_edit, 1, 1)
        
        self.browse_upx_btn = QPushButton("浏览...")
        self.browse_upx_btn.clicked.connect(self.browse_upx_dir)
        layout.addWidget(self.browse_upx_btn, 1, 2)
        
        return group
    
    def create_module_group(self) -> QGroupBox:
        """创建模块选项组"""
        group = QGroupBox("模块选项")
        layout = QVBoxLayout(group)
        
        # 隐藏导入
        hidden_layout = QHBoxLayout()
        hidden_layout.addWidget(QLabel("隐藏导入:"))
        self.hidden_imports_edit = QLineEdit()
        self.hidden_imports_edit.setPlaceholderText("用逗号分隔的模块名，如: numpy,pandas")
        hidden_layout.addWidget(self.hidden_imports_edit)
        layout.addLayout(hidden_layout)
        
        # 排除模块
        exclude_layout = QHBoxLayout()
        exclude_layout.addWidget(QLabel("排除模块:"))
        self.exclude_modules_edit = QLineEdit()
        self.exclude_modules_edit.setPlaceholderText("用逗号分隔的要排除的模块名")
        exclude_layout.addWidget(self.exclude_modules_edit)
        layout.addLayout(exclude_layout)
        
        # 路径
        paths_layout = QHBoxLayout()
        paths_layout.addWidget(QLabel("搜索路径:"))
        self.paths_edit = QLineEdit()
        self.paths_edit.setPlaceholderText("额外的模块搜索路径，用分号分隔")
        paths_layout.addWidget(self.paths_edit)
        layout.addLayout(paths_layout)
        
        return group
    
    def create_args_group(self) -> QGroupBox:
        """创建附加参数组"""
        group = QGroupBox("附加参数")
        layout = QVBoxLayout(group)
        
        layout.addWidget(QLabel("自定义PyInstaller参数:"))
        self.additional_args_edit = QTextEdit()
        self.additional_args_edit.setPlaceholderText(
            "输入额外的PyInstaller命令行参数，每行一个参数\n"
            "例如:\n"
            "--add-data src;dest\n"
            "--collect-all package_name\n"
            "--runtime-hook hook.py"
        )
        self.additional_args_edit.setMaximumHeight(100)
        layout.addWidget(self.additional_args_edit)
        
        return group
    
    def connect_signals(self) -> None:
        """连接信号槽"""
        self.name_edit.textChanged.connect(self.on_name_changed)
        self.contents_dir_edit.textChanged.connect(self.on_contents_dir_changed)
        self.clean_checkbox.toggled.connect(self.on_clean_toggled)
        self.log_level_combo.currentTextChanged.connect(self.on_log_level_changed)
        self.upx_checkbox.toggled.connect(self.on_upx_toggled)
        self.upx_dir_edit.textChanged.connect(self.on_upx_dir_changed)
        self.hidden_imports_edit.textChanged.connect(self.on_hidden_imports_changed)
        self.exclude_modules_edit.textChanged.connect(self.on_exclude_modules_changed)
        self.paths_edit.textChanged.connect(self.on_paths_changed)
        self.additional_args_edit.textChanged.connect(self.on_additional_args_changed)
    
    @pyqtSlot()
    def browse_upx_dir(self) -> None:
        """浏览UPX目录"""
        from PyQt5.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(self, "选择UPX目录")
        if dir_path:
            self.upx_dir_edit.setText(dir_path)
    
    @pyqtSlot(str)
    def on_name_changed(self, text: str) -> None:
        """应用程序名称变更"""
        self.model.name = text
        self.config_changed.emit()
    
    @pyqtSlot(str)
    def on_contents_dir_changed(self, text: str) -> None:
        """内容目录变更"""
        self.model.contents_directory = text
        self.config_changed.emit()
    
    @pyqtSlot(bool)
    def on_clean_toggled(self, checked: bool) -> None:
        """清理构建选项变更"""
        self.model.clean = checked
        self.config_changed.emit()
    
    @pyqtSlot(str)
    def on_log_level_changed(self, text: str) -> None:
        """日志级别变更"""
        self.model.log_level = text
        self.config_changed.emit()
    
    @pyqtSlot(bool)
    def on_upx_toggled(self, checked: bool) -> None:
        """UPX选项变更"""
        self.model.enable_upx = checked
        self.config_changed.emit()
    
    @pyqtSlot(str)
    def on_upx_dir_changed(self, text: str) -> None:
        """UPX目录变更"""
        self.model.upx_dir = text
        self.config_changed.emit()
    
    @pyqtSlot(str)
    def on_hidden_imports_changed(self, text: str) -> None:
        """隐藏导入变更"""
        if text.strip():
            self.model.hidden_imports = [m.strip() for m in text.split(',') if m.strip()]
        else:
            self.model.hidden_imports = []
        self.config_changed.emit()
    
    @pyqtSlot(str)
    def on_exclude_modules_changed(self, text: str) -> None:
        """排除模块变更"""
        self.model.exclude_module = text
        self.config_changed.emit()
    
    @pyqtSlot(str)
    def on_paths_changed(self, text: str) -> None:
        """搜索路径变更"""
        self.model.paths = text
        self.config_changed.emit()
    
    @pyqtSlot()
    def on_additional_args_changed(self) -> None:
        """附加参数变更"""
        self.model.additional_args = self.additional_args_edit.toPlainText()
        self.config_changed.emit()
    
    def refresh_ui(self) -> None:
        """刷新界面"""
        # 更新基本选项
        self.name_edit.setText(self.model.name)
        self.contents_dir_edit.setText(self.model.contents_directory)
        self.clean_checkbox.setChecked(self.model.clean)
        if self.model.log_level:
            self.log_level_combo.setCurrentText(self.model.log_level)
        
        # 更新UPX选项
        self.upx_checkbox.setChecked(self.model.enable_upx)
        self.upx_dir_edit.setText(self.model.upx_dir)
        
        # 更新模块选项
        if self.model.hidden_imports:
            self.hidden_imports_edit.setText(','.join(self.model.hidden_imports))
        self.exclude_modules_edit.setText(self.model.exclude_module)
        self.paths_edit.setText(self.model.paths)
        
        # 更新附加参数
        self.additional_args_edit.setPlainText(self.model.additional_args)
