"""
词库管理对话框
"""

import customtkinter as ctk
from tkinter import filedialog
from config import get_colors, theme_manager
from models import WordModel


class WordbookDialog(ctk.CTkToplevel):
    """词库管理对话框"""

    def __init__(self, parent, on_words_imported=None, **kwargs):
        """初始化词库管理对话框

        Args:
            parent: 父窗口
            on_words_imported: 导入单词后的回调
        """
        super().__init__(parent, **kwargs)

        self._on_words_imported = on_words_imported

        colors = get_colors()
        self.title("词库管理")
        self.geometry("400x500")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=colors["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 260}+{parent.winfo_y() + 100}")

        self._create_widgets()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        self.title_label = ctk.CTkLabel(
            self,
            text="📚 词库管理",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["accent_blue"]
        )
        self.title_label.pack(pady=(15, 10))

        # 导入词库
        self.import_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.import_frame.pack(fill="x", padx=15, pady=10)

        self.import_title_label = ctk.CTkLabel(
            self.import_frame,
            text="导入词库",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.import_title_label.pack(anchor="w", padx=15, pady=(10, 5))

        btn_frame = ctk.CTkFrame(self.import_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.import_txt_btn = ctk.CTkButton(
            btn_frame, text="导入 TXT", width=100, height=30,
            fg_color=colors["accent_blue"],
            text_color="#ffffff",
            command=lambda: self._import_words_file("txt")
        )
        self.import_txt_btn.pack(side="left", padx=5)

        self.import_csv_btn = ctk.CTkButton(
            btn_frame, text="导入 CSV", width=100, height=30,
            fg_color=colors["accent_green"],
            text_color="#ffffff",
            command=lambda: self._import_words_file("csv")
        )
        self.import_csv_btn.pack(side="left", padx=5)

        # 手动添加单词
        self.add_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.add_frame.pack(fill="x", padx=15, pady=10)

        self.add_title_label = ctk.CTkLabel(
            self.add_frame,
            text="添加单词",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.add_title_label.pack(anchor="w", padx=15, pady=(10, 5))

        self.word_entry = ctk.CTkEntry(
            self.add_frame,
            placeholder_text="英文单词",
            fg_color=colors["bg_input"],
            text_color=colors["text_primary"]
        )
        self.word_entry.pack(fill="x", padx=15, pady=2)

        self.phonetic_entry = ctk.CTkEntry(
            self.add_frame,
            placeholder_text="音标 (可选)",
            fg_color=colors["bg_input"],
            text_color=colors["text_primary"]
        )
        self.phonetic_entry.pack(fill="x", padx=15, pady=2)

        self.meaning_entry = ctk.CTkEntry(
            self.add_frame,
            placeholder_text="中文释义",
            fg_color=colors["bg_input"],
            text_color=colors["text_primary"]
        )
        self.meaning_entry.pack(fill="x", padx=15, pady=2)

        self.example_entry = ctk.CTkEntry(
            self.add_frame,
            placeholder_text="例句 (可选)",
            fg_color=colors["bg_input"],
            text_color=colors["text_primary"]
        )
        self.example_entry.pack(fill="x", padx=15, pady=2)

        self.add_btn = ctk.CTkButton(
            self.add_frame, text="添加", width=80, height=30,
            fg_color=colors["accent_blue"],
            text_color="#ffffff",
            command=self._add_word
        )
        self.add_btn.pack(pady=10)

        # 词库统计
        self.stats_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.stats_frame.pack(fill="x", padx=15, pady=10)

        words_data = WordModel.load_words()
        total_words = len(words_data.get("words", []))
        starred_words = sum(1 for w in words_data.get("words", []) if w.get("starred"))

        self.stats_label = ctk.CTkLabel(
            self.stats_frame,
            text=f"词库统计: 共 {total_words} 个单词, 收藏 {starred_words} 个",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.stats_label.pack(pady=10)

        # 关闭按钮
        self.close_btn = ctk.CTkButton(
            self,
            text="关闭",
            width=100,
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=self.destroy
        )
        self.close_btn.pack(pady=10)

    def _import_words_file(self, file_type):
        """导入词库文件

        Args:
            file_type: 文件类型
        """
        if file_type == "txt":
            filetypes = [("Text files", "*.txt")]
        else:
            filetypes = [("CSV files", "*.csv")]

        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            count = WordModel.import_words_from_file(filepath, file_type)
            self._update_stats()
            if self._on_words_imported:
                self._on_words_imported()
            print(f"成功导入 {count} 个单词")

    def _add_word(self):
        """添加单词"""
        word = self.word_entry.get().strip()
        meaning = self.meaning_entry.get().strip()
        if word and meaning:
            WordModel.add_word_manually(
                word=word,
                phonetic=self.phonetic_entry.get().strip(),
                meaning=meaning,
                example=self.example_entry.get().strip()
            )
            self.word_entry.delete(0, 'end')
            self.phonetic_entry.delete(0, 'end')
            self.meaning_entry.delete(0, 'end')
            self.example_entry.delete(0, 'end')
            self._update_stats()
            if self._on_words_imported:
                self._on_words_imported()

    def _update_stats(self):
        """更新统计显示"""
        words_data = WordModel.load_words()
        total_words = len(words_data.get("words", []))
        starred_words = sum(1 for w in words_data.get("words", []) if w.get("starred"))
        self.stats_label.configure(text=f"词库统计: 共 {total_words} 个单词, 收藏 {starred_words} 个")

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

        # 更新导入区域
        self.import_frame.configure(fg_color=colors["bg_card"])
        self.import_title_label.configure(text_color=colors["text_primary"])
        self.import_txt_btn.configure(fg_color=colors["accent_blue"])
        self.import_csv_btn.configure(fg_color=colors["accent_green"])

        # 更新添加单词区域
        self.add_frame.configure(fg_color=colors["bg_card"])
        self.add_title_label.configure(text_color=colors["text_primary"])
        self.word_entry.configure(fg_color=colors["bg_input"], text_color=colors["text_primary"])
        self.phonetic_entry.configure(fg_color=colors["bg_input"], text_color=colors["text_primary"])
        self.meaning_entry.configure(fg_color=colors["bg_input"], text_color=colors["text_primary"])
        self.example_entry.configure(fg_color=colors["bg_input"], text_color=colors["text_primary"])
        self.add_btn.configure(fg_color=colors["accent_blue"])

        # 更新统计区域
        self.stats_frame.configure(fg_color=colors["bg_card"])
        self.stats_label.configure(text_color=colors["text_secondary"])

        # 更新关闭按钮
        self.close_btn.configure(fg_color=colors["bg_input"], hover_color=colors["border"], text_color=colors["text_primary"])

    def destroy(self):
        """销毁对话框"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
