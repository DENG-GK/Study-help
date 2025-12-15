"""
学习助手 v2.0 - 科技感桌面待办与番茄钟
作者：哈雷酱 (￣▽￣)
功能：待办管理、番茄钟、分科目学习时长记录、统计图表
"""

import customtkinter as ctk
import json
import os
from datetime import datetime, timedelta
from threading import Thread
import time
import winsound
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
matplotlib.rcParams['axes.unicode_minus'] = False

# ==================== 配置 ====================
APP_NAME = "ImgMaster的专用学习助手"

# 处理打包后的路径问题
import sys
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe，使用exe所在目录
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 如果是脚本运行，使用脚本所在目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
TODOS_FILE = os.path.join(DATA_DIR, "todos.json")
RECORDS_FILE = os.path.join(DATA_DIR, "study_records.json")
SUBJECTS_FILE = os.path.join(DATA_DIR, "subjects.json")

# 单词数据文件
WORDS_FILE = os.path.join(DATA_DIR, "words.json")
WORD_SETTINGS_FILE = os.path.join(DATA_DIR, "word_settings.json")
WORD_STATS_FILE = os.path.join(DATA_DIR, "word_stats.json")

# 番茄钟默认设置（分钟）
DEFAULT_FOCUS_TIME = 25
DEFAULT_BREAK_TIME = 5

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

# 默认科目
DEFAULT_SUBJECTS = ["数学", "英语", "政治", "专业课", "其他"]

# 颜色配置
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
CHART_COLORS = ['#58a6ff', '#3fb950', '#f85149', '#d29922', '#a371f7',
                '#f778ba', '#79c0ff', '#7ee787', '#ffa657', '#d2a8ff']

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)


