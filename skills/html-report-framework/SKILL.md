---
name: html-report-framework
description: HTML 报告生成通用框架 - 设计美化、内容生成、排版调整和常见问题解决方案
triggers:
  - html报告
  - 网页报告
  - report design
  - 报告排版
  - 报告美化
argument-hint: <报告类型> [样式主题]
quality: high
source: conversation
---

# HTML 报告通用框架

## Purpose

提供 HTML 报告生成的完整工具链和最佳实践，涵盖设计美化、内容生成、排版调整和常见问题解决方案。从月报项目中提炼的实战经验。

## When to Activate

当用户需要创建或优化任何 HTML 格式的数据报告时激活，特别适用于：
- 数据可视化报告
- 定期业务报告
- KPI dashboard
- 复刻 PPT 风格的网页报告

## Core Modules

### 1. 设计美化 (Design Enhancement)

#### PPT 风格排版模板
```html
<!-- 标准章节结构 -->
<section class="report-section">
    <!-- 标题 + 分隔线 -->
    <div class="section-header">
        <h2 style="color: #8B4513; font-weight: bold;">章节标题</h2>
        <div class="divider" style="background: #DAA520; height: 4px;"></div>
    </div>

    <!-- 结论文本框 -->
    <div class="conclusion-box" style="
        background: #F5F5F5;
        color: #333333;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #1677ff;
    ">
        <p>结论段落1</p>
        <p>结论段落2</p>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
        <!-- 单图：80%宽度居中 -->
        <div style="width: 80%; margin: 0 auto;">
            <canvas id="chart1"></canvas>
        </div>

        <!-- 双图：48%宽度并列 -->
        <div style="display: flex; gap: 4%;">
            <div style="flex: 1;"><canvas id="chart2"></canvas></div>
            <div style="flex: 1;"><canvas id="chart3"></canvas></div>
        </div>
    </div>
</section>
```

#### 响应式布局方案
```css
/* 侧边栏 + 主内容区 */
body {
    display: flex;
    margin: 0;
}

#sidebar-nav {
    position: fixed;
    left: 0;
    top: 0;
    width: 220px;
    height: 100vh;
    overflow-y: auto;
    background: #f8f9fa;
    border-right: 1px solid #dee2e6;
}

#main-content {
    margin-left: 240px;
    padding: 20px;
    max-width: 1200px;
}

/* 响应式：小屏隐藏侧边栏 */
@media (max-width: 1024px) {
    #sidebar-nav { display: none; }
    #main-content { margin-left: 0; }
}
```

#### 配色方案库
```javascript
const colorThemes = {
    ppt: {
        title: '#8B4513',       // 棕色标题
        divider: '#DAA520',     // 金色分隔线
        text: '#333333',        // 深灰文字
        accent: '#E84C3D',      // 红色强调
        background: '#FFFFFF',
        conclusionBg: '#F5F5F5'
    },
    modern: {
        title: '#1677ff',
        divider: '#40a9ff',
        text: '#262626',
        accent: '#ff4d4f',
        background: '#ffffff',
        conclusionBg: '#f0f5ff'
    },
    minimal: {
        title: '#000000',
        divider: '#d9d9d9',
        text: '#595959',
        accent: '#1890ff',
        background: '#fafafa',
        conclusionBg: '#f5f5f5'
    }
};
```

#### 字体层级系统
```css
/* 3级标题层级 */
h1 {
    font-size: 28px;
    font-weight: bold;
    color: #8B4513;
    margin-bottom: 8px;
}

h2 {
    font-size: 20px;
    font-weight: bold;
    color: #333333;
    margin-top: 30px;
    margin-bottom: 15px;
}

h3 {
    font-size: 16px;
    font-weight: 600;
    color: #595959;
    margin-top: 20px;
}

/* 正文 */
p {
    font-size: 14px;
    line-height: 1.8;
    color: #333333;
}
```

### 2. 内容生成 (Content Generation)

