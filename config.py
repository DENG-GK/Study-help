"""
配置模块 - 所有常量和配置项集中管理
作者：哈雷酱 (￣▽￣)
"""

import os
import sys
import json

# ==================== 应用配置 ====================
APP_NAME = "ImgMaster的专用学习助手"

# 处理打包后的路径问题
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 数据文件路径 ====================
DATA_DIR = os.path.join(BASE_DIR, "data")
TODOS_FILE = os.path.join(DATA_DIR, "todos.json")
RECORDS_FILE = os.path.join(DATA_DIR, "study_records.json")
SUBJECTS_FILE = os.path.join(DATA_DIR, "subjects.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "app_settings.json")

# 单词数据文件
WORDS_FILE = os.path.join(DATA_DIR, "words.json")
WORD_SETTINGS_FILE = os.path.join(DATA_DIR, "word_settings.json")
WORD_STATS_FILE = os.path.join(DATA_DIR, "word_stats.json")

# 数学数据文件
MATH_QUESTIONS_FILE = os.path.join(DATA_DIR, "math_questions.json")
MATH_MISTAKES_FILE = os.path.join(DATA_DIR, "math_mistakes.json")
MATH_PROGRESS_FILE = os.path.join(DATA_DIR, "math_progress.json")
MATH_SETTINGS_FILE = os.path.join(DATA_DIR, "math_settings.json")
MATH_FORMULAS_FILE = os.path.join(DATA_DIR, "math_formulas.json")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# ==================== 番茄钟设置 ====================
DEFAULT_FOCUS_TIME = 25
DEFAULT_BREAK_TIME = 5

# ==================== 单词学习设置 ====================
REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]

DEFAULT_WORD_SETTINGS = {
    "daily_new_words": 30,
    "daily_review_words": 50,
    "learning_mode": "card",
    "auto_play_sound": False,
    "show_example": True
}

# ==================== 数学学习设置 ====================
# 错题复习间隔（天）- 基于艾宾浩斯遗忘曲线
MATH_REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]

# 数学默认设置
DEFAULT_MATH_SETTINGS = {
    "daily_count": 3,                # 每日刷题数量：1/3/5
    "difficulty_mode": "progressive", # 难度模式：progressive(递进)/random(随机)/fixed(固定)
    "include_mistakes": True,        # 是否包含错题
    "mistake_ratio": 0.3,            # 错题占比
    "show_solution": True,           # 是否显示解析
    "auto_add_mistake": False        # 答错是否自动加入错题本
}

# 数学章节配置
MATH_CHAPTERS = {
    "高等数学": ["极限", "导数", "积分", "微分方程", "级数", "多元函数"],
    "线性代数": ["行列式", "矩阵", "向量", "线性方程组", "特征值"],
    "概率统计": ["随机事件", "随机变量", "数字特征", "大数定律", "参数估计"]
}

# ==================== 默认科目 ====================
DEFAULT_SUBJECTS = ["数学", "英语", "政治", "专业课", "其他"]

# ==================== 颜色配置 ====================
# 深色主题
DARK_COLORS = {
    "bg_dark": "#0d1117",
    "bg_card": "#161b22",
    "bg_input": "#21262d",
    "accent_blue": "#58a6ff",
    "accent_green": "#3fb950",
    "accent_red": "#f85149",
    "accent_yellow": "#d29922",
    "accent_purple": "#a371f7",
    "text_primary": "#e6edf3",
    "text_secondary": "#7d8590",
    "border": "#30363d"
}

# 浅色主题
LIGHT_COLORS = {
    "bg_dark": "#ffffff",
    "bg_card": "#f6f8fa",
    "bg_input": "#eaeef2",
    "accent_blue": "#0969da",
    "accent_green": "#1a7f37",
    "accent_red": "#cf222e",
    "accent_yellow": "#9a6700",
    "accent_purple": "#8250df",
    "text_primary": "#000000",      # 改为纯黑色，更清晰
    "text_secondary": "#24292f",    # 改为深灰色，更清晰
    "border": "#d0d7de"
}

# 图表颜色
CHART_COLORS = [
    "#58a6ff", "#3fb950", "#f85149", "#d29922", "#a371f7",
    "#f778ba", "#79c0ff", "#7ee787", "#ffa657", "#d2a8ff"
]


class ThemeManager:
    """主题管理器"""

    _instance = None
    _current_theme = "dark"
    _callbacks = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_theme()
        return cls._instance

    def _load_theme(self):
        """从设置文件加载主题"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self._current_theme = settings.get("theme", "dark")
        except:
            self._current_theme = "dark"

    def _save_theme(self):
        """保存主题到设置文件"""
        try:
            settings = {}
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
            settings["theme"] = self._current_theme
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False)
        except:
            pass

    @property
    def current_theme(self):
        return self._current_theme

    @property
    def is_dark(self):
        return self._current_theme == "dark"

    def get_colors(self):
        """获取当前主题的颜色配置"""
        if self._current_theme == "dark":
            return DARK_COLORS.copy()
        return LIGHT_COLORS.copy()

    def toggle_theme(self):
        """切换主题"""
        self._current_theme = "light" if self._current_theme == "dark" else "dark"
        self._save_theme()
        self._notify_callbacks()
        return self._current_theme

    def set_theme(self, theme):
        """设置主题

        Args:
            theme: 主题名称 ("dark" 或 "light")
        """
        if theme in ("dark", "light"):
            self._current_theme = theme
            self._save_theme()
            self._notify_callbacks()

    def register_callback(self, callback):
        """注册主题变化回调"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback):
        """注销主题变化回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_callbacks(self):
        """通知所有回调"""
        for callback in self._callbacks:
            try:
                callback(self._current_theme)
            except:
                pass


# 创建全局主题管理器实例
theme_manager = ThemeManager()


def get_colors():
    """获取当前主题颜色（推荐使用此函数）

    注意：此函数每次调用都会返回当前主题的颜色，
    确保主题切换后能获取到最新颜色。
    """
    return theme_manager.get_colors()


# 兼容旧代码：COLORS 作为动态属性
# 警告：直接使用 COLORS 可能导致主题切换后颜色不更新
# 推荐使用 get_colors() 函数
COLORS = theme_manager.get_colors()
