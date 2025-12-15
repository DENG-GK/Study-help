"""
任务提醒控制器模块
"""

import threading
from datetime import datetime, timedelta
from models import TodoModel


class ReminderController:
    """任务提醒控制器 - 管理定时提醒"""

    def __init__(self, on_reminder=None):
        """初始化提醒控制器

        Args:
            on_reminder: 提醒触发时的回调函数，接收 (todo_text, reminder_time) 参数
        """
        self._on_reminder = on_reminder
        self._timers = {}  # {todo_id: timer}
        self._running = False

    def start(self):
        """启动提醒服务"""
        self._running = True
        self._check_reminders()

    def stop(self):
        """停止提醒服务"""
        self._running = False
        # 取消所有定时器
        for timer in self._timers.values():
            timer.cancel()
        self._timers.clear()

    def _check_reminders(self):
        """检查并设置提醒"""
        if not self._running:
            return

        data = TodoModel.load_todos()
        now = datetime.now()

        for todo in data.get("todos", []):
            if todo.get("completed"):
                continue

            reminder_time = todo.get("reminder_time")
            if not reminder_time:
                continue

            todo_id = todo.get("id")

            # 如果已经有定时器，跳过
            if todo_id in self._timers:
                continue

            try:
                reminder_dt = datetime.fromisoformat(reminder_time)
                delay = (reminder_dt - now).total_seconds()

                if delay > 0:
                    # 设置定时器
                    timer = threading.Timer(
                        delay,
                        self._trigger_reminder,
                        args=[todo_id, todo.get("text", ""), reminder_time]
                    )
                    timer.daemon = True
                    timer.start()
                    self._timers[todo_id] = timer
                elif delay > -60:  # 1分钟内的过期提醒也触发
                    self._trigger_reminder(todo_id, todo.get("text", ""), reminder_time)
            except (ValueError, TypeError):
                pass

        # 每分钟检查一次新提醒
        if self._running:
            check_timer = threading.Timer(60, self._check_reminders)
            check_timer.daemon = True
            check_timer.start()

    def _trigger_reminder(self, todo_id, text, reminder_time):
        """触发提醒

        Args:
            todo_id: 待办ID
            text: 待办文本
            reminder_time: 提醒时间
        """
        # 移除已触发的定时器
        if todo_id in self._timers:
            del self._timers[todo_id]

        # 清除待办中的提醒时间（已提醒）
        self._clear_reminder(todo_id)

        if self._on_reminder:
            self._on_reminder(text, reminder_time)

    def _clear_reminder(self, todo_id):
        """清除待办的提醒时间

        Args:
            todo_id: 待办ID
        """
        data = TodoModel.load_todos()
        for todo in data.get("todos", []):
            if todo.get("id") == todo_id:
                todo["reminder_time"] = None
                break
        TodoModel.save_todos(data)

    def set_reminder(self, todo_id, reminder_time):
        """设置提醒

        Args:
            todo_id: 待办ID
            reminder_time: 提醒时间（datetime 或 ISO格式字符串）
        """
        data = TodoModel.load_todos()

        if isinstance(reminder_time, datetime):
            reminder_str = reminder_time.isoformat()
        else:
            reminder_str = reminder_time

        for todo in data.get("todos", []):
            if todo.get("id") == todo_id:
                todo["reminder_time"] = reminder_str
                break

        TodoModel.save_todos(data)

        # 重新检查提醒
        if self._running:
            # 取消旧的定时器
            if todo_id in self._timers:
                self._timers[todo_id].cancel()
                del self._timers[todo_id]
            # 添加新定时器
            self._check_reminders()

    def cancel_reminder(self, todo_id):
        """取消提醒

        Args:
            todo_id: 待办ID
        """
        # 取消定时器
        if todo_id in self._timers:
            self._timers[todo_id].cancel()
            del self._timers[todo_id]

        # 清除数据
        self._clear_reminder(todo_id)

    @staticmethod
    def get_quick_reminder_options():
        """获取快捷提醒选项

        Returns:
            [(显示文本, timedelta), ...]
        """
        return [
            ("5分钟后", timedelta(minutes=5)),
            ("15分钟后", timedelta(minutes=15)),
            ("30分钟后", timedelta(minutes=30)),
            ("1小时后", timedelta(hours=1)),
            ("2小时后", timedelta(hours=2)),
            ("明天此时", timedelta(days=1)),
        ]
