---
name: monthly-report-html-generator
description: "从数据源自动生成月度运营数据 HTML 报告，支持 ECharts 图表、规则驱动结论、可折叠侧栏导航"
version: 1.1.0
---

# 月报 HTML 生成器

## Purpose

从 Excel/CSV/Dataphin 数据源自动生成交互式月度运营数据 HTML 报告。单一 Python 脚本读取所有数据 CSV，通过 f-string 模板直接生成完整 HTML（含 ECharts 图表 + 规则驱动结论 + 可折叠侧栏导航）。

## When to Activate

当用户需要生成月度运营数据报告时自动激活，特别适用于：
- 从数据仓库生成定期报告（Excel → CSV → HTML）
- 将 CSV 数据可视化为交互式网页
- 复刻 PPT 风格的数据报告为 HTML
- 需要自动生成数据结论的报告

## Architecture

### V04 架构（当前版本）

```
Input/rawdata.xlsx
    ↓ process_data.py（数据处理，产出 23 个 CSV）
Output/*.csv
    ↓ generate_html.py（单脚本，f-string 模板）
HTML/月报报告_{YYYYMMDD}_{HHMM}.html（自包含，仅依赖 CDN ECharts）
```

**核心设计决策**：
- **单文件输出**：HTML 自包含所有 CSS + JS + 数据，无外部依赖文件
- **ECharts 5.5.0**：CDN 加载 + fallback，替代 Chart.js
- **Python f-string 模板**：数据直接嵌入 JS 数组，无需中间 JSON
- **规则驱动结论**：基于环比计算自动生成，非 AI 生成

## Core Capabilities

### 1. 数据处理
- **多源数据读取**：支持 Excel (.xlsx)、CSV、Dataphin MCP 查询
- **数据校验**：自动检测字段缺失、数据类型错误
- **单位转换**：原始值 → 显示单位（÷1e8=亿, ÷1e4=万, ×100=%, ×1000=‰）
- **字段名兼容**：`get_month_col()` 处理 `month` / `date_month` 双命名
- **中间数据快照**：保存处理过程中的 CSV 快照用于调试和校验

### 2. 图表渲染（ECharts 5.5.0）
- **图表类型注册表**：
  - `stacked_bar_line`：堆叠柱状图 + 折线（交易额、花费）
  - `dual_line`：双折线图（CPS、转化漏斗）
  - `bar_multi_line`：柱状图 + 多折线（质量指标）
  - `dual_line_with_bar`：柱状图 + 双折线（渠道成本）
  - `single_line`：单折线（整体竞得率、转化率）
  - `multi_line_grouped`：多折线分组（分Q竞得率）
  - `stacked_column_chart`：堆叠柱状图（撞库数据）
- **数据标签**：全部图表默认启用
- **CDN + Fallback**：bootcdn 主加载 + jsdelivr 备用
- **自动 resize**：`window.addEventListener('resize')` 遍历所有图表实例

### 3. 规则驱动结论生成
- **环比计算引擎**：`_trend_word(cur, prev)` 返回方向词 + 变化幅度
- **14 个结论生成器**：每个报告板块一个专用函数
  - `gen_conclusion_scale()` — 规模（交易额 + 花费 + 最大客群）
  - `gen_conclusion_cost()` — 成本（全首借CPS + T0CPS）
  - `gen_conclusion_quality()` — 质量（额度 + 过件率）
  - `gen_conclusion_channel_overview()` — 渠道总览（日耗 + CPS + 额度 + 过件率）
  - `gen_conclusion_request()` — 请求（请求量 + 参竞率）
  - `gen_conclusion_winrate()` — 竞得率（整体 + 分Q）
  - `gen_conclusion_conversion()` — 转化（曝光-授信 + CTR + CVR）
  - `gen_conclusion_jz_attack()` — 精准撞库
  - `gen_conclusion_jz_conversion()` — 精准转化
- **输出格式**：`<strong>2月XX：</strong>指标A XX元，环比上升X%；`

