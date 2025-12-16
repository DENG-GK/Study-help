"""
数学学习控制器模块
"""

import random
from models import MathModel


class MathController:
    """数学学习控制器 - 管理刷题逻辑"""

    def __init__(self, on_question_update=None, on_progress_update=None, on_answer_result=None):
        """初始化数学学习控制器

        Args:
            on_question_update: 题目更新回调函数
            on_progress_update: 进度更新回调函数
            on_answer_result: 答题结果回调函数
        """
        self.current_tab = "practice"  # practice/mistakes/formulas/progress/settings
        self.question_list = []
        self.current_question = None
        self.question_index = 0
        self.show_solution = False
        self.user_answer = None
        self.is_answered = False

        # 今日统计
        self.today_done = 0
        self.today_correct = 0

        # 回调函数
        self._on_question_update = on_question_update
        self._on_progress_update = on_progress_update
        self._on_answer_result = on_answer_result

    def switch_tab(self, tab):
        """切换标签页

        Args:
            tab: 标签页名称 ('practice', 'mistakes', 'formulas', 'progress', 'settings')
        """
        self.current_tab = tab
        if self._on_question_update:
            self._on_question_update()

    def load_daily_questions(self):
        """加载今日刷题题目"""
        self.question_list = MathModel.get_daily_questions()
        if self.question_list:
            self.question_index = 0
            self.current_question = self.question_list[0]
        else:
            self.current_question = None

        self.show_solution = False
        self.user_answer = None
        self.is_answered = False
        self.today_done = 0
        self.today_correct = 0

        if self._on_question_update:
            self._on_question_update()
        if self._on_progress_update:
            self._on_progress_update()

    def next_question(self):
        """下一题"""
        if not self.question_list:
            return

        self.question_index = (self.question_index + 1) % len(self.question_list)
        self.current_question = self.question_list[self.question_index]
        self.show_solution = False
        self.user_answer = None
        self.is_answered = False

        if self._on_question_update:
            self._on_question_update()

    def prev_question(self):
        """上一题"""
        if not self.question_list:
            return

        self.question_index = (self.question_index - 1) % len(self.question_list)
        self.current_question = self.question_list[self.question_index]
        self.show_solution = False
        self.user_answer = None
        self.is_answered = False

        if self._on_question_update:
            self._on_question_update()

    def submit_answer(self, answer):
        """提交答案

        Args:
            answer: 用户答案（选择题为 'A'/'B'/'C'/'D'）

        Returns:
            是否正确
        """
        if not self.current_question or self.is_answered:
            return None

        self.user_answer = answer
        self.is_answered = True
        correct_answer = self.current_question.get("answer", "")
        is_correct = answer.upper() == correct_answer.upper()

        # 更新统计
        self.today_done += 1
        if is_correct:
            self.today_correct += 1

        # 记录答题结果
        MathModel.record_answer(
            self.current_question.get("id"),
            is_correct,
            self.current_question.get("chapter"),
            self.current_question.get("section")
        )

        if self._on_progress_update:
            self._on_progress_update()

        if self._on_answer_result:
            self._on_answer_result(is_correct, correct_answer)

        return is_correct

    def toggle_solution(self):
        """显示/隐藏解析"""
        settings = MathModel.load_settings()
        if not settings.get("show_solution", True):
            return

        self.show_solution = not self.show_solution

        if self._on_question_update:
            self._on_question_update()

    def add_to_mistakes(self, notes=""):
        """将当前题目加入错题本

        Args:
            notes: 笔记

        Returns:
            是否新增成功（False表示已存在并更新）
        """
        if not self.current_question:
            return False

        return MathModel.add_mistake(self.current_question.get("id"), notes)

    def remove_from_mistakes(self):
        """从错题本移除当前题目"""
        if not self.current_question:
            return

        MathModel.remove_mistake(self.current_question.get("id"))

    def mark_mastered(self):
        """标记当前错题为已掌握"""
        if not self.current_question:
            return

        MathModel.mark_mistake_mastered(self.current_question.get("id"), True)

    # ==================== 错题本相关 ====================
    def load_mistakes(self):
        """加载错题本

        Returns:
            错题列表（包含题目数据）
        """
        return MathModel.get_all_mistakes()

    def add_image_mistake(self, image_path, chapter="其他", section="其他", notes="", difficulty=1, answer_image_path=None):
        """添加图片错题

        Args:
            image_path: 错题图片路径
            chapter: 章节
            section: 小节
            notes: 笔记
            difficulty: 难度
            answer_image_path: 答案图片路径（可选）

        Returns:
            新错题ID
        """
        return MathModel.add_image_mistake(image_path, chapter, section, notes, difficulty, answer_image_path)

    def load_review_mistakes(self):
        """加载需要复习的错题

        Returns:
            需要复习的错题列表
        """
        return MathModel.get_review_mistakes()

    def start_mistake_review(self):
        """开始错题复习"""
        review_list = self.load_review_mistakes()
        if not review_list:
            self.question_list = []
            self.current_question = None
        else:
            self.question_list = [item["question"] for item in review_list]
            # 标记为错题来源
            for q in self.question_list:
                q["from_mistakes"] = True
            self.question_index = 0
            self.current_question = self.question_list[0]

        self.show_solution = False
        self.user_answer = None
        self.is_answered = False

        if self._on_question_update:
            self._on_question_update()

    # ==================== 公式速查相关 ====================
    def load_formulas(self, category=None):
        """加载公式

        Args:
            category: 分类名称，None表示全部

        Returns:
            公式数据
        """
        data = MathModel.load_formulas()
        formulas = data.get("formulas", {})

        if category:
            return formulas.get(category, [])
        return formulas

    def get_formula_categories(self):
        """获取公式分类列表

        Returns:
            分类名称列表
        """
        data = MathModel.load_formulas()
        return list(data.get("formulas", {}).keys())

    # ==================== 进度相关 ====================
    def get_chapter_progress(self, chapter=None):
        """获取章节进度

        Args:
            chapter: 章节名称，None表示全部

        Returns:
            进度数据
        """
        if chapter:
            return MathModel.get_chapter_progress(chapter)
        return MathModel.load_progress().get("chapters", {})

    def get_overall_stats(self):
        """获取整体统计

        Returns:
            统计数据字典
        """
        return MathModel.get_overall_progress()

    # ==================== 设置相关 ====================
    def load_settings(self):
        """加载设置

        Returns:
            设置数据字典
        """
        return MathModel.load_settings()

    def save_settings(self, settings):
        """保存设置

        Args:
            settings: 设置数据字典
        """
        MathModel.save_settings(settings)

    def update_setting(self, key, value):
        """更新单个设置项

        Args:
            key: 设置键
            value: 设置值
        """
        settings = self.load_settings()
        settings[key] = value
        self.save_settings(settings)

    # ==================== 辅助方法 ====================
    def get_progress_text(self):
        """获取进度文本

        Returns:
            进度文本字符串
        """
        settings = MathModel.load_settings()
        daily_count = settings.get("daily_count", 3)

        accuracy = 0
        if self.today_done > 0:
            accuracy = round(self.today_correct / self.today_done * 100, 1)

        return f"进度: {self.question_index + 1}/{len(self.question_list)}  今日: {self.today_done}/{daily_count}  正确率: {accuracy}%"

    def get_current_question_info(self):
        """获取当前题目信息

        Returns:
            题目信息字典
        """
        if not self.current_question:
            return None

        return {
            "question": self.current_question,
            "index": self.question_index,
            "total": len(self.question_list),
            "is_answered": self.is_answered,
            "user_answer": self.user_answer,
            "show_solution": self.show_solution,
            "from_mistakes": self.current_question.get("from_mistakes", False)
        }

    def get_question_count_by_difficulty(self):
        """获取各难度题目数量统计

        Returns:
            难度统计字典
        """
        data = MathModel.load_questions()
        questions = data.get("questions", [])

        stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for q in questions:
            diff = q.get("difficulty", 1)
            if diff in stats:
                stats[diff] += 1

        return stats
