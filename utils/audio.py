"""
音频播放工具模块
"""

import os
from threading import Thread


def play_word_sound(word):
    """播放单词发音

    Args:
        word: 要播放发音的单词
    """
    if not word:
        return

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
            except ImportError:
                # 备用方案：使用系统命令
                os.startfile(temp_file)
        except Exception as e:
            print(f"播放发音失败: {e}")

    Thread(target=play, daemon=True).start()
