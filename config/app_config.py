"""
应用程序配置管理模块
"""
from typing import Dict, Any
import json
import os

class AppConfig:
    """应用程序配置管理类"""
    
    # 应用程序基本信息
    APP_NAME = "PyInstaller打包工具"
    APP_VERSION = "1.0.1"
    APP_AUTHOR = "xuyou & xiaomizha"
    
    # 默认配置
    DEFAULT_CONFIG = {
        "output_dir": os.path.abspath("./dist"),
        "is_one_file": True,
        "is_windowed": False,
        "enable_upx": False,
        "clean": False,
        "log_level": "INFO",
        "open_output_after_build": True,
        "auto_detect_modules": True,
        "use_ast_detection": True,
        "use_pyinstaller_detection": False,
        "python_interpreter": "",  # 自定义Python解释器路径
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def save_config(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        self.config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """批量更新配置"""
        self.config.update(config_dict)