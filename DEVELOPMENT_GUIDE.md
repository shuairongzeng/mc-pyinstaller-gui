# PyInstaller GUI 项目开发指导文档

## 📋 项目概述

本文档为 PyInstaller GUI 项目的完整开发指导，基于深度项目分析制定，包含详细的优化计划、任务进度跟踪和实施指南。

### 项目基本信息
- **项目名称**: PyInstaller 打包工具
- **版本**: 1.0.1
- **技术栈**: Python 3.x + PyQt5 + PyInstaller
- **架构模式**: MVC (Model-View-Controller)
- **开发状态**: 生产就绪，需要优化

## 🎯 开发目标

### 短期目标 (1-2个月)
- 优化核心功能性能和稳定性
- 提升用户体验和界面现代化
- 完善错误处理和异常管理

### 中期目标 (3-6个月)
- 实现高级功能和扩展性
- 建立完善的测试体系
- 优化代码质量和架构

### 长期目标 (6个月以上)
- 构建插件生态系统
- 支持云端功能
- 建立社区和文档体系

## 📊 任务进度跟踪

### 🟢 已完成任务
- [x] **项目优化分析** (100%)
  - 完成项目架构分析
  - 识别优化机会和改进点
  - 制定详细的实施计划

### 🟡 进行中任务
- [/] **创建开发指导文档** (80%)
  - 完成文档框架设计
  - 正在编写详细实施指南
  - 待完成：代码示例和最佳实践

### 🔴 待开始任务

#### 优先级1：核心功能优化 (预计4-6周)
- [ ] **异步打包处理** (0%)
  - 估计工时：2周
  - 负责人：待分配
  - 依赖：无
  
- [ ] **智能依赖检测优化** (0%)
  - 估计工时：2-3周
  - 负责人：待分配
  - 依赖：无
  
- [ ] **错误处理增强** (0%)
  - 估计工时：1-2周
  - 负责人：待分配
  - 依赖：异步打包处理

#### 优先级2：用户体验提升 (预计3-4周)
- [ ] **界面现代化** (0%)
  - 估计工时：2-3周
  - 负责人：待分配
  - 依赖：核心功能优化完成
  
- [ ] **功能增强** (0%)
  - 估计工时：1-2周
  - 负责人：待分配
  - 依赖：界面现代化

#### 优先级3：扩展功能 (预计6-8周)
- [ ] **高级功能开发** (0%)
  - 估计工时：4-5周
  - 负责人：待分配
  - 依赖：用户体验提升完成
  
- [ ] **开发者工具** (0%)
  - 估计工时：2-3周
  - 负责人：待分配
  - 依赖：高级功能开发

## 🚀 详细实施计划

### 阶段一：核心功能优化 (4-6周)

#### 1.1 异步打包处理 (2周)

**目标**: 将同步打包过程改为异步执行，提升用户体验

**技术要求**:
- 使用 QThread 或 QRunnable 实现后台处理
- 实现进度回调和状态更新
- 支持打包过程的取消操作
- 添加超时处理机制

**实施步骤**:
1. **第1-2天**: 设计异步架构
   - 创建 `AsyncPackageWorker` 类
   - 定义信号和槽机制
   - 设计进度回调接口

2. **第3-5天**: 实现核心功能
   - 重构 `PackageService` 类
   - 实现异步执行逻辑
   - 添加进度追踪功能

3. **第6-8天**: UI集成和测试
   - 更新主窗口的打包逻辑
   - 实现进度条和状态显示
   - 添加取消按钮功能

4. **第9-10天**: 测试和优化
   - 单元测试和集成测试
   - 性能优化和错误处理
   - 文档更新

**验收标准**:
- [ ] 打包过程不阻塞UI界面
- [ ] 实时显示打包进度
- [ ] 支持取消正在进行的打包
- [ ] 异常情况下能正确恢复

**关键文件**:
- `services/async_package_service.py` (新建)
- `views/main_window.py` (修改)
- `controllers/main_controller.py` (修改)

#### 1.2 智能依赖检测优化 (2-3周)

**目标**: 提升模块检测的准确性和性能

**技术要求**:
- 优化AST解析算法
- 添加缓存机制
- 支持常见框架的预设配置
- 实现依赖冲突检测

**实施步骤**:
1. **第1-3天**: 算法优化
   - 分析现有检测算法的性能瓶颈
   - 实现增量检测机制
   - 添加结果缓存功能

2. **第4-7天**: 预设配置系统
   - 创建框架配置模板
   - 实现配置自动匹配
   - 添加用户自定义配置

3. **第8-12天**: 冲突检测功能
   - 实现依赖关系分析
   - 添加版本兼容性检查
   - 提供解决方案建议

4. **第13-15天**: 性能优化和测试
   - 并行处理优化
   - 内存使用优化
   - 全面测试验证

**验收标准**:
- [ ] 检测速度提升50%以上
- [ ] 支持主流框架自动配置
- [ ] 能识别并提示依赖冲突
- [ ] 缓存机制正常工作

**关键文件**:
- `services/enhanced_module_detector.py` (新建)
- `config/framework_templates.py` (新建)
- `services/dependency_analyzer.py` (新建)

#### 1.3 错误处理增强 (1-2周)

**目标**: 建立统一的异常处理机制

**技术要求**:
- 创建全局异常处理器
- 实现详细的错误诊断
- 提供自动修复建议
- 添加错误报告功能

**实施步骤**:
1. **第1-2天**: 异常处理架构设计
2. **第3-5天**: 实现核心处理逻辑
3. **第6-8天**: 集成到现有系统
4. **第9-10天**: 测试和文档

**验收标准**:
- [ ] 统一的异常处理机制
- [ ] 用户友好的错误提示
- [ ] 自动修复建议功能
- [ ] 错误日志和报告

### 阶段二：用户体验提升 (3-4周)

#### 2.1 界面现代化 (2-3周)

**目标**: 提升界面的现代感和易用性

**技术要求**:
- 采用Material Design设计语言
- 实现暗色主题支持
- 响应式布局设计
- 动画和过渡效果

