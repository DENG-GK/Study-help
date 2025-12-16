"""
单词学习统计对话框
"""

import customtkinter as ctk
from config import get_colors, theme_manager
from models import WordModel, BaseModel


class WordStatsDialog(ctk.CTkToplevel):
    """单词学习统计对话框"""

    def __init__(self, parent, **kwargs):
        """初始化单词统计对话框

        Args:
            parent: 父窗口
        """
        super().__init__(parent, **kwargs)

        colors = get_colors()
        self.title("📊 单词学习统计")
        self.geometry("350x450")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=colors["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 285}+{parent.winfo_y() + 130}")

        self._create_widgets()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        self.title_label = ctk.CTkLabel(
            self,
            text="📊 单词学习统计",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["accent_blue"]
        )
        self.title_label.pack(pady=(15, 10))

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
        self.overview_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.overview_frame.pack(fill="x", padx=15, pady=10)

        self.overview_title_label = ctk.CTkLabel(
            self.overview_frame,
            text="📚 词库概览",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["accent_purple"]
        )
        self.overview_title_label.pack(anchor="w", padx=15, pady=(10, 5))

        self.stats_grid = ctk.CTkFrame(self.overview_frame, fg_color="transparent")
        self.stats_grid.pack(fill="x", padx=15, pady=(0, 10))

        stats_items = [
            ("总单词", f"{total_words}", colors["accent_blue"]),
            ("已掌握", f"{mastered_words}", colors["accent_green"]),
            ("学习中", f"{learning_words}", colors["accent_yellow"]),
            ("未学习", f"{new_words}", colors["text_secondary"]),
        ]

        self.stat_frames = []
        self.stat_value_labels = []
        self.stat_name_labels = []
        for i, (label, value, color) in enumerate(stats_items):
            item = ctk.CTkFrame(self.stats_grid, fg_color=colors["bg_input"], corner_radius=8)
            item.pack(side="left", expand=True, fill="x", padx=3)
            self.stat_frames.append(item)

            value_label = ctk.CTkLabel(item, text=value, font=ctk.CTkFont(size=16, weight="bold"),
                        text_color=color)
            value_label.pack(pady=(8, 2))
            self.stat_value_labels.append((value_label, color))

            name_label = ctk.CTkLabel(item, text=label, font=ctk.CTkFont(size=10),
                        text_color=colors["text_secondary"])
            name_label.pack(pady=(0, 8))
            self.stat_name_labels.append(name_label)

        # 今日学习
        self.today_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.today_frame.pack(fill="x", padx=15, pady=10)

        self.today_title_label = ctk.CTkLabel(
            self.today_frame,
            text="📅 今日学习",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["accent_green"]
        )
        self.today_title_label.pack(anchor="w", padx=15, pady=(10, 5))

        today_info = ctk.CTkFrame(self.today_frame, fg_color="transparent")
        today_info.pack(fill="x", padx=15, pady=(0, 10))

        self.reviewed_label = ctk.CTkLabel(today_info, text=f"复习单词: {today_reviewed} 个",
                    text_color=colors["text_primary"])
        self.reviewed_label.pack(anchor="w", pady=2)

        self.correct_wrong_label = ctk.CTkLabel(today_info, text=f"正确: {today_correct} 个 | 错误: {today_wrong} 个",
                    text_color=colors["text_primary"])
        self.correct_wrong_label.pack(anchor="w", pady=2)

        accuracy_color = colors["accent_green"] if accuracy >= 80 else colors["accent_yellow"]
        self.accuracy_label = ctk.CTkLabel(today_info, text=f"正确率: {accuracy:.1f}%",
                    text_color=accuracy_color)
        self.accuracy_label.pack(anchor="w", pady=2)

        # 收藏统计
        self.star_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.star_frame.pack(fill="x", padx=15, pady=10)

        self.star_label = ctk.CTkLabel(
            self.star_frame,
            text=f"⭐ 收藏单词: {starred_words} 个",
            font=ctk.CTkFont(size=13),
            text_color=colors["accent_yellow"]
        )
        self.star_label.pack(pady=10)

        # 关闭按钮
        self.close_btn = ctk.CTkButton(
            self,
            text="关闭",
            width=100,
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

        # 更新标题
        self.title_label.configure(text_color=colors["accent_blue"])

        # 更新词库概览区域
        self.overview_frame.configure(fg_color=colors["bg_card"])
        self.overview_title_label.configure(text_color=colors["accent_purple"])

        for frame in self.stat_frames:
            frame.configure(fg_color=colors["bg_input"])
        for name_label in self.stat_name_labels:
            name_label.configure(text_color=colors["text_secondary"])

        # 更新今日学习区域
        self.today_frame.configure(fg_color=colors["bg_card"])
        self.today_title_label.configure(text_color=colors["accent_green"])
        self.reviewed_label.configure(text_color=colors["text_primary"])
        self.correct_wrong_label.configure(text_color=colors["text_primary"])

        # 更新收藏区域
        self.star_frame.configure(fg_color=colors["bg_card"])
        self.star_label.configure(text_color=colors["accent_yellow"])

        # 更新关闭按钮
        self.close_btn.configure(fg_color=colors["accent_blue"], hover_color=colors["accent_purple"])

    def destroy(self):
        """销毁对话框"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
