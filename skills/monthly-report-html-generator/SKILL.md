---
name: monthly-report-html-generator
description: 从数据源自动生成月度运营数据 HTML 报告，包含图表、结论、层级导航
triggers:
  - 月报
  - monthly report
  - html报告
  - 数据报告
  - 运营报告
argument-hint: <数据源路径> [配置文件]
quality: high
source: conversation
---

# 月报 HTML 生成器

## Purpose

从 Excel/CSV/Dataphin 数据源自动生成交互式月度运营数据 HTML 报告，支持图表渲染、结论生成、层级导航和可编辑内容。

## When to Activate

当用户需要生成月度运营数据报告时自动激活，特别适用于：
- 从数据仓库生成定期报告
- 将 Excel 数据可视化为网页
- 复刻 PPT 风格的数据报告为 HTML

## Core Capabilities

### 1. 数据处理
- **多源数据读取**：支持 Excel (.xlsx)、CSV、Dataphin MCP 查询
- **数据校验**：自动检测字段缺失、数据类型错误
- **数据转换**：聚合、透视、计算衍生指标
- **中间数据快照**：保存处理过程中的 CSV 快照用于调试

### 2. 图表渲染
- **Chart.js 集成**：支持柱状图、折线图、混合图、饼图、漏斗图
- **数据驱动**：图表配置从 JSON 文件加载
- **响应式布局**：单图居中80%、双图左右48%并列
- **自动初始化**：27+ 图表类型自动渲染

### 3. 内容生成
- **结论文本**：基于数据自动生成或手动输入
- **层级标题**：3级标题结构（一级章节 → 二级主题 → 三级细节）
- **可编辑内容**：`contenteditable="true"` 支持浏览器内编辑

