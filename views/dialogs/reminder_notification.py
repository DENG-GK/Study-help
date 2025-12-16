"""
提醒通知对话框
"""

import customtkinter as ctk
from config import get_colors, theme_manager


class ReminderNotification(ctk.CTkToplevel):
    """提醒通知弹窗"""

    def __init__(self, parent, task_text, reminder_time, **kwargs):
        """初始化提醒通知

        Args:
            parent: 父窗口
            task_text: 任务文本
            reminder_time: 提醒时间
        """
        super().__init__(parent, **kwargs)

        colors = get_colors()
        self.title("⏰ 任务提醒")
        self.geometry("350x200")
        self.transient(parent)
        self.configure(fg_color=colors["bg_dark"])

        # 居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 350) // 2
        y = (self.winfo_screenheight() - 200) // 2
        self.geometry(f"+{x}+{y}")

        # 窗口置顶
        self.attributes('-topmost', True)
        self.lift()
        self.focus_force()

        self._create_widgets(task_text, reminder_time)

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

        # 10秒后自动关闭
        self.after(10000, self.destroy)

    def _create_widgets(self, task_text, reminder_time):
        """创建控件"""
        colors = get_colors()

        # 图标和标题
        self.header_frame = ctk.CTkFrame(self, fg_color=colors["accent_yellow"], corner_radius=0)
        self.header_frame.pack(fill="x")

        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="⏰ 任务提醒",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        )
        self.header_label.pack(pady=15)

        # 任务内容
        self.content_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.task_title_label = ctk.CTkLabel(
            self.content_frame,
            text="📋 待完成任务：",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.task_title_label.pack(anchor="w", padx=15, pady=(15, 5))

        self.task_text_label = ctk.CTkLabel(
            self.content_frame,
            text=task_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["text_primary"],
            wraplength=300
        )
        self.task_text_label.pack(anchor="w", padx=15, pady=(0, 15))

        # 关闭按钮
        self.close_btn = ctk.CTkButton(
            self,
            text="知道了",
            width=120,
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"],
            text_color="#ffffff",
            command=self.destroy
        )
        self.close_btn.pack(pady=10)

    def _on_theme_change(self, theme):
        """主题变化回调"""
        self._apply_theme()

    def _apply_theme(self):
        """应用当前主题颜色"""
        colors = get_colors()

        # 更新窗口背景
        self.configure(fg_color=colors["bg_dark"])

        # 更新标题栏
        self.header_frame.configure(fg_color=colors["accent_yellow"])

        # 更新内容区域
        self.content_frame.configure(fg_color=colors["bg_card"])
        self.task_title_label.configure(text_color=colors["text_secondary"])
        self.task_text_label.configure(text_color=colors["text_primary"])

        # 更新关闭按钮
        self.close_btn.configure(fg_color=colors["accent_blue"], hover_color=colors["accent_purple"])

    def destroy(self):
        """销毁对话框"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
