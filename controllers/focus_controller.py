"""
专注记录控制器模块
"""

from datetime import datetime
from models import RecordModel


class FocusController:
    """专注记录控制器 - 管理手动专注时长记录"""

    def __init__(self, on_stats_update=None):
        """初始化专注记录控制器

        Args:
            on_stats_update: 统计更新回调函数
        """
        self.tracking = False
        self.start_time = None
        self.subject = "其他"
        self._on_stats_update = on_stats_update

    def start(self, subject="其他"):
        """开始记录专注时长

        Args:
            subject: 学习科目
        """
        self.tracking = True
        self.start_time = datetime.now()
        self.subject = subject

    def stop(self):
        """停止记录专注时长

        Returns:
            记录的分钟数
        """
        minutes = 0
        if self.tracking and self.start_time:
            # 计算专注时长
            duration = datetime.now() - self.start_time
            minutes = int(duration.total_seconds() / 60)
            if minutes > 0:
                RecordModel.add_focus_time(minutes, self.subject, add_pomodoro=False)
                if self._on_stats_update:
                    self._on_stats_update()

        self.tracking = False
        self.start_time = None
        return minutes

    @property
    def is_tracking(self):
        """是否正在记录"""
        return self.tracking
