"""
词库管理对话框
"""

import customtkinter as ctk
from tkinter import filedialog
from config import COLORS
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

        self.title("词库管理")
        self.geometry("400x500")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=COLORS["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 260}+{parent.winfo_y() + 100}")

        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        ctk.CTkLabel(
            self,
            text="📚 词库管理",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["accent_blue"]
        ).pack(pady=(15, 10))

        # 导入词库
        import_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        import_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            import_frame,
            text="导入词库",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        btn_frame = ctk.CTkFrame(import_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkButton(
            btn_frame, text="导入 TXT", width=100, height=30,
            fg_color=COLORS["accent_blue"],
            command=lambda: self._import_words_file("txt")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="导入 CSV", width=100, height=30,
            fg_color=COLORS["accent_green"],
            command=lambda: self._import_words_file("csv")
        ).pack(side="left", padx=5)

        # 手动添加单词
        add_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        add_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            add_frame,
            text="添加单词",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.word_entry = ctk.CTkEntry(add_frame, placeholder_text="英文单词", fg_color=COLORS["bg_input"])
        self.word_entry.pack(fill="x", padx=15, pady=2)

        self.phonetic_entry = ctk.CTkEntry(add_frame, placeholder_text="音标 (可选)", fg_color=COLORS["bg_input"])
        self.phonetic_entry.pack(fill="x", padx=15, pady=2)

        self.meaning_entry = ctk.CTkEntry(add_frame, placeholder_text="中文释义", fg_color=COLORS["bg_input"])
        self.meaning_entry.pack(fill="x", padx=15, pady=2)

        self.example_entry = ctk.CTkEntry(add_frame, placeholder_text="例句 (可选)", fg_color=COLORS["bg_input"])
        self.example_entry.pack(fill="x", padx=15, pady=2)

        ctk.CTkButton(
            add_frame, text="添加", width=80, height=30,
            fg_color=COLORS["accent_blue"],
            command=self._add_word
        ).pack(pady=10)

        # 词库统计
        stats_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        stats_frame.pack(fill="x", padx=15, pady=10)

        words_data = WordModel.load_words()
        total_words = len(words_data.get("words", []))
        starred_words = sum(1 for w in words_data.get("words", []) if w.get("starred"))

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text=f"词库统计: 共 {total_words} 个单词, 收藏 {starred_words} 个",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.stats_label.pack(pady=10)

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
