# HTML Report Framework — 组件参考 (Architecture Reference)

> 本文件包含所有核心模块的完整 CSS/JS 代码示例，是 `SKILL.md` 的详细技术附录。
> 日常使用时请直接从 `resources/starter-template.html` 复制骨架，此文件用于查阅组件实现细节。

---

## Core Module 1: CSS 变量设计系统

所有颜色通过 CSS 变量管理，一处修改全局生效：

```css
:root {
  /* 主色 */
  --primary: #1a365d;
  --accent: #2b6cb0;
  --accent-light: #4299e1;
  --accent-bg: #ebf8ff;
  /* 语义色 */
  --success: #276749;
  --success-bg: #f0fff4;
  --warning: #744210;
  --warning-bg: #fffbeb;
  --danger: #9b2c2c;
  --danger-bg: #fff5f5;
  /* 灰阶 */
  --gray-50: #f7fafc;
  --gray-100: #edf2f7;
  --gray-200: #e2e8f0;
  --gray-400: #a0aec0;
  --gray-600: #718096;
  --gray-800: #2d3748;
  --border: #e2e8f0;
  /* 布局 */
  --sidebar-width: 260px;
  --header-height: 64px;
}
```

**主题切换**：只需替换 `:root` 变量值即可全局换肤：
- `deepBlue`（默认）：`--primary: #1a365d; --accent: #2b6cb0`
- `ppt`：`--primary: #8B4513; --accent: #DAA520`
- `modern`：`--primary: #1677ff; --accent: #40a9ff`

---

## Core Module 2: 专业组件库

以下组件从高质量 SOP 文档中提炼，直接复制到 section-body 中使用：

### 信息提示框 (Callout)
```html
<div class="callout info"><span class="callout-icon">💡</span>
  <div class="callout-body"><div class="callout-title">提示标题</div><p>内容</p></div>
</div>
<!-- 变体：info(蓝) / warning(黄) / success(绿) / danger(红) -->
```
```css
.callout { border-radius: 6px; padding: 14px 16px; margin: 16px 0; display: flex; gap: 12px; }
.callout.info { background: var(--accent-bg); border-left: 4px solid var(--accent); color: var(--primary); }
.callout.warning { background: var(--warning-bg); border-left: 4px solid #d69e2e; color: var(--warning); }
.callout.success { background: var(--success-bg); border-left: 4px solid #38a169; color: var(--success); }
.callout.danger { background: var(--danger-bg); border-left: 4px solid #e53e3e; color: var(--danger); }
.callout-icon { font-size: 18px; flex-shrink: 0; } .callout-title { font-weight: 700; font-size: 13px; }
```

### 指标卡片 (Metric Card)
```html
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-label">COST PER MILLE</div>
    <div class="metric-abbr">CPM</div>
    <div class="metric-desc">千次展示成本</div>
  </div>
</div>
```
```css
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; }
.metric-card { background: linear-gradient(135deg, var(--primary), var(--accent)); color: #fff; border-radius: 8px; padding: 16px; }
.metric-label { font-size: 11px; opacity: .8; text-transform: uppercase; letter-spacing: .05em; }
.metric-abbr { font-size: 20px; font-weight: 800; } .metric-desc { font-size: 11px; opacity: .75; }
```

### 结构化信息卡 (Info Card)
```html
<div class="info-card">
  <div class="info-card-title">📊 表名</div>
  <div class="info-row"><div class="info-label">主键</div><div class="info-value">字段名</div></div>
  <div class="info-row"><div class="info-label">更新频率</div><div class="info-value">每日 T+1</div></div>
</div>
```
```css
.info-card { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin: 16px 0; }
.info-card-title { background: var(--gray-100); padding: 12px 16px; font-weight: 700; }
.info-row { display: grid; grid-template-columns: 120px 1fr; border-bottom: 1px solid var(--border); }
.info-label { background: var(--gray-50); padding: 9px 14px; font-weight: 700; font-size: 12px; border-right: 1px solid var(--border); }
.info-value { padding: 9px 14px; font-size: 13px; }
```

