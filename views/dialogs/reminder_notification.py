"""
提醒通知对话框
"""

import customtkinter as ctk
from config import COLORS


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

        self.title("⏰ 任务提醒")
        self.geometry("350x200")
        self.transient(parent)
        self.configure(fg_color=COLORS["bg_dark"])

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

        # 5秒后自动关闭
        self.after(10000, self.destroy)

    def _create_widgets(self, task_text, reminder_time):
        """创建控件"""
        # 图标和标题
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["accent_yellow"], corner_radius=0)
        header_frame.pack(fill="x")

        ctk.CTkLabel(
            header_frame,
            text="⏰ 任务提醒",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#000000"
        ).pack(pady=15)

        # 任务内容
        content_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            content_frame,
            text="📋 待完成任务：",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            content_frame,
            text=task_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"],
            wraplength=300
        ).pack(anchor="w", padx=15, pady=(0, 15))

        # 关闭按钮
        ctk.CTkButton(
            self,
            text="知道了",
            width=120,
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=self.destroy
        ).pack(pady=10)
