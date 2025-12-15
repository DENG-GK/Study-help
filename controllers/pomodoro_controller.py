"""
番茄钟控制器模块
"""

import time
import winsound
from threading import Thread
from models import RecordModel
from config import DEFAULT_FOCUS_TIME, DEFAULT_BREAK_TIME


class PomodoroController:
    """番茄钟控制器 - 管理番茄钟状态和计时逻辑"""

    def __init__(self, on_tick=None, on_complete=None, on_stats_update=None):
        """初始化番茄钟控制器

        Args:
            on_tick: 每秒回调函数，参数为剩余秒数
            on_complete: 完成回调函数，参数为是否是专注时间
            on_stats_update: 统计更新回调函数
        """
        self.running = False
        self.paused = False
        self.is_focus_time = True
        self.remaining_seconds = DEFAULT_FOCUS_TIME * 60
        self.current_subject = "其他"
        self.recorded_minutes = 0  # 已记录的专注分钟数（用于实时记录）

        self._thread = None
        self._on_tick = on_tick
        self._on_complete = on_complete
        self._on_stats_update = on_stats_update

    @property
    def status_text(self):
        """获取当前状态文本"""
        if not self.running and not self.paused:
            return "准备开始专注"
        elif self.paused:
            return "已暂停"
        elif self.is_focus_time:
            return f"🔥 专注中 - {self.current_subject}"
        else:
            return "☕ 休息中..."

    def start(self, subject="其他"):
        """开始番茄钟

        Args:
            subject: 当前学习科目
        """
        self.running = True
        self.paused = False
        self.current_subject = subject

        # 如果是新开始（不是继续），重置已记录分钟数
        if self.remaining_seconds == DEFAULT_FOCUS_TIME * 60:
            self.recorded_minutes = 0

        self._thread = Thread(target=self._countdown, daemon=True)
        self._thread.start()

    def pause(self):
        """暂停番茄钟"""
        self.paused = True
        self.running = False

    def resume(self):
        """继续番茄钟"""
        self.start(self.current_subject)

    def reset(self):
        """重置番茄钟"""
        self.running = False
        self.paused = False
        self.is_focus_time = True
        self.remaining_seconds = DEFAULT_FOCUS_TIME * 60
        self.recorded_minutes = 0

    def _countdown(self):
        """倒计时线程"""
        while self.remaining_seconds > 0 and self.running:
            time.sleep(1)
            if self.running:
                self.remaining_seconds -= 1

                if self._on_tick:
                    self._on_tick(self.remaining_seconds)

                # 实时记录专注时长：每过1分钟记录一次（仅在专注时间）
                if self.is_focus_time:
                    elapsed_minutes = (DEFAULT_FOCUS_TIME * 60 - self.remaining_seconds) // 60
                    if elapsed_minutes > self.recorded_minutes:
                        # 新增了1分钟，记录它（不增加番茄数）
                        RecordModel.add_focus_time(1, self.current_subject, add_pomodoro=False)
                        self.recorded_minutes = elapsed_minutes
                        if self._on_stats_update:
                            self._on_stats_update()

        if self.remaining_seconds <= 0 and self.running:
            self._on_countdown_complete()

    def _on_countdown_complete(self):
        """倒计时完成处理"""
        self.running = False

        # 播放提示音
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except:
            pass

        was_focus_time = self.is_focus_time

        if self.is_focus_time:
            # 专注结束，只增加番茄数（时间已经实时记录了）
            self._add_pomodoro_count()

            # 重置已记录分钟数，准备下一轮
            self.recorded_minutes = 0

            # 切换到休息
            self.is_focus_time = False
            self.remaining_seconds = DEFAULT_BREAK_TIME * 60
        else:
            # 休息结束，切换到专注
            self.is_focus_time = True
            self.remaining_seconds = DEFAULT_FOCUS_TIME * 60
            self.recorded_minutes = 0

        if self._on_complete:
            self._on_complete(was_focus_time)

        if self._on_stats_update:
            self._on_stats_update()

    def _add_pomodoro_count(self):
        """仅增加番茄计数（不增加时间）"""
        records = RecordModel.load_records()
        today = RecordModel._ensure_today_record(records)
        records["records"][today]["pomodoros"] += 1
        RecordModel.save_records(records)

    @staticmethod
    def format_time(seconds):
        """格式化时间显示

        Args:
            seconds: 秒数

        Returns:
            格式化的时间字符串 'MM:SS'
        """
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
