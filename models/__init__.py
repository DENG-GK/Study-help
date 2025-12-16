"""
数据模型层
"""

from .base import BaseModel
from .subject import SubjectModel
from .todo import TodoModel
from .record import RecordModel
from .word import WordModel
from .math_model import MathModel

# 为了向后兼容，提供 DataManager 别名
class DataManager:
    """数据管理器 - 整合所有数据操作（向后兼容）"""

    # 基础操作
    load_json = staticmethod(BaseModel.load_json)
    save_json = staticmethod(BaseModel.save_json)
    get_today_str = staticmethod(BaseModel.get_today_str)

    # 科目管理
    load_subjects = staticmethod(SubjectModel.load_subjects)
    save_subjects = staticmethod(SubjectModel.save_subjects)
    add_subject = staticmethod(SubjectModel.add_subject)
    remove_subject = staticmethod(SubjectModel.remove_subject)

    # 待办事项
    load_todos = staticmethod(TodoModel.load_todos)
    save_todos = staticmethod(TodoModel.save_todos)

    # 学习记录
    load_records = staticmethod(RecordModel.load_records)
    save_records = staticmethod(RecordModel.save_records)
    add_focus_time = staticmethod(RecordModel.add_focus_time)
    add_completed_task = staticmethod(RecordModel.add_completed_task)
    remove_completed_task = staticmethod(RecordModel.remove_completed_task)
    get_today_stats = staticmethod(RecordModel.get_today_stats)
    get_history_stats = staticmethod(RecordModel.get_history_stats)

    # 单词管理
    load_words = staticmethod(WordModel.load_words)
    save_words = staticmethod(WordModel.save_words)
    load_word_settings = staticmethod(WordModel.load_word_settings)
    save_word_settings = staticmethod(WordModel.save_word_settings)
    load_word_stats = staticmethod(WordModel.load_word_stats)
    save_word_stats = staticmethod(WordModel.save_word_stats)
    get_today_words = staticmethod(WordModel.get_today_words)
    update_word_progress = staticmethod(WordModel.update_word_progress)
    toggle_star_word = staticmethod(WordModel.toggle_star_word)
    add_word_manually = staticmethod(WordModel.add_word_manually)
    import_words_from_file = staticmethod(WordModel.import_words_from_file)

    # 数学模块
    load_math_questions = staticmethod(MathModel.load_questions)
    save_math_questions = staticmethod(MathModel.save_questions)
    load_math_mistakes = staticmethod(MathModel.load_mistakes)
    save_math_mistakes = staticmethod(MathModel.save_mistakes)
    load_math_progress = staticmethod(MathModel.load_progress)
    save_math_progress = staticmethod(MathModel.save_progress)
    load_math_settings = staticmethod(MathModel.load_settings)
    save_math_settings = staticmethod(MathModel.save_settings)
    load_math_formulas = staticmethod(MathModel.load_formulas)
    get_daily_math_questions = staticmethod(MathModel.get_daily_questions)

__all__ = [
    'BaseModel', 'SubjectModel', 'TodoModel', 'RecordModel', 'WordModel', 'MathModel',
    'DataManager'
]