**实施步骤**:
1. **第1-3天**: 设计系统建立
2. **第4-8天**: 组件重构和样式应用
3. **第9-12天**: 主题系统实现
4. **第13-15天**: 测试和优化

**验收标准**:
- [ ] 现代化的视觉设计
- [ ] 完整的暗色主题支持
- [ ] 响应式布局适配
- [ ] 流畅的动画效果

#### 2.2 功能增强 (1-2周)

**目标**: 添加实用的交互功能

**技术要求**:
- 拖拽文件支持
- 配置模板系统
- 历史记录管理
- 快捷键支持

**实施步骤**:
1. **第1-3天**: 拖拽功能实现
2. **第4-6天**: 模板系统开发
3. **第7-9天**: 历史记录功能
4. **第10天**: 快捷键和测试

**验收标准**:
- [ ] 支持拖拽文件到界面
- [ ] 配置模板保存和加载
- [ ] 历史记录查看和恢复
- [ ] 常用快捷键支持

### 阶段三：扩展功能 (6-8周)

#### 3.1 高级功能开发 (4-5周)

**目标**: 实现高级功能和扩展性

**技术要求**:
- 多环境支持
- 云端配置同步
- 插件系统架构
- API接口设计

#### 3.2 开发者工具 (2-3周)

**目标**: 提供开发和调试工具

**技术要求**:
- 调试模式
- 性能分析工具
- 自动化测试框架
- 日志分析工具

## 📝 开发规范

### 代码规范
- 遵循PEP 8编码规范
- 使用类型注解 (Type Hints)
- 编写完整的文档字符串
- 保持函数和类的单一职责

### 测试规范
- 单元测试覆盖率 > 80%
- 集成测试覆盖主要功能
- UI测试覆盖关键交互
- 性能测试验证优化效果

### 版本控制
- 使用语义化版本号
- 详细的提交信息
- 功能分支开发模式
- 代码审查机制

## 🔧 开发环境配置

### 必需工具
- Python 3.8+
- PyQt5 5.15+
- PyInstaller 5.0+
- Git

### 推荐工具
- VS Code / PyCharm
- Black (代码格式化)
- Pylint (代码检查)
- Pytest (测试框架)

### 环境设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行项目
python run.py
```

## 📚 参考资源

### 技术文档
- [PyQt5 官方文档](https://doc.qt.io/qtforpython/)
- [PyInstaller 文档](https://pyinstaller.readthedocs.io/)
- [Python 类型注解指南](https://docs.python.org/3/library/typing.html)

### 设计资源
- [Material Design 指南](https://material.io/design)
- [Qt Style Sheets](https://doc.qt.io/qt-5/stylesheet.html)

## 💻 技术实现指南

### 异步打包处理实现示例

#### 创建异步工作线程

```python
# services/async_package_service.py
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from typing import Optional, Callable
import subprocess
import os

class AsyncPackageWorker(QThread):
    """异步打包工作线程"""

    # 信号定义
    progress_updated = pyqtSignal(int)  # 进度更新
    output_received = pyqtSignal(str)   # 输出信息
    error_occurred = pyqtSignal(str)    # 错误信息
    finished_signal = pyqtSignal(bool, str)  # 完成信号

    def __init__(self, model, python_interpreter=""):
        super().__init__()
        self.model = model
        self.python_interpreter = python_interpreter
        self.process: Optional[subprocess.Popen] = None
        self._cancelled = False

    def run(self):
        """执行打包任务"""
        try:
            self.output_received.emit("开始准备打包...")
            self.progress_updated.emit(10)

            # 生成打包命令
            command = self.model.generate_command()
            if not command:
                self.error_occurred.emit("无法生成打包命令")
                return

            self.output_received.emit(f"执行命令: {command}")
            self.progress_updated.emit(20)

            # 执行打包
            self._execute_packaging(command)

        except Exception as e:
            self.error_occurred.emit(f"打包过程出错: {str(e)}")
            self.finished_signal.emit(False, str(e))

    def _execute_packaging(self, command: str):
        """执行打包命令"""
        try:
            # 设置工作目录
            work_dir = os.path.dirname(self.model.script_path)

            # 启动进程
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=work_dir
            )

            # 实时读取输出
            while True:
                if self._cancelled:
                    self.process.terminate()
                    self.finished_signal.emit(False, "用户取消")
                    return

                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break

                if output:
                    self.output_received.emit(output.strip())
                    # 根据输出内容更新进度
                    self._update_progress_from_output(output)

            # 检查结果
            return_code = self.process.poll()
            if return_code == 0:
                self.progress_updated.emit(100)
                self.finished_signal.emit(True, "打包完成")
            else:
                self.finished_signal.emit(False, f"打包失败，退出码: {return_code}")

        except Exception as e:
            self.finished_signal.emit(False, f"执行错误: {str(e)}")

    def _update_progress_from_output(self, output: str):
        """根据输出内容更新进度"""
        # 简单的进度估算逻辑
        if "INFO: Building" in output:
            self.progress_updated.emit(40)
        elif "INFO: Collecting" in output:
            self.progress_updated.emit(60)
        elif "INFO: Building EXE" in output:
            self.progress_updated.emit(80)
        elif "successfully created" in output:
            self.progress_updated.emit(95)

    def cancel(self):
        """取消打包"""
        self._cancelled = True
        if self.process:
            self.process.terminate()
```

#### 集成到主窗口

```python
# views/main_window.py (修改部分)
def start_package(self) -> None:
    """开始打包 - 异步版本"""
    # 验证配置
    if not self.model.script_path:
        QMessageBox.warning(self, "错误", "请选择要打包的Python脚本")
        return

    # 清空上一次的日志
    if self.log_tab:
        self.log_tab.clear_log()

    # 切换到日志标签页
    self.tab_widget.setCurrentWidget(self.log_tab)

    # 创建异步工作线程
    python_interpreter = self.config.get("python_interpreter", "")
    self.package_worker = AsyncPackageWorker(self.model, python_interpreter)

    # 连接信号
    self.package_worker.progress_updated.connect(self.log_tab.update_progress)
    self.package_worker.output_received.connect(self.log_tab.append_log)
    self.package_worker.error_occurred.connect(self.log_tab.append_error)
    self.package_worker.finished_signal.connect(self.on_package_finished)

    # 更新UI状态
    self.start_package_btn.setEnabled(False)
    self.cancel_package_btn.setEnabled(True)

    # 启动异步任务
    self.package_worker.start()

