"""
用户友好的错误对话框组件
"""
import os
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QScrollArea, QWidget, QFrame, QApplication,
    QProgressBar, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QIcon

from utils.error_diagnostics import get_error_diagnostics, try_auto_fix
from utils.logger import log_info, log_error


class AutoFixWorker(QThread):
    """自动修复工作线程"""
    
    progress_updated = pyqtSignal(int, str)  # 进度, 状态消息
    fix_completed = pyqtSignal(bool, str)    # 成功, 结果消息
    
    def __init__(self, error_type: str, error_message: str, context: Dict[str, Any]):
        super().__init__()
        self.error_type = error_type
        self.error_message = error_message
        self.context = context
    
    def run(self):
        """执行自动修复"""
        try:
            self.progress_updated.emit(10, "正在分析错误...")
            
            # 模拟分析过程
            self.msleep(500)
            self.progress_updated.emit(30, "正在查找解决方案...")
            
            self.msleep(500)
            self.progress_updated.emit(50, "正在应用修复...")
            
            # 执行自动修复
            success, message = try_auto_fix(self.error_type, self.error_message, self.context)
            
            self.progress_updated.emit(90, "正在验证修复结果...")
            self.msleep(300)
            
            self.progress_updated.emit(100, "修复完成")
            self.fix_completed.emit(success, message)
            
        except Exception as e:
            self.fix_completed.emit(False, f"自动修复过程出错: {e}")


