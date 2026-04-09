"""
HTML报告生成模块
负责生成现代化、可编辑的HTML格式RTA排除策略分析报告
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
from utils import convert_old_rule_to_quantile, calc_spr, calc_cps, make_region_mask, filter_by_region
from metrics import (
    calc_comparison_metrics,
    calc_four_segments,
    calc_segment_amt_ratios,
    calc_v8_spr_table,
)


def generate_html_report(result, old_exclude_rule, output_path=None):
    """
    生成完整的HTML报告

    Args:
        result: 算法结果字典
        old_exclude_rule: 老策略排除规则（如['01q', '02q', ...]）
        output_path: 输出路径（可选）

    Returns:
        str: 生成的报告文件路径
    """
    print("\n" + "="*100)
    print("生成HTML报告")
    print("="*100)

    # 提取数据
    df_combined = result['df_combined']
    df_ctrl = result['df_ctrl']
    exclude_region = result['exclude_region']

    # 转换老策略规则为聚合后的格式
    old_exclude_v8 = convert_old_rule_to_quantile(old_exclude_rule)

    # 构建HTML内容
    html_content = generate_html_structure(df_combined, df_ctrl, exclude_region, old_exclude_v8)

    # 保存文件
    if output_path is None:
        output_path = '.'

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = f'{output_path}/RTA排除策略报告_{timestamp}.html'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n报告已生成: {file_path}")
    return file_path


def format_percent(value):
    """格式化为百分比字符串"""
    return f"{value*100:.2f}%"


def format_number(value):
    """格式化数字"""
    if value < 1:
        return f"{value*100:.2f}%"
    else:
        return f"{value:.4f}"


# ============================================================================
# HTML结构生成
# ============================================================================

def generate_html_structure(df_combined, df_ctrl, exclude_region, old_exclude_v8):
    """生成完整的HTML结构"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RTA排除策略分析报告</title>
    {generate_css()}
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
</head>
<body>
    <div class="container">
        <!-- 侧栏折叠按钮 -->
        <button id="sidebar-toggle" onclick="toggleSidebar()">&#9664;</button>

        <!-- 左侧导航栏 -->
        <nav class="sidebar" id="sidebar">
            <div class="logo">
                <h2>RTA排除策略报告</h2>
                <p class="timestamp">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <ul class="nav-list">
                <li><a href="#section1" class="nav-link">一、核心结论</a></li>
                <li><a href="#section2" class="nav-link">二、排除策略制定</a>
                    <ul class="sub-nav">
                        <li><a href="#section2-1">2.1 排除策略现状</a></li>
                        <li><a href="#section2-2">2.2 排除策略制定</a></li>
                    </ul>
                </li>
                <li><a href="#section3" class="nav-link">三、合理性评估</a>
                    <ul class="sub-nav">
                        <li><a href="#section3-1">3.1 置入置出分析</a></li>
                        <li><a href="#section3-2">3.2 图表展示</a></li>
                    </ul>
                </li>
            </ul>
        </nav>

        <!-- 主内容区 -->
        <main class="content">
            {generate_section1_conclusion_html(df_ctrl, exclude_region, old_exclude_v8)}
            {generate_section2_strategy_html(df_combined, df_ctrl, exclude_region, old_exclude_v8)}
            {generate_section3_evaluation_html(df_ctrl, exclude_region, old_exclude_v8)}
        </main>
    </div>

    {generate_javascript()}
