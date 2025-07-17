#!/usr/bin/env python3
"""
示例应用程序 - 用于测试打包功能
这是一个简单的GUI应用程序，可以用来测试PyInstaller打包工具
"""

import sys
import tkinter as tk
from tkinter import messagebox

class ExampleApp:
    """示例应用程序类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("示例应用程序")
        self.root.geometry("400x300")
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 标题标签
        title_label = tk.Label(
            self.root, 
            text="这是一个示例应用程序", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # 说明文本
        info_text = tk.Text(self.root, height=8, width=50)
        info_text.pack(pady=10)
        
        info_content = """这是一个用于测试PyInstaller打包工具的示例程序。

功能特点：
1. 使用tkinter创建GUI界面
2. 包含按钮交互功能
3. 可以显示消息框
4. 适合用来测试打包效果

使用方法：
1. 在PyInstaller GUI工具中选择此文件
2. 配置打包选项
3. 点击"开始打包"按钮
4. 等待打包完成
"""
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # 测试按钮
        test_button = tk.Button(
            button_frame,
            text="测试功能",
            command=self.test_function,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12),
            padx=20
        )
        test_button.pack(side=tk.LEFT, padx=10)
        
        # 关于按钮
        about_button = tk.Button(
            button_frame,
            text="关于",
            command=self.show_about,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12),
            padx=20
        )
        about_button.pack(side=tk.LEFT, padx=10)
        
        # 退出按钮
        exit_button = tk.Button(
            button_frame,
            text="退出",
            command=self.root.quit,
            bg="#f44336",
            fg="white",
            font=("Arial", 12),
            padx=20
        )
        exit_button.pack(side=tk.LEFT, padx=10)
    
    def test_function(self):
        """测试功能"""
        messagebox.showinfo(
            "测试功能", 
            "恭喜！这个示例程序运行正常！\n\n如果您看到这个消息，说明：\n1. 程序已成功打包\n2. 所有依赖都正确包含\n3. GUI功能正常工作"
        )
    
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于", 
            "示例应用程序 v1.0\n\n这是一个用于测试PyInstaller打包工具的示例程序。\n\n作者：PyInstaller GUI工具\n创建时间：2025年"
        )
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = ExampleApp()
        app.run()
    except Exception as e:
        print(f"程序运行出错: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
