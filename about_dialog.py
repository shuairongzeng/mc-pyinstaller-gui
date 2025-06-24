"""
关于对话框

@Description: 关于对话框
@Version: 1.0.1
@Author: xuyou & xiaomizha
"""
from datetime import datetime
import webbrowser
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QCursor


class AboutDialog(QDialog):
    """关于对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("关于PyInstaller打包工具")
        self.setFixedSize(750, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        self.create_about_tab(tab_widget)
        self.create_license_tab(tab_widget)
        self.create_system_tab(tab_widget)
        self.create_bottom_buttons(layout)

        self.center_window()

    def create_clickable_label(self, text, url, stylesheet=None):
        label = QLabel(text)
        if stylesheet is None:
            stylesheet = """
                    QLabel { 
                        color: blue;
                        text-decoration: underline;
                    }
                    QLabel:hover {
                        color: darkblue;
                    }
                """
        label.setStyleSheet(stylesheet)
        label.setCursor(QCursor(Qt.PointingHandCursor))
        label.mousePressEvent = lambda event: webbrowser.open(url)
        return label

    def create_about_tab(self, tab_widget):
        """关于选项卡"""
        about_widget = QWidget()
        layout = QVBoxLayout(about_widget)

        title_layout = QHBoxLayout()

        icon_label = QLabel()
        icon_pixmap = QPixmap("icon.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
        title_layout.addWidget(icon_label)

        title_info_layout = QVBoxLayout()
        app_name_label = self.create_clickable_label("PyInstaller打包工具",
                                                     "https://github.com/xuyouer/xuyou-pyinstaller-gui/",
                                                     "QLabel { color: initial; text-decoration: initial; }")
        app_name_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_info_layout.addWidget(app_name_label)
        version_label = QLabel("版本: 1.0.1")
        version_label.setFont(QFont("Arial", 10))
        title_info_layout.addWidget(version_label)
        title_layout.addLayout(title_info_layout)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        description_label = QLabel(
            "这是一个基于PyQt5开发的PyInstaller图形化打包工具，\n"
            "旨在简化Python程序的打包过程，提供直观易用的界面。"
        )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignJustify)
        layout.addWidget(description_label)

        # 作者
        # author_label = QLabel("作者: xuyou & xiaomizha")
        # author_label.setFont(QFont("Arial", 10, QFont.Bold))
        # layout.addWidget(author_label)
        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("作者: "))
        xuyou_label = self.create_clickable_label("xuyou", "https://github.com/xuyouer/")
        author_layout.addWidget(xuyou_label)
        author_layout.addWidget(QLabel("&"))
        xiaomizha_label = self.create_clickable_label("xiaomizha", "https://github.com/xuyouer/")
        author_layout.addWidget(xiaomizha_label)
        author_layout.addStretch()
        author_widget = QWidget()
        author_widget.setLayout(author_layout)
        layout.addWidget(author_widget)

        # 开发信息
        # dev_info_label = QLabel(
        #     "开发语言: Python https://www.python.org/\n"
        #     "GUI框架: PyQt5 https://www.riverbankcomputing.com/software/pyqt/\n"
        #     "打包工具: PyInstaller https://pyinstaller.org/"
        # )
        # layout.addWidget(dev_info_label)
        dev_info_layout = QVBoxLayout()
        python_layout = QHBoxLayout()
        python_layout.addWidget(QLabel("开发语言: "))
        python_label = self.create_clickable_label("Python", "https://www.python.org/")
        python_layout.addWidget(python_label)
        python_layout.addStretch()
        pyqt5_layout = QHBoxLayout()
        pyqt5_layout.addWidget(QLabel("GUI框架: "))
        pyqt5_label = self.create_clickable_label("PyQt5", "https://www.riverbankcomputing.com/software/pyqt/")
        pyqt5_layout.addWidget(pyqt5_label)
        pyqt5_layout.addStretch()
        pyinstaller_layout = QHBoxLayout()
        pyinstaller_layout.addWidget(QLabel("打包工具: "))
        pyinstaller_label = self.create_clickable_label("PyInstaller", "https://www.pyinstaller.org/")
        pyinstaller_layout.addWidget(pyinstaller_label)
        pyinstaller_layout.addStretch()
        dev_info_layout.addLayout(python_layout)
        dev_info_layout.addLayout(pyqt5_layout)
        dev_info_layout.addLayout(pyinstaller_layout)
        dev_info_widget = QWidget()
        dev_info_widget.setLayout(dev_info_layout)
        layout.addWidget(dev_info_widget)

        # 版权信息
        # current_year = datetime.now().year
        # copyright_label = QLabel(f"Copyright © 2020-{current_year} xuyou & xiaomizha. All rights reserved.")
        # copyright_label.setFont(QFont("Arial", 9))
        # copyright_label.setStyleSheet("color: gray;")
        # layout.addWidget(copyright_label)
        copyright_layout = QHBoxLayout()
        current_year = datetime.now().year
        copyright_layout.addWidget(QLabel(f"Copyright © 2020-{current_year} "))
        xuyou_copyright = self.create_clickable_label("xuyou", "https://github.com/xuyouer/")
        copyright_layout.addWidget(xuyou_copyright)
        copyright_layout.addWidget(QLabel(","))
        xiaomizha_copyright = self.create_clickable_label("xiaomizha", "https://github.com/xuyouer/")
        copyright_layout.addWidget(xiaomizha_copyright)
        copyright_layout.addWidget(QLabel("., Ltd. All rights reserved."))
        copyright_layout.addStretch()
        copyright_widget = QWidget()
        copyright_widget.setLayout(copyright_layout)
        copyright_widget.setFont(QFont("Arial", 12, QFont.Bold))
        copyright_widget.setStyleSheet("color: gray;")
        layout.addWidget(copyright_widget)

        layout.addStretch()

        tab_widget.addTab(about_widget, "关于")

    def create_license_tab(self, tab_widget):
        """许可证选项卡"""
        license_widget = QWidget()
        layout = QVBoxLayout(license_widget)

        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setText(
            "MIT License\n\n"

            "Copyright (c) 2025 xuyouer\n\n"

            "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
            "of this software and associated documentation files (the \"Software\"), to deal\n"
            "in the Software without restriction, including without limitation the rights\n"
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
            "copies of the Software, and to permit persons to whom the Software is\n"
            "furnished to do so, subject to the following conditions:\n\n"

            "The above copyright notice and this permission notice shall be included in all\n"
            "copies or substantial portions of the Software.\n\n"

            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
            "SOFTWARE.\n\n"
            "本软件使用的第三方库:\n"
            "- PyQt5: 遵循GPL v3许可证\n"
            "- PyInstaller: 遵循GPL v2许可证\n"
        )
        layout.addWidget(license_text)

        tab_widget.addTab(license_widget, "许可证")

    def create_system_tab(self, tab_widget):
        """系统信息选项卡"""
        system_widget = QWidget()
        layout = QVBoxLayout(system_widget)

        system_text = QTextEdit()
        system_text.setReadOnly(True)

        import sys
        import platform

        system_info = f"""系统信息:
操作系统: {platform.system()} {platform.release()}
架构: {platform.machine()}
处理器: {platform.processor()}

Python版本: {sys.version}
Python路径: {sys.executable}

PyQt5信息:
"""

        try:
            from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
            system_info += f"Qt版本: {QT_VERSION_STR}\n"
            system_info += f"PyQt5版本: {PYQT_VERSION_STR}\n"
        except ImportError:
            system_info += "PyQt5版本信息获取失败\n"

        system_info += "\nPyInstaller信息:\n"
        try:
            import subprocess
            result = subprocess.run(
                ["pyinstaller", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                system_info += f"PyInstaller版本: {result.stdout.strip()}\n"
            else:
                system_info += "PyInstaller未安装或不在PATH中\n"
        except Exception as e:
            system_info += f"PyInstaller检查失败: {str(e)}\n"

        system_text.setText(system_info)
        layout.addWidget(system_text)

        tab_widget.addTab(system_widget, "系统信息")

    def create_bottom_buttons(self, layout):
        """底部按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        ok_button.setMinimumWidth(80)

        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

    def center_window(self):
        """窗口居中"""
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        else:
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.desktop().screenGeometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
