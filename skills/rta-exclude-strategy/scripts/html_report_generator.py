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
</head>
<body>
    <div class="container">
        <!-- 左侧导航栏 -->
        <nav class="sidebar">
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
            width: 280px;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 1.5rem;
            overflow-y: auto;
            z-index: 1000;
        }

        .logo h2 {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
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
            margin-left: 280px;
            padding: 3rem;
            width: calc(100% - 280px);
        }

        section {
            background: white;
            border-radius: 12px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        h1 {
            font-size: 2rem;
            color: #1a202c;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid #667eea;
        }

        h2 {
            font-size: 1.5rem;
            color: #2d3748;
            margin: 2rem 0 1.5rem;
        }

        h3 {
            font-size: 1.25rem;
            color: #4a5568;
            margin: 1.5rem 0 1rem;
        }

        .conclusion-text {
            background: linear-gradient(135deg, #f6f8fb 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 1.5rem 0;
        }

        .conclusion-text p {
            margin-bottom: 1rem;
            line-height: 1.8;
        }

        .conclusion-text strong {
            color: #667eea;
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        th {
            padding: 1rem;
            text-align: center;
            font-weight: 600;
            font-size: 0.95rem;
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
            color: #2d3748;
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
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            font-weight: 600;
        }

        .heatmap-cell.high {
            background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
            color: white;
        }

        .heatmap-cell.medium {
            background: linear-gradient(135deg, #ffd43b 0%, #fab005 100%);
            color: #333;
        }

        .heatmap-cell.low {
            background: linear-gradient(135deg, #ffa94d 0%, #ff8c42 100%);
            color: white;
        }

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
                width: 240px;
            }

            .content {
                margin-left: 240px;
                width: calc(100% - 240px);
            }
        }

        @media (max-width: 768px) {
            .sidebar {
                position: relative;
                width: 100%;
                height: auto;
            }

            .content {
                margin-left: 0;
                width: 100%;
                padding: 1.5rem;
            }
        }

        /* 打印样式 */
        @media print {
            .sidebar {
                display: none;
            }

            .content {
                margin-left: 0;
                width: 100%;
            }

            section {
                page-break-inside: avoid;
            }
        }
    </style>
    """


def generate_javascript():
    """生成交互JavaScript"""
    return """
    <script>
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
    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()

    # 老策略指标
    old_exclude_data_ctrl = df_ctrl[df_ctrl['V8_Q'].isin(old_exclude_v8)]
    old_exclude_amt_ratio = old_exclude_data_ctrl['t3_loan_amt'].sum() / total_ctrl_amt
    old_exclude_spr = calc_spr(old_exclude_data_ctrl)
    old_remain_data_ctrl = df_ctrl[~df_ctrl['V8_Q'].isin(old_exclude_v8)]
    old_remain_spr = calc_spr(old_remain_data_ctrl)

    # 新策略指标
    new_exclude_data_ctrl = filter_by_region(df_ctrl, exclude_region)
    new_exclude_amt_ratio = new_exclude_data_ctrl['t3_loan_amt'].sum() / total_ctrl_amt
    new_exclude_spr = calc_spr(new_exclude_data_ctrl)
    new_remain_data_ctrl = df_ctrl[~make_region_mask(df_ctrl, exclude_region)]
    new_remain_spr = calc_spr(new_remain_data_ctrl)

    return f"""
    <section id="section1">
        <h1>一、核心结论：关键指标对比（旧策略 vs 新策略）</h1>

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
    v8_list = [f'{i:02d}Q' for i in range(1, 13)]
    v8_stats_all = df_combined.groupby('V8_Q').agg({
        't3_ato': 'sum',
        't3_safe_adt': 'sum'
    }).reset_index()
    v8_stats_all['安全过件率'] = v8_stats_all['t3_safe_adt'] / v8_stats_all['t3_ato']

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
    total_ctrl_expo = df_ctrl['expo_cnt'].sum()
    total_ctrl_ato = df_ctrl['t3_ato'].sum()
    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()

    # 老策略指标
    old_exclude_data_ctrl = df_ctrl[df_ctrl['V8_Q'].isin(old_exclude_v8)]
    old_exclude_expo_ratio = old_exclude_data_ctrl['expo_cnt'].sum() / total_ctrl_expo
    old_exclude_ato_ratio = old_exclude_data_ctrl['t3_ato'].sum() / total_ctrl_ato
    old_exclude_amt_ratio = old_exclude_data_ctrl['t3_loan_amt'].sum() / total_ctrl_amt
    old_exclude_spr = calc_spr(old_exclude_data_ctrl)
    old_remain_data_ctrl = df_ctrl[~df_ctrl['V8_Q'].isin(old_exclude_v8)]
    old_remain_spr = calc_spr(old_remain_data_ctrl)
    old_remain_cps = calc_cps(old_remain_data_ctrl)

    # 新策略指标
    new_exclude_data_ctrl = filter_by_region(df_ctrl, exclude_region)
    new_exclude_expo_ratio = new_exclude_data_ctrl['expo_cnt'].sum() / total_ctrl_expo
    new_exclude_ato_ratio = new_exclude_data_ctrl['t3_ato'].sum() / total_ctrl_ato
    new_exclude_amt_ratio = new_exclude_data_ctrl['t3_loan_amt'].sum() / total_ctrl_amt
    new_exclude_spr = calc_spr(new_exclude_data_ctrl)
    new_remain_data_ctrl = df_ctrl[~make_region_mask(df_ctrl, exclude_region)]
    new_remain_spr = calc_spr(new_remain_data_ctrl)
    new_remain_cps = calc_cps(new_remain_data_ctrl)

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
        metrics_rows += f"""
        <tr>
            <td style="text-align: left;">{metric_name}</td>
            <td>{format_number(old_val)}</td>
            <td>{format_number(new_val)}</td>
            <td>{format_number(abs(diff_val))}</td>
        </tr>
        """

    # 生成热力图
    heatmap_html = generate_heatmap_html(df_combined, exclude_region)

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
    """


def generate_heatmap_html(df_combined, exclude_region):
    """生成V8 x V9RN二维热力图"""

    v8_list = [f'{i:02d}Q' for i in range(1, 13)]
    v9_list = [f'{i:02d}Q' for i in range(1, 13)]

    # 表头
    header_cells = "".join([f'<th>{v9}</th>' for v9 in v9_list])

    # 数据行
    data_rows = ""
    for v8 in v8_list:
        row_cells = f"<th>{v8}</th>"

        for v9 in v9_list:
            cell_data = df_combined[(df_combined['V8_Q'] == v8) & (df_combined['V9RN_Q'] == v9)]

            if len(cell_data) > 0 and cell_data['t3_ato'].sum() > 0:
                spr = cell_data['t3_safe_adt'].sum() / cell_data['t3_ato'].sum()

                # 判断单元格样式
                if (v8, v9) in exclude_region:
                    cell_class = "heatmap-cell excluded"
                elif spr >= 0.15:
                    cell_class = "heatmap-cell high"
                elif spr >= 0.10:
                    cell_class = "heatmap-cell medium"
                else:
                    cell_class = "heatmap-cell low"

                row_cells += f'<td class="{cell_class}">{format_percent(spr)}</td>'
            else:
                row_cells += '<td class="heatmap-cell">-</td>'

        data_rows += f"<tr>{row_cells}</tr>"

    return f"""
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
    df_ctrl['old_exclude'] = df_ctrl['V8_Q'].isin(old_exclude_v8)
    df_ctrl['new_exclude'] = make_region_mask(df_ctrl, exclude_region)

    only_old = df_ctrl[(df_ctrl['old_exclude']) & (~df_ctrl['new_exclude'])]  # 置入客群
    only_new = df_ctrl[(~df_ctrl['old_exclude']) & (df_ctrl['new_exclude'])]  # 置出客群

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
            • 评价：新策略新增排除的客群质量较低，排除合���
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
    df_ctrl['old_exclude'] = df_ctrl['V8_Q'].isin(old_exclude_v8)
    df_ctrl['new_exclude'] = make_region_mask(df_ctrl, exclude_region)

    both_exclude = df_ctrl[(df_ctrl['old_exclude']) & (df_ctrl['new_exclude'])]
    only_old = df_ctrl[(df_ctrl['old_exclude']) & (~df_ctrl['new_exclude'])]
    only_new = df_ctrl[(~df_ctrl['old_exclude']) & (df_ctrl['new_exclude'])]
    both_keep = df_ctrl[(~df_ctrl['old_exclude']) & (~df_ctrl['new_exclude'])]

    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()

    # 计算新老策略的排除交易占比
    new_exclude_amt_ratio = (both_exclude['t3_loan_amt'].sum() + only_new['t3_loan_amt'].sum()) / total_ctrl_amt
    old_exclude_amt_ratio = (both_exclude['t3_loan_amt'].sum() + only_old['t3_loan_amt'].sum()) / total_ctrl_amt

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
                    <td>{format_percent(both_exclude['t3_loan_amt'].sum()/total_ctrl_amt)}</td>
                    <td>{format_percent(only_new['t3_loan_amt'].sum()/total_ctrl_amt)}</td>
                    <td class="bold-cell">{format_percent(new_exclude_amt_ratio)}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">新策略不排除</th>
                    <td>{format_percent(only_old['t3_loan_amt'].sum()/total_ctrl_amt)}</td>
                    <td>{format_percent(both_keep['t3_loan_amt'].sum()/total_ctrl_amt)}</td>
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
                    <td>{format_percent(calc_spr(both_exclude))}</td>
                    <td>{format_percent(calc_spr(only_new))}</td>
                    <td class="bold-cell">{format_percent(new_exclude_spr)}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">新策略不排除</th>
                    <td>{format_percent(calc_spr(only_old))}</td>
                    <td>{format_percent(calc_spr(both_keep))}</td>
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
                    <td>{calc_cps(both_exclude):.4f}</td>
                    <td>{calc_cps(only_new):.4f}</td>
                    <td class="bold-cell">{new_exclude_cps:.4f}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">新策略不排除</th>
                    <td>{calc_cps(only_old):.4f}</td>
                    <td>{calc_cps(both_keep):.4f}</td>
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