def cancel_package(self) -> None:
    """取消打包"""
    if hasattr(self, 'package_worker') and self.package_worker.isRunning():
        self.package_worker.cancel()
        self.log_tab.append_log("正在取消打包...")
```

### 智能依赖检测优化实现

#### 增强的模块检测器

```python
# services/enhanced_module_detector.py
import ast
import os
import sys
import json
import hashlib
from typing import Set, Dict, List, Optional, Tuple
from pathlib import Path
import importlib.util

class EnhancedModuleDetector:
    """增强的模块检测器"""

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.framework_configs = self._load_framework_configs()
        self._detection_cache: Dict[str, Set[str]] = {}

    def detect_modules_with_cache(self, script_path: str) -> Set[str]:
        """带缓存的模块检测"""
        # 计算文件哈希
        file_hash = self._calculate_file_hash(script_path)
        cache_file = self.cache_dir / f"modules_{file_hash}.json"

        # 尝试从缓存加载
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    return set(cached_data['modules'])
            except Exception:
                pass  # 缓存损坏，重新检测

        # 执行检测
        modules = self._detect_modules_enhanced(script_path)

        # 保存到缓存
        try:
            cache_data = {
                'modules': list(modules),
                'timestamp': os.path.getmtime(script_path),
                'file_hash': file_hash
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except Exception:
            pass  # 缓存保存失败不影响主功能

        return modules

    def _detect_modules_enhanced(self, script_path: str) -> Set[str]:
        """增强的模块检测逻辑"""
        modules = set()

        # AST静态分析
        ast_modules = self._ast_analysis(script_path)
        modules.update(ast_modules)

        # 框架特定检测
        framework_modules = self._detect_framework_modules(script_path, ast_modules)
        modules.update(framework_modules)

        # 动态导入检测
        dynamic_modules = self._detect_dynamic_imports(script_path)
        modules.update(dynamic_modules)

        return modules

    def _detect_framework_modules(self, script_path: str, detected_modules: Set[str]) -> Set[str]:
        """检测框架特定的模块"""
        additional_modules = set()

        for framework, config in self.framework_configs.items():
            # 检查是否使用了该框架
            if any(module in detected_modules for module in config.get('indicators', [])):
                # 添加框架相关的隐藏导入
                additional_modules.update(config.get('hidden_imports', []))

                # 添加数据文件
                data_files = config.get('data_files', [])
                for data_file in data_files:
                    # 这里可以添加数据文件处理逻辑
                    pass

        return additional_modules

    def _load_framework_configs(self) -> Dict:
        """加载框架配置"""
        return {
            'django': {
                'indicators': ['django', 'django.core', 'django.conf'],
                'hidden_imports': [
                    'django.core.management',
                    'django.contrib.auth',
                    'django.contrib.contenttypes',
                    'django.contrib.sessions',
                    'django.contrib.messages',
                    'django.contrib.staticfiles'
                ],
                'data_files': ['templates', 'static']
            },
            'flask': {
                'indicators': ['flask', 'flask.app'],
                'hidden_imports': [
                    'flask.json',
                    'flask.logging',
                    'jinja2.ext'
                ],
                'data_files': ['templates', 'static']
            },
            'opencv': {
                'indicators': ['cv2'],
                'hidden_imports': [
                    'numpy.core._multiarray_umath',
                    'numpy.core._multiarray_tests',
                    'numpy.linalg._umath_linalg',
                    'numpy.fft._pocketfft_internal'
                ]
            },
            'matplotlib': {
                'indicators': ['matplotlib', 'matplotlib.pyplot'],
                'hidden_imports': [
                    'matplotlib.backends.backend_tkagg',
                    'matplotlib.backends.backend_qt5agg',
                    'matplotlib.figure',
                    'matplotlib.font_manager'
                ],
                'data_files': ['matplotlib/mpl-data']
            }
        }

    def analyze_dependencies(self, script_path: str) -> Dict:
        """分析依赖关系和冲突"""
        detected_modules = self.detect_modules_with_cache(script_path)

        analysis = {
            'detected_modules': detected_modules,
            'missing_modules': set(),
            'conflicted_modules': set(),
            'recommendations': []
        }

        # 检查模块是否可用
        for module in detected_modules:
            if not self._is_module_available(module):
                analysis['missing_modules'].add(module)

        # 检查版本冲突
        conflicts = self._check_version_conflicts(detected_modules)
        analysis['conflicted_modules'].update(conflicts)

        # 生成建议
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def _is_module_available(self, module_name: str) -> bool:
        """检查模块是否可用"""
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ValueError, ModuleNotFoundError):
            return False

    def _check_version_conflicts(self, modules: Set[str]) -> Set[str]:
        """检查版本冲突"""
        # 这里可以实现更复杂的版本冲突检测逻辑
        conflicts = set()

        # 示例：检查已知的冲突组合
        known_conflicts = {
            ('tensorflow', 'tensorflow-gpu'): "TensorFlow和TensorFlow-GPU不能同时安装",
            ('opencv-python', 'opencv-contrib-python'): "建议只安装opencv-contrib-python"
        }

        for conflict_pair, message in known_conflicts.items():
            if all(module in modules for module in conflict_pair):
                conflicts.update(conflict_pair)

        return conflicts

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []

        if analysis['missing_modules']:
            recommendations.append(
                f"发现 {len(analysis['missing_modules'])} 个缺失模块，"
                f"建议安装: {', '.join(list(analysis['missing_modules'])[:5])}"
            )

        if analysis['conflicted_modules']:
            recommendations.append(
                f"发现 {len(analysis['conflicted_modules'])} 个冲突模块，"
                "建议检查版本兼容性"
            )

        # 根据检测到的框架提供建议
        detected = analysis['detected_modules']
        if 'django' in detected:
            recommendations.append("检测到Django项目，建议启用collect-all选项")

        if 'numpy' in detected or 'pandas' in detected:
            recommendations.append("检测到科学计算库，建议增加内存限制")

        return recommendations
