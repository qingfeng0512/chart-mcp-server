#!/usr/bin/env python3
"""
图表MCP服务器 - 优雅版
提供多种图表生成功能，采用装饰器和主题系统设计
"""

import os
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from fastmcp import FastMCP

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建图像存储目录
IMAGES_DIR = Path(__file__).parent.parent / "images"
IMAGES_DIR.mkdir(exist_ok=True, parents=True)

# 创建MCP实例
app = FastMCP("chart-generator")


# ============================================================================
# 优雅颜色主题系统
# ============================================================================

class ColorTheme:
    """优雅的颜色主题系统"""

    # 主色调 - 海洋蓝系列
    PRIMARY = "#49bccf"
    SECONDARY = "#5cd4e5"
    ACCENT = "#2c8a99"

    # 补充色系
    WARM_RED = "#ff6b6b"
    SUNSET = "#ffd93d"
    FOREST = "#6bcf7f"
    PURPLE = "#a78bfa"

    # 中性色
    DARK = "#2d3748"
    GRAY = "#718096"
    LIGHT_GRAY = "#e2e8f0"
    WHITE = "#ffffff"

    # 渐变色系
    GRADIENT_BLUE = ["#49bccf", "#5cd4e5", "#7dd3fc", "#a78bfa"]
    GRADIENT_SUNSET = ["#ff6b6b", "#ff8e53", "#ffd93d", "#ffed4e"]

    # 优雅配色方案
    ELEGANT_PALETTES = {
        "ocean": {
            "primary": "#0066CC",
            "secondary": "#4A90E2",
            "accent": "#7BB3FF",
            "light": "#E6F2FF",
            "gradient": ["#0066CC", "#4A90E2", "#7BB3FF", "#A8CCFF", "#D4E6FF"]
        },
        "sunset": {
            "primary": "#FF6B6B",
            "secondary": "#FF8E53",
            "accent": "#FFB347",
            "light": "#FFF0E6",
            "gradient": ["#FF6B6B", "#FF8E53", "#FFB347", "#FFD166", "#FFE6A6"]
        },
        "forest": {
            "primary": "#2D6A4F",
            "secondary": "#52B788",
            "accent": "#95D5B2",
            "light": "#E9F5EC",
            "gradient": ["#2D6A4F", "#52B788", "#95D5B2", "#B7E4C7", "#D8F3DC"]
        },
        "violet": {
            "primary": "#5E60CE",
            "secondary": "#7B68EE",
            "accent": "#B4A7D6",
            "light": "#F0E6FF",
            "gradient": ["#5E60CE", "#7B68EE", "#9B7BD8", "#B4A7D6", "#D1C4E9"]
        },
        "coral": {
            "primary": "#FF7F7F",
            "secondary": "#FF9999",
            "accent": "#FFB3B3",
            "light": "#FFE6E6",
            "gradient": ["#FF7F7F", "#FF9999", "#FFB3B3", "#FFCCCC", "#FFE6E6"]
        }
    }

    # Plotly内置专业配色方案
    QUALITATIVE_SETS = {
        "elegant": px.colors.qualitative.Set3,
        "pastel": px.colors.qualitative.Pastel,
        "vivid": px.colors.qualitative.Vivid,
        "bold": px.colors.qualitative.Bold,
        "plotly": px.colors.qualitative.Plotly,
        "safari": px.colors.qualitative.Pastel,
        "alphabet": px.colors.qualitative.Alphabet
    }


def get_elegant_color(
    chart_type: str = None,
    palette_name: str = None,
    data_context: str = None
) -> dict:
    """
    智能选择优雅的颜色搭配

    Args:
        chart_type: 图表类型 (line, column, bar, area, pie, scatter, radar, dual_axes, etc.)
        palette_name: 指定调色板名称
        data_context: 数据上下文 (temperature, sales, progress, comparison, etc.)

    Returns:
        包含颜色信息的字典
    """
    # 默认调色板选择逻辑
    if not palette_name:
        if chart_type == "temperature" or data_context == "temperature":
            palette_name = "sunset"
        elif chart_type == "sales" or data_context == "sales":
            palette_name = "ocean"
        elif chart_type == "progress" or data_context == "progress":
            palette_name = "forest"
        elif chart_type == "comparison" or chart_type == "dual_axes":
            palette_name = "violet"
        else:
            # 根据图表类型智能选择
            palette_mapping = {
                "line": "ocean",
                "column": "ocean",
                "bar": "ocean",
                "area": "sunset",
                "pie": "coral",
                "scatter": "violet",
                "radar": "forest",
                "histogram": "ocean",
                "treemap": "sunset",
                "dual_axes": "violet"
            }
            palette_name = palette_mapping.get(chart_type, "ocean")

    palette = ColorTheme.ELEGANT_PALETTES.get(palette_name, ColorTheme.ELEGANT_PALETTES["ocean"])

    return {
        "primary": palette["primary"],
        "secondary": palette["secondary"],
        "accent": palette["accent"],
        "light": palette["light"],
        "gradient": palette["gradient"],
        "palette_name": palette_name
    }


def get_palette_colors(palette_name: str, count: int = 1) -> list:
    """
    从指定调色板获取颜色列表

    Args:
        palette_name: 调色板名称
        count: 需要的颜色数量

    Returns:
        颜色列表
    """
    palette = ColorTheme.ELEGANT_PALETTES.get(palette_name, ColorTheme.ELEGANT_PALETTES["ocean"])
    colors = palette["gradient"]

    # 如果需要的颜色超过调色板容量，循环使用
    if count > len(colors):
        extended_colors = []
        for i in range(count):
            extended_colors.append(colors[i % len(colors)])
        return extended_colors

    return colors[:count]


