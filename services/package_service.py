"""
打包服务模块
"""
import subprocess
import sys
import os
from typing import Optional, Callable
from PyQt5.QtCore import QThread, pyqtSignal
from models.packer_model import PyInstallerModel

class PackageService(QThread):
    """打包服务类"""

    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal(int)

    def __init__(self, model: PyInstallerModel, python_interpreter: str = ""):
        super().__init__()
        self.model = model
        self.python_interpreter = python_interpreter
        self.process: Optional[subprocess.Popen] = None
        self._is_cancelled = False
    
    def run(self) -> None:
        """执行打包任务"""
        try:
            command = self.model.generate_command(self.python_interpreter)
            if not command:
                self.finished_signal.emit(False, "无法生成打包命令")
                return
            
            self.output_signal.emit(f"执行命令: {command}")
            
            # 创建子进程
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self.process = subprocess.Popen(
                command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=creationflags
            )
            
            # 读取输出
            while True:
                if self._is_cancelled:
                    self.process.terminate()
                    self.finished_signal.emit(False, "打包已取消")
                    return
                
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    self.output_signal.emit(output.strip())
            
            # 检查返回码
            return_code = self.process.poll()
            if return_code == 0:
                self.finished_signal.emit(True, "打包完成")
            else:
                self.finished_signal.emit(False, f"打包失败，返回码: {return_code}")
                
        except Exception as e:
            self.finished_signal.emit(False, f"打包过程中发生错误: {str(e)}")
    
    def cancel(self) -> None:
        """取消打包任务"""
        self._is_cancelled = True
        if self.process and self.process.poll() is None:
            self.process.terminate()

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