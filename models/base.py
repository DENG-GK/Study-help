"""
基础数据操作模块
"""

import json
import os
from datetime import datetime


class BaseModel:
    """基础数据模型 - 提供通用的JSON读写操作"""

    @staticmethod
    def load_json(filepath, default=None):
        """加载JSON文件

        Args:
            filepath: 文件路径
            default: 默认值（文件不存在或读取失败时返回）

        Returns:
            JSON数据或默认值
        """
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
        """保存JSON文件

        Args:
            filepath: 文件路径
            data: 要保存的数据
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存文件失败: {e}")

    @staticmethod
    def get_today_str():
        """获取今天的日期字符串

        Returns:
            格式为 'YYYY-MM-DD' 的日期字符串
        """
        return datetime.now().strftime("%Y-%m-%d")