</body>
</html>"""

    return html


def generate_css():
    """生成内嵌CSS样式"""
    return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
                         'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }

        .container {
            display: flex;
            min-height: 100vh;
        }

        /* 侧边栏样式 */
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 260px;
            height: 100vh;
            background: linear-gradient(180deg, #1a365d 0%, #2d4a7a 100%);
            color: white;
            padding: 2rem 1.5rem;
            overflow-y: auto;
            z-index: 100;
            transition: transform 0.3s ease;
        }

        .sidebar.collapsed {
            transform: translateX(-260px);
        }

        #sidebar-toggle {
            position: fixed;
            left: 260px;
            top: 12px;
            z-index: 101;
            width: 28px;
            height: 28px;
            background: #1a365d;
            color: #fff;
            border: none;
            border-radius: 0 6px 6px 0;
            cursor: pointer;
            font-size: 12px;
            transition: left 0.3s ease;
        }

        body.sidebar-collapsed #sidebar-toggle {
            left: 0;
        }

        .logo h2 {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            padding-bottom: 1rem;
        }

        .timestamp {
            font-size: 0.875rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }

        .nav-list {
            list-style: none;
        }

        .nav-list > li {
            margin-bottom: 1rem;
        }

        .nav-link {
            display: block;
            color: white;
            text-decoration: none;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            transition: all 0.3s;
            font-weight: 500;
        }

        .nav-link:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateX(5px);
        }

        .sub-nav {
            list-style: none;
            margin-top: 0.5rem;
            margin-left: 1rem;
        }

        .sub-nav li {
            margin-bottom: 0.5rem;
        }

        .sub-nav a {
            display: block;
            color: rgba(255, 255, 255, 0.85);
            text-decoration: none;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            font-size: 0.9rem;
            transition: all 0.3s;
        }

        .sub-nav a:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }

        /* 主内容区样式 */
        .content {
            margin-left: max(260px, calc((100vw - 1200px) / 2));
            padding: 32px 48px;
            max-width: 1200px;
            transition: margin-left 0.3s ease;
        }

        body.sidebar-collapsed .content {
            margin-left: auto;
            margin-right: auto;
        }

        section {
            background: white;
            border-radius: 10px;
            padding: 2rem 2.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
            border-left: 4px solid #2b6cb0;
        }

        h1 {
            font-size: 1.5rem;
            color: #1a365d;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #2b6cb0;
            font-weight: 700;
        }

        h2 {
            font-size: 1.25rem;
            color: #1a365d;
            margin: 1.5rem 0 1rem;
            font-weight: 600;
        }

        h3 {
            font-size: 1.1rem;
            color: #2d4a7a;
            margin: 1.25rem 0 0.75rem;
            font-weight: 600;
        }

        .conclusion-text {
            background: #f7fafc;
            padding: 1.25rem 1.75rem;
            border-radius: 8px;
            border-left: 4px solid #2b6cb0;
            margin: 1.25rem 0;
            font-size: 0.9rem;
        }

        .conclusion-text p {
            margin-bottom: 0.75rem;
            line-height: 1.8;
        }

        .conclusion-text strong {
            color: #2b6cb0;
            font-weight: 600;
        }

        /* 表格样式 */
        .table-container {
            margin: 1.5rem 0;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        thead {
            background: linear-gradient(135deg, #1a365d 0%, #2d4a7a 100%);
            color: white;
        }

        th {
            padding: 0.75rem 1rem;
            text-align: center;
            font-weight: 600;
            font-size: 0.825rem;
            letter-spacing: 0.025em;
        }

        td {
            padding: 0.875rem 1rem;
            text-align: center;
            border-bottom: 1px solid #e2e8f0;
        }

        tbody tr {
            transition: background-color 0.2s;
        }

        tbody tr:hover {
            background-color: #f7fafc;
        }

        tbody tr:last-child td {
            border-bottom: none;
        }

        .excluded-cell {
            background: linear-gradient(135deg, #ffb6c1 0%, #ff9aa2 100%);
            font-weight: 600;
            color: #c53030;
        }

        .bold-cell {
            font-weight: 600;
            color: #1a365d;
        }

        /* 热力图样式 */
        .heatmap-container {
            margin: 2rem 0;
            overflow-x: auto;
        }

        .heatmap-table {
            font-size: 0.85rem;
        }

        .heatmap-table th,
        .heatmap-table td {
            padding: 0.5rem;
            min-width: 70px;
        }

        .heatmap-cell {
            position: relative;
        }

        .heatmap-cell.excluded {
            background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
            color: white;
            font-weight: 600;
        }

        /* KPI卡片 */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .kpi-card {
            background: white;
            border-radius: 10px;
            padding: 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
            text-align: center;
            border-top: 3px solid #2b6cb0;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }

        .kpi-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: #1a365d;
            margin-bottom: 0.375rem;
        }

        .kpi-label {
            font-size: 0.8rem;
            color: #718096;
            margin-bottom: 0.375rem;
        }

        .kpi-delta {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 10px;
            display: inline-block;
        }

        .kpi-delta.positive { color: #276749; background: #c6f6d5; }
        .kpi-delta.negative { color: #9b2c2c; background: #fed7d7; }

        /* 差异列箭头 */
        .diff-cell { font-weight: 600; }
        .diff-cell.positive { color: #38a169; }
        .diff-cell.negative { color: #e53e3e; }
        .diff-arrow { font-size: 1.1em; margin-right: 4px; }

        /* 排序功能 */
        .sortable {
            cursor: pointer;
            position: relative;
            user-select: none;
        }

        .sortable:hover {
            opacity: 0.8;
        }

        .sortable::after {
            content: ' ⇅';
            opacity: 0.5;
        }

        .sortable.asc::after {
            content: ' ↑';
            opacity: 1;
        }

        .sortable.desc::after {
            content: ' ↓';
            opacity: 1;
        }

        /* 响应式设计 */
        @media (max-width: 1024px) {
            .sidebar {
                display: none;
            }

            #sidebar-toggle {
                display: none;
            }

            .content {
                margin-left: 0;
                padding: 16px;
            }

            .kpi-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 768px) {
            .kpi-grid {
                grid-template-columns: 1fr;
            }
        }

        /* 打印样式 */
        @media print {
            .sidebar, #sidebar-toggle {
                display: none !important;
            }

            .content {
                margin-left: 0;
                max-width: 100%;
                padding: 0;
            }

            section {
                box-shadow: none;
                border: 1px solid #e2e8f0;
                page-break-inside: avoid;
            }

            .kpi-card {
                box-shadow: none;
                border: 1px solid #e2e8f0;
            }

            @page {
                margin: 1.5cm;
                size: A4;
            }
        }
    </style>
    """


def generate_javascript():
    """生成交互JavaScript"""
    return """
    <script>
        // 侧栏折叠/展开
        function toggleSidebar() {
            const body = document.body;
            const sidebar = document.getElementById('sidebar');
            const btn = document.getElementById('sidebar-toggle');
            body.classList.toggle('sidebar-collapsed');
            sidebar.classList.toggle('collapsed');
            btn.innerHTML = body.classList.contains('sidebar-collapsed') ? '&#9654;' : '&#9664;';
        }

        // 平滑滚动到锚点
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // 表格排序功能
        function sortTable(table, columnIndex, isAscending) {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));

            rows.sort((a, b) => {
                const aValue = a.cells[columnIndex].textContent.trim();
                const bValue = b.cells[columnIndex].textContent.trim();

                // 尝试解析为数字
                const aNum = parseFloat(aValue.replace('%', ''));
                const bNum = parseFloat(bValue.replace('%', ''));

                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAscending ? aNum - bNum : bNum - aNum;
                }

                // 字符串比较
                return isAscending ?
                    aValue.localeCompare(bValue, 'zh-CN') :
                    bValue.localeCompare(aValue, 'zh-CN');
            });

            // 重新插入排序后的行
            rows.forEach(row => tbody.appendChild(row));
        }

        // 为可排序的表头添加点击事件
        document.querySelectorAll('.sortable').forEach(th => {
            th.addEventListener('click', function() {
                const table = this.closest('table');
                const thead = this.closest('thead');
                const columnIndex = Array.from(this.parentElement.children).indexOf(this);

                // 切换排序方向
                const isAscending = !this.classList.contains('asc');

                // 移除其他列的排序标记
                thead.querySelectorAll('th').forEach(header => {
                    header.classList.remove('asc', 'desc');
                });

                // 添加当前列的排序标记
                this.classList.add(isAscending ? 'asc' : 'desc');

                // 执行排序
                sortTable(table, columnIndex, isAscending);
            });
        });

        // 高亮当前章节
        window.addEventListener('scroll', function() {
            const sections = document.querySelectorAll('section[id]');
            const navLinks = document.querySelectorAll('.nav-link');

            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                if (window.pageYOffset >= sectionTop - 100) {
                    current = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.style.background = '';
                if (link.getAttribute('href') === '#' + current) {
                    link.style.background = 'rgba(255, 255, 255, 0.15)';
                }
            });
        });
    </script>
    """


