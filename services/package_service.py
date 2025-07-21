"""
打包服务模块
"""
import subprocess
import sys
import os
import time
import threading
from typing import Optional, Callable
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from models.packer_model import PyInstallerModel
from utils.logger import log_info, log_error, log_warning, report_error
from utils.exceptions import PackageError, handle_exception_with_dialog

class AsyncPackageWorker(QThread):
    """异步打包工作线程"""

    # 信号定义
    progress_updated = pyqtSignal(int)  # 进度更新
    output_received = pyqtSignal(str)   # 输出信息
    error_occurred = pyqtSignal(str)    # 错误信息
    finished_signal = pyqtSignal(bool, str)  # 完成信号
    status_changed = pyqtSignal(str)    # 状态变化信号
    remaining_time_updated = pyqtSignal(int)  # 剩余时间更新（秒）
    timeout_warning = pyqtSignal(int)  # 超时警告（剩余秒数）

    def __init__(self, model: PyInstallerModel, python_interpreter: str = "", timeout: int = None):
        super().__init__()
        self.model = model
        self.python_interpreter = python_interpreter
        # 如果没有指定超时时间，从配置中获取
        self.timeout = timeout if timeout is not None else model.config.get_package_timeout()
        self.process: Optional[subprocess.Popen] = None
        self._cancelled = False
        self.start_time = None
        self.remaining_time_timer = None
        self._start_time = 0

    def run(self) -> None:
        """执行打包任务"""
        try:
            self._start_time = time.time()
            self.start_time = self._start_time  # 为剩余时间监控使用

            # 启动剩余时间监控
            if self.model.config.get("timeout_show_remaining", True):
                self._start_remaining_time_monitor()

            self.status_changed.emit("准备打包...")
            self.output_received.emit("=" * 50)
            self.output_received.emit("开始异步打包过程...")
            self.output_received.emit(f"超时设置: {self.model.config.format_timeout_display(self.timeout)}")
            self.output_received.emit("=" * 50)
            self.progress_updated.emit(5)

            # 验证配置
            self.output_received.emit("正在验证打包配置...")
            errors = self.model.validate_config()
            if errors:
                error_msg = "配置验证失败:\n" + "\n".join(f"  - {error}" for error in errors)
                self.error_occurred.emit(error_msg)
                self.finished_signal.emit(False, "配置验证失败")
                return

            self.output_received.emit("✅ 配置验证通过")
            self.progress_updated.emit(8)

            # 生成打包命令
            self.output_received.emit("正在生成打包命令...")
            command = self.model.generate_command(self.python_interpreter)
            if not command:
                self.error_occurred.emit("无法生成打包命令")
                self.finished_signal.emit(False, "无法生成打包命令")
                return

            self.output_received.emit("✅ 打包命令生成成功")
            self.output_received.emit(f"命令: {command}")
            self.progress_updated.emit(10)
            self.status_changed.emit("正在执行打包...")

            # 执行打包
            self._execute_packaging(command)

        except Exception as e:
            # 生成详细的错误报告
            context = {
                'script_path': self.model.script_path,
                'output_dir': self.model.output_dir,
                'python_interpreter': self.python_interpreter,
                'timeout': self.timeout
            }

            report_id = report_error(
                "PackageProcessError",
                str(e),
                context,
                self._get_stack_trace()
            )

            error_msg = f"打包过程出错: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.finished_signal.emit(False, str(e))

            log_error(f"打包失败，错误报告ID: {report_id}")
        finally:
            # 停止剩余时间监控
            self._stop_remaining_time_monitor()

    def _execute_packaging(self, command: str):
        """执行打包命令"""
        try:
            # 设置工作目录
            work_dir = os.path.dirname(self.model.script_path) if self.model.script_path else os.getcwd()
            self.output_received.emit(f"工作目录: {work_dir}")
            self.output_received.emit("正在启动PyInstaller进程...")

            # 启动进程
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=work_dir,
                creationflags=creationflags,
                bufsize=1  # 行缓冲，确保实时输出
            )

            self.output_received.emit("✅ PyInstaller进程已启动")
            self.output_received.emit("-" * 50)
            self.progress_updated.emit(20)

            # 启动超时监控
            timeout_thread = threading.Thread(target=self._monitor_timeout)
            timeout_thread.daemon = True
            timeout_thread.start()

            # 添加心跳计数器
            line_count = 0
            last_heartbeat = time.time()

            # 实时读取输出
            while True:
                if self._cancelled:
                    self.output_received.emit("⚠️ 用户请求取消打包...")
                    self.process.terminate()
                    self.status_changed.emit("正在取消...")
                    self.finished_signal.emit(False, "用户取消")
                    return

                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break

                if output:
                    line_count += 1
                    # 显示原始输出
                    self.output_received.emit(output.strip())
                    # 根据输出内容更新进度
                    self._update_progress_from_output(output)
                    last_heartbeat = time.time()
                else:
                    # 心跳机制 - 如果长时间没有输出，显示进度信息
                    current_time = time.time()
                    if current_time - last_heartbeat > 5:  # 5秒没有输出
                        elapsed = current_time - self._start_time
                        self.output_received.emit(f"⏱️ 打包进行中... 已用时 {elapsed:.1f}秒，处理了 {line_count} 行输出")
                        last_heartbeat = current_time

            # 显示最终统计
            total_time = time.time() - self._start_time
            self.output_received.emit("-" * 50)
            self.output_received.emit(f"📊 打包统计: 总用时 {total_time:.1f}秒，处理了 {line_count} 行输出")

            # 检查结果
            return_code = self.process.poll()
            if return_code == 0:
                self.progress_updated.emit(100)
                self.status_changed.emit("打包完成")
                self.output_received.emit("🎉 打包成功完成！")
                self.output_received.emit("=" * 50)
                self.finished_signal.emit(True, "打包完成")
            else:
                self.error_occurred.emit(f"打包失败，退出码: {return_code}")
                self.output_received.emit(f"❌ 打包失败，退出码: {return_code}")
                self.output_received.emit("=" * 50)
                self.finished_signal.emit(False, f"打包失败，退出码: {return_code}")

        except Exception as e:
            self.error_occurred.emit(f"执行错误: {str(e)}")
            self.output_received.emit(f"💥 执行异常: {str(e)}")
            self.finished_signal.emit(False, f"执行错误: {str(e)}")

    def _update_progress_from_output(self, output: str):
        """根据输出内容更新进度"""
        output_lower = output.lower()

        # 详细的进度估算逻辑
        if "info: pyinstaller:" in output_lower:
            self.progress_updated.emit(25)
            self.status_changed.emit("PyInstaller 初始化...")
        elif "info: loading module" in output_lower:
            self.progress_updated.emit(30)
            self.status_changed.emit("正在加载模块...")
        elif "info: analyzing" in output_lower:
            self.progress_updated.emit(35)
            self.status_changed.emit("正在分析依赖...")
        elif "info: processing" in output_lower:
            self.progress_updated.emit(40)
            self.status_changed.emit("正在处理文件...")
        elif "info: building exe" in output_lower:
            self.progress_updated.emit(80)
            self.status_changed.emit("正在生成可执行文件...")
        elif "info: building" in output_lower:
            self.progress_updated.emit(50)
            self.status_changed.emit("正在构建...")
        elif "info: collecting" in output_lower:
            self.progress_updated.emit(60)
            self.status_changed.emit("正在收集依赖...")
        elif "info: copying" in output_lower:
            self.progress_updated.emit(70)
            self.status_changed.emit("正在复制文件...")
        elif "info: appending" in output_lower:
            self.progress_updated.emit(75)
            self.status_changed.emit("正在打包资源...")
        elif "successfully created" in output_lower:
            self.progress_updated.emit(95)
            self.status_changed.emit("即将完成...")
        elif "warning:" in output_lower:
            # 警告信息，添加特殊标记
            self.output_received.emit(f"⚠️ {output.strip()}")
        elif "error:" in output_lower:
            # 错误信息，添加特殊标记
            self.output_received.emit(f"❌ {output.strip()}")

    def _monitor_timeout(self):
        """监控超时"""
        while not self._cancelled and self.process and self.process.poll() is None:
            elapsed = time.time() - self._start_time
            if elapsed > self.timeout:
                self.error_occurred.emit(f"打包超时 ({self.timeout}秒)")
                if self.process:
                    self.process.terminate()
                self.finished_signal.emit(False, f"打包超时 ({self.timeout}秒)")
                return
            time.sleep(1)

    def cancel(self) -> None:
        """取消打包"""
        self._cancelled = True
        if self.process:
            self.process.terminate()

    def _get_stack_trace(self) -> str:
        """获取当前堆栈跟踪"""
        import traceback
        return traceback.format_exc()

    def _start_remaining_time_monitor(self):
        """启动剩余时间监控"""
        if self.remaining_time_timer is None:
            self.remaining_time_timer = QTimer()
            self.remaining_time_timer.timeout.connect(self._update_remaining_time)
            self.remaining_time_timer.start(5000)  # 每5秒更新一次

    def _stop_remaining_time_monitor(self):
        """停止剩余时间监控"""
        if self.remaining_time_timer:
            self.remaining_time_timer.stop()
            self.remaining_time_timer = None

    def _update_remaining_time(self):
        """更新剩余时间"""
        if not self.start_time:
            return

        elapsed = time.time() - self.start_time
        remaining = max(0, self.timeout - elapsed)

        # 发送剩余时间信号
        self.remaining_time_updated.emit(int(remaining))

        # 检查是否需要发送超时警告
        if self.model.config.get("timeout_warning_enabled", True):
            warning_threshold = min(300, self.timeout * 0.1)  # 5分钟或10%的时间
            if remaining <= warning_threshold and remaining > 0:
                self.timeout_warning.emit(int(remaining))

        # 如果已经超时，停止监控
        if remaining <= 0:
            self._stop_remaining_time_monitor()