### 流程图 (Flow Diagram)
```html
<div class="flow-diagram">
  <div class="flow-box terminal">开始</div>
  <span class="flow-arrow">→</span>
  <div class="flow-box highlight">关键步骤</div>
  <span class="flow-arrow">→</span>
  <div class="flow-box decision">判断</div>
  <span class="flow-arrow">→</span>
  <div class="flow-box terminal">结束</div>
</div>
<!-- terminal=深蓝圆角 highlight=蓝色高亮 decision=黄色判断 -->
```
```css
.flow-diagram { display: flex; align-items: center; gap: 0; margin: 20px 0; flex-wrap: wrap; justify-content: center; }
.flow-box { padding: 12px 16px; border-radius: 8px; text-align: center; font-size: 12px; font-weight: 600; border: 2px solid var(--border); }
.flow-box.terminal { background: var(--primary); color: #fff; border-color: var(--primary); border-radius: 20px; }
.flow-box.highlight { background: var(--accent-bg); border-color: var(--accent); color: var(--accent); }
.flow-box.decision { background: var(--warning-bg); border-color: #f6e05e; color: var(--warning); }
.flow-arrow { padding: 0 8px; color: var(--gray-400); font-size: 18px; }
```

### 数据链路 (Chain Pipeline)
```html
<div class="chain-container">
  <div class="chain-node"><div class="chain-box"><div class="chain-abbr">曝光</div></div></div>
  <div class="chain-arrow">→</div>
  <div class="chain-node"><div class="chain-box chain-box-green"><div class="chain-abbr">授信</div></div></div>
  <div class="chain-arrow">→</div>
  <div class="chain-node"><div class="chain-box chain-box-amber"><div class="chain-abbr">动支</div></div></div>
</div>
```
```css
.chain-container { display: flex; align-items: stretch; margin: 20px 0; justify-content: center; }
.chain-box { background: linear-gradient(135deg, var(--primary), var(--accent)); color: #fff; border-radius: 8px; padding: 12px 16px; text-align: center; }
.chain-box-green { background: linear-gradient(135deg, #276749, #38a169); }
.chain-box-amber { background: linear-gradient(135deg, #744210, #b7791f); }
.chain-abbr { font-size: 16px; font-weight: 800; }
.chain-arrow { display: flex; align-items: center; padding: 0 8px; color: var(--gray-400); font-size: 20px; }
```

### 更多组件速查

| 组件 | 用途 | 关键 CSS |
|------|------|---------|
| `.def-grid` + `.def-card` | 并列概念对比（顶部色条区分） | `grid-template-columns: 1fr 1fr; border-top: 3px solid var(--accent)` |
| `.formula-block` | 暗色背景公式展示 | `background: #1e2d40; .f-result{#68d391} .f-var{#fbd38d}` |
| `.timeline` + `.tl-item` | 版本/时间线（active/inactive 圆点） | `::before 垂直线, .tl-dot border-radius: 50%` |
| `.vflow` + `.vflow-dot` | 垂直流程（带连接线） | `.vflow-line{width:2px; flex:1; background:var(--gray-200)}` |
| `<details class="collapsible">` | 可折叠详情（原生，无需JS） | `summary 样式化, [open] summary border-bottom` |
| `.compare-table .pro/.con` | 对比表（文字颜色区分优劣） | `.pro{color:var(--success)} .con{color:var(--danger)}` |
| `.checklist` + `<input checkbox>` | 交互检查清单（checked 划线变灰） | `:checked + label{text-decoration: line-through}` |

---

## Core Module 3: 渐变色 Section 头部

每个 section 使用带编号圆圈的渐变头部，比纯文字标题更专业：

