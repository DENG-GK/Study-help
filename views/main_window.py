"""
主窗口模块
作者：哈雷酱 (￣▽￣)
"""

import customtkinter as ctk
from config import COLORS, APP_NAME, DEFAULT_FOCUS_TIME
from models import SubjectModel, RecordModel
from controllers import PomodoroController, FocusController
from views.components import HeaderComponent, StatsCard, PomodoroCard, TodoList, WordCard
from views.dialogs import (
    StatsDialog, SubjectDialog, WordbookDialog,
    WordStatsDialog, WordSettingsDialog
)


class StudyAssistantApp(ctk.CTk):
    """学习助手主窗口"""

    def __init__(self):
        super().__init__()

        # 窗口设置
        self.title(APP_NAME)
        self.geometry("920x720")
        self.resizable(False, False)

        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 设置窗口背景颜色
        self.configure(fg_color=COLORS["bg_dark"])

        # 窗口置顶
        self.attributes('-topmost', True)

        # 设置半透明效果 (Windows)
        try:
            self.attributes('-alpha', 0.92)
        except:
            pass

        # 初始化控制器
        self._init_controllers()

        # 创建界面
        self._create_widgets()

    def _init_controllers(self):
        """初始化控制器"""
        # 番茄钟控制器
        self.pomodoro_controller = PomodoroController(
            on_tick=self._on_pomodoro_tick,
            on_complete=self._on_pomodoro_complete,
            on_stats_update=self._update_stats_display
        )

        # 专注记录控制器
        self.focus_controller = FocusController(
            on_stats_update=self._update_stats_display
        )

    def _create_widgets(self):
        """创建所有控件"""
        # 主容器
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # 创建顶部标题栏
        self.header = HeaderComponent(
            self.main_container,
            on_opacity_change=self._change_opacity
        )
        self.header.pack(fill="x", padx=0, pady=0)

        # 创建内容区域（左右两栏）
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 左栏容器 - 学习管理 (410px)
        self.left_column = ctk.CTkFrame(self.content_frame, fg_color="transparent", width=410)
        self.left_column.pack(side="left", fill="both", padx=(0, 5))
        self.left_column.pack_propagate(False)

        # 右栏容器 - 背单词 (490px)
        self.right_column = ctk.CTkFrame(self.content_frame, fg_color="transparent", width=490)
        self.right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # 创建左栏内容
        self._create_left_panel()

        # 创建右栏内容
        self._create_right_panel()

        # 初始化数据显示
        self._update_stats_display()

    def _create_left_panel(self):
        """创建左栏 - 学习管理面板"""
        # 今日统计卡片
        self.stats_card = StatsCard(
            self.left_column,
            on_detail_click=self._show_stats_dialog
        )
        self.stats_card.pack(fill="x", padx=5, pady=5)

        # 番茄钟卡片
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

        # 待办列表
        self.todo_list = TodoList(
            self.left_column,
            on_stats_update=self._update_stats_display
        )
        self.todo_list.pack(fill="both", expand=True, padx=5, pady=5)

        # 底部专注记录按钮
        self._create_focus_tracker()

    def _create_focus_tracker(self):
        """创建专注记录区域"""
        self.bottom_frame = ctk.CTkFrame(self.left_column, fg_color=COLORS["bg_card"], corner_radius=10)
        self.bottom_frame.pack(fill="x", padx=5, pady=5)

        # 科目选择
        self.track_subject_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.track_subject_frame.pack(fill="x", padx=15, pady=(8, 5))

        ctk.CTkLabel(
            self.track_subject_frame,
            text="记录科目：",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")

        subjects = SubjectModel.load_subjects()
        self.track_subject_var = ctk.StringVar(value="其他")
        self.track_subject_menu = ctk.CTkOptionMenu(
            self.track_subject_frame,
            values=subjects,
            variable=self.track_subject_var,
            width=90,
            height=24,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["accent_green"],
            button_hover_color=COLORS["accent_blue"]
        )
        self.track_subject_menu.pack(side="left", padx=5)

        self.focus_track_btn = ctk.CTkButton(
            self.bottom_frame,
            text="⏱ 开始记录学习时长",
            height=32,
            fg_color=COLORS["accent_green"],
            hover_color="#2ea043",
            text_color="#000000",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._toggle_focus_tracking
        )
        self.focus_track_btn.pack(fill="x", padx=15, pady=(5, 8))

    def _create_right_panel(self):
        """创建右栏 - 背单词面板"""
        self.word_card = WordCard(
            self.right_column,
            on_wordbook_click=self._show_wordbook_dialog,
            on_stats_click=self._show_word_stats_dialog,
            on_settings_click=self._show_word_settings_dialog
        )
        self.word_card.pack(fill="both", expand=True)

    # ==================== 事件处理方法 ====================

    def _change_opacity(self, value):
        """调节窗口透明度

        Args:
            value: 透明度值 (0.3-1.0)
        """
        try:
            self.attributes('-alpha', value)
        except:
            pass

    def _update_stats_display(self):
        """更新统计显示"""
        stats = RecordModel.get_today_stats()
        self.stats_card.update_stats(
            stats['focus_time'],
            stats['completed_tasks'],
            stats['pomodoros']
        )

    # ===== 番茄钟相关 =====

    def _toggle_pomodoro(self):
        """开始/暂停番茄钟"""
        if not self.pomodoro_controller.running:
            subject = self.pomodoro_card.get_current_subject()
            self.pomodoro_controller.start(subject)
            self.pomodoro_card.update_start_button(True)
            self._update_pomodoro_status()
        else:
            self.pomodoro_controller.pause()
            self.pomodoro_card.update_start_button(False)
            self.pomodoro_card.update_status("已暂停", COLORS["text_secondary"])

    def _reset_pomodoro(self):
        """重置番茄钟"""
        self.pomodoro_controller.reset()
        self.pomodoro_card.update_timer(PomodoroController.format_time(DEFAULT_FOCUS_TIME * 60))
        self.pomodoro_card.update_start_button(False)
        self.pomodoro_card.update_status("准备开始专注", COLORS["text_secondary"])
        self.pomodoro_card.timer_label.configure(text_color=COLORS["accent_blue"])

    def _on_pomodoro_tick(self, remaining_seconds):
        """番茄钟每秒回调

        Args:
            remaining_seconds: 剩余秒数
        """
        self.after(0, lambda: self._update_pomodoro_timer(remaining_seconds))

    def _update_pomodoro_timer(self, remaining_seconds):
        """更新番茄钟计时器显示

        Args:
            remaining_seconds: 剩余秒数
        """
        time_str = PomodoroController.format_time(remaining_seconds)
        self.pomodoro_card.update_timer(time_str)
        self.pomodoro_card.update_timer_color(
            remaining_seconds,
            self.pomodoro_controller.is_focus_time
        )

    def _on_pomodoro_complete(self, was_focus_time):
        """番茄钟完成回调

        Args:
            was_focus_time: 是否是专注时间结束
        """
        self.after(0, lambda: self._handle_pomodoro_complete(was_focus_time))

    def _handle_pomodoro_complete(self, was_focus_time):
        """处理番茄钟完成

        Args:
            was_focus_time: 是否是专注时间结束
        """
        self.pomodoro_card.update_start_button(False)

        if was_focus_time:
            self.pomodoro_card.update_status("🎉 专注完成！休息一下吧", COLORS["accent_yellow"])
        else:
            self.pomodoro_card.update_status("☕ 休息结束！准备下一轮", COLORS["accent_blue"])

        time_str = PomodoroController.format_time(self.pomodoro_controller.remaining_seconds)
        self.pomodoro_card.update_timer(time_str)

    def _update_pomodoro_status(self):
        """更新番茄钟状态显示"""
        status = self.pomodoro_controller.status_text
        if self.pomodoro_controller.is_focus_time:
            color = COLORS["accent_green"]
        else:
            color = COLORS["accent_yellow"]
        self.pomodoro_card.update_status(status, color)

    def _on_subject_change(self, value):
        """科目选择变更

        Args:
            value: 选中的科目
        """
        self.pomodoro_controller.current_subject = value

    # ===== 专注记录相关 =====

    def _toggle_focus_tracking(self):
        """切换专注记录状态"""
        if not self.focus_controller.is_tracking:
            subject = self.track_subject_var.get()
            self.focus_controller.start(subject)
            self.focus_track_btn.configure(
                text=f"⏹ 停止记录 ({subject})",
                fg_color=COLORS["accent_red"],
                hover_color="#da3633"
            )
        else:
            self.focus_controller.stop()
            self.focus_track_btn.configure(
                text="⏱ 开始记录学习时长",
                fg_color=COLORS["accent_green"],
                hover_color="#2ea043"
            )

    # ===== 对话框相关 =====

    def _show_stats_dialog(self):
        """显示统计对话框"""
        StatsDialog(self)

    def _show_subject_dialog(self):
        """显示科目管理对话框"""
        SubjectDialog(self, on_close=self._on_subjects_updated)

    def _on_subjects_updated(self, subjects):
        """科目更新回调

        Args:
            subjects: 更新后的科目列表
        """
        self.pomodoro_card.update_subjects(subjects)
        self.track_subject_menu.configure(values=subjects)

    def _show_wordbook_dialog(self):
        """显示词库管理对话框"""
        WordbookDialog(self, on_words_imported=self.word_card.reload_words)

    def _show_word_stats_dialog(self):
        """显示单词统计对话框"""
        WordStatsDialog(self)

    def _show_word_settings_dialog(self):
        """显示单词设置对话框"""
        WordSettingsDialog(self, on_save=self.word_card._update_progress_display)