class PackageService(QThread):
    """增强的打包服务类 - 保持向后兼容"""

    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal(int)

    def __init__(self, model: PyInstallerModel, python_interpreter: str = ""):
        super().__init__()
        self.model = model
        self.python_interpreter = python_interpreter
        self.worker: Optional[AsyncPackageWorker] = None
        self._is_cancelled = False

    def run(self) -> None:
        """执行打包任务 - 使用新的异步工作线程"""
        try:
            # 创建异步工作线程
            self.worker = AsyncPackageWorker(self.model, self.python_interpreter)

            # 连接信号
            self.worker.output_received.connect(self.output_signal.emit)
            self.worker.finished_signal.connect(self.finished_signal.emit)
            self.worker.progress_updated.connect(self.progress_signal.emit)
            self.worker.error_occurred.connect(lambda msg: self.output_signal.emit(f"[ERROR] {msg}"))

            # 启动工作线程并等待完成
            self.worker.start()
            self.worker.wait()  # 等待工作线程完成

        except Exception as e:
            self.finished_signal.emit(False, f"打包服务错误: {str(e)}")

    def cancel(self) -> None:
        """取消打包任务"""
        self._is_cancelled = True
        if self.worker:
            self.worker.cancel()


class AsyncPackageService:
    """异步打包服务管理器"""

    def __init__(self, model: PyInstallerModel, python_interpreter: str = "", timeout: int = 300):
        self.model = model
        self.python_interpreter = python_interpreter
        self.timeout = timeout
        self.worker: Optional[AsyncPackageWorker] = None

        # 存储回调函数，在创建worker时连接
        self._callbacks = {
            'progress': None,
            'output': None,
            'error': None,
            'finished': None,
            'status': None
        }

    def start_packaging(self) -> bool:
        """开始异步打包"""
        if self.worker and self.worker.isRunning():
            return False  # 已有任务在运行

        try:
            # 创建工作线程
            self.worker = AsyncPackageWorker(self.model, self.python_interpreter, self.timeout)

            # 立即连接信号
            self._connect_worker_signals()

            # 启动工作线程
            self.worker.start()
            return True
        except Exception as e:
            print(f"启动异步打包失败: {e}")
            return False

    def cancel_packaging(self) -> None:
        """取消打包"""
        if self.worker:
            self.worker.cancel()

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.worker is not None and self.worker.isRunning()

    def connect_signals(self, progress_callback=None, output_callback=None,
                       error_callback=None, finished_callback=None, status_callback=None,
                       remaining_time_callback=None, timeout_warning_callback=None):
        """连接信号回调"""
        # 存储回调函数
        self._callbacks['progress'] = progress_callback
        self._callbacks['output'] = output_callback
        self._callbacks['error'] = error_callback
        self._callbacks['finished'] = finished_callback
        self._callbacks['status'] = status_callback
        self._callbacks['remaining_time'] = remaining_time_callback
        self._callbacks['timeout_warning'] = timeout_warning_callback

        # 如果worker已存在，立即连接
        if self.worker:
            self._connect_worker_signals()

    def _connect_worker_signals(self):
        """连接worker信号到回调函数"""
        if not self.worker:
            return

        if self._callbacks['progress']:
            self.worker.progress_updated.connect(self._callbacks['progress'])
        if self._callbacks['output']:
            self.worker.output_received.connect(self._callbacks['output'])
        if self._callbacks['error']:
            self.worker.error_occurred.connect(self._callbacks['error'])
        if self._callbacks['finished']:
            self.worker.finished_signal.connect(self._callbacks['finished'])
        if self._callbacks['status']:
            self.worker.status_changed.connect(self._callbacks['status'])
        if self._callbacks['remaining_time']:
            self.worker.remaining_time_updated.connect(self._callbacks['remaining_time'])
        if self._callbacks['timeout_warning']:
            self.worker.timeout_warning.connect(self._callbacks['timeout_warning'])


class PyInstallerChecker:
    """PyInstaller检查和安装工具"""

    @staticmethod
    def check_pyinstaller(python_interpreter: str = "") -> bool:
        """检查PyInstaller是否安装"""
        python_exe = python_interpreter or sys.executable
        try:
            result = subprocess.run(
                [python_exe, "-m", "PyInstaller", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def install_pyinstaller(output_callback: Optional[Callable[[str], None]] = None, python_interpreter: str = "") -> bool:
        """安装PyInstaller"""
        python_exe = python_interpreter or sys.executable
        try:
            if output_callback:
                output_callback(f"正在安装PyInstaller到 {python_exe}...")

            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            process = subprocess.Popen(
                [python_exe, "-m", "pip", "install", "PyInstaller"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=creationflags
            )
            
            for line in iter(process.stdout.readline, ''):
                if output_callback:
                    output_callback(line.strip())
            
            process.wait()
            return process.returncode == 0
            
        except Exception as e:
            if output_callback:
                output_callback(f"安装失败: {str(e)}")
            return False