```

### 错误处理增强实现

#### 全局异常处理器

```python
# utils/exception_handler.py
import sys
import traceback
import logging
from typing import Optional, Callable, Dict, Any
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QObject, pyqtSignal

class GlobalExceptionHandler(QObject):
    """全局异常处理器"""

    exception_occurred = pyqtSignal(str, str)  # 异常类型, 异常信息

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.error_solutions = self._load_error_solutions()

        # 设置全局异常处理
        sys.excepthook = self.handle_exception

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 允许Ctrl+C正常退出
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # 格式化异常信息
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        error_type = exc_type.__name__

        # 记录日志
        self.logger.error(f"未处理的异常: {error_type}\n{error_msg}")

        # 查找解决方案
        solution = self._find_solution(error_type, str(exc_value))

        # 发送信号
        self.exception_occurred.emit(error_type, str(exc_value))

        # 显示用户友好的错误对话框
        self._show_error_dialog(error_type, str(exc_value), solution)

    def _load_error_solutions(self) -> Dict[str, Dict[str, Any]]:
        """加载错误解决方案"""
        return {
            'ModuleNotFoundError': {
                'pattern': 'No module named',
                'solution': '缺少必要的Python模块',
                'actions': [
                    '检查requirements.txt文件',
                    '运行: pip install -r requirements.txt',
                    '确认虚拟环境已激活'
                ]
            },
            'FileNotFoundError': {
                'pattern': 'No such file or directory',
                'solution': '找不到指定的文件或目录',
                'actions': [
                    '检查文件路径是否正确',
                    '确认文件是否存在',
                    '检查文件权限'
                ]
            },
            'PermissionError': {
                'pattern': 'Permission denied',
                'solution': '权限不足',
                'actions': [
                    '以管理员身份运行程序',
                    '检查文件/目录权限',
                    '确认文件未被其他程序占用'
                ]
            },
            'PyInstallerError': {
                'pattern': 'PyInstaller',
                'solution': 'PyInstaller打包错误',
                'actions': [
                    '检查PyInstaller版本',
                    '清理build和dist目录',
                    '检查隐藏导入配置',
                    '查看详细错误日志'
                ]
            }
        }

    def _find_solution(self, error_type: str, error_message: str) -> Optional[Dict[str, Any]]:
        """查找错误解决方案"""
        # 精确匹配错误类型
        if error_type in self.error_solutions:
            solution = self.error_solutions[error_type]
            if solution['pattern'] in error_message:
                return solution

        # 模糊匹配错误信息
        for solution_type, solution in self.error_solutions.items():
            if solution['pattern'].lower() in error_message.lower():
                return solution

        return None

    def _show_error_dialog(self, error_type: str, error_message: str, solution: Optional[Dict]):
        """显示错误对话框"""
        try:
            app = QApplication.instance()
            if not app:
                return

            # 创建错误对话框
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("程序错误")

            # 设置主要信息
            msg_box.setText(f"程序遇到了一个错误：{error_type}")

            # 设置详细信息
            if solution:
                detail_text = f"错误描述：{error_message}\n\n"
                detail_text += f"可能的解决方案：{solution['solution']}\n\n"
                detail_text += "建议操作：\n"
                for i, action in enumerate(solution['actions'], 1):
                    detail_text += f"{i}. {action}\n"
            else:
                detail_text = f"错误详情：{error_message}\n\n"
                detail_text += "建议：\n1. 重启程序\n2. 检查日志文件\n3. 联系技术支持"

            msg_box.setDetailedText(detail_text)

            # 添加按钮
            msg_box.addButton("确定", QMessageBox.AcceptRole)
            if solution and 'auto_fix' in solution:
                msg_box.addButton("自动修复", QMessageBox.ActionRole)

            msg_box.exec_()

        except Exception as e:
            # 异常处理器本身出错时的后备方案
            print(f"异常处理器错误: {e}")
            print(f"原始错误: {error_type}: {error_message}")
```

## 🧪 测试策略和实施

### 测试框架配置

#### 安装测试依赖
```bash
pip install pytest pytest-qt pytest-cov pytest-mock
```

#### 测试目录结构
```
tests/
├── __init__.py
├── conftest.py                 # pytest配置
├── unit/                       # 单元测试
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/                # 集成测试
│   ├── test_packaging_flow.py
│   └── test_ui_integration.py
├── ui/                        # UI测试
│   ├── test_main_window.py
│   └── test_dialogs.py
└── fixtures/                  # 测试数据
    ├── sample_scripts/
    └── config_files/
```

#### 单元测试示例

```python
# tests/unit/test_models.py
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from models.packer_model import PyInstallerModel
from config.app_config import AppConfig

class TestPyInstallerModel:
    """PyInstallerModel单元测试"""

    @pytest.fixture
    def config(self):
        """测试配置"""
        return AppConfig()

    @pytest.fixture
    def model(self, config):
        """测试模型"""
        return PyInstallerModel(config)

    def test_model_initialization(self, model):
        """测试模型初始化"""
        assert model.script_path == ""
        assert model.is_one_file == True
        assert model.is_windowed == False
        assert isinstance(model.additional_files, list)

    def test_validate_config_empty_script(self, model):
        """测试空脚本路径验证"""
        errors = model.validate_config()
        assert "请选择要打包的Python脚本文件" in errors

    def test_validate_config_nonexistent_script(self, model):
        """测试不存在的脚本文件验证"""
        model.script_path = "nonexistent.py"
        errors = model.validate_config()
        assert any("脚本文件不存在" in error for error in errors)

    def test_validate_config_valid_script(self, model):
        """测试有效脚本验证"""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b'print("Hello World")')
            temp_script = f.name

        try:
            model.script_path = temp_script
            errors = model.validate_config()
            # 应该没有关于脚本路径的错误
            assert not any("脚本文件" in error for error in errors)
        finally:
            os.unlink(temp_script)

    def test_generate_command_basic(self, model):
        """测试基本命令生成"""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            temp_script = f.name

        try:
            model.script_path = temp_script
            model.output_dir = "./dist"
            model.is_one_file = True

            command = model.generate_command()

            assert "pyinstaller" in command.lower()
            assert "--onefile" in command
            assert temp_script in command
        finally:
            os.unlink(temp_script)

    @patch('os.path.exists')
    def test_generate_command_with_icon(self, mock_exists, model):
        """测试带图标的命令生成"""
        mock_exists.return_value = True

        model.script_path = "test.py"
        model.icon_path = "icon.ico"

        command = model.generate_command()
        assert "--icon=icon.ico" in command