class ErrorDialog(QDialog):
    """用户友好的错误对话框"""
    
    def __init__(self, error_type: str, error_message: str, context: Dict[str, Any] = None, parent=None):
        super().__init__(parent)
        self.error_type = error_type
        self.error_message = error_message
        self.context = context or {}
        self.diagnosis = None
        self.auto_fix_worker = None
        
        self.setWindowTitle("错误详情")
        self.setModal(True)
        self.resize(600, 500)
        
        # 获取错误诊断
        self._get_diagnosis()
        
        # 设置UI
        self._setup_ui()
        self._setup_styles()
        
        # 连接信号
        self._connect_signals()
    
    def _get_diagnosis(self):
        """获取错误诊断信息"""
        try:
            diagnostics = get_error_diagnostics()
            self.diagnosis = diagnostics.diagnose_error(self.error_type, self.error_message, self.context)
        except Exception as e:
            log_error(f"获取错误诊断失败: {e}")
            self.diagnosis = {
                'severity': 'medium',
                'category': 'unknown',
                'root_cause': '未知错误',
                'solutions': ['重启程序', '检查日志文件', '联系技术支持'],
                'auto_fix_available': False,
                'prevention_tips': [],
                'related_docs': []
            }
    
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 错误标题区域
        self._create_header_section(layout)
        
        # 错误详情区域
        self._create_details_section(layout)
        
        # 解决方案区域
        self._create_solutions_section(layout)
        
        # 自动修复区域
        if self.diagnosis.get('auto_fix_available', False):
            self._create_auto_fix_section(layout)
        
        # 按钮区域
        self._create_button_section(layout)
    
    def _create_header_section(self, parent_layout):
        """创建错误标题区域"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # 错误图标
        icon_label = QLabel()
        severity = self.diagnosis.get('severity', 'medium')
        icon_path = self._get_severity_icon(severity)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("⚠️")
            icon_label.setStyleSheet("font-size: 32px;")
        
        # 错误信息
        info_layout = QVBoxLayout()
        
        # 错误类型
        error_type_label = QLabel(f"错误类型: {self.error_type}")
        error_type_label.setFont(QFont("", 12, QFont.Bold))
        
        # 根本原因
        root_cause = self.diagnosis.get('root_cause', '未知原因')
        cause_label = QLabel(f"原因: {root_cause}")
        cause_label.setWordWrap(True)
        
        # 严重程度
        severity_text = {'low': '低', 'medium': '中', 'high': '高'}.get(severity, '未知')
        severity_label = QLabel(f"严重程度: {severity_text}")
        severity_color = {'low': '#4CAF50', 'medium': '#FF9800', 'high': '#F44336'}.get(severity, '#757575')
        severity_label.setStyleSheet(f"color: {severity_color}; font-weight: bold;")
        
        info_layout.addWidget(error_type_label)
        info_layout.addWidget(cause_label)
        info_layout.addWidget(severity_label)
        
        header_layout.addWidget(icon_label)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        parent_layout.addWidget(header_frame)
    
    def _create_details_section(self, parent_layout):
        """创建错误详情区域"""
        details_label = QLabel("错误详情:")
        details_label.setFont(QFont("", 10, QFont.Bold))
        parent_layout.addWidget(details_label)
        
        # 错误消息文本框
        self.details_text = QTextEdit()
        self.details_text.setPlainText(self.error_message)
        self.details_text.setMaximumHeight(100)
        self.details_text.setReadOnly(True)
        parent_layout.addWidget(self.details_text)
    
    def _create_solutions_section(self, parent_layout):
        """创建解决方案区域"""
        solutions_label = QLabel("建议的解决方案:")
        solutions_label.setFont(QFont("", 10, QFont.Bold))
        parent_layout.addWidget(solutions_label)
        
        # 解决方案列表
        solutions_frame = QFrame()
        solutions_frame.setFrameStyle(QFrame.StyledPanel)
        solutions_layout = QVBoxLayout(solutions_frame)
        
        solutions = self.diagnosis.get('solutions', [])
        for i, solution in enumerate(solutions, 1):
            solution_label = QLabel(f"{i}. {solution}")
            solution_label.setWordWrap(True)
            solution_label.setMargin(5)
            solutions_layout.addWidget(solution_label)
        
        parent_layout.addWidget(solutions_frame)
        
        # 预防提示
        prevention_tips = self.diagnosis.get('prevention_tips', [])
        if prevention_tips:
            tips_label = QLabel("预防提示:")
            tips_label.setFont(QFont("", 9, QFont.Bold))
            parent_layout.addWidget(tips_label)
            
            tips_text = "\n".join(f"• {tip}" for tip in prevention_tips)
            tips_display = QLabel(tips_text)
            tips_display.setWordWrap(True)
            tips_display.setStyleSheet("color: #666; font-size: 9px; margin: 5px;")
            parent_layout.addWidget(tips_display)
    
    def _create_auto_fix_section(self, parent_layout):
        """创建自动修复区域"""
        auto_fix_frame = QFrame()
        auto_fix_frame.setFrameStyle(QFrame.StyledPanel)
        auto_fix_frame.setStyleSheet("background-color: #E8F5E8; border: 1px solid #4CAF50;")
        auto_fix_layout = QVBoxLayout(auto_fix_frame)
        
        # 自动修复标题
        auto_fix_label = QLabel("🔧 自动修复")
        auto_fix_label.setFont(QFont("", 10, QFont.Bold))
        auto_fix_label.setStyleSheet("color: #2E7D32;")
        
        # 自动修复说明
        fix_desc = QLabel("系统可以尝试自动修复此问题，是否要尝试？")
        fix_desc.setWordWrap(True)
        
        # 进度条（初始隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # 进度状态标签
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        
        # 自动修复按钮
        self.auto_fix_btn = QPushButton("尝试自动修复")
        self.auto_fix_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        auto_fix_layout.addWidget(auto_fix_label)
        auto_fix_layout.addWidget(fix_desc)
        auto_fix_layout.addWidget(self.progress_bar)
        auto_fix_layout.addWidget(self.progress_label)
        auto_fix_layout.addWidget(self.auto_fix_btn)
        
        parent_layout.addWidget(auto_fix_frame)
    
    def _create_button_section(self, parent_layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        
        # 复制错误信息按钮
        self.copy_btn = QPushButton("复制错误信息")
        self.copy_btn.clicked.connect(self._copy_error_info)
        
        # 查看日志按钮
        self.log_btn = QPushButton("查看日志")
        self.log_btn.clicked.connect(self._open_log_file)
        
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.log_btn)
        button_layout.addStretch()
        
        # 关闭按钮
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setDefault(True)
        
        button_layout.addWidget(self.close_btn)
        parent_layout.addLayout(button_layout)
    
    def _setup_styles(self):
        """设置样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QFrame {
                background-color: white;
                border-radius: 6px;
                padding: 10px;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: #fafafa;
            }
        """)
    
    def _connect_signals(self):
        """连接信号"""
        if hasattr(self, 'auto_fix_btn'):
            self.auto_fix_btn.clicked.connect(self._start_auto_fix)
    
    def _get_severity_icon(self, severity: str) -> str:
        """获取严重程度图标路径"""
        icon_map = {
            'low': 'images/info.png',
            'medium': 'images/warning.png',
            'high': 'images/error.png'
        }
        return icon_map.get(severity, 'images/warning.png')
    
    @pyqtSlot()
    def _start_auto_fix(self):
        """开始自动修复"""
        self.auto_fix_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        
        # 创建并启动自动修复工作线程
        self.auto_fix_worker = AutoFixWorker(self.error_type, self.error_message, self.context)
        self.auto_fix_worker.progress_updated.connect(self._on_fix_progress)
        self.auto_fix_worker.fix_completed.connect(self._on_fix_completed)
        self.auto_fix_worker.start()
    
    @pyqtSlot(int, str)
    def _on_fix_progress(self, progress: int, status: str):
        """自动修复进度更新"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(status)
    
    @pyqtSlot(bool, str)
    def _on_fix_completed(self, success: bool, message: str):
        """自动修复完成"""
        self.progress_bar.setVisible(False)
        self.progress_label.setText(f"修复结果: {message}")
        
        if success:
            self.progress_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.auto_fix_btn.setText("修复成功")
            self.auto_fix_btn.setStyleSheet("background-color: #4CAF50;")
        else:
            self.progress_label.setStyleSheet("color: #F44336; font-weight: bold;")
            self.auto_fix_btn.setText("修复失败")
            self.auto_fix_btn.setStyleSheet("background-color: #F44336;")
    
    @pyqtSlot()
    def _copy_error_info(self):
        """复制错误信息到剪贴板"""
        try:
            clipboard = QApplication.clipboard()
            error_info = f"""错误类型: {self.error_type}
错误消息: {self.error_message}
根本原因: {self.diagnosis.get('root_cause', '未知')}
严重程度: {self.diagnosis.get('severity', '未知')}

建议解决方案:
"""
            solutions = self.diagnosis.get('solutions', [])
            for i, solution in enumerate(solutions, 1):
                error_info += f"{i}. {solution}\n"
            
            clipboard.setText(error_info)
            self.progress_label.setText("错误信息已复制到剪贴板")
            self.progress_label.setVisible(True)
            
        except Exception as e:
            log_error(f"复制错误信息失败: {e}")
    
    @pyqtSlot()
    def _open_log_file(self):
        """打开日志文件"""
        try:
            import subprocess
            import platform
            
            log_dir = "logs"
            if os.path.exists(log_dir):
                if platform.system() == "Windows":
                    subprocess.run(["explorer", log_dir])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", log_dir])
                else:  # Linux
                    subprocess.run(["xdg-open", log_dir])
            else:
                self.progress_label.setText("日志目录不存在")
                self.progress_label.setVisible(True)
                
        except Exception as e:
            log_error(f"打开日志文件失败: {e}")


def show_error_dialog(error_type: str, error_message: str, context: Dict[str, Any] = None, parent=None):
    """显示错误对话框"""
    dialog = ErrorDialog(error_type, error_message, context, parent)
    return dialog.exec_()
