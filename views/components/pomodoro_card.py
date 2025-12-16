"""
番茄钟卡片组件
"""

import customtkinter as ctk
from config import get_colors, theme_manager, DEFAULT_FOCUS_TIME


class PomodoroCard(ctk.CTkFrame):
    """番茄钟卡片组件"""

    def __init__(self, parent, subjects, on_start=None, on_reset=None,
                 on_subject_change=None, on_manage_subjects=None, **kwargs):
        """初始化番茄钟卡片

        Args:
            parent: 父容器
            subjects: 科目列表
            on_start: 开始/暂停回调
            on_reset: 重置回调
            on_subject_change: 科目变更回调
            on_manage_subjects: 管理科目回调
        """
        colors = get_colors()
        super().__init__(parent, fg_color=colors["bg_card"], corner_radius=10, **kwargs)

        self._subjects = subjects
        self._on_start = on_start
        self._on_reset = on_reset
        self._on_subject_change = on_subject_change
        self._on_manage_subjects = on_manage_subjects

        self._create_widgets()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        # 标题
        self.pomodoro_title = ctk.CTkLabel(
            self,
            text="🍅 番茄钟",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["accent_red"]
        )
        self.pomodoro_title.pack(anchor="w", padx=15, pady=(10, 5))

        # 科目选择
        self.subject_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.subject_frame.pack(fill="x", padx=15, pady=(0, 5))

        self.subject_label = ctk.CTkLabel(
            self.subject_frame,
            text="科目：",
            font=ctk.CTkFont(size=11),
            text_color=colors["text_secondary"]
        )
        self.subject_label.pack(side="left")

        self.subject_var = ctk.StringVar(value="其他")
        self.subject_menu = ctk.CTkOptionMenu(
            self.subject_frame,
            values=self._subjects,
            variable=self.subject_var,
            width=110,
            height=28,
            font=ctk.CTkFont(size=13),
            fg_color=colors["bg_input"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_purple"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_card"],
            dropdown_hover_color=colors["accent_blue"],
            command=self._on_subject_change
        )
        self.subject_menu.pack(side="left", padx=5)

        # 管理科目按钮
        self.manage_subject_btn = ctk.CTkButton(
            self.subject_frame,
            text="⚙",
            width=25,
            height=25,
            fg_color="transparent",
            hover_color=colors["bg_input"],
            command=self._on_manage_subjects
        )
        self.manage_subject_btn.pack(side="left", padx=2)

        # 计时器显示
        self.timer_label = ctk.CTkLabel(
            self,
            text="25:00",
            font=ctk.CTkFont(size=52, weight="bold"),
            text_color=colors["accent_blue"]
        )
        self.timer_label.pack(pady=10)

        # 状态文字
        self.status_label = ctk.CTkLabel(
            self,
            text="准备开始专注",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["text_secondary"]
        )
        self.status_label.pack(pady=(0, 10))

        # 按钮
        self.pomo_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pomo_btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.start_btn = ctk.CTkButton(
            self.pomo_btn_frame,
            text="▶ 开始",
            width=90,
            height=30,
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"],
            text_color="#ffffff",
            command=self._on_start
        )
        self.start_btn.pack(side="left", expand=True, padx=5)

        self.reset_btn = ctk.CTkButton(
            self.pomo_btn_frame,
            text="↺ 重置",
            width=90,
            height=30,
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=self._on_reset
        )
        self.reset_btn.pack(side="left", expand=True, padx=5)

    def update_timer(self, time_str):
        """更新计时器显示

        Args:
            time_str: 时间字符串 'MM:SS'
        """
        self.timer_label.configure(text=time_str)

    def update_timer_color(self, remaining_seconds, is_focus_time):
        """更新计时器颜色

        Args:
            remaining_seconds: 剩余秒数
            is_focus_time: 是否是专注时间
        """
        colors = get_colors()
        if is_focus_time:
            if remaining_seconds < 60:
                self.timer_label.configure(text_color=colors["accent_red"])
            else:
                self.timer_label.configure(text_color=colors["accent_blue"])

    def update_status(self, status_text, color=None):
        """更新状态文本

        Args:
            status_text: 状态文本
            color: 颜色（可选）
        """
        if color is None:
            color = get_colors()["text_secondary"]
        self.status_label.configure(text=status_text, text_color=color)

    def update_start_button(self, is_running):
        """更新开始按钮文本

        Args:
            is_running: 是否正在运行
        """
        if is_running:
            self.start_btn.configure(text="⏸ 暂停")
        else:
            self.start_btn.configure(text="▶ 开始")

    def update_subjects(self, subjects):
        """更新科目列表

        Args:
            subjects: 新的科目列表
        """
        self._subjects = subjects
        self.subject_menu.configure(values=subjects)

    def get_current_subject(self):
        """获取当前选中的科目

        Returns:
            当前科目名称
        """
        return self.subject_var.get()

    def _on_theme_change(self, theme):
        """主题变化回调"""
        self._apply_theme()

    def _apply_theme(self):
        """应用当前主题颜色"""
        colors = get_colors()

        # 更新自身背景
        self.configure(fg_color=colors["bg_card"])

        # 更新标题
        self.pomodoro_title.configure(text_color=colors["accent_red"])

        # 更新科目选择
        self.subject_label.configure(text_color=colors["text_secondary"])
        self.subject_menu.configure(
            fg_color=colors["bg_input"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_purple"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_card"],
            dropdown_hover_color=colors["accent_blue"]
        )
        self.manage_subject_btn.configure(hover_color=colors["bg_input"])

        # 更新计时器（保持当前颜色逻辑）
        self.timer_label.configure(text_color=colors["accent_blue"])

        # 更新状态
        self.status_label.configure(text_color=colors["text_secondary"])

        # 更新按钮
        self.start_btn.configure(
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"],
            text_color="#ffffff"
        )
        self.reset_btn.configure(
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"]
        )

    def destroy(self):
        """销毁组件时注销回调"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
