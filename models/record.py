"""
学习记录管理模块
"""

from datetime import datetime, timedelta
from .base import BaseModel
from config import RECORDS_FILE


class RecordModel:
    """学习记录数据模型"""

    @staticmethod
    def load_records():
        """加载学习记录

        Returns:
            学习记录数据字典
        """
        return BaseModel.load_json(RECORDS_FILE, {"records": {}})

    @staticmethod
    def save_records(data):
        """保存学习记录

        Args:
            data: 学习记录数据字典
        """
        BaseModel.save_json(RECORDS_FILE, data)

    @staticmethod
    def _ensure_today_record(records):
        """确保今日记录存在

        Args:
            records: 记录数据字典

        Returns:
            今日日期字符串
        """
        today = BaseModel.get_today_str()
        if today not in records["records"]:
            records["records"][today] = {
                "total_time": 0,
                "completed_tasks": 0,
                "pomodoros": 0,
                "subjects": {}
            }
        return today

    @staticmethod
    def add_focus_time(minutes, subject="其他", add_pomodoro=True):
        """添加专注时间（分科目）

        Args:
            minutes: 专注时间（分钟）
            subject: 科目名称
            add_pomodoro: 是否增加番茄计数
        """
        records = RecordModel.load_records()
        today = RecordModel._ensure_today_record(records)

        records["records"][today]["total_time"] += minutes

        if add_pomodoro:
            records["records"][today]["pomodoros"] += 1

        if "subjects" not in records["records"][today]:
            records["records"][today]["subjects"] = {}

        if subject not in records["records"][today]["subjects"]:
            records["records"][today]["subjects"][subject] = 0
        records["records"][today]["subjects"][subject] += minutes

        RecordModel.save_records(records)

    @staticmethod
    def add_completed_task():
        """添加完成任务数"""
        records = RecordModel.load_records()
        today = RecordModel._ensure_today_record(records)
        records["records"][today]["completed_tasks"] += 1
        RecordModel.save_records(records)

    @staticmethod
    def remove_completed_task():
        """减少完成任务数"""
        records = RecordModel.load_records()
        today = BaseModel.get_today_str()
        if today in records["records"]:
            if records["records"][today]["completed_tasks"] > 0:
                records["records"][today]["completed_tasks"] -= 1
                RecordModel.save_records(records)

    @staticmethod
    def get_today_stats():
        """获取今日统计

        Returns:
            今日统计数据字典
        """
        records = RecordModel.load_records()
        today = BaseModel.get_today_str()
        if today in records["records"]:
            record = records["records"][today]
            return {
                "focus_time": record.get("total_time", 0),
                "completed_tasks": record.get("completed_tasks", 0),
                "pomodoros": record.get("pomodoros", 0),
                "subjects": record.get("subjects", {})
            }
        return {"focus_time": 0, "completed_tasks": 0, "pomodoros": 0, "subjects": {}}

    @staticmethod
    def get_history_stats(days=7):
        """获取历史统计数据

        Args:
            days: 获取多少天的数据

        Returns:
            历史统计数据列表
        """
        records = RecordModel.load_records()
        history = []

        for i in range(days - 1, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in records["records"]:
                record = records["records"][date]
                history.append({
                    "date": date,
                    "total_time": record.get("total_time", 0),
                    "subjects": record.get("subjects", {})
                })
            else:
                history.append({
                    "date": date,
                    "total_time": 0,
                    "subjects": {}
                })

        return history

    @staticmethod
    def get_week_stats():
        """获取本周统计

        Returns:
            本周统计数据字典
        """
        records = RecordModel.load_records()
        today = datetime.now()
        # 获取本周一
        monday = today - timedelta(days=today.weekday())

        total_time = 0
        total_tasks = 0
        total_pomodoros = 0
        subjects = {}
        daily_data = []

        for i in range(7):
            date = (monday + timedelta(days=i)).strftime("%Y-%m-%d")
            if date in records["records"]:
                record = records["records"][date]
                day_time = record.get("total_time", 0)
                total_time += day_time
                total_tasks += record.get("completed_tasks", 0)
                total_pomodoros += record.get("pomodoros", 0)

                for subj, mins in record.get("subjects", {}).items():
                    subjects[subj] = subjects.get(subj, 0) + mins

                daily_data.append({"date": date, "total_time": day_time})
            else:
                daily_data.append({"date": date, "total_time": 0})

        return {
            "total_time": total_time,
            "total_tasks": total_tasks,
            "total_pomodoros": total_pomodoros,
            "subjects": subjects,
            "daily_data": daily_data,
            "avg_time": total_time / 7 if total_time > 0 else 0
        }

    @staticmethod
    def get_month_stats():
        """获取本月统计

        Returns:
            本月统计数据字典
        """
        records = RecordModel.load_records()
        today = datetime.now()
        # 获取本月第一天
        first_day = today.replace(day=1)

        total_time = 0
        total_tasks = 0
        total_pomodoros = 0
        subjects = {}
        daily_data = []
        days_in_month = 0

        current = first_day
        while current.month == today.month and current <= today:
            date = current.strftime("%Y-%m-%d")
            days_in_month += 1

            if date in records["records"]:
                record = records["records"][date]
                day_time = record.get("total_time", 0)
                total_time += day_time
                total_tasks += record.get("completed_tasks", 0)
                total_pomodoros += record.get("pomodoros", 0)

                for subj, mins in record.get("subjects", {}).items():
                    subjects[subj] = subjects.get(subj, 0) + mins

                daily_data.append({"date": date, "total_time": day_time})
            else:
                daily_data.append({"date": date, "total_time": 0})

            current += timedelta(days=1)

        return {
            "total_time": total_time,
            "total_tasks": total_tasks,
            "total_pomodoros": total_pomodoros,
            "subjects": subjects,
            "daily_data": daily_data,
            "avg_time": total_time / days_in_month if days_in_month > 0 else 0,
            "days_count": days_in_month
        }