# ==================== 数据管理类 ====================
class DataManager:
    """数据管理器 - 负责所有数据的读写"""

    @staticmethod
    def load_json(filepath, default=None):
        """加载JSON文件"""
        if default is None:
            default = {}
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载文件失败: {e}")
        return default

    @staticmethod
    def save_json(filepath, data):
        """保存JSON文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存文件失败: {e}")

    @staticmethod
    def get_today_str():
        """获取今天的日期字符串"""
        return datetime.now().strftime("%Y-%m-%d")

    # ===== 科目管理 =====
    @staticmethod
    def load_subjects():
        """加载科目列表"""
        data = DataManager.load_json(SUBJECTS_FILE, {"subjects": DEFAULT_SUBJECTS})
        if not data.get("subjects"):
            data["subjects"] = DEFAULT_SUBJECTS
            DataManager.save_json(SUBJECTS_FILE, data)
        return data["subjects"]

    @staticmethod
    def save_subjects(subjects):
        """保存科目列表"""
        DataManager.save_json(SUBJECTS_FILE, {"subjects": subjects})

    @staticmethod
    def add_subject(name):
        """添加科目"""
        subjects = DataManager.load_subjects()
        if name and name not in subjects:
            subjects.append(name)
            DataManager.save_subjects(subjects)
        return subjects

    @staticmethod
    def remove_subject(name):
        """删除科目"""
        subjects = DataManager.load_subjects()
        if name in subjects and name != "其他":
            subjects.remove(name)
            DataManager.save_subjects(subjects)
        return subjects

    # ===== 待办事项 =====
    @staticmethod
    def load_todos():
        """加载待办事项"""
        return DataManager.load_json(TODOS_FILE, {"todos": []})

    @staticmethod
    def save_todos(data):
        """保存待办事项"""
        DataManager.save_json(TODOS_FILE, data)

    # ===== 学习记录 =====
    @staticmethod
    def load_records():
        """加载学习记录"""
        return DataManager.load_json(RECORDS_FILE, {"records": {}})

    @staticmethod
    def save_records(data):
        """保存学习记录"""
        DataManager.save_json(RECORDS_FILE, data)

    @staticmethod
    def add_focus_time(minutes, subject="其他", add_pomodoro=True):
        """添加专注时间（分科目）

        Args:
            minutes: 专注时间（分钟）
            subject: 科目名称
            add_pomodoro: 是否增加番茄计数（实时记录时为False）
        """
        records = DataManager.load_records()
        today = DataManager.get_today_str()

        if today not in records["records"]:
            records["records"][today] = {
                "total_time": 0,
                "completed_tasks": 0,
                "pomodoros": 0,
                "subjects": {}
            }

        # 更新总时间
        records["records"][today]["total_time"] += minutes

        # 只有完成整个番茄钟时才增加番茄数
        if add_pomodoro:
            records["records"][today]["pomodoros"] += 1

        # 更新科目时间
        if "subjects" not in records["records"][today]:
            records["records"][today]["subjects"] = {}

        if subject not in records["records"][today]["subjects"]:
            records["records"][today]["subjects"][subject] = 0
        records["records"][today]["subjects"][subject] += minutes

        DataManager.save_records(records)

    @staticmethod
    def add_completed_task():
        """添加完成任务数"""
        records = DataManager.load_records()
        today = DataManager.get_today_str()
        if today not in records["records"]:
            records["records"][today] = {
                "total_time": 0,
                "completed_tasks": 0,
                "pomodoros": 0,
                "subjects": {}
            }
        records["records"][today]["completed_tasks"] += 1
        DataManager.save_records(records)

    @staticmethod
    def remove_completed_task():
        """减少完成任务数（取消完成时调用）"""
        records = DataManager.load_records()
        today = DataManager.get_today_str()
        if today in records["records"]:
            if records["records"][today]["completed_tasks"] > 0:
                records["records"][today]["completed_tasks"] -= 1
                DataManager.save_records(records)

    @staticmethod
    def get_today_stats():
        """获取今日统计"""
        records = DataManager.load_records()
        today = DataManager.get_today_str()
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
        """获取历史统计数据"""
        records = DataManager.load_records()
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

    # ===== 单词管理 =====
    @staticmethod
    def load_words():
        """加载单词库"""
        return DataManager.load_json(WORDS_FILE, {"words": []})

    @staticmethod
    def save_words(data):
        """保存单词库"""
        DataManager.save_json(WORDS_FILE, data)

    @staticmethod
    def load_word_settings():
        """加载单词学习设置"""
        return DataManager.load_json(WORD_SETTINGS_FILE, DEFAULT_WORD_SETTINGS)

    @staticmethod
    def save_word_settings(settings):
        """保存单词学习设置"""
        DataManager.save_json(WORD_SETTINGS_FILE, settings)

    @staticmethod
    def load_word_stats():
        """加载单词学习统计"""
        return DataManager.load_json(WORD_STATS_FILE, {"records": {}})

    @staticmethod
    def save_word_stats(data):
        """保存单词学习统计"""
        DataManager.save_json(WORD_STATS_FILE, data)

    @staticmethod
    def get_today_words():
        """获取今日学习单词（新学+复习）"""
        data = DataManager.load_words()
        settings = DataManager.load_word_settings()
        today = DataManager.get_today_str()

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
        """更新单词学习进度"""
        data = DataManager.load_words()
        today = DataManager.get_today_str()

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

        DataManager.save_words(data)

        # 更新今日统计
        stats = DataManager.load_word_stats()
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

        DataManager.save_word_stats(stats)

    @staticmethod
    def toggle_star_word(word_id):
        """收藏/取消收藏单词"""
        data = DataManager.load_words()

        for word in data.get("words", []):
            if word.get("id") == word_id:
                word["starred"] = not word.get("starred", False)
                break

        DataManager.save_words(data)

    @staticmethod
    def add_word_manually(word, phonetic="", meaning="", example="", example_cn=""):
        """手动添加单词"""
        data = DataManager.load_words()
        today = DataManager.get_today_str()

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
        DataManager.save_words(data)
        return new_word

    @staticmethod
    def import_words_from_file(filepath, file_type="txt"):
        """从文件导入单词"""
        import csv

        data = DataManager.load_words()
        today = DataManager.get_today_str()
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

            DataManager.save_words(data)
        except Exception as e:
            print(f"导入失败: {e}")

        return count


# ==================== 主应用类 ====================
class StudyAssistantApp(ctk.CTk):
    """学习助手主窗口"""

    def __init__(self):
        super().__init__()

        # 窗口设置
        self.title(APP_NAME)
        self.geometry("920x720")  # 扩展为左右并排布局
        self.resizable(False, False)

        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 设置窗口背景颜色
        self.configure(fg_color=COLORS["bg_dark"])

        # 窗口置顶
        self.attributes('-topmost', True)

        # 设置半透明效果 (Windows)
        try:
            self.attributes('-alpha', 0.92)
        except:
            pass

        # 拖动窗口相关数据（事件绑定在标题栏上，避免和滑块冲突）
        self._drag_data = {"x": 0, "y": 0}

        # 番茄钟状态
        self.pomodoro_running = False
        self.pomodoro_paused = False
        self.is_focus_time = True
        self.remaining_seconds = DEFAULT_FOCUS_TIME * 60
        self.pomodoro_thread = None
        self.current_subject = "其他"
        self.recorded_minutes = 0  # 已记录的专注分钟数（用于实时记录）

        # 专注计时状态
        self.focus_tracking = False
        self.focus_start_time = None
        self.tracking_subject = "其他"

        # 当前页面
        self.current_page = "main"

        # ===== 背单词状态 =====
        self.word_learning_mode = "card"  # card/choice/spell
        self.current_word = None  # 当前学习的单词
        self.word_list = []  # 今日学习单词列表
        self.word_index = 0  # 当前单词索引
        self.card_flipped = False  # 卡片是否翻转
        self.today_new_count = 0  # 今日新学数量
        self.today_review_count = 0  # 今日复习数量

        # 创建界面（内部会自动加载数据）
        self.create_widgets()

    def start_move(self, event):
        """开始拖动"""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_move(self, event):
        """拖动中"""
        x = self.winfo_x() + (event.x - self._drag_data["x"])
        y = self.winfo_y() + (event.y - self._drag_data["y"])
        self.geometry(f"+{x}+{y}")

    def change_opacity(self, value):
        """调节窗口透明度"""
        try:
            self.attributes('-alpha', value)
            percent = int(value * 100)
            if hasattr(self, 'opacity_value_label'):
                self.opacity_value_label.configure(text=f"{percent}%")
        except:
            pass

    def create_widgets(self):
        """创建所有控件"""

        # 主容器
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # 创建顶部标题栏（跨越整个窗口）
        self.create_header()

        # 创建内容区域（左右两栏）
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 左栏容器 - 学习管理 (420px)
        self.left_column = ctk.CTkFrame(self.content_frame, fg_color="transparent", width=410)
        self.left_column.pack(side="left", fill="both", padx=(0, 5))
        self.left_column.pack_propagate(False)

        # 右栏容器 - 背单词 (490px)
        self.right_column = ctk.CTkFrame(self.content_frame, fg_color="transparent", width=490)
        self.right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # 创建左栏内容（学习管理）
        self.create_left_panel()

        # 创建右栏内容（背单词）
        self.create_word_panel()

    def create_header(self):
        """创建顶部标题栏"""
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color=COLORS["bg_card"], corner_radius=0)
        self.header_frame.pack(fill="x", padx=0, pady=0)

        # 绑定拖动事件
        self.header_frame.bind('<Button-1>', self.start_move)
        self.header_frame.bind('<B1-Motion>', self.on_move)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="📚 ImgMaster的专用学习助手",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["accent_blue"]
        )
        self.title_label.pack(side="left", padx=15, pady=10)
        self.title_label.bind('<Button-1>', self.start_move)
        self.title_label.bind('<B1-Motion>', self.on_move)

        # 日期显示
        self.date_label = ctk.CTkLabel(
            self.header_frame,
            text=datetime.now().strftime("%m月%d日"),
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.date_label.pack(side="right", padx=15, pady=10)

        # 透明度调节
        self.opacity_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.opacity_frame.pack(side="right", padx=10)

        ctk.CTkLabel(
            self.opacity_frame,
            text="🔆",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=2)

        self.opacity_slider = ctk.CTkSlider(
            self.opacity_frame,
            from_=0.3,
            to=1.0,
            number_of_steps=70,
            width=100,
            height=14,
            fg_color=COLORS["bg_input"],
            progress_color=COLORS["accent_blue"],
            button_color=COLORS["accent_blue"],
            button_hover_color=COLORS["accent_purple"],
            command=self.change_opacity
        )
        self.opacity_slider.set(0.92)
        self.opacity_slider.pack(side="left", padx=2)

        self.opacity_value_label = ctk.CTkLabel(
            self.opacity_frame,
            text="92%",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"],
            width=30
        )
        self.opacity_value_label.pack(side="left", padx=2)

    def create_left_panel(self):
        """创建左栏 - 学习管理面板"""
        # ===== 今日统计卡片 =====
        self.stats_frame = ctk.CTkFrame(self.left_column, fg_color=COLORS["bg_card"], corner_radius=10)
        self.stats_frame.pack(fill="x", padx=5, pady=5)

        # 标题行容器（标题 + 详情按钮）
        stats_header = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        stats_header.pack(fill="x", padx=15, pady=(10, 5))

        self.stats_title = ctk.CTkLabel(
            stats_header,
            text="📊 今日成就",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_blue"]
        )
        self.stats_title.pack(side="left")

        # 详情按钮 - 打开统计页面（饼图和曲线图）
        self.stats_detail_btn = ctk.CTkButton(
            stats_header,
            text="📈 详情",
            width=60,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            command=self.show_stats_page
        )
        self.stats_detail_btn.pack(side="right")

        # 统计数据容器
        self.stats_data_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        self.stats_data_frame.pack(fill="x", padx=15, pady=(0, 10))

        # 专注时长
        self.focus_stat_frame = ctk.CTkFrame(self.stats_data_frame, fg_color=COLORS["bg_input"], corner_radius=8)
        self.focus_stat_frame.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.focus_time_label = ctk.CTkLabel(
            self.focus_stat_frame,
            text="0 分钟",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_green"]
        )
        self.focus_time_label.pack(pady=(6, 1))
        ctk.CTkLabel(self.focus_stat_frame, text="专注时长", font=ctk.CTkFont(size=9),
                    text_color=COLORS["text_secondary"]).pack(pady=(0, 6))

        # 完成任务
        self.task_stat_frame = ctk.CTkFrame(self.stats_data_frame, fg_color=COLORS["bg_input"], corner_radius=8)
        self.task_stat_frame.pack(side="left", expand=True, fill="x", padx=(5, 5))
        self.completed_label = ctk.CTkLabel(
            self.task_stat_frame,
            text="0 个",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_red"]
        )
        self.completed_label.pack(pady=(6, 1))
        ctk.CTkLabel(self.task_stat_frame, text="完成任务", font=ctk.CTkFont(size=9),
                    text_color=COLORS["text_secondary"]).pack(pady=(0, 6))

        # 番茄数
        self.pomo_stat_frame = ctk.CTkFrame(self.stats_data_frame, fg_color=COLORS["bg_input"], corner_radius=8)
        self.pomo_stat_frame.pack(side="left", expand=True, fill="x", padx=(5, 0))
        self.pomodoro_count_label = ctk.CTkLabel(
            self.pomo_stat_frame,
            text="0 个",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_yellow"]
        )
        self.pomodoro_count_label.pack(pady=(6, 1))
        ctk.CTkLabel(self.pomo_stat_frame, text="番茄数", font=ctk.CTkFont(size=9),
                    text_color=COLORS["text_secondary"]).pack(pady=(0, 6))

        # ===== 番茄钟区域 =====
        self.pomodoro_frame = ctk.CTkFrame(self.left_column, fg_color=COLORS["bg_card"], corner_radius=10)
        self.pomodoro_frame.pack(fill="x", padx=5, pady=5)

        self.pomodoro_title = ctk.CTkLabel(
            self.pomodoro_frame,
            text="🍅 番茄钟",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_red"]
        )
        self.pomodoro_title.pack(anchor="w", padx=15, pady=(10, 5))

        # 科目选择
        self.subject_frame = ctk.CTkFrame(self.pomodoro_frame, fg_color="transparent")
        self.subject_frame.pack(fill="x", padx=15, pady=(0, 5))

        ctk.CTkLabel(self.subject_frame, text="科目：", font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_secondary"]).pack(side="left")

        subjects = DataManager.load_subjects()
        self.subject_var = ctk.StringVar(value=self.current_subject)
        self.subject_menu = ctk.CTkOptionMenu(
            self.subject_frame,
            values=subjects,
            variable=self.subject_var,
            width=100,
            height=25,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["accent_blue"],
            button_hover_color=COLORS["accent_purple"],
            command=self.on_subject_change
        )
        self.subject_menu.pack(side="left", padx=5)

        # 管理科目按钮
        self.manage_subject_btn = ctk.CTkButton(
            self.subject_frame,
            text="⚙",
            width=25,
            height=25,
            fg_color="transparent",
            hover_color=COLORS["bg_input"],
            command=self.show_subject_manager
        )
        self.manage_subject_btn.pack(side="left", padx=2)

        # 计时器显示
        self.timer_label = ctk.CTkLabel(
            self.pomodoro_frame,
            text="25:00",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color=COLORS["accent_blue"]
        )
        self.timer_label.pack(pady=8)

        # 状态文字
        self.status_label = ctk.CTkLabel(
            self.pomodoro_frame,
            text="准备开始专注",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(pady=(0, 8))

        # 番茄钟按钮
        self.pomo_btn_frame = ctk.CTkFrame(self.pomodoro_frame, fg_color="transparent")
        self.pomo_btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.start_btn = ctk.CTkButton(
            self.pomo_btn_frame,
            text="▶ 开始",
            width=90,
            height=30,
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=self.toggle_pomodoro
        )
        self.start_btn.pack(side="left", expand=True, padx=5)

        self.reset_btn = ctk.CTkButton(
            self.pomo_btn_frame,
            text="↺ 重置",
            width=90,
            height=30,
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            command=self.reset_pomodoro
        )
        self.reset_btn.pack(side="left", expand=True, padx=5)

        # ===== 待办事项区域 =====
        self.todos_frame = ctk.CTkFrame(self.left_column, fg_color=COLORS["bg_card"], corner_radius=10)
        self.todos_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 待办标题和添加按钮
        self.todos_header = ctk.CTkFrame(self.todos_frame, fg_color="transparent")
        self.todos_header.pack(fill="x", padx=15, pady=(10, 5))

        self.todos_title = ctk.CTkLabel(
            self.todos_header,
            text="📋 今日待办",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_yellow"]
        )
        self.todos_title.pack(side="left")

        self.add_btn = ctk.CTkButton(
            self.todos_header,
            text="+ 添加",
            width=55,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=self.show_add_dialog
        )
        self.add_btn.pack(side="right")

        # 待办列表（可滚动）
        self.todos_scrollable = ctk.CTkScrollableFrame(
            self.todos_frame,
            fg_color="transparent",
            height=120
        )
        self.todos_scrollable.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # ===== 底部专注记录按钮 =====
        self.bottom_frame = ctk.CTkFrame(self.left_column, fg_color=COLORS["bg_card"], corner_radius=10)
        self.bottom_frame.pack(fill="x", padx=5, pady=5)

        # 科目选择（用于手动计时）
        self.track_subject_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.track_subject_frame.pack(fill="x", padx=15, pady=(8, 5))

        ctk.CTkLabel(self.track_subject_frame, text="记录科目：", font=ctk.CTkFont(size=10),
                    text_color=COLORS["text_secondary"]).pack(side="left")

        self.track_subject_var = ctk.StringVar(value="其他")
        self.track_subject_menu = ctk.CTkOptionMenu(
            self.track_subject_frame,
            values=subjects,
            variable=self.track_subject_var,
            width=90,
            height=24,
            fg_color=COLORS["bg_input"],
            button_color=COLORS["accent_green"],
            button_hover_color=COLORS["accent_blue"]
        )
        self.track_subject_menu.pack(side="left", padx=5)

        self.focus_track_btn = ctk.CTkButton(
            self.bottom_frame,
            text="⏱ 开始记录学习时长",
            height=32,
            fg_color=COLORS["accent_green"],
            hover_color="#2ea043",
            text_color="#000000",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_focus_tracking
        )
        self.focus_track_btn.pack(fill="x", padx=15, pady=(5, 8))

        # 加载数据
        self.load_todos()
        self.update_stats_display()

    def create_word_panel(self):
        """创建右栏 - 背单词面板"""
        # ===== 顶部标题和进度 =====
        word_header = ctk.CTkFrame(self.right_column, fg_color=COLORS["bg_card"], corner_radius=10)
        word_header.pack(fill="x", padx=5, pady=5)

        header_top = ctk.CTkFrame(word_header, fg_color="transparent")
        header_top.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            header_top,
            text="📖 英语单词",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_purple"]
        ).pack(side="left")

        # 学习模式切换
        self.mode_frame = ctk.CTkFrame(header_top, fg_color="transparent")
        self.mode_frame.pack(side="right")

        self.card_mode_btn = ctk.CTkButton(
            self.mode_frame, text="卡片", width=45, height=24,
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=lambda: self.switch_word_mode("card")
        )
        self.card_mode_btn.pack(side="left", padx=2)

        self.choice_mode_btn = ctk.CTkButton(
            self.mode_frame, text="选择", width=45, height=24,
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            command=lambda: self.switch_word_mode("choice")
        )
        self.choice_mode_btn.pack(side="left", padx=2)

        self.spell_mode_btn = ctk.CTkButton(
            self.mode_frame, text="拼写", width=45, height=24,
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            command=lambda: self.switch_word_mode("spell")
        )
        self.spell_mode_btn.pack(side="left", padx=2)

        # 今日进度
        progress_frame = ctk.CTkFrame(word_header, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.word_progress_label = ctk.CTkLabel(
            progress_frame,
            text="今日: 新学 0/30  复习 0/50",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        self.word_progress_label.pack(side="left")

        # ===== 单词卡片区域 =====
        self.word_card_frame = ctk.CTkFrame(self.right_column, fg_color=COLORS["bg_card"], corner_radius=10)
        self.word_card_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 单词显示
        self.word_display = ctk.CTkLabel(
            self.word_card_frame,
            text="abandon",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.word_display.pack(pady=(40, 5))

        # 音标和发音按钮
        phonetic_frame = ctk.CTkFrame(self.word_card_frame, fg_color="transparent")
        phonetic_frame.pack(pady=5)

        self.phonetic_label = ctk.CTkLabel(
            phonetic_frame,
            text="/əˈbændən/",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        self.phonetic_label.pack(side="left", padx=5)

        self.sound_btn = ctk.CTkButton(
            phonetic_frame,
            text="🔊",
            width=30,
            height=25,
            fg_color="transparent",
            hover_color=COLORS["bg_input"],
            command=self.play_word_sound
        )
        self.sound_btn.pack(side="left", padx=5)

        # 释义区域（点击显示）
        self.meaning_frame = ctk.CTkFrame(self.word_card_frame, fg_color=COLORS["bg_input"], corner_radius=10)
        self.meaning_frame.pack(fill="x", padx=20, pady=15)

        self.meaning_label = ctk.CTkLabel(
            self.meaning_frame,
            text="点击卡片显示释义",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
            wraplength=400
        )
        self.meaning_label.pack(pady=15, padx=15)

        # 例句区域
        self.example_frame = ctk.CTkFrame(self.word_card_frame, fg_color="transparent")
        self.example_frame.pack(fill="x", padx=20, pady=5)

        self.example_label = ctk.CTkLabel(
            self.example_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            wraplength=420
        )
        self.example_label.pack(pady=5)

        # 绑定卡片点击事件
        self.word_card_frame.bind('<Button-1>', self.flip_word_card)
        self.word_display.bind('<Button-1>', self.flip_word_card)
        self.meaning_frame.bind('<Button-1>', self.flip_word_card)

        # ===== 操作按钮区域 =====
        self.word_action_frame = ctk.CTkFrame(self.right_column, fg_color=COLORS["bg_card"], corner_radius=10)
        self.word_action_frame.pack(fill="x", padx=5, pady=5)

        # 卡片模式按钮
        self.card_buttons_frame = ctk.CTkFrame(self.word_action_frame, fg_color="transparent")
        self.card_buttons_frame.pack(fill="x", padx=15, pady=10)

        self.dont_know_btn = ctk.CTkButton(
            self.card_buttons_frame,
            text="❌ 不认识",
            width=100,
            height=35,
            fg_color=COLORS["accent_red"],
            hover_color="#da3633",
            command=lambda: self.answer_word("wrong")
        )
        self.dont_know_btn.pack(side="left", expand=True, padx=5)

        self.fuzzy_btn = ctk.CTkButton(
            self.card_buttons_frame,
            text="😐 模糊",
            width=100,
            height=35,
            fg_color=COLORS["accent_yellow"],
            hover_color="#b08800",
            text_color="#000000",
            command=lambda: self.answer_word("fuzzy")
        )
        self.fuzzy_btn.pack(side="left", expand=True, padx=5)

        self.know_btn = ctk.CTkButton(
            self.card_buttons_frame,
            text="✅ 认识",
            width=100,
            height=35,
            fg_color=COLORS["accent_green"],
            hover_color="#2ea043",
            command=lambda: self.answer_word("correct")
        )
        self.know_btn.pack(side="left", expand=True, padx=5)

        # 选择题模式按钮（初始隐藏）
        self.choice_buttons_frame = ctk.CTkFrame(self.word_action_frame, fg_color="transparent")

        # 创建4个选项按钮
        self.choice_btns = []
        for i in range(4):
            btn = ctk.CTkButton(
                self.choice_buttons_frame,
                text=f"选项 {i+1}",
                width=200,
                height=35,
                fg_color=COLORS["bg_input"],
                hover_color=COLORS["accent_blue"],
                anchor="w",
                command=lambda idx=i: self.select_choice(idx)
            )
            btn.pack(fill="x", padx=15, pady=3)
            self.choice_btns.append(btn)

        # 拼写模式输入框（初始隐藏）
        self.spell_frame = ctk.CTkFrame(self.word_action_frame, fg_color="transparent")

        spell_input_frame = ctk.CTkFrame(self.spell_frame, fg_color="transparent")
        spell_input_frame.pack(fill="x", padx=15, pady=5)

        self.spell_entry = ctk.CTkEntry(
            spell_input_frame,
            placeholder_text="输入单词拼写...",
            height=40,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"]
        )
        self.spell_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.spell_entry.bind('<Return>', self.check_spelling)

        self.spell_submit_btn = ctk.CTkButton(
            spell_input_frame,
            text="确认",
            width=80,
            height=40,
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=self.check_spelling
        )
        self.spell_submit_btn.pack(side="right")

        # 拼写结果显示
        self.spell_result_label = ctk.CTkLabel(
            self.spell_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        self.spell_result_label.pack(pady=5)

        # ===== 底部功能按钮 =====
        word_bottom = ctk.CTkFrame(self.right_column, fg_color=COLORS["bg_card"], corner_radius=10)
        word_bottom.pack(fill="x", padx=5, pady=5)

        bottom_btns = ctk.CTkFrame(word_bottom, fg_color="transparent")
        bottom_btns.pack(fill="x", padx=10, pady=8)

        self.star_btn = ctk.CTkButton(
            bottom_btns, text="⭐ 收藏", width=70, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["accent_yellow"],
            command=self.toggle_star_word
        )
        self.star_btn.pack(side="left", expand=True, padx=3)

        self.wordbook_btn = ctk.CTkButton(
            bottom_btns, text="📚 词库", width=70, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            command=self.show_wordbook_manager
        )
        self.wordbook_btn.pack(side="left", expand=True, padx=3)

        self.word_stats_btn = ctk.CTkButton(
            bottom_btns, text="📊 统计", width=70, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            command=self.show_word_stats
        )
        self.word_stats_btn.pack(side="left", expand=True, padx=3)

        self.word_settings_btn = ctk.CTkButton(
            bottom_btns, text="⚙ 设置", width=70, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            command=self.show_word_settings
        )
        self.word_settings_btn.pack(side="left", expand=True, padx=3)

        # 加载今日单词
        self.load_today_words()

    # ==================== 背单词相关方法 ====================

    def switch_word_mode(self, mode):
        """切换学习模式"""
        self.word_learning_mode = mode

        # 更新按钮样式
        modes = {"card": self.card_mode_btn, "choice": self.choice_mode_btn, "spell": self.spell_mode_btn}
        for m, btn in modes.items():
            if m == mode:
                btn.configure(fg_color=COLORS["accent_blue"])
            else:
                btn.configure(fg_color=COLORS["bg_input"])

        # 隐藏所有模式的按钮框架
        self.card_buttons_frame.pack_forget()
        self.choice_buttons_frame.pack_forget()
        self.spell_frame.pack_forget()

        # 显示当前模式的按钮框架
        if mode == "card":
            self.card_buttons_frame.pack(fill="x", padx=15, pady=10)
        elif mode == "choice":
            self.choice_buttons_frame.pack(fill="x", padx=15, pady=10)
            self.generate_choices()
        elif mode == "spell":
            self.spell_frame.pack(fill="x", padx=15, pady=10)
            self.spell_entry.delete(0, 'end')
            self.spell_result_label.configure(text="")

        # 重置卡片状态
        self.card_flipped = False
        self.update_word_display()

    def flip_word_card(self, event=None):
        """翻转单词卡片"""
        if self.word_learning_mode != "card":
            return

        self.card_flipped = not self.card_flipped
        self.update_word_display()

    def update_word_display(self):
        """更新单词显示"""
        if not self.current_word:
            self.word_display.configure(text="暂无单词")
            self.phonetic_label.configure(text="")
            self.meaning_label.configure(text="请先导入词库或添加单词")
            self.example_label.configure(text="")
            return

        word = self.current_word

        # 根据模式显示不同内容
        if self.word_learning_mode == "card":
            # 卡片模式：显示单词，点击翻转显示释义
            self.word_display.configure(text=word.get("word", ""))
            self.phonetic_label.configure(text=word.get("phonetic", ""))

            if self.card_flipped:
                self.meaning_label.configure(
                    text=word.get("meaning", ""),
                    text_color=COLORS["text_primary"]
                )
                example = word.get("example", "")
                example_cn = word.get("example_cn", "")
                if example:
                    self.example_label.configure(text=f"例: {example}\n{example_cn}")
                else:
                    self.example_label.configure(text="")
            else:
                self.meaning_label.configure(
                    text="点击卡片显示释义",
                    text_color=COLORS["text_secondary"]
                )
                self.example_label.configure(text="")

        elif self.word_learning_mode == "choice":
            # 选择题模式：显示单词，从4个选项中选择正确释义
            self.word_display.configure(text=word.get("word", ""))
            self.phonetic_label.configure(text=word.get("phonetic", ""))
            self.meaning_label.configure(
                text="请选择正确的释义",
                text_color=COLORS["text_secondary"]
            )
            self.example_label.configure(text="")

        elif self.word_learning_mode == "spell":
            # 拼写模式：显示中文释义，输入英文单词
            self.word_display.configure(text="???")
            self.phonetic_label.configure(text="")
            self.meaning_label.configure(
                text=word.get("meaning", ""),
                text_color=COLORS["text_primary"]
            )
            example = word.get("example", "")
            example_cn = word.get("example_cn", "")
            if example_cn:
                # 隐藏英文例句，只显示中文翻译作为提示
                self.example_label.configure(text=f"提示: {example_cn}")
            else:
                self.example_label.configure(text="")

        # 更新收藏按钮状态
        if word.get("starred", False):
            self.star_btn.configure(text="⭐ 已收藏", fg_color=COLORS["accent_yellow"], text_color="#000000")
        else:
            self.star_btn.configure(text="⭐ 收藏", fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])

    def play_word_sound(self):
        """播放单词发音"""
        if not self.current_word:
            return

        word = self.current_word.get("word", "")
        if not word:
            return

        # 使用线程播放，避免阻塞UI
        def play():
            try:
                import urllib.request
                import tempfile
                url = f"https://dict.youdao.com/dictvoice?audio={word}&type=1"
                temp_file = os.path.join(tempfile.gettempdir(), f"{word}.mp3")

                urllib.request.urlretrieve(url, temp_file)

                # 使用系统默认播放器（需要安装pygame或playsound）
                try:
                    import playsound
                    playsound.playsound(temp_file)
                except:
                    # 备用方案：使用系统命令
                    os.startfile(temp_file)
            except Exception as e:
                print(f"播放发音失败: {e}")

        Thread(target=play, daemon=True).start()

    def answer_word(self, result):
        """回答单词（认识/模糊/不认识）"""
        if not self.current_word:
            return

        # 更新单词进度
        is_correct = result == "correct"
        DataManager.update_word_progress(self.current_word["id"], is_correct)

        # 更新统计
        if result == "correct":
            self.today_new_count += 1
        self.update_word_progress_display()

        # 显示下一个单词
        self.next_word()

    def next_word(self):
        """显示下一个单词"""
        if not self.word_list:
            self.current_word = None
            self.update_word_display()
            return

        self.word_index = (self.word_index + 1) % len(self.word_list)
        self.current_word = self.word_list[self.word_index]
        self.card_flipped = False

        # 如果是选择题模式，重新生成选项
        if self.word_learning_mode == "choice":
            self.generate_choices()

        # 如果是拼写模式，清空输入框
        if self.word_learning_mode == "spell":
            self.spell_entry.delete(0, 'end')
            self.spell_result_label.configure(text="")

        self.update_word_display()

    def generate_choices(self):
        """生成选择题选项"""
        import random

        if not self.current_word or not self.word_list:
            return

        correct_meaning = self.current_word.get("meaning", "")
        self.correct_choice_idx = random.randint(0, 3)

        # 获取其他单词的释义作为干扰项
        other_meanings = [w.get("meaning", "") for w in self.word_list
                         if w.get("id") != self.current_word.get("id") and w.get("meaning")]

        # 如果干扰项不够，添加一些默认选项
        default_meanings = ["n. 学习；研究", "v. 帮助；援助", "adj. 重要的", "adv. 经常地",
                          "v. 改变；变化", "n. 问题；难题", "adj. 不同的", "v. 发展；开发"]
        while len(other_meanings) < 3:
            other_meanings.extend(default_meanings)

        random.shuffle(other_meanings)
        distractors = other_meanings[:3]

        # 设置选项
        distractor_idx = 0
        for i in range(4):
            if i == self.correct_choice_idx:
                self.choice_btns[i].configure(
                    text=f"{chr(65+i)}. {correct_meaning}",
                    fg_color=COLORS["bg_input"],
                    text_color=COLORS["text_primary"]
                )
            else:
                self.choice_btns[i].configure(
                    text=f"{chr(65+i)}. {distractors[distractor_idx]}",
                    fg_color=COLORS["bg_input"],
                    text_color=COLORS["text_primary"]
                )
                distractor_idx += 1

    def select_choice(self, idx):
        """选择题模式：选择选项"""
        if not self.current_word:
            return

        is_correct = idx == self.correct_choice_idx

        # 显示正确/错误反馈
        for i in range(4):
            if i == self.correct_choice_idx:
                self.choice_btns[i].configure(fg_color=COLORS["accent_green"])
            elif i == idx and not is_correct:
                self.choice_btns[i].configure(fg_color=COLORS["accent_red"])

        # 更新单词进度
        DataManager.update_word_progress(self.current_word["id"], is_correct)

        # 更新统计
        if is_correct:
            self.today_new_count += 1
        self.update_word_progress_display()

        # 延迟后显示下一个单词
        self.after(800, self.next_word)

    def check_spelling(self, event=None):
        """拼写模式：检查拼写"""
        if not self.current_word:
            return

        user_input = self.spell_entry.get().strip().lower()
        correct_word = self.current_word.get("word", "").strip().lower()

        is_correct = user_input == correct_word

        if is_correct:
            self.spell_result_label.configure(
                text="✅ 正确！",
                text_color=COLORS["accent_green"]
            )
            # 显示正确单词
            self.word_display.configure(text=self.current_word.get("word", ""))
        else:
            self.spell_result_label.configure(
                text=f"❌ 错误！正确答案: {self.current_word.get('word', '')}",
                text_color=COLORS["accent_red"]
            )
            # 显示正确单词
            self.word_display.configure(text=self.current_word.get("word", ""))

        # 更新单词进度
        DataManager.update_word_progress(self.current_word["id"], is_correct)

        # 更新统计
        if is_correct:
            self.today_new_count += 1
        self.update_word_progress_display()

        # 延迟后显示下一个单词
        self.after(1200, self.next_word)

    def toggle_star_word(self):
        """收藏/取消收藏当前单词"""
        if not self.current_word:
            return

        DataManager.toggle_star_word(self.current_word["id"])

        # 更新按钮显示
        is_starred = self.current_word.get("starred", False)
        self.current_word["starred"] = not is_starred

        if self.current_word["starred"]:
            self.star_btn.configure(text="⭐ 已收藏", fg_color=COLORS["accent_yellow"], text_color="#000000")
        else:
            self.star_btn.configure(text="⭐ 收藏", fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"])

    def load_today_words(self):
        """加载今日学习单词（乱序）"""
        import random
        self.word_list = DataManager.get_today_words()
        if self.word_list:
            random.shuffle(self.word_list)  # 打乱顺序
            self.word_index = 0
            self.current_word = self.word_list[0]
        else:
            self.current_word = None

        self.card_flipped = False
        self.update_word_display()
        self.update_word_progress_display()

    def update_word_progress_display(self):
        """更新单词学习进度显示"""
        settings = DataManager.load_word_settings()
        daily_new = settings.get("daily_new_words", 30)
        daily_review = settings.get("daily_review_words", 50)

        self.word_progress_label.configure(
            text=f"今日: 新学 {self.today_new_count}/{daily_new}  复习 {self.today_review_count}/{daily_review}"
        )

    def show_wordbook_manager(self):
        """显示词库管理"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("词库管理")
        dialog.geometry("400x500")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.geometry(f"+{self.winfo_x() + 260}+{self.winfo_y() + 100}")

        ctk.CTkLabel(
            dialog,
            text="📚 词库管理",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["accent_blue"]
        ).pack(pady=(15, 10))

        # 导入词库按钮
        import_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_card"], corner_radius=10)
        import_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            import_frame,
            text="导入词库",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        btn_frame = ctk.CTkFrame(import_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkButton(
            btn_frame, text="导入 TXT", width=100, height=30,
            fg_color=COLORS["accent_blue"],
            command=lambda: self.import_words_file("txt")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="导入 CSV", width=100, height=30,
            fg_color=COLORS["accent_green"],
            command=lambda: self.import_words_file("csv")
        ).pack(side="left", padx=5)

        # 手动添加单词
        add_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_card"], corner_radius=10)
        add_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            add_frame,
            text="添加单词",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # 单词输入
        word_entry = ctk.CTkEntry(add_frame, placeholder_text="英文单词", fg_color=COLORS["bg_input"])
        word_entry.pack(fill="x", padx=15, pady=2)

        phonetic_entry = ctk.CTkEntry(add_frame, placeholder_text="音标 (可选)", fg_color=COLORS["bg_input"])
        phonetic_entry.pack(fill="x", padx=15, pady=2)

        meaning_entry = ctk.CTkEntry(add_frame, placeholder_text="中文释义", fg_color=COLORS["bg_input"])
        meaning_entry.pack(fill="x", padx=15, pady=2)

        example_entry = ctk.CTkEntry(add_frame, placeholder_text="例句 (可选)", fg_color=COLORS["bg_input"])
        example_entry.pack(fill="x", padx=15, pady=2)

        def add_word():
            word = word_entry.get().strip()
            meaning = meaning_entry.get().strip()
            if word and meaning:
                DataManager.add_word_manually(
                    word=word,
                    phonetic=phonetic_entry.get().strip(),
                    meaning=meaning,
                    example=example_entry.get().strip()
                )
                word_entry.delete(0, 'end')
                phonetic_entry.delete(0, 'end')
                meaning_entry.delete(0, 'end')
                example_entry.delete(0, 'end')
                self.load_today_words()

        ctk.CTkButton(
            add_frame, text="添加", width=80, height=30,
            fg_color=COLORS["accent_blue"],
            command=add_word
        ).pack(pady=10)

        # 词库统计
        stats_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_card"], corner_radius=10)
        stats_frame.pack(fill="x", padx=15, pady=10)

        words_data = DataManager.load_words()
        total_words = len(words_data.get("words", []))
        starred_words = sum(1 for w in words_data.get("words", []) if w.get("starred"))

        ctk.CTkLabel(
            stats_frame,
            text=f"词库统计: 共 {total_words} 个单词, 收藏 {starred_words} 个",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(pady=10)

    def import_words_file(self, file_type):
        """导入词库文件"""
        from tkinter import filedialog

        if file_type == "txt":
            filetypes = [("Text files", "*.txt")]
        else:
            filetypes = [("CSV files", "*.csv")]

        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            count = DataManager.import_words_from_file(filepath, file_type)
            self.load_today_words()
            # 显示导入结果
            print(f"成功导入 {count} 个单词")

    def show_word_stats(self):
        """显示单词学习统计"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("📊 单词学习统计")
        dialog.geometry("350x450")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.geometry(f"+{self.winfo_x() + 285}+{self.winfo_y() + 130}")

        ctk.CTkLabel(
            dialog,
            text="📊 单词学习统计",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["accent_blue"]
        ).pack(pady=(15, 10))

        # 加载统计数据
        words_data = DataManager.load_words()
        word_stats = DataManager.load_word_stats()
        today = DataManager.get_today_str()

        words = words_data.get("words", [])
        total_words = len(words)
        starred_words = sum(1 for w in words if w.get("starred"))
        mastered_words = sum(1 for w in words if w.get("level", 0) >= 4)
        learning_words = sum(1 for w in words if 0 < w.get("level", 0) < 4)
        new_words = sum(1 for w in words if w.get("level", 0) == 0)

        # 今日统计
        today_stats = word_stats.get("records", {}).get(today, {})
        today_reviewed = today_stats.get("reviewed", 0)
        today_correct = today_stats.get("correct", 0)
        today_wrong = today_stats.get("wrong", 0)
        accuracy = (today_correct / today_reviewed * 100) if today_reviewed > 0 else 0

        # 词库概览
        overview_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_card"], corner_radius=10)
        overview_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            overview_frame,
            text="📚 词库概览",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["accent_purple"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        stats_grid = ctk.CTkFrame(overview_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=15, pady=(0, 10))

        stats_items = [
            ("总单词", f"{total_words}", COLORS["accent_blue"]),
            ("已掌握", f"{mastered_words}", COLORS["accent_green"]),
            ("学习中", f"{learning_words}", COLORS["accent_yellow"]),
            ("未学习", f"{new_words}", COLORS["text_secondary"]),
        ]

        for i, (label, value, color) in enumerate(stats_items):
            item = ctk.CTkFrame(stats_grid, fg_color=COLORS["bg_input"], corner_radius=8)
            item.pack(side="left", expand=True, fill="x", padx=3)
            ctk.CTkLabel(item, text=value, font=ctk.CTkFont(size=16, weight="bold"),
                        text_color=color).pack(pady=(8, 2))
            ctk.CTkLabel(item, text=label, font=ctk.CTkFont(size=10),
                        text_color=COLORS["text_secondary"]).pack(pady=(0, 8))

        # 今日学习
        today_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_card"], corner_radius=10)
        today_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            today_frame,
            text="📅 今日学习",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["accent_green"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        today_info = ctk.CTkFrame(today_frame, fg_color="transparent")
        today_info.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(today_info, text=f"复习单词: {today_reviewed} 个",
                    text_color=COLORS["text_primary"]).pack(anchor="w", pady=2)
        ctk.CTkLabel(today_info, text=f"正确: {today_correct} 个 | 错误: {today_wrong} 个",
                    text_color=COLORS["text_primary"]).pack(anchor="w", pady=2)
        ctk.CTkLabel(today_info, text=f"正确率: {accuracy:.1f}%",
                    text_color=COLORS["accent_green"] if accuracy >= 80 else COLORS["accent_yellow"]).pack(anchor="w", pady=2)

        # 收藏统计
        star_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_card"], corner_radius=10)
        star_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            star_frame,
            text=f"⭐ 收藏单词: {starred_words} 个",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["accent_yellow"]
        ).pack(pady=10)

        # 关闭按钮
        ctk.CTkButton(
            dialog,
            text="关闭",
            width=100,
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=dialog.destroy
        ).pack(pady=10)

    def show_word_settings(self):
        """显示单词学习设置"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("学习设置")
        dialog.geometry("300x350")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.geometry(f"+{self.winfo_x() + 310}+{self.winfo_y() + 150}")

        ctk.CTkLabel(
            dialog,
            text="⚙ 学习设置",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["accent_blue"]
        ).pack(pady=(15, 15))

        settings = DataManager.load_word_settings()

        # 每日新学数量
        ctk.CTkLabel(dialog, text="每日新学单词数:", text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20)
        new_words_entry = ctk.CTkEntry(dialog, fg_color=COLORS["bg_input"])
        new_words_entry.insert(0, str(settings.get("daily_new_words", 30)))
        new_words_entry.pack(fill="x", padx=20, pady=5)

        # 每日复习数量
        ctk.CTkLabel(dialog, text="每日复习单词数:", text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20)
        review_words_entry = ctk.CTkEntry(dialog, fg_color=COLORS["bg_input"])
        review_words_entry.insert(0, str(settings.get("daily_review_words", 50)))
        review_words_entry.pack(fill="x", padx=20, pady=5)

        # 显示例句
        show_example_var = ctk.BooleanVar(value=settings.get("show_example", True))
        ctk.CTkCheckBox(
            dialog, text="显示例句",
            variable=show_example_var,
            fg_color=COLORS["accent_blue"]
        ).pack(anchor="w", padx=20, pady=10)

        def save_settings():
            try:
                new_settings = {
                    "daily_new_words": int(new_words_entry.get()),
                    "daily_review_words": int(review_words_entry.get()),
                    "show_example": show_example_var.get(),
                    "learning_mode": self.word_learning_mode,
                    "auto_play_sound": False
                }
                DataManager.save_word_settings(new_settings)
                self.update_word_progress_display()
                dialog.destroy()
            except ValueError:
                pass

        ctk.CTkButton(
            dialog, text="保存设置",
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=save_settings
        ).pack(pady=20)

    def create_main_page(self):
        """兼容旧版 - 重新创建主界面"""
        # 清空并重建界面
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.create_header()
        # 重新创建内容区域
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        # 左栏容器
        self.left_column = ctk.CTkFrame(self.content_frame, fg_color="transparent", width=410)
        self.left_column.pack(side="left", fill="both", padx=(0, 5))
        self.left_column.pack_propagate(False)
        # 右栏容器
        self.right_column = ctk.CTkFrame(self.content_frame, fg_color="transparent", width=490)
        self.right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))
        # 重建内容
        self.create_left_panel()
        self.create_word_panel()
        self.current_page = "main"

    def show_stats_page(self):
        """显示统计页面（弹窗形式）"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("📊 学习统计")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.geometry(f"+{self.winfo_x() + 210}+{self.winfo_y() + 60}")

        # ===== 顶部标题栏 =====
        header_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_card"], corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)

        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 学习统计",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["accent_blue"]
        )
        title_label.pack(side="left", padx=15, pady=10)

        # ===== 今日科目分布饼图 =====
        pie_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_card"], corner_radius=10)
        pie_frame.pack(fill="x", padx=10, pady=10)

        pie_title = ctk.CTkLabel(
            pie_frame,
            text="🥧 今日学习分布",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_purple"]
        )
        pie_title.pack(anchor="w", padx=15, pady=(10, 5))

        # 创建饼图
        self.create_pie_chart(pie_frame)

        # ===== 历史趋势折线图 =====
        line_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_card"], corner_radius=10)
        line_frame.pack(fill="both", expand=True, padx=10, pady=10)

        line_title = ctk.CTkLabel(
            line_frame,
            text="📈 近7天学习趋势",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["accent_green"]
        )
        line_title.pack(anchor="w", padx=15, pady=(10, 5))

        # 创建折线图
        self.create_line_chart(line_frame)

        # 关闭按钮
        ctk.CTkButton(
            dialog,
            text="关闭",
            width=100,
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=dialog.destroy
        ).pack(pady=10)

    def create_pie_chart(self, parent):
        """创建今日科目分布饼图"""
        stats = DataManager.get_today_stats()
        subjects_data = stats.get("subjects", {})

        fig, ax = plt.subplots(figsize=(4, 2.5), facecolor=COLORS["bg_card"])
        ax.set_facecolor(COLORS["bg_card"])

        if subjects_data and sum(subjects_data.values()) > 0:
            labels = list(subjects_data.keys())
            sizes = list(subjects_data.values())
            colors = CHART_COLORS[:len(labels)]

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct='%1.0f%%',
                colors=colors,
                textprops={'color': COLORS["text_primary"], 'fontsize': 9},
                pctdistance=0.75
            )

            for autotext in autotexts:
                autotext.set_color(COLORS["text_primary"])
                autotext.set_fontsize(8)
        else:
            ax.text(0.5, 0.5, "暂无数据", ha='center', va='center',
                   fontsize=14, color=COLORS["text_secondary"], transform=ax.transAxes)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=10)

    def create_line_chart(self, parent):
        """创建历史趋势折线图"""
        history = DataManager.get_history_stats(7)

        fig, ax = plt.subplots(figsize=(4, 3), facecolor=COLORS["bg_card"])
        ax.set_facecolor(COLORS["bg_card"])

        dates = [h["date"][-5:] for h in history]  # 只显示月-日
        totals = [h["total_time"] for h in history]

        ax.plot(dates, totals, marker='o', color=COLORS["accent_blue"],
                linewidth=2, markersize=6)
        ax.fill_between(dates, totals, alpha=0.3, color=COLORS["accent_blue"])

        ax.set_xlabel("日期", color=COLORS["text_secondary"], fontsize=10)
        ax.set_ylabel("学习时长(分钟)", color=COLORS["text_secondary"], fontsize=10)

        ax.tick_params(colors=COLORS["text_secondary"], labelsize=8)
        ax.spines['bottom'].set_color(COLORS["border"])
        ax.spines['left'].set_color(COLORS["border"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.grid(True, linestyle='--', alpha=0.3, color=COLORS["border"])

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def show_subject_manager(self):
        """显示科目管理对话框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("管理科目")
        dialog.geometry("300x400")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["bg_dark"])

        # 居中显示
        dialog.geometry(f"+{self.winfo_x() + 60}+{self.winfo_y() + 100}")

        # 标题
        ctk.CTkLabel(
            dialog,
            text="📚 科目管理",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["accent_blue"]
        ).pack(pady=(15, 10))

        # 添加新科目
        add_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        add_frame.pack(fill="x", padx=15, pady=5)

        new_subject_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="输入新科目名称",
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"]
        )
        new_subject_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def add_new_subject():
            name = new_subject_entry.get().strip()
            if name:
                DataManager.add_subject(name)
                new_subject_entry.delete(0, 'end')
                refresh_list()

        ctk.CTkButton(
            add_frame,
            text="添加",
            width=60,
            fg_color=COLORS["accent_green"],
            hover_color="#2ea043",
            command=add_new_subject
        ).pack(side="right")

        # 科目列表
        list_frame = ctk.CTkScrollableFrame(dialog, fg_color=COLORS["bg_card"])
        list_frame.pack(fill="both", expand=True, padx=15, pady=10)

        def refresh_list():
            for widget in list_frame.winfo_children():
                widget.destroy()

            subjects = DataManager.load_subjects()
            for subject in subjects:
                item_frame = ctk.CTkFrame(list_frame, fg_color=COLORS["bg_input"], corner_radius=5)
                item_frame.pack(fill="x", pady=2)

                ctk.CTkLabel(
                    item_frame,
                    text=subject,
                    text_color=COLORS["text_primary"]
                ).pack(side="left", padx=10, pady=5)

                if subject != "其他":
                    def delete_subject(s=subject):
                        DataManager.remove_subject(s)
                        refresh_list()

                    ctk.CTkButton(
                        item_frame,
                        text="×",
                        width=25,
                        height=25,
                        fg_color="transparent",
                        hover_color=COLORS["accent_red"],
                        command=delete_subject
                    ).pack(side="right", padx=5, pady=2)

        refresh_list()

        # 关闭按钮
        def on_close():
            # 更新下拉菜单
            subjects = DataManager.load_subjects()
            self.subject_menu.configure(values=subjects)
            self.track_subject_menu.configure(values=subjects)
            dialog.destroy()

        ctk.CTkButton(
            dialog,
            text="完成",
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=on_close
        ).pack(pady=15)

    def on_subject_change(self, value):
        """科目选择变更"""
        self.current_subject = value

    # ==================== 待办事项功能 ====================

    def load_todos(self):
        """加载并显示待办事项"""
        # 清空现有显示
        for widget in self.todos_scrollable.winfo_children():
            widget.destroy()

        data = DataManager.load_todos()
        today = DataManager.get_today_str()

        # 筛选今日待办
        today_todos = [t for t in data.get("todos", []) if t.get("date", today) == today]

        if not today_todos:
            empty_label = ctk.CTkLabel(
                self.todos_scrollable,
                text="暂无待办事项\n点击 [+ 添加] 创建新任务",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            )
            empty_label.pack(pady=30)
            return

        for todo in today_todos:
            self.create_todo_item(todo)

    def create_todo_item(self, todo):
        """创建单个待办事项控件"""
        is_completed = todo.get("completed", False)

        # 完成的待办整条变蓝色，未完成的是默认灰色
        if is_completed:
            frame_color = COLORS["accent_blue"]
            text_color = "#ffffff"  # 蓝色背景用白色文字
            del_btn_hover = "#3d8bff"
        else:
            frame_color = COLORS["bg_input"]
            text_color = COLORS["text_primary"]
            del_btn_hover = COLORS["accent_red"]

        frame = ctk.CTkFrame(self.todos_scrollable, fg_color=frame_color, corner_radius=8)
        frame.pack(fill="x", pady=3)

        # 复选框
        var = ctk.BooleanVar(value=is_completed)
        checkbox = ctk.CTkCheckBox(
            frame,
            text="",
            variable=var,
            width=24,
            fg_color=COLORS["accent_green"] if is_completed else COLORS["accent_blue"],
            hover_color=COLORS["accent_purple"],
            command=lambda t=todo, v=var: self.toggle_todo(t, v)
        )
        checkbox.pack(side="left", padx=(10, 5), pady=8)

        # 任务文字
        task_label = ctk.CTkLabel(
            frame,
            text=todo.get("text", ""),
            font=ctk.CTkFont(size=13),
            text_color=text_color,
            anchor="w"
        )
        task_label.pack(side="left", fill="x", expand=True, pady=8)

        # 删除按钮
        del_btn = ctk.CTkButton(
            frame,
            text="×",
            width=25,
            height=25,
            fg_color="transparent",
            hover_color=del_btn_hover,
            text_color=text_color,
            command=lambda t=todo: self.delete_todo(t)
        )
        del_btn.pack(side="right", padx=5, pady=5)

    def show_add_dialog(self):
        """显示添加任务对话框"""
        dialog = ctk.CTkInputDialog(
            text="输入任务内容：",
            title="添加待办"
        )
        result = dialog.get_input()
        if result:
            self.add_todo(result)

    def add_todo(self, text, date=None):
        """添加待办事项"""
        if date is None:
            date = DataManager.get_today_str()

        data = DataManager.load_todos()
        new_todo = {
            "id": int(time.time() * 1000),
            "text": text,
            "completed": False,
            "date": date,
            "created_at": datetime.now().isoformat()
        }
        data["todos"].append(new_todo)
        DataManager.save_todos(data)
        self.load_todos()

    def toggle_todo(self, todo, var):
        """切换待办完成状态"""
        data = DataManager.load_todos()
        new_state = var.get()

        for t in data["todos"]:
            if t["id"] == todo["id"]:
                t["completed"] = new_state
                # 根据新状态更新完成任务计数
                if new_state:
                    DataManager.add_completed_task()
                else:
                    DataManager.remove_completed_task()
                break

        DataManager.save_todos(data)
        self.load_todos()
        self.update_stats_display()

    def delete_todo(self, todo):
        """删除待办事项"""
        data = DataManager.load_todos()
        data["todos"] = [t for t in data["todos"] if t["id"] != todo["id"]]
        DataManager.save_todos(data)
        self.load_todos()

    # ==================== 番茄钟功能 ====================

    def toggle_pomodoro(self):
        """开始/暂停番茄钟"""
        if not self.pomodoro_running:
            self.start_pomodoro()
        else:
            self.pause_pomodoro()

    def start_pomodoro(self):
        """开始番茄钟"""
        self.pomodoro_running = True
        self.pomodoro_paused = False
        self.current_subject = self.subject_var.get()

        # 如果是新开始（不是继续），重置已记录分钟数
        if self.remaining_seconds == DEFAULT_FOCUS_TIME * 60:
            self.recorded_minutes = 0

        self.start_btn.configure(text="⏸ 暂停")

        if self.is_focus_time:
            self.status_label.configure(text=f"🔥 专注中 - {self.current_subject}",
                                        text_color=COLORS["accent_green"])
        else:
            self.status_label.configure(text="☕ 休息中...",
                                        text_color=COLORS["accent_yellow"])

        # 启动计时线程
        self.pomodoro_thread = Thread(target=self.pomodoro_countdown, daemon=True)
        self.pomodoro_thread.start()

    def pause_pomodoro(self):
        """暂停番茄钟"""
        self.pomodoro_paused = True
        self.pomodoro_running = False
        self.start_btn.configure(text="▶ 继续")
        self.status_label.configure(text="已暂停", text_color=COLORS["text_secondary"])

    def reset_pomodoro(self):
        """重置番茄钟"""
        self.pomodoro_running = False
        self.pomodoro_paused = False
        self.is_focus_time = True
        self.remaining_seconds = DEFAULT_FOCUS_TIME * 60
        self.recorded_minutes = 0  # 重置已记录分钟数
        self.update_timer_display()
        self.start_btn.configure(text="▶ 开始")
        self.status_label.configure(text="准备开始专注", text_color=COLORS["text_secondary"])

    def pomodoro_countdown(self):
        """番茄钟倒计时"""
        while self.remaining_seconds > 0 and self.pomodoro_running:
            time.sleep(1)
            if self.pomodoro_running:
                self.remaining_seconds -= 1
                self.after(0, self.update_timer_display)

                # 实时记录专注时长：每过1分钟记录一次（仅在专注时间）
                if self.is_focus_time:
                    elapsed_minutes = (DEFAULT_FOCUS_TIME * 60 - self.remaining_seconds) // 60
                    if elapsed_minutes > self.recorded_minutes:
                        # 新增了1分钟，记录它（不增加番茄数）
                        DataManager.add_focus_time(1, self.current_subject, add_pomodoro=False)
                        self.recorded_minutes = elapsed_minutes
                        self.after(0, self.update_stats_display)

        if self.remaining_seconds <= 0 and self.pomodoro_running:
            self.after(0, self.pomodoro_complete)

    def update_timer_display(self):
        """更新计时器显示"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")

        # 根据时间改变颜色
        if self.is_focus_time:
            if self.remaining_seconds < 60:
                self.timer_label.configure(text_color=COLORS["accent_red"])
            else:
                self.timer_label.configure(text_color=COLORS["accent_blue"])

    def pomodoro_complete(self):
        """番茄钟完成"""
        self.pomodoro_running = False

        # 播放提示音
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except:
            pass

        if self.is_focus_time:
            # 专注结束，只增加番茄数（时间已经实时记录了）
            self.add_pomodoro_count()
            self.update_stats_display()

            # 重置已记录分钟数，准备下一轮
            self.recorded_minutes = 0

            # 切换到休息
            self.is_focus_time = False
            self.remaining_seconds = DEFAULT_BREAK_TIME * 60
            self.status_label.configure(text="🎉 专注完成！休息一下吧",
                                        text_color=COLORS["accent_yellow"])
        else:
            # 休息结束，切换到专注
            self.is_focus_time = True
            self.remaining_seconds = DEFAULT_FOCUS_TIME * 60
            self.recorded_minutes = 0  # 重置已记录分钟数
            self.status_label.configure(text="☕ 休息结束！准备下一轮",
                                        text_color=COLORS["accent_blue"])

        self.update_timer_display()
        self.start_btn.configure(text="▶ 开始")

    def add_pomodoro_count(self):
        """仅增加番茄计数（不增加时间）"""
        records = DataManager.load_records()
        today = DataManager.get_today_str()
        if today not in records["records"]:
            records["records"][today] = {
                "total_time": 0,
                "completed_tasks": 0,
                "pomodoros": 0,
                "subjects": {}
            }
        records["records"][today]["pomodoros"] += 1
        DataManager.save_records(records)

    # ==================== 专注时长记录 ====================

    def toggle_focus_tracking(self):
        """切换专注记录状态"""
        if not self.focus_tracking:
            self.focus_tracking = True
            self.focus_start_time = datetime.now()
            self.tracking_subject = self.track_subject_var.get()
            self.focus_track_btn.configure(
                text=f"⏹ 停止记录 ({self.tracking_subject})",
                fg_color=COLORS["accent_red"],
                hover_color="#da3633"
            )
        else:
            self.focus_tracking = False
            if self.focus_start_time:
                # 计算专注时长
                duration = datetime.now() - self.focus_start_time
                minutes = int(duration.total_seconds() / 60)
                if minutes > 0:
                    DataManager.add_focus_time(minutes, self.tracking_subject)
                    self.update_stats_display()

            self.focus_start_time = None
            self.focus_track_btn.configure(
                text="⏱ 开始记录学习时长",
                fg_color=COLORS["accent_green"],
                hover_color="#2ea043"
            )

    # ==================== 统计显示 ====================

    def update_stats_display(self):
        """更新统计显示"""
        stats = DataManager.get_today_stats()
        self.focus_time_label.configure(text=f"{stats['focus_time']} 分钟")
        self.completed_label.configure(text=f"{stats['completed_tasks']} 个")
        self.pomodoro_count_label.configure(text=f"{stats['pomodoros']} 个")


# ==================== 程序入口 ====================
if __name__ == "__main__":
    app = StudyAssistantApp()
    app.mainloop()
