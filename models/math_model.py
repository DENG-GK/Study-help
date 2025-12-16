"""
数学学习模块数据模型
"""

import time
import random
from datetime import datetime, timedelta
from .base import BaseModel
from config import (
    MATH_QUESTIONS_FILE, MATH_MISTAKES_FILE, MATH_PROGRESS_FILE,
    MATH_SETTINGS_FILE, MATH_FORMULAS_FILE,
    DEFAULT_MATH_SETTINGS, MATH_REVIEW_INTERVALS, MATH_CHAPTERS
)


class MathModel:
    """数学数据模型"""

    # ==================== 题库操作 ====================
    @staticmethod
    def load_questions():
        """加载题库

        Returns:
            题库数据字典
        """
        return BaseModel.load_json(MATH_QUESTIONS_FILE, {"questions": []})

    @staticmethod
    def save_questions(data):
        """保存题库

        Args:
            data: 题库数据字典
        """
        BaseModel.save_json(MATH_QUESTIONS_FILE, data)

    @staticmethod
    def get_question_by_id(question_id):
        """根据ID获取题目

        Args:
            question_id: 题目ID

        Returns:
            题目数据或None
        """
        data = MathModel.load_questions()
        for q in data.get("questions", []):
            if q.get("id") == question_id:
                return q
        return None

    @staticmethod
    def get_questions_by_chapter(chapter, section=None):
        """按章节获取题目

        Args:
            chapter: 章节名称（如"高等数学"）
            section: 小节名称（如"极限"），可选

        Returns:
            题目列表
        """
        data = MathModel.load_questions()
        questions = data.get("questions", [])

        result = [q for q in questions if q.get("chapter") == chapter]
        if section:
            result = [q for q in result if q.get("section") == section]

        return result

    @staticmethod
    def get_questions_by_difficulty(difficulty):
        """按难度获取题目

        Args:
            difficulty: 难度等级 (1-5)

        Returns:
            题目列表
        """
        data = MathModel.load_questions()
        return [q for q in data.get("questions", []) if q.get("difficulty") == difficulty]

    # ==================== 错题本操作 ====================
    @staticmethod
    def load_mistakes():
        """加载错题本

        Returns:
            错题数据字典
        """
        return BaseModel.load_json(MATH_MISTAKES_FILE, {"mistakes": []})

    @staticmethod
    def save_mistakes(data):
        """保存错题本

        Args:
            data: 错题数据字典
        """
        BaseModel.save_json(MATH_MISTAKES_FILE, data)

    @staticmethod
    def add_mistake(question_id, notes=""):
        """添加错题

        Args:
            question_id: 题目ID
            notes: 笔记

        Returns:
            是否成功添加（若已存在则更新）
        """
        data = MathModel.load_mistakes()
        today = BaseModel.get_today_str()

        # 检查是否已存在
        for mistake in data.get("mistakes", []):
            if mistake.get("question_id") == question_id:
                # 已存在，更新错误次数
                mistake["wrong_count"] = mistake.get("wrong_count", 1) + 1
                mistake["last_wrong"] = today
                if notes:
                    mistake["notes"] = notes
                MathModel.save_mistakes(data)
                return False  # 表示更新而非新增

        # 新增错题
        new_mistake = {
            "id": f"m{int(time.time() * 1000)}",
            "question_id": question_id,
            "wrong_date": today,
            "wrong_count": 1,
            "last_wrong": today,
            "last_review": None,
            "next_review": today,  # 立即可复习
            "level": 0,
            "mastered": False,
            "notes": notes
        }
        data["mistakes"].append(new_mistake)
        MathModel.save_mistakes(data)
        return True

    @staticmethod
    def add_image_mistake(image_path, chapter="其他", section="其他", notes="", difficulty=1, answer_image_path=None):
        """添加图片类型的错题

        Args:
            image_path: 错题图片路径
            chapter: 章节
            section: 小节
            notes: 笔记
            difficulty: 难度 (1-5)
            answer_image_path: 答案图片路径（可选）

        Returns:
            新错题的ID
        """
        import shutil
        import os
        from config import DATA_DIR

        data = MathModel.load_mistakes()
        today = BaseModel.get_today_str()

        # 创建错题图片目录
        mistake_images_dir = os.path.join(DATA_DIR, "mistake_images")
        os.makedirs(mistake_images_dir, exist_ok=True)

        # 生成唯一ID
        mistake_id = f"img_m{int(time.time() * 1000)}"

        # 复制错题图片到数据目录
        ext = os.path.splitext(image_path)[1]
        new_image_name = f"{mistake_id}_question{ext}"
        new_image_path = os.path.join(mistake_images_dir, new_image_name)
        shutil.copy2(image_path, new_image_path)

        # 复制答案图片（如果有）
        new_answer_path = None
        if answer_image_path:
            answer_ext = os.path.splitext(answer_image_path)[1]
            new_answer_name = f"{mistake_id}_answer{answer_ext}"
            new_answer_path = os.path.join(mistake_images_dir, new_answer_name)
            shutil.copy2(answer_image_path, new_answer_path)

        # 新增图片错题
        new_mistake = {
            "id": mistake_id,
            "question_id": None,  # 图片错题没有题库关联
            "type": "image",  # 标记为图片类型
            "image_path": new_image_path,
            "answer_image_path": new_answer_path,  # 答案图片路径
            "chapter": chapter,
            "section": section,
            "difficulty": difficulty,
            "wrong_date": today,
            "wrong_count": 1,
            "last_wrong": today,
            "last_review": None,
            "next_review": today,
            "level": 0,
            "mastered": False,
            "notes": notes
        }
        data["mistakes"].append(new_mistake)
        MathModel.save_mistakes(data)
        return mistake_id

    @staticmethod
    def get_all_mistakes():
        """获取所有错题（包括图片类型）

        Returns:
            所有错题列表（包含题目数据或图片信息）
        """
        data = MathModel.load_mistakes()
        result = []

        for mistake in data.get("mistakes", []):
            if mistake.get("type") == "image":
                # 图片类型错题
                result.append({
                    "mistake": mistake,
                    "question": {
                        "id": mistake.get("id"),
                        "type": "image",
                        "image_path": mistake.get("image_path"),
                        "answer_image_path": mistake.get("answer_image_path"),
                        "chapter": mistake.get("chapter", "其他"),
                        "section": mistake.get("section", "其他"),
                        "difficulty": mistake.get("difficulty", 1),
                        "question": "[图片错题]",
                        "options": [],
                        "answer": "",
                        "solution": mistake.get("notes", "")
                    }
                })
            else:
                # 普通题库错题
                question = MathModel.get_question_by_id(mistake.get("question_id"))
                if question:
                    result.append({
                        "mistake": mistake,
                        "question": question
                    })

        return result

    @staticmethod
    def remove_mistake(question_id):
        """移除错题

        Args:
            question_id: 题目ID
        """
        data = MathModel.load_mistakes()
        data["mistakes"] = [m for m in data.get("mistakes", [])
                           if m.get("question_id") != question_id]
        MathModel.save_mistakes(data)

    @staticmethod
    def mark_mistake_mastered(question_id, mastered=True):
        """标记错题为已掌握

        Args:
            question_id: 题目ID
            mastered: 是否已掌握
        """
        data = MathModel.load_mistakes()
        for mistake in data.get("mistakes", []):
            if mistake.get("question_id") == question_id:
                mistake["mastered"] = mastered
                break
        MathModel.save_mistakes(data)

    @staticmethod
    def update_mistake_review(question_id, is_correct):
        """更新错题复习进度

        Args:
            question_id: 题目ID
            is_correct: 是否回答正确
        """
        data = MathModel.load_mistakes()
        today = BaseModel.get_today_str()

        for mistake in data.get("mistakes", []):
            if mistake.get("question_id") == question_id:
                level = mistake.get("level", 0)

                if is_correct:
                    new_level = min(level + 1, len(MATH_REVIEW_INTERVALS) - 1)
                    # 如果达到最高等级，标记为已掌握
                    if new_level >= len(MATH_REVIEW_INTERVALS) - 1:
                        mistake["mastered"] = True
                else:
                    new_level = max(level - 1, 0)
                    mistake["wrong_count"] = mistake.get("wrong_count", 1) + 1
                    mistake["last_wrong"] = today

                mistake["level"] = new_level
                mistake["last_review"] = today

                # 计算下次复习时间
                days = MATH_REVIEW_INTERVALS[new_level]
                next_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                mistake["next_review"] = next_date
                break

        MathModel.save_mistakes(data)

    @staticmethod
    def get_review_mistakes():
        """获取需要复习的错题

        Returns:
            需要复习的错题列表（包含题目数据）
        """
        data = MathModel.load_mistakes()
        today = BaseModel.get_today_str()

        result = []
        for mistake in data.get("mistakes", []):
            if mistake.get("mastered"):
                continue
            next_review = mistake.get("next_review", "")
            if next_review and next_review <= today:
                # 获取对应的题目
                question = MathModel.get_question_by_id(mistake.get("question_id"))
                if question:
                    result.append({
                        "mistake": mistake,
                        "question": question
                    })

        return result

    # ==================== 知识点进度操作 ====================
    @staticmethod
    def load_progress():
        """加载知识点进度

        Returns:
            进度数据字典
        """
        default_progress = {"chapters": {}}
        # 初始化默认章节结构
        for chapter, sections in MATH_CHAPTERS.items():
            default_progress["chapters"][chapter] = {}
            for section in sections:
                default_progress["chapters"][chapter][section] = {
                    "total": 0,
                    "done": 0,
                    "correct": 0
                }

        return BaseModel.load_json(MATH_PROGRESS_FILE, default_progress)

    @staticmethod
    def save_progress(data):
        """保存知识点进度

        Args:
            data: 进度数据字典
        """
        BaseModel.save_json(MATH_PROGRESS_FILE, data)

    @staticmethod
    def update_progress(chapter, section, is_correct):
        """更新知识点进度

        Args:
            chapter: 章节名称
            section: 小节名称
            is_correct: 是否回答正确
        """
        data = MathModel.load_progress()

        if chapter not in data["chapters"]:
            data["chapters"][chapter] = {}
        if section not in data["chapters"][chapter]:
            data["chapters"][chapter][section] = {"total": 0, "done": 0, "correct": 0}

        data["chapters"][chapter][section]["done"] += 1
        if is_correct:
            data["chapters"][chapter][section]["correct"] += 1

        MathModel.save_progress(data)

    @staticmethod
    def get_chapter_progress(chapter):
        """获取章节进度

        Args:
            chapter: 章节名称

        Returns:
            章节进度数据
        """
        data = MathModel.load_progress()
        return data.get("chapters", {}).get(chapter, {})

    @staticmethod
    def get_overall_progress():
        """获取整体进度统计

        Returns:
            整体进度统计
        """
        data = MathModel.load_progress()
        total_done = 0
        total_correct = 0

        for chapter_data in data.get("chapters", {}).values():
            for section_data in chapter_data.values():
                total_done += section_data.get("done", 0)
                total_correct += section_data.get("correct", 0)

        return {
            "total_done": total_done,
            "total_correct": total_correct,
            "accuracy": round(total_correct / total_done * 100, 1) if total_done > 0 else 0
        }

    # ==================== 设置操作 ====================
    @staticmethod
    def load_settings():
        """加载数学学习设置

        Returns:
            设置数据字典
        """
        return BaseModel.load_json(MATH_SETTINGS_FILE, DEFAULT_MATH_SETTINGS.copy())

    @staticmethod
    def save_settings(settings):
        """保存数学学习设置

        Args:
            settings: 设置数据字典
        """
        BaseModel.save_json(MATH_SETTINGS_FILE, settings)

    # ==================== 公式速查操作 ====================
    @staticmethod
    def load_formulas():
        """加载公式库

        Returns:
            公式数据字典
        """
        return BaseModel.load_json(MATH_FORMULAS_FILE, {"formulas": {}})

    @staticmethod
    def save_formulas(data):
        """保存公式库

        Args:
            data: 公式数据字典
        """
        BaseModel.save_json(MATH_FORMULAS_FILE, data)

    @staticmethod
    def get_formulas_by_category(category):
        """按分类获取公式

        Args:
            category: 分类名称

        Returns:
            公式列表
        """
        data = MathModel.load_formulas()
        return data.get("formulas", {}).get(category, [])

    # ==================== 每日刷题逻辑 ====================
    @staticmethod
    def get_daily_questions():
        """获取每日刷题题目

        Returns:
            今日题目列表
        """
        settings = MathModel.load_settings()
        daily_count = settings.get("daily_count", 3)
        difficulty_mode = settings.get("difficulty_mode", "progressive")
        include_mistakes = settings.get("include_mistakes", True)
        mistake_ratio = settings.get("mistake_ratio", 0.3)

        result = []

        # 如果包含错题
        if include_mistakes:
            review_mistakes = MathModel.get_review_mistakes()
            mistake_count = max(1, int(daily_count * mistake_ratio))
            if review_mistakes:
                random.shuffle(review_mistakes)
                for item in review_mistakes[:mistake_count]:
                    q = item["question"].copy()
                    q["from_mistakes"] = True
                    result.append(q)

        # 补充题库中的题目
        remaining = daily_count - len(result)
        if remaining > 0:
            data = MathModel.load_questions()
            questions = data.get("questions", [])

            if difficulty_mode == "progressive":
                # 递进难度：先易后难
                sorted_questions = sorted(questions, key=lambda x: x.get("difficulty", 1))
            elif difficulty_mode == "random":
                # 随机
                sorted_questions = questions.copy()
                random.shuffle(sorted_questions)
            else:
                # 固定（按顺序）
                sorted_questions = questions

            # 排除已在结果中的题目
            result_ids = {q.get("id") for q in result}
            available = [q for q in sorted_questions if q.get("id") not in result_ids]

            for q in available[:remaining]:
                result.append(q)

        return result

    @staticmethod
    def record_answer(question_id, is_correct, chapter=None, section=None):
        """记录答题结果

        Args:
            question_id: 题目ID
            is_correct: 是否正确
            chapter: 章节（可选，用于更新进度）
            section: 小节（可选，用于更新进度）
        """
        settings = MathModel.load_settings()

        # 如果答错且设置了自动加入错题本
        if not is_correct and settings.get("auto_add_mistake", False):
            MathModel.add_mistake(question_id)

        # 更新知识点进度
        if chapter and section:
            MathModel.update_progress(chapter, section, is_correct)

        # 如果是错题复习，更新错题状态
        data = MathModel.load_mistakes()
        for mistake in data.get("mistakes", []):
            if mistake.get("question_id") == question_id:
                MathModel.update_mistake_review(question_id, is_correct)
                break

    # ==================== 统计操作 ====================
    @staticmethod
    def get_today_stats():
        """获取今日刷题统计

        Returns:
            今日统计数据
        """
        progress = MathModel.get_overall_progress()
        mistakes_data = MathModel.load_mistakes()
        today = BaseModel.get_today_str()

        # 统计今日做题数（简化处理：从进度中获取总数）
        today_done = 0
        today_correct = 0

        # 统计未掌握的错题数
        unmastered_mistakes = len([m for m in mistakes_data.get("mistakes", [])
                                   if not m.get("mastered")])

        return {
            "total_done": progress["total_done"],
            "total_correct": progress["total_correct"],
            "accuracy": progress["accuracy"],
            "unmastered_mistakes": unmastered_mistakes
        }