# ============================================================================
# 第一部分：核心结论
# ============================================================================

def generate_section1_conclusion_html(df_ctrl, exclude_region, old_exclude_v8):
    """生成第一部分HTML：核心结论"""

    # 计算指标
    m = calc_comparison_metrics(df_ctrl, exclude_region, old_exclude_v8)
    total_ctrl_amt = m['total_ctrl_amt']
    old_exclude_amt_ratio = m['old_exclude_amt_ratio']
    old_exclude_spr = m['old_exclude_spr']
    old_remain_spr = m['old_remain_spr']
    old_remain_cps = m['old_remain_cps']
    new_exclude_amt_ratio = m['new_exclude_amt_ratio']
    new_exclude_spr = m['new_exclude_spr']
    new_remain_spr = m['new_remain_spr']
    new_remain_cps = m['new_remain_cps']

    # KPI差异计算
    amt_ratio_diff = new_exclude_amt_ratio - old_exclude_amt_ratio
    spr_lift = (new_remain_spr - old_remain_spr) * 100
    exclude_spr_diff = new_exclude_spr - old_exclude_spr
    cps_diff = new_remain_cps - old_remain_cps

    amt_delta_class = 'positive' if amt_ratio_diff > 0 else 'negative'
    amt_delta_sign = '+' if amt_ratio_diff > 0 else ''
    spr_delta_class = 'positive' if spr_lift > 0 else 'negative'
    spr_delta_sign = '+' if spr_lift > 0 else ''
    ex_spr_delta_class = 'negative' if exclude_spr_diff < 0 else 'positive'
    ex_spr_delta_sign = '+' if exclude_spr_diff >= 0 else ''
    cps_delta_class = 'positive' if cps_diff > 0 else 'negative'
    cps_delta_sign = '+' if cps_diff > 0 else ''

    return f"""
    <section id="section1">
        <h1>一、核心结论：关键指标对比（旧策略 vs 新策略）</h1>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-value">{format_percent(new_exclude_amt_ratio)}</div>
                <div class="kpi-label">新策略排除交易占比</div>
                <div class="kpi-delta {amt_delta_class}">{'↑' if amt_ratio_diff > 0 else '↓'} 较旧策略 {amt_delta_sign}{amt_ratio_diff*100:.2f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{format_percent(new_remain_spr)}</div>
                <div class="kpi-label">保留客群SPR</div>
                <div class="kpi-delta {spr_delta_class}">{'↑' if spr_lift > 0 else '↓'} 较旧策略 {spr_delta_sign}{spr_lift:.2f}pct</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{format_percent(new_exclude_spr)}</div>
                <div class="kpi-label">排除客群SPR</div>
                <div class="kpi-delta {ex_spr_delta_class}">{'↑' if exclude_spr_diff >= 0 else '↓'} 较旧策略 {ex_spr_delta_sign}{exclude_spr_diff*100:.2f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{new_remain_cps:.4f}</div>
                <div class="kpi-label">保留客群CPS</div>
                <div class="kpi-delta {cps_delta_class}">{'↑' if cps_diff > 0 else '↓'} 较旧策略 {cps_delta_sign}{cps_diff:.4f}</div>
            </div>
        </div>

        <div class="conclusion-text">
            <p><strong>1. 新策略显著提升保留客群质量</strong></p>
            <p>
                旧策略排除交易占比<strong>{format_percent(old_exclude_amt_ratio)}</strong>，
                保留客群安全过件率<strong>{format_percent(old_remain_spr)}</strong><br>
                新策略排除交易占比<strong>{format_percent(new_exclude_amt_ratio)}</strong>，
                保留客群安全过件率<strong>{format_percent(new_remain_spr)}</strong><br>
                新策略保留客群安全过件率提升<strong>{(new_remain_spr-old_remain_spr)*100:.2f}</strong>个百分点，
                相当于提升了<strong>{(new_remain_spr/old_remain_spr-1)*100:.1f}%</strong>
            </p>

            <p><strong>2. 新策略更精准识别低质量客群</strong></p>
            <p>
                旧策略排除客群安全过件率<strong>{format_percent(old_exclude_spr)}</strong><br>
                新策略排除客群安全过件率<strong>{format_percent(new_exclude_spr)}</strong><br>
                新策略排除客群质量更低，排除更精准
            </p>

            <p><strong>3. 满足约束条件</strong></p>
            <p>
                新策略排除交易占比<strong>{format_percent(new_exclude_amt_ratio)}</strong>，在20%约束范围内
            </p>

            <p><strong>4. 二维模型优势</strong></p>
            <p>
                新策略采用<strong>V8 x V9RN二维模型</strong>，相比旧策略的V8单维度模型，
                可以更细粒度地识别客群质量
            </p>

            <p><strong>综合评价：</strong>新策略优于旧策略，建议采用新策略</p>
        </div>
    </section>
    """


