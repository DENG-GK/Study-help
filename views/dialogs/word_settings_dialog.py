"""
单词学习设置对话框
"""

import customtkinter as ctk
from config import get_colors, theme_manager
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

        colors = get_colors()
        self.title("学习设置")
        self.geometry("300x350")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=colors["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 310}+{parent.winfo_y() + 150}")

        self._create_widgets()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        self.title_label = ctk.CTkLabel(
            self,
            text="⚙ 学习设置",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["accent_blue"]
        )
        self.title_label.pack(pady=(15, 15))

        settings = WordModel.load_word_settings()

        # 每日新学数量
        self.new_words_label = ctk.CTkLabel(
            self,
            text="每日新学单词数:",
            text_color=colors["text_secondary"]
        )
        self.new_words_label.pack(anchor="w", padx=20)

        self.new_words_entry = ctk.CTkEntry(
            self,
            fg_color=colors["bg_input"],
            text_color=colors["text_primary"]
        )
        self.new_words_entry.insert(0, str(settings.get("daily_new_words", 30)))
        self.new_words_entry.pack(fill="x", padx=20, pady=5)

        # 每日复习数量
        self.review_words_label = ctk.CTkLabel(
            self,
            text="每日复习单词数:",
            text_color=colors["text_secondary"]
        )
        self.review_words_label.pack(anchor="w", padx=20)

        self.review_words_entry = ctk.CTkEntry(
            self,
            fg_color=colors["bg_input"],
            text_color=colors["text_primary"]
        )
        self.review_words_entry.insert(0, str(settings.get("daily_review_words", 50)))
        self.review_words_entry.pack(fill="x", padx=20, pady=5)

        # 显示例句
        self.show_example_var = ctk.BooleanVar(value=settings.get("show_example", True))
        self.show_example_checkbox = ctk.CTkCheckBox(
            self,
            text="显示例句",
            variable=self.show_example_var,
            fg_color=colors["accent_blue"],
            text_color=colors["text_primary"]
        )
        self.show_example_checkbox.pack(anchor="w", padx=20, pady=10)

        # 保存按钮
        self.save_btn = ctk.CTkButton(
            self,
            text="保存设置",
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"],
            text_color="#ffffff",
            command=self._save_settings
        )
        self.save_btn.pack(pady=20)

        # 关闭按钮
        self.close_btn = ctk.CTkButton(
            self,
            text="取消",
            width=100,
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=self.destroy
        )
        self.close_btn.pack(pady=(0, 15))

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

        # 更新标签
        self.new_words_label.configure(text_color=colors["text_secondary"])
        self.review_words_label.configure(text_color=colors["text_secondary"])

        # 更新输入框
        self.new_words_entry.configure(fg_color=colors["bg_input"], text_color=colors["text_primary"])
        self.review_words_entry.configure(fg_color=colors["bg_input"], text_color=colors["text_primary"])

        # 更新复选框
        self.show_example_checkbox.configure(fg_color=colors["accent_blue"], text_color=colors["text_primary"])

        # 更新按钮
        self.save_btn.configure(fg_color=colors["accent_blue"], hover_color=colors["accent_purple"])
        self.close_btn.configure(fg_color=colors["bg_input"], hover_color=colors["border"], text_color=colors["text_primary"])

    def destroy(self):
        """销毁对话框"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
