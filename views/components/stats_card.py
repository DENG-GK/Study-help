"""
今日统计卡片组件
"""

import customtkinter as ctk
from config import COLORS


class StatsCard(ctk.CTkFrame):
    """今日统计卡片组件"""

    def __init__(self, parent, on_detail_click=None, **kwargs):
        """初始化统计卡片

        Args:
            parent: 父容器
            on_detail_click: 详情按钮点击回调
        """
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=10, **kwargs)

        self._on_detail_click = on_detail_click
        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        # 标题行容器
        stats_header = ctk.CTkFrame(self, fg_color="transparent")
        stats_header.pack(fill="x", padx=15, pady=(10, 5))

        self.stats_title = ctk.CTkLabel(
            stats_header,
            text="📊 今日成就",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_blue"]
        )
        self.stats_title.pack(side="left")

        # 详情按钮
        self.stats_detail_btn = ctk.CTkButton(
            stats_header,
            text="📈 详情",
            width=60,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            command=self._on_detail_click
        )
        self.stats_detail_btn.pack(side="right")

        # 统计数据容器
        self.stats_data_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_data_frame.pack(fill="x", padx=15, pady=(0, 10))

        # 专注时长
        self.focus_stat_frame = ctk.CTkFrame(
            self.stats_data_frame,
            fg_color=COLORS["bg_input"],
            corner_radius=8
        )
        self.focus_stat_frame.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.focus_time_label = ctk.CTkLabel(
            self.focus_stat_frame,
            text="0 分钟",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_green"]
        )
        self.focus_time_label.pack(pady=(6, 1))

        ctk.CTkLabel(
            self.focus_stat_frame,
            text="专注时长",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(0, 6))

        # 完成任务
        self.task_stat_frame = ctk.CTkFrame(
            self.stats_data_frame,
            fg_color=COLORS["bg_input"],
            corner_radius=8
        )
        self.task_stat_frame.pack(side="left", expand=True, fill="x", padx=(5, 5))

        self.completed_label = ctk.CTkLabel(
            self.task_stat_frame,
            text="0 个",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_red"]
        )
        self.completed_label.pack(pady=(6, 1))

        ctk.CTkLabel(
            self.task_stat_frame,
            text="完成任务",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(0, 6))

        # 番茄数
        self.pomo_stat_frame = ctk.CTkFrame(
            self.stats_data_frame,
            fg_color=COLORS["bg_input"],
            corner_radius=8
        )
        self.pomo_stat_frame.pack(side="left", expand=True, fill="x", padx=(5, 0))

        self.pomodoro_count_label = ctk.CTkLabel(
            self.pomo_stat_frame,
            text="0 个",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_yellow"]
        )
        self.pomodoro_count_label.pack(pady=(6, 1))

        ctk.CTkLabel(
            self.pomo_stat_frame,
            text="番茄数",
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(0, 6))

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
