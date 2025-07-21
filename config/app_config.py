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
        "auto_detect_modules": True,  # 是否自动检测模块
        "use_ast_detection": True,
        "use_pyinstaller_detection": False,
        "python_interpreter": "",  # 自定义Python解释器路径
        "package_timeout": 600,  # 打包超时时间（秒），默认10分钟
        "timeout_warning_enabled": True,  # 是否启用超时警告
        "timeout_auto_suggest": True,  # 是否启用智能超时建议
        "timeout_show_remaining": True,  # 是否显示剩余时间
        "show_detection_notification": True,  # 是否显示检测完成通知
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

    # 超时相关的便捷方法
    def get_package_timeout(self) -> int:
        """获取打包超时时间（秒）"""
        return self.get("package_timeout", 600)

    def set_package_timeout(self, timeout_seconds: int) -> None:
        """设置打包超时时间（秒）"""
        if timeout_seconds < 60:  # 最小1分钟
            timeout_seconds = 60
        elif timeout_seconds > 7200:  # 最大2小时
            timeout_seconds = 7200
        self.set("package_timeout", timeout_seconds)

    def get_timeout_presets(self) -> Dict[str, int]:
        """获取超时时间预设选项"""
        return {
            "快速项目 (5分钟)": 300,
            "小型项目 (10分钟)": 600,
            "中型项目 (20分钟)": 1200,
            "大型项目 (30分钟)": 1800,
            "复杂项目 (1小时)": 3600,
            "超大项目 (2小时)": 7200
        }

    def format_timeout_display(self, timeout_seconds: int) -> str:
        """格式化超时时间显示"""
        if timeout_seconds < 60:
            return f"{timeout_seconds}秒"
        elif timeout_seconds < 3600:
            minutes = timeout_seconds // 60
            seconds = timeout_seconds % 60
            if seconds == 0:
                return f"{minutes}分钟"
            else:
                return f"{minutes}分{seconds}秒"
        else:
            hours = timeout_seconds // 3600
            minutes = (timeout_seconds % 3600) // 60
            if minutes == 0:
                return f"{hours}小时"
            else:
                return f"{hours}小时{minutes}分钟"

    def suggest_timeout_for_project(self, script_path: str = None) -> int:
        """根据项目特征智能建议超时时间"""
        if not script_path or not os.path.exists(script_path):
            return self.get_package_timeout()

        try:
            # 分析项目复杂度
            complexity_score = self._analyze_project_complexity(script_path)

            # 根据复杂度建议超时时间
            if complexity_score < 10:
                return 300  # 5分钟
            elif complexity_score < 25:
                return 600  # 10分钟
            elif complexity_score < 50:
                return 1200  # 20分钟
            elif complexity_score < 100:
                return 1800  # 30分钟
            else:
                return 3600  # 1小时

        except Exception:
            return self.get_package_timeout()

    def _analyze_project_complexity(self, script_path: str) -> int:
        """分析项目复杂度评分"""
        complexity_score = 0

        try:
            project_dir = os.path.dirname(script_path)

            # 统计Python文件数量
            py_files = []
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    if file.endswith('.py'):
                        py_files.append(os.path.join(root, file))

            complexity_score += len(py_files) * 2

            # 检查是否有常见的重型依赖
            heavy_dependencies = [
                'tensorflow', 'torch', 'pytorch', 'numpy', 'scipy', 'pandas',
                'matplotlib', 'opencv', 'cv2', 'sklearn', 'django', 'flask'
            ]

            # 简单检查主脚本中的导入
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                for dep in heavy_dependencies:
                    if f'import {dep}' in content or f'from {dep}' in content:
                        complexity_score += 10

            # 检查项目大小
            total_size = 0
            for py_file in py_files:
                try:
                    total_size += os.path.getsize(py_file)
                except:
                    pass

            # 每MB增加5分
            complexity_score += (total_size // (1024 * 1024)) * 5

        except Exception:
            pass

        return complexity_score