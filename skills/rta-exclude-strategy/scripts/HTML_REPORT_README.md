# HTML Report Generator - 使用说明

## 功能概述

`html_report_generator.py` 将 RTA 排除策略的 Excel 报告转换为现代化、可交互的 HTML 格式。

## 核心特性

### 1. 视觉设计
- 固定左侧导航栏,渐变紫色背景
- 响应式布局,支持桌面和移动设备
- 现代 CSS 样式 (类似 Tailwind)
- 渐变色热力图,红色标记排除区域

### 2. 交互功能
- 平滑锚点滚动
- 表格列排序 (点击表头)
- 表格行悬停高亮
- 当前章节高亮

### 3. 报告结构
- **一、核心结论**: 关键指标对比
- **二、排除策略制定**: 现状与新策略
- **三、合理性评估**: 置入置出分析和交叉表

## 使用方���

### 基本用法

```python
from scripts.html_report_generator import generate_html_report

# result: 算法输出字典 (包含 df_combined, df_ctrl, exclude_region)
# old_exclude_rule: 老策略规则列表,如 ['01q', '02q', '03q']
file_path = generate_html_report(result, old_exclude_rule)
```

### 指定输出路径

```python
file_path = generate_html_report(
    result,
    old_exclude_rule,
    output_path='./reports'
)
```

## 输出文件

生成的 HTML 文件:
- 文件名格式: `RTA排除策略报告_{timestamp}.html`
- 自包含 (CSS 和 JavaScript 内嵌)
- 无需外部依赖,可直接在浏览器打开

## 测试

运行测试脚本:

```bash
python test_html_report.py
```

验证功能:

```bash
python verify_html.py
```

## 与 Excel 报告的对应关系

| Excel 功能 | HTML 实现 |
|-----------|----------|
| 章节标题 | H1/H2/H3 标签 + 锚点 |
| 表格 | `<table>` + 排序功能 |
| 红色填充 (排除区域) | `.excluded-cell` 类 + 渐变色 |
| 数字格式化 | `format_number()` / `format_percent()` |
| 热力图 | 渐变背景色 (绿/黄/橙/红) |

## 函数签名

```python
def generate_html_report(result, old_exclude_rule, output_path=None) -> str
```

**参数**:
- `result` (dict): 包含 `df_combined`, `df_ctrl`, `exclude_region`
- `old_exclude_rule` (list): 老策略规则,如 `['01q', '02q']`
- `output_path` (str, optional): 输出目录路径

**返回**:
- `str`: 生成的 HTML 文件绝对路径

## 浏览器兼容性

- Chrome/Edge: ✓ 完全支持
- Firefox: ✓ 完全支持
- Safari: ✓ 完全支持
- IE11: ✗ 不支持 (使用 CSS Grid 和现代 JavaScript)

## 打印支持

HTML 包含 `@media print` 样式,打印时:
- 自动隐藏侧边栏
- 内容区占满整页
- 保持表格和文本可读性
