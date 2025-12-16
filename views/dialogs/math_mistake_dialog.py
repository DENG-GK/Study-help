"""
数学错题导入对话框
"""

import customtkinter as ctk
from tkinter import filedialog
from config import get_colors, theme_manager, MATH_CHAPTERS
from PIL import Image
import os


class MathMistakeDialog(ctk.CTkToplevel):
    """数学错题导入对话框"""

    def __init__(self, parent, on_import=None, **kwargs):
        """初始化错题导入对话框

        Args:
            parent: 父窗口
            on_import: 导入后的回调
        """
        super().__init__(parent, **kwargs)

        self._on_import = on_import
        self._question_image_path = None  # 错题图片
        self._answer_image_path = None    # 答案图片
        self._question_preview = None
        self._answer_preview = None

        colors = get_colors()
        self.title("导入错题图片")
        self.geometry("500x720")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=colors["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 210}+{parent.winfo_y() + 10}")

        self._create_widgets()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        # 创建滚动容器
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 标题
        self.title_label = ctk.CTkLabel(
            self.scroll_frame,
            text="📷 导入错题图片",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["accent_red"]
        )
        self.title_label.pack(pady=(10, 10))

        # ========== 错题图片区域 ==========
        self.question_frame = ctk.CTkFrame(self.scroll_frame, fg_color=colors["bg_card"], corner_radius=10)
        self.question_frame.pack(fill="x", padx=10, pady=5)

        question_header = ctk.CTkFrame(self.question_frame, fg_color="transparent")
        question_header.pack(fill="x", padx=15, pady=(10, 5))

        self.question_title = ctk.CTkLabel(
            question_header,
            text="📝 错题图片",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["accent_blue"]
        )
        self.question_title.pack(side="left")

        self.question_status = ctk.CTkLabel(
            question_header,
            text="(必填)",
            font=ctk.CTkFont(size=11),
            text_color=colors["accent_red"]
        )
        self.question_status.pack(side="left", padx=5)

        # 错题图片预览
        self.question_preview_frame = ctk.CTkFrame(
            self.question_frame, fg_color=colors["bg_input"], corner_radius=8, height=150
        )
        self.question_preview_frame.pack(fill="x", padx=15, pady=5)
        self.question_preview_frame.pack_propagate(False)

        self.question_preview_label = ctk.CTkLabel(
            self.question_preview_frame,
            text="📷 点击选择错题图片\n拍摄或截图你的错题",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.question_preview_label.pack(expand=True)
        self.question_preview_label.bind("<Button-1>", lambda e: self._select_question_image())

        self.question_btn = ctk.CTkButton(
            self.question_frame,
            text="📂 选择错题图片",
            width=130,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"],
            text_color="#ffffff",
            command=self._select_question_image
        )
        self.question_btn.pack(pady=8)

        # ========== 答案图片区域 ==========
        self.answer_frame = ctk.CTkFrame(self.scroll_frame, fg_color=colors["bg_card"], corner_radius=10)
        self.answer_frame.pack(fill="x", padx=10, pady=5)

        answer_header = ctk.CTkFrame(self.answer_frame, fg_color="transparent")
        answer_header.pack(fill="x", padx=15, pady=(10, 5))

        self.answer_title = ctk.CTkLabel(
            answer_header,
            text="✅ 答案/解析图片",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["accent_green"]
        )
        self.answer_title.pack(side="left")

        self.answer_status = ctk.CTkLabel(
            answer_header,
            text="(可选)",
            font=ctk.CTkFont(size=11),
            text_color=colors["text_secondary"]
        )
        self.answer_status.pack(side="left", padx=5)

        # 答案图片预览
        self.answer_preview_frame = ctk.CTkFrame(
            self.answer_frame, fg_color=colors["bg_input"], corner_radius=8, height=150
        )
        self.answer_preview_frame.pack(fill="x", padx=15, pady=5)
        self.answer_preview_frame.pack_propagate(False)

        self.answer_preview_label = ctk.CTkLabel(
            self.answer_preview_frame,
            text="📷 点击选择答案图片\n可以是解析、答案或解题过程",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.answer_preview_label.pack(expand=True)
        self.answer_preview_label.bind("<Button-1>", lambda e: self._select_answer_image())

        self.answer_btn = ctk.CTkButton(
            self.answer_frame,
            text="📂 选择答案图片",
            width=130,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=colors["accent_green"],
            hover_color="#2ea043",
            text_color="#ffffff",
            command=self._select_answer_image
        )
        self.answer_btn.pack(pady=8)

        # ========== 错题信息 ==========
        self.info_frame = ctk.CTkFrame(self.scroll_frame, fg_color=colors["bg_card"], corner_radius=10)
        self.info_frame.pack(fill="x", padx=10, pady=5)

        self.info_title = ctk.CTkLabel(
            self.info_frame,
            text="📋 错题信息",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.info_title.pack(anchor="w", padx=15, pady=(10, 5))

        # 章节选择
        chapter_row = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        chapter_row.pack(fill="x", padx=15, pady=3)

        self.chapter_label = ctk.CTkLabel(
            chapter_row,
            text="章节：",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"],
            width=50
        )
        self.chapter_label.pack(side="left")

        chapters = list(MATH_CHAPTERS.keys())
        self.chapter_var = ctk.StringVar(value=chapters[0] if chapters else "高等数学")
        self.chapter_menu = ctk.CTkOptionMenu(
            chapter_row,
            values=chapters,
            variable=self.chapter_var,
            width=140,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_input"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_purple"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_card"],
            dropdown_hover_color=colors["accent_blue"],
            command=self._on_chapter_change
        )
        self.chapter_menu.pack(side="left", padx=5)

        # 小节选择
        section_row = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        section_row.pack(fill="x", padx=15, pady=3)

        self.section_label = ctk.CTkLabel(
            section_row,
            text="小节：",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"],
            width=50
        )
        self.section_label.pack(side="left")

        initial_sections = MATH_CHAPTERS.get(self.chapter_var.get(), ["其他"])
        self.section_var = ctk.StringVar(value=initial_sections[0] if initial_sections else "其他")
        self.section_menu = ctk.CTkOptionMenu(
            section_row,
            values=initial_sections,
            variable=self.section_var,
            width=140,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_input"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_purple"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_card"],
            dropdown_hover_color=colors["accent_blue"]
        )
        self.section_menu.pack(side="left", padx=5)

        # 难度选择
        difficulty_row = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        difficulty_row.pack(fill="x", padx=15, pady=3)

        self.difficulty_label = ctk.CTkLabel(
            difficulty_row,
            text="难度：",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"],
            width=50
        )
        self.difficulty_label.pack(side="left")

        self.difficulty_var = ctk.StringVar(value="⭐⭐⭐")
        self.difficulty_menu = ctk.CTkOptionMenu(
            difficulty_row,
            values=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
            variable=self.difficulty_var,
            width=140,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_input"],
            button_color=colors["accent_yellow"],
            button_hover_color=colors["accent_purple"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_card"],
            dropdown_hover_color=colors["accent_yellow"]
        )
        self.difficulty_menu.pack(side="left", padx=5)

        # 笔记
        self.notes_label = ctk.CTkLabel(
            self.info_frame,
            text="笔记（可选）：",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.notes_label.pack(anchor="w", padx=15, pady=(8, 2))

        self.notes_text = ctk.CTkTextbox(
            self.info_frame,
            height=60,
            font=ctk.CTkFont(size=12),
            fg_color=colors["bg_input"],
            text_color=colors["text_primary"],
            corner_radius=8
        )
        self.notes_text.pack(fill="x", padx=15, pady=(0, 10))

        # ========== 按钮区域 ==========
        btn_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)

        self.import_btn = ctk.CTkButton(
            btn_frame,
            text="✅ 导入错题",
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=colors["accent_green"],
            hover_color="#2ea043",
            text_color="#ffffff",
            command=self._import_mistake
        )
        self.import_btn.pack(side="left", expand=True, padx=5)

        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text="取消",
            width=100,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"],
            command=self.destroy
        )
        self.cancel_btn.pack(side="left", expand=True, padx=5)

    def _on_chapter_change(self, value):
        """章节变化时更新小节列表"""
        sections = MATH_CHAPTERS.get(value, ["其他"])
        self.section_menu.configure(values=sections)
        self.section_var.set(sections[0] if sections else "其他")

    def _select_question_image(self):
        """选择错题图片"""
        filepath = self._select_image_file()
        if filepath:
            self._question_image_path = filepath
            self._show_preview(filepath, "question")

    def _select_answer_image(self):
        """选择答案图片"""
        filepath = self._select_image_file()
        if filepath:
            self._answer_image_path = filepath
            self._show_preview(filepath, "answer")

    def _select_image_file(self):
        """选择图片文件"""
        filetypes = [
            ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("所有文件", "*.*")
        ]
        return filedialog.askopenfilename(filetypes=filetypes)

    def _show_preview(self, filepath, image_type):
        """显示图片预览

        Args:
            filepath: 图片路径
            image_type: 'question' 或 'answer'
        """
        colors = get_colors()
        try:
            # 加载并缩放图片
            img = Image.open(filepath)
            # 计算缩放比例，保持宽高比
            max_width = 420
            max_height = 130
            ratio = min(max_width / img.width, max_height / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 转换为 CTkImage
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=new_size)

            if image_type == "question":
                self._question_preview = ctk_img
                self.question_preview_label.configure(image=ctk_img, text="")
                self.question_status.configure(text="✅ 已选择", text_color=colors["accent_green"])
            else:
                self._answer_preview = ctk_img
                self.answer_preview_label.configure(image=ctk_img, text="")
                self.answer_status.configure(text="✅ 已选择", text_color=colors["accent_green"])

        except Exception as e:
            if image_type == "question":
                self.question_preview_label.configure(image=None, text=f"图片加载失败: {e}")
                self._question_image_path = None
            else:
                self.answer_preview_label.configure(image=None, text=f"图片加载失败: {e}")
                self._answer_image_path = None

    def _import_mistake(self):
        """导入错题"""
        colors = get_colors()

        if not self._question_image_path:
            self.question_status.configure(text="⚠️ 请选择错题图片！", text_color=colors["accent_red"])
            return

        # 获取难度（数字）
        difficulty_str = self.difficulty_var.get()
        difficulty = len(difficulty_str.replace(" ", ""))  # 计算星号数量

        # 获取笔记
        notes = self.notes_text.get("1.0", "end-1c").strip()

        # 调用回调
        if self._on_import:
            self._on_import(
                question_image_path=self._question_image_path,
                answer_image_path=self._answer_image_path,  # 可能为 None
                chapter=self.chapter_var.get(),
                section=self.section_var.get(),
                difficulty=difficulty,
                notes=notes
            )

        self.destroy()

    def _on_theme_change(self, theme):
        """主题变化回调"""
        self._apply_theme()

    def _apply_theme(self):
        """应用当前主题颜色"""
        colors = get_colors()

        # 更新窗口背景
        self.configure(fg_color=colors["bg_dark"])

        # 更新标题
        self.title_label.configure(text_color=colors["accent_red"])

        # 更新错题图片区域
        self.question_frame.configure(fg_color=colors["bg_card"])
        self.question_title.configure(text_color=colors["accent_blue"])
        self.question_preview_frame.configure(fg_color=colors["bg_input"])
        self.question_preview_label.configure(text_color=colors["text_secondary"])
        self.question_btn.configure(
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"]
        )

        # 更新答案图片区域
        self.answer_frame.configure(fg_color=colors["bg_card"])
        self.answer_title.configure(text_color=colors["accent_green"])
        self.answer_preview_frame.configure(fg_color=colors["bg_input"])
        self.answer_preview_label.configure(text_color=colors["text_secondary"])
        self.answer_btn.configure(
            fg_color=colors["accent_green"],
            hover_color="#2ea043"
        )

        # 更新信息区域
        self.info_frame.configure(fg_color=colors["bg_card"])
        self.info_title.configure(text_color=colors["text_primary"])
        self.chapter_label.configure(text_color=colors["text_secondary"])
        self.section_label.configure(text_color=colors["text_secondary"])
        self.difficulty_label.configure(text_color=colors["text_secondary"])
        self.notes_label.configure(text_color=colors["text_secondary"])

        # 更新下拉菜单
        for menu in [self.chapter_menu, self.section_menu, self.difficulty_menu]:
            menu.configure(
                fg_color=colors["bg_input"],
                text_color=colors["text_primary"],
                dropdown_text_color=colors["text_primary"],
                dropdown_fg_color=colors["bg_card"]
            )

        self.notes_text.configure(
            fg_color=colors["bg_input"],
            text_color=colors["text_primary"]
        )

        # 更新按钮
        self.import_btn.configure(fg_color=colors["accent_green"])
        self.cancel_btn.configure(
            fg_color=colors["bg_input"],
            hover_color=colors["border"],
            text_color=colors["text_primary"]
        )

    def destroy(self):
        """销毁对话框"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
