"""
科目管理对话框
"""

import customtkinter as ctk
from config import get_colors, theme_manager
from models import SubjectModel


class SubjectDialog(ctk.CTkToplevel):
    """科目管理对话框"""

    def __init__(self, parent, on_close=None, **kwargs):
        """初始化科目管理对话框

        Args:
            parent: 父窗口
            on_close: 关闭时回调（返回更新后的科目列表）
        """
        super().__init__(parent, **kwargs)

        self._on_close = on_close

        colors = get_colors()
        self.title("管理科目")
        self.geometry("300x400")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=colors["bg_dark"])
        self.geometry(f"+{parent.winfo_x() + 60}+{parent.winfo_y() + 100}")

        self._create_widgets()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        # 标题
        self.title_label = ctk.CTkLabel(
            self,
            text="📚 科目管理",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["accent_blue"]
        )
        self.title_label.pack(pady=(15, 10))

        # 添加新科目
        self.add_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.add_frame.pack(fill="x", padx=15, pady=5)

        self.new_subject_entry = ctk.CTkEntry(
            self.add_frame,
            placeholder_text="输入新科目名称",
            fg_color=colors["bg_input"],
            border_color=colors["border"],
            text_color=colors["text_primary"]
        )
        self.new_subject_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.add_btn = ctk.CTkButton(
            self.add_frame,
            text="添加",
            width=60,
            fg_color=colors["accent_green"],
            hover_color="#2ea043",
            text_color="#ffffff",
            command=self._add_subject
        )
        self.add_btn.pack(side="right")

        # 科目列表
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=colors["bg_card"])
        self.list_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self._refresh_list()

        # 关闭按钮
        self.close_btn = ctk.CTkButton(
            self,
            text="完成",
            fg_color=colors["accent_blue"],
            hover_color=colors["accent_purple"],
            text_color="#ffffff",
            command=self._on_close_click
        )
        self.close_btn.pack(pady=15)

    def _add_subject(self):
        """添加新科目"""
        name = self.new_subject_entry.get().strip()
        if name:
            SubjectModel.add_subject(name)
            self.new_subject_entry.delete(0, 'end')
            self._refresh_list()

    def _refresh_list(self):
        """刷新科目列表"""
        colors = get_colors()

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        subjects = SubjectModel.load_subjects()
        for subject in subjects:
            item_frame = ctk.CTkFrame(self.list_frame, fg_color=colors["bg_input"], corner_radius=5)
            item_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(
                item_frame,
                text=subject,
                text_color=colors["text_primary"]
            ).pack(side="left", padx=10, pady=5)

            if subject != "其他":
                def delete_subject(s=subject):
                    SubjectModel.remove_subject(s)
                    self._refresh_list()

                ctk.CTkButton(
                    item_frame,
                    text="×",
                    width=25,
                    height=25,
                    fg_color="transparent",
                    hover_color=colors["accent_red"],
                    text_color=colors["text_primary"],
                    command=delete_subject
                ).pack(side="right", padx=5, pady=2)

    def _on_close_click(self):
        """关闭按钮点击"""
        if self._on_close:
            subjects = SubjectModel.load_subjects()
            self._on_close(subjects)
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
        self.title_label.configure(text_color=colors["accent_blue"])

        # 更新输入框
        self.new_subject_entry.configure(
            fg_color=colors["bg_input"],
            border_color=colors["border"],
            text_color=colors["text_primary"]
        )

        # 更新添加按钮
        self.add_btn.configure(fg_color=colors["accent_green"])

        # 更新列表框架
        self.list_frame.configure(fg_color=colors["bg_card"])

        # 更新关闭按钮
        self.close_btn.configure(fg_color=colors["accent_blue"], hover_color=colors["accent_purple"])

        # 刷新列表以更新颜色
        self._refresh_list()

    def destroy(self):
        """销毁对话框"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
