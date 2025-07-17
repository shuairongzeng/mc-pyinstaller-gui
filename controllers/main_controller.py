"""
主控制器
"""
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QMessageBox

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel
from services.package_service import PackageService, PyInstallerChecker
from services.module_detector import ModuleDetector

class MainController(QObject):
    """主控制器类"""
    
    def __init__(self, config: AppConfig, model: PyInstallerModel):
        super().__init__()
        self.config = config
        self.model = model
        self.package_service: Optional[PackageService] = None
        self.module_detector = ModuleDetector(
            use_ast=config.get("use_ast_detection", True),
            use_pyinstaller=config.get("use_pyinstaller_detection", False),
            python_interpreter=config.get("python_interpreter", "")
        )
    
    def validate_before_package(self) -> bool:
        """打包前验证"""
        errors = self.model.validate_config()
        if errors:
            error_msg = "\n".join(errors)
            QMessageBox.warning(None, "配置错误", f"请修正以下错误:\n{error_msg}")
            return False
        return True
    
    def check_pyinstaller_installation(self) -> bool:
        """检查PyInstaller安装状态"""
        python_interpreter = self.config.get("python_interpreter", "")
        return PyInstallerChecker.check_pyinstaller(python_interpreter)

    def install_pyinstaller(self, output_callback=None) -> bool:
        """安装PyInstaller"""
        python_interpreter = self.config.get("python_interpreter", "")
        return PyInstallerChecker.install_pyinstaller(output_callback, python_interpreter)
    
    def create_package_service(self) -> PackageService:
        """创建打包服务"""
        python_interpreter = self.config.get("python_interpreter", "")
        self.package_service = PackageService(self.model, python_interpreter)
        return self.package_service
    
    def get_module_detector(self) -> ModuleDetector:
        """获取模块检测器"""
        return self.module_detector
    
    def update_detector_settings(self, use_ast: bool, use_pyinstaller: bool, python_interpreter: str = "") -> None:
        """更新检测器设置"""
        self.module_detector.use_ast = use_ast
        self.module_detector.use_pyinstaller = use_pyinstaller
        if python_interpreter:
            self.module_detector.python_interpreter = python_interpreter
        self.config.set("use_ast_detection", use_ast)
        self.config.set("use_pyinstaller_detection", use_pyinstaller)
        if python_interpreter:
            self.config.set("python_interpreter", python_interpreter)
    
    def save_config(self) -> None:
        """保存配置"""
        self.config.save_config()
    
    def load_project_config(self, file_path: str) -> bool:
        """加载项目配置"""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            self.model.from_dict(config_data)
            return True
        except Exception as e:
            QMessageBox.critical(None, "错误", f"加载项目配置失败: {str(e)}")
            return False
    
    def save_project_config(self, file_path: str) -> bool:
        """保存项目配置"""
        try:
            import json
            config_data = self.model.to_dict()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.critical(None, "错误", f"保存项目配置失败: {str(e)}")
            return False
