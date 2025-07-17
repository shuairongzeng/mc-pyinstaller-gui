"""
PyInstaller打包工具

@Description: 基于PyQt5开发的PyInstaller图形化打包工具
@Version: 1.0.1
@Author: xuyou & xiaomizha
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from config.app_config import AppConfig
from models.packer_model import PyInstallerModel
from views.main_window import MainWindow
from controllers.main_controller import MainController
from utils.logger import log_info, log_error, log_exception


def main():
    """主函数"""
    try:
        # 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName(AppConfig.APP_NAME)
        app.setApplicationVersion(AppConfig.APP_VERSION)
        
        # 设置应用程序图标
        if os.path.exists("icon.png"):
            app.setWindowIcon(QIcon("icon.png"))
        
        log_info(f"启动 {AppConfig.APP_NAME} v{AppConfig.APP_VERSION}")
        
        # 创建配置和模型
        config = AppConfig()
        model = PyInstallerModel(config)

        # 创建控制器
        controller = MainController(config, model)

        # 创建主窗口
        main_window = MainWindow(config, model, controller)
        main_window.show()
        
        log_info("应用程序启动成功")
        
        # 运行应用程序
        exit_code = app.exec_()
        
        log_info(f"应用程序退出，退出码: {exit_code}")
        return exit_code
        
    except Exception as e:
        log_exception(f"应用程序启动失败: {str(e)}")
        try:
            QMessageBox.critical(None, "启动错误", f"应用程序启动失败:\n{str(e)}")
        except:
            print(f"应用程序启动失败: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