### 4. 布局样式
- **PPT 风格排版**：
  - 棕色标题 (#8B4513)
  - 金色分隔线 (#DAA520)
  - 浅灰结论框 (#F5F5F5)
  - 结论 + 图表垂直布局
- **侧边栏导航**：3层级导航，点击跳转，当前章节高亮
- **响应式设计**：小屏自动隐藏侧边栏

## Workflow

### Step 1: 数据源分析
```bash
# 探索旧版数据处理逻辑
cd /path/to/legacy/report
python generate_report.py --dry-run  # 查看数据流程
```

**关键文件**：
- `generate_report.py` - 编排层入口
- `core/data_processor.py` - 22个 indicator builder
- `config/analysis_templates.py` - 分析模板和计算公式
- `Data/intermediate/legacy_logs/*.csv` - 中间快照

### Step 2: 数据提取与转换
```python
# 从 Excel 提取数据
import pandas as pd

data = pd.read_excel('source.xlsx', sheet_name='pivot')
charts_data = {
    'chart1': {
        'labels': data['month'].tolist(),
        'series': [{'name': '首借', 'data': data['首借'].tolist()}]
    }
}
# 保存为 JSON
import json
with open('data/report-data.json', 'w', encoding='utf-8') as f:
    json.dump(charts_data, f, indent=2, ensure_ascii=False)
```

### Step 3: HTML 结构生成
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>2026年3月 月度运营数据报告</title>
    <script src="./assets/chart.umd.min.js"></script>
    <script src="./assets/chartjs-plugin-datalabels.min.js"></script>
</head>
<body>
    <!-- 侧边栏导航 -->
    <nav id="sidebar-nav">
        <div class="nav-section">
            <a href="#section1" class="nav-l1">一、获客规模指标</a>
            <a href="#subsection1-1" class="nav-l2">1-7评级首借交易</a>
        </div>
    </nav>

    <!-- 主内容区 -->
    <main id="main-content">
        <section id="section1">
            <h2 contenteditable="true">一、获客规模指标</h2>
            <div class="conclusion-box" contenteditable="true">
                <p>2月交易总额4.80亿元，环比下降25.1%。</p>
            </div>
            <div class="charts-container">
                <canvas id="chart1"></canvas>
            </div>
        </section>
    </main>

    <script src="./data/report-data.js"></script>
    <script src="./charts.js"></script>
</body>
</html>
```

### Step 4: 图表初始化脚本
```javascript
// charts.js
function initAllCharts() {
    const charts = window.REPORT_DATA.charts;

    // 柱状图
    new Chart(document.getElementById('chart1'), {
        type: 'bar',
        data: {
            labels: charts.chart1.labels,
            datasets: charts.chart1.series.map(s => ({
                label: s.name,
                data: s.data,
                backgroundColor: s.color
            }))
        },
        options: {
            responsive: true,
            plugins: {
                datalabels: {
                    anchor: 'end',
                    align: 'top',
                    formatter: (value) => value.toFixed(2)
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', initAllCharts);
```

### Step 5: 数据准确性校验
```bash
# 对比新旧版数据
python verify_data.py \
    --old Data/intermediate/legacy_logs/20260304/*.csv \
    --new data/report-data.json

# 输出差异报告
✓ API回流 Feb-26: 0.0008 (一致)
✗ 1-3过件率 Feb-26: 8.4% (旧版) vs 7.4% (新版) - 偏差1pp
```

## Critical Lessons Learned

### 问题 1: 资源路径错误
**症状**：浏览器 404 错误，Chart.js 加载失败
**根因**：HTML 中使用 `../assets/` 而非 `./assets/`
**修复**：
```html
<!-- 错误 -->
<script src="../assets/chart.umd.min.js"></script>

<!-- 正确 -->
<script src="./assets/chart.umd.min.js"></script>
```

### 问题 2: 数据源混用
**症状**：同一页面图表数据不一致
**根因**：存在两个数据源（chart-data.json 手动OCR vs report-data.json 程序提取）
**修复**：
```bash
# 归档错误数据源
mv chart-data.json chart-data.json.bak

# 统一使用精确数据源
# charts.js 仅引用 data/report-data.js
```

### 问题 3: 图表未初始化
**症状**：Canvas 元素存在但无图表渲染
**根因**：charts.js 中仅初始化了 5/27 图表
**修复**：
```javascript
// 为所有 27 个 canvas 创建初始化函数
function initChart1() { /* ... */ }
function initChart2() { /* ... */ }
// ... 共 27 个

function initAllCharts() {
    initChart1();
    initChart2();
    // ...
}
```

### 问题 4: contenteditable 保存
**症状**：编辑后刷新页面内容丢失
**解决方案**：
- 方案 A：使用 localStorage 自动保存
- 方案 B：提示用户手动保存 HTML
- 方案 C：集成后端 API 持久化

本项目采用方案 B（简单可靠）。

## Input Parameters

```yaml
data_source:
  type: excel | csv | dataphin
  path: /path/to/source.xlsx
  sheet_name: pivot  # Excel 专用
  table_name: dwd.monthly_metrics  # Dataphin 专用

report_config:
  title: "2026年3月 月度运营数据报告"
  period:
    start: "2026-02-01"
    end: "2026-02-29"
  sections:
    - name: "获客规模指标"
      subsections:
        - title: "1-7评级首借交易"
          charts: [1]
        - title: "业务花费"
          charts: [2, 3]

style_theme: ppt  # 或 modern, minimal, dashboard
```

## Output Structure

```
output/
├── index.html              # 主报告文件
├── charts.js               # 图表渲染脚本
├── data/
│   ├── report-data.json    # 图表数据
│   └── report-data.js      # 浏览器版本
├── assets/
│   ├── chart.umd.min.js
│   └── chartjs-plugin-datalabels.min.js
├── LAYOUT_CHANGES.md       # 修改日志
└── VERIFICATION_REPORT.md  # 数据校验报告
```

## Usage Examples

### Example 1: 从 Excel 生成报告
```bash
/monthly-report-html-generator \
    --source monthly_data.xlsx \
    --sheet pivot \
    --output output/report.html
```

### Example 2: 从 Dataphin 生成报告
```bash
/monthly-report-html-generator \
    --source dataphin:dwd.monthly_metrics \
    --period 2026-02 \
    --template ppt
```

### Example 3: 复刻 PPT 排版
```bash
/monthly-report-html-generator \
    --source data.xlsx \
    --reference report.pptx \
    --output-dir monthly_report_v2/
```

## Quality Checklist

生成报告后必须验证：

- [ ] 所有图表正常渲染（无空白 canvas）
- [ ] 数据与源 Excel/CSV 精确一致
- [ ] 结论文本语法通顺、数据准确
- [ ] 侧边栏导航点击跳转正常
- [ ] contenteditable 功能正常
- [ ] 响应式布局在小屏正常
- [ ] 浏览器控制台无 JavaScript 错误
- [ ] 打印/PDF 导出格式正确

## Advanced Features

### 自动结论生成
```python
def generate_conclusion(data):
    """基于数据自动生成结论文本"""
    current = data['current_month']
    previous = data['previous_month']
    change = ((current - previous) / previous) * 100

    if change > 0:
        trend = f"环比增长{abs(change):.1f}%"
    else:
        trend = f"环比下降{abs(change):.1f}%"

    return f"本月总额{current:.2f}亿元，{trend}。"
```

### 数据血缘追踪
```bash
# 记录数据处理链路
数据源 → data_processor.py → CSV快照 → report-data.json → charts.js → 浏览器
```

## Related Skills

- `/dp-explorer` - Dataphin 数据探索
- `/frontend-design` - 前端界面优化
- `/document-skills:xlsx` - Excel 数据处理

## Notes

- **性能优化**：27+ 图表建议使用懒加��（滚动到可见区域再渲染）
- **数据安全**：敏感数据请勿直接内嵌 HTML，使用后端 API 动态加载
- **版本控制**：report-data.json 建议纳入 Git 管理，便于追踪数据变化
- **浏览器兼容**：Chart.js 4.x 不支持 IE11，建议 Chrome 90+ / Firefox 88+