# ============================================================================
# 第二部分：排除策略制定
# ============================================================================

def generate_section2_strategy_html(df_combined, df_ctrl, exclude_region, old_exclude_v8):
    """生成第二部分HTML：排除策略制定"""

    section2_1 = generate_section2_1_old_strategy_html(df_combined, old_exclude_v8)
    section2_2 = generate_section2_2_new_strategy_html(df_combined, df_ctrl, exclude_region, old_exclude_v8)

    return f"""
    <section id="section2">
        <h1>二、排除策略制定</h1>

        <div id="section2-1">
            {section2_1}
        </div>

        <div id="section2-2">
            {section2_2}
        </div>
    </section>
    """


def generate_section2_1_old_strategy_html(df_combined, old_exclude_v8):
    """生成2.1：排除策略现状（老策略）"""

    # 计算V8各分位的安全过件率
    v8_stats_all, v8_list = calc_v8_spr_table(df_combined)

    # 生成表格行
    table_rows = ""
    for v8 in v8_list:
        v8_data = v8_stats_all[v8_stats_all['V8_Q'] == v8]
        if len(v8_data) > 0:
            spr = v8_data['安全过件率'].values[0]
            is_excluded = v8 in old_exclude_v8
            cell_class = 'excluded-cell' if is_excluded else ''
            is_excluded_text = '是' if is_excluded else '否'

            table_rows += f"""
            <tr>
                <td>{v8}</td>
                <td>{format_percent(spr)}</td>
                <td class="{cell_class}">{is_excluded_text}</td>
            </tr>
            """

    return f"""
    <h2>1. 排除策略现状</h2>

    <h3>表1：老策略排除规则（V8单维度）</h3>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th class="sortable">V8分位</th>
                    <th class="sortable">安全过件率（全量）</th>
                    <th class="sortable">是否排除</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    """


def generate_section2_2_new_strategy_html(df_combined, df_ctrl, exclude_region, old_exclude_v8):
    """生成2.2：排除策略制定（新策略）"""

    # 计算指标
    m = calc_comparison_metrics(df_ctrl, exclude_region, old_exclude_v8)
    total_ctrl_expo = m['total_ctrl_expo']
    total_ctrl_ato = m['total_ctrl_ato']
    total_ctrl_amt = m['total_ctrl_amt']
    old_exclude_expo_ratio = m['old_exclude_expo_ratio']
    old_exclude_ato_ratio = m['old_exclude_ato_ratio']
    old_exclude_amt_ratio = m['old_exclude_amt_ratio']
    old_exclude_spr = m['old_exclude_spr']
    old_remain_spr = m['old_remain_spr']
    old_remain_cps = m['old_remain_cps']
    new_exclude_expo_ratio = m['new_exclude_expo_ratio']
    new_exclude_ato_ratio = m['new_exclude_ato_ratio']
    new_exclude_amt_ratio = m['new_exclude_amt_ratio']
    new_exclude_spr = m['new_exclude_spr']
    new_remain_spr = m['new_remain_spr']
    new_remain_cps = m['new_remain_cps']

    # 指标对比表
    metrics = [
        ('排除曝光占比', old_exclude_expo_ratio, new_exclude_expo_ratio),
        ('排除申完占比', old_exclude_ato_ratio, new_exclude_ato_ratio),
        ('排除交易占比', old_exclude_amt_ratio, new_exclude_amt_ratio),
        ('排除用户安全过件率', old_exclude_spr, new_exclude_spr),
        ('排除后对照组安全过件率', old_remain_spr, new_remain_spr),
        ('排除后CPS', old_remain_cps, new_remain_cps)
    ]

    metrics_rows = ""
    for metric_name, old_val, new_val in metrics:
        diff_val = new_val - old_val
        if abs(diff_val) < 0.0001:
            arrow = '→'
            diff_class = ''
        elif diff_val > 0:
            arrow = '↑'
            diff_class = 'positive' if '安全过件率' in metric_name else ''
        else:
            arrow = '↓'
            diff_class = 'negative' if '安全过件率' in metric_name else ''

        metrics_rows += f"""
        <tr>
            <td style="text-align: left;">{metric_name}</td>
            <td>{format_number(old_val)}</td>
            <td>{format_number(new_val)}</td>
            <td class="diff-cell {diff_class}">
                <span class="diff-arrow">{arrow}</span> {format_number(abs(diff_val))}
            </td>
        </tr>
        """

    # 生成热力图
    heatmap_html = generate_heatmap_html(df_combined, exclude_region)
    diff_heatmap_html = generate_diff_heatmap_html(df_combined, exclude_region, old_exclude_v8)

    return f"""
    <h2>2. 排除策略制定</h2>

    <h3>1）方案展示</h3>
    <h4>表1：新策略排除较老策略排除在对照组上的指标差异</h4>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th class="sortable">指标</th>
                    <th class="sortable">旧策略</th>
                    <th class="sortable">新策略</th>
                    <th class="sortable">差异</th>
                </tr>
            </thead>
            <tbody>
                {metrics_rows}
            </tbody>
        </table>
    </div>

    <h3>2）排除规则："安全过件率低于10%客群"</h3>
    <h4>表2：新策略排除规则（V8 x V9RN二维）</h4>
    {heatmap_html}

    <h3>3）新旧策略差异对比</h3>
    <h4>图3：置入置出差异热力图（V8 x V9RN二维）</h4>
    {diff_heatmap_html}
    """


