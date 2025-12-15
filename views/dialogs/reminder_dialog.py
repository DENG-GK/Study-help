"""
提醒设置对话框
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from config import COLORS
from controllers.reminder_controller import ReminderController


class ReminderDialog(ctk.CTkToplevel):
    """提醒设置对话框"""

    def __init__(self, parent, todo, reminder_controller, on_close=None, **kwargs):
        """初始化提醒设置对话框

        Args:
            parent: 父窗口
            todo: 待办事项数据
            reminder_controller: 提醒控制器实例
            on_close: 关闭回调
        """
        super().__init__(parent, **kwargs)

        self.todo = todo
        self.reminder_controller = reminder_controller
        self._on_close = on_close

        self.title("⏰ 设置提醒")
        self.geometry("320x400")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=COLORS["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 100}")

        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        # 标题
        title_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0)
        title_frame.pack(fill="x")

        ctk.CTkLabel(
            title_frame,
            text="⏰ 设置提醒",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["accent_blue"]
        ).pack(padx=15, pady=10)

        # 任务名称
        task_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        task_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            task_frame,
            text="任务：",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=15, pady=(10, 0))

        ctk.CTkLabel(
            task_frame,
            text=self.todo.get("text", ""),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
            wraplength=280
        ).pack(anchor="w", padx=15, pady=(5, 10))

        # 快捷提醒选项
        quick_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        quick_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            quick_frame,
            text="⚡ 快捷设置",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["accent_yellow"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        options = ReminderController.get_quick_reminder_options()
        button_frame = ctk.CTkFrame(quick_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        for i, (text, delta) in enumerate(options):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                width=130,
                height=32,
                fg_color=COLORS["bg_input"],
                hover_color=COLORS["accent_blue"],
                command=lambda d=delta: self._set_quick_reminder(d)
            )
            btn.grid(row=row, column=col, padx=5, pady=3)

        # 自定义时间
        custom_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        custom_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            custom_frame,
            text="🕐 自定义时间",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["accent_purple"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        time_input_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        time_input_frame.pack(fill="x", padx=15, pady=(0, 10))

        # 小时选择
        ctk.CTkLabel(
            time_input_frame,
            text="时:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")

        self.hour_var = ctk.StringVar(value=str(datetime.now().hour))
        self.hour_entry = ctk.CTkEntry(
            time_input_frame,
            width=50,
            textvariable=self.hour_var,
            fg_color=COLORS["bg_input"],
            justify="center"
        )
        self.hour_entry.pack(side="left", padx=5)

        # 分钟选择
        ctk.CTkLabel(
            time_input_frame,
            text="分:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(10, 0))

        self.minute_var = ctk.StringVar(value=str((datetime.now().minute // 5 + 1) * 5 % 60))
        self.minute_entry = ctk.CTkEntry(
            time_input_frame,
            width=50,
            textvariable=self.minute_var,
            fg_color=COLORS["bg_input"],
            justify="center"
        )
        self.minute_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            time_input_frame,
            text="设置",
            width=60,
            fg_color=COLORS["accent_green"],
            hover_color="#2ea043",
            command=self._set_custom_reminder
        ).pack(side="left", padx=10)

        # 当前提醒状态
        current_reminder = self.todo.get("reminder_time")
        if current_reminder:
            status_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
            status_frame.pack(fill="x", padx=10, pady=5)

            try:
                reminder_dt = datetime.fromisoformat(current_reminder)
                reminder_str = reminder_dt.strftime("%m-%d %H:%M")
            except:
                reminder_str = current_reminder

            ctk.CTkLabel(
                status_frame,
                text=f"📌 当前提醒: {reminder_str}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["accent_green"]
            ).pack(side="left", padx=15, pady=10)

            ctk.CTkButton(
                status_frame,
                text="取消提醒",
                width=80,
                height=28,
                fg_color=COLORS["accent_red"],
                hover_color="#da3633",
                command=self._cancel_reminder
            ).pack(side="right", padx=15, pady=10)

        # 关闭按钮
        ctk.CTkButton(
            self,
            text="关闭",
            width=100,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            command=self._close
        ).pack(pady=15)

    def _set_quick_reminder(self, delta):
        """设置快捷提醒

        Args:
            delta: timedelta 时间增量
        """
        reminder_time = datetime.now() + delta
        self.reminder_controller.set_reminder(self.todo["id"], reminder_time)
        self._close()

    def _set_custom_reminder(self):
        """设置自定义提醒"""
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())

            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("时间范围无效")

            now = datetime.now()
            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # 如果时间已过，设置为明天
            if reminder_time <= now:
                reminder_time += timedelta(days=1)

            self.reminder_controller.set_reminder(self.todo["id"], reminder_time)
            self._close()
        except ValueError:
            # 显示错误提示（简单处理）
            pass

    def _cancel_reminder(self):
        """取消提醒"""
        self.reminder_controller.cancel_reminder(self.todo["id"])
        self._close()

    def _close(self):
        """关闭对话框"""
        if self._on_close:
            self._on_close()
        self.destroy()
