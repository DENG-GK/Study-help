"""
数学学习卡片组件
"""

import customtkinter as ctk
from config import get_colors, theme_manager, MATH_CHAPTERS
from controllers import MathController
from PIL import Image, ImageTk
from utils.latex_renderer import LaTeXRenderer
import re
import os


# LaTeX 到 Unicode 的简单转换表（用于快速显示）
LATEX_UNICODE_MAP = {
    r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
    r'\epsilon': 'ε', r'\zeta': 'ζ', r'\eta': 'η', r'\theta': 'θ',
    r'\lambda': 'λ', r'\mu': 'μ', r'\pi': 'π', r'\sigma': 'σ',
    r'\phi': 'φ', r'\omega': 'ω', r'\Omega': 'Ω', r'\Delta': 'Δ',
    r'\infty': '∞', r'\partial': '∂', r'\nabla': '∇',
    r'\int': '∫', r'\sum': 'Σ', r'\prod': '∏',
    r'\pm': '±', r'\mp': '∓', r'\times': '×', r'\div': '÷',
    r'\cdot': '·', r'\neq': '≠', r'\leq': '≤', r'\geq': '≥',
    r'\approx': '≈', r'\equiv': '≡', r'\subset': '⊂', r'\supset': '⊃',
    r'\in': '∈', r'\notin': '∉', r'\cup': '∪', r'\cap': '∩',
    r'\emptyset': '∅', r'\forall': '∀', r'\exists': '∃',
    r'\rightarrow': '→', r'\leftarrow': '←', r'\Rightarrow': '⇒',
    r'\leftrightarrow': '↔', r'\to': '→',
    r'\sqrt': '√', r'\sin': 'sin', r'\cos': 'cos', r'\tan': 'tan',
    r'\ln': 'ln', r'\log': 'log', r'\lim': 'lim', r'\exp': 'exp',
    r'\frac': '/', r'\text': '',
}


def latex_to_readable(text):
    """将 LaTeX 公式转换为可读文本

    Args:
        text: 包含 LaTeX 的文本

    Returns:
        转换后的可读文本
    """
    if not text:
        return text

    result = text

    # 处理 \frac{a}{b} -> a/b
    result = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1)/(\2)', result)

    # 处理 \sqrt{x} -> √(x)
    result = re.sub(r'\\sqrt\{([^}]*)\}', r'√(\1)', result)

    # 处理 x^{n} -> x^n
    result = re.sub(r'\^\\{([^}]*)\\}', r'^(\1)', result)
    result = re.sub(r'\^\{([^}]*)\}', r'^(\1)', result)

    # 处理 x_{n} -> x_n
    result = re.sub(r'_\{([^}]*)\}', r'_(\1)', result)

    # 处理 \lim_{x \to 0} -> lim(x→0)
    result = re.sub(r'\\lim_\{([^}]*)\}', r'lim(\1)', result)

    # 替换希腊字母和数学符号
    for latex, unicode_char in LATEX_UNICODE_MAP.items():
        result = result.replace(latex, unicode_char)

    # 移除剩余的反斜杠命令
    result = re.sub(r'\\[a-zA-Z]+', '', result)

    # 清理多余的大括号
    result = result.replace('{', '').replace('}', '')

    # 移除 $ 符号
    result = result.replace('$', '')

    # 清理多余空格
    result = re.sub(r'\s+', ' ', result).strip()

    return result


