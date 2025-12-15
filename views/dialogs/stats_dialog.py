"""
统计详情对话框
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
matplotlib.rcParams["axes.unicode_minus"] = False

from config import COLORS, CHART_COLORS
from models import RecordModel


class StatsDialog(ctk.CTkToplevel):
    """统计详情对话框"""

    def __init__(self, parent, **kwargs):
        """初始化统计对话框

        Args:
            parent: 父窗口
        """
        super().__init__(parent, **kwargs)

        self.title("📊 学习统计")
        self.geometry("550x700")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=COLORS["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 180}+{parent.winfo_y() + 10}")

        self.current_view = "week"  # week, month
        self.canvas_widgets = []

        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        # 顶部标题栏
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)

        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 学习统计",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["accent_blue"]
        )
        title_label.pack(side="left", padx=15, pady=10)

        # 切换按钮
        switch_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        switch_frame.pack(side="right", padx=15, pady=10)

        self.week_btn = ctk.CTkButton(
            switch_frame,
            text="本周",
            width=60,
            height=28,
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=lambda: self._switch_view("week")
        )
        self.week_btn.pack(side="left", padx=2)

        self.month_btn = ctk.CTkButton(
            switch_frame,
            text="本月",
            width=60,
            height=28,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["accent_purple"],
            command=lambda: self._switch_view("month")
        )
        self.month_btn.pack(side="left", padx=2)

        # 内容区域
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._update_content()

        # 关闭按钮
        ctk.CTkButton(
            self,
            text="关闭",
            width=100,
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=self.destroy
        ).pack(pady=10)

    def _switch_view(self, view):
        """切换视图

        Args:
            view: 视图类型 (week/month)
        """
        self.current_view = view

        if view == "week":
            self.week_btn.configure(fg_color=COLORS["accent_blue"])
            self.month_btn.configure(fg_color=COLORS["bg_input"])
        else:
            self.week_btn.configure(fg_color=COLORS["bg_input"])
            self.month_btn.configure(fg_color=COLORS["accent_blue"])

        self._update_content()

    def _update_content(self):
        """更新内容"""
        # 清空现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 关闭旧的图表
        for canvas in self.canvas_widgets:
            try:
                plt.close(canvas.figure)
            except:
                pass
        self.canvas_widgets.clear()

        if self.current_view == "week":
            stats = RecordModel.get_week_stats()
            title_prefix = "本周"
        else:
            stats = RecordModel.get_month_stats()
            title_prefix = "本月"

        # 总览卡片
        self._create_summary_card(stats, title_prefix)

        # 科目分布饼图
        self._create_pie_chart(stats, title_prefix)

        # 每日趋势折线图
        self._create_line_chart(stats, title_prefix)

    def _create_summary_card(self, stats, title_prefix):
        """创建总览卡片"""
        summary_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        summary_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            summary_frame,
            text=f"📋 {title_prefix}总览",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_yellow"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # 统计数据
        data_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
        data_frame.pack(fill="x", padx=15, pady=(0, 10))

        total_hours = stats["total_time"] / 60
        avg_hours = stats["avg_time"] / 60

        items = [
            ("⏱ 总时长", f"{total_hours:.1f}小时"),
            ("📊 日均", f"{avg_hours:.1f}小时"),
            ("✅ 任务", f"{stats['total_tasks']}个"),
            ("🍅 番茄", f"{stats['total_pomodoros']}个"),
        ]

        for i, (label, value) in enumerate(items):
            item_frame = ctk.CTkFrame(data_frame, fg_color=COLORS["bg_input"], corner_radius=8)
            item_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            data_frame.grid_columnconfigure(i, weight=1)

            ctk.CTkLabel(
                item_frame,
                text=label,
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"]
            ).pack(pady=(8, 2))

            ctk.CTkLabel(
                item_frame,
                text=value,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["accent_blue"]
            ).pack(pady=(0, 8))

    def _create_pie_chart(self, stats, title_prefix):
        """创建科目分布饼图"""
        pie_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        pie_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            pie_frame,
            text=f"🥧 {title_prefix}学习分布",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_purple"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        fig, ax = plt.subplots(figsize=(4.5, 2.5), facecolor=COLORS["bg_card"])
        ax.set_facecolor(COLORS["bg_card"])

        subjects_data = stats.get("subjects", {})

        if subjects_data and sum(subjects_data.values()) > 0:
            labels = list(subjects_data.keys())
            sizes = list(subjects_data.values())
            colors = CHART_COLORS[:len(labels)]

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct="%1.0f%%",
                colors=colors,
                textprops={"color": COLORS["text_primary"], "fontsize": 9},
                pctdistance=0.75
            )

            for autotext in autotexts:
                autotext.set_color(COLORS["text_primary"])
                autotext.set_fontsize(8)
        else:
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center",
                   fontsize=14, color=COLORS["text_secondary"], transform=ax.transAxes)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)
        self.canvas_widgets.append(canvas)

    def _create_line_chart(self, stats, title_prefix):
        """创建每日趋势折线图"""
        line_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        line_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            line_frame,
            text=f"📈 {title_prefix}学习趋势",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_green"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        fig, ax = plt.subplots(figsize=(4.5, 3), facecolor=COLORS["bg_card"])
        ax.set_facecolor(COLORS["bg_card"])

        daily_data = stats.get("daily_data", [])

        if daily_data:
            dates = [d["date"][-5:] for d in daily_data]  # MM-DD
            totals = [d["total_time"] for d in daily_data]

            # 如果数据点太多，只显示部分标签
            if len(dates) > 10:
                step = len(dates) // 7
                x_ticks = range(0, len(dates), step)
                x_labels = [dates[i] for i in x_ticks]
            else:
                x_ticks = range(len(dates))
                x_labels = dates

            ax.plot(range(len(totals)), totals, marker="o", color=COLORS["accent_blue"],
                    linewidth=2, markersize=4)
            ax.fill_between(range(len(totals)), totals, alpha=0.3, color=COLORS["accent_blue"])

            ax.set_xticks(list(x_ticks))
            ax.set_xticklabels(x_labels, rotation=45, ha="right")

        ax.set_xlabel("日期", color=COLORS["text_secondary"], fontsize=10)
        ax.set_ylabel("学习时长(分钟)", color=COLORS["text_secondary"], fontsize=10)

        ax.tick_params(colors=COLORS["text_secondary"], labelsize=8)
        ax.spines["bottom"].set_color(COLORS["border"])
        ax.spines["left"].set_color(COLORS["border"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.grid(True, linestyle="--", alpha=0.3, color=COLORS["border"])

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=line_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)
        self.canvas_widgets.append(canvas)
