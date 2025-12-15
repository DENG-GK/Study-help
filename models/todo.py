"""
待办事项管理模块
"""

from .base import BaseModel
from config import TODOS_FILE


class TodoModel:
    """待办事项数据模型"""

    @staticmethod
    def load_todos():
        """加载待办事项

        Returns:
            待办事项数据字典
        """
        return BaseModel.load_json(TODOS_FILE, {"todos": []})

    @staticmethod
    def save_todos(data):
        """保存待办事项

        Args:
            data: 待办事项数据字典
        """
        BaseModel.save_json(TODOS_FILE, data)
