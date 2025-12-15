"""
对话框模块
"""

from .stats_dialog import StatsDialog
from .subject_dialog import SubjectDialog
from .wordbook_dialog import WordbookDialog
from .word_stats_dialog import WordStatsDialog
from .word_settings_dialog import WordSettingsDialog

__all__ = [
    'StatsDialog', 'SubjectDialog', 'WordbookDialog',
    'WordStatsDialog', 'WordSettingsDialog'
]
