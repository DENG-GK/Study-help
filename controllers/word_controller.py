"""
单词学习控制器模块
"""

import random
from models import WordModel


class WordController:
    """单词学习控制器 - 管理单词学习逻辑"""

    def __init__(self, on_word_update=None, on_progress_update=None):
        """初始化单词学习控制器

        Args:
            on_word_update: 单词更新回调函数
            on_progress_update: 进度更新回调函数
        """
        self.mode = "card"  # card/choice/spell
        self.word_list = []
        self.current_word = None
        self.word_index = 0
        self.card_flipped = False
        self.today_new_count = 0
        self.today_review_count = 0
        self.correct_choice_idx = 0

        self._on_word_update = on_word_update
        self._on_progress_update = on_progress_update

    def load_today_words(self):
        """加载今日学习单词（乱序）"""
        self.word_list = WordModel.get_today_words()
        if self.word_list:
            random.shuffle(self.word_list)
            self.word_index = 0
            self.current_word = self.word_list[0]
        else:
            self.current_word = None

        self.card_flipped = False

        if self._on_word_update:
            self._on_word_update()
        if self._on_progress_update:
            self._on_progress_update()

    def switch_mode(self, mode):
        """切换学习模式

        Args:
            mode: 学习模式 ('card', 'choice', 'spell')
        """
        self.mode = mode
        self.card_flipped = False

        if mode == "choice":
            self.generate_choices()

        if self._on_word_update:
            self._on_word_update()

    def flip_card(self):
        """翻转卡片"""
        if self.mode != "card":
            return

        self.card_flipped = not self.card_flipped

        if self._on_word_update:
            self._on_word_update()

    def answer_word(self, result):
        """回答单词（认识/模糊/不认识）

        Args:
            result: 回答结果 ('correct', 'fuzzy', 'wrong')
        """
        if not self.current_word:
            return

        # 更新单词进度
        is_correct = result == "correct"
        WordModel.update_word_progress(self.current_word["id"], is_correct)

        # 更新统计
        if result == "correct":
            self.today_new_count += 1

        if self._on_progress_update:
            self._on_progress_update()

        # 显示下一个单词
        self.next_word()

    def next_word(self):
        """显示下一个单词"""
        if not self.word_list:
            self.current_word = None
            if self._on_word_update:
                self._on_word_update()
            return

        self.word_index = (self.word_index + 1) % len(self.word_list)
        self.current_word = self.word_list[self.word_index]
        self.card_flipped = False

        # 如果是选择题模式，重新生成选项
        if self.mode == "choice":
            self.generate_choices()

        if self._on_word_update:
            self._on_word_update()

    def generate_choices(self):
        """生成选择题选项

        Returns:
            选项列表 [(index, meaning, is_correct), ...]
        """
        if not self.current_word or not self.word_list:
            return []

        correct_meaning = self.current_word.get("meaning", "")
        self.correct_choice_idx = random.randint(0, 3)

        # 获取其他单词的释义作为干扰项
        other_meanings = [
            w.get("meaning", "") for w in self.word_list
            if w.get("id") != self.current_word.get("id") and w.get("meaning")
        ]

        # 如果干扰项不够，添加一些默认选项
        default_meanings = [
            "n. 学习；研究", "v. 帮助；援助", "adj. 重要的", "adv. 经常地",
            "v. 改变；变化", "n. 问题；难题", "adj. 不同的", "v. 发展；开发"
        ]
        while len(other_meanings) < 3:
            other_meanings.extend(default_meanings)

        random.shuffle(other_meanings)
        distractors = other_meanings[:3]

        # 构建选项
        choices = []
        distractor_idx = 0
        for i in range(4):
            if i == self.correct_choice_idx:
                choices.append((i, correct_meaning, True))
            else:
                choices.append((i, distractors[distractor_idx], False))
                distractor_idx += 1

        return choices

    def select_choice(self, idx):
        """选择题模式：选择选项

        Args:
            idx: 选项索引

        Returns:
            是否正确
        """
        if not self.current_word:
            return False

        is_correct = idx == self.correct_choice_idx

        # 更新单词进度
        WordModel.update_word_progress(self.current_word["id"], is_correct)

        # 更新统计
        if is_correct:
            self.today_new_count += 1

        if self._on_progress_update:
            self._on_progress_update()

        return is_correct

    def check_spelling(self, user_input):
        """拼写模式：检查拼写

        Args:
            user_input: 用户输入的拼写

        Returns:
            (是否正确, 正确单词)
        """
        if not self.current_word:
            return False, ""

        user_input = user_input.strip().lower()
        correct_word = self.current_word.get("word", "").strip().lower()

        is_correct = user_input == correct_word

        # 更新单词进度
        WordModel.update_word_progress(self.current_word["id"], is_correct)

        # 更新统计
        if is_correct:
            self.today_new_count += 1

        if self._on_progress_update:
            self._on_progress_update()

        return is_correct, self.current_word.get("word", "")

    def toggle_star(self):
        """收藏/取消收藏当前单词"""
        if not self.current_word:
            return

        WordModel.toggle_star_word(self.current_word["id"])

        # 更新本地状态
        is_starred = self.current_word.get("starred", False)
        self.current_word["starred"] = not is_starred

        if self._on_word_update:
            self._on_word_update()

    def get_progress_text(self):
        """获取进度文本

        Returns:
            进度文本字符串
        """
        settings = WordModel.load_word_settings()
        daily_new = settings.get("daily_new_words", 30)
        daily_review = settings.get("daily_review_words", 50)

        return f"今日: 新学 {self.today_new_count}/{daily_new}  复习 {self.today_review_count}/{daily_review}"
