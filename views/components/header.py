"""
顶部标题栏组件
"""

import customtkinter as ctk
from datetime import datetime
from config import get_colors, theme_manager


class HeaderComponent(ctk.CTkFrame):
    """顶部标题栏组件"""

    def __init__(self, parent, on_opacity_change=None, on_theme_toggle=None, **kwargs):
        """初始化标题栏组件

        Args:
            parent: 父容器
            on_opacity_change: 透明度变化回调函数
            on_theme_toggle: 主题切换回调函数
        """
        colors = get_colors()
        super().__init__(parent, fg_color=colors["bg_card"], corner_radius=0, **kwargs)

        self._on_opacity_change = on_opacity_change
        self._on_theme_toggle = on_theme_toggle
        self._drag_data = {"x": 0, "y": 0}

        self._create_widgets()
        self._bind_events()

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _create_widgets(self):
        """创建控件"""
        colors = get_colors()

        # 标题
        self.title_label = ctk.CTkLabel(
            self,
            text="📚 ImgMaster的专用学习助手",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=colors["accent_blue"]
        )
        self.title_label.pack(side="left", padx=15, pady=10)

        # 日期显示
        self.date_label = ctk.CTkLabel(
            self,
            text=datetime.now().strftime("%m月%d日"),
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.date_label.pack(side="right", padx=15, pady=10)

        # 主题切换按钮
        theme_icon = "🌙" if theme_manager.is_dark else "☀️"
        self.theme_btn = ctk.CTkButton(
            self,
            text=theme_icon,
            width=32,
            height=28,
            fg_color=colors["bg_input"],
            hover_color=colors["accent_purple"],
            text_color=colors["text_primary"],
            command=self._toggle_theme
        )
        self.theme_btn.pack(side="right", padx=5, pady=10)

        # 透明度调节
        self.opacity_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.opacity_frame.pack(side="right", padx=10)

        self.opacity_icon_label = ctk.CTkLabel(
            self.opacity_frame,
            text="🔆",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.opacity_icon_label.pack(side="left", padx=2)

        self.opacity_slider = ctk.CTkSlider(
            self.opacity_frame,
            from_=0.3,
            to=1.0,
            number_of_steps=70,
            width=100,
            height=14,
            fg_color=colors["bg_input"],
            progress_color=colors["accent_blue"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_purple"],
            command=self._on_slider_change
        )
        self.opacity_slider.set(0.92)
        self.opacity_slider.pack(side="left", padx=2)

        self.opacity_value_label = ctk.CTkLabel(
            self.opacity_frame,
            text="92%",
            font=ctk.CTkFont(size=10),
            text_color=colors["text_secondary"],
            width=30
        )
        self.opacity_value_label.pack(side="left", padx=2)

    def _bind_events(self):
        """绑定事件"""
        self.bind("<Button-1>", self._start_move)
        self.bind("<B1-Motion>", self._on_move)
        self.title_label.bind("<Button-1>", self._start_move)
        self.title_label.bind("<B1-Motion>", self._on_move)

    def _start_move(self, event):
        """开始拖动"""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_move(self, event):
        """拖动中"""
        root = self.winfo_toplevel()
        x = root.winfo_x() + (event.x - self._drag_data["x"])
        y = root.winfo_y() + (event.y - self._drag_data["y"])
        root.geometry(f"+{x}+{y}")

    def _on_slider_change(self, value):
        """透明度滑块变化"""
        percent = int(value * 100)
        self.opacity_value_label.configure(text=f"{percent}%")

        if self._on_opacity_change:
            self._on_opacity_change(value)

    def _toggle_theme(self):
        """切换主题"""
        new_theme = theme_manager.toggle_theme()

        # 更新按钮图标
        theme_icon = "🌙" if new_theme == "dark" else "☀️"
        self.theme_btn.configure(text=theme_icon)

        # 更新 customtkinter 的外观模式
        ctk.set_appearance_mode(new_theme)

        if self._on_theme_toggle:
            self._on_theme_toggle(new_theme)

    def update_theme_button(self):
        """更新主题按钮图标"""
        theme_icon = "🌙" if theme_manager.is_dark else "☀️"
        self.theme_btn.configure(text=theme_icon)

    def _on_theme_change(self, theme):
        """主题变化回调"""
        self._apply_theme()

    def _apply_theme(self):
        """应用当前主题颜色"""
        colors = get_colors()

        # 更新自身背景
        self.configure(fg_color=colors["bg_card"])

        # 更新标题颜色
        self.title_label.configure(text_color=colors["accent_blue"])

        # 更新日期颜色
        self.date_label.configure(text_color=colors["text_secondary"])

        # 更新主题按钮
        theme_icon = "🌙" if theme_manager.is_dark else "☀️"
        self.theme_btn.configure(
            text=theme_icon,
            fg_color=colors["bg_input"],
            hover_color=colors["accent_purple"],
            text_color=colors["text_primary"]
        )

        # 更新透明度相关组件
        self.opacity_icon_label.configure(text_color=colors["text_secondary"])
        self.opacity_slider.configure(
            fg_color=colors["bg_input"],
            progress_color=colors["accent_blue"],
            button_color=colors["accent_blue"],
            button_hover_color=colors["accent_purple"]
        )
        self.opacity_value_label.configure(text_color=colors["text_secondary"])

    def destroy(self):
        """销毁组件时注销回调"""
        theme_manager.unregister_callback(self._on_theme_change)
        super().destroy()
