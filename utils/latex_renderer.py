"""
LaTeX 渲染工具
使用 matplotlib 渲染数学公式
"""

import io
from PIL import Image, ImageTk
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 配置 matplotlib 支持中文和数学公式
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False
rcParams['mathtext.fontset'] = 'cm'  # Computer Modern 字体，更适合数学公式


class LaTeXRenderer:
    """LaTeX 公式渲染器"""

    # 缓存已渲染的图像
    _cache = {}
    _max_cache_size = 100

    @staticmethod
    def render_latex(latex_str, fontsize=16, dpi=150, text_color='black', bg_color='white'):
        """渲染 LaTeX 公式为图像

        Args:
            latex_str: LaTeX 公式字符串（不需要包含 $ 符号）
            fontsize: 字体大小
            dpi: 分辨率
            text_color: 文字颜色
            bg_color: 背景颜色

        Returns:
            PIL Image 对象
        """
        # 检查缓存
        cache_key = (latex_str, fontsize, dpi, text_color, bg_color)
        if cache_key in LaTeXRenderer._cache:
            return LaTeXRenderer._cache[cache_key]

        try:
            # 创建图形
            fig, ax = plt.subplots(figsize=(0.1, 0.1))
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)

            # 渲染公式
            # 如果公式不包含 $ 符号，自动添加
            if not latex_str.startswith('$'):
                latex_str = f'${latex_str}$'

            text = ax.text(0.5, 0.5, latex_str,
                          fontsize=fontsize,
                          color=text_color,
                          ha='center', va='center',
                          transform=ax.transAxes)

            ax.axis('off')

            # 调整图形大小以适应文本
            fig.canvas.draw()
            bbox = text.get_window_extent(renderer=fig.canvas.get_renderer())
            bbox = bbox.transformed(fig.dpi_scale_trans.inverted())

            # 添加边距
            pad = 0.1
            fig.set_size_inches(bbox.width + pad, bbox.height + pad)

            # 保存到内存
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=dpi,
                       bbox_inches='tight', pad_inches=0.05,
                       facecolor=bg_color, edgecolor='none')
            buf.seek(0)

            plt.close(fig)

            # 加载为 PIL Image
            img = Image.open(buf)
            img = img.convert('RGBA')

            # 缓存结果
            if len(LaTeXRenderer._cache) >= LaTeXRenderer._max_cache_size:
                # 清除一半缓存
                keys = list(LaTeXRenderer._cache.keys())
                for k in keys[:len(keys)//2]:
                    del LaTeXRenderer._cache[k]

            LaTeXRenderer._cache[cache_key] = img

            return img

        except Exception as e:
            print(f"LaTeX 渲染失败: {e}")
            # 返回错误提示图像
            return LaTeXRenderer._create_error_image(str(e), bg_color, text_color)

    @staticmethod
    def _create_error_image(error_msg, bg_color, text_color):
        """创建错误提示图像

        Args:
            error_msg: 错误信息
            bg_color: 背景颜色
            text_color: 文字颜色

        Returns:
            PIL Image 对象
        """
        fig, ax = plt.subplots(figsize=(3, 0.5))
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.text(0.5, 0.5, f"[公式渲染失败]",
               fontsize=12, color='red',
               ha='center', va='center',
               transform=ax.transAxes)
        ax.axis('off')

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100,
                   bbox_inches='tight', pad_inches=0.05,
                   facecolor=bg_color)
        buf.seek(0)
        plt.close(fig)

        img = Image.open(buf)
        return img.convert('RGBA')

    @staticmethod
    def render_to_tkimage(latex_str, fontsize=16, dpi=150, text_color='black', bg_color='white'):
        """渲染 LaTeX 公式为 Tkinter 可用的图像

        Args:
            latex_str: LaTeX 公式字符串
            fontsize: 字体大小
            dpi: 分辨率
            text_color: 文字颜色
            bg_color: 背景颜色

        Returns:
            ImageTk.PhotoImage 对象
        """
        img = LaTeXRenderer.render_latex(latex_str, fontsize, dpi, text_color, bg_color)
        return ImageTk.PhotoImage(img)

    @staticmethod
    def render_mixed_text(text, fontsize=14, dpi=150, text_color='black', bg_color='white'):
        """渲染混合文本（普通文本 + LaTeX 公式）

        公式用 $ 包裹，例如：求极限 $\\lim_{x \\to 0} \\frac{\\sin x}{x}$

        Args:
            text: 混合文本
            fontsize: 字体大小
            dpi: 分辨率
            text_color: 文字颜色
            bg_color: 背景颜色

        Returns:
            PIL Image 对象
        """
        try:
            fig, ax = plt.subplots(figsize=(0.1, 0.1))
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)

            # matplotlib 会自动处理 $ 包裹的公式
            text_obj = ax.text(0.5, 0.5, text,
                              fontsize=fontsize,
                              color=text_color,
                              ha='center', va='center',
                              transform=ax.transAxes,
                              wrap=True)

            ax.axis('off')

            # 调整大小
            fig.canvas.draw()
            bbox = text_obj.get_window_extent(renderer=fig.canvas.get_renderer())
            bbox = bbox.transformed(fig.dpi_scale_trans.inverted())

            pad = 0.2
            fig.set_size_inches(max(bbox.width + pad, 1), max(bbox.height + pad, 0.5))

            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=dpi,
                       bbox_inches='tight', pad_inches=0.1,
                       facecolor=bg_color, edgecolor='none')
            buf.seek(0)
            plt.close(fig)

            img = Image.open(buf)
            return img.convert('RGBA')

        except Exception as e:
            print(f"混合文本渲染失败: {e}")
            return LaTeXRenderer._create_error_image(str(e), bg_color, text_color)

    @staticmethod
    def clear_cache():
        """清除渲染缓存"""
        LaTeXRenderer._cache.clear()

    @staticmethod
    def get_theme_colors(is_dark=True):
        """获取主题对应的渲染颜色

        Args:
            is_dark: 是否深色主题

        Returns:
            (text_color, bg_color) 元组
        """
        if is_dark:
            return ('#e6edf3', '#161b22')  # 深色主题
        else:
            return ('#000000', '#f6f8fa')  # 浅色主题


