"""
待办事项列表组件
"""

import time
import customtkinter as ctk
from datetime import datetime
from config import COLORS
from models import TodoModel, RecordModel, BaseModel


class TodoList(ctk.CTkFrame):
    """待办事项列表组件"""

    def __init__(self, parent, on_stats_update=None, on_reminder_click=None, **kwargs):
        """初始化待办列表

        Args:
            parent: 父容器
            on_stats_update: 统计更新回调
            on_reminder_click: 提醒按钮点击回调，接收 todo 参数
        """
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=10, **kwargs)

        self._on_stats_update = on_stats_update
        self._on_reminder_click = on_reminder_click
        self._create_widgets()
        self.load_todos()

    def _create_widgets(self):
        """创建控件"""
        # 标题和添加按钮
        self.todos_header = ctk.CTkFrame(self, fg_color="transparent")
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
            self,
            fg_color="transparent",
            height=120
        )
        self.todos_scrollable.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def load_todos(self):
        """加载并显示待办事项"""
        # 清空现有显示
        for widget in self.todos_scrollable.winfo_children():
            widget.destroy()

        data = TodoModel.load_todos()
        today = BaseModel.get_today_str()

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
            self._create_todo_item(todo)

    def _create_todo_item(self, todo):
        """创建单个待办事项控件

        Args:
            todo: 待办事项数据
        """
        is_completed = todo.get("completed", False)
        has_reminder = bool(todo.get("reminder_time"))

        # 完成的待办整条变蓝色
        if is_completed:
            frame_color = COLORS["accent_blue"]
            text_color = "#ffffff"
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
            command=lambda t=todo, v=var: self._toggle_todo(t, v)
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
            command=lambda t=todo: self._delete_todo(t)
        )
        del_btn.pack(side="right", padx=5, pady=5)

        # 提醒按钮（未完成的任务才显示）
        if not is_completed:
            reminder_icon = "🔔" if has_reminder else "⏰"
            reminder_color = COLORS["accent_yellow"] if has_reminder else "transparent"
            reminder_btn = ctk.CTkButton(
                frame,
                text=reminder_icon,
                width=25,
                height=25,
                fg_color=reminder_color,
                hover_color=COLORS["accent_yellow"],
                text_color=text_color if not has_reminder else "#000000",
                command=lambda t=todo: self._on_reminder_btn_click(t)
            )
            reminder_btn.pack(side="right", padx=2, pady=5)

    def _on_reminder_btn_click(self, todo):
        """提醒按钮点击处理

        Args:
            todo: 待办事项数据
        """
        if self._on_reminder_click:
            self._on_reminder_click(todo)

    def show_add_dialog(self):
        """显示添加任务对话框"""
        dialog = ctk.CTkInputDialog(
            text="输入任务内容：",
            title="添加待办"
        )
        result = dialog.get_input()
        if result:
            self._add_todo(result)

    def _add_todo(self, text, date=None):
        """添加待办事项

        Args:
            text: 任务文本
            date: 日期（默认今天）
        """
        if date is None:
            date = BaseModel.get_today_str()

        data = TodoModel.load_todos()
        new_todo = {
            "id": int(time.time() * 1000),
            "text": text,
            "completed": False,
            "date": date,
            "created_at": datetime.now().isoformat(),
            "reminder_time": None
        }
        data["todos"].append(new_todo)
        TodoModel.save_todos(data)
        self.load_todos()

    def _toggle_todo(self, todo, var):
        """切换待办完成状态

        Args:
            todo: 待办事项数据
            var: 复选框变量
        """
        data = TodoModel.load_todos()
        new_state = var.get()

        for t in data["todos"]:
            if t["id"] == todo["id"]:
                t["completed"] = new_state
                # 根据新状态更新完成任务计数
                if new_state:
                    RecordModel.add_completed_task()
                else:
                    RecordModel.remove_completed_task()
                break

        TodoModel.save_todos(data)
        self.load_todos()

        if self._on_stats_update:
            self._on_stats_update()

    def _delete_todo(self, todo):
        """删除待办事项

        Args:
            todo: 待办事项数据
        """
        data = TodoModel.load_todos()
        data["todos"] = [t for t in data["todos"] if t["id"] != todo["id"]]
        TodoModel.save_todos(data)
        self.load_todos()
