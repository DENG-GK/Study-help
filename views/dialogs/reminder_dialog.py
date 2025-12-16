"""
提醒设置对话框
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from config import get_colors, theme_manager
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

        colors = get_colors()
        self.title("⏰ 设置提醒")
        self.geometry("340x520")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=colors["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 50}")

        self._create_widgets()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        # 标题
        self.title_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=0)
        self.title_frame.pack(fill="x")

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="⏰ 设置提醒",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["accent_blue"]
        )
        self.title_label.pack(padx=15, pady=10)

        # 任务名称
        self.task_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.task_frame.pack(fill="x", padx=10, pady=10)

        self.task_title_label = ctk.CTkLabel(
            self.task_frame,
            text="任务：",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.task_title_label.pack(anchor="w", padx=15, pady=(10, 0))

        self.task_text_label = ctk.CTkLabel(
            self.task_frame,
            text=self.todo.get("text", ""),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"],
            wraplength=280
        )
        self.task_text_label.pack(anchor="w", padx=15, pady=(5, 10))

        # 快捷提醒选项
        self.quick_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.quick_frame.pack(fill="x", padx=10, pady=5)

        self.quick_title_label = ctk.CTkLabel(
            self.quick_frame,
            text="⚡ 快捷设置",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["accent_yellow"]
        )
        self.quick_title_label.pack(anchor="w", padx=15, pady=(10, 5))

        options = ReminderController.get_quick_reminder_options()
        self.button_frame = ctk.CTkFrame(self.quick_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.quick_btns = []
        for i, (text, delta) in enumerate(options):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(
                self.button_frame,
                text=text,
                width=130,
                height=32,
                fg_color=colors["bg_input"],
                hover_color=colors["accent_blue"],
                text_color=colors["text_primary"],
                command=lambda d=delta: self._set_quick_reminder(d)
            )
            btn.grid(row=row, column=col, padx=5, pady=3)
            self.quick_btns.append(btn)

        # 自定义时间
        self.custom_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.custom_frame.pack(fill="x", padx=10, pady=5)

        self.custom_title_label = ctk.CTkLabel(
            self.custom_frame,
            text="🕐 自定义时间",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["accent_purple"]
        )
        self.custom_title_label.pack(anchor="w", padx=15, pady=(10, 5))

        self.time_input_frame = ctk.CTkFrame(self.custom_frame, fg_color="transparent")
        self.time_input_frame.pack(fill="x", padx=15, pady=(5, 15))

        # 小时选择
        self.hour_label = ctk.CTkLabel(
            self.time_input_frame,
            text="时:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["text_secondary"]
        )
        self.hour_label.pack(side="left")

        self.hour_var = ctk.StringVar(value=str(datetime.now().hour))
        self.hour_entry = ctk.CTkEntry(
            self.time_input_frame,
            width=70,
            height=42,
            textvariable=self.hour_var,
            fg_color=colors["bg_input"],
            text_color=colors["text_primary"],
            font=ctk.CTkFont(size=18, weight="bold"),
            justify="center"
        )
        self.hour_entry.pack(side="left", padx=8)

        # 分钟选择
        self.minute_label = ctk.CTkLabel(
            self.time_input_frame,
            text="分:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["text_secondary"]
        )
        self.minute_label.pack(side="left", padx=(10, 0))

        self.minute_var = ctk.StringVar(value=str((datetime.now().minute // 5 + 1) * 5 % 60))
        self.minute_entry = ctk.CTkEntry(
            self.time_input_frame,
            width=70,
            height=42,
            textvariable=self.minute_var,
            fg_color=colors["bg_input"],
            text_color=colors["text_primary"],
            font=ctk.CTkFont(size=18, weight="bold"),
            justify="center"
        )
        self.minute_entry.pack(side="left", padx=8)

        self.set_btn = ctk.CTkButton(
            self.time_input_frame,
            text="确定",
            width=70,
            height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=colors["accent_green"],
            hover_color="#2ea043",
            text_color="#ffffff",
            command=self._set_custom_reminder
        )
        self.set_btn.pack(side="left", padx=(15, 0))

        # 当前提醒状态
        self.status_frame = None
        self.status_label = None
        self.cancel_btn = None
        current_reminder = self.todo.get("reminder_time")
        if current_reminder:
            self._create_status_frame(current_reminder)

        # 关闭按钮
        self.close_btn = ctk.CTkButton(
            self,
            text="关闭",
            width=100,
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=self._close
        )
        self.close_btn.pack(pady=15)

    def _create_status_frame(self, current_reminder):
        """创建当前提醒状态框架"""
        colors = get_colors()

        self.status_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.status_frame.pack(fill="x", padx=10, pady=5)

        try:
            reminder_dt = datetime.fromisoformat(current_reminder)
            reminder_str = reminder_dt.strftime("%m-%d %H:%M")
        except:
            reminder_str = current_reminder

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text=f"📌 当前提醒: {reminder_str}",
            font=ctk.CTkFont(size=12),
            text_color=colors["accent_green"]
        )
        self.status_label.pack(side="left", padx=15, pady=10)

        self.cancel_btn = ctk.CTkButton(
            self.status_frame,
            text="取消提醒",
            width=80,
            height=28,
            fg_color=colors["accent_red"],
            hover_color="#da3633",
            text_color="#ffffff",
            command=self._cancel_reminder
        )
        self.cancel_btn.pack(side="right", padx=15, pady=10)

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

    def _on_theme_change(self, theme):
        """主题变化回调"""
        self._apply_theme()

    def _apply_theme(self):
        """应用当前主题颜色"""
        colors = get_colors()

        # 更新窗口背景
        self.configure(fg_color=colors["bg_dark"])

        # 更新标题区域
        self.title_frame.configure(fg_color=colors["bg_card"])
        self.title_label.configure(text_color=colors["accent_blue"])

        # 更新任务区域
        self.task_frame.configure(fg_color=colors["bg_card"])
        self.task_title_label.configure(text_color=colors["text_secondary"])
        self.task_text_label.configure(text_color=colors["text_primary"])

        # 更新快捷设置区域
        self.quick_frame.configure(fg_color=colors["bg_card"])
        self.quick_title_label.configure(text_color=colors["accent_yellow"])
        for btn in self.quick_btns:
            btn.configure(fg_color=colors["bg_input"], hover_color=colors["accent_blue"], text_color=colors["text_primary"])

        # 更新自定义时间区域
        self.custom_frame.configure(fg_color=colors["bg_card"])
        self.custom_title_label.configure(text_color=colors["accent_purple"])
        self.hour_label.configure(text_color=colors["text_secondary"])
        self.minute_label.configure(text_color=colors["text_secondary"])
        self.hour_entry.configure(fg_color=colors["bg_input"], text_color=colors["text_primary"])
        self.minute_entry.configure(fg_color=colors["bg_input"], text_color=colors["text_primary"])
        self.set_btn.configure(fg_color=colors["accent_green"])

        # 更新状态区域
        if self.status_frame:
            self.status_frame.configure(fg_color=colors["bg_card"])
            self.status_label.configure(text_color=colors["accent_green"])
            self.cancel_btn.configure(fg_color=colors["accent_red"])

        # 更新关闭按钮
        self.close_btn.configure(fg_color=colors["bg_input"], hover_color=colors["border"], text_color=colors["text_primary"])

    def destroy(self):
        """销毁对话框"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
