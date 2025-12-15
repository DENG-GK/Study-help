"""
配置模块 - 所有常量和配置项集中管理
作者：哈雷酱 (￣▽￣)
"""

import os
import sys

# ==================== 应用配置 ====================
APP_NAME = "ImgMaster的专用学习助手"

# 处理打包后的路径问题
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe，使用exe所在目录
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 如果是脚本运行，使用脚本所在目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 数据文件路径 ====================
DATA_DIR = os.path.join(BASE_DIR, "data")
TODOS_FILE = os.path.join(DATA_DIR, "todos.json")
RECORDS_FILE = os.path.join(DATA_DIR, "study_records.json")
SUBJECTS_FILE = os.path.join(DATA_DIR, "subjects.json")

# 单词数据文件
WORDS_FILE = os.path.join(DATA_DIR, "words.json")
WORD_SETTINGS_FILE = os.path.join(DATA_DIR, "word_settings.json")
WORD_STATS_FILE = os.path.join(DATA_DIR, "word_stats.json")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# ==================== 番茄钟设置 ====================
DEFAULT_FOCUS_TIME = 25  # 专注时间（分钟）
DEFAULT_BREAK_TIME = 5   # 休息时间（分钟）

# ==================== 单词学习设置 ====================
# 艾宾浩斯遗忘曲线复习间隔（天）
REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]

# 默认单词学习设置
DEFAULT_WORD_SETTINGS = {
    "daily_new_words": 30,
    "daily_review_words": 50,
    "learning_mode": "card",
    "auto_play_sound": False,
    "show_example": True
}

# ==================== 默认科目 ====================
DEFAULT_SUBJECTS = ["数学", "英语", "政治", "专业课", "其他"]

# ==================== 颜色配置 ====================
COLORS = {
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

# 图表颜色
CHART_COLORS = [
    '#58a6ff', '#3fb950', '#f85149', '#d29922', '#a371f7',
    '#f778ba', '#79c0ff', '#7ee787', '#ffa657', '#d2a8ff'
]