def _spr_to_color(spr, min_spr, max_spr):
    """SPR值映射到连续色阶（红→黄→绿）"""
    if max_spr == min_spr:
        return '#ffd43b'
    ratio = (spr - min_spr) / (max_spr - min_spr)
    if ratio < 0.5:
        r = 255
        g = int(180 + 150 * (ratio / 0.5))
        b = int(50 + 50 * (ratio / 0.5))
    else:
        r = int(255 - 200 * ((ratio - 0.5) / 0.5))
        g = int(200 + 55 * ((ratio - 0.5) / 0.5))
        b = int(50 + 50 * ((ratio - 0.5) / 0.5))
    return f'rgb({r},{g},{b})'


def generate_heatmap_html(df_combined, exclude_region):
    """生成V8 x V9RN二维热力图（ECharts交互版 + 表格版）"""

    v8_list = [f'{i:02d}Q' for i in range(1, 13)]
    v9_list = [f'{i:02d}Q' for i in range(1, 13)]

    # 收集所有非排除区域的SPR值，用于确定色阶范围
    all_spr_values = []
    cell_spr_map = {}
    for v8 in v8_list:
        for v9 in v9_list:
            cell_data = df_combined[(df_combined['V8_Q'] == v8) & (df_combined['V9RN_Q'] == v9)]
            if len(cell_data) > 0 and cell_data['t3_ato'].sum() > 0:
                spr = cell_data['t3_safe_adt'].sum() / cell_data['t3_ato'].sum()
                cell_spr_map[(v8, v9)] = spr
                if (v8, v9) not in exclude_region:
                    all_spr_values.append(spr)

    min_spr = min(all_spr_values) if all_spr_values else 0
    max_spr = max(all_spr_values) if all_spr_values else 1

    # ---- ECharts data ----
    # Build series data: [v9_index, v8_index, spr_pct, is_excluded]
    echarts_data = []
    excluded_data = []
    for v8_idx, v8 in enumerate(v8_list):
        for v9_idx, v9 in enumerate(v9_list):
            is_excluded = (v8, v9) in exclude_region
            spr_val = cell_spr_map.get((v8, v9), None)
            spr_pct = round(spr_val * 100, 2) if spr_val is not None else None
            if is_excluded:
                excluded_data.append([v9_idx, v8_idx, spr_pct if spr_pct is not None else -1])
            else:
                if spr_pct is not None:
                    echarts_data.append([v9_idx, v8_idx, spr_pct])

    # Find excluded region bounding box for markArea (contiguous rectangle is not guaranteed,
    # so we draw one markArea rect per excluded cell)
    mark_area_data = []
    for (v8, v9) in exclude_region:
        if v8 in v8_list and v9 in v9_list:
            v9_idx = v9_list.index(v9)
            v8_idx = v8_list.index(v8)
            mark_area_data.append([
                {"xAxis": v9_idx - 0.5, "yAxis": v8_idx - 0.5},
                {"xAxis": v9_idx + 0.5, "yAxis": v8_idx + 0.5}
            ])

    import json
    echarts_data_json = json.dumps(echarts_data)
    excluded_data_json = json.dumps(excluded_data)
    v8_labels_json = json.dumps(v8_list)
    v9_labels_json = json.dumps(v9_list)
    mark_area_json = json.dumps(mark_area_data)

    echarts_chart_id = "heatmap_echarts_spr"

    echarts_html = f"""
    <div style="margin: 1.5rem 0;">
        <p style="font-size:0.85rem; color:#718096; margin-bottom:0.5rem;">
            交互式热力图（鼠标悬停查看详情，红色区域为排除区域）
        </p>
        <div id="{echarts_chart_id}" style="width:100%; height:500px;"></div>
    </div>
    <script>
    (function() {{
        var chartDom = document.getElementById('{echarts_chart_id}');
        var myChart = echarts.init(chartDom);

        var v8Labels = {v8_labels_json};
        var v9Labels = {v9_labels_json};
        var normalData = {echarts_data_json};
        var excludedData = {excluded_data_json};
        var markAreaData = {mark_area_json};

        var option = {{
            tooltip: {{
                position: 'top',
                formatter: function(params) {{
                    var v9 = v9Labels[params.data[0]];
                    var v8 = v8Labels[params.data[1]];
                    var spr = params.data[2];
                    var isExcluded = params.seriesName === '排除区域';
                    var sprText = (spr === -1 || spr === null) ? 'N/A' : spr.toFixed(2) + '%';
                    return 'V8: ' + v8 + '<br/>V9RN: ' + v9 +
                           '<br/>SPR: ' + sprText +
                           '<br/>状态: ' + (isExcluded ? '<span style="color:#e53e3e;font-weight:600;">已排除</span>' : '保留');
                }}
            }},
            grid: {{
                left: '80px',
                right: '120px',
                top: '30px',
                bottom: '60px'
            }},
            xAxis: {{
                type: 'category',
                data: v9Labels,
                name: 'V9RN',
                nameLocation: 'middle',
                nameGap: 35,
                axisLabel: {{ fontSize: 11 }},
                splitArea: {{ show: true }}
            }},
            yAxis: {{
                type: 'category',
                data: v8Labels,
                name: 'V8',
                nameLocation: 'middle',
                nameGap: 50,
                axisLabel: {{ fontSize: 11 }},
                splitArea: {{ show: true }}
            }},
            visualMap: {{
                type: 'piecewise',
                pieces: [
                    {{ max: 5,  label: '≤5%',    color: '#b2182b' }},
                    {{ min: 5,  max: 10, label: '5–10%',  color: '#ef8a62' }},
                    {{ min: 10, max: 15, label: '10–15%', color: '#fddbc7' }},
                    {{ min: 15, max: 20, label: '15–20%', color: '#d1e5f0' }},
                    {{ min: 20, label: '>20%',   color: '#2166ac' }}
                ],
                orient: 'vertical',
                right: 10,
                top: 'center',
                textStyle: {{ fontSize: 11 }},
                dimension: 2,
                seriesIndex: 0
            }},
            series: [
                {{
                    name: '安全过件率',
                    type: 'heatmap',
                    data: normalData,
                    label: {{
                        show: true,
                        fontSize: 9,
                        formatter: function(params) {{
                            return params.data[2] !== null ? params.data[2].toFixed(1) + '%' : '';
                        }}
                    }},
                    emphasis: {{
                        itemStyle: {{ shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }}
                    }}
                }},
                {{
                    name: '排除区域',
                    type: 'heatmap',
                    data: excludedData,
                    itemStyle: {{ color: '#e53e3e' }},
                    label: {{
                        show: true,
                        fontSize: 9,
                        color: '#fff',
                        formatter: function(params) {{
                            return params.data[2] === -1 ? '排除' :
                                   params.data[2].toFixed(1) + '%';
                        }}
                    }},
                    emphasis: {{
                        itemStyle: {{ shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }}
                    }},
                    markArea: {{
                        silent: true,
                        itemStyle: {{
                            color: 'transparent',
                            borderColor: '#555',
                            borderWidth: 2,
                            borderType: 'dashed'
                        }},
                        data: markAreaData
                    }}
                }}
            ]
        }};
        myChart.setOption(option);
        window.addEventListener('resize', function() {{ myChart.resize(); }});
    }})();
    </script>
    """

    # ---- Existing table heatmap ----
    # 表头
    header_cells = "".join([f'<th>{v9}</th>' for v9 in v9_list])

    # 数据行
    data_rows = ""
    for v8 in v8_list:
        row_cells = f"<th>{v8}</th>"

        for v9 in v9_list:
            if (v8, v9) in cell_spr_map:
                spr = cell_spr_map[(v8, v9)]
                if (v8, v9) in exclude_region:
                    style = 'background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: white; font-weight: 600;'
                else:
                    bg_color = _spr_to_color(spr, min_spr, max_spr)
                    text_color = 'white' if spr < (min_spr + max_spr) / 2 else '#333'
                    style = f'background-color: {bg_color}; color: {text_color};'
                row_cells += f'<td class="heatmap-cell" style="{style}">{format_percent(spr)}</td>'
            else:
                row_cells += '<td class="heatmap-cell">-</td>'

        data_rows += f"<tr>{row_cells}</tr>"

    table_html = f"""
    <div class="heatmap-container">
        <table class="heatmap-table">
            <thead>
                <tr>
                    <th>V8\\V9RN</th>
                    {header_cells}
                </tr>
            </thead>
            <tbody>
                {data_rows}
            </tbody>
        </table>
    </div>
    """

    return echarts_html + table_html


