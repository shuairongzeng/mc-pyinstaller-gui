"""
菜单栏管理器
"""
import webbrowser
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import QMenuBar, QAction, QMessageBox, QFileDialog
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtGui import QKeySequence

if TYPE_CHECKING:
    from views.main_window import MainWindow

from services.package_service import PyInstallerChecker
from about_dialog import AboutDialog

class MenuBarManager(QObject):
    """菜单栏管理器"""
    
    def __init__(self, main_window: 'MainWindow'):
        super().__init__()
        self.main_window = main_window
        self.menu_bar = main_window.menuBar()
        self.create_menus()
    
    def create_menus(self) -> None:
        """创建菜单"""
        self.create_file_menu()
        self.create_edit_menu()
        self.create_tools_menu()
        self.create_help_menu()
    
    def create_file_menu(self) -> None:
        """创建文件菜单"""
        file_menu = self.menu_bar.addMenu("文件(&F)")
        
        # 新建项目
        new_action = QAction("新建项目(&N)", self.main_window)
        new_action.setShortcut(QKeySequence.New)
        new_action.setStatusTip("创建新的打包项目")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # 打开项目
        open_action = QAction("打开项目(&O)", self.main_window)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("打开已保存的项目配置")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        # 保存项目
        save_action = QAction("保存项目(&S)", self.main_window)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("保存当前项目配置")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        # 另存为
        save_as_action = QAction("另存为(&A)", self.main_window)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip("将项目配置保存到新文件")
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出(&X)", self.main_window)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip("退出程序")
        exit_action.triggered.connect(self.main_window.close)
        file_menu.addAction(exit_action)
    
    def create_edit_menu(self) -> None:
        """创建编辑菜单"""
        edit_menu = self.menu_bar.addMenu("编辑(&E)")
        
        # 清空配置
        clear_action = QAction("清空配置(&C)", self.main_window)
        clear_action.setShortcut("Ctrl+R")
        clear_action.setStatusTip("清空所有配置项")
        clear_action.triggered.connect(self.main_window.clear_config)
        edit_menu.addAction(clear_action)
        
        edit_menu.addSeparator()
        
        # 设置
        settings_action = QAction("设置(&S)", self.main_window)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("打开程序设置")
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)
    
    def create_tools_menu(self) -> None:
        """创建工具菜单"""
        tools_menu = self.menu_bar.addMenu("工具(&T)")
        
        # 检查PyInstaller
        check_action = QAction("检查PyInstaller(&C)", self.main_window)
        check_action.setStatusTip("检查PyInstaller是否正确安装")
        check_action.triggered.connect(self.check_pyinstaller)
        tools_menu.addAction(check_action)
        
        # 安装PyInstaller
        install_action = QAction("安装PyInstaller(&I)", self.main_window)
        install_action.setStatusTip("安装或更新PyInstaller")
        install_action.triggered.connect(self.install_pyinstaller)
        tools_menu.addAction(install_action)
        
        tools_menu.addSeparator()
        
        # 检测所需模块
        detect_action = QAction("检测所需模块(&D)", self.main_window)
        detect_action.setStatusTip("检测脚本文件所需的模块")
        detect_action.triggered.connect(self.detect_modules)
        tools_menu.addAction(detect_action)
        
        tools_menu.addSeparator()
        
        # 打开输出文件夹
        open_output_action = QAction("打开输出文件夹(&O)", self.main_window)
        open_output_action.setStatusTip("打开打包输出文件夹")
        open_output_action.triggered.connect(self.main_window.open_output_folder)
        tools_menu.addAction(open_output_action)
    
    def create_help_menu(self) -> None:
        """创建帮助菜单"""
        help_menu = self.menu_bar.addMenu("帮助(&H)")
        
        # 使用说明
        help_action = QAction("使用说明(&H)", self.main_window)
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.setStatusTip("查看使用说明")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        # PyInstaller文档
        pyinstaller_doc_action = QAction("PyInstaller文档(&P)", self.main_window)
        pyinstaller_doc_action.setStatusTip("打开PyInstaller官方文档")
        pyinstaller_doc_action.triggered.connect(self.open_pyinstaller_docs)
        help_menu.addAction(pyinstaller_doc_action)
        
        help_menu.addSeparator()
        
        # 项目首页
        homepage_action = QAction("项目首页(&G)", self.main_window)
        homepage_action.setStatusTip("打开项目GitHub页面")
        homepage_action.triggered.connect(self.open_homepage)
        help_menu.addAction(homepage_action)
        
        # 报告问题
        issue_action = QAction("报告问题(&I)", self.main_window)
        issue_action.setStatusTip("报告问题或建议")
        issue_action.triggered.connect(self.report_issue)
        help_menu.addAction(issue_action)
        
        help_menu.addSeparator()
        
        # 关于
        about_action = QAction("关于(&A)", self.main_window)
        about_action.setStatusTip("显示关于对话框")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    @pyqtSlot()
    def new_project(self, checked=False) -> None:
        """新建项目"""
        reply = QMessageBox.question(
            self.main_window, "新建项目", 
            "新建项目将清空当前所有配置，是否继续？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.main_window.clear_config()
    
    @pyqtSlot()
    def open_project(self, checked=False) -> None:
        """打开项目"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, "打开项目配置", "",
            "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 加载配置到模型
                self.main_window.model.from_dict(config_data)
                
                # 刷新所有标签页
                if self.main_window.basic_tab:
                    self.main_window.basic_tab.refresh_ui()
                if self.main_window.advanced_tab:
                    self.main_window.advanced_tab.refresh_ui()
                if self.main_window.settings_tab:
                    self.main_window.settings_tab.refresh_ui()
                
                QMessageBox.information(self.main_window, "成功", "项目配置已加载")
            except Exception as e:
                QMessageBox.critical(self.main_window, "错误", f"加载项目配置失败: {str(e)}")
    
    @pyqtSlot()
    def save_project(self, checked=False) -> None:
        """保存项目"""
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "保存项目配置", "project_config.json",
            "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            self._save_project_to_file(file_path)
    
    @pyqtSlot()
    def save_project_as(self, checked=False) -> None:
        """另存为项目"""
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "另存为项目配置", "project_config.json",
            "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            self._save_project_to_file(file_path)
    
    def _save_project_to_file(self, file_path: str) -> None:
        """保存项目到文件"""
        try:
            import json
            config_data = self.main_window.model.to_dict()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self.main_window, "成功", f"项目配置已保存到: {file_path}")
        except Exception as e:
            QMessageBox.critical(self.main_window, "错误", f"保存项目配置失败: {str(e)}")
    
    @pyqtSlot()
    def open_settings(self, checked=False) -> None:
        """打开设置"""
        QMessageBox.information(self.main_window, "设置", "设置功能正在开发中...")

    @pyqtSlot()
    def check_pyinstaller(self, checked=False) -> None:
        """检查PyInstaller"""
        controller = getattr(self.main_window, 'controller', None)
        if controller and controller.check_pyinstaller_installation():
            python_interpreter = controller.config.get("python_interpreter", "")
            env_info = f"在环境 {python_interpreter}" if python_interpreter else "在当前环境"
            QMessageBox.information(self.main_window, "检查结果", f"PyInstaller{env_info}中已正确安装")
        else:
            python_interpreter = controller.config.get("python_interpreter", "") if controller else ""
            env_info = f"在环境 {python_interpreter}" if python_interpreter else "在当前环境"
            reply = QMessageBox.question(
                self.main_window, "检查结果",
                f"PyInstaller{env_info}中未安装或安装不正确，是否现在安装？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.install_pyinstaller()
    
    @pyqtSlot()
    def install_pyinstaller(self, checked=False) -> None:
        """安装PyInstaller"""
        self.main_window.install_pyinstaller()

    @pyqtSlot()
    def detect_modules(self, checked=False) -> None:
        """检测模块"""
        if not self.main_window.model.script_path:
            QMessageBox.warning(self.main_window, "错误", "请先选择要检测的Python脚本")
            return
        
        # 切换到模块标签页
        if self.main_window.module_tab:
            self.main_window.tab_widget.setCurrentWidget(self.main_window.module_tab)
            self.main_window.module_tab.start_detection()
    
    @pyqtSlot()
    def show_help(self, checked=False) -> None:
        """显示帮助"""
        help_text = """
PyInstaller打包工具使用说明

1. 基本设置
   - 选择要打包的Python脚本文件
   - 选择打包类型（单文件或单目录）
   - 选择窗口类型（控制台或窗口）
   - 可选择图标文件和附加文件

2. 高级设置
   - 设置应用程序名称和内容目录
   - 启用UPX压缩
   - 配置隐藏导入和排除模块
   - 添加自定义参数

3. 模块管理
   - 自动检测所需模块
   - 手动管理隐藏导入模块

4. 打包设置
   - 设置输出目录
   - 配置构建选项
   - 预览生成的命令

5. 开始打包
   - 点击"开始打包"按钮
   - 在日志标签页查看打包过程
   - 打包完成后可自动打开输出文件夹
        """
        QMessageBox.information(self.main_window, "使用说明", help_text)

    @pyqtSlot()
    def open_pyinstaller_docs(self, checked=False) -> None:
        """打开PyInstaller文档"""
        webbrowser.open("https://pyinstaller.readthedocs.io/")

    @pyqtSlot()
    def open_homepage(self, checked=False) -> None:
        """打开项目首页"""
        webbrowser.open("https://github.com/xuyou/pyinstaller-gui")

    @pyqtSlot()
    def report_issue(self, checked=False) -> None:
        """报告问题"""
        webbrowser.open("https://github.com/xuyou/pyinstaller-gui/issues")

    @pyqtSlot()
    def show_about(self, checked=False) -> None:
        """显示关于对话框"""
        about_dialog = AboutDialog(self.main_window)
        about_dialog.exec_()
