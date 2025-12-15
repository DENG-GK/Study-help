"""
统计详情对话框
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
matplotlib.rcParams['axes.unicode_minus'] = False

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
        self.geometry("500x600")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=COLORS["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 210}+{parent.winfo_y() + 60}")

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

        # 今日科目分布饼图
        pie_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        pie_frame.pack(fill="x", padx=10, pady=10)

        pie_title = ctk.CTkLabel(
            pie_frame,
            text="🥧 今日学习分布",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_purple"]
        )
        pie_title.pack(anchor="w", padx=15, pady=(10, 5))

        self._create_pie_chart(pie_frame)

        # 历史趋势折线图
        line_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        line_frame.pack(fill="both", expand=True, padx=10, pady=10)

        line_title = ctk.CTkLabel(
            line_frame,
            text="📈 近7天学习趋势",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_green"]
        )
        line_title.pack(anchor="w", padx=15, pady=(10, 5))

        self._create_line_chart(line_frame)

        # 关闭按钮
        ctk.CTkButton(
            self,
            text="关闭",
            width=100,
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=self.destroy
        ).pack(pady=10)

    def _create_pie_chart(self, parent):
        """创建今日科目分布饼图

        Args:
            parent: 父容器
        """
        stats = RecordModel.get_today_stats()
        subjects_data = stats.get("subjects", {})

        fig, ax = plt.subplots(figsize=(4, 2.5), facecolor=COLORS["bg_card"])
        ax.set_facecolor(COLORS["bg_card"])

        if subjects_data and sum(subjects_data.values()) > 0:
            labels = list(subjects_data.keys())
            sizes = list(subjects_data.values())
            colors = CHART_COLORS[:len(labels)]

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct='%1.0f%%',
                colors=colors,
                textprops={'color': COLORS["text_primary"], 'fontsize': 9},
                pctdistance=0.75
            )

            for autotext in autotexts:
                autotext.set_color(COLORS["text_primary"])
                autotext.set_fontsize(8)
        else:
            ax.text(0.5, 0.5, "暂无数据", ha='center', va='center',
                   fontsize=14, color=COLORS["text_secondary"], transform=ax.transAxes)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)

    def _create_line_chart(self, parent):
        """创建历史趋势折线图

        Args:
            parent: 父容器
        """
        history = RecordModel.get_history_stats(7)

        fig, ax = plt.subplots(figsize=(4, 3), facecolor=COLORS["bg_card"])
        ax.set_facecolor(COLORS["bg_card"])

        dates = [h["date"][-5:] for h in history]  # 只显示月-日
        totals = [h["total_time"] for h in history]

        ax.plot(dates, totals, marker='o', color=COLORS["accent_blue"],
                linewidth=2, markersize=6)
        ax.fill_between(dates, totals, alpha=0.3, color=COLORS["accent_blue"])

        ax.set_xlabel("日期", color=COLORS["text_secondary"], fontsize=10)
        ax.set_ylabel("学习时长(分钟)", color=COLORS["text_secondary"], fontsize=10)

        ax.tick_params(colors=COLORS["text_secondary"], labelsize=8)
        ax.spines['bottom'].set_color(COLORS["border"])
        ax.spines['left'].set_color(COLORS["border"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.grid(True, linestyle='--', alpha=0.3, color=COLORS["border"])

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
