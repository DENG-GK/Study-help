"""
学习助手 v2.0 - 科技感桌面待办与番茄钟
作者：哈雷酱 (￣▽￣)
功能：待办管理、番茄钟、分科目学习时长记录、统计图表、单词学习

这是模块化重构后的入口文件。
"""

import customtkinter as ctk
from views import StudyAssistantApp


def main():
    """程序入口"""
    # 设置主题
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # 创建并运行应用
    app = StudyAssistantApp()
    app.mainloop()


if __name__ == "__main__":
    main()
