# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Chart MCP Server** - a Model Context Protocol server that provides 15 different types of chart generation capabilities with AI-powered smart color selection and elegant design. The server is built using FastMCP framework and generates high-quality charts using Plotly.

## Quick Start

### Running the Server

```bash
# Install dependencies
pip install -e .

# Or install manually
pip install fastmcp plotly pandas kaleido pillow wordcloud matplotlib numpy

# Start the server
python src/main_optimized.py
```

The server will start two services:
- **MCP Server**: http://127.0.0.1:8080/mcp
- **Static Image Server**: http://127.0.0.1:8081/ (PNG files only)

### Development Commands

```bash
# Format code
black src/
isort src/

# Run tests (if available)
pytest

# Install in development mode
pip install -e .
```

## Code Architecture

### Main Files

- **`src/main_optimized.py`** (1600 lines) - Main server file with all chart generation logic
- **`src/main.py`** - Backup copy of the main file
- **`images/`** - Directory for generated chart images
- **`README.md`** - Detailed documentation
- **`QUICKSTART.md`** - Quick start guide

### Core Components

#### 1. **ColorTheme System** (lines 38-110)
- Defines 5 elegant color palettes: ocean, sunset, forest, violet, coral
- Provides `get_elegant_color()` function for AI-powered color selection
- Maps chart types to appropriate color schemes automatically

#### 2. **15 Chart Generation Tools** (decorated with `@app.tool()`)
All tools are located in `src/main_optimized.py`:

1. `generate_area_chart()` - Area charts
2. `generate_bar_chart()` - Horizontal bar charts
3. `generate_column_chart()` - Vertical column charts
4. `generate_dual_axes_chart()` - Dual-axis charts
5. `generate_fishbone_diagram()` - Fishbone/Ishikawa diagrams
6. `generate_flow_diagram()` - Flow charts
7. `generate_histogram_chart()` - Histograms
8. `generate_line_chart()` - Line charts
9. `generate_mind_map()` - Mind maps
10. `generate_network_graph()` - Network graphs
11. `generate_pie_chart()` - Pie charts
12. `generate_radar_chart()` - Radar charts
13. `generate_scatter_chart()` - Scatter plots
14. `generate_treemap_chart()` - Treemap charts
15. `generate_word_cloud_chart()` - Word clouds

#### 3. **Decorator System** (lines 189-246)
- `validate_and_parse_data()` - Validates and parses input data
- Converts JSON strings to pandas DataFrames
- Handles empty/null value checks
- Manages error responses

#### 4. **Layout System** (lines 243-258)
- `apply_elegant_layout()` - Applies elegant chart layout
- `apply_elegant_coordinate_system()` - Configures axes with minimal borders (left and bottom only)
- Uses `mirror=False` to avoid duplicate border lines

#### 5. **Dual Server Architecture** (lines 1555-1600)
- **MCP Server** (port 8080) - Handles chart generation requests
- **Static File Server** (port 8081) - Serves generated PNG images
- Access control: Only `.png` files are allowed (returns 404 for others)

### AI Smart Color Selection

The system automatically selects colors based on:
- **Chart type**: Different chart types have default color schemes
- **Data context**: e.g., "temperature" → sunset palette, "sales" → ocean palette
- **Custom palette**: Can override with `palette` parameter
- **Custom color**: Can specify exact color with `color` parameter

Color palette mapping:
- Line/Column/Bar → ocean palette
- Area → sunset palette
- Pie → coral palette
- Scatter → violet palette
- Radar → forest palette
- Dual-axes → violet palette (with color variations)

### Key Functions

- `get_elegant_color()` - Smart color selection based on chart type and context
- `save_chart_as_image()` - Saves charts to PNG format with high resolution (1400x900, 2x scale)
- `generate_unique_filename()` - Creates unique filenames with timestamp and UUID
- `apply_elegant_coordinate_system()` - Configures minimal borders (left and bottom only)

## Data Formats

### Standard Chart Data
```python
data = [
    {"x_field": "value1", "y_field": 100},
    {"x_field": "value2", "y_field": 150}
]
```

### Pie Chart Data
```python
data = [
    {"label_field": "Category A", "value_field": 45},
    {"label_field": "Category B", "value_field": 30}
]
```

### Dual-Axis Chart Data
```python
data = [
    {"x_field": "Jan", "y1_field": 120, "y2_field": 1000},
    {"x_field": "Feb", "y1_field": 150, "y2_field": 1200}
]
```

## Design Principles

1. **Elegant Minimalism**: Charts use only left and bottom borders, no duplicate lines
2. **AI-Powered Aesthetics**: Automatic color selection based on data type and context
3. **High Quality Output**: 2x scale rendering for crisp display on all devices
4. **Security**: Strict access control for generated files
5. **Modularity**: Each chart type is a separate, self-contained function
6. **Consistency**: All charts use the same elegant layout system

## Dependencies

Core dependencies from `requirements.txt`:
- `fastmcp>=0.1.0` - MCP server framework
- `plotly>=5.18.0` - Chart rendering
- `pandas>=2.0.0` - Data processing
- `kaleido>=0.2.1` - Image export engine
- `matplotlib>=3.7.0` - Static chart rendering
- `wordcloud>=1.9.0` - Word cloud generation
- `networkx>=3.0` - Network graph generation
- Additional: numpy, scipy, scikit-learn, pillow, pyecharts

## Common Development Tasks

### Adding a New Chart Type

1. Create a new function with `@app.tool()` decorator
2. Use `validate_and_parse_data()` for data validation
3. Call `apply_elegant_layout()` and `apply_elegant_coordinate_system()`
4. Use `get_elegant_color()` for automatic color selection
5. Save with `save_chart_as_image()` and return URL

### Modifying Color Schemes

Edit the `ColorTheme.ELEGANT_PALETTES` dictionary (lines 62-98). Each palette should include:
- `primary` - Main color
- `secondary` - Secondary color
- `accent` - Accent color
- `light` - Light variant
- `gradient` - Array of gradient colors

### Customizing Layout

Modify `apply_elegant_coordinate_system()` (lines 206-240) to change:
- Border styles
- Grid configuration
- Font sizes
- Axis properties

## Important Implementation Details

1. **File Access Control**: The static file server only allows `.png` files. Other files return 404 with Chinese message "请访问具体资源文件路径"

2. **Border Rendering**: Uses `mirror=False` to avoid duplicate border lines on right and top edges

3. **DataFrame Handling**: The decorator converts list data to pandas DataFrames automatically

4. **Error Handling**: All functions return consistent error format:
   ```python
   {"success": False, "error": "error message"}
   ```

5. **Image Resolution**: All charts are rendered at 1400x900 pixels with 2x scale for high DPI displays

6. **Threading**: The static file server runs in a daemon thread and starts automatically when the MCP server starts

## Testing

When the server is running, you can test chart generation by calling any of the 15 tools. Example:

```python
result = generate_line_chart(
    data=[{"date": "12-17", "temperature": 5}],
    x_field="date",
    y_field="temperature",
    title="Temperature Trend"
)
```

Check `result["image_url"]` for the generated PNG file URL.
