"""
模块管理标签页
"""
import os
import logging
from typing import Optional, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox, QListWidget,
    QMessageBox, QProgressBar, QTextEdit, QFileDialog
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel
from services.module_detector import ModuleDetector

class ModuleDetectionThread(QThread):
    """模块检测线程"""
    
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, detector: ModuleDetector, script_path: str):
        super().__init__()
        self.detector = detector
        self.script_path = script_path
    
    def run(self) -> None:
        """执行模块检测"""
        try:
            self.progress_signal.emit("开始检测模块...")
            modules = self.detector.detect_modules(self.script_path)
            # 将set转换为list，因为信号期望list类型
            modules_list = list(modules) if isinstance(modules, set) else modules
            self.finished_signal.emit(modules_list)
        except Exception as e:
            self.error_signal.emit(str(e))

class ModuleTab(QWidget):
    """模块管理标签页"""

    config_changed = pyqtSignal()

    def __init__(self, model: PyInstallerModel, config: AppConfig, detector: ModuleDetector):
        super().__init__()
        self.model = model
        self.config = config
        self.detector = detector
        self.detection_thread: Optional[ModuleDetectionThread] = None

        # 设置日志器
        self.logger = logging.getLogger(__name__)

        self.init_ui()
        self.connect_signals()
    
    def init_ui(self) -> None:
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 检测设置组
        detection_group = self.create_detection_group()
        layout.addWidget(detection_group)
        
        # 检测控制组
        control_group = self.create_control_group()
        layout.addWidget(control_group)
        
        # 检测结果组
        result_group = self.create_result_group()
        layout.addWidget(result_group)
        
        # 手动管理组
        manual_group = self.create_manual_group()
        layout.addWidget(manual_group)
    
    def create_detection_group(self) -> QGroupBox:
        """创建检测设置组"""
        group = QGroupBox("检测设置")
        layout = QVBoxLayout(group)

        # Python解释器选择
        interpreter_layout = QHBoxLayout()
        interpreter_layout.addWidget(QLabel("Python解释器:"))

        self.python_interpreter_edit = QLineEdit()
        self.python_interpreter_edit.setPlaceholderText("留空使用当前环境，或选择conda/venv环境的python.exe")
        self.python_interpreter_edit.setText(self.config.get("python_interpreter", ""))
        self.python_interpreter_edit.setToolTip("指定用于模块检测的Python解释器路径\n留空将使用当前环境\n建议选择你的conda虚拟环境中的python.exe")
        interpreter_layout.addWidget(self.python_interpreter_edit)

        self.browse_interpreter_btn = QPushButton("浏览...")
        self.browse_interpreter_btn.clicked.connect(self.browse_python_interpreter)
        self.browse_interpreter_btn.setToolTip("选择Python解释器")
        interpreter_layout.addWidget(self.browse_interpreter_btn)

        layout.addLayout(interpreter_layout)

        # 检测方法选择
        self.use_ast_checkbox = QCheckBox("使用AST静态分析")
        self.use_ast_checkbox.setChecked(self.config.get("use_ast_detection", True))
        self.use_ast_checkbox.setToolTip("通过分析Python代码的抽象语法树检测导入的模块")
        layout.addWidget(self.use_ast_checkbox)

        self.use_pyinstaller_checkbox = QCheckBox("使用PyInstaller调试信息")
        self.use_pyinstaller_checkbox.setChecked(self.config.get("use_pyinstaller_detection", False))
        self.use_pyinstaller_checkbox.setToolTip("通过PyInstaller的调试模式检测所需模块")
        layout.addWidget(self.use_pyinstaller_checkbox)

        return group
    
    def create_control_group(self) -> QGroupBox:
        """创建检测控制组"""
        group = QGroupBox("模块检测")
        layout = QVBoxLayout(group)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        
        self.detect_btn = QPushButton("开始检测")
        self.detect_btn.clicked.connect(self.start_detection)
        btn_layout.addWidget(self.detect_btn)
        
        self.stop_detect_btn = QPushButton("停止检测")
        self.stop_detect_btn.clicked.connect(self.stop_detection)
        self.stop_detect_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_detect_btn)
        
        self.clear_result_btn = QPushButton("清空结果")
        self.clear_result_btn.clicked.connect(self.clear_results)
        btn_layout.addWidget(self.clear_result_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态信息
        self.status_label = QLabel("准备就绪")
        layout.addWidget(self.status_label)
        
        return group
    
    def create_result_group(self) -> QGroupBox:
        """创建检测结果组"""
        group = QGroupBox("检测结果")
        layout = QVBoxLayout(group)
        
        # 结果列表
        self.detected_modules_list = QListWidget()
        self.detected_modules_list.setToolTip("双击模块名可以添加到隐藏导入列表")
        layout.addWidget(self.detected_modules_list)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.add_to_hidden_btn = QPushButton("添加到隐藏导入")
        self.add_to_hidden_btn.clicked.connect(self.add_to_hidden_imports)
        btn_layout.addWidget(self.add_to_hidden_btn)
        
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all_modules)
        btn_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("取消全选")
        self.deselect_all_btn.clicked.connect(self.deselect_all_modules)
        btn_layout.addWidget(self.deselect_all_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return group
    
    def create_manual_group(self) -> QGroupBox:
        """创建手动管理组"""
        group = QGroupBox("手动管理")
        layout = QVBoxLayout(group)
        
        # 当前隐藏导入
        layout.addWidget(QLabel("当前隐藏导入模块:"))
        self.hidden_imports_list = QListWidget()
        layout.addWidget(self.hidden_imports_list)
        
        # 添加/删除按钮
        btn_layout = QHBoxLayout()
        
        self.add_manual_btn = QPushButton("手动添加")
        self.add_manual_btn.clicked.connect(self.add_manual_import)
        btn_layout.addWidget(self.add_manual_btn)
        
        self.remove_hidden_btn = QPushButton("移除选中")
        self.remove_hidden_btn.clicked.connect(self.remove_hidden_import)
        btn_layout.addWidget(self.remove_hidden_btn)
        
        self.clear_hidden_btn = QPushButton("清空全部")
        self.clear_hidden_btn.clicked.connect(self.clear_hidden_imports)
        btn_layout.addWidget(self.clear_hidden_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return group
    
    def connect_signals(self) -> None:
        """连接信号槽"""
        self.use_ast_checkbox.toggled.connect(self.on_detection_method_changed)
        self.use_pyinstaller_checkbox.toggled.connect(self.on_detection_method_changed)
        self.python_interpreter_edit.textChanged.connect(self.on_python_interpreter_changed)
        self.detected_modules_list.itemDoubleClicked.connect(self.on_module_double_clicked)
    
    @pyqtSlot()
    def start_detection(self) -> None:
        """开始模块检测"""
        self.logger.info("🔍 开始模块检测")
        self.logger.info(f"脚本路径: {self.model.script_path}")

        if not self.model.script_path:
            self.logger.warning("❌ 未选择Python脚本")
            QMessageBox.warning(self, "错误", "请先选择要检测的Python脚本")
            return

        if not os.path.exists(self.model.script_path):
            self.logger.error(f"❌ 脚本文件不存在: {self.model.script_path}")
            QMessageBox.warning(self, "错误", f"脚本文件不存在: {self.model.script_path}")
            return

        # 更新检测器设置
        self.detector.use_ast = self.use_ast_checkbox.isChecked()
        self.detector.use_pyinstaller = self.use_pyinstaller_checkbox.isChecked()

        self.logger.info(f"检测设置 - AST: {self.detector.use_ast}, PyInstaller: {self.detector.use_pyinstaller}")
        
        # 创建检测线程
        self.logger.info("📝 创建检测线程")
        self.detection_thread = ModuleDetectionThread(self.detector, self.model.script_path)
        self.detection_thread.progress_signal.connect(self.on_detection_progress)
        self.detection_thread.finished_signal.connect(self.on_detection_finished)
        self.detection_thread.error_signal.connect(self.on_detection_error)

        # 更新UI状态
        self.logger.info("🔄 更新UI状态")
        self.detect_btn.setEnabled(False)
        self.stop_detect_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度

        # 开始检测
        self.logger.info("🚀 启动检测线程")
        self.detection_thread.start()
    
    @pyqtSlot()
    def stop_detection(self) -> None:
        """停止模块检测"""
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.terminate()
            self.detection_thread.wait(3000)
        
        self.reset_detection_ui()
        self.status_label.setText("检测已停止")
    
    @pyqtSlot(str)
    def on_detection_progress(self, message: str) -> None:
        """检测进度更新"""
        self.status_label.setText(message)
    
    @pyqtSlot(list)
    def on_detection_finished(self, modules: List[str]) -> None:
        """检测完成"""
        self.logger.info(f"✅ 检测完成，发现 {len(modules)} 个模块")
        self.logger.info(f"检测到的模块: {sorted(modules)}")

        self.reset_detection_ui()

        # 显示结果
        self.detected_modules_list.clear()
        for module in sorted(modules):
            self.detected_modules_list.addItem(module)

        # 进行智能分析
        self.logger.info("🧠 开始智能分析")
        if self.model.script_path and os.path.exists(self.model.script_path):
            try:
                self.logger.info(f"分析脚本: {self.model.script_path}")
                analysis = self.detector.analyze_missing_modules(self.model.script_path)

                self.logger.info(f"智能分析结果:")
                self.logger.info(f"  - 检测到模块: {len(analysis['detected_modules'])}")
                self.logger.info(f"  - 缺失模块: {len(analysis['missing_modules'])}")
                self.logger.info(f"  - 推荐隐藏导入: {len(analysis['hidden_imports'])}")
                self.logger.info(f"  - 推荐collect-all: {len(analysis['collect_all'])}")

                # 显示分析结果
                self.show_analysis_results(analysis)

                # 自动应用智能检测的隐藏导入
                if self.config.get("auto_add_detected_modules", True):
                    self.logger.info("🔧 自动应用智能检测的隐藏导入")
                    added_count = 0
                    # 添加智能检测的隐藏导入
                    for module in analysis['hidden_imports']:
                        if module not in self.model.hidden_imports:
                            self.model.hidden_imports.append(module)
                            added_count += 1

                    self.logger.info(f"添加了 {added_count} 个隐藏导入")
                    self.refresh_hidden_imports_list()
                    self.config_changed.emit()

                self.status_label.setText(f"智能分析完成，发现 {len(modules)} 个模块，推荐 {len(analysis['hidden_imports'])} 个隐藏导入")

            except Exception as e:
                self.logger.error(f"❌ 智能分析失败: {str(e)}")
                import traceback
                self.logger.error(f"错误详情: {traceback.format_exc()}")
                self.status_label.setText(f"检测完成，发现 {len(modules)} 个模块（智能分析失败: {str(e)}）")
        else:
            self.status_label.setText(f"检测完成，发现 {len(modules)} 个模块")
        
        if not modules:
            QMessageBox.information(self, "检测完成", "未检测到明显的导入模块")

    def show_analysis_results(self, analysis: dict) -> None:
        """显示分析结果"""
        from PyQt5.QtWidgets import QMessageBox, QTextEdit, QVBoxLayout, QDialog, QPushButton

        # 创建结果对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("智能模块分析结果")
        dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout(dialog)

        # 创建文本显示区域
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)

        # 构建结果文本
        result_text = "🔍 智能模块分析结果\n"
        result_text += "=" * 50 + "\n\n"

        result_text += f"📋 检测到的模块: {len(analysis['detected_modules'])}\n"
        for module in sorted(analysis['detected_modules']):
            result_text += f"  ✓ {module}\n"

        if analysis['missing_modules']:
            result_text += f"\n❌ 缺失的模块: {len(analysis['missing_modules'])}\n"
            for module in analysis['missing_modules']:
                result_text += f"  ✗ {module} (请先安装此模块)\n"

        if analysis['collect_all']:
            result_text += f"\n📦 推荐的collect-all参数: {len(analysis['collect_all'])}\n"
            for module in analysis['collect_all']:
                result_text += f"  --collect-all={module}\n"

        result_text += f"\n🔒 推荐的隐藏导入: {len(analysis['hidden_imports'])}\n"
        for module in sorted(analysis['hidden_imports'])[:15]:  # 只显示前15个
            result_text += f"  --hidden-import={module}\n"
        if len(analysis['hidden_imports']) > 15:
            result_text += f"  ... 还有 {len(analysis['hidden_imports']) - 15} 个\n"

        if analysis['suggestions']:
            result_text += f"\n💡 建议:\n"
            for suggestion in analysis['suggestions'][:10]:  # 只显示前10个建议
                result_text += f"  • {suggestion}\n"
            if len(analysis['suggestions']) > 10:
                result_text += f"  ... 还有 {len(analysis['suggestions']) - 10} 个建议\n"

        result_text += f"\n✅ 这些参数已自动应用到打包配置中！"

        text_edit.setPlainText(result_text)
        layout.addWidget(text_edit)

        # 添加关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        # 显示对话框
        dialog.exec_()

    @pyqtSlot(str)
    def on_detection_error(self, error: str) -> None:
        """检测错误"""
        self.logger.error(f"❌ 检测失败: {error}")
        self.reset_detection_ui()
        self.status_label.setText(f"检测失败: {error}")
        QMessageBox.critical(self, "检测失败", f"模块检测失败:\n{error}")
    
    def reset_detection_ui(self) -> None:
        """重置检测UI状态"""
        self.detect_btn.setEnabled(True)
        self.stop_detect_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
    
    @pyqtSlot()
    def clear_results(self) -> None:
        """清空检测结果"""
        self.detected_modules_list.clear()
        self.status_label.setText("结果已清空")
    
    @pyqtSlot()
    def add_to_hidden_imports(self) -> None:
        """添加选中模块到隐藏导入"""
        selected_items = self.detected_modules_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提示", "请先选择要添加的模块")
            return
        
        added_count = 0
        for item in selected_items:
            module_name = item.text()
            if module_name not in self.model.hidden_imports:
                self.model.hidden_imports.append(module_name)
                added_count += 1
        
        self.refresh_hidden_imports_list()
        QMessageBox.information(self, "完成", f"已添加 {added_count} 个模块到隐藏导入")
    
    @pyqtSlot()
    def on_module_double_clicked(self) -> None:
        """模块双击处理"""
        self.add_to_hidden_imports()
    
    @pyqtSlot()
    def select_all_modules(self) -> None:
        """全选模块"""
        self.detected_modules_list.selectAll()
    
    @pyqtSlot()
    def deselect_all_modules(self) -> None:
        """取消全选模块"""
        self.detected_modules_list.clearSelection()
    
    @pyqtSlot()
    def add_manual_import(self) -> None:
        """手动添加隐藏导入"""
        from PyQt5.QtWidgets import QInputDialog
        module_name, ok = QInputDialog.getText(
            self, "添加模块", "请输入模块名称:"
        )
        if ok and module_name.strip():
            module_name = module_name.strip()
            if module_name not in self.model.hidden_imports:
                self.model.hidden_imports.append(module_name)
                self.refresh_hidden_imports_list()
            else:
                QMessageBox.information(self, "提示", "该模块已存在于隐藏导入列表中")
    
    @pyqtSlot()
    def remove_hidden_import(self) -> None:
        """移除选中的隐藏导入"""
        current_row = self.hidden_imports_list.currentRow()
        if current_row >= 0:
            item = self.hidden_imports_list.takeItem(current_row)
            if item:
                module_name = item.text()
                if module_name in self.model.hidden_imports:
                    self.model.hidden_imports.remove(module_name)
    
    @pyqtSlot()
    def clear_hidden_imports(self) -> None:
        """清空所有隐藏导入"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有隐藏导入模块吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.model.hidden_imports.clear()
            self.refresh_hidden_imports_list()
    
    @pyqtSlot()
    def browse_python_interpreter(self) -> None:
        """浏览选择Python解释器"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Python解释器",
            "",
            "Python解释器 (python.exe);;所有文件 (*.*)"
        )
        if file_path:
            self.python_interpreter_edit.setText(file_path)
            self.config.set("python_interpreter", file_path)
            # 更新检测器设置
            self.detector.python_interpreter = file_path or self.detector.python_interpreter

    @pyqtSlot()
    def on_python_interpreter_changed(self) -> None:
        """Python解释器路径变更"""
        interpreter_path = self.python_interpreter_edit.text().strip()
        self.config.set("python_interpreter", interpreter_path)
        # 更新检测器设置
        self.detector.python_interpreter = interpreter_path or self.detector.python_interpreter

    @pyqtSlot()
    def on_detection_method_changed(self) -> None:
        """检测方法变更"""
        self.config.set("use_ast_detection", self.use_ast_checkbox.isChecked())
        self.config.set("use_pyinstaller_detection", self.use_pyinstaller_checkbox.isChecked())
    
    def refresh_hidden_imports_list(self) -> None:
        """刷新隐藏导入列表"""
        self.hidden_imports_list.clear()
        for module in self.model.hidden_imports:
            self.hidden_imports_list.addItem(module)