# ============================================================================
# 工具函数
# ============================================================================

def apply_elegant_coordinate_system(fig, grid_style: str = "dot"):
    """
    为图表应用优雅的坐标系统

    Args:
        fig: Plotly图表对象
        grid_style: 网格样式 (dot, dash, solid)
    """
    grid_configs = {
        "dot": {'griddash': 'dot', 'gridcolor': 'rgba(128,128,128,0.25)'},
        "dash": {'griddash': 'dash', 'gridcolor': 'rgba(128,128,128,0.3)'},
        "solid": {'griddash': 'solid', 'gridcolor': 'rgba(128,128,128,0.35)'}
    }

    fig.update_layout(
        xaxis=dict(
            showline=True,
            linewidth=2,
            linecolor=ColorTheme.DARK,
            showgrid=True,
            gridwidth=1,
            **grid_configs.get(grid_style, grid_configs["dot"]),
            showticklabels=True,
            tickfont=dict(size=12, color=ColorTheme.DARK),
            title=dict(font=dict(size=14, color=ColorTheme.DARK)),
            mirror=False,
            zeroline=True,
            zerolinecolor=ColorTheme.LIGHT_GRAY
        ),
        yaxis=dict(
            showline=True,
            linewidth=2,
            linecolor=ColorTheme.DARK,
            showgrid=True,
            gridwidth=1,
            **grid_configs.get(grid_style, grid_configs["dot"]),
            showticklabels=True,
            tickfont=dict(size=12, color=ColorTheme.DARK),
            title=dict(font=dict(size=14, color=ColorTheme.DARK)),
            mirror=False,
            zeroline=True,
            zerolinecolor=ColorTheme.LIGHT_GRAY
        ),
        plot_bgcolor=ColorTheme.WHITE,
        paper_bgcolor=ColorTheme.WHITE
    )


def apply_elegant_layout(fig, title: str, show_grid: bool = True):
    """
    应用优雅的图表布局

    Args:
        fig: Plotly图表对象
        title: 图表标题
        show_grid: 是否显示网格
    """
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=22, color=ColorTheme.DARK, family="Arial, sans-serif"),
            x=0.5,
            xanchor='center',
            y=0.95
        ),
        font=dict(family="Arial, sans-serif", color=ColorTheme.DARK),
        margin=dict(l=80, r=80, t=100, b=80),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor=ColorTheme.WHITE,
            bordercolor=ColorTheme.LIGHT_GRAY,
            borderwidth=1
        ),
        hovermode='x unified'
    )


def generate_unique_filename(chart_type: str = "chart", extension: str = "png") -> str:
    """生成唯一的文件名"""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4()).replace('-', '')[:9]
    return f"{chart_type}_{timestamp}_{unique_id}.{extension}"


def save_chart_as_image(fig, filename: str, width: int = 1400, height: int = 900, scale: float = 2) -> str:
    """保存图表为图像文件并返回路径"""
    filepath = IMAGES_DIR / filename
    fig.write_image(
        str(filepath),
        format="png",
        width=width,
        height=height,
        scale=scale
    )
    return str(filepath)


def generate_image_url(filepath: str) -> str:
    """生成图像的HTTP访问URL"""
    filename = os.path.basename(filepath)
    url = f"http://127.0.0.1:8081/{filename}"
    logger.info(f"生成图像URL: {url}")
    return url


# ============================================================================
# 装饰器：数据验证和解析
# ============================================================================

def validate_and_parse_data(required_fields: List[str] = None):
    """
    数据验证和解析装饰器

    Args:
        required_fields: 必需字段列表
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 处理data参数（如果存在）
                if 'data' in kwargs and kwargs['data'] is not None:
                    if isinstance(kwargs['data'], str):
                        try:
                            kwargs['data'] = json.loads(kwargs['data'])
                        except json.JSONDecodeError as e:
                            return {
                                "success": False,
                                "error": f"数据解析失败: {str(e)}"
                            }

                    # 如果是列表，转换为DataFrame
                    if isinstance(kwargs['data'], list):
                        kwargs['data'] = pd.DataFrame(kwargs['data'])

                # 处理words参数（词云图使用）
                if 'words' in kwargs and kwargs['words'] is not None:
                    if isinstance(kwargs['words'], str):
                        try:
                            kwargs['words'] = json.loads(kwargs['words'])
                        except json.JSONDecodeError as e:
                            return {
                                "success": False,
                                "error": f"词云数据解析失败: {str(e)}"
                            }

                # 验证必需字段
                if required_fields:
                    for field in required_fields:
                        if field not in kwargs:
                            return {
                                "success": False,
                                "error": f"参数 '{field}' 是必需的"
                            }
                        value = kwargs[field]
                        # 检查值是否为空
                        if value is None:
                            return {
                                "success": False,
                                "error": f"参数 '{field}' 不能为空"
                            }
                        # 如果是DataFrame，检查是否为空
                        if isinstance(value, pd.DataFrame) and value.empty:
                            return {
                                "success": False,
                                "error": f"参数 '{field}' 的数据不能为空"
                            }

                return func(*args, **kwargs)

            except Exception as e:
                logger.error(f"数据处理错误: {str(e)}")
                return {
                    "success": False,
                    "error": f"数据处理异常: {str(e)}"
                }
        return wrapper
    return decorator


# ============================================================================
# 图表生成函数
# ============================================================================

@app.tool()
@validate_and_parse_data(required_fields=['data', 'x_field', 'y_field'])
def generate_area_chart(
    data: Union[List[Dict], str],
    x_field: str,
    y_field: str,
    title: Optional[str] = "面积图",
    color: Optional[str] = None,
    palette: Optional[str] = None,
    data_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成优雅的面积图

    Args:
        data: 数据，可以是JSON字符串或字典列表
        x_field: X轴字段名
        y_field: Y轴字段名
        title: 图表标题
        color: 图表颜色（可选，默认自动选择优雅配色）
        palette: 指定调色板名称（可选）
        data_context: 数据上下文，用于智能配色（可选）

    Returns:
        包含图像URL的结果
    """
    logger.info(f"生成面积图: {title}")

    # 智能选择颜色
    if color is None:
        color_info = get_elegant_color("area", palette, data_context)
        color = color_info["primary"]

    # 创建面积图
    fig = px.area(
        data,
        x=x_field,
        y=y_field,
        title=title,
        color_discrete_sequence=[color]
    )

    # 应用优雅样式
    apply_elegant_layout(fig, title)
    apply_elegant_coordinate_system(fig, grid_style="dot")

    # 保存并返回
    filename = generate_unique_filename("area")
    filepath = save_chart_as_image(fig, filename)
    image_url = generate_image_url(filepath)

    return {
        "success": True,
        "image_url": image_url,
        "message": f"面积图生成成功：{title}"
    }


