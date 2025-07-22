#!/usr/bin/env python3
"""
增强的模块管理标签页
集成精准依赖分析器和动态依赖追踪器
"""

import os
import sys
from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar,
    QCheckBox, QGroupBox, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QSplitter, QFrame, QScrollArea, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.precise_dependency_analyzer import PreciseDependencyAnalyzer
from services.dynamic_dependency_tracker import DynamicDependencyTracker
from utils.logger import log_info, log_error


class EnhancedAnalysisThread(QThread):
    """增强的分析线程"""
    
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, script_path: str, python_interpreter: str = ""):
        super().__init__()
        self.script_path = script_path
        self.python_interpreter = python_interpreter
        self.should_stop = False
    
    def run(self):
        """执行分析"""
        try:
            self.progress_signal.emit("初始化精准依赖分析器...")
            
            # 创建分析器
            precise_analyzer = PreciseDependencyAnalyzer(
                python_interpreter=self.python_interpreter,
                cache_dir=".enhanced_gui_cache"
            )
            
            dynamic_tracker = DynamicDependencyTracker(
                python_interpreter=self.python_interpreter,
                timeout=30
            )
            
            def progress_callback(message):
                if not self.should_stop:
                    self.progress_signal.emit(message)
            
            # 执行精准分析
            self.progress_signal.emit("开始精准依赖分析...")
            precise_result = precise_analyzer.analyze_dependencies(
                self.script_path, progress_callback
            )
            
            if self.should_stop:
                return
            
            # 执行动态分析
            self.progress_signal.emit("开始动态依赖分析...")
            dynamic_result = dynamic_tracker.get_comprehensive_analysis(
                self.script_path, progress_callback
            )
            
            if self.should_stop:
                return
            
            # 合并结果
            combined_result = {
                'precise_analysis': precise_result,
                'dynamic_analysis': dynamic_result,
                'analysis_successful': True
            }
            
            self.finished_signal.emit(combined_result)
            
        except Exception as e:
            log_error(f"增强分析失败: {e}")
            self.error_signal.emit(str(e))
    
    def stop(self):
        """停止分析"""
        self.should_stop = True


class ModuleTreeWidget(QTreeWidget):
    """模块树形显示组件"""
    
    def __init__(self):
        super().__init__()
        self.setHeaderLabels(['模块名', '类型', '版本', '状态', '大小'])
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
    
    def populate_modules(self, precise_result, dynamic_result):
        """填充模块数据"""
        self.clear()
        
        # 创建根节点
        standard_root = QTreeWidgetItem(self, ['标准库模块', '', '', '', ''])
        standard_root.setExpanded(True)
        
        third_party_root = QTreeWidgetItem(self, ['第三方库', '', '', '', ''])
        third_party_root.setExpanded(True)
        
        local_root = QTreeWidgetItem(self, ['本地模块', '', '', '', ''])
        local_root.setExpanded(True)
        
        dynamic_root = QTreeWidgetItem(self, ['动态检测', '', '', '', ''])
        dynamic_root.setExpanded(True)
        
        # 添加标准库模块
        for module in sorted(precise_result.standard_modules):
            info = precise_result.module_details.get(module)
            if info:
                item = QTreeWidgetItem(standard_root, [
                    module,
                    '标准库',
                    info.version,
                    '✅ 可用' if info.is_available else '❌ 缺失',
                    self._format_size(info.size)
                ])
                item.setIcon(0, self._get_module_icon('standard'))
        
        # 添加第三方库
        for module in sorted(precise_result.third_party_modules):
            info = precise_result.module_details.get(module)
            if info:
                item = QTreeWidgetItem(third_party_root, [
                    module,
                    '第三方库',
                    info.version,
                    '✅ 可用' if info.is_available else '❌ 缺失',
                    self._format_size(info.size)
                ])
                item.setIcon(0, self._get_module_icon('third_party', info.is_available))
        
        # 添加本地模块
        for module in sorted(precise_result.local_modules):
            info = precise_result.module_details.get(module)
            if info:
                item = QTreeWidgetItem(local_root, [
                    module,
                    '本地模块',
                    info.version,
                    '✅ 可用' if info.is_available else '❌ 缺失',
                    self._format_size(info.size)
                ])
                item.setIcon(0, self._get_module_icon('local'))
        
        # 添加动态检测结果
        dynamic_data = dynamic_result.get('dynamic_result')
        if dynamic_data:
            # 条件模块
            if dynamic_data.conditional_modules:
                conditional_item = QTreeWidgetItem(dynamic_root, ['条件导入', '', '', '', ''])
                for module in sorted(dynamic_data.conditional_modules):
                    QTreeWidgetItem(conditional_item, [module, '条件', '', '❓ 条件', ''])
            
            # 延迟导入
            if dynamic_data.lazy_imports:
                lazy_item = QTreeWidgetItem(dynamic_root, ['延迟导入', '', '', '', ''])
                for module in sorted(dynamic_data.lazy_imports):
                    QTreeWidgetItem(lazy_item, [module, '延迟', '', '⏰ 延迟', ''])
            
            # 可选模块
            if dynamic_data.optional_modules:
                optional_item = QTreeWidgetItem(dynamic_root, ['可选模块', '', '', '', ''])
                for module in sorted(dynamic_data.optional_modules):
                    QTreeWidgetItem(optional_item, [module, '可选', '', '🔄 可选', ''])
        
        # 调整列宽
        for i in range(5):
            self.resizeColumnToContents(i)
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        if size == 0:
            return ""
        elif size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f}KB"
        else:
            return f"{size/(1024*1024):.1f}MB"
    
    def _get_module_icon(self, module_type: str, is_available: bool = True) -> QIcon:
        """获取模块图标"""
        # 这里可以根据需要添加实际的图标
        return QIcon()


