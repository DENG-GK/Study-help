"""
单词学习设置对话框
"""

import customtkinter as ctk
from config import COLORS
from models import WordModel


class WordSettingsDialog(ctk.CTkToplevel):
    """单词学习设置对话框"""

    def __init__(self, parent, on_save=None, **kwargs):
        """初始化单词设置对话框

        Args:
            parent: 父窗口
            on_save: 保存设置后的回调
        """
        super().__init__(parent, **kwargs)

        self._on_save = on_save

        self.title("学习设置")
        self.geometry("300x350")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=COLORS["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 310}+{parent.winfo_y() + 150}")

        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        ctk.CTkLabel(
            self,
            text="⚙ 学习设置",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["accent_blue"]
        ).pack(pady=(15, 15))

        settings = WordModel.load_word_settings()

        # 每日新学数量
        ctk.CTkLabel(self, text="每日新学单词数:", text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20)
        self.new_words_entry = ctk.CTkEntry(self, fg_color=COLORS["bg_input"])
        self.new_words_entry.insert(0, str(settings.get("daily_new_words", 30)))
        self.new_words_entry.pack(fill="x", padx=20, pady=5)

        # 每日复习数量
        ctk.CTkLabel(self, text="每日复习单词数:", text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20)
        self.review_words_entry = ctk.CTkEntry(self, fg_color=COLORS["bg_input"])
        self.review_words_entry.insert(0, str(settings.get("daily_review_words", 50)))
        self.review_words_entry.pack(fill="x", padx=20, pady=5)

        # 显示例句
        self.show_example_var = ctk.BooleanVar(value=settings.get("show_example", True))
        ctk.CTkCheckBox(
            self, text="显示例句",
            variable=self.show_example_var,
            fg_color=COLORS["accent_blue"]
        ).pack(anchor="w", padx=20, pady=10)

        # 保存按钮
        ctk.CTkButton(
            self, text="保存设置",
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=self._save_settings
        ).pack(pady=20)

    def _save_settings(self):
        """保存设置"""
        try:
            new_settings = {
                "daily_new_words": int(self.new_words_entry.get()),
                "daily_review_words": int(self.review_words_entry.get()),
                "show_example": self.show_example_var.get(),
                "learning_mode": "card",
                "auto_play_sound": False
            }
            WordModel.save_word_settings(new_settings)
            if self._on_save:
                self._on_save()
            self.destroy()
        except ValueError:
            pass