```

#### UI测试示例

```python
# tests/ui/test_main_window.py
import pytest
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from views.main_window import MainWindow
from config.app_config import AppConfig
from models.packer_model import PyInstallerModel

@pytest.fixture(scope="session")
def qapp():
    """创建QApplication实例"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app

class TestMainWindow:
    """主窗口UI测试"""

    @pytest.fixture
    def main_window(self, qapp):
        """创建主窗口"""
        config = AppConfig()
        model = PyInstallerModel(config)
        window = MainWindow(config, model)
        window.show()
        return window

    def test_window_title(self, main_window):
        """测试窗口标题"""
        expected_title = f"{AppConfig.APP_NAME} v{AppConfig.APP_VERSION}"
        assert main_window.windowTitle() == expected_title

    def test_tabs_creation(self, main_window):
        """测试标签页创建"""
        tab_widget = main_window.tab_widget
        assert tab_widget.count() == 5  # 基本、高级、模块、设置、日志

        tab_titles = [tab_widget.tabText(i) for i in range(tab_widget.count())]
        expected_titles = ["基本设置", "高级设置", "模块管理", "打包设置", "打包日志"]
        assert tab_titles == expected_titles

    def test_buttons_exist(self, main_window):
        """测试按钮存在性"""
        assert hasattr(main_window, 'start_package_btn')
        assert hasattr(main_window, 'cancel_package_btn')
        assert hasattr(main_window, 'generate_cmd_btn')
        assert hasattr(main_window, 'clear_config_btn')

    def test_start_package_button_click(self, main_window, qtbot):
        """测试开始打包按钮点击"""
        # 模拟按钮点击
        qtbot.mouseClick(main_window.start_package_btn, Qt.LeftButton)

        # 验证错误提示（因为没有选择脚本）
        # 这里需要检查是否显示了警告对话框
        # 实际实现中可能需要mock QMessageBox

    def test_clear_config_button(self, main_window, qtbot):
        """测试清空配置按钮"""
        # 设置一些配置
        main_window.model.script_path = "test.py"
        main_window.model.is_one_file = False

        # 点击清空按钮（需要处理确认对话框）
        with patch('PyQt5.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):
            qtbot.mouseClick(main_window.clear_config_btn, Qt.LeftButton)

        # 验证配置被清空
        assert main_window.model.script_path == ""
        assert main_window.model.is_one_file == True
```

### 性能测试和基准测试

#### 模块检测性能测试

```python
# tests/performance/test_module_detection_performance.py
import pytest
import time
import tempfile
import os
from services.enhanced_module_detector import EnhancedModuleDetector

class TestModuleDetectionPerformance:
    """模块检测性能测试"""

    @pytest.fixture
    def large_script(self):
        """创建大型测试脚本"""
        script_content = """
import os
import sys
import json
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import datasets
from tensorflow import keras
import torch
import cv2
from PyQt5.QtWidgets import QApplication
import django
from flask import Flask

