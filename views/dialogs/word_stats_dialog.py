"""
单词学习统计对话框
"""

import customtkinter as ctk
from config import COLORS
from models import WordModel, BaseModel


class WordStatsDialog(ctk.CTkToplevel):
    """单词学习统计对话框"""

    def __init__(self, parent, **kwargs):
        """初始化单词统计对话框

        Args:
            parent: 父窗口
        """
        super().__init__(parent, **kwargs)

        self.title("📊 单词学习统计")
        self.geometry("350x450")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=COLORS["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 285}+{parent.winfo_y() + 130}")

        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        ctk.CTkLabel(
            self,
            text="📊 单词学习统计",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["accent_blue"]
        ).pack(pady=(15, 10))

        # 加载统计数据
        words_data = WordModel.load_words()
        word_stats = WordModel.load_word_stats()
        today = BaseModel.get_today_str()

        words = words_data.get("words", [])
        total_words = len(words)
        starred_words = sum(1 for w in words if w.get("starred"))
        mastered_words = sum(1 for w in words if w.get("level", 0) >= 4)
        learning_words = sum(1 for w in words if 0 < w.get("level", 0) < 4)
        new_words = sum(1 for w in words if w.get("level", 0) == 0)

        # 今日统计
        today_stats = word_stats.get("records", {}).get(today, {})
        today_reviewed = today_stats.get("reviewed", 0)
        today_correct = today_stats.get("correct", 0)
        today_wrong = today_stats.get("wrong", 0)
        accuracy = (today_correct / today_reviewed * 100) if today_reviewed > 0 else 0

        # 词库概览
        overview_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        overview_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            overview_frame,
            text="📚 词库概览",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["accent_purple"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        stats_grid = ctk.CTkFrame(overview_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=15, pady=(0, 10))

        stats_items = [
            ("总单词", f"{total_words}", COLORS["accent_blue"]),
            ("已掌握", f"{mastered_words}", COLORS["accent_green"]),
            ("学习中", f"{learning_words}", COLORS["accent_yellow"]),
            ("未学习", f"{new_words}", COLORS["text_secondary"]),
        ]

        for i, (label, value, color) in enumerate(stats_items):
            item = ctk.CTkFrame(stats_grid, fg_color=COLORS["bg_input"], corner_radius=8)
            item.pack(side="left", expand=True, fill="x", padx=3)
            ctk.CTkLabel(item, text=value, font=ctk.CTkFont(size=16, weight="bold"),
                        text_color=color).pack(pady=(8, 2))
            ctk.CTkLabel(item, text=label, font=ctk.CTkFont(size=10),
                        text_color=COLORS["text_secondary"]).pack(pady=(0, 8))

        # 今日学习
        today_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        today_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            today_frame,
            text="📅 今日学习",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["accent_green"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        today_info = ctk.CTkFrame(today_frame, fg_color="transparent")
        today_info.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(today_info, text=f"复习单词: {today_reviewed} 个",
                    text_color=COLORS["text_primary"]).pack(anchor="w", pady=2)
        ctk.CTkLabel(today_info, text=f"正确: {today_correct} 个 | 错误: {today_wrong} 个",
                    text_color=COLORS["text_primary"]).pack(anchor="w", pady=2)
        ctk.CTkLabel(today_info, text=f"正确率: {accuracy:.1f}%",
                    text_color=COLORS["accent_green"] if accuracy >= 80 else COLORS["accent_yellow"]).pack(anchor="w", pady=2)

        # 收藏统计
        star_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        star_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            star_frame,
            text=f"⭐ 收藏单词: {starred_words} 个",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["accent_yellow"]
        ).pack(pady=10)

        # 关闭按钮
        ctk.CTkButton(
            self,
            text="关闭",
            width=100,
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=self.destroy
        ).pack(pady=10)
