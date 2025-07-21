"""
模块管理标签页
"""
import os
import logging
from typing import Optional, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox, QListWidget,
    QMessageBox, QProgressBar, QTextEdit, QFileDialog,
    QRadioButton, QButtonGroup, QScrollArea, QFrame, QSplitter
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel
from services.module_detector import ModuleDetector
from services.python_env_scanner import get_scanner, PythonEnvironment

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
    # 新增信号：静默检测完成
    silent_detection_finished = pyqtSignal(list, dict)  # modules, analysis_result

    def __init__(self, model: PyInstallerModel, config: AppConfig, detector: ModuleDetector):
        super().__init__()
        self.model = model
        self.config = config
        self.detector = detector
        self.detection_thread: Optional[ModuleDetectionThread] = None
        self._is_silent_detection = False  # 跟踪是否是静默检测

        # 设置日志器
        self.logger = logging.getLogger(__name__)

        # Python 环境扫描器
        self.env_scanner = get_scanner()
        self.environments: List[PythonEnvironment] = []
        self.env_button_group = QButtonGroup()
        self.selected_environment: Optional[PythonEnvironment] = None

        self.init_ui()
        self.connect_signals()
        self.scan_environments()  # 初始化时扫描环境
    
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

        # Python 环境选择区域
        env_group = self.create_environment_selection_group()
        layout.addWidget(env_group)

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

    def create_environment_selection_group(self) -> QGroupBox:
        """创建环境选择组"""
        group = QGroupBox("Python 环境选择")
        layout = QVBoxLayout(group)

        # 顶部控制按钮
        control_layout = QHBoxLayout()

        self.refresh_env_btn = QPushButton("🔄 刷新环境")
        self.refresh_env_btn.clicked.connect(self.scan_environments)
        self.refresh_env_btn.setToolTip("重新扫描系统中的 Python 环境")
        control_layout.addWidget(self.refresh_env_btn)

        self.install_pyinstaller_btn = QPushButton("📦 安装 PyInstaller")
        self.install_pyinstaller_btn.clicked.connect(self.install_pyinstaller_to_selected)
        self.install_pyinstaller_btn.setToolTip("在选中的环境中安装 PyInstaller")
        self.install_pyinstaller_btn.setEnabled(False)
        control_layout.addWidget(self.install_pyinstaller_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # 环境列表滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setMinimumHeight(120)

        self.env_list_widget = QWidget()
        self.env_list_layout = QVBoxLayout(self.env_list_widget)
        self.env_list_layout.setContentsMargins(5, 5, 5, 5)

        scroll_area.setWidget(self.env_list_widget)
        layout.addWidget(scroll_area)

        # 手动输入区域（保留原有功能）
        manual_frame = QFrame()
        manual_frame.setFrameStyle(QFrame.StyledPanel)
        manual_layout = QVBoxLayout(manual_frame)
        manual_layout.setContentsMargins(5, 5, 5, 5)

        manual_label = QLabel("或手动输入解释器路径：")
        manual_layout.addWidget(manual_label)

        manual_input_layout = QHBoxLayout()
        self.python_interpreter_edit = QLineEdit()
        self.python_interpreter_edit.setPlaceholderText("手动输入 Python 解释器路径...")
        self.python_interpreter_edit.setText(self.config.get("python_interpreter", ""))
        self.python_interpreter_edit.textChanged.connect(self.on_manual_interpreter_changed)
        manual_input_layout.addWidget(self.python_interpreter_edit)

        self.browse_interpreter_btn = QPushButton("浏览...")
        self.browse_interpreter_btn.clicked.connect(self.browse_python_interpreter)
        self.browse_interpreter_btn.setToolTip("选择Python解释器")
        manual_input_layout.addWidget(self.browse_interpreter_btn)

        manual_layout.addLayout(manual_input_layout)
        layout.addWidget(manual_frame)

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
        self.python_interpreter_edit.textChanged.connect(self.on_manual_interpreter_changed)
        self.detected_modules_list.itemDoubleClicked.connect(self.on_module_double_clicked)
    
    @pyqtSlot()
    def start_detection(self, silent: bool = False) -> None:
        """开始模块检测

        Args:
            silent: 是否静默执行（不显示UI反馈）
        """
        self._is_silent_detection = silent
        self.logger.info("🔍 开始模块检测" + (" (静默模式)" if silent else ""))
        self.logger.info(f"脚本路径: {self.model.script_path}")

        if not self.model.script_path:
            self.logger.warning("❌ 未选择Python脚本")
            if not silent:
                QMessageBox.warning(self, "错误", "请先选择要检测的Python脚本")
            return

        if not os.path.exists(self.model.script_path):
            self.logger.error(f"❌ 脚本文件不存在: {self.model.script_path}")
            if not silent:
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

        # 更新UI状态（仅在非静默模式下）
        if not silent:
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

        # 如果是静默模式，更新主窗口状态栏
        if self._is_silent_detection:
            # 获取主窗口
            main_window = self.window()
            if main_window and hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"模块检测: {message}")
    
    @pyqtSlot(list)
    def on_detection_finished(self, modules: List[str]) -> None:
        """检测完成"""
        self.logger.info(f"✅ 检测完成，发现 {len(modules)} 个模块")
        self.logger.info(f"检测到的模块: {sorted(modules)}")

        # 仅在非静默模式下更新UI
        if not self._is_silent_detection:
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

                # 优先使用增强的模块检测器
                try:
                    from services.enhanced_module_detector import EnhancedModuleDetector
                    enhanced_detector = EnhancedModuleDetector(cache_dir=".gui_cache", max_workers=2)

                    def gui_callback(message):
                        self.logger.info(f"🔍 {message}")
                        self.status_label.setText(message)

                    self.logger.info("🚀 使用增强模块检测器进行分析")
                    enhanced_result = enhanced_detector.detect_modules_with_cache(self.model.script_path, gui_callback)

                    # 转换为原始格式以兼容现有代码
                    analysis = {
                        'detected_modules': list(enhanced_result.detected_modules),
                        'missing_modules': list(enhanced_result.missing_modules),
                        'hidden_imports': enhanced_result.hidden_imports,
                        'collect_all': enhanced_result.collect_all,
                        'suggestions': enhanced_result.recommendations,
                        'data_files': enhanced_result.data_files,
                        'framework_configs': enhanced_result.framework_configs
                    }

                    self.logger.info(f"✅ 增强智能分析结果:")
                    self.logger.info(f"  - 检测到模块: {len(analysis['detected_modules'])}")
                    self.logger.info(f"  - 缺失模块: {len(analysis['missing_modules'])}")
                    self.logger.info(f"  - 推荐隐藏导入: {len(analysis['hidden_imports'])}")
                    self.logger.info(f"  - 推荐collect-all: {len(analysis['collect_all'])}")
                    self.logger.info(f"  - 框架配置: {len(analysis['framework_configs'])}")
                    self.logger.info(f"  - 缓存命中: {'是' if enhanced_result.cache_hit else '否'}")
                    self.logger.info(f"  - 检测时间: {enhanced_result.detection_time:.2f}s")

                except ImportError as ie:
                    self.logger.warning(f"⚠️  增强模块检测器不可用: {ie}")
                    self.logger.info("🔄 回退到原始模块检测器")
                    analysis = self.detector.analyze_missing_modules(self.model.script_path)

                    self.logger.info(f"📊 原始智能分析结果:")
                    self.logger.info(f"  - 检测到模块: {len(analysis['detected_modules'])}")
                    self.logger.info(f"  - 缺失模块: {len(analysis['missing_modules'])}")
                    self.logger.info(f"  - 推荐隐藏导入: {len(analysis['hidden_imports'])}")
                    self.logger.info(f"  - 推荐collect-all: {len(analysis['collect_all'])}")

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

                # 更新状态信息
                framework_info = ""
                if 'framework_configs' in analysis and analysis['framework_configs']:
                    frameworks = list(analysis['framework_configs'].keys())
                    framework_info = f"，检测到框架: {', '.join(frameworks)}"

                # 根据模式决定是否显示结果对话框和更新状态
                if self._is_silent_detection:
                    # 静默模式：发出信号
                    self.silent_detection_finished.emit(modules, analysis)
                else:
                    # 非静默模式：显示结果对话框和更新状态
                    self.show_analysis_results(analysis)
                    self.status_label.setText(f"智能分析完成，发现 {len(modules)} 个模块，推荐 {len(analysis['hidden_imports'])} 个隐藏导入{framework_info}")

            except Exception as e:
                self.logger.error(f"❌ 智能分析失败: {str(e)}")
                import traceback
                self.logger.error(f"错误详情: {traceback.format_exc()}")

                if self._is_silent_detection:
                    # 静默模式下也发出信号，但带有空的分析结果
                    empty_analysis = {'detected_modules': modules, 'hidden_imports': [], 'collect_all': [], 'data_files': []}
                    self.silent_detection_finished.emit(modules, empty_analysis)
                else:
                    self.status_label.setText(f"检测完成，发现 {len(modules)} 个模块（智能分析失败: {str(e)}）")
        else:
            if not self._is_silent_detection:
                self.status_label.setText(f"检测完成，发现 {len(modules)} 个模块")
            else:
                # 静默模式下发出信号，但带有空的分析结果
                empty_analysis = {'detected_modules': modules, 'hidden_imports': [], 'collect_all': [], 'data_files': []}
                self.silent_detection_finished.emit(modules, empty_analysis)

        # 仅在非静默模式下显示消息框
        if not modules and not self._is_silent_detection:
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
    def on_detection_method_changed(self) -> None:
        """检测方法变更"""
        self.config.set("use_ast_detection", self.use_ast_checkbox.isChecked())
        self.config.set("use_pyinstaller_detection", self.use_pyinstaller_checkbox.isChecked())
    
    def refresh_hidden_imports_list(self) -> None:
        """刷新隐藏导入列表"""
        self.hidden_imports_list.clear()
        for module in self.model.hidden_imports:
            self.hidden_imports_list.addItem(module)

    # ==================== 环境管理相关方法 ====================

    @pyqtSlot()
    def scan_environments(self) -> None:
        """扫描 Python 环境"""
        try:
            self.refresh_env_btn.setEnabled(False)
            self.refresh_env_btn.setText("🔄 扫描中...")

            # 扫描环境
            self.environments = self.env_scanner.scan_all_environments()

            # 更新 UI
            self.update_environment_list()

            self.logger.info(f"扫描到 {len(self.environments)} 个 Python 环境")

        except Exception as e:
            self.logger.error(f"扫描环境失败: {e}")
            QMessageBox.warning(self, "错误", f"扫描环境失败: {str(e)}")
        finally:
            self.refresh_env_btn.setEnabled(True)
            self.refresh_env_btn.setText("🔄 刷新环境")

    def update_environment_list(self) -> None:
        """更新环境列表显示"""
        # 清空现有的单选按钮
        for button in self.env_button_group.buttons():
            self.env_button_group.removeButton(button)
            button.deleteLater()

        # 清空布局
        while self.env_list_layout.count():
            child = self.env_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.environments:
            no_env_label = QLabel("未找到 Python 环境，请点击刷新或手动输入路径")
            no_env_label.setStyleSheet("color: #666; font-style: italic;")
            self.env_list_layout.addWidget(no_env_label)
            return

        # 添加环境单选按钮
        current_interpreter = self.config.get("python_interpreter", "")

        for i, env in enumerate(self.environments):
            radio_btn = QRadioButton(env.get_display_name())
            radio_btn.setToolTip(f"路径: {env.path}\n描述: {env.description}")

            # 设置样式
            if not env.is_available:
                radio_btn.setStyleSheet("color: #999;")
                radio_btn.setEnabled(False)
            elif not env.has_pyinstaller:
                radio_btn.setStyleSheet("color: #ff6600;")
            else:
                radio_btn.setStyleSheet("color: #006600;")

            # 检查是否为当前选中的环境
            if current_interpreter and env.path == current_interpreter:
                radio_btn.setChecked(True)
                self.selected_environment = env
                self.install_pyinstaller_btn.setEnabled(not env.has_pyinstaller)
            elif not current_interpreter and env.is_current:
                radio_btn.setChecked(True)
                self.selected_environment = env
                self.install_pyinstaller_btn.setEnabled(not env.has_pyinstaller)

            # 连接信号
            radio_btn.toggled.connect(lambda checked, environment=env: self.on_environment_selected(checked, environment))

            self.env_button_group.addButton(radio_btn, i)
            self.env_list_layout.addWidget(radio_btn)

        self.env_list_layout.addStretch()

    @pyqtSlot(bool, PythonEnvironment)
    def on_environment_selected(self, checked: bool, environment: PythonEnvironment) -> None:
        """环境选择变更"""
        if checked:
            self.selected_environment = environment

            # 更新配置
            self.config.set("python_interpreter", environment.path)

            # 更新手动输入框
            self.python_interpreter_edit.setText(environment.path)

            # 更新检测器设置
            self.detector.python_interpreter = environment.path

            # 更新安装按钮状态
            self.install_pyinstaller_btn.setEnabled(not environment.has_pyinstaller)

            self.logger.info(f"选择环境: {environment.name} ({environment.path})")

    @pyqtSlot()
    def on_manual_interpreter_changed(self) -> None:
        """手动输入解释器路径变更"""
        interpreter_path = self.python_interpreter_edit.text().strip()

        # 如果手动输入了路径，取消所有单选按钮的选择
        if interpreter_path:
            for button in self.env_button_group.buttons():
                button.setChecked(False)
            self.selected_environment = None
            self.install_pyinstaller_btn.setEnabled(False)

        # 更新配置和检测器
        self.config.set("python_interpreter", interpreter_path)
        self.detector.python_interpreter = interpreter_path or self.detector.python_interpreter

    @pyqtSlot()
    def install_pyinstaller_to_selected(self) -> None:
        """在选中的环境中安装 PyInstaller"""
        if not self.selected_environment:
            QMessageBox.warning(self, "错误", "请先选择一个 Python 环境")
            return

        reply = QMessageBox.question(
            self, "确认安装",
            f"确定要在以下环境中安装 PyInstaller 吗？\n\n"
            f"环境: {self.selected_environment.name}\n"
            f"路径: {self.selected_environment.path}",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.install_pyinstaller_btn.setEnabled(False)
            self.install_pyinstaller_btn.setText("📦 安装中...")

            try:
                success = self.env_scanner.install_pyinstaller(self.selected_environment.path)

                if success:
                    QMessageBox.information(self, "成功", "PyInstaller 安装成功！")
                    # 重新扫描环境以更新状态
                    self.scan_environments()
                else:
                    QMessageBox.warning(self, "失败", "PyInstaller 安装失败，请检查网络连接和权限")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"安装过程中出现错误: {str(e)}")
            finally:
                self.install_pyinstaller_btn.setEnabled(True)
                self.install_pyinstaller_btn.setText("📦 安装 PyInstaller")
