"""
基本设置标签页
"""
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QFileDialog, QCheckBox,
    QRadioButton, QButtonGroup, QMessageBox, QListWidget
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel

class BasicTab(QWidget):
    """基本设置标签页"""
    
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
        
        # 脚本选择组
        script_group = self.create_script_group()
        layout.addWidget(script_group)
        
        # 打包选项组
        package_group = self.create_package_group()
        layout.addWidget(package_group)
        
        # 图标设置组
        icon_group = self.create_icon_group()
        layout.addWidget(icon_group)
        
        # 附加文件组
        files_group = self.create_files_group()
        layout.addWidget(files_group)
        
        layout.addStretch()
    
    def create_script_group(self) -> QGroupBox:
        """创建脚本选择组"""
        group = QGroupBox("脚本选择")
        layout = QGridLayout(group)
        
        # 脚本路径
        layout.addWidget(QLabel("Python脚本:"), 0, 0)
        self.script_path_edit = QLineEdit()
        self.script_path_edit.setPlaceholderText("选择要打包的Python脚本文件")
        layout.addWidget(self.script_path_edit, 0, 1)
        
        self.browse_script_btn = QPushButton("浏览...")
        self.browse_script_btn.clicked.connect(self.browse_script)
        layout.addWidget(self.browse_script_btn, 0, 2)
        
        return group
    
    def create_package_group(self) -> QGroupBox:
        """创建打包选项组"""
        group = QGroupBox("打包选项")
        layout = QVBoxLayout(group)
        
        # 打包类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("打包类型:"))
        
        self.package_type_group = QButtonGroup()
        self.one_file_radio = QRadioButton("单文件")
        self.one_dir_radio = QRadioButton("单目录")
        
        self.package_type_group.addButton(self.one_file_radio, 0)
        self.package_type_group.addButton(self.one_dir_radio, 1)
        
        type_layout.addWidget(self.one_file_radio)
        type_layout.addWidget(self.one_dir_radio)
        type_layout.addStretch()
        
        layout.addLayout(type_layout)
        
        # 窗口类型
        window_layout = QHBoxLayout()
        window_layout.addWidget(QLabel("窗口类型:"))
        
        self.window_type_group = QButtonGroup()
        self.console_radio = QRadioButton("控制台")
        self.windowed_radio = QRadioButton("窗口")
        
        self.window_type_group.addButton(self.console_radio, 0)
        self.window_type_group.addButton(self.windowed_radio, 1)
        
        window_layout.addWidget(self.console_radio)
        window_layout.addWidget(self.windowed_radio)
        window_layout.addStretch()
        
        layout.addLayout(window_layout)
        
        return group
    
    def create_icon_group(self) -> QGroupBox:
        """创建图标设置组"""
        group = QGroupBox("图标设置")
        layout = QGridLayout(group)
        
        layout.addWidget(QLabel("图标文件:"), 0, 0)
        self.icon_path_edit = QLineEdit()
        self.icon_path_edit.setPlaceholderText("选择图标文件 (.ico, .png)")
        layout.addWidget(self.icon_path_edit, 0, 1)
        
        self.browse_icon_btn = QPushButton("浏览...")
        self.browse_icon_btn.clicked.connect(self.browse_icon)
        layout.addWidget(self.browse_icon_btn, 0, 2)
        
        return group
    
    def create_files_group(self) -> QGroupBox:
        """创建附加文件组"""
        group = QGroupBox("附加文件")
        layout = QVBoxLayout(group)
        
        # 添加文件按钮
        btn_layout = QHBoxLayout()
        self.add_file_btn = QPushButton("添加文件")
        self.add_file_btn.clicked.connect(self.add_file)
        btn_layout.addWidget(self.add_file_btn)
        
        self.add_dir_btn = QPushButton("添加目录")
        self.add_dir_btn.clicked.connect(self.add_directory)
        btn_layout.addWidget(self.add_dir_btn)
        
        self.remove_file_btn = QPushButton("移除选中")
        self.remove_file_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.remove_file_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 文件列表
        self.files_list = QListWidget()
        layout.addWidget(self.files_list)
        
        return group
    
    def connect_signals(self) -> None:
        """连接信号槽"""
        self.script_path_edit.textChanged.connect(self.on_script_path_changed)
        self.icon_path_edit.textChanged.connect(self.on_icon_path_changed)
        self.package_type_group.buttonClicked.connect(self.on_package_type_changed)
        self.window_type_group.buttonClicked.connect(self.on_window_type_changed)
    
    @pyqtSlot()
    def browse_script(self) -> None:
        """浏览脚本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Python脚本", "", "Python文件 (*.py);;所有文件 (*)"
        )
        if file_path:
            self.script_path_edit.setText(file_path)
    
    @pyqtSlot()
    def browse_icon(self) -> None:
        """浏览图标文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图标文件", "", "图标文件 (*.ico *.png);;所有文件 (*)"
        )
        if file_path:
            self.icon_path_edit.setText(file_path)
    
    @pyqtSlot()
    def add_file(self) -> None:
        """添加文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择要添加的文件", "", "所有文件 (*)"
        )
        if file_path:
            self.model.additional_files.append(file_path)
            self.files_list.addItem(f"文件: {file_path}")
            self.config_changed.emit()
    
    @pyqtSlot()
    def add_directory(self) -> None:
        """添加目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择要添加的目录")
        if dir_path:
            self.model.additional_dirs.append(dir_path)
            self.files_list.addItem(f"目录: {dir_path}")
            self.config_changed.emit()
    
    @pyqtSlot()
    def remove_selected(self) -> None:
        """移除选中的文件/目录"""
        current_row = self.files_list.currentRow()
        if current_row >= 0:
            item = self.files_list.takeItem(current_row)
            if item:
                text = item.text()
                if text.startswith("文件: "):
                    file_path = text[4:]  # 移除"文件: "前缀
                    if file_path in self.model.additional_files:
                        self.model.additional_files.remove(file_path)
                elif text.startswith("目录: "):
                    dir_path = text[4:]  # 移除"目录: "前缀
                    if dir_path in self.model.additional_dirs:
                        self.model.additional_dirs.remove(dir_path)
                self.config_changed.emit()
    
    @pyqtSlot(str)
    def on_script_path_changed(self, text: str) -> None:
        """脚本路径变更"""
        self.model.script_path = text
        self.config_changed.emit()
    
    @pyqtSlot(str)
    def on_icon_path_changed(self, text: str) -> None:
        """图标路径变更"""
        self.model.icon_path = text
        self.config_changed.emit()
    
    @pyqtSlot()
    def on_package_type_changed(self) -> None:
        """打包类型变更"""
        self.model.is_one_file = self.one_file_radio.isChecked()
        self.config_changed.emit()
    
    @pyqtSlot()
    def on_window_type_changed(self) -> None:
        """窗口类型变更"""
        self.model.is_windowed = self.windowed_radio.isChecked()
        self.config_changed.emit()
    
    def refresh_ui(self) -> None:
        """刷新界面"""
        # 更新脚本路径
        self.script_path_edit.setText(self.model.script_path)
        
        # 更新图标路径
        self.icon_path_edit.setText(self.model.icon_path)
        
        # 更新打包类型
        if self.model.is_one_file:
            self.one_file_radio.setChecked(True)
        else:
            self.one_dir_radio.setChecked(True)
        
        # 更新窗口类型
        if self.model.is_windowed:
            self.windowed_radio.setChecked(True)
        else:
            self.console_radio.setChecked(True)
        
        # 更新文件列表
        self.files_list.clear()
        for file_path in self.model.additional_files:
            self.files_list.addItem(f"文件: {file_path}")
        for dir_path in self.model.additional_dirs:
            self.files_list.addItem(f"目录: {dir_path}")