### 4. 布局样式
- **深蓝主题排版**：
  - 标题色 #1a365d，边框色 #d5cec4
  - 结论框左蓝边 blockquote 样式
  - 图表容器白色卡片 + 圆角阴影
- **侧边栏导航**：3层级，点击跳转，折叠/展开动画
- **侧栏折叠按钮**：`toggleSidebar()` + CSS transition
- **动态居中**：`margin-left: max(260px, calc((100vw - 1200px) / 2))`
- **响应式设计**：小屏侧栏自适应 + 图表单列
- **可编辑内容**：`contenteditable="true"` 支持浏览器内编辑
- **HTML 导出**：内置导出按钮

## Workflow

### Step 1: 数据处理（process_data.py）
```python
# 读取源数据 Excel，处理并输出 CSV
import pandas as pd
raw = pd.read_excel('Input/rawdata.xlsx', sheet_name=None)
# 22+ 指标处理函数，产出 Output/*.csv
```

### Step 2: HTML 生成（generate_html.py）
```python
from datetime import datetime
import pandas as pd
from pathlib import Path

def build_html():
    # 1. 读取所有 CSV
    trade = pd.read_csv("Output/trade_by_group.csv")
    # ... 23 个 CSV

    # 2. 单位转换
    trade_total = to_js_array(trade["总计"] / 1e8, 2)  # 亿

    # 3. 生成结论
    concl_scale = gen_conclusion_scale(trade, spend)

    # 4. f-string 模板生成 HTML
    html = f'''<!DOCTYPE html>
    <html><head>
    <script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.5.0/echarts.min.js"></script>
    </head><body>
    <blockquote>{concl_scale}</blockquote>
    <div id="chart-trade"></div>
    <script>
    echarts.init(document.getElementById('chart-trade')).setOption({{
        xAxis: {{ data: {trade_months} }},
        series: [{{ data: {trade_total}, type: 'line' }}]
    }});
    </script>
    </body></html>'''

    # 5. 写入带时间戳的文件
    out = Path("HTML") / datetime.now().strftime("月报报告_%Y%m%d_%H%M.html")
    out.write_text(html, encoding="utf-8")
```

### Step 3: 数据准确性校验
```bash
# 对比 CSV 源数据与 HTML 内嵌数据
grep "trade_total" output.html  # 检查数值
# 对比 V01 PPT 数据确保一致
diff Output/trade_by_group.csv ../V01_PPT/Output/trade_by_group.csv
```

## Critical Lessons Learned

### 问题 1: 字段名不统一
**症状**：`KeyError: 'month'`
**根因**：`spend_by_channel.csv` 用 `date_month`，其他 CSV 用 `month`
**修复**：
```python
def get_month_col(df):
    for c in ["month", "date_month"]:
        if c in df.columns:
            return c
    raise ValueError(f"No month column: {list(df.columns)}")
```

### 问题 2: 微小值精度丢失
**症状**：抖音 CVR 全显示 0.0
**根因**：原始值 ~4.45e-5，×100=0.00445，round(2)=0.0
**修复**：
```python
# 对极小值指标使用更高精度
dy_cvf_cvr = to_js_array(dy_cv_f["CVR"] * 100, 4)  # 4位小数
```

### 问题 3: f-string 中调用不存在的函数
**症状**：`NameError: conv_overall_js is not defined`
**根因**：在 f-string 中引用了未定义的函数
**修复**：在 f-string 之前预计算所有变量
```python
# 预计算
tx_cvo_months_js = months_js(tx_cv_o)
# 然后在 f-string 中使用 {tx_cvo_months_js}
```

### 问题 4: 图表顶部被标题遮挡
**症状**：数据标签被 chart-title 文字框挡住
**根因**：`grid.top: 20` 太小
**修复**：全局改为 `grid.top: 45`

### 问题 5: 页面内容偏左不居中
**症状**：`margin-left: 260px; margin-right: auto` 无法居中
**根因**：固定左偏移 + auto 右边距只会左对齐
**修复**：
```css
/* 动态居中：宽屏居中，窄屏紧贴侧栏 */
#main-content {
    margin-left: max(260px, calc((100vw - 1200px) / 2));
    max-width: 1200px;
}
```