@app.tool()
@validate_and_parse_data(required_fields=['data', 'x_field', 'y_field'])
def generate_bar_chart(
    data: Union[List[Dict], str],
    x_field: str,
    y_field: str,
    title: Optional[str] = "条形图（水平）",
    color: Optional[str] = None,
    palette: Optional[str] = None,
    data_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成优雅的条形图（水平柱状图）

    Args:
        data: 数据，可以是JSON字符串或字典列表
        x_field: X轴字段名
        y_field: Y轴字段名
        title: 图表标题
        color: 图表颜色（可选，默认自动选择优雅配色）
        palette: 指定调色板名称（可选）
        data_context: 数据上下文，用于智能配色（可选）

    Returns:
        包含图像URL的结果
    """
    logger.info(f"生成条形图: {title}")

    # 智能选择颜色
    if color is None:
        color_info = get_elegant_color("bar", palette, data_context)
        color = color_info["primary"]

    fig = px.bar(
        data,
        x=x_field,
        y=y_field,
        title=title,
        color_discrete_sequence=[color],
        orientation='h'
    )

    apply_elegant_layout(fig, title)
    apply_elegant_coordinate_system(fig, grid_style="dash")

    filename = generate_unique_filename("bar")
    filepath = save_chart_as_image(fig, filename)
    image_url = generate_image_url(filepath)

    return {
        "success": True,
        "image_url": image_url,
        "message": f"条形图（水平）生成成功：{title}"
    }


@app.tool()
@validate_and_parse_data(required_fields=['data', 'x_field', 'y_field'])
def generate_column_chart(
    data: Union[List[Dict], str],
    x_field: str,
    y_field: str,
    title: Optional[str] = "柱状图（垂直）",
    color: Optional[str] = None,
    palette: Optional[str] = None,
    data_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成优雅的柱状图（垂直）

    Args:
        data: 数据，可以是JSON字符串或字典列表
        x_field: X轴字段名
        y_field: Y轴字段名
        title: 图表标题
        color: 图表颜色（可选，默认自动选择优雅配色）
        palette: 指定调色板名称（可选）
        data_context: 数据上下文，用于智能配色（可选）

    Returns:
        包含图像URL的结果
    """
    logger.info(f"生成柱状图: {title}")

    # 智能选择颜色
    if color is None:
        color_info = get_elegant_color("column", palette, data_context)
        color = color_info["primary"]

    fig = px.bar(
        data,
        x=x_field,
        y=y_field,
        title=title,
        color_discrete_sequence=[color]
    )

    apply_elegant_layout(fig, title)
    apply_elegant_coordinate_system(fig, grid_style="dot")

    filename = generate_unique_filename("column")
    filepath = save_chart_as_image(fig, filename)
    image_url = generate_image_url(filepath)

    return {
        "success": True,
        "image_url": image_url,
        "message": f"柱状图（垂直）生成成功：{title}"
    }


@app.tool()
@validate_and_parse_data(required_fields=['data', 'x_field', 'y1_field', 'y2_field'])
def generate_dual_axes_chart(
    data: Union[List[Dict], str],
    x_field: str,
    y1_field: str,
    y2_field: str,
    title: Optional[str] = "双轴图",
    color1: Optional[str] = None,
    color2: Optional[str] = None,
    palette: Optional[str] = None,
    data_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成优雅的双轴图表

    Args:
        data: 数据，可以是JSON字符串或字典列表
        x_field: X轴字段名
        y1_field: 第一个Y轴字段名
        y2_field: 第二个Y轴字段名
        title: 图表标题
        color1: 第一个Y轴颜色（可选，默认自动选择优雅配色）
        color2: 第二个Y轴颜色（可选，默认自动选择优雅配色）
        palette: 指定调色板名称（可选）
        data_context: 数据上下文，用于智能配色（可选）

    Returns:
        包含图像URL的结果
    """
    logger.info(f"生成双轴图: {title}")

    # 智能选择颜色
    if color1 is None or color2 is None:
        color_info = get_elegant_color("dual_axes", palette, data_context)
        if color1 is None:
            color1 = color_info["primary"]
        if color2 is None:
            color2 = color_info["secondary"]

    # 创建子图
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 添加第一个Y轴数据
    x_values = data[x_field].tolist() if isinstance(data, pd.DataFrame) else [row[x_field] for row in data]
    y1_values = data[y1_field].tolist() if isinstance(data, pd.DataFrame) else [row[y1_field] for row in data]
    y2_values = data[y2_field].tolist() if isinstance(data, pd.DataFrame) else [row[y2_field] for row in data]

    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y1_values,
            name=y1_field,
            line=dict(color=color1, width=3),
            fill='tozeroy',
            fillcolor=color1,
            opacity=0.3
        ),
        secondary_y=False,
    )

    # 添加第二个Y轴数据
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y2_values,
            name=y2_field,
            line=dict(color=color2, width=3)
        ),
        secondary_y=True,
    )

    # 设置Y轴标题
    fig.update_yaxes(title_text=y1_field, secondary_y=False, title=dict(font=dict(color=color1)))
    fig.update_yaxes(title_text=y2_field, secondary_y=True, title=dict(font=dict(color=color2)))

    apply_elegant_layout(fig, title)

    filename = generate_unique_filename("dual_axes")
    filepath = save_chart_as_image(fig, filename)
    image_url = generate_image_url(filepath)

    return {
        "success": True,
        "image_url": image_url,
        "message": f"双轴图生成成功：{title}"
    }


@app.tool()
def generate_fishbone_diagram(
    problem: str,
    causes: List[str],
    title: Optional[str] = "鱼骨图"
) -> Dict[str, Any]:
    """
    生成优雅的鱼骨图（因果图）

    Args:
        problem: 主要问题
        causes: 原因列表
        title: 图表标题

    Returns:
        包含图像URL的结果
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.patches import FancyBboxPatch

        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # 设置优雅的背景
        fig.patch.set_facecolor(ColorTheme.WHITE)
        ax.set_facecolor(ColorTheme.WHITE)

        # 绘制主骨（使用渐变色）
        ax.arrow(1, 5, 8, 0,
                head_width=0.25, head_length=0.4,
                fc=ColorTheme.PRIMARY, ec=ColorTheme.PRIMARY,
                linewidth=4, alpha=0.8)

        # 绘制鱼头
        head = patches.Polygon(
            [(9.5, 4.5), (11, 5), (9.5, 5.5)],
            closed=True, fill=True,
            facecolor=ColorTheme.PRIMARY,
            edgecolor=ColorTheme.ACCENT,
            linewidth=3
        )
        ax.add_patch(head)

        # 添加问题文本（带背景框）
        bbox_props = dict(boxstyle="round,pad=0.5",
                         facecolor=ColorTheme.SECONDARY,
                         edgecolor=ColorTheme.ACCENT,
                         linewidth=2,
                         alpha=0.9)
        ax.text(10.2, 5, problem, fontsize=18, fontweight='bold',
               color=ColorTheme.WHITE, ha='left', va='center',
               bbox=bbox_props)

        # 绘制上侧骨
        y_positions = [7, 8, 9]
        for i, cause in enumerate(causes[:3]):
            if i < len(y_positions):
                y = y_positions[i]
                # 主骨
                ax.plot([3, 7], [y, 5], color=ColorTheme.DARK, linewidth=2.5, alpha=0.7)
                # 分支骨
                ax.plot([7, 7.5], [5, y], color=ColorTheme.DARK, linewidth=2.5, alpha=0.7)

                # 原因文本框
                cause_bbox = dict(boxstyle="round,pad=0.4",
                                facecolor=ColorTheme.GRADIENT_BLUE[i % len(ColorTheme.GRADIENT_BLUE)],
                                edgecolor=ColorTheme.DARK,
                                linewidth=1.5,
                                alpha=0.9)
                ax.text(3.5, y, cause, fontsize=12, fontweight='bold',
                       color=ColorTheme.WHITE, ha='left', va='center',
                       bbox=cause_bbox)

        # 绘制下侧骨
        y_positions = [3, 2, 1]
        for i, cause in enumerate(causes[3:6]):
            if i < len(y_positions):
                y = y_positions[i]
                # 主骨
                ax.plot([3, 7], [y, 5], color=ColorTheme.DARK, linewidth=2.5, alpha=0.7)
                # 分支骨
                ax.plot([7, 7.5], [5, y], color=ColorTheme.DARK, linewidth=2.5, alpha=0.7)

                # 原因文本框
                cause_bbox = dict(boxstyle="round,pad=0.4",
                                facecolor=ColorTheme.GRADIENT_SUNSET[i % len(ColorTheme.GRADIENT_SUNSET)],
                                edgecolor=ColorTheme.DARK,
                                linewidth=1.5,
                                alpha=0.9)
                ax.text(3.5, y, cause, fontsize=12, fontweight='bold',
                       color=ColorTheme.WHITE, ha='left', va='center',
                       bbox=cause_bbox)

        # 添加标题
        plt.suptitle(title, fontsize=24, fontweight='bold',
                    color=ColorTheme.DARK, y=0.95)

        filename = generate_unique_filename("fishbone")
        filepath = IMAGES_DIR / filename
        plt.savefig(str(filepath), dpi=300, bbox_inches='tight',
                   facecolor=ColorTheme.WHITE, edgecolor='none')
        plt.close()

        image_url = generate_image_url(filepath)

        return {
            "success": True,
            "image_url": image_url,
            "message": f"鱼骨图生成成功：{title}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.tool()
def generate_flow_diagram(
    steps: List[Dict[str, str]],
    title: Optional[str] = "流程图"
) -> Dict[str, Any]:
    """
    生成优雅的流程图

    Args:
        steps: 流程步骤列表，每个步骤包含 'id', 'text', 'next' 字段
        title: 图表标题

    Returns:
        包含图像URL的结果
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.patches import FancyBboxPatch

        fig, ax = plt.subplots(1, 1, figsize=(14, 12))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 12)
        ax.axis('off')

        # 设置优雅的背景
        fig.patch.set_facecolor(ColorTheme.WHITE)
        ax.set_facecolor(ColorTheme.WHITE)

        # 绘制流程步骤
        y_pos = 10
        step_height = 1.2
        step_width = 6

        for i, step in enumerate(steps):
            text = step.get('text', f'步骤{i+1}')

            # 创建渐变色
            color_idx = i % len(ColorTheme.GRADIENT_BLUE)
            box_color = ColorTheme.GRADIENT_BLUE[color_idx]

            # 绘制圆角矩形
            box = FancyBboxPatch(
                (3, y_pos - step_height/2), step_width, step_height,
                boxstyle="round,pad=0.15",
                facecolor=box_color,
                edgecolor=ColorTheme.DARK,
                linewidth=2.5,
                alpha=0.9
            )
            ax.add_patch(box)

            # 添加文本
            ax.text(6, y_pos, text, ha='center', va='center',
                   fontsize=14, fontweight='bold',
                   color=ColorTheme.WHITE)

            # 绘制箭头
            if i < len(steps) - 1:
                arrow = patches.FancyArrowPatch(
                    (6, y_pos - step_height/2),
                    (6, y_pos - step_height/2 - 0.3),
                    arrowstyle='->',
                    mutation_scale=25,
                    color=ColorTheme.DARK,
                    linewidth=3,
                    alpha=0.8
                )
                ax.add_patch(arrow)

            y_pos -= step_height + 0.5

        # 添加标题
        plt.suptitle(title, fontsize=24, fontweight='bold',
                    color=ColorTheme.DARK, y=0.95)

        filename = generate_unique_filename("flow")
        filepath = IMAGES_DIR / filename
        plt.savefig(str(filepath), dpi=300, bbox_inches='tight',
                   facecolor=ColorTheme.WHITE, edgecolor='none')
        plt.close()

        image_url = generate_image_url(filepath)

        return {
            "success": True,
            "image_url": image_url,
            "message": f"流程图生成成功：{title}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.tool()
@validate_and_parse_data()
def generate_histogram_chart(
    data: Union[List[float], str],
    bins: Optional[int] = 30,
    title: Optional[str] = "直方图",
    color: Optional[str] = None,
    palette: Optional[str] = None,
    data_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成优雅的直方图

    Args:
        data: 数据列表或JSON字符串
        bins: 分箱数量
        title: 图表标题
        color: 图表颜色（可选，默认自动选择优雅配色）
        palette: 指定调色板名称（可选）
        data_context: 数据上下文，用于智能配色（可选）

    Returns:
        包含图像URL的结果
    """
    logger.info(f"生成直方图: {title}")

    # 智能选择颜色
    if color is None:
        color_info = get_elegant_color("histogram", palette, data_context)
        color = color_info["primary"]

    fig = px.histogram(
        x=data if isinstance(data, list) else data.iloc[:, 0],
        nbins=bins,
        title=title,
        color_discrete_sequence=[color]
    )

    apply_elegant_layout(fig, title)
    apply_elegant_coordinate_system(fig, grid_style="dash")

    filename = generate_unique_filename("histogram")
    filepath = save_chart_as_image(fig, filename)
    image_url = generate_image_url(filepath)

    return {
        "success": True,
        "image_url": image_url,
        "message": f"直方图生成成功：{title}"
    }


@app.tool()
@validate_and_parse_data(required_fields=['data', 'x_field', 'y_field'])
def generate_line_chart(
    data: Union[List[Dict], str],
    x_field: str,
    y_field: str,
    title: Optional[str] = "线图",
    color: Optional[str] = None,
    palette: Optional[str] = None,
    data_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成优雅的线图

    Args:
        data: 数据，可以是JSON字符串或字典列表
        x_field: X轴字段名
        y_field: Y轴字段名
        title: 图表标题
        color: 图表颜色（可选，默认自动选择优雅配色）
        palette: 指定调色板名称（可选）
        data_context: 数据上下文，用于智能配色（可选）

    Returns:
        包含图像URL的结果
    """
    logger.info(f"生成线图: {title}")

    # 智能选择颜色
    if color is None:
        color_info = get_elegant_color("line", palette, data_context)
        color = color_info["primary"]

    fig = px.line(
        data,
        x=x_field,
        y=y_field,
        title=title,
        color_discrete_sequence=[color]
    )

    fig.update_traces(
        line=dict(width=4, color=color),
        fill='tozeroy',
        fillcolor=color,
        opacity=0.3
    )

    apply_elegant_layout(fig, title)
    apply_elegant_coordinate_system(fig, grid_style="dot")

    filename = generate_unique_filename("line")
    filepath = save_chart_as_image(fig, filename)
    image_url = generate_image_url(filepath)

    return {
        "success": True,
        "image_url": image_url,
        "message": f"线图生成成功：{title}"
    }


@app.tool()
def generate_mind_map(
    topic: str,
    branches: List[str],
    title: Optional[str] = "思维导图"
) -> Dict[str, Any]:
    """
    生成优雅的思维导图

    Args:
        topic: 中心主题
        branches: 分支主题列表
        title: 图表标题

    Returns:
        包含图像URL的结果
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        ax.set_xlim(-12, 12)
        ax.set_ylim(-12, 12)
        ax.axis('off')

        # 设置优雅的背景
        fig.patch.set_facecolor(ColorTheme.WHITE)
        ax.set_facecolor(ColorTheme.WHITE)

        # 绘制中心节点（使用渐变效果）
        center_circle = plt.Circle((0, 0), 2, facecolor=ColorTheme.PRIMARY,
                                 edgecolor=ColorTheme.ACCENT, linewidth=4, alpha=0.9)
        ax.add_patch(center_circle)

        # 添加中心文本
        ax.text(0, 0, topic, ha='center', va='center', fontsize=20,
               fontweight='bold', color=ColorTheme.WHITE, wrap=True)

        # 绘制分支
        n_branches = len(branches)
        angles = np.linspace(0, 2 * np.pi, n_branches, endpoint=False)

        for i, (angle, branch) in enumerate(zip(angles, branches)):
            # 计算位置
            branch_dist = 6
            x = branch_dist * np.cos(angle)
            y = branch_dist * np.sin(angle)

            # 绘制连接线
            line = plt.Line2D([2 * np.cos(angle), x - 1.5 * np.cos(angle)],
                            [2 * np.sin(angle), y - 1.5 * np.sin(angle)],
                            color=ColorTheme.DARK, linewidth=3, alpha=0.7)
            ax.add_line(line)

            # 绘制分支节点（使用渐变色）
            branch_color = ColorTheme.GRADIENT_BLUE[i % len(ColorTheme.GRADIENT_BLUE)]
            branch_circle = plt.Circle((x, y), 1.5, facecolor=branch_color,
                                     edgecolor=ColorTheme.DARK, linewidth=2.5, alpha=0.9)
            ax.add_patch(branch_circle)

            # 添加分支文本
            ax.text(x, y, branch, ha='center', va='center', fontsize=13,
                   fontweight='bold', color=ColorTheme.WHITE, wrap=True)

        # 添加标题
        plt.suptitle(title, fontsize=26, fontweight='bold',
                    color=ColorTheme.DARK, y=0.95)

        filename = generate_unique_filename("mindmap")
        filepath = IMAGES_DIR / filename
        plt.savefig(str(filepath), dpi=300, bbox_inches='tight',
                   facecolor=ColorTheme.WHITE, edgecolor='none')
        plt.close()

        image_url = generate_image_url(filepath)

        return {
            "success": True,
            "image_url": image_url,
            "message": f"思维导图生成成功：{title}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.tool()
def generate_network_graph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    title: Optional[str] = "网络图"
) -> Dict[str, Any]:
    """
    生成优雅的网络图

    Args:
        nodes: 节点列表，每个节点包含 'id' 和 'label'
        edges: 边列表，每个边包含 'source' 和 'target'
        title: 图表标题

    Returns:
        包含图像URL的结果
    """
    try:
        import matplotlib.pyplot as plt
        import networkx as nx

        G = nx.Graph()

        # 添加节点
        for node in nodes:
            G.add_node(node['id'], label=node.get('label', node['id']))

        # 添加边
        for edge in edges:
            G.add_edge(edge['source'], edge['target'])

        plt.figure(figsize=(14, 12))
        fig, ax = plt.subplots(1, 1, figsize=(14, 12))

        # 设置背景
        fig.patch.set_facecolor(ColorTheme.WHITE)
        ax.set_facecolor(ColorTheme.WHITE)

        # 使用spring布局
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

        # 绘制边（使用优雅的样式）
        nx.draw_networkx_edges(G, pos, edge_color=ColorTheme.GRAY,
                             width=3, alpha=0.6, ax=ax)

        # 绘制节点（使用渐变色）
        node_colors = [ColorTheme.GRADIENT_BLUE[i % len(ColorTheme.GRADIENT_BLUE)]
                      for i in range(len(nodes))]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                             node_size=2000, alpha=0.9, ax=ax)

        # 绘制标签
        labels = {node['id']: node.get('label', node['id']) for node in nodes}
        nx.draw_networkx_labels(G, pos, labels, font_size=12,
                              font_weight='bold', font_color=ColorTheme.WHITE, ax=ax)

        # 添加标题
        plt.title(title, fontsize=24, fontweight='bold',
                 color=ColorTheme.DARK, pad=30)
        plt.axis('off')

        filename = generate_unique_filename("network")
        filepath = IMAGES_DIR / filename
        plt.savefig(str(filepath), dpi=300, bbox_inches='tight',
                   facecolor=ColorTheme.WHITE, edgecolor='none')
        plt.close()

        image_url = generate_image_url(filepath)

        return {
            "success": True,
            "image_url": image_url,
            "message": f"网络图生成成功：{title}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.tool()
@validate_and_parse_data(required_fields=['data', 'label_field', 'value_field'])
def generate_pie_chart(
    data: Union[List[Dict], str],
    label_field: str,
    value_field: str,
    title: Optional[str] = "饼图",
    color_scheme: Optional[str] = None,
    palette: Optional[str] = None,
    data_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成优雅的饼图

    Args:
        data: 数据，可以是JSON字符串或字典列表
        label_field: 标签字段名
        value_field: 数值字段名
        title: 图表标题
        color_scheme: 颜色方案（可选，默认自动选择优雅配色）
        palette: 指定调色板名称（可选）
        data_context: 数据上下文，用于智能配色（可选）

    Returns:
        包含图像URL的结果
    """
    logger.info(f"生成饼图: {title}")

    # 智能选择颜色
    if color_scheme is None and palette is None:
        color_info = get_elegant_color("pie", palette, data_context)
        colors = color_info["gradient"]
        palette_name = color_info["palette_name"]
    else:
        colors = ColorTheme.QUALITATIVE_SETS.get(color_scheme, ColorTheme.QUALITATIVE_SETS["elegant"])
        palette_name = color_scheme if color_scheme else "elegant"

    fig = px.pie(
        data,
        values=value_field,
        names=label_field,
        title=title,
        color_discrete_sequence=colors,
        hole=0.4  # 添加环形效果
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont=dict(size=14, color=ColorTheme.WHITE),
        marker=dict(line=dict(color=ColorTheme.WHITE, width=3))
    )

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=22, color=ColorTheme.DARK),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor=ColorTheme.WHITE,
        paper_bgcolor=ColorTheme.WHITE,
        font=dict(family="Arial, sans-serif", color=ColorTheme.DARK),
        margin=dict(l=80, r=80, t=120, b=80),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            bgcolor=ColorTheme.WHITE,
            bordercolor=ColorTheme.LIGHT_GRAY,
            borderwidth=1
        )
    )

    filename = generate_unique_filename("pie")
    filepath = save_chart_as_image(fig, filename)
    image_url = generate_image_url(filepath)

    return {
        "success": True,
        "image_url": image_url,
        "message": f"饼图生成成功：{title}"
    }


@app.tool()
@validate_and_parse_data(required_fields=['data', 'category_field', 'value_fields'])
def generate_radar_chart(
    data: Union[List[Dict], str],
    category_field: str,
    value_fields: List[str],
    title: Optional[str] = "雷达图",
    palette: Optional[str] = None,
    data_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成优雅的雷达图

    Args:
        data: 数据，可以是JSON字符串或字典列表
        category_field: 类别字段名
        value_fields: 数值字段名列表
        title: 图表标题
        palette: 指定调色板名称（可选）
        data_context: 数据上下文，用于智能配色（可选）

    Returns:
        包含图像URL的结果
    """
    logger.info(f"生成雷达图: {title}")

    # 智能选择颜色
    color_info = get_elegant_color("radar", palette, data_context)
    colors = color_info["gradient"]

    fig = go.Figure()

    for i, field in enumerate(value_fields):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=data[field],
            theta=data[category_field],
            fill='toself',
            name=field,
            line=dict(color=color, width=4),
            fillcolor=color,
            opacity=0.4
        ))

    max_value = max([data[field].max() for field in value_fields])

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_value],
                showline=True,
                linewidth=2,
                linecolor=ColorTheme.DARK,
                gridcolor=ColorTheme.LIGHT_GRAY,
                tickfont=dict(size=12, color=ColorTheme.DARK)
            ),
            angularaxis=dict(
                showline=True,
                linewidth=2,
                linecolor=ColorTheme.DARK,
                tickfont=dict(size=12, color=ColorTheme.DARK)
            )
        ),
        title=dict(
            text=title,
            font=dict(size=22, color=ColorTheme.DARK),
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        plot_bgcolor=ColorTheme.WHITE,
        paper_bgcolor=ColorTheme.WHITE,
        font=dict(family="Arial, sans-serif", color=ColorTheme.DARK),
        margin=dict(l=100, r=100, t=120, b=100)
    )

    filename = generate_unique_filename("radar")
    filepath = save_chart_as_image(fig, filename)
    image_url = generate_image_url(filepath)

    return {
        "success": True,
        "image_url": image_url,
        "message": f"雷达图生成成功：{title}"
    }


