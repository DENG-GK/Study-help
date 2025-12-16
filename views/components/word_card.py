"""
单词学习卡片组件
"""

import customtkinter as ctk
from config import get_colors, theme_manager
from controllers import WordController
from utils import play_word_sound


class WordCard(ctk.CTkFrame):
    """单词学习卡片组件"""

    def __init__(self, parent, on_wordbook_click=None, on_stats_click=None,
                 on_settings_click=None, **kwargs):
        """初始化单词卡片

        Args:
            parent: 父容器
            on_wordbook_click: 词库管理回调
            on_stats_click: 统计回调
            on_settings_click: 设置回调
        """
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._on_wordbook_click = on_wordbook_click
        self._on_stats_click = on_stats_click
        self._on_settings_click = on_settings_click

        # 创建控制器
        self.controller = WordController(
            on_word_update=self._update_word_display,
            on_progress_update=self._update_progress_display
        )

        self._create_widgets()
        self.controller.load_today_words()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        # ===== 顶部标题和进度 =====
        self.word_header = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.word_header.pack(fill="x", padx=5, pady=5)

        header_top = ctk.CTkFrame(self.word_header, fg_color="transparent")
        header_top.pack(fill="x", padx=15, pady=(10, 5))

        self.word_title_label = ctk.CTkLabel(
            header_top,
            text="📖 英语单词",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["accent_purple"]
        )
        self.word_title_label.pack(side="left")

        # 学习模式切换
        self.mode_frame = ctk.CTkFrame(header_top, fg_color="transparent")
        self.mode_frame.pack(side="right")

        self.card_mode_btn = ctk.CTkButton(
            self.mode_frame, text="卡片", width=45, height=24,
            font=ctk.CTkFont(size=10),
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"],
            text_color="#ffffff",
            command=lambda: self._switch_mode("card")
        )
        self.card_mode_btn.pack(side="left", padx=2)

        self.choice_mode_btn = ctk.CTkButton(
            self.mode_frame, text="选择", width=45, height=24,
            font=ctk.CTkFont(size=10),
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=lambda: self._switch_mode("choice")
        )
        self.choice_mode_btn.pack(side="left", padx=2)

        self.spell_mode_btn = ctk.CTkButton(
            self.mode_frame, text="拼写", width=45, height=24,
            font=ctk.CTkFont(size=10),
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=lambda: self._switch_mode("spell")
        )
        self.spell_mode_btn.pack(side="left", padx=2)

        # 今日进度
        progress_frame = ctk.CTkFrame(self.word_header, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.word_progress_label = ctk.CTkLabel(
            progress_frame,
            text="今日: 新学 0/30  复习 0/50",
            font=ctk.CTkFont(size=11),
            text_color=colors["text_secondary"]
        )
        self.word_progress_label.pack(side="left")

        # ===== 单词卡片区域 =====
        self.word_card_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.word_card_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 单词显示
        self.word_display = ctk.CTkLabel(
            self.word_card_frame,
            text="abandon",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.word_display.pack(pady=(40, 5))

        # 音标和发音按钮
        phonetic_frame = ctk.CTkFrame(self.word_card_frame, fg_color="transparent")
        phonetic_frame.pack(pady=5)

        self.phonetic_label = ctk.CTkLabel(
            phonetic_frame,
            text="/əˈbændən/",
            font=ctk.CTkFont(size=14),
            text_color=colors["text_secondary"]
        )
        self.phonetic_label.pack(side="left", padx=5)

        self.sound_btn = ctk.CTkButton(
            phonetic_frame,
            text="🔊",
            width=30,
            height=25,
            fg_color="transparent",
            hover_color=colors["bg_input"],
            command=self._play_sound
        )
        self.sound_btn.pack(side="left", padx=5)

        # 释义区域
        self.meaning_frame = ctk.CTkFrame(self.word_card_frame, fg_color=colors["bg_input"], corner_radius=10)
        self.meaning_frame.pack(fill="x", padx=20, pady=15)

        self.meaning_label = ctk.CTkLabel(
            self.meaning_frame,
            text="点击卡片显示释义",
            font=ctk.CTkFont(size=14),
            text_color=colors["text_secondary"],
            wraplength=400
        )
        self.meaning_label.pack(pady=15, padx=15)

        # 例句区域
        self.example_frame = ctk.CTkFrame(self.word_card_frame, fg_color="transparent")
        self.example_frame.pack(fill="x", padx=20, pady=5)

        self.example_label = ctk.CTkLabel(
            self.example_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=colors["text_secondary"],
            wraplength=420
        )
        self.example_label.pack(pady=5)

        # 绑定卡片点击事件
        self.word_card_frame.bind('<Button-1>', self._flip_card)
        self.word_display.bind('<Button-1>', self._flip_card)
        self.meaning_frame.bind('<Button-1>', self._flip_card)

        # ===== 操作按钮区域 =====
        self.word_action_frame = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.word_action_frame.pack(fill="x", padx=5, pady=5)

        # 卡片模式按钮
        self.card_buttons_frame = ctk.CTkFrame(self.word_action_frame, fg_color="transparent")
        self.card_buttons_frame.pack(fill="x", padx=15, pady=10)

        self.dont_know_btn = ctk.CTkButton(
            self.card_buttons_frame,
            text="❌ 不认识",
            width=100,
            height=35,
            fg_color=colors["accent_red"],
            hover_color="#da3633",
            command=lambda: self.controller.answer_word("wrong")
        )
        self.dont_know_btn.pack(side="left", expand=True, padx=5)

        self.fuzzy_btn = ctk.CTkButton(
            self.card_buttons_frame,
            text="😐 模糊",
            width=100,
            height=35,
            fg_color=colors["accent_yellow"],
            hover_color="#b08800",
            text_color="#000000",
            command=lambda: self.controller.answer_word("fuzzy")
        )
        self.fuzzy_btn.pack(side="left", expand=True, padx=5)

        self.know_btn = ctk.CTkButton(
            self.card_buttons_frame,
            text="✅ 认识",
            width=100,
            height=35,
            fg_color=colors["accent_green"],
            hover_color="#2ea043",
            command=lambda: self.controller.answer_word("correct")
        )
        self.know_btn.pack(side="left", expand=True, padx=5)

        # 选择题模式按钮（初始隐藏）
        self.choice_buttons_frame = ctk.CTkFrame(self.word_action_frame, fg_color="transparent")

        self.choice_btns = []
        for i in range(4):
            btn = ctk.CTkButton(
                self.choice_buttons_frame,
                text=f"选项 {i+1}",
                width=200,
                height=35,
                fg_color=colors["bg_input"],
                hover_color=colors["accent_blue"],
                anchor="w",
                command=lambda idx=i: self._select_choice(idx)
            )
            btn.pack(fill="x", padx=15, pady=3)
            self.choice_btns.append(btn)

        # 拼写模式输入框（初始隐藏）
        self.spell_frame = ctk.CTkFrame(self.word_action_frame, fg_color="transparent")

        spell_input_frame = ctk.CTkFrame(self.spell_frame, fg_color="transparent")
        spell_input_frame.pack(fill="x", padx=15, pady=5)

        self.spell_entry = ctk.CTkEntry(
            spell_input_frame,
            placeholder_text="输入单词拼写...",
            height=40,
            font=ctk.CTkFont(size=16),
            fg_color=colors["bg_input"],
            border_color=colors["border"]
        )
        self.spell_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.spell_entry.bind('<Return>', self._check_spelling)

        self.spell_submit_btn = ctk.CTkButton(
            spell_input_frame,
            text="确认",
            width=80,
            height=40,
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"],
            command=self._check_spelling
        )
        self.spell_submit_btn.pack(side="right")

        self.spell_result_label = ctk.CTkLabel(
            self.spell_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=colors["text_secondary"]
        )
        self.spell_result_label.pack(pady=5)

        # ===== 底部功能按钮 =====
        self.word_bottom = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.word_bottom.pack(fill="x", padx=5, pady=5)

        bottom_btns = ctk.CTkFrame(self.word_bottom, fg_color="transparent")
        bottom_btns.pack(fill="x", padx=10, pady=8)

        self.star_btn = ctk.CTkButton(
            bottom_btns, text="⭐ 收藏", width=70, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=colors["bg_input"],
            hover_color=colors["accent_yellow"],
            text_color=colors["text_primary"],
            command=self._toggle_star
        )
        self.star_btn.pack(side="left", expand=True, padx=3)

        self.wordbook_btn = ctk.CTkButton(
            bottom_btns, text="📚 词库", width=70, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=self._on_wordbook_click
        )
        self.wordbook_btn.pack(side="left", expand=True, padx=3)

        self.word_stats_btn = ctk.CTkButton(
            bottom_btns, text="📊 统计", width=70, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=self._on_stats_click
        )
        self.word_stats_btn.pack(side="left", expand=True, padx=3)

        self.word_settings_btn = ctk.CTkButton(
            bottom_btns, text="⚙ 设置", width=70, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=self._on_settings_click
        )
        self.word_settings_btn.pack(side="left", expand=True, padx=3)

    def _switch_mode(self, mode):
        """切换学习模式

        Args:
            mode: 学习模式
        """
        colors = get_colors()
        self.controller.switch_mode(mode)

        # 更新按钮样式
        modes = {"card": self.card_mode_btn, "choice": self.choice_mode_btn, "spell": self.spell_mode_btn}
        for m, btn in modes.items():
            if m == mode:
                btn.configure(fg_color=colors["accent_blue"], text_color="#ffffff")
            else:
                btn.configure(fg_color=colors["bg_input"], text_color=colors["text_primary"])

        # 隐藏所有模式的按钮框架
        self.card_buttons_frame.pack_forget()
        self.choice_buttons_frame.pack_forget()
        self.spell_frame.pack_forget()

        # 显示当前模式的按钮框架
        if mode == "card":
            self.card_buttons_frame.pack(fill="x", padx=15, pady=10)
        elif mode == "choice":
            self.choice_buttons_frame.pack(fill="x", padx=15, pady=10)
            self._update_choices()
        elif mode == "spell":
            self.spell_frame.pack(fill="x", padx=15, pady=10)
            self.spell_entry.delete(0, 'end')
            self.spell_result_label.configure(text="")

    def _flip_card(self, event=None):
        """翻转卡片"""
        self.controller.flip_card()

    def _play_sound(self):
        """播放发音"""
        if self.controller.current_word:
            play_word_sound(self.controller.current_word.get("word", ""))

    def _toggle_star(self):
        """收藏/取消收藏"""
        self.controller.toggle_star()

    def _select_choice(self, idx):
        """选择题模式：选择选项

        Args:
            idx: 选项索引
        """
        colors = get_colors()
        is_correct = self.controller.select_choice(idx)

        # 显示正确/错误反馈
        for i in range(4):
            if i == self.controller.correct_choice_idx:
                self.choice_btns[i].configure(fg_color=colors["accent_green"])
            elif i == idx and not is_correct:
                self.choice_btns[i].configure(fg_color=colors["accent_red"])

        # 延迟后显示下一个单词
        self.after(800, self._next_word_after_choice)

    def _next_word_after_choice(self):
        """选择题答完后显示下一个单词"""
        self.controller.next_word()
        self._update_choices()

    def _check_spelling(self, event=None):
        """检查拼写"""
        colors = get_colors()
        user_input = self.spell_entry.get()
        is_correct, correct_word = self.controller.check_spelling(user_input)

        if is_correct:
            self.spell_result_label.configure(
                text="✅ 正确！",
                text_color=colors["accent_green"]
            )
        else:
            self.spell_result_label.configure(
                text=f"❌ 错误！正确答案: {correct_word}",
                text_color=colors["accent_red"]
            )

        # 显示正确单词
        self.word_display.configure(text=correct_word)

        # 延迟后显示下一个单词
        self.after(1200, self._next_word_after_spell)

    def _next_word_after_spell(self):
        """拼写答完后显示下一个单词"""
        self.controller.next_word()
        self.spell_entry.delete(0, 'end')
        self.spell_result_label.configure(text="")

    def _update_word_display(self):
        """更新单词显示"""
        colors = get_colors()
        word = self.controller.current_word
        mode = self.controller.mode

        if not word:
            self.word_display.configure(text="暂无单词")
            self.phonetic_label.configure(text="")
            self.meaning_label.configure(text="请先导入词库或添加单词")
            self.example_label.configure(text="")
            return

        if mode == "card":
            self.word_display.configure(text=word.get("word", ""))
            self.phonetic_label.configure(text=word.get("phonetic", ""))

            if self.controller.card_flipped:
                self.meaning_label.configure(
                    text=word.get("meaning", ""),
                    text_color=colors["text_primary"]
                )
                example = word.get("example", "")
                example_cn = word.get("example_cn", "")
                if example:
                    self.example_label.configure(text=f"例: {example}\n{example_cn}")
                else:
                    self.example_label.configure(text="")
            else:
                self.meaning_label.configure(
                    text="点击卡片显示释义",
                    text_color=colors["text_secondary"]
                )
                self.example_label.configure(text="")

        elif mode == "choice":
            self.word_display.configure(text=word.get("word", ""))
            self.phonetic_label.configure(text=word.get("phonetic", ""))
            self.meaning_label.configure(
                text="请选择正确的释义",
                text_color=colors["text_secondary"]
            )
            self.example_label.configure(text="")

        elif mode == "spell":
            self.word_display.configure(text="???")
            self.phonetic_label.configure(text="")
            self.meaning_label.configure(
                text=word.get("meaning", ""),
                text_color=colors["text_primary"]
            )
            example_cn = word.get("example_cn", "")
            if example_cn:
                self.example_label.configure(text=f"提示: {example_cn}")
            else:
                self.example_label.configure(text="")

        # 更新收藏按钮状态
        if word.get("starred", False):
            self.star_btn.configure(text="⭐ 已收藏", fg_color=colors["accent_yellow"], text_color="#000000")
        else:
            self.star_btn.configure(text="⭐ 收藏", fg_color=colors["bg_input"], text_color=colors["text_primary"])

    def _update_progress_display(self):
        """更新进度显示"""
        self.word_progress_label.configure(text=self.controller.get_progress_text())

    def _update_choices(self):
        """更新选择题选项"""
        colors = get_colors()
        choices = self.controller.generate_choices()
        for i, (idx, meaning, is_correct) in enumerate(choices):
            self.choice_btns[i].configure(
                text=f"{chr(65+i)}. {meaning}",
                fg_color=colors["bg_input"],
                text_color=colors["text_primary"]
            )

    def reload_words(self):
        """重新加载单词"""
        self.controller.load_today_words()

    def _on_theme_change(self, theme):
        """主题变化回调"""
        self._apply_theme()

    def _apply_theme(self):
        """应用当前主题颜色"""
        colors = get_colors()

        # 更新顶部标题区域
        self.word_header.configure(fg_color=colors["bg_card"])
        self.word_title_label.configure(text_color=colors["accent_purple"])
        self.word_progress_label.configure(text_color=colors["text_secondary"])

        # 更新模式切换按钮
        current_mode = self.controller.mode
        modes = {"card": self.card_mode_btn, "choice": self.choice_mode_btn, "spell": self.spell_mode_btn}
        for m, btn in modes.items():
            if m == current_mode:
                btn.configure(fg_color=colors["accent_blue"], hover_color=colors["accent_purple"], text_color="#ffffff")
            else:
                btn.configure(fg_color=colors["bg_input"], hover_color=colors["border"], text_color=colors["text_primary"])

        # 更新单词卡片区域
        self.word_card_frame.configure(fg_color=colors["bg_card"])
        self.word_display.configure(text_color=colors["text_primary"])
        self.phonetic_label.configure(text_color=colors["text_secondary"])
        self.sound_btn.configure(hover_color=colors["bg_input"])
        self.meaning_frame.configure(fg_color=colors["bg_input"])
        self.example_label.configure(text_color=colors["text_secondary"])

        # 更新操作按钮区域
        self.word_action_frame.configure(fg_color=colors["bg_card"])
        self.dont_know_btn.configure(fg_color=colors["accent_red"])
        self.fuzzy_btn.configure(fg_color=colors["accent_yellow"])
        self.know_btn.configure(fg_color=colors["accent_green"])

        # 更新选择题按钮
        for btn in self.choice_btns:
            btn.configure(
                fg_color=colors["bg_input"],
                hover_color=colors["accent_blue"],
                text_color=colors["text_primary"]
            )

        # 更新拼写输入区域
        self.spell_entry.configure(
            fg_color=colors["bg_input"],
            border_color=colors["border"]
        )
        self.spell_submit_btn.configure(
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"]
        )
        self.spell_result_label.configure(text_color=colors["text_secondary"])

        # 更新底部按钮
        self.word_bottom.configure(fg_color=colors["bg_card"])
        self.wordbook_btn.configure(fg_color=colors["bg_input"], hover_color=colors["border"], text_color=colors["text_primary"])
        self.word_stats_btn.configure(fg_color=colors["bg_input"], hover_color=colors["border"], text_color=colors["text_primary"])
        self.word_settings_btn.configure(fg_color=colors["bg_input"], hover_color=colors["border"], text_color=colors["text_primary"])

        # 重新更新单词显示以应用新颜色
        self._update_word_display()

    def destroy(self):
        """销毁组件时注销回调"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