### 问题 6: 中文乱码（U+FFFD）
**症状**：`3.4 ��音转化`、`付��商店`
**根因**：文件编码错误或编辑器截断中文字符
**修复**：逐一搜索 `��` 并替换为正确中文

### 问题 7: 百分比精度不一致导致结论与图表矛盾
**症状**：JSON 数据显示环比 +0.1pp，但结论文本写 +0.03pp（3倍差距）；21 个数据点出现 WARN
**根因**：`_fmt_pct()` 使用"智能精度"（>10% 用1位小数，≤10% 用2位小数），导致 JSON 输出精度低于结论文本精度
**修复**：
```python
# 统一使用2位小数，避免 chart 数据与结论文案精度不一致
def _fmt_pct(v):
    return f"{v:.2f}"
```
**泛化规则**：所有百分比/千分比/比率类数据统一使用 2 位小数输出，包括日耗、日请求量、花费等金额类数据也应提升至 2 位小数

### 问题 8: JS 选择器与 HTML class 不匹配导致动态结论注入失败
**症状**：`setConclusions()` 的 `querySelectorAll` 返回空数组，所有动态结论静默失败
**根因**：charts.js 使用 `.conclusion-content` 选择器，但 HTML 中实际 class 为 `.conclusion-box`
**修复**：将 JS 选择器从 `.conclusion-content` 改为 `.conclusion-box`
**泛化规则**：JS/CSS 选择器修改时必须同步检查 HTML 中对应元素的 class/id 是否匹配

### 问题 9: 死代码 — JS 引用不存在的 canvas 元素
**症状**：`renderTradeByChannel()` 和 `renderTradeChange()` 引用 `chart-trade-by-channel` 和 `chart-trade-change`，但 HTML 中无对应 canvas
**根因**：HTML 重构时移除了 canvas 元素，但 charts.js 未同步清理
**修复**：从 charts.js 中移除死函数及其在 `initAllCharts` 中的调用
**泛化规则**：HTML 结构变更后必须 grep 检查 JS 中所有 `getElementById` / `querySelector` 引用是否仍然有效

## Quality Checklist

生成报告后必须验证：

- [ ] 脚本执行无报错（`python generate_html.py` 返回 [OK]）
- [ ] 零乱码字符（grep `��` 返回空）
- [ ] 所有图表正常渲染（23 个 ECharts 实例）
- [ ] 数据与源 CSV 精确一致
- [ ] 14 个结论区域全部填充（无 placeholder 文本）
- [ ] 侧边栏导航点击跳转正常
- [ ] 侧栏折叠/展开按钮正常
- [ ] 内容在宽屏居中显示
- [ ] 响应式布局在小屏正常
- [ ] 浏览器控制台无 JavaScript 错误
- [ ] contenteditable 功能正常
- [ ] 百分比/比率数据统一 2 位小数（`_fmt_pct` 输出与结论文案精度一致）
- [ ] JS 选择器与 HTML class/id 完全匹配（grep 交叉验证）
- [ ] 无死代码（JS 中所有 `getElementById`/`querySelector` 引用在 HTML 中存在）

## Output Structure

```
V04_HTMl/
├── generate_html.py           # 单脚本生成器（~1500行）
├── Input/
│   └── rawdata.xlsx           # 源数据
├── Output/
│   ├── trade_by_group.csv     # 23 个中间 CSV
│   ├── spend_by_channel.csv
│   └── ...
└── HTML/
    └── 月报报告_{YYYYMMDD}_{HHMM}.html  # 自包含输出
```

## Related Skills

- `/html-report-framework` - HTML 报告通用框架
- `/dp-explorer` - Dataphin 数据探索
- `/document-skills:xlsx` - Excel 数据处理

## Notes

- **ECharts 5.5.0**：CDN 双源加载，支持所有现代浏览器
- **文件命名**：自动加时间戳，避免覆盖历史版本
- **数据安全**：敏感数据内嵌 HTML 后注意分发范围
- **Windows 终端乱码**：Python print 中文路径在 GBK 终端显示异常，不影响 HTML 输出