class AnalysisResultWidget(QWidget):
    """分析结果显示组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 模块树标签页
        self.module_tree = ModuleTreeWidget()
        self.tab_widget.addTab(self.module_tree, "📦 模块详情")
        
        # 建议标签页
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.tab_widget.addTab(self.recommendations_text, "💡 建议")
        
        # PyInstaller参数标签页
        self.pyinstaller_text = QTextEdit()
        self.pyinstaller_text.setReadOnly(True)
        self.tab_widget.addTab(self.pyinstaller_text, "🔧 PyInstaller参数")
        
        # 环境信息标签页
        self.environment_text = QTextEdit()
        self.environment_text.setReadOnly(True)
        self.tab_widget.addTab(self.environment_text, "🌍 环境信息")
        
        layout.addWidget(self.tab_widget)
    
    def update_results(self, precise_result, dynamic_result):
        """更新分析结果"""
        # 更新模块树
        self.module_tree.populate_modules(precise_result, dynamic_result)
        
        # 更新建议
        self._update_recommendations(precise_result, dynamic_result)
        
        # 更新PyInstaller参数
        self._update_pyinstaller_params(precise_result)
        
        # 更新环境信息
        self._update_environment_info(precise_result)
    
    def _update_recommendations(self, precise_result, dynamic_result):
        """更新建议"""
        text = "🎯 精准依赖分析建议\n"
        text += "=" * 50 + "\n\n"
        
        # 精准分析建议
        if precise_result.recommendations:
            text += "📋 精准分析建议:\n"
            for i, rec in enumerate(precise_result.recommendations, 1):
                text += f"  {i}. {rec}\n"
            text += "\n"
        
        # 动态分析建议
        dynamic_recs = dynamic_result.get('recommendations', [])
        if dynamic_recs:
            text += "🔍 动态分析建议:\n"
            for i, rec in enumerate(dynamic_recs, 1):
                text += f"  {i}. {rec}\n"
            text += "\n"
        
        # 警告
        if precise_result.warnings:
            text += "⚠️ 警告:\n"
            for i, warning in enumerate(precise_result.warnings, 1):
                text += f"  {i}. {warning}\n"
            text += "\n"
        
        # 统计信息
        text += "📊 统计信息:\n"
        text += f"  - 标准库模块: {len(precise_result.standard_modules)} 个\n"
        text += f"  - 第三方库模块: {len(precise_result.third_party_modules)} 个\n"
        text += f"  - 本地模块: {len(precise_result.local_modules)} 个\n"
        text += f"  - 可用模块: {len(precise_result.available_modules)} 个\n"
        text += f"  - 缺失模块: {len(precise_result.missing_modules)} 个\n"
        
        if dynamic_result.get('dynamic_result'):
            dr = dynamic_result['dynamic_result']
            text += f"  - 条件导入: {len(dr.conditional_modules)} 个\n"
            text += f"  - 延迟导入: {len(dr.lazy_imports)} 个\n"
            text += f"  - 可选模块: {len(dr.optional_modules)} 个\n"
        
        self.recommendations_text.setPlainText(text)
    
    def _update_pyinstaller_params(self, precise_result):
        """更新PyInstaller参数"""
        text = "🔧 推荐的PyInstaller参数\n"
        text += "=" * 50 + "\n\n"
        
        if precise_result.hidden_imports:
            text += "隐藏导入 (--hidden-import):\n"
            for imp in precise_result.hidden_imports:
                text += f"  --hidden-import={imp}\n"
            text += "\n"
        
        if precise_result.collect_all:
            text += "收集全部 (--collect-all):\n"
            for pkg in precise_result.collect_all:
                text += f"  --collect-all={pkg}\n"
            text += "\n"
        
        if precise_result.data_files:
            text += "数据文件 (--add-data):\n"
            for data in precise_result.data_files:
                text += f"  {data}\n"
            text += "\n"
        
        # 生成完整命令示例
        text += "完整命令示例:\n"
        text += "pyinstaller your_script.py"
        
        for imp in precise_result.hidden_imports:
            text += f" --hidden-import={imp}"
        
        for pkg in precise_result.collect_all:
            text += f" --collect-all={pkg}"
        
        text += "\n"
        
        self.pyinstaller_text.setPlainText(text)
    
    def _update_environment_info(self, precise_result):
        """更新环境信息"""
        env_info = precise_result.environment_info
        
        text = "🌍 Python环境信息\n"
        text += "=" * 50 + "\n\n"
        
        text += f"Python版本: {env_info.get('python_version', 'Unknown')}\n"
        text += f"Python可执行文件: {env_info.get('python_executable', 'Unknown')}\n"
        text += f"平台: {env_info.get('platform', 'Unknown')}\n"
        text += f"虚拟环境: {'是' if env_info.get('is_virtual_env') else '否'}\n"
        
        if env_info.get('virtual_env_path'):
            text += f"虚拟环境路径: {env_info['virtual_env_path']}\n"
        
        text += f"\n已安装包 ({len(env_info.get('installed_packages', {}))}) 个):\n"
        
        installed_packages = env_info.get('installed_packages', {})
        for pkg, version in sorted(installed_packages.items()):
            text += f"  {pkg} == {version}\n"
        
        self.environment_text.setPlainText(text)


class EnhancedModuleTab(QWidget):
    """增强的模块管理标签页"""

    # 信号
    analysis_finished = pyqtSignal(dict)

    def __init__(self, model, config, parent=None):
        super().__init__(parent)
        self.model = model
        self.config = config
        self.analysis_thread: Optional[EnhancedAnalysisThread] = None

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 控制面板
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)

        # 分析结果显示
        self.result_widget = AnalysisResultWidget()
        layout.addWidget(self.result_widget)

    def create_control_panel(self) -> QWidget:
        """创建控制面板"""
        panel = QGroupBox("依赖分析控制")
        layout = QGridLayout(panel)

        # 分析选项
        options_group = QGroupBox("分析选项")
        options_layout = QVBoxLayout(options_group)

        self.enable_precise_analysis = QCheckBox("启用精准依赖分析")
        self.enable_precise_analysis.setChecked(True)
        self.enable_precise_analysis.setToolTip("使用环境感知的精准依赖分析")
        options_layout.addWidget(self.enable_precise_analysis)

        self.enable_dynamic_analysis = QCheckBox("启用动态依赖追踪")
        self.enable_dynamic_analysis.setChecked(True)
        self.enable_dynamic_analysis.setToolTip("通过静态分析检测动态导入模式")
        options_layout.addWidget(self.enable_dynamic_analysis)

        self.enable_execution_analysis = QCheckBox("启用执行分析 (实验性)")
        self.enable_execution_analysis.setChecked(False)
        self.enable_execution_analysis.setToolTip("通过实际执行脚本检测运行时依赖 (可能有风险)")
        options_layout.addWidget(self.enable_execution_analysis)

        layout.addWidget(options_group, 0, 0, 1, 2)

        # 控制按钮
        self.analyze_btn = QPushButton("🎯 开始精准分析")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.analyze_btn, 1, 0)

        self.stop_btn = QPushButton("⏹️ 停止分析")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.stop_btn, 1, 1)

        return panel

    def connect_signals(self):
        """连接信号"""
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.stop_btn.clicked.connect(self.stop_analysis)

    @pyqtSlot()
    def start_analysis(self):
        """开始分析"""
        if not self.model.script_path:
            QMessageBox.warning(self, "错误", "请先选择要分析的Python脚本")
            return

        if not os.path.exists(self.model.script_path):
            QMessageBox.warning(self, "错误", f"脚本文件不存在: {self.model.script_path}")
            return

        log_info("开始增强依赖分析")

        # 更新UI状态
        self.analyze_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_label.setText("正在初始化分析...")

        # 获取Python解释器
        python_interpreter = self.config.get("python_interpreter", "")

        # 创建并启动分析线程
        self.analysis_thread = EnhancedAnalysisThread(
            self.model.script_path,
            python_interpreter
        )
        self.analysis_thread.progress_signal.connect(self.on_analysis_progress)
        self.analysis_thread.finished_signal.connect(self.on_analysis_finished)
        self.analysis_thread.error_signal.connect(self.on_analysis_error)

        self.analysis_thread.start()

    @pyqtSlot()
    def stop_analysis(self):
        """停止分析"""
        if self.analysis_thread and self.analysis_thread.isRunning():
            log_info("停止增强依赖分析")
            self.analysis_thread.stop()
            self.analysis_thread.wait(3000)

        self.reset_ui_state()
        self.status_label.setText("分析已停止")

    @pyqtSlot(str)
    def on_analysis_progress(self, message: str):
        """分析进度更新"""
        self.status_label.setText(message)
        log_info(f"分析进度: {message}")

    @pyqtSlot(dict)
    def on_analysis_finished(self, result: dict):
        """分析完成"""
        log_info("增强依赖分析完成")

        self.reset_ui_state()

        if result.get('analysis_successful'):
            precise_result = result['precise_analysis']
            dynamic_result = result['dynamic_analysis']

            # 更新结果显示
            self.result_widget.update_results(precise_result, dynamic_result)

            # 更新状态
            total_modules = len(precise_result.standard_modules |
                             precise_result.third_party_modules |
                             precise_result.local_modules)
            missing_count = len(precise_result.missing_modules)

            self.status_label.setText(
                f"分析完成: 发现 {total_modules} 个模块，{missing_count} 个缺失"
            )

            # 发出信号
            self.analysis_finished.emit(result)

            # 显示完成通知
            if self.config.get("show_analysis_notification", True):
                self.show_completion_notification(precise_result, dynamic_result)
        else:
            self.status_label.setText("分析失败")

    @pyqtSlot(str)
    def on_analysis_error(self, error_message: str):
        """分析错误"""
        log_error(f"增强依赖分析错误: {error_message}")

        self.reset_ui_state()
        self.status_label.setText(f"分析失败: {error_message}")

        QMessageBox.critical(self, "分析错误", f"依赖分析失败:\n{error_message}")

    def reset_ui_state(self):
        """重置UI状态"""
        self.analyze_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

    def show_completion_notification(self, precise_result, dynamic_result):
        """显示完成通知"""
        total_modules = len(precise_result.standard_modules |
                          precise_result.third_party_modules |
                          precise_result.local_modules)
        missing_count = len(precise_result.missing_modules)

        message = f"✅ 依赖分析完成!\n\n"
        message += f"📦 发现模块: {total_modules} 个\n"
        message += f"❌ 缺失模块: {missing_count} 个\n"

        if precise_result.hidden_imports:
            message += f"🔧 推荐隐藏导入: {len(precise_result.hidden_imports)} 个\n"

        if precise_result.collect_all:
            message += f"📋 推荐collect-all: {len(precise_result.collect_all)} 个\n"

        dynamic_data = dynamic_result.get('dynamic_result')
        if dynamic_data:
            if dynamic_data.conditional_modules:
                message += f"❓ 条件导入: {len(dynamic_data.conditional_modules)} 个\n"
            if dynamic_data.lazy_imports:
                message += f"⏰ 延迟导入: {len(dynamic_data.lazy_imports)} 个\n"

        QMessageBox.information(self, "分析完成", message)
