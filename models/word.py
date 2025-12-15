"""
单词管理模块
"""

import time
import csv
from datetime import datetime, timedelta
from .base import BaseModel
from config import (
    WORDS_FILE, WORD_SETTINGS_FILE, WORD_STATS_FILE,
    DEFAULT_WORD_SETTINGS, REVIEW_INTERVALS
)


class WordModel:
    """单词数据模型"""

    @staticmethod
    def load_words():
        """加载单词库

        Returns:
            单词库数据字典
        """
        return BaseModel.load_json(WORDS_FILE, {"words": []})

    @staticmethod
    def save_words(data):
        """保存单词库

        Args:
            data: 单词库数据字典
        """
        BaseModel.save_json(WORDS_FILE, data)

    @staticmethod
    def load_word_settings():
        """加载单词学习设置

        Returns:
            设置数据字典
        """
        return BaseModel.load_json(WORD_SETTINGS_FILE, DEFAULT_WORD_SETTINGS)

    @staticmethod
    def save_word_settings(settings):
        """保存单词学习设置

        Args:
            settings: 设置数据字典
        """
        BaseModel.save_json(WORD_SETTINGS_FILE, settings)

    @staticmethod
    def load_word_stats():
        """加载单词学习统计

        Returns:
            统计数据字典
        """
        return BaseModel.load_json(WORD_STATS_FILE, {"records": {}})

    @staticmethod
    def save_word_stats(data):
        """保存单词学习统计

        Args:
            data: 统计数据字典
        """
        BaseModel.save_json(WORD_STATS_FILE, data)

    @staticmethod
    def get_today_words():
        """获取今日学习单词（新学+复习）

        Returns:
            今日学习单词列表
        """
        data = WordModel.load_words()
        settings = WordModel.load_word_settings()
        today = BaseModel.get_today_str()

        words = data.get("words", [])
        if not words:
            return []

        # 分类：需要复习的 和 新单词
        review_words = []
        new_words = []

        for word in words:
            next_review = word.get("next_review", "")
            if next_review and next_review <= today:
                review_words.append(word)
            elif word.get("level", 0) == 0:
                new_words.append(word)

        # 按设置限制数量
        daily_new = settings.get("daily_new_words", 30)
        daily_review = settings.get("daily_review_words", 50)

        result = review_words[:daily_review] + new_words[:daily_new]
        return result

    @staticmethod
    def update_word_progress(word_id, is_correct):
        """更新单词学习进度

        Args:
            word_id: 单词ID
            is_correct: 是否回答正确
        """
        data = WordModel.load_words()
        today = BaseModel.get_today_str()

        for word in data.get("words", []):
            if word.get("id") == word_id:
                level = word.get("level", 0)

                # 计算新等级
                if is_correct:
                    new_level = min(level + 1, 5)
                else:
                    new_level = max(level - 1, 0)

                word["level"] = new_level
                word["review_count"] = word.get("review_count", 0) + 1

                if is_correct:
                    word["correct_count"] = word.get("correct_count", 0) + 1

                # 计算下次复习时间
                if new_level >= len(REVIEW_INTERVALS):
                    days = 30
                else:
                    days = REVIEW_INTERVALS[new_level]

                next_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                word["next_review"] = next_date
                break

        WordModel.save_words(data)

        # 更新今日统计
        stats = WordModel.load_word_stats()
        if today not in stats["records"]:
            stats["records"][today] = {
                "new_learned": 0,
                "reviewed": 0,
                "correct": 0,
                "wrong": 0,
                "starred": 0
            }

        stats["records"][today]["reviewed"] += 1
        if is_correct:
            stats["records"][today]["correct"] += 1
        else:
            stats["records"][today]["wrong"] += 1

        WordModel.save_word_stats(stats)

    @staticmethod
    def toggle_star_word(word_id):
        """收藏/取消收藏单词

        Args:
            word_id: 单词ID
        """
        data = WordModel.load_words()

        for word in data.get("words", []):
            if word.get("id") == word_id:
                word["starred"] = not word.get("starred", False)
                break

        WordModel.save_words(data)

    @staticmethod
    def add_word_manually(word, phonetic="", meaning="", example="", example_cn=""):
        """手动添加单词

        Args:
            word: 单词
            phonetic: 音标
            meaning: 释义
            example: 例句
            example_cn: 例句翻译

        Returns:
            新添加的单词数据
        """
        data = WordModel.load_words()
        today = BaseModel.get_today_str()

        new_word = {
            "id": int(time.time() * 1000),
            "word": word,
            "phonetic": phonetic,
            "meaning": meaning,
            "example": example,
            "example_cn": example_cn,
            "level": 0,
            "next_review": today,
            "review_count": 0,
            "correct_count": 0,
            "starred": False,
            "source": "manual"
        }

        data["words"].append(new_word)
        WordModel.save_words(data)
        return new_word

    @staticmethod
    def import_words_from_file(filepath, file_type="txt"):
        """从文件导入单词

        Args:
            filepath: 文件路径
            file_type: 文件类型 ('txt' 或 'csv')

        Returns:
            导入的单词数量
        """
        data = WordModel.load_words()
        today = BaseModel.get_today_str()
        count = 0

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if file_type == "csv":
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) >= 2:
                            word = row[0].strip()
                            meaning = row[1].strip()
                            phonetic = row[2].strip() if len(row) > 2 else ""
                            example = row[3].strip() if len(row) > 3 else ""

                            if word and meaning:
                                new_word = {
                                    "id": int(time.time() * 1000) + count,
                                    "word": word,
                                    "phonetic": phonetic,
                                    "meaning": meaning,
                                    "example": example,
                                    "example_cn": "",
                                    "level": 0,
                                    "next_review": today,
                                    "review_count": 0,
                                    "correct_count": 0,
                                    "starred": False,
                                    "source": "import"
                                }
                                data["words"].append(new_word)
                                count += 1
                else:  # txt 格式：每行 "单词 释义" 或 "单词\t释义"
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        # 尝试不同的分隔符
                        parts = None
                        for sep in ['\t', '  ', ' ']:
                            if sep in line:
                                parts = line.split(sep, 1)
                                break

                        if parts and len(parts) >= 2:
                            word = parts[0].strip()
                            meaning = parts[1].strip()

                            if word and meaning:
                                new_word = {
                                    "id": int(time.time() * 1000) + count,
                                    "word": word,
                                    "phonetic": "",
                                    "meaning": meaning,
                                    "example": "",
                                    "example_cn": "",
                                    "level": 0,
                                    "next_review": today,
                                    "review_count": 0,
                                    "correct_count": 0,
                                    "starred": False,
                                    "source": "import"
                                }
                                data["words"].append(new_word)
                                count += 1

            WordModel.save_words(data)
        except Exception as e:
            print(f"导入失败: {e}")

        return count
