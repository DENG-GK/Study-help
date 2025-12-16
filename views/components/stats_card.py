"""
今日统计卡片组件
"""

import customtkinter as ctk
from config import get_colors, theme_manager


class StatsCard(ctk.CTkFrame):
    """今日统计卡片组件"""

    def __init__(self, parent, on_detail_click=None, **kwargs):
        """初始化统计卡片

        Args:
            parent: 父容器
            on_detail_click: 详情按钮点击回调
        """
        colors = get_colors()
        super().__init__(parent, fg_color=colors["bg_card"], corner_radius=10, **kwargs)

        self._on_detail_click = on_detail_click
        self._create_widgets()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        # 标题行容器
        stats_header = ctk.CTkFrame(self, fg_color="transparent")
        stats_header.pack(fill="x", padx=15, pady=(10, 5))

        self.stats_title = ctk.CTkLabel(
            stats_header,
            text="📊 今日成就",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["accent_blue"]
        )
        self.stats_title.pack(side="left")

        # 详情按钮
        self.stats_detail_btn = ctk.CTkButton(
            stats_header,
            text="📈 详情",
            width=60,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=self._on_detail_click
        )
        self.stats_detail_btn.pack(side="right")

        # 统计数据容器
        self.stats_data_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_data_frame.pack(fill="x", padx=15, pady=(0, 10))

        # 专注时长
        self.focus_stat_frame = ctk.CTkFrame(
            self.stats_data_frame,
            fg_color=colors["bg_input"],
            corner_radius=8
        )
        self.focus_stat_frame.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.focus_time_label = ctk.CTkLabel(
            self.focus_stat_frame,
            text="0 分钟",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["accent_green"]
        )
        self.focus_time_label.pack(pady=(8, 2))

        self.focus_desc_label = ctk.CTkLabel(
            self.focus_stat_frame,
            text="专注时长",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=colors["text_secondary"]
        )
        self.focus_desc_label.pack(pady=(0, 8))

        # 完成任务
        self.task_stat_frame = ctk.CTkFrame(
            self.stats_data_frame,
            fg_color=colors["bg_input"],
            corner_radius=8
        )
        self.task_stat_frame.pack(side="left", expand=True, fill="x", padx=(5, 5))

        self.completed_label = ctk.CTkLabel(
            self.task_stat_frame,
            text="0 个",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["accent_red"]
        )
        self.completed_label.pack(pady=(8, 2))

        self.task_desc_label = ctk.CTkLabel(
            self.task_stat_frame,
            text="完成任务",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=colors["text_secondary"]
        )
        self.task_desc_label.pack(pady=(0, 8))

        # 番茄数
        self.pomo_stat_frame = ctk.CTkFrame(
            self.stats_data_frame,
            fg_color=colors["bg_input"],
            corner_radius=8
        )
        self.pomo_stat_frame.pack(side="left", expand=True, fill="x", padx=(5, 0))

        self.pomodoro_count_label = ctk.CTkLabel(
            self.pomo_stat_frame,
            text="0 个",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["accent_yellow"]
        )
        self.pomodoro_count_label.pack(pady=(8, 2))

        self.pomo_desc_label = ctk.CTkLabel(
            self.pomo_stat_frame,
            text="番茄数",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=colors["text_secondary"]
        )
        self.pomo_desc_label.pack(pady=(0, 8))

    def update_stats(self, focus_time, completed_tasks, pomodoros):
        """更新统计显示

        Args:
            focus_time: 专注时长（分钟）
            completed_tasks: 完成任务数
            pomodoros: 番茄数
        """
        self.focus_time_label.configure(text=f"{focus_time} 分钟")
        self.completed_label.configure(text=f"{completed_tasks} 个")
        self.pomodoro_count_label.configure(text=f"{pomodoros} 个")

    def _on_theme_change(self, theme):
        """主题变化回调"""
        self._apply_theme()

    def _apply_theme(self):
        """应用当前主题颜色"""
        colors = get_colors()

        # 更新自身背景
        self.configure(fg_color=colors["bg_card"])

        # 更新标题
        self.stats_title.configure(text_color=colors["accent_blue"])

        # 更新详情按钮
        self.stats_detail_btn.configure(
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"]
        )

        # 更新专注时长卡片
        self.focus_stat_frame.configure(fg_color=colors["bg_input"])
        self.focus_time_label.configure(text_color=colors["accent_green"])
        self.focus_desc_label.configure(text_color=colors["text_secondary"])

        # 更新完成任务卡片
        self.task_stat_frame.configure(fg_color=colors["bg_input"])
        self.completed_label.configure(text_color=colors["accent_red"])
        self.task_desc_label.configure(text_color=colors["text_secondary"])

        # 更新番茄数卡片
        self.pomo_stat_frame.configure(fg_color=colors["bg_input"])
        self.pomodoro_count_label.configure(text_color=colors["accent_yellow"])
        self.pomo_desc_label.configure(text_color=colors["text_secondary"])

    def destroy(self):
        """销毁组件时注销回调"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