def generate_diff_heatmap_html(df_combined, exclude_region, old_exclude_v8):
    """生成新旧策略差异热力图（ECharts版）

    颜色编码：
      - 双排除（both exclude）：深灰 #999999
      - 置入（old排除, new保留）：蓝色 #2166ac
      - 置出（new排除, old保留）：橙色 #fc8d59
      - 双保留（both keep）：浅灰 #e0e0e0
    """
    import json

    v8_list = [f'{i:02d}Q' for i in range(1, 13)]
    v9_list = [f'{i:02d}Q' for i in range(1, 13)]

    # category codes: 0=both_keep, 1=place_in(old only), 2=place_out(new only), 3=both_exclude
    COLOR_MAP = {0: '#e0e0e0', 1: '#2166ac', 2: '#fc8d59', 3: '#999999'}
    LABEL_MAP = {0: '双保留', 1: '置入', 2: '置出', 3: '双排除'}

    series_data = []
    for v8_idx, v8 in enumerate(v8_list):
        for v9_idx, v9 in enumerate(v9_list):
            old_excl = v8 in old_exclude_v8
            new_excl = (v8, v9) in exclude_region
            if old_excl and new_excl:
                cat = 3
            elif old_excl and not new_excl:
                cat = 1
            elif not old_excl and new_excl:
                cat = 2
            else:
                cat = 0
            series_data.append([v9_idx, v8_idx, cat])

    series_data_json = json.dumps(series_data)
    v8_labels_json = json.dumps(v8_list)
    v9_labels_json = json.dumps(v9_list)

    chart_id = "heatmap_echarts_diff"

    return f"""
    <div style="margin: 1.5rem 0;">
        <p style="font-size:0.85rem; color:#718096; margin-bottom:0.5rem;">
            新旧策略差异热力图（蓝=置入，橙=置出，灰=双排除，浅灰=双保留）
        </p>
        <div id="{chart_id}" style="width:100%; height:500px;"></div>
    </div>
    <script>
    (function() {{
        var chartDom = document.getElementById('{chart_id}');
        var myChart = echarts.init(chartDom);

        var v8Labels = {v8_labels_json};
        var v9Labels = {v9_labels_json};
        var rawData = {series_data_json};

        var colorMap = {{'0': '#e0e0e0', '1': '#2166ac', '2': '#fc8d59', '3': '#999999'}};
        var labelMap = {{'0': '双保留', '1': '置入', '2': '置出', '3': '双排除'}};

        // Split into 4 series so each gets a fixed color and legend entry
        var seriesGroups = {{'0': [], '1': [], '2': [], '3': []}};
        rawData.forEach(function(d) {{
            seriesGroups[String(d[2])].push(d);
        }});

        var seriesList = ['0','1','2','3'].map(function(cat) {{
            return {{
                name: labelMap[cat],
                type: 'heatmap',
                data: seriesGroups[cat],
                itemStyle: {{ color: colorMap[cat] }},
                label: {{
                    show: cat !== '0',
                    fontSize: 9,
                    color: cat === '0' ? '#999' : '#fff',
                    formatter: function(params) {{ return labelMap[String(params.data[2])]; }}
                }},
                emphasis: {{
                    itemStyle: {{ shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.4)' }}
                }}
            }};
        }});

        var option = {{
            tooltip: {{
                position: 'top',
                formatter: function(params) {{
                    var v9 = v9Labels[params.data[0]];
                    var v8 = v8Labels[params.data[1]];
                    var cat = params.data[2];
                    return 'V8: ' + v8 + '<br/>V9RN: ' + v9 +
                           '<br/>状态: <strong>' + labelMap[String(cat)] + '</strong>';
                }}
            }},
            legend: {{
                data: ['双保留', '置入', '置出', '双排除'],
                top: 5,
                textStyle: {{ fontSize: 11 }}
            }},
            grid: {{
                left: '80px',
                right: '20px',
                top: '50px',
                bottom: '60px'
            }},
            xAxis: {{
                type: 'category',
                data: v9Labels,
                name: 'V9RN',
                nameLocation: 'middle',
                nameGap: 35,
                axisLabel: {{ fontSize: 11 }},
                splitArea: {{ show: true }}
            }},
            yAxis: {{
                type: 'category',
                data: v8Labels,
                name: 'V8',
                nameLocation: 'middle',
                nameGap: 50,
                axisLabel: {{ fontSize: 11 }},
                splitArea: {{ show: true }}
            }},
            series: seriesList
        }};
        myChart.setOption(option);
        window.addEventListener('resize', function() {{ myChart.resize(); }});
    }})();
    </script>
    """