# 大量的函数和类定义
""" + "\n".join([f"def function_{i}(): pass" for i in range(1000)])

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            return f.name

    def test_detection_speed(self, large_script):
        """测试检测速度"""
        detector = EnhancedModuleDetector()

        # 第一次检测（无缓存）
        start_time = time.time()
        modules_first = detector.detect_modules_with_cache(large_script)
        first_duration = time.time() - start_time

        # 第二次检测（有缓存）
        start_time = time.time()
        modules_second = detector.detect_modules_with_cache(large_script)
        second_duration = time.time() - start_time

        # 验证结果一致性
        assert modules_first == modules_second

        # 验证缓存效果（第二次应该更快）
        assert second_duration < first_duration * 0.1  # 至少快10倍

        # 性能基准
        assert first_duration < 5.0  # 首次检测应在5秒内完成
        assert second_duration < 0.1  # 缓存检测应在0.1秒内完成

        print(f"首次检测: {first_duration:.3f}s, 缓存检测: {second_duration:.3f}s")
        print(f"检测到 {len(modules_first)} 个模块")

        # 清理
        os.unlink(large_script)
```

## 📈 性能监控和优化

### 性能监控工具

#### 内存使用监控

```python
# utils/performance_monitor.py
import psutil
import time
import threading
from typing import Dict, List, Callable, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

class PerformanceMonitor(QObject):
    """性能监控器"""

    stats_updated = pyqtSignal(dict)  # 统计信息更新信号

    def __init__(self, interval: int = 1000):  # 1秒间隔
        super().__init__()
        self.interval = interval
        self.timer = QTimer()
        self.timer.timeout.connect(self._collect_stats)
        self.process = psutil.Process()
        self.start_time = time.time()
        self.peak_memory = 0
        self.stats_history: List[Dict] = []

    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
        self.timer.start(self.interval)

    def stop_monitoring(self):
        """停止监控"""
        self.timer.stop()

    def _collect_stats(self):
        """收集性能统计"""
        try:
            # CPU使用率
            cpu_percent = self.process.cpu_percent()

            # 内存使用
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            self.peak_memory = max(self.peak_memory, memory_mb)

            # 线程数
            thread_count = self.process.num_threads()

            # 运行时间
            runtime = time.time() - self.start_time

            stats = {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_mb,
                'peak_memory_mb': self.peak_memory,
                'thread_count': thread_count,
                'runtime_seconds': runtime,
                'timestamp': time.time()
            }

            self.stats_history.append(stats)

            # 只保留最近100个记录
            if len(self.stats_history) > 100:
                self.stats_history.pop(0)

            self.stats_updated.emit(stats)

        except Exception as e:
            print(f"性能监控错误: {e}")

    def get_summary(self) -> Dict:
        """获取性能摘要"""
        if not self.stats_history:
            return {}

        cpu_values = [s['cpu_percent'] for s in self.stats_history]
        memory_values = [s['memory_mb'] for s in self.stats_history]

        return {
            'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
            'max_cpu_percent': max(cpu_values),
            'avg_memory_mb': sum(memory_values) / len(memory_values),
            'peak_memory_mb': self.peak_memory,
            'total_runtime': self.stats_history[-1]['runtime_seconds'],
            'sample_count': len(self.stats_history)
        }
```

### 代码质量检查配置

#### pylint配置文件

```ini
# .pylintrc
[MASTER]
init-hook='import sys; sys.path.append(".")'
jobs=1
load-plugins=
persistent=yes
suggestion-mode=yes
unsafe-load-any-extension=no

[MESSAGES CONTROL]
confidence=
disable=C0330,C0326,R0903,R0913,W0613,C0103,R0801

[REPORTS]
evaluation=10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)
output-format=text
reports=no
score=yes

[REFACTORING]
max-nested-blocks=5
never-returning-functions=sys.exit

[BASIC]
argument-naming-style=snake_case
attr-naming-style=snake_case
bad-names=foo,bar,baz,toto,tutu,tata
class-attribute-naming-style=any
class-naming-style=PascalCase
const-naming-style=UPPER_CASE
function-naming-style=snake_case
good-names=i,j,k,ex,Run,_
include-naming-hint=no
inlinevar-naming-style=any
method-naming-style=snake_case
module-naming-style=snake_case
variable-naming-style=snake_case

[FORMAT]
expected-line-ending-format=
ignore-long-lines=^\s*(# )?<?https?://\S+>?$
indent-after-paren=4
indent-string='    '
max-line-length=100
max-module-lines=1000
single-line-class-stmt=no
single-line-if-stmt=no

[LOGGING]
logging-format-style=old
logging-modules=logging

[MISCELLANEOUS]
notes=FIXME,XXX,TODO

[SIMILARITIES]
ignore-comments=yes
ignore-docstrings=yes
ignore-imports=no
min-similarity-lines=4

[SPELLING]
max-spelling-suggestions=4
spelling-dict=
spelling-ignore-words=
spelling-private-dict-file=
spelling-store-unknown-words=no

[STRING]
check-str-concat-over-line-jumps=no

[TYPECHECK]
contextmanager-decorators=contextlib.contextmanager
generated-members=
ignore-mixin-members=yes
ignore-none=yes
ignore-on-opaque-inference=yes
ignored-classes=optparse.Values,thread._local,_thread._local
ignored-modules=
missing-member-hint=yes
missing-member-hint-distance=1
missing-member-max-choices=1

[VARIABLES]
additional-builtins=
allow-global-unused-variables=yes
callbacks=cb_,_cb
dummy-variables-rgx=_+$|(_[a-zA-Z0-9_]*[a-zA-Z0-9]+?$)|dummy|^ignored_|^unused_
ignored-argument-names=_.*|^ignored_|^unused_
init-import=no
redefining-builtins-modules=six.moves,past.builtins,future.builtins,builtins,io

[CLASSES]
defining-attr-methods=__init__,__new__,setUp,__post_init__
exclude-protected=_asdict,_fields,_replace,_source,_make
valid-classmethod-first-arg=cls
valid-metaclass-classmethod-first-arg=cls
```

#### GitHub Actions CI配置

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install system dependencies (Ubuntu)
      if: matrix.os == 'ubuntu-latest'
      run: |
        sudo apt-get update
        sudo apt-get install -y xvfb

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Lint with pylint
      run: |
        pylint --rcfile=.pylintrc **/*.py

    - name: Format check with black
      run: |
        black --check --diff .

    - name: Type check with mypy
      run: |
        mypy --config-file=mypy.ini .

    - name: Test with pytest
      run: |
        pytest --cov=. --cov-report=xml --cov-report=html
      env:
        QT_QPA_PLATFORM: offscreen

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true

  build:
    needs: test
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Build executable
      run: |
        python build_optimized.py

    - name: Test executable
      run: |
        ./dist/PyInstaller-GUI.exe --version

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: PyInstaller-GUI-${{ github.sha }}
        path: dist/
```

## 📋 项目进度跟踪表

### 开发里程碑

| 里程碑 | 目标日期 | 状态 | 完成度 | 负责人 | 备注 |
|--------|----------|------|--------|--------|------|
| 项目分析完成 | 2025-01-21 | ✅ 完成 | 100% | 分析团队 | 已识别所有优化点 |
| 开发文档完成 | 2025-01-21 | 🟡 进行中 | 90% | 文档团队 | 待完善部分细节 |
| 核心功能优化 | 2025-03-01 | ⏳ 计划中 | 0% | 待分配 | 包含异步处理等 |
| 用户体验提升 | 2025-03-15 | ⏳ 计划中 | 0% | 待分配 | UI现代化改造 |
| 扩展功能开发 | 2025-04-30 | ⏳ 计划中 | 0% | 待分配 | 高级功能实现 |
| 测试完善 | 2025-05-15 | ⏳ 计划中 | 0% | 测试团队 | 全面测试覆盖 |
| 文档完善 | 2025-05-30 | ⏳ 计划中 | 0% | 文档团队 | 用户手册等 |
| 正式发布 | 2025-06-15 | ⏳ 计划中 | 0% | 发布团队 | v2.0版本发布 |

### 详细任务进度

#### 优先级1：核心功能优化 (预计4-6周)

| 任务 | 预计工时 | 开始日期 | 结束日期 | 状态 | 完成度 | 阻塞问题 |
|------|----------|----------|----------|------|--------|----------|
| 异步打包处理 | 2周 | TBD | TBD | ⏳ 待开始 | 0% | 需要分配开发人员 |
| 智能依赖检测优化 | 2-3周 | TBD | TBD | ⏳ 待开始 | 0% | 需要算法设计 |
| 错误处理增强 | 1-2周 | TBD | TBD | ⏳ 待开始 | 0% | 依赖异步处理完成 |

#### 优先级2：用户体验提升 (预计3-4周)

| 任务 | 预计工时 | 开始日期 | 结束日期 | 状态 | 完成度 | 阻塞问题 |
|------|----------|----------|----------|------|--------|----------|
| 界面现代化 | 2-3周 | TBD | TBD | ⏳ 待开始 | 0% | 需要UI设计师 |
| 功能增强 | 1-2周 | TBD | TBD | ⏳ 待开始 | 0% | 依赖界面现代化 |

#### 优先级3：扩展功能 (预计6-8周)

| 任务 | 预计工时 | 开始日期 | 结束日期 | 状态 | 完成度 | 阻塞问题 |
|------|----------|----------|----------|------|--------|----------|
| 高级功能开发 | 4-5周 | TBD | TBD | ⏳ 待开始 | 0% | 需要架构设计 |
| 开发者工具 | 2-3周 | TBD | TBD | ⏳ 待开始 | 0% | 依赖高级功能 |

## 🎯 最佳实践指南

### 代码开发最佳实践

#### 1. 代码结构和组织

```python
# 推荐的文件头部注释格式
"""
模块名称：异步打包服务
功能描述：提供异步的PyInstaller打包功能
作者：开发团队
创建日期：2025-01-21
最后修改：2025-01-21
版本：1.0.0
"""

# 导入顺序：标准库 -> 第三方库 -> 本地模块
import os
import sys
from typing import Optional, List, Dict

from PyQt5.QtCore import QThread, pyqtSignal
import pyinstaller

from config.app_config import AppConfig
from utils.logger import log_info, log_error
```

#### 2. 函数和类设计原则

```python
class AsyncPackageService:
    """
    异步打包服务类

    职责：
    - 管理异步打包任务
    - 提供进度回调
    - 处理打包错误

    使用示例：
        service = AsyncPackageService(model)
        service.progress_updated.connect(callback)
        service.start_packaging()
    """

    def __init__(self, model: PyInstallerModel, config: AppConfig):
        """
        初始化异步打包服务

        Args:
            model: 打包配置模型
            config: 应用配置

        Raises:
            ValueError: 当model或config为None时
        """
        if not model or not config:
            raise ValueError("model和config参数不能为None")

        self.model = model
        self.config = config
        self._worker: Optional[AsyncPackageWorker] = None

    def start_packaging(self) -> bool:
        """
        开始异步打包

        Returns:
            bool: 成功启动返回True，否则返回False

        Raises:
            RuntimeError: 当已有打包任务在运行时
        """
        if self._worker and self._worker.isRunning():
            raise RuntimeError("已有打包任务在运行中")

        try:
            self._worker = AsyncPackageWorker(self.model)
            self._worker.start()
            return True
        except Exception as e:
            log_error(f"启动打包任务失败: {e}")
            return False
```

#### 3. 错误处理模式

```python
# 推荐的错误处理模式
def process_file(file_path: str) -> Optional[Dict]:
    """
    处理文件的推荐错误处理模式
    """
    try:
        # 参数验证
        if not file_path:
            raise ValueError("文件路径不能为空")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 主要逻辑
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        result = {"content": content, "size": len(content)}
        log_info(f"成功处理文件: {file_path}")
        return result

    except (ValueError, FileNotFoundError) as e:
        # 预期的错误，记录并重新抛出
        log_error(f"文件处理参数错误: {e}")
        raise

    except PermissionError as e:
        # 权限错误，提供友好的错误信息
        log_error(f"文件访问权限不足: {file_path}")
        raise RuntimeError(f"无法访问文件，请检查权限: {file_path}") from e

    except Exception as e:
        # 未预期的错误，记录详细信息
        log_error(f"处理文件时发生未知错误: {file_path}, 错误: {e}")
        raise RuntimeError(f"文件处理失败: {file_path}") from e
```

#### 4. 测试编写指南

```python
# 测试类命名和组织
class TestAsyncPackageService:
    """异步打包服务测试类"""

    @pytest.fixture
    def mock_model(self):
        """创建模拟的打包模型"""
        model = Mock(spec=PyInstallerModel)
        model.script_path = "test.py"
        model.output_dir = "./dist"
        model.validate_config.return_value = []
        model.generate_command.return_value = "pyinstaller test.py"
        return model

    @pytest.fixture
    def service(self, mock_model):
        """创建测试用的服务实例"""
        config = AppConfig()
        return AsyncPackageService(mock_model, config)

    def test_init_with_valid_params(self, mock_model):
        """测试正常初始化"""
        config = AppConfig()
        service = AsyncPackageService(mock_model, config)

        assert service.model == mock_model
        assert service.config == config
        assert service._worker is None

    def test_init_with_none_model(self):
        """测试model为None的情况"""
        config = AppConfig()

        with pytest.raises(ValueError, match="model和config参数不能为None"):
            AsyncPackageService(None, config)

    def test_start_packaging_success(self, service, mock_model):
        """测试成功启动打包"""
        with patch('services.async_package_service.AsyncPackageWorker') as MockWorker:
            mock_worker = Mock()
            MockWorker.return_value = mock_worker

            result = service.start_packaging()

            assert result is True
            MockWorker.assert_called_once_with(mock_model)
            mock_worker.start.assert_called_once()

    def test_start_packaging_already_running(self, service):
        """测试重复启动打包的情况"""
        # 模拟已有任务在运行
        service._worker = Mock()
        service._worker.isRunning.return_value = True

        with pytest.raises(RuntimeError, match="已有打包任务在运行中"):
            service.start_packaging()
```

### UI开发最佳实践

#### 1. 组件设计原则

```python
class ModernButton(QPushButton):
    """现代化按钮组件"""

    def __init__(self, text: str, button_type: str = "primary", parent=None):
        """
        初始化现代化按钮

        Args:
            text: 按钮文本
            button_type: 按钮类型 (primary, secondary, danger)
            parent: 父组件
        """
        super().__init__(text, parent)
        self.button_type = button_type
        self._setup_style()
        self._setup_animations()

    def _setup_style(self):
        """设置按钮样式"""
        styles = {
            "primary": """
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                    color: #757575;
                }
            """,
            "secondary": """
                QPushButton {
                    background-color: transparent;
                    color: #2196F3;
                    border: 1px solid #2196F3;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #E3F2FD;
                }
            """,
            "danger": """
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
            """
        }

        self.setStyleSheet(styles.get(self.button_type, styles["primary"]))

    def _setup_animations(self):
        """设置按钮动画效果"""
        # 这里可以添加QPropertyAnimation等动画效果
        pass
```

#### 2. 响应式布局设计

```python
class ResponsiveLayout(QVBoxLayout):
    """响应式布局管理器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.breakpoints = {
            'small': 600,
            'medium': 960,
            'large': 1280
        }
        self.current_size = 'large'

    def resizeEvent(self, event):
        """处理窗口大小变化"""
        width = event.size().width()

        new_size = 'large'
        if width < self.breakpoints['small']:
            new_size = 'small'
        elif width < self.breakpoints['medium']:
            new_size = 'medium'

        if new_size != self.current_size:
            self.current_size = new_size
            self._adjust_layout()

    def _adjust_layout(self):
        """根据屏幕大小调整布局"""
        if self.current_size == 'small':
            # 小屏幕：垂直布局，隐藏部分元素
            self.setDirection(QBoxLayout.TopToBottom)
        elif self.current_size == 'medium':
            # 中等屏幕：混合布局
            pass
        else:
            # 大屏幕：水平布局，显示所有元素
            self.setDirection(QBoxLayout.LeftToRight)