```html
<div class="section">
  <div class="section-header">
    <div class="section-number">1</div>
    <div><div class="section-title">章节标题</div>
         <div class="section-subtitle">English Subtitle</div></div>
  </div>
  <div class="section-body"><!-- 内容 --></div>
</div>
```
```css
.section { background: #fff; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 28px; }
.section-header { background: linear-gradient(135deg, var(--primary), var(--accent)); color: #fff; padding: 16px 24px; display: flex; align-items: center; gap: 12px; }
.section-number { background: rgba(255,255,255,.2); border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.section-title { font-size: 16px; font-weight: 700; } .section-subtitle { font-size: 12px; opacity: .75; }
.section-body { padding: 24px; }
```

---

## Core Module 4: 微交互

```css
/* 表格行 hover */
tbody tr:hover { background: var(--accent-bg); transition: background 0.1s; }
/* 卡片抬升 */
.card:hover, .info-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(43,108,176,0.15); transition: all 0.15s; }
/* 折叠箭头旋转 */
.collapsible[open] summary::before { transform: rotate(90deg); transition: transform 0.2s; }
```

```javascript
// Sidebar 滚动高亮（所有页面必须包含）
const sections = document.querySelectorAll('.section[id]');
const navLinks = document.querySelectorAll('.sidebar a[href^="#"]');
window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(s => { if (window.scrollY >= s.offsetTop - 100) current = s.id; });
  navLinks.forEach(a => { a.classList.toggle('active', a.getAttribute('href') === '#' + current); });
});
```

---

## Core Module 5: 图表渲染（ECharts 5.5.0）

### CDN 加载 + Fallback
```html
<!-- 主 CDN -->
<script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.5.0/echarts.min.js"></script>
<!-- Fallback -->
<script>
if (typeof echarts === 'undefined') {
    document.write('<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"><\/script>');
}
</script>
```

### 图表类型注册表
```javascript
// 7 种常用图表模式
const chartPatterns = {
    stacked_bar_line: {     // 堆叠柱状图 + 折线（交易额、花费）
        series: [
            { type: 'bar', stack: 'total' },
            { type: 'bar', stack: 'total' },
            { type: 'line', yAxisIndex: 1 }
        ]
    },
    dual_line: {            // 双折线图（CPS、转化漏斗）
        series: [
            { type: 'line' },
            { type: 'line' }
        ]
    },
    bar_multi_line: {       // 柱状图 + 多折线（质量指标）
        series: [
            { type: 'bar' },
            { type: 'line', yAxisIndex: 1 },
            { type: 'line', yAxisIndex: 1 }
        ]
    },
    dual_line_with_bar: {   // 柱状图 + 双折线（渠道成本）
        series: [
            { type: 'bar' },
            { type: 'line', yAxisIndex: 1 },
            { type: 'line', yAxisIndex: 1 }
        ]
    },
    single_line: {},        // 单折线（竞得率、转化率）
    multi_line_grouped: {}, // 多折线分组（分Q竞得率）
    stacked_column_chart: {}// 堆叠柱状图（撞库数据）
};
```

### ECharts 关键配置
```javascript
// grid.top 必须 >= 45，否则数据标签被标题遮挡
option = {
    grid: { top: 45, left: '10%', right: '10%', bottom: '15%' },
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    xAxis: { type: 'category', data: months },
    yAxis: [
        { type: 'value', name: '金额(亿)' },
        { type: 'value', name: '比率(%)', position: 'right' }
    ],
    series: [{
        type: 'bar',
        data: values,
        label: { show: true, position: 'top' }  // 数据标签默认启用
    }]
};

// 自动 resize：遍历所有图表实例
window.addEventListener('resize', function() {
    document.querySelectorAll('[id^="chart-"]').forEach(function(el) {
        var inst = echarts.getInstanceByDom(el);
        if (inst) inst.resize();
    });
});
```

---

## Core Module 6: Mermaid 流程图 (10.x)

### CDN 加载
```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
```