# ============================================================================
# 第三部分：合理性评估
# ============================================================================

def generate_section3_evaluation_html(df_ctrl, exclude_region, old_exclude_v8):
    """生成第三部分HTML：合理性评估"""

    section3_1 = generate_section3_1_place_analysis_html(df_ctrl, exclude_region, old_exclude_v8)
    section3_2 = generate_section3_2_cross_tables_html(df_ctrl, exclude_region, old_exclude_v8)

    return f"""
    <section id="section3">
        <h1>三、合理性评估</h1>

        <div id="section3-1">
            {section3_1}
        </div>

        <div id="section3-2">
            {section3_2}
        </div>
    </section>
    """


def generate_section3_1_place_analysis_html(df_ctrl, exclude_region, old_exclude_v8):
    """生成3.1：置入置出合理性分析"""

    # 计算四个客群
    segs = calc_four_segments(df_ctrl, exclude_region, old_exclude_v8)
    only_old = segs['only_old']  # 置入客群
    only_new = segs['only_new']  # 置出客群

    # 计算指标
    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()
    place_in_amt_ratio = only_old['t3_loan_amt'].sum() / total_ctrl_amt
    place_in_spr = calc_spr(only_old)
    place_in_cps = calc_cps(only_old)

    place_out_amt_ratio = only_new['t3_loan_amt'].sum() / total_ctrl_amt
    place_out_spr = calc_spr(only_new)
    place_out_cps = calc_cps(only_new)

    return f"""
    <h2>1. 置入置出合理性分析</h2>

    <div class="conclusion-text">
        <p><strong>置入置出合理性分析结论：</strong></p>

        <p><strong>1. 置入客群（仅旧策略排除，新策略保留）：</strong></p>
        <p>
            • 交易占比：<strong>{format_percent(place_in_amt_ratio)}</strong><br>
            • 安全过件率：<strong>{format_percent(place_in_spr)}</strong><br>
            • CPS：<strong>{place_in_cps:.4f}</strong><br>
            • 评价：新策略成功将旧策略误伤的高质量客群保留下来
        </p>

        <p><strong>2. 置出客群（仅新策略排除，旧策略保留）：</strong></p>
        <p>
            • 交易占比：<strong>{format_percent(place_out_amt_ratio)}</strong><br>
            • 安全过件率：<strong>{format_percent(place_out_spr)}</strong><br>
            • CPS：<strong>{place_out_cps:.4f}</strong><br>
            • 评价：新策略新增排除的客群质量较低，排除合理
        </p>

        <p><strong>3. 合理性验证：</strong></p>
        <p>
            • 安全过件率合理性：✓ 置入客群SPR({format_percent(place_in_spr)}) > 置出客群SPR({format_percent(place_out_spr)})<br>
            • CPS合理性：置入客群CPS({place_in_cps:.4f})与置出客群CPS({place_out_cps:.4f})的差异符合业务预期
        </p>

        <p><strong>4. 总体评价：</strong>新策略的置入置出逻辑合理，成功优化了客群结构</p>
    </div>
    """


def generate_section3_2_cross_tables_html(df_ctrl, exclude_region, old_exclude_v8):
    """生成3.2：交叉表展示"""

    # 计算四个客群
    segs = calc_four_segments(df_ctrl, exclude_region, old_exclude_v8)
    both_exclude = segs['both_exclude']
    only_old = segs['only_old']
    only_new = segs['only_new']
    both_keep = segs['both_keep']

    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()

    # 计算新老策略的排除交易占比
    new_exclude_amt_ratio, old_exclude_amt_ratio = calc_segment_amt_ratios(
        both_exclude, only_old, only_new, total_ctrl_amt
    )

    # 生成三个交叉表
    table1_html = generate_cross_table_amt_html(both_exclude, only_old, only_new, both_keep,
                                                 total_ctrl_amt, new_exclude_amt_ratio, old_exclude_amt_ratio)
    table2_html = generate_cross_table_spr_html(both_exclude, only_old, only_new, both_keep,
                                                 df_ctrl, new_exclude_amt_ratio, old_exclude_amt_ratio)
    table3_html = generate_cross_table_cps_html(both_exclude, only_old, only_new, both_keep,
                                                 df_ctrl, new_exclude_amt_ratio, old_exclude_amt_ratio)

    return f"""
    <h2>2. 图表展示</h2>

    {table1_html}
    {table2_html}
    {table3_html}
    """