#### 数据驱动的结论文本生成
```python
def generate_conclusion(data):
    """基于数据自动生成结论文本"""
    current = data['current_value']
    previous = data['previous_value']
    change_pct = ((current - previous) / previous) * 100

    # 趋势描述
    if abs(change_pct) < 5:
        trend = "基本持平"
    elif change_pct > 0:
        trend = f"增长{abs(change_pct):.1f}%"
    else:
        trend = f"下降{abs(change_pct):.1f}%"

    # 程度描述
    if abs(change_pct) > 20:
        degree = "大幅"
    elif abs(change_pct) > 10:
        degree = "明显"
    else:
        degree = "小幅"

    conclusion = f"本月{data['metric_name']}{current:.2f}{data['unit']}，环比{degree}{trend}。"

    # 添加原因分析（可选）
    if data.get('top_contributor'):
        conclusion += f"主要由{data['top_contributor']}贡献。"

    return conclusion
```

#### 图表自动配置
```javascript
function detectChartType(data) {
    // 基于数据类型自动选择图表
    const seriesCount = data.series.length;
    const hasTrend = data.labels.every(l => /\d{4}-\d{2}/.test(l)); // 日期格式

    if (seriesCount === 1 && hasTrend) {
        return 'line';  // 单系列趋势 → 折线图
    } else if (seriesCount >= 3 && !hasTrend) {
        return 'bar';   // 多系列对比 → 柱状图
    } else if (data.series[0].data.every(v => v >= 0 && v <= 100)) {
        return 'percentage-bar';  // 百分比数据 → 百分比堆叠柱状图
    }

    return 'mixed';  // 默认混合图
}
```

#### Markdown 转 HTML
```python
import markdown

def convert_conclusion(md_text):
    """将 Markdown 格式的结论转为 HTML"""
    html = markdown.markdown(md_text, extensions=[
        'extra',      # 表格、定义列表
        'nl2br',      # 换行符转 <br>
        'sane_lists'  // 更严格的列表解析
    ])
    return f'<div class="conclusion-box">{html}</div>'
```

### 3. 排版调整 (Layout Tuning)

#### 图表布局引擎
```javascript
function determineChartLayout(charts) {
    // 自动决定图表排列方式
    const layouts = [];

    charts.forEach((chart, index) => {
        if (chart.important) {
            // 重要图表：单独一行，80%宽度
            layouts.push({
                type: 'single',
                charts: [chart],
                width: '80%'
            });
        } else if (index < charts.length - 1 && !charts[index + 1].important) {
            // 两个非重要图表：并列显示
            layouts.push({
                type: 'dual',
                charts: [chart, charts[index + 1]],
                width: '48%'
            });
            charts.splice(index + 1, 1);  // 跳过下一个
        } else {
            // 单个图表：居中显示
            layouts.push({
                type: 'single',
                charts: [chart],
                width: '70%'
            });
        }
    });

    return layouts;
}
```

#### 自适应间距计算
```css
/* 基于屏幕宽度的自适应间距 */
.report-section {
    margin-bottom: clamp(30px, 5vh, 80px);
}

.conclusion-box {
    margin: clamp(15px, 3vh, 30px) 0;
    padding: clamp(15px, 2.5vw, 25px);
}

.chart-container {
    margin-top: clamp(20px, 3vh, 40px);
}
```

#### 打印优化（PDF 导出）
```css
@media print {
    /* 隐藏交互元素 */
    #sidebar-nav,
    .edit-button,
    .export-button {
        display: none !important;
    }

    /* 调整页面边距 */
    @page {
        margin: 1.5cm;
        size: A4;
    }

    /* 避免图表跨页 */
    .chart-container {
        page-break-inside: avoid;
    }

    /* 避免章节跨页 */
    .report-section {
        page-break-inside: avoid;
    }

    /* 强制某些章节新起一页 */
    .report-section.page-break {
        page-break-before: always;
    }
}
```