### 初始化配置
```javascript
mermaid.initialize({
    startOnLoad: true,
    theme: 'base',
    themeVariables: {
        primaryColor: '#ebf8ff',
        primaryTextColor: '#1a365d',
        primaryBorderColor: '#2b6cb0',
        lineColor: '#a0aec0',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif',
        fontSize: '13px'
    },
    flowchart: { curve: 'basis', padding: 12 },
    sequence: { actorMargin: 50, messageFontSize: 12 },
    gantt: { titleTopMargin: 15, barHeight: 20, fontSize: 11 }
});
```

### 支持图表类型
| 类型 | 语法关键字 | 适用场景 |
|------|-----------|---------|
| 流程图 | `flowchart TD/LR` | 决策流程、业务链路 |
| 时序图 | `sequenceDiagram` | 数据流、API 调用链 |
| 甘特图 | `gantt` | 项目排期、里程碑 |
| 类图 | `classDiagram` | 数据模型、架构设计 |
| 状态图 | `stateDiagram-v2` | 状态机、审批流程 |

### HTML 嵌入模式
```html
<div class="mermaid-wrapper">
    <pre class="mermaid">
flowchart TD
    A[开始] --> B{判断}
    B -->|是| C[执行]
    B -->|否| D[跳过]
    C --> E[结束]
    style A fill:#1a365d,color:#fff
    style E fill:#f0fff4,color:#276749,stroke:#38a169
    </pre>
</div>
```
```css
.mermaid-wrapper { margin: 16px 0; overflow-x: auto; }
.mermaid-wrapper .mermaid { display: flex; justify-content: center; }
```