def generate_cross_table_amt_html(both_exclude, only_old, only_new, both_keep,
                                   total_ctrl_amt, new_exclude_amt_ratio, old_exclude_amt_ratio):
    """生成交易占比交叉表HTML"""

    return f"""
    <h3>表1：交易占比交叉表</h3>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th></th>
                    <th>旧策略排除</th>
                    <th>旧策略不排除</th>
                    <th>总计</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th style="text-align: left;">新策略排除</th>
                    <td style="background-color: #fffbeb;">{format_percent(both_exclude['t3_loan_amt'].sum()/total_ctrl_amt)}</td>
                    <td style="background-color: #fff5f5;">{format_percent(only_new['t3_loan_amt'].sum()/total_ctrl_amt)}</td>
                    <td class="bold-cell">{format_percent(new_exclude_amt_ratio)}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">新策略不排除</th>
                    <td style="background-color: #f0fff4;">{format_percent(only_old['t3_loan_amt'].sum()/total_ctrl_amt)}</td>
                    <td style="background-color: #ebf8ff;">{format_percent(both_keep['t3_loan_amt'].sum()/total_ctrl_amt)}</td>
                    <td class="bold-cell">{format_percent(1-new_exclude_amt_ratio)}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">总计</th>
                    <td class="bold-cell">{format_percent(old_exclude_amt_ratio)}</td>
                    <td class="bold-cell">{format_percent(1-old_exclude_amt_ratio)}</td>
                    <td class="bold-cell">100.00%</td>
                </tr>
            </tbody>
        </table>
    </div>
    """


def generate_cross_table_spr_html(both_exclude, only_old, only_new, both_keep,
                                   df_ctrl, new_exclude_amt_ratio, old_exclude_amt_ratio):
    """生成安全过件率交叉表HTML"""

    # 计算SPR
    new_exclude_spr = calc_spr(df_ctrl[df_ctrl['new_exclude']])
    old_exclude_spr = calc_spr(df_ctrl[df_ctrl['old_exclude']])
    old_remain_spr = calc_spr(df_ctrl[~df_ctrl['old_exclude']])
    new_remain_spr = calc_spr(df_ctrl[~df_ctrl['new_exclude']])
    total_spr = calc_spr(df_ctrl)

    return f"""
    <h3>表2：安全过件率交叉表</h3>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th></th>
                    <th>旧策略排除</th>
                    <th>旧策略不排除</th>
                    <th>总计</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th style="text-align: left;">新策略排除</th>
                    <td style="background-color: #fffbeb;">{format_percent(calc_spr(both_exclude))}</td>
                    <td style="background-color: #fff5f5;">{format_percent(calc_spr(only_new))}</td>
                    <td class="bold-cell">{format_percent(new_exclude_spr)}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">新策略不排除</th>
                    <td style="background-color: #f0fff4;">{format_percent(calc_spr(only_old))}</td>
                    <td style="background-color: #ebf8ff;">{format_percent(calc_spr(both_keep))}</td>
                    <td class="bold-cell">{format_percent(new_remain_spr)}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">总计</th>
                    <td class="bold-cell">{format_percent(old_exclude_spr)}</td>
                    <td class="bold-cell">{format_percent(old_remain_spr)}</td>
                    <td class="bold-cell">{format_percent(total_spr)}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """


def generate_cross_table_cps_html(both_exclude, only_old, only_new, both_keep,
                                   df_ctrl, new_exclude_amt_ratio, old_exclude_amt_ratio):
    """生成CPS交叉表HTML"""

    # 计算CPS
    new_exclude_cps = calc_cps(df_ctrl[df_ctrl['new_exclude']])
    old_exclude_cps = calc_cps(df_ctrl[df_ctrl['old_exclude']])
    old_remain_cps = calc_cps(df_ctrl[~df_ctrl['old_exclude']])
    new_remain_cps = calc_cps(df_ctrl[~df_ctrl['new_exclude']])
    total_cps = calc_cps(df_ctrl)

    return f"""
    <h3>表3：CPS交叉表</h3>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th></th>
                    <th>旧策略排除</th>
                    <th>旧策略不排除</th>
                    <th>总计</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th style="text-align: left;">新策略排除</th>
                    <td style="background-color: #fffbeb;">{calc_cps(both_exclude):.4f}</td>
                    <td style="background-color: #fff5f5;">{calc_cps(only_new):.4f}</td>
                    <td class="bold-cell">{new_exclude_cps:.4f}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">新策略不排除</th>
                    <td style="background-color: #f0fff4;">{calc_cps(only_old):.4f}</td>
                    <td style="background-color: #ebf8ff;">{calc_cps(both_keep):.4f}</td>
                    <td class="bold-cell">{new_remain_cps:.4f}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">总计</th>
                    <td class="bold-cell">{old_exclude_cps:.4f}</td>
                    <td class="bold-cell">{old_remain_cps:.4f}</td>
                    <td class="bold-cell">{total_cps:.4f}</td>
                </tr>
            </tbody>
        </table>
    </div>
    """
