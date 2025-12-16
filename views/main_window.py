"""
主窗口模块
作者：哈雷酱 (￣▽￣)
"""

import customtkinter as ctk
from config import get_colors, APP_NAME, DEFAULT_FOCUS_TIME, theme_manager
from models import SubjectModel, RecordModel
from controllers import PomodoroController, FocusController, ReminderController
from views.components import HeaderComponent, StatsCard, PomodoroCard, TodoList, WordCard, MathCard
from views.dialogs import (
    StatsDialog, SubjectDialog, WordbookDialog,
    WordStatsDialog, WordSettingsDialog,
    ReminderDialog, ReminderNotification
)


class StudyAssistantApp(ctk.CTk):
    """学习助手主窗口"""

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("920x720")
        self.resizable(False, False)

        # 设置主题（根据保存的设置）
        ctk.set_appearance_mode(theme_manager.current_theme)
        ctk.set_default_color_theme("blue")

        colors = get_colors()
        self.configure(fg_color=colors["bg_dark"])
        self.attributes("-topmost", True)

        try:
            self.attributes("-alpha", 0.92)
        except:
            pass

        self._init_controllers()
        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # 注册主题变化回调
        theme_manager.register_callback(self._on_theme_change)

    def _init_controllers(self):
        """初始化控制器"""
        self.pomodoro_controller = PomodoroController(
            on_tick=self._on_pomodoro_tick,
            on_complete=self._on_pomodoro_complete,
            on_stats_update=self._update_stats_display
        )

        self.focus_controller = FocusController(
            on_stats_update=self._update_stats_display
        )

        self.reminder_controller = ReminderController(
            on_reminder=self._on_reminder_triggered
        )
        self.reminder_controller.start()

    def _create_widgets(self):
        """创建所有控件"""
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.header = HeaderComponent(
            self.main_container,
            on_opacity_change=self._change_opacity,
            on_theme_toggle=self._handle_theme_toggle
        )
        self.header.pack(fill="x", padx=0, pady=0)

        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.left_column = ctk.CTkFrame(self.content_frame, fg_color="transparent", width=410)
        self.left_column.pack(side="left", fill="both", padx=(0, 5))
        self.left_column.pack_propagate(False)

        self.right_column = ctk.CTkFrame(self.content_frame, fg_color="transparent", width=490)
        self.right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self._create_left_panel()
        self._create_right_panel()
        self._update_stats_display()

    def _create_left_panel(self):
        """创建左栏 - 学习管理面板"""
        self.stats_card = StatsCard(
            self.left_column,
            on_detail_click=self._show_stats_dialog
        )
        self.stats_card.pack(fill="x", padx=5, pady=5)

        subjects = SubjectModel.load_subjects()
        self.pomodoro_card = PomodoroCard(
            self.left_column,
            subjects=subjects,
            on_start=self._toggle_pomodoro,
            on_reset=self._reset_pomodoro,
            on_subject_change=self._on_subject_change,
            on_manage_subjects=self._show_subject_dialog
        )
        self.pomodoro_card.pack(fill="x", padx=5, pady=5)

        self.todo_list = TodoList(
            self.left_column,
            on_stats_update=self._update_stats_display,
            on_reminder_click=self._show_reminder_dialog
        )
        self.todo_list.pack(fill="both", expand=True, padx=5, pady=5)

        self._create_focus_tracker()

    def _create_focus_tracker(self):
        """创建专注记录区域"""
        colors = get_colors()

        self.bottom_frame = ctk.CTkFrame(self.left_column, fg_color=colors["bg_card"], corner_radius=10)
        self.bottom_frame.pack(fill="x", padx=5, pady=5)

        self.track_subject_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.track_subject_frame.pack(fill="x", padx=15, pady=(8, 5))

        self.track_label = ctk.CTkLabel(
            self.track_subject_frame,
            text="记录科目：",
            font=ctk.CTkFont(size=10),
            text_color=colors["text_secondary"]
        )
        self.track_label.pack(side="left")

        subjects = SubjectModel.load_subjects()
        self.track_subject_var = ctk.StringVar(value="其他")
        self.track_subject_menu = ctk.CTkOptionMenu(
            self.track_subject_frame,
            values=subjects,
            variable=self.track_subject_var,
            width=100,
            height=28,
            font=ctk.CTkFont(size=13),
            fg_color=colors["bg_input"],
            button_color=colors["accent_green"],
            button_hover_color=colors["accent_blue"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_card"],
            dropdown_hover_color=colors["accent_green"]
        )
        self.track_subject_menu.pack(side="left", padx=5)

        self.focus_track_btn = ctk.CTkButton(
            self.bottom_frame,
            text="⏱ 开始记录学习时长",
            height=32,
            fg_color=colors["accent_green"],
            hover_color="#2ea043",
            text_color="#000000",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._toggle_focus_tracking
        )
        self.focus_track_btn.pack(fill="x", padx=15, pady=(5, 8))

    def _create_right_panel(self):
        """创建右栏 - 学习面板（英语/数学切换）"""
        colors = get_colors()

        # 顶部切换按钮
        self.right_header = ctk.CTkFrame(self.right_column, fg_color=colors["bg_card"], corner_radius=10)
        self.right_header.pack(fill="x", padx=5, pady=5)

        header_inner = ctk.CTkFrame(self.right_header, fg_color="transparent")
        header_inner.pack(fill="x", padx=10, pady=8)

        self.current_right_tab = "english"  # 当前Tab

        self.english_tab_btn = ctk.CTkButton(
            header_inner,
            text="📖 英语单词",
            width=100,
            height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=colors["accent_purple"],
            hover_color=colors["accent_blue"],
            text_color="#ffffff",
            command=lambda: self._switch_right_tab("english")
        )
        self.english_tab_btn.pack(side="left", padx=5)

        self.math_tab_btn = ctk.CTkButton(
            header_inner,
            text="📐 考研数学",
            width=100,
            height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=colors["bg_input"],
            hover_color=colors["accent_blue"],
            text_color=colors["text_primary"],
            command=lambda: self._switch_right_tab("math")
        )
        self.math_tab_btn.pack(side="left", padx=5)

        # 内容容器
        self.right_content = ctk.CTkFrame(self.right_column, fg_color="transparent")
        self.right_content.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # 英语单词卡片
        self.word_card = WordCard(
            self.right_content,
            on_wordbook_click=self._show_wordbook_dialog,
            on_stats_click=self._show_word_stats_dialog,
            on_settings_click=self._show_word_settings_dialog
        )

        # 数学卡片
        self.math_card = MathCard(self.right_content)

        # 默认显示英语
        self._show_right_tab("english")

    def _switch_right_tab(self, tab):
        """切换右侧面板Tab"""
        colors = get_colors()
        self.current_right_tab = tab

        if tab == "english":
            self.english_tab_btn.configure(
                fg_color=colors["accent_purple"],
                text_color="#ffffff"
            )
            self.math_tab_btn.configure(
                fg_color=colors["bg_input"],
                text_color=colors["text_primary"]
            )
        else:
            self.english_tab_btn.configure(
                fg_color=colors["bg_input"],
                text_color=colors["text_primary"]
            )
            self.math_tab_btn.configure(
                fg_color=colors["accent_blue"],
                text_color="#ffffff"
            )

        self._show_right_tab(tab)

    def _show_right_tab(self, tab):
        """显示指定的右侧Tab"""
        self.word_card.pack_forget()
        self.math_card.pack_forget()

        if tab == "english":
            self.word_card.pack(fill="both", expand=True)
        else:
            self.math_card.pack(fill="both", expand=True)

    def _on_closing(self):
        """窗口关闭处理"""
        theme_manager.unregister_callback(self._on_theme_change)
        self.reminder_controller.stop()
        self.pomodoro_controller.reset()
        if self.focus_controller.is_tracking:
            self.focus_controller.stop()
        self.destroy()

    def _change_opacity(self, value):
        try:
            self.attributes("-alpha", value)
        except:
            pass

    def _handle_theme_toggle(self, theme):
        """主题切换按钮回调（来自 HeaderComponent）"""
        # HeaderComponent 会触发 theme_manager.toggle_theme()
        # theme_manager 会通知所有注册的回调
        pass

    def _on_theme_change(self, theme):
        """主题变化回调"""
        colors = get_colors()

        # 更新主窗口背景
        self.configure(fg_color=colors["bg_dark"])

        # 更新右侧面板切换按钮
        self.right_header.configure(fg_color=colors["bg_card"])
        if self.current_right_tab == "english":
            self.english_tab_btn.configure(
                fg_color=colors["accent_purple"],
                hover_color=colors["accent_blue"],
                text_color="#ffffff"
            )
            self.math_tab_btn.configure(
                fg_color=colors["bg_input"],
                hover_color=colors["accent_blue"],
                text_color=colors["text_primary"]
            )
        else:
            self.english_tab_btn.configure(
                fg_color=colors["bg_input"],
                hover_color=colors["accent_blue"],
                text_color=colors["text_primary"]
            )
            self.math_tab_btn.configure(
                fg_color=colors["accent_blue"],
                hover_color=colors["accent_purple"],
                text_color="#ffffff"
            )

        # 更新专注记录区域
        self.bottom_frame.configure(fg_color=colors["bg_card"])
        self.track_label.configure(text_color=colors["text_secondary"])
        self.track_subject_menu.configure(
            fg_color=colors["bg_input"],
            button_color=colors["accent_green"],
            button_hover_color=colors["accent_blue"],
            text_color=colors["text_primary"],
            dropdown_text_color=colors["text_primary"],
            dropdown_fg_color=colors["bg_card"],
            dropdown_hover_color=colors["accent_green"]
        )

        # 更新专注按钮（根据当前状态）
        if self.focus_controller.is_tracking:
            self.focus_track_btn.configure(fg_color=colors["accent_red"])
        else:
            self.focus_track_btn.configure(fg_color=colors["accent_green"])

    def _update_stats_display(self):
        stats = RecordModel.get_today_stats()
        self.stats_card.update_stats(
            stats["focus_time"],
            stats["completed_tasks"],
            stats["pomodoros"]
        )

    def _toggle_pomodoro(self):
        colors = get_colors()
        if not self.pomodoro_controller.running:
            subject = self.pomodoro_card.get_current_subject()
            self.pomodoro_controller.start(subject)
            self.pomodoro_card.update_start_button(True)
            self._update_pomodoro_status()
        else:
            self.pomodoro_controller.pause()
            self.pomodoro_card.update_start_button(False)
            self.pomodoro_card.update_status("已暂停", colors["text_secondary"])

    def _reset_pomodoro(self):
        colors = get_colors()
        self.pomodoro_controller.reset()
        self.pomodoro_card.update_timer(PomodoroController.format_time(DEFAULT_FOCUS_TIME * 60))
        self.pomodoro_card.update_start_button(False)
        self.pomodoro_card.update_status("准备开始专注", colors["text_secondary"])
        self.pomodoro_card.timer_label.configure(text_color=colors["accent_blue"])

    def _on_pomodoro_tick(self, remaining_seconds):
        self.after(0, lambda: self._update_pomodoro_timer(remaining_seconds))

    def _update_pomodoro_timer(self, remaining_seconds):
        time_str = PomodoroController.format_time(remaining_seconds)
        self.pomodoro_card.update_timer(time_str)
        self.pomodoro_card.update_timer_color(
            remaining_seconds,
            self.pomodoro_controller.is_focus_time
        )

    def _on_pomodoro_complete(self, was_focus_time):
        self.after(0, lambda: self._handle_pomodoro_complete(was_focus_time))

    def _handle_pomodoro_complete(self, was_focus_time):
        colors = get_colors()
        self.pomodoro_card.update_start_button(False)
        if was_focus_time:
            self.pomodoro_card.update_status("🎉 专注完成！休息一下吧", colors["accent_yellow"])
        else:
            self.pomodoro_card.update_status("☕ 休息结束！准备下一轮", colors["accent_blue"])
        time_str = PomodoroController.format_time(self.pomodoro_controller.remaining_seconds)
        self.pomodoro_card.update_timer(time_str)

    def _update_pomodoro_status(self):
        colors = get_colors()
        status = self.pomodoro_controller.status_text
        if self.pomodoro_controller.is_focus_time:
            color = colors["accent_green"]
        else:
            color = colors["accent_yellow"]
        self.pomodoro_card.update_status(status, color)

    def _on_subject_change(self, value):
        self.pomodoro_controller.current_subject = value

    def _toggle_focus_tracking(self):
        colors = get_colors()
        if not self.focus_controller.is_tracking:
            subject = self.track_subject_var.get()
            self.focus_controller.start(subject)
            self.focus_track_btn.configure(
                text=f"⏹ 停止记录 ({subject})",
                fg_color=colors["accent_red"],
                hover_color="#da3633"
            )
        else:
            self.focus_controller.stop()
            self.focus_track_btn.configure(
                text="⏱ 开始记录学习时长",
                fg_color=colors["accent_green"],
                hover_color="#2ea043"
            )

    def _show_reminder_dialog(self, todo):
        ReminderDialog(
            self,
            todo,
            self.reminder_controller,
            on_close=self.todo_list.load_todos
        )

    def _on_reminder_triggered(self, task_text, reminder_time):
        self.after(0, lambda: self._show_reminder_notification(task_text, reminder_time))

    def _show_reminder_notification(self, task_text, reminder_time):
        ReminderNotification(self, task_text, reminder_time)
        self.todo_list.load_todos()

    def _show_stats_dialog(self):
        StatsDialog(self)

    def _show_subject_dialog(self):
        SubjectDialog(self, on_close=self._on_subjects_updated)

    def _on_subjects_updated(self, subjects):
        self.pomodoro_card.update_subjects(subjects)
        self.track_subject_menu.configure(values=subjects)

    def _show_wordbook_dialog(self):
        WordbookDialog(self, on_words_imported=self.word_card.reload_words)

    def _show_word_stats_dialog(self):
        WordStatsDialog(self)

    def _show_word_settings_dialog(self):
        WordSettingsDialog(self, on_save=self.word_card._update_progress_display)