### 4. 常见问题解决 (Common Issues)

#### 问题诊断清单
```markdown
### 图表不显示
- [ ] Chart.js 库是否正确加载？（检查控制台 404 错误）
- [ ] Canvas 元素 ID 是否与初始化代码匹配？
- [ ] 数据 JSON 文件是否正确加载？
- [ ] 图表初始化是否在 DOM 加载后执行？

### 数据不准确
- [ ] 数据源是否是最新版本？
- [ ] 是否存在多个数据文件（chart-data.json vs report-data.json）？
- [ ] 数据类型是否正确（数字 vs 字符串）？
- [ ] 时间粒度是否匹配（日 vs 月）？

### 样式错乱
- [ ] CSS 路径是否正确（./assets/ vs ../assets/）？
- [ ] 是否有 CSS 冲突（检查 specificity）？
- [ ] 响应式断点是否合理？
- [ ] 浏览器是否支持使用的 CSS 特性？

### contenteditable 保存问题
- [ ] 是否添加了 localStorage 自动保存？
- [ ] 是否提示用户手动保存 HTML？
- [ ] 是否集成了后端 API？
```

#### 修复模式库

**模式 1: 资源路径修复**
```bash
# 问题症状
浏览器控制台: GET file:///.../assets/chart.umd.min.js net::ERR_FILE_NOT_FOUND

# 根因
HTML 中路径错误: <script src="../assets/chart.umd.min.js"></script>

# 修复
<script src="./assets/chart.umd.min.js"></script>
```

**模式 2: 图表初始化时序修复**
```javascript
// 问题：图表初始化时 DOM 未加载完成
new Chart(...)  // ❌ 直接执行失败

// 修复：等待 DOM 加载
document.addEventListener('DOMContentLoaded', function() {
    initAllCharts();  // ✅ 在 DOM 加载后初始化
});
```

**模式 3: 数据源统一**
```javascript
// 问题：混用多个数据源
fetch('chart-data.json')  // OCR 手动数据（有误差）
fetch('data/report-data.json')  // 程序提取（精确）

// 修复：统一数据源
// 1. 废弃错误数据源
mv chart-data.json chart-data.json.bak

// 2. 只使用精确数据源
<script src="./data/report-data.js"></script>
<script>
    const chartsData = window.REPORT_DATA.charts;
</script>
```

**模式 4: 图表覆盖问题**
```javascript
// 问题：只初始化了部分图表（5/27）
function initCharts() {
    initChart1();
    initChart2();
    // ... 遗漏 22 个图表
}

// 修复：自动化图表初始化
function initAllCharts() {
    const canvasElements = document.querySelectorAll('canvas[id^="chart"]');
    canvasElements.forEach(canvas => {
        const chartId = canvas.id;
        const chartData = window.REPORT_DATA.charts[chartId];
        if (chartData) {
            renderChart(canvas.id, chartData);
        }
    });
}
```

#### 最佳实践文档

**数据处理**:
1. 始终从源数据生成中间 JSON，而非手动编辑
2. 保留数据处理脚本（Python/Node）用于更新
3. 版本控制数据文件，追踪历史变化
4. 使用数据校验脚本对比新旧版本

**图表渲染**:
1. 使用 Chart.js 4.x（性能优化，API 更简洁）
2. 图表数据外置到 JSON，避免硬编码
3. 统一图表配色方案
4. 添加数据标签（datalabels 插件）

**内容编辑**:
1. 使用 `contenteditable="true"` 而非富文本编辑器
2. 添加视觉反馈（hover 效果、focus 背景色）
3. 提供保存提示（localStorage 或手动保存）
4. 保持原始 HTML 文件作为模板

**性能优化**:
1. 懒加载图表（滚动到可见区域再渲染）
2. 压缩 Chart.js 库（使用 min.js）
3. 图片优化（WebP 格式，适当压缩）
4. 避免内联大量数据（使用外部 JSON）