```

### 性能优化最佳实践

#### 1. 内存管理

```python
class ResourceManager:
    """资源管理器"""

    def __init__(self):
        self._resources: Dict[str, Any] = {}
        self._cleanup_callbacks: List[Callable] = []

    def register_resource(self, name: str, resource: Any, cleanup_callback: Optional[Callable] = None):
        """注册资源"""
        self._resources[name] = resource
        if cleanup_callback:
            self._cleanup_callbacks.append(cleanup_callback)

    def get_resource(self, name: str) -> Optional[Any]:
        """获取资源"""
        return self._resources.get(name)

    def cleanup(self):
        """清理所有资源"""
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                log_error(f"资源清理失败: {e}")

        self._resources.clear()
        self._cleanup_callbacks.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

# 使用示例
def process_large_data():
    """处理大量数据的示例"""
    with ResourceManager() as rm:
        # 注册需要清理的资源
        large_data = load_large_dataset()
        rm.register_resource("dataset", large_data, lambda: del large_data)

        temp_files = create_temp_files()
        rm.register_resource("temp_files", temp_files, cleanup_temp_files)

        # 处理数据
        result = process_data(large_data)
        return result
        # 资源会在退出时自动清理
```

#### 2. 缓存策略

```python
from functools import lru_cache
import time
from typing import Any, Dict, Optional