### 主题适配
Mermaid 的 `themeVariables` 应与 CSS 变量保持一致：
- `primaryColor` → `var(--accent-bg)` (#ebf8ff)
- `primaryTextColor` → `var(--primary)` (#1a365d)
- `primaryBorderColor` → `var(--accent)` (#2b6cb0)
- `lineColor` → `var(--gray-400)` (#a0aec0)

---

## Core Module 7: 布局系统

### 动态居中（侧栏 + 内容区）
```css
/* 核心：宽屏居中，窄屏紧贴侧栏 */
#main-content {
    margin-left: max(260px, calc((100vw - 1200px) / 2));
    padding: 32px 48px;
    max-width: 1200px;
    transition: margin-left 0.3s ease;
}

/* 侧栏折叠后居中 */
body.sidebar-collapsed #main-content {
    margin-left: auto;
    margin-right: auto;
}
```

**为什么不用 `margin-left: 260px; margin-right: auto`**：
固定左偏移 + auto 右边距只会左对齐，无法居中。CSS `max()` 函数在宽屏时取 `calc((100vw - 1200px) / 2)`（居中），窄屏时取 `260px`（紧贴侧栏）。

### 可折叠侧栏
```css
#sidebar {
    position: fixed;
    left: 0; top: 0;
    width: 260px;
    height: 100vh;
    overflow-y: auto;
    background: linear-gradient(180deg, #1a365d 0%, #2d4a7a 100%);
    color: #fff;
    z-index: 100;
    transition: transform 0.3s ease, width 0.3s ease;
}

#sidebar.collapsed {
    transform: translateX(-260px);
}

#sidebar-toggle {
    position: fixed;
    left: 260px;
    top: 12px;
    z-index: 101;
    width: 24px; height: 24px;
    background: #2d4a7a;
    color: #fff;
    border: none;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
    font-size: 12px;
    transition: left 0.3s ease;
}

body.sidebar-collapsed #sidebar-toggle {
    left: 0;
}
```

```javascript
function toggleSidebar() {
    const body = document.body;
    const sidebar = document.getElementById('sidebar');
    const btn = document.getElementById('sidebar-toggle');
    body.classList.toggle('sidebar-collapsed');
    sidebar.classList.toggle('collapsed');
    btn.innerHTML = body.classList.contains('sidebar-collapsed') ? '&#9654;' : '&#9664;';
    // 触发图表 resize
    setTimeout(function() {
        window.dispatchEvent(new Event('resize'));
    }, 350);
}
```

### 响应式断点
```css
@media (max-width: 1024px) {
    #sidebar { display: none; }
    #sidebar-toggle { display: none; }
    #main-content { margin-left: 0; padding: 16px; }
}

@media print {
    #sidebar, #sidebar-toggle, .export-button { display: none !important; }
    #main-content { margin-left: 0; max-width: 100%; }
    .chart-container { page-break-inside: avoid; }
    @page { margin: 1.5cm; size: A4; }
}
```

---

## Core Module 8: 规则驱动结论引擎

### 环比计算核心
```python
def _trend_word(cur, prev):
    """返回 (方向词, 变化幅度%)"""
    if prev == 0 or pd.isna(prev) or pd.isna(cur):
        return "持平", 0.0
    pct = (cur - prev) / abs(prev) * 100
    if pct > 0:
        return "上升", round(pct, 1)
    elif pct < 0:
        return "下降", round(abs(pct), 1)
    return "持平", 0.0

def _fmt_val(v, unit="", decimals=2):
    """格式化数值 + 单位"""
    return f"{v:,.{decimals}f}{unit}"
```

### 结论生成器模式
```python
def gen_conclusion_xxx(df_a, df_b=None):
    """结论生成器标准模式"""
    month_col = get_month_col(df_a)
    months = df_a[month_col].tolist()
    label = months[-1]       # 当前月

    # 取末两行计算环比
    cur_val = df_a["指标"].iloc[-1]
    prev_val = df_a["指标"].iloc[-2]
    direction, pct = _trend_word(cur_val, prev_val)

    return (f"<strong>{label}XX：</strong>"
            f"指标A {_fmt_val(cur_val, '亿')}，环比{direction}{pct}%；"
            f"指标B ...")
```

**输出格式**：`<strong>2月XX：</strong>指标A XX元，环比上升X%；` — 嵌入 blockquote 结论框。

---

## Core Module 9: Python f-string HTML 模板

### 核心模式
```python
from datetime import datetime
from pathlib import Path
import pandas as pd

def build_html():
    # 1. 读取 CSV
    trade = pd.read_csv("Output/trade_by_group.csv")

    # 2. 转换为 JS 数组字符串
    def to_js_array(series, decimals=2):
        return "[" + ",".join(f"{v:.{decimals}f}" for v in series) + "]"

    trade_total = to_js_array(trade["总计"] / 1e8, 2)

    # 3. 预计算所有变量（不在 f-string 中调用函数）
    concl_scale = gen_conclusion_scale(trade, spend)

    # 4. f-string 模板（注意 {{ }} 转义 JS 大括号）
    html = f'''<!DOCTYPE html>
    <html><head>
    <script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.5.0/echarts.min.js"></script>
    </head><body>
    <blockquote>{concl_scale}</blockquote>
    <div id="chart-trade" style="width:100%;height:400px;"></div>
    <script>
    echarts.init(document.getElementById('chart-trade')).setOption({{
        grid: {{ top: 45 }},
        xAxis: {{ data: {trade_months} }},
        series: [{{ data: {trade_total}, type: 'line' }}]
    }});
    </script>
    </body></html>'''

    # 5. 带时间戳输出
    out = Path("HTML") / datetime.now().strftime("报告_%Y%m%d_%H%M.html")
    out.write_text(html, encoding="utf-8")
```

**关键约束**：
- f-string 中 JS 的 `{` `}` 必须写成 `{{` `}}`
- 所有变量必须在 f-string 之前预计算，不能在 f-string 内调用函数
- Python 列表 `[1, 2, 3]` 可直接嵌入 JS（格式兼容）

---

## Common Issues — 详细代码示例

### 问题 2: 页面内容偏左不居中（完整修复代码）
```css
#main-content {
    margin-left: max(260px, calc((100vw - 1200px) / 2));
    max-width: 1200px;
}
```

### 问题 6: 字段名不统一（完整修复代码）
```python
def get_month_col(df):
    for c in ["month", "date_month"]:
        if c in df.columns:
            return c
    raise ValueError(f"No month column: {list(df.columns)}")
```
