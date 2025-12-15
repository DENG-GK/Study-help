"""
科目管理模块
"""

from .base import BaseModel
from config import SUBJECTS_FILE, DEFAULT_SUBJECTS


class SubjectModel:
    """科目数据模型"""

    @staticmethod
    def load_subjects():
        """加载科目列表

        Returns:
            科目列表
        """
        data = BaseModel.load_json(SUBJECTS_FILE, {"subjects": DEFAULT_SUBJECTS})
        if not data.get("subjects"):
            data["subjects"] = DEFAULT_SUBJECTS
            SubjectModel.save_subjects(data["subjects"])
        return data["subjects"]

    @staticmethod
    def save_subjects(subjects):
        """保存科目列表

        Args:
            subjects: 科目列表
        """
        BaseModel.save_json(SUBJECTS_FILE, {"subjects": subjects})

    @staticmethod
    def add_subject(name):
        """添加科目

        Args:
            name: 科目名称

        Returns:
            更新后的科目列表
        """
        subjects = SubjectModel.load_subjects()
        if name and name not in subjects:
            subjects.append(name)
            SubjectModel.save_subjects(subjects)
        return subjects

    @staticmethod
    def remove_subject(name):
        """删除科目

        Args:
            name: 科目名称

        Returns:
            更新后的科目列表
        """
        subjects = SubjectModel.load_subjects()
        if name in subjects and name != "其他":
            subjects.remove(name)
            SubjectModel.save_subjects(subjects)
        return subjects