# 常用公式模板
COMMON_FORMULAS = {
    "极限": {
        "重要极限1": r"\lim_{x \to 0} \frac{\sin x}{x} = 1",
        "重要极限2": r"\lim_{x \to \infty} \left(1 + \frac{1}{x}\right)^x = e",
        "等价无穷小": r"\sin x \sim x, \tan x \sim x, \ln(1+x) \sim x",
    },
    "导数": {
        "幂函数": r"(x^n)' = nx^{n-1}",
        "指数函数": r"(e^x)' = e^x, (a^x)' = a^x \ln a",
        "对数函数": r"(\ln x)' = \frac{1}{x}, (\log_a x)' = \frac{1}{x \ln a}",
        "三角函数": r"(\sin x)' = \cos x, (\cos x)' = -\sin x",
        "链式法则": r"[f(g(x))]' = f'(g(x)) \cdot g'(x)",
    },
    "积分": {
        "幂函数": r"\int x^n dx = \frac{x^{n+1}}{n+1} + C, (n \neq -1)",
        "指数函数": r"\int e^x dx = e^x + C",
        "三角函数": r"\int \sin x dx = -\cos x + C",
        "分部积分": r"\int u dv = uv - \int v du",
    },
    "线性代数": {
        "行列式": r"|A| = \sum_{j=1}^{n} a_{ij}A_{ij}",
        "逆矩阵": r"A^{-1} = \frac{1}{|A|} A^*",
        "特征值": r"Ax = \lambda x",
    },
    "概率": {
        "全概率公式": r"P(A) = \sum_{i=1}^{n} P(B_i)P(A|B_i)",
        "贝叶斯公式": r"P(B_i|A) = \frac{P(B_i)P(A|B_i)}{\sum_{j=1}^{n} P(B_j)P(A|B_j)}",
        "期望": r"E(X) = \sum_{i} x_i p_i \text{ 或 } \int_{-\infty}^{\infty} xf(x)dx",
        "方差": r"D(X) = E(X^2) - [E(X)]^2",
    }
}