#### 反面案例集

**❌ 案例 1: 过度装饰**
```css
/* 不要：过度使用动画和阴影 */
.chart {
    animation: float 3s ease-in-out infinite;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    filter: drop-shadow(5px 5px 10px #000);
}

/* 应该：简洁专业 */
.chart {
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
```

**❌ 案例 2: 硬编码数据**
```html
<!-- 不要：数据直接写在 HTML 里 -->
<script>
const chart1Data = [1.2, 3.4, 5.6, ...];  // 更新时需手动修改
</script>

<!-- 应该：数据外置 JSON -->
<script src="./data/report-data.js"></script>
<script>
const chart1Data = window.REPORT_DATA.charts.chart1.data;
</script>
```

**❌ 案例 3: 缺少响应式**
```css
/* 不要：固定宽度 */
.sidebar { width: 250px; }
.main { width: 1000px; }

/* 应该：响应式布局 */
.sidebar { width: 220px; }
.main { max-width: 1200px; margin-left: 240px; }

@media (max-width: 1024px) {
    .sidebar { display: none; }
    .main { margin-left: 0; }
}
```

## Advanced Topics

### 数据血缘追踪
```python
# 建立数据处理链路图
数据源（Excel）
  ↓ data_processor.py
中间数据（CSV快照）
  ↓ chart_renderer.py
图表数据（JSON）
  ↓ charts.js
浏览器渲染
```

### A/B 测试框架
```javascript
// 测试不同配色方案的用户偏好
const experiments = {
    'theme-v1': { theme: 'ppt', users: [] },
    'theme-v2': { theme: 'modern', users: [] }
};

function assignExperiment(userId) {
    const variant = Math.random() < 0.5 ? 'theme-v1' : 'theme-v2';
    applyTheme(experiments[variant].theme);
    trackEvent('experiment_view', { userId, variant });
}
```

### 自动化测试
```javascript
// 图表渲染测试
describe('Chart Rendering', () => {
    it('should render all 27 charts', () => {
        const charts = document.querySelectorAll('canvas');
        expect(charts.length).toBe(27);

        charts.forEach(canvas => {
            const ctx = canvas.getContext('2d');
            expect(ctx).not.toBeNull();
        });
    });

    it('should load data from JSON', async () => {
        const response = await fetch('./data/report-data.json');
        const data = await response.json();
        expect(data.charts).toBeDefined();
        expect(Object.keys(data.charts).length).toBeGreaterThan(0);
    });
});
```

## Related Skills

- `/monthly-report-html-generator` - 月报 HTML 专用生成器
- `/frontend-design` - 前端设计优化
- `/document-skills:pptx` - PPT 处理（用于参考样式）

## Usage Examples

### Example 1: 快速诊断报告问题
```bash
/html-report-framework diagnose \
    --file report.html \
    --issues "图表不显示"
```

### Example 2: 应用最佳实践
```bash
/html-report-framework optimize \
    --input report.html \
    --apply responsive,print,accessibility
```

### Example 3: 生成样式模板
```bash
/html-report-framework template \
    --theme ppt \
    --output my-report-template.html
```

## Quality Checklist

报告上线前检查���

- [ ] 数据准确性（与源数据对比）
- [ ] 图表完整性（所有 canvas 渲染）
- [ ] 响应式布局（1024px 以下正常）
- [ ] 打印效果（PDF 导出正常）
- [ ] 浏览器兼容性（Chrome/Firefox/Edge）
- [ ] 性能（首屏加载 < 3秒）
- [ ] 无障碍性（WCAG 2.1 AA 级）

## Notes

- **版本管理**：HTML 报告建议用 Git 管理，便于追踪修改
- **数据安全**：敏感数据不要内嵌 HTML，使用后端 API
- **持续改进**：定期回顾用户反馈，优化模板和工具
- **文档先行**：每次重大修改前更新文档，避免知识流失