@app.tool()
@validate_and_parse_data(required_fields=['data', 'x_field', 'y_field'])
def generate_scatter_chart(
    data: Union[List[Dict], str],
    x_field: str,
    y_field: str,
    size_field: Optional[str] = None,
    color_field: Optional[str] = None,
    title: Optional[str] = "散点图",
    color: Optional[str] = None,
    palette: Optional[str] = None,
    data_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成优雅的散点图

    Args:
        data: 数据，可以是JSON字符串或字典列表
        x_field: X轴字段名
        y_field: Y轴字段名
        size_field: 大小字段名（可选）
        color_field: 颜色字段名（可选）
        title: 图表标题
        color: 图表颜色（可选，默认自动选择优雅配色）
        palette: 指定调色板名称（可选）
        data_context: 数据上下文，用于智能配色（可选）

    Returns:
        包含图像URL的结果
    """
    logger.info(f"生成散点图: {title}")

    # 智能选择颜色
    if color is None:
        color_info = get_elegant_color("scatter", palette, data_context)
        color = color_info["primary"]

    fig = px.scatter(
        data,
        x=x_field,
        y=y_field,
        size=size_field,
        color=color_field,
        title=title,
        color_continuous_scale="teal",
        size_max=30
    )

    fig.update_traces(
        marker=dict(
            line=dict(width=2, color=ColorTheme.WHITE),
            opacity=0.8
        )
    )

    apply_elegant_layout(fig, title)
    apply_elegant_coordinate_system(fig, grid_style="dash")

    filename = generate_unique_filename("scatter")
    filepath = save_chart_as_image(fig, filename)
    image_url = generate_image_url(filepath)

    return {
        "success": True,
        "image_url": image_url,
        "message": f"散点图生成成功：{title}"
    }


@app.tool()
@validate_and_parse_data(required_fields=['data', 'path_field', 'value_field'])
def generate_treemap_chart(
    data: Union[List[Dict], str],
    path_field: str,
    value_field: str,
    title: Optional[str] = "树形图"
) -> Dict[str, Any]:
    """
    生成优雅的树形图

    Args:
        data: 数据，可以是JSON字符串或字典列表
        path_field: 路径字段名
        value_field: 数值字段名
        title: 图表标题

    Returns:
        包含图像URL的结果
    """
    logger.info(f"生成树形图: {title}")

    fig = px.treemap(
        data,
        path=[path_field],
        values=value_field,
        title=title,
        color=value_field,
        color_continuous_scale='teal'
    )

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=22, color=ColorTheme.DARK),
            x=0.5,
            xanchor='center'
        ),
        plot_bgcolor=ColorTheme.WHITE,
        paper_bgcolor=ColorTheme.WHITE,
        font=dict(family="Arial, sans-serif", color=ColorTheme.DARK),
        margin=dict(l=50, r=50, t=100, b=50)
    )

    filename = generate_unique_filename("treemap")
    filepath = save_chart_as_image(fig, filename)
    image_url = generate_image_url(filepath)

    return {
        "success": True,
        "image_url": image_url,
        "message": f"树形图生成成功：{title}"
    }


@app.tool()
def generate_word_cloud_chart(
    words: List[Dict[str, Union[str, int]]],
    title: Optional[str] = "词云图"
) -> Dict[str, Any]:
    """
    生成优雅的词云图

    Args:
        words: 词频列表，每个词包含 'word' 和 'freq' 字段
        title: 图表标题

    Returns:
        包含图像URL的结果
    """
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt

        # 创建词频字典
        word_freq = {word['word']: word['freq'] for word in words}

        # 检查是否有中文字符
        has_chinese = any(ord(char) > 127 for word in word_freq.keys() for char in word)

        # 生成词云
        if has_chinese:
            import matplotlib.font_manager as fm

            font_path = None
            for font_name in ['SimHei', 'Microsoft YaHei', 'SimSun', 'DejaVu Sans', 'Arial Unicode MS']:
                try:
                    font_prop = fm.FontProperties(family=font_name)
                    font_path = fm.findfont(font_prop)
                    if font_path and ('Sim' in font_path or 'Hei' in font_path or 'YaHei' in font_path):
                        break
                except:
                    continue

            if not font_path:
                import platform
                system = platform.system()
                if system == 'Darwin':
                    font_path = '/System/Library/Fonts/PingFang.ttc'
                elif system == 'Windows':
                    font_path = 'C:/Windows/Fonts/simsun.ttc'
                else:
                    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

            wordcloud = WordCloud(
                width=1400,
                height=900,
                background_color=ColorTheme.WHITE,
                colormap='viridis',
                max_words=120,
                font_path=font_path if font_path and os.path.exists(font_path) else None,
                min_font_size=16,
                max_font_size=120,
                relative_scaling=0.5
            ).generate_from_frequencies(word_freq)
        else:
            wordcloud = WordCloud(
                width=1400,
                height=900,
                background_color=ColorTheme.WHITE,
                colormap='viridis',
                max_words=120,
                min_font_size=16,
                max_font_size=120,
                relative_scaling=0.5
            ).generate_from_frequencies(word_freq)

        plt.figure(figsize=(16, 12))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=26, fontweight='bold',
                 color=ColorTheme.DARK, pad=30)

        filename = generate_unique_filename("wordcloud")
        filepath = IMAGES_DIR / filename
        plt.savefig(str(filepath), dpi=300, bbox_inches='tight',
                   facecolor=ColorTheme.WHITE, edgecolor='none')
        plt.close()

        image_url = generate_image_url(filepath)

        return {
            "success": True,
            "image_url": image_url,
            "message": f"词云图生成成功：{title}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# 服务器启动
# ============================================================================

if __name__ == "__main__":
    # 配置MCP HTTP服务器
    app.settings.host = "127.0.0.1"
    app.settings.port = 8080
    app.settings.streamable_http_path = "/mcp"

    # 配置静态图像服务器
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import threading

    class ImageHTTPRequestHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(IMAGES_DIR), **kwargs)

        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()

        def log_message(self, format, *args):
            pass

        def do_GET(self):
            # 检查文件扩展名
            if not self.path.endswith('.png'):
                self.send_response(404)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write('<h1>404 Not Found</h1><p>请访问具体资源文件路径</p>'.encode('utf-8'))
                return

            # 允许访问 PNG 文件
            super().do_GET()

    def start_image_server():
        httpd = HTTPServer(("127.0.0.1", 8081), ImageHTTPRequestHandler)
        print(f"🖼️  静态文件服务器已启动: http://127.0.0.1:8081")
        httpd.serve_forever()

    # 启动静态图像服务器线程
    image_server_thread = threading.Thread(target=start_image_server, daemon=True)
    image_server_thread.start()

    # 运行MCP HTTP服务器
    print("🚀 启动优雅图表MCP服务器...")
    print(f"📡 MCP服务地址: http://127.0.0.1:8080/mcp")
    print(f"🖼️  图像访问地址: http://127.0.0.1:8081/chart_xxx.png")
    print("✨ 使用 Streamable HTTP 协议")
    print("🎨 采用优雅设计主题")
    print("=" * 60)

    try:
        app.run(transport="streamable-http")
    except KeyboardInterrupt:
        print("\n✅ 服务器已停止")
