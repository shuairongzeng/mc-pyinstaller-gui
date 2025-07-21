"""
打包日志标签页
"""
from typing import Optional
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QProgressBar, QGroupBox, QCheckBox
)
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QFont, QTextCursor

class LogTab(QWidget):
    """打包日志标签页"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_auto_scroll()
    
    def init_ui(self) -> None:
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 日志控制组
        control_group = self.create_control_group()
        layout.addWidget(control_group)
        
        # 命令预览组
        preview_group = self.create_preview_group()
        layout.addWidget(preview_group, 0)  # 不给stretch，保持紧凑

        # 日志输出组
        log_group = self.create_log_group()
        layout.addWidget(log_group, 1)  # 给日志组分配主要空间
        
        # 进度信息
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel("准备就绪")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addLayout(progress_layout)
    
    def create_control_group(self) -> QGroupBox:
        """创建日志控制组"""
        group = QGroupBox("日志控制")
        layout = QHBoxLayout(group)
        
        # 清空日志按钮
        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.clicked.connect(self.clear_log)
        layout.addWidget(self.clear_log_btn)
        
        # 保存日志按钮
        self.save_log_btn = QPushButton("保存日志")
        self.save_log_btn.clicked.connect(self.save_log)
        layout.addWidget(self.save_log_btn)
        
        # 自动滚动选项
        self.auto_scroll_checkbox = QCheckBox("自动滚动")
        self.auto_scroll_checkbox.setChecked(True)
        layout.addWidget(self.auto_scroll_checkbox)
        
        # 显示时间戳选项
        self.show_timestamp_checkbox = QCheckBox("显示时间戳")
        self.show_timestamp_checkbox.setChecked(True)
        layout.addWidget(self.show_timestamp_checkbox)
        
        layout.addStretch()
        
        return group
    
    def create_preview_group(self) -> QGroupBox:
        """创建命令预览组"""
        group = QGroupBox("命令预览")
        layout = QVBoxLayout(group)

        self.command_preview = QTextEdit()
        self.command_preview.setReadOnly(True)
        # 移除最大高度限制，让预览框能够更好地适应内容
        self.command_preview.setMinimumHeight(60)  # 设置最小高度确保基本可用性
        # 设置合理的最大高度，避免占用过多空间
        self.command_preview.setMaximumHeight(120)
        # 设置大小策略
        from PyQt5.QtWidgets import QSizePolicy
        self.command_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.command_preview.setPlaceholderText("生成的PyInstaller命令将在这里显示...")

        # 设置等宽字体
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.command_preview.setFont(font)

        layout.addWidget(self.command_preview)

        return group
    
    def create_log_group(self) -> QGroupBox:
        """创建日志输出组"""
        group = QGroupBox("打包日志")
        layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("打包日志将在这里显示...")
        
        # 设置等宽字体
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.log_text.setFont(font)
        
        layout.addWidget(self.log_text)
        
        return group
    
    def setup_auto_scroll(self) -> None:
        """设置自动滚动"""
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.scroll_to_bottom)
        self.scroll_timer.setSingleShot(True)
    
    @pyqtSlot(str)
    def append_log(self, message: str) -> None:
        """添加日志消息"""
        if not message.strip():
            return
        
        # 添加时间戳
        if self.show_timestamp_checkbox.isChecked():
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
        else:
            formatted_message = message
        
        # 添加到日志
        self.log_text.append(formatted_message)
        
        # 自动滚动
        if self.auto_scroll_checkbox.isChecked():
            self.scroll_timer.start(100)  # 延迟100ms滚动，避免频繁滚动
    
    @pyqtSlot()
    def scroll_to_bottom(self) -> None:
        """滚动到底部"""
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @pyqtSlot()
    def clear_log(self) -> None:
        """清空日志"""
        self.log_text.clear()
        self.progress_label.setText("日志已清空")
    
    @pyqtSlot()
    def save_log(self) -> None:
        """保存日志到文件"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", f"pyinstaller_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, "成功", f"日志已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存日志失败: {str(e)}")
    
    def update_command_preview(self, command: str) -> None:
        """更新命令预览"""
        if command:
            self.command_preview.setPlainText(command)
        else:
            self.command_preview.setPlainText("无法生成命令，请检查配置")

    def update_progress(self, progress: int) -> None:
        """更新进度 - 兼容旧接口"""
        self.set_progress(progress)
    
    def set_progress(self, value: int, maximum: int = 100) -> None:
        """设置进度"""
        if maximum > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, maximum)
            self.progress_bar.setValue(value)
        else:
            self.progress_bar.setVisible(False)
    
    def set_progress_text(self, text: str) -> None:
        """设置进度文本"""
        self.progress_label.setText(text)
    
    def show_progress(self, show: bool = True) -> None:
        """显示/隐藏进度条"""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # 不确定进度
    
    def log_info(self, message: str) -> None:
        """记录信息日志"""
        self.append_log(f"[INFO] {message}")
    
    def log_warning(self, message: str) -> None:
        """记录警告日志"""
        self.append_log(f"[WARNING] {message}")
    
    def log_error(self, message: str) -> None:
        """记录错误日志"""
        self.append_log(f"[ERROR] {message}")
    
    def log_success(self, message: str) -> None:
        """记录成功日志"""
        self.append_log(f"[SUCCESS] {message}")
    
    def start_packaging_ui(self) -> None:
        """开始打包时的UI更新"""
        self.show_progress(True)
        self.set_progress_text("正在打包...")
        self.log_info("开始打包过程")
    
    def finish_packaging_ui(self, success: bool, message: str = "") -> None:
        """完成打包时的UI更新"""
        self.show_progress(False)
        if success:
            self.set_progress_text("打包完成")
            self.log_success("打包成功完成")
            if message:
                self.log_info(message)
        else:
            self.set_progress_text("打包失败")
            self.log_error(f"打包失败: {message}")
    
    def cancel_packaging_ui(self) -> None:
        """取消打包时的UI更新"""
        self.show_progress(False)
        self.set_progress_text("打包已取消")
        self.log_warning("打包过程已被用户取消")
