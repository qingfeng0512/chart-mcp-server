# 图表MCP服务器

一个基于 Model Context Protocol (MCP) 的图表生成服务器，提供15种不同类型的图表生成功能，支持AI智能配色和优雅设计。

复刻：https://www.modelscope.cn/mcp/servers/antvis/mcp-server-chart



## 功能特性

本服务器提供以下15种图表生成工具：

1. **generate_area_chart** - 生成面积图
2. **generate_bar_chart** - 生成柱状图（水平）
3. **generate_column_chart** - 生成柱状图（垂直）
4. **generate_dual_axes_chart** - 生成双轴图表
5. **generate_fishbone_diagram** - 生成鱼骨图（因果分析图）
6. **generate_flow_diagram** - 生成流程图
7. **generate_histogram_chart** - 生成直方图
8. **generate_line_chart** - 生成线图
9. **generate_mind_map** - 生成思维导图
10. **generate_network_graph** - 生成网络图
11. **generate_pie_chart** - 生成饼图
12. **generate_radar_chart** - 生成雷达图
13. **generate_scatter_chart** - 生成散点图
14. **generate_treemap_chart** - 生成树形图
15. **generate_word_cloud_chart** - 生成词云图

## 🎨 AI智能配色

- **自动配色**: AI根据图表类型和数据上下文自动选择优雅配色方案
- **主题系统**: 内置5种优雅配色主题（海洋蓝、日落、森林、紫色、珊瑚）
- **智能映射**: 不同类型的数据自动匹配最适合的颜色主题
- **自定义支持**: 可通过palette参数指定特定调色板

## 安装依赖

```bash
pip install -e .
```

或使用 pip 安装依赖：

```bash
pip install fastmcp plotly pandas kaleido pillow wordcloud matplotlib numpy
```

## 运行服务器

```bash
python src/main_optimized.py
```

## 使用示例

### 折线图（AI自动配色）

```python
data = [
    {"date": "12-17", "temperature": 5},
    {"date": "12-18", "temperature": 3},
    {"date": "12-19", "temperature": 2}
]

result = generate_line_chart(
    data=data,
    x_field="date",
    y_field="temperature",
    title="温度变化趋势"
)
```

### 柱状图（AI自动配色）

```python
data = [
    {"month": "1月", "sales": 120},
    {"month": "2月", "sales": 98},
    {"month": "3月", "sales": 145}
]

result = generate_column_chart(
    data=data,
    x_field="month",
    y_field="sales",
    title="月度销售额统计"
)
```

### 饼图（AI自动配色）

```python
data = [
    {"category": "移动端", "value": 45},
    {"category": "桌面端", "value": 30},
    {"category": "平板", "value": 15}
]

result = generate_pie_chart(
    data=data,
    label_field="category",
    value_field="value",
    title="市场份额分布"
)
```

### 双轴图（AI自动配色）

```python
data = [
    {"month": "1月", "revenue": 120, "users": 1000},
    {"month": "2月", "revenue": 150, "users": 1200},
    {"month": "3月", "revenue": 180, "users": 1500}
]

result = generate_dual_axes_chart(
    data=data,
    x_field="month",
    y1_field="revenue",
    y2_field="users",
    title="收入与用户增长对比"
)
```

## 输出说明

所有图表工具返回的结果格式如下：

```python
{
    "success": True,           # 是否成功
    "image_url": "http://127.0.0.1:8081/xxx.png", # 图像URL
    "message": "生成成功"       # 消息
}
```

如果生成失败：

```python
{
    "success": False,
    "error": "错误信息"
}
```

## 图像访问

- **静态文件服务器**: http://127.0.0.1:8081/
- **访问限制**: 仅允许访问.png格式文件
- **安全提示**: 访问非PNG文件将返回404错误

## 图像文件

- 所有生成的图像保存在 `images/` 目录中
- 文件名格式：`{chart_type}_YYYYMMDD_XXXXXXXX.png`
- 图像分辨率：1400x900，2倍缩放（高清晰度）

## 技术栈

- **FastMCP** - MCP服务器框架
- **Plotly** - 交互式图表库
- **Pandas** - 数据处理
- **Matplotlib** - 静态图表绘制
- **WordCloud** - 词云生成
- **NetworkX** - 网络图生成
- **Kaleido** - 图像导出引擎

## 设计特性

- **优雅边框**: 只显示左边和下边框，移除重复边框线
- **现代配色**: 采用现代UI设计趋势的配色方案
- **响应式布局**: 图表布局自适应不同数据量
- **高清晰度**: 2倍缩放确保在各种设备上清晰显示

## 注意事项

1. 确保已安装 `kaleido` 库，用于将 Plotly 图表导出为图像
2. 首次运行可能需要安装系统字体（用于 Matplotlib）
3. 图像文件会保存在 `images/` 目录中，请确保有写入权限
4. 服务器启动后会同时启动图像静态文件服务器（端口8081）

## 许可证

MIT License