class TimedCache:
    """带过期时间的缓存"""

    def __init__(self, default_ttl: int = 300):  # 5分钟默认过期时间
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if time.time() > entry['expires']:
            del self._cache[key]
            return None

        return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        ttl = ttl or self.default_ttl
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }

    def clear_expired(self) -> None:
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires']
        ]

        for key in expired_keys:
            del self._cache[key]

# 使用装饰器实现方法缓存
def cached_method(ttl: int = 300):
    """方法缓存装饰器"""
    def decorator(func):
        cache = TimedCache(ttl)

        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"

            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper
    return decorator

# 使用示例
class ModuleDetector:
    @cached_method(ttl=600)  # 缓存10分钟
    def detect_modules(self, script_path: str) -> Set[str]:
        """检测模块（带缓存）"""
        # 实际的检测逻辑
        return self._do_detection(script_path)
```

## 📚 学习资源和参考文档

### 技术文档链接

#### Python开发
- [Python官方文档](https://docs.python.org/3/)
- [PEP 8 编码规范](https://pep8.org/)
- [Python类型注解指南](https://docs.python.org/3/library/typing.html)
- [asyncio异步编程](https://docs.python.org/3/library/asyncio.html)

#### PyQt5开发
- [PyQt5官方文档](https://doc.qt.io/qtforpython/)
- [Qt样式表参考](https://doc.qt.io/qt-5/stylesheet.html)
- [Qt信号槽机制](https://doc.qt.io/qt-5/signalsandslots.html)
- [Qt多线程编程](https://doc.qt.io/qt-5/threads.html)

#### PyInstaller
- [PyInstaller官方文档](https://pyinstaller.readthedocs.io/)
- [PyInstaller高级用法](https://pyinstaller.readthedocs.io/en/stable/advanced-topics.html)
- [PyInstaller钩子编写](https://pyinstaller.readthedocs.io/en/stable/hooks.html)

#### 测试和质量保证
- [pytest文档](https://docs.pytest.org/)
- [pytest-qt插件](https://pytest-qt.readthedocs.io/)
- [coverage.py文档](https://coverage.readthedocs.io/)
- [pylint文档](https://pylint.pycqa.org/)

### 设计资源

#### UI/UX设计
- [Material Design指南](https://material.io/design)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Fluent Design System](https://www.microsoft.com/design/fluent/)

#### 图标和素材
- [Material Design Icons](https://materialdesignicons.com/)
- [Feather Icons](https://feathericons.com/)
- [Unsplash](https://unsplash.com/) - 免费图片素材

### 开发工具推荐

#### IDE和编辑器
- [PyCharm Professional](https://www.jetbrains.com/pycharm/) - 功能最全面的Python IDE
- [Visual Studio Code](https://code.visualstudio.com/) - 轻量级但功能强大
- [Sublime Text](https://www.sublimetext.com/) - 快速响应的文本编辑器

#### 调试和分析工具
- [pdb](https://docs.python.org/3/library/pdb.html) - Python内置调试器
- [memory_profiler](https://pypi.org/project/memory-profiler/) - 内存使用分析
- [py-spy](https://github.com/benfred/py-spy) - 性能分析工具
- [Qt Creator](https://www.qt.io/product/development-tools) - Qt应用开发和调试

---

**文档版本**: 1.0
**最后更新**: 2025-01-21
**维护者**: 开发团队