class MathCard(ctk.CTkFrame):
    """数学学习卡片组件"""

    def __init__(self, parent, on_settings_click=None, **kwargs):
        """初始化数学卡片

        Args:
            parent: 父容器
            on_settings_click: 设置回调
        """
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._on_settings_click = on_settings_click
        self.current_tab = "practice"

        # 创建控制器
        self.controller = MathController(
            on_question_update=self._update_question_display,
            on_progress_update=self._update_progress_display,
            on_answer_result=self._on_answer_result
        )

        self._create_widgets()
        self.controller.load_daily_questions()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        # ===== 顶部标题和Tab切换 =====
        self.header = ctk.CTkFrame(self, fg_color=colors["bg_card"], corner_radius=10)
        self.header.pack(fill="x", padx=5, pady=5)

        header_top = ctk.CTkFrame(self.header, fg_color="transparent")
        header_top.pack(fill="x", padx=15, pady=(10, 5))

        self.title_label = ctk.CTkLabel(
            header_top,
            text="📐 考研数学",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["accent_blue"]
        )
        self.title_label.pack(side="left")

        # Tab切换按钮
        self.tab_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.tab_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.tab_btns = {}
        tabs = [
            ("practice", "📝 刷题"),
            ("mistakes", "❌ 错题"),
            ("formulas", "📖 公式"),
            ("progress", "📊 进度")
        ]

        for tab_id, tab_text in tabs:
            btn = ctk.CTkButton(
                self.tab_frame,
                text=tab_text,
                width=72,
                height=28,
                font=ctk.CTkFont(size=12),
                fg_color=colors["accent_blue"] if tab_id == "practice" else colors["bg_input"],
                hover_color=colors["accent_purple"],
                text_color="#ffffff" if tab_id == "practice" else colors["text_primary"],
                command=lambda t=tab_id: self._switch_tab(t)
            )
            btn.pack(side="left", padx=2)
            self.tab_btns[tab_id] = btn

        # ===== 内容区域容器 =====
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 创建各个Tab的内容
        self._create_practice_tab()
        self._create_mistakes_tab()
        self._create_formulas_tab()
        self._create_progress_tab()

        # 默认显示刷题Tab
        self._show_tab("practice")

    def _create_practice_tab(self):
        """创建刷题Tab"""
        colors = get_colors()

        self.practice_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # 题目卡片
        self.question_card = ctk.CTkFrame(self.practice_frame, fg_color=colors["bg_card"], corner_radius=10)
        self.question_card.pack(fill="both", expand=True, pady=(0, 5))

        # 题目信息
        self.question_info = ctk.CTkFrame(self.question_card, fg_color="transparent")
        self.question_info.pack(fill="x", padx=15, pady=(10, 5))

        self.chapter_label = ctk.CTkLabel(
            self.question_info,
            text="高等数学 - 极限",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.chapter_label.pack(side="left")

        self.difficulty_label = ctk.CTkLabel(
            self.question_info,
            text="难度: ⭐",
            font=ctk.CTkFont(size=12),
            text_color=colors["accent_yellow"]
        )
        self.difficulty_label.pack(side="right")

        # 题目文本（支持LaTeX渲染）
        self.question_text_frame = ctk.CTkFrame(self.question_card, fg_color=colors["bg_input"], corner_radius=8)
        self.question_text_frame.pack(fill="x", padx=15, pady=10)

        self.question_label = ctk.CTkLabel(
            self.question_text_frame,
            text="加载题目中...",
            font=ctk.CTkFont(size=15),
            text_color=colors["text_primary"],
            wraplength=380,
            justify="left"
        )
        self.question_label.pack(pady=15, padx=15, anchor="w")

        # 选项区域
        self.options_frame = ctk.CTkFrame(self.question_card, fg_color="transparent")
        self.options_frame.pack(fill="x", padx=15, pady=5)

        self.option_btns = []
        for i in range(4):
            btn = ctk.CTkButton(
                self.options_frame,
                text=f"{chr(65+i)}. 选项",
                height=38,
                font=ctk.CTkFont(size=13),
                fg_color=colors["bg_input"],
                hover_color=colors["accent_blue"],
                text_color=colors["text_primary"],
                anchor="w",
                command=lambda idx=i: self._select_option(idx)
            )
            btn.pack(fill="x", pady=2)
            self.option_btns.append(btn)

        # 解析区域（初始隐藏）
        self.solution_frame = ctk.CTkFrame(self.question_card, fg_color=colors["bg_input"], corner_radius=8)

        self.solution_title = ctk.CTkLabel(
            self.solution_frame,
            text="💡 解析",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["accent_green"]
        )
        self.solution_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.solution_label = ctk.CTkLabel(
            self.solution_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=colors["text_primary"],
            wraplength=380,
            justify="left"
        )
        self.solution_label.pack(anchor="w", padx=15, pady=(0, 10))

        # 操作按钮
        self.action_frame = ctk.CTkFrame(self.practice_frame, fg_color=colors["bg_card"], corner_radius=10)
        self.action_frame.pack(fill="x", pady=5)

        action_btns = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        action_btns.pack(fill="x", padx=10, pady=8)

        self.prev_btn = ctk.CTkButton(
            action_btns,
            text="◀ 上一题",
            width=85,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=self.controller.prev_question
        )
        self.prev_btn.pack(side="left", padx=3)

        self.solution_btn = ctk.CTkButton(
            action_btns,
            text="📖 解析",
            width=75,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_input"],
            hover_color=colors["accent_purple"],
            text_color=colors["text_primary"],
            command=self._toggle_solution
        )
        self.solution_btn.pack(side="left", padx=3)

        self.mistake_btn = ctk.CTkButton(
            action_btns,
            text="➕ 错题",
            width=75,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_input"],
            hover_color=colors["accent_red"],
            text_color=colors["text_primary"],
            command=self._add_to_mistakes
        )
        self.mistake_btn.pack(side="left", padx=3)

        self.next_btn = ctk.CTkButton(
            action_btns,
            text="下一题 ▶",
            width=85,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"],
            text_color="#ffffff",
            command=self.controller.next_question
        )
        self.next_btn.pack(side="right", padx=3)

        # 进度显示
        self.progress_label = ctk.CTkLabel(
            self.action_frame,
            text="进度: 0/0  今日: 0/3  正确率: 0%",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.progress_label.pack(pady=(0, 8))

    def _create_mistakes_tab(self):
        """创建错题本Tab"""
        colors = get_colors()

        self.mistakes_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # 错题本标题
        mistakes_header = ctk.CTkFrame(self.mistakes_frame, fg_color=colors["bg_card"], corner_radius=10)
        mistakes_header.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            mistakes_header,
            text="📕 我的错题本",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["accent_red"]
        ).pack(side="left", padx=15, pady=10)

        # 按钮区域
        btn_row = ctk.CTkFrame(mistakes_header, fg_color="transparent")
        btn_row.pack(side="right", padx=10, pady=10)

        self.import_mistake_btn = ctk.CTkButton(
            btn_row,
            text="📷 导入图片",
            width=90,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"],
            text_color="#ffffff",
            command=self._show_import_dialog
        )
        self.import_mistake_btn.pack(side="left", padx=3)

        self.review_btn = ctk.CTkButton(
            btn_row,
            text="📝 开始复习",
            width=90,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=colors["accent_green"],
            hover_color="#2ea043",
            text_color="#ffffff",
            command=self._start_mistake_review
        )
        self.review_btn.pack(side="left", padx=3)

        # 错题列表
        self.mistakes_list = ctk.CTkScrollableFrame(
            self.mistakes_frame,
            fg_color=colors["bg_card"],
            corner_radius=10
        )
        self.mistakes_list.pack(fill="both", expand=True)

    def _create_formulas_tab(self):
        """创建公式速查Tab"""
        colors = get_colors()

        self.formulas_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # 公式分类选择
        formulas_header = ctk.CTkFrame(self.formulas_frame, fg_color=colors["bg_card"], corner_radius=10)
        formulas_header.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            formulas_header,
            text="📖 公式速查",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["accent_purple"]
        ).pack(side="left", padx=15, pady=10)

        self.formula_category_var = ctk.StringVar(value="极限")
        categories = self.controller.get_formula_categories()
        if not categories:
            categories = ["极限", "导数", "积分", "行列式", "矩阵", "特征值", "概率", "随机变量"]

        self.formula_category_menu = ctk.CTkOptionMenu(
            formulas_header,
            values=categories,
            variable=self.formula_category_var,
            width=110,
            height=30,
            font=ctk.CTkFont(size=13),
            fg_color=colors["bg_input"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_purple"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_card"],
            dropdown_hover_color=colors["accent_blue"],
            command=self._load_formulas
        )
        self.formula_category_menu.pack(side="right", padx=15, pady=10)

        # 公式列表
        self.formulas_list = ctk.CTkScrollableFrame(
            self.formulas_frame,
            fg_color=colors["bg_card"],
            corner_radius=10
        )
        self.formulas_list.pack(fill="both", expand=True)

    def _create_progress_tab(self):
        """创建进度Tab"""
        colors = get_colors()

        self.progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # 总体统计
        stats_card = ctk.CTkFrame(self.progress_frame, fg_color=colors["bg_card"], corner_radius=10)
        stats_card.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            stats_card,
            text="📊 学习统计",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["accent_blue"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        stats_row = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_row.pack(fill="x", padx=15, pady=(0, 10))

        # 统计卡片
        for label, color, var_name in [
            ("总做题", colors["accent_blue"], "total_done"),
            ("正确数", colors["accent_green"], "total_correct"),
            ("正确率", colors["accent_yellow"], "accuracy")
        ]:
            stat_frame = ctk.CTkFrame(stats_row, fg_color=colors["bg_input"], corner_radius=8)
            stat_frame.pack(side="left", expand=True, fill="x", padx=3)

            value_label = ctk.CTkLabel(
                stat_frame,
                text="0",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color
            )
            value_label.pack(pady=(8, 2))
            setattr(self, f"stat_{var_name}_label", value_label)

            ctk.CTkLabel(
                stat_frame,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=colors["text_secondary"]
            ).pack(pady=(0, 8))

        # 章节进度
        self.chapter_progress_frame = ctk.CTkScrollableFrame(
            self.progress_frame,
            fg_color=colors["bg_card"],
            corner_radius=10
        )
        self.chapter_progress_frame.pack(fill="both", expand=True, pady=5)

    def _switch_tab(self, tab):
        """切换Tab"""
        colors = get_colors()
        self.current_tab = tab

        # 更新按钮样式
        for tab_id, btn in self.tab_btns.items():
            if tab_id == tab:
                btn.configure(fg_color=colors["accent_blue"], text_color="#ffffff")
            else:
                btn.configure(fg_color=colors["bg_input"], text_color=colors["text_primary"])

        self._show_tab(tab)

    def _show_tab(self, tab):
        """显示指定Tab"""
        # 隐藏所有Tab
        self.practice_frame.pack_forget()
        self.mistakes_frame.pack_forget()
        self.formulas_frame.pack_forget()
        self.progress_frame.pack_forget()

        # 显示指定Tab
        if tab == "practice":
            self.practice_frame.pack(fill="both", expand=True)
        elif tab == "mistakes":
            self.mistakes_frame.pack(fill="both", expand=True)
            self._load_mistakes_list()
        elif tab == "formulas":
            self.formulas_frame.pack(fill="both", expand=True)
            self._load_formulas(self.formula_category_var.get())
        elif tab == "progress":
            self.progress_frame.pack(fill="both", expand=True)
            self._load_progress()

    def _select_option(self, idx):
        """选择选项"""
        if self.controller.is_answered:
            return

        answer = chr(65 + idx)  # A, B, C, D
        self.controller.submit_answer(answer)

    def _on_answer_result(self, is_correct, correct_answer):
        """答题结果回调"""
        colors = get_colors()

        # 显示正确/错误反馈
        correct_idx = ord(correct_answer.upper()) - 65
        for i, btn in enumerate(self.option_btns):
            if i == correct_idx:
                btn.configure(fg_color=colors["accent_green"])
            elif self.controller.user_answer and ord(self.controller.user_answer.upper()) - 65 == i and not is_correct:
                btn.configure(fg_color=colors["accent_red"])

    def _toggle_solution(self):
        """切换解析显示"""
        self.controller.toggle_solution()

    def _add_to_mistakes(self):
        """添加到错题本"""
        is_new = self.controller.add_to_mistakes()
        colors = get_colors()

        if is_new:
            self.mistake_btn.configure(text="✅ 已加入", fg_color=colors["accent_green"])
        else:
            self.mistake_btn.configure(text="📝 已更新", fg_color=colors["accent_yellow"])

        self.after(1500, lambda: self.mistake_btn.configure(
            text="➕ 错题",
            fg_color=colors["bg_input"]
        ))

    def _update_question_display(self):
        """更新题目显示"""
        colors = get_colors()
        info = self.controller.get_current_question_info()

        if not info or not info["question"]:
            self.question_label.configure(text="暂无题目，请检查题库")
            self.chapter_label.configure(text="")
            self.difficulty_label.configure(text="")
            for btn in self.option_btns:
                btn.configure(text="", state="disabled")
            return

        question = info["question"]

        # 更新题目信息
        chapter = question.get("chapter", "")
        section = question.get("section", "")
        self.chapter_label.configure(text=f"{chapter} - {section}")

        difficulty = question.get("difficulty", 1)
        stars = "⭐" * difficulty
        self.difficulty_label.configure(text=f"难度: {stars}")

        # 更新题目文本 - 使用 LaTeX 转换
        question_text = question.get("question", "")
        display_text = latex_to_readable(question_text)
        self.question_label.configure(text=display_text)

        # 更新选项
        options = question.get("options", [])
        for i, btn in enumerate(self.option_btns):
            if i < len(options):
                # 选项也需要转换 LaTeX
                option_text = latex_to_readable(options[i])
                btn.configure(
                    text=f"{chr(65+i)}. {option_text}",
                    state="normal",
                    fg_color=colors["bg_input"],
                    text_color=colors["text_primary"]
                )
            else:
                btn.configure(text="", state="disabled")

        # 显示/隐藏解析
        if info["show_solution"]:
            solution = question.get("solution", "暂无解析")
            # 解析也需要转换 LaTeX
            self.solution_label.configure(text=latex_to_readable(solution))
            self.solution_frame.pack(fill="x", padx=15, pady=(5, 10))
        else:
            self.solution_frame.pack_forget()

        # 更新错题按钮状态
        if question.get("from_mistakes"):
            self.mistake_btn.configure(text="📕 来自错题")
        else:
            self.mistake_btn.configure(text="➕ 错题")

    def _update_progress_display(self):
        """更新进度显示"""
        self.progress_label.configure(text=self.controller.get_progress_text())

    def _load_mistakes_list(self):
        """加载错题列表"""
        colors = get_colors()

        # 清空列表
        for widget in self.mistakes_list.winfo_children():
            widget.destroy()

        mistakes = self.controller.load_mistakes()

        if not mistakes:
            ctk.CTkLabel(
                self.mistakes_list,
                text="暂无错题 🎉\n做题时点击「➕ 错题」可添加\n或点击「📷 导入图片」添加图片错题",
                font=ctk.CTkFont(size=13),
                text_color=colors["text_secondary"]
            ).pack(pady=50)
            return

        for item in mistakes:
            mistake = item["mistake"]
            question = item["question"]

            item_frame = ctk.CTkFrame(self.mistakes_list, fg_color=colors["bg_input"], corner_radius=8)
            item_frame.pack(fill="x", padx=10, pady=3)

            # 判断是否是图片类型
            if question.get("type") == "image":
                # 图片错题显示
                info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                info_frame.pack(fill="x", padx=10, pady=8)

                # 显示章节和标记
                ctk.CTkLabel(
                    info_frame,
                    text=f"📷 {question.get('chapter', '其他')} - {question.get('section', '其他')}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=colors["accent_blue"]
                ).pack(side="left")

                # 显示是否有答案图片
                answer_path = question.get("answer_image_path")
                if answer_path and os.path.exists(answer_path):
                    ctk.CTkLabel(
                        info_frame,
                        text="✅ 有答案",
                        font=ctk.CTkFont(size=10),
                        text_color=colors["accent_green"]
                    ).pack(side="left", padx=10)

                # 显示图片缩略图（如果存在）
                image_path = question.get("image_path", "")
                if image_path and os.path.exists(image_path):
                    try:
                        img = Image.open(image_path)
                        img.thumbnail((60, 40))
                        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 40))
                        ctk.CTkLabel(
                            info_frame,
                            image=ctk_img,
                            text=""
                        ).pack(side="right", padx=5)
                    except:
                        pass

                # 笔记预览
                notes = mistake.get("notes", "")
                if notes:
                    notes_preview = notes[:30] + "..." if len(notes) > 30 else notes
                    ctk.CTkLabel(
                        item_frame,
                        text=f"📝 {notes_preview}",
                        font=ctk.CTkFont(size=10),
                        text_color=colors["text_secondary"]
                    ).pack(anchor="w", padx=10, pady=(0, 5))
            else:
                # 普通题库错题
                q_text = question.get("question", "")
                # 转换 LaTeX
                q_text = latex_to_readable(q_text)
                q_text = q_text[:50] + "..." if len(q_text) > 50 else q_text

                ctk.CTkLabel(
                    item_frame,
                    text=q_text,
                    font=ctk.CTkFont(size=11),
                    text_color=colors["text_primary"],
                    anchor="w"
                ).pack(side="left", fill="x", expand=True, padx=10, pady=8)

            # 错误次数
            wrong_count = mistake.get("wrong_count", 1)
            ctk.CTkLabel(
                item_frame,
                text=f"错{wrong_count}次",
                font=ctk.CTkFont(size=10),
                text_color=colors["accent_red"]
            ).pack(side="right", padx=10)

    def _load_formulas(self, category):
        """加载公式列表"""
        colors = get_colors()

        # 清空列表
        for widget in self.formulas_list.winfo_children():
            widget.destroy()

        formulas = self.controller.load_formulas(category)

        if not formulas:
            ctk.CTkLabel(
                self.formulas_list,
                text="暂无公式数据",
                font=ctk.CTkFont(size=13),
                text_color=colors["text_secondary"]
            ).pack(pady=50)
            return

        for formula in formulas:
            item_frame = ctk.CTkFrame(self.formulas_list, fg_color=colors["bg_input"], corner_radius=8)
            item_frame.pack(fill="x", padx=10, pady=4)

            # 公式名称
            ctk.CTkLabel(
                item_frame,
                text=formula.get("name", ""),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=colors["accent_blue"]
            ).pack(anchor="w", padx=15, pady=(10, 3))

            # 公式内容（使用 LaTeX 转换）
            formula_text = formula.get("formula", "")
            readable_formula = latex_to_readable(formula_text)
            ctk.CTkLabel(
                item_frame,
                text=readable_formula,
                font=ctk.CTkFont(size=15),
                text_color=colors["text_primary"],
                wraplength=380
            ).pack(anchor="w", padx=15, pady=(0, 3))

            # 描述
            desc = formula.get("description", "")
            if desc:
                ctk.CTkLabel(
                    item_frame,
                    text=desc,
                    font=ctk.CTkFont(size=12),
                    text_color=colors["text_secondary"]
                ).pack(anchor="w", padx=15, pady=(0, 10))

    def _load_progress(self):
        """加载进度数据"""
        colors = get_colors()

        # 更新总体统计
        stats = self.controller.get_overall_stats()
        self.stat_total_done_label.configure(text=str(stats.get("total_done", 0)))
        self.stat_total_correct_label.configure(text=str(stats.get("total_correct", 0)))
        self.stat_accuracy_label.configure(text=f"{stats.get('accuracy', 0)}%")

        # 清空章节进度
        for widget in self.chapter_progress_frame.winfo_children():
            widget.destroy()

        # 加载章节进度
        progress_data = self.controller.get_chapter_progress()

        for chapter, sections in progress_data.items():
            # 章节标题
            chapter_label = ctk.CTkLabel(
                self.chapter_progress_frame,
                text=f"📚 {chapter}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=colors["text_primary"]
            )
            chapter_label.pack(anchor="w", padx=15, pady=(10, 5))

            # 小节进度
            for section, data in sections.items():
                section_frame = ctk.CTkFrame(
                    self.chapter_progress_frame,
                    fg_color=colors["bg_input"],
                    corner_radius=5
                )
                section_frame.pack(fill="x", padx=15, pady=2)

                ctk.CTkLabel(
                    section_frame,
                    text=section,
                    font=ctk.CTkFont(size=11),
                    text_color=colors["text_primary"]
                ).pack(side="left", padx=10, pady=5)

                done = data.get("done", 0)
                correct = data.get("correct", 0)
                accuracy = round(correct / done * 100, 1) if done > 0 else 0

                ctk.CTkLabel(
                    section_frame,
                    text=f"做题: {done}  正确率: {accuracy}%",
                    font=ctk.CTkFont(size=10),
                    text_color=colors["text_secondary"]
                ).pack(side="right", padx=10, pady=5)

    def _start_mistake_review(self):
        """开始错题复习"""
        self.controller.start_mistake_review()
        self._switch_tab("practice")

    def _show_import_dialog(self):
        """显示错题导入对话框"""
        from views.dialogs import MathMistakeDialog

        def on_import(question_image_path, answer_image_path, chapter, section, difficulty, notes):
            """导入回调"""
            self.controller.add_image_mistake(
                image_path=question_image_path,
                chapter=chapter,
                section=section,
                notes=notes,
                difficulty=difficulty,
                answer_image_path=answer_image_path
            )
            # 刷新错题列表
            self._load_mistakes_list()

        MathMistakeDialog(self.winfo_toplevel(), on_import=on_import)

    def _on_theme_change(self, theme):
        """主题变化回调"""
        self._apply_theme()

    def _apply_theme(self):
        """应用当前主题颜色"""
        colors = get_colors()

        # 更新头部
        self.header.configure(fg_color=colors["bg_card"])
        self.title_label.configure(text_color=colors["accent_blue"])

        # 更新Tab按钮
        for tab_id, btn in self.tab_btns.items():
            if tab_id == self.current_tab:
                btn.configure(
                    fg_color=colors["accent_blue"],
                    hover_color=colors["accent_purple"],
                    text_color="#ffffff"
                )
            else:
                btn.configure(
                    fg_color=colors["bg_input"],
                    hover_color=colors["border"],
                    text_color=colors["text_primary"]
                )

        # 更新刷题区域
        self.question_card.configure(fg_color=colors["bg_card"])
        self.chapter_label.configure(text_color=colors["text_secondary"])
        self.difficulty_label.configure(text_color=colors["accent_yellow"])
        self.question_text_frame.configure(fg_color=colors["bg_input"])
        self.question_label.configure(text_color=colors["text_primary"])

        for btn in self.option_btns:
            if not self.controller.is_answered:
                btn.configure(
                    fg_color=colors["bg_input"],
                    hover_color=colors["accent_blue"],
                    text_color=colors["text_primary"]
                )

        self.solution_frame.configure(fg_color=colors["bg_input"])
        self.solution_title.configure(text_color=colors["accent_green"])
        self.solution_label.configure(text_color=colors["text_primary"])

        # 更新操作按钮
        self.action_frame.configure(fg_color=colors["bg_card"])
        self.prev_btn.configure(
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"]
        )
        self.solution_btn.configure(
            fg_color=colors["bg_input"],
            hover_color=colors["accent_purple"],
            text_color=colors["text_primary"]
        )
        self.mistake_btn.configure(
            fg_color=colors["bg_input"],
            hover_color=colors["accent_red"],
            text_color=colors["text_primary"]
        )
        self.next_btn.configure(
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"]
        )
        self.progress_label.configure(text_color=colors["text_secondary"])

        # 更新错题本
        self.mistakes_list.configure(fg_color=colors["bg_card"])
        self.review_btn.configure(fg_color=colors["accent_green"])
        self.import_mistake_btn.configure(
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"]
        )

        # 更新公式
        self.formulas_list.configure(fg_color=colors["bg_card"])
        self.formula_category_menu.configure(
            fg_color=colors["bg_input"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_purple"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_card"],
            dropdown_hover_color=colors["accent_blue"]
        )

        # 更新进度
        self.chapter_progress_frame.configure(fg_color=colors["bg_card"])

        # 重新加载当前Tab以应用颜色
        if self.current_tab == "mistakes":
            self._load_mistakes_list()
        elif self.current_tab == "formulas":
            self._load_formulas(self.formula_category_var.get())
        elif self.current_tab == "progress":
            self._load_progress()

    def destroy(self):
        """销毁组件时注销回调"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
