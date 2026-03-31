"""
可视化模块
为HTML报告提供交互式图表生成能力
使用纯HTML/CSS/SVG实现,不依赖外部库
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any


# ============================================================================
# 颜色工具函数
# ============================================================================

def value_to_color(value, min_val, max_val, color_scheme='red_green'):
    """
    将数值映射到颜色渐变

    Args:
        value: 当前值
        min_val: 最小值
        max_val: 最大值
        color_scheme: 颜色方案 ('red_green', 'blue_red', 'gray')

    Returns:
        str: RGB颜色字符串
    """
    if pd.isna(value) or min_val == max_val:
        return 'rgb(240, 240, 240)'

    # 归一化到0-1
    normalized = (value - min_val) / (max_val - min_val)
    normalized = max(0, min(1, normalized))

    if color_scheme == 'red_green':
        # 低值红色 -> 高值绿色
        r = int(255 * (1 - normalized))
        g = int(255 * normalized)
        b = 50
        return f'rgb({r}, {g}, {b})'

    elif color_scheme == 'blue_red':
        # 低值蓝色 -> 高值红色
        r = int(255 * normalized)
        g = 50
        b = int(255 * (1 - normalized))
        return f'rgb({r}, {g}, {b})'

    elif color_scheme == 'gray':
        # 灰度渐变
        gray = int(255 * (1 - normalized))
        return f'rgb({gray}, {gray}, {gray})'

    return 'rgb(200, 200, 200)'


def get_exclude_color():
    """获取排除区域标记颜色"""
    return 'rgb(255, 182, 193)'  # 浅红色


# ============================================================================
# 1. 二维热力图 (V8 x V9RN 交叉表)
# ============================================================================

def generate_heatmap_html(df_combined: pd.DataFrame,
                          exclude_region: List[Tuple[str, str]],
                          metric: str = 'spr') -> str:
    """
    生成V8 x V9RN二维热力图

    Args:
        df_combined: 全量数据
        exclude_region: 排除区域列表
        metric: 显示指标 ('spr': 安全过件率, 'count': 样本量, 'amt': 交易金额)

    Returns:
        str: HTML字符串
    """
    v8_list = [f'{i:02d}Q' for i in range(1, 13)]
    v9_list = [f'{i:02d}Q' for i in range(1, 13)]

    # 计算每个格子的指标值
    heatmap_data = {}
    values = []

    for v8 in v8_list:
        for v9 in v9_list:
            cell_data = df_combined[(df_combined['V8_Q'] == v8) & (df_combined['V9RN_Q'] == v9)]

            if len(cell_data) > 0 and cell_data['t3_ato'].sum() > 0:
                if metric == 'spr':
                    value = cell_data['t3_safe_adt'].sum() / cell_data['t3_ato'].sum()
                elif metric == 'count':
                    value = cell_data['t3_ato'].sum()
                elif metric == 'amt':
                    value = cell_data['t3_loan_amt'].sum()
                else:
                    value = 0

                heatmap_data[(v8, v9)] = value
                values.append(value)
            else:
                heatmap_data[(v8, v9)] = None

    # 计算颜色范围
    valid_values = [v for v in values if v is not None]
    min_val = min(valid_values) if valid_values else 0
    max_val = max(valid_values) if valid_values else 1

    # 生成HTML
    html_parts = []
    html_parts.append('''
<div class="heatmap-container" style="margin: 20px 0; overflow-x: auto;">
    <style>
        .heatmap-table {
            border-collapse: collapse;
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            font-size: 11px;
            margin: 0 auto;
        }
        .heatmap-table th {
            background-color: #f0f0f0;
            font-weight: bold;
            padding: 8px 6px;
            text-align: center;
            border: 1px solid #ddd;
        }
        .heatmap-table td {
            padding: 8px 6px;
            text-align: center;
            border: 1px solid #ddd;
            position: relative;
            cursor: pointer;
            transition: all 0.2s;
        }
        .heatmap-table td:hover {
            transform: scale(1.05);
            z-index: 10;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
        }
        .cell-value {
            font-weight: bold;
        }
        .cell-excluded {
            border: 3px solid #dc3545;
            box-shadow: inset 0 0 0 1px #dc3545;
        }
        .heatmap-legend {
            margin-top: 15px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
            font-size: 12px;
        }
        .legend-item {
            display: inline-block;
            margin-right: 20px;
        }
        .legend-color {
            display: inline-block;
            width: 20px;
            height: 20px;
            vertical-align: middle;
            margin-right: 5px;
            border: 1px solid #999;
        }
    </style>

    <table class="heatmap-table">
        <thead>
            <tr>
                <th>V8 \\ V9RN</th>
''')

    # 表头 - V9RN列
    for v9 in v9_list:
        html_parts.append(f'                <th>{v9}</th>\n')

    html_parts.append('''            </tr>
        </thead>
        <tbody>
''')

    # 数据行
    for v8 in v8_list:
        html_parts.append(f'            <tr>\n')
        html_parts.append(f'                <th>{v8}</th>\n')

        for v9 in v9_list:
            value = heatmap_data.get((v8, v9))
            is_excluded = (v8, v9) in exclude_region

            if value is not None:
                # 计算背景色
                bg_color = value_to_color(value, min_val, max_val, 'red_green')

                # 格式化显示值
                if metric == 'spr':
                    display_value = f'{value*100:.1f}%'
                elif metric == 'count':
                    display_value = f'{int(value):,}'
                else:
                    display_value = f'{value:.0f}'

                # 应用排除标记
                cell_class = 'cell-excluded' if is_excluded else ''
                excluded_text = '&#10;[已排除]' if is_excluded else ''

                html_parts.append(f'                <td class="{cell_class}" style="background-color: {bg_color};" ')
                html_parts.append(f'title="V8: {v8}, V9RN: {v9}&#10;值: {display_value}{excluded_text}">\n')
                html_parts.append(f'                    <span class="cell-value">{display_value}</span>\n')
                html_parts.append('                </td>\n')
            else:
                html_parts.append('                <td style="background-color: #f5f5f5; color: #999;">-</td>\n')

        html_parts.append('            </tr>\n')

    exclude_color = get_exclude_color()
    html_parts.append(f'''        </tbody>
    </table>

    <div class="heatmap-legend">
        <div class="legend-item">
            <span class="legend-color" style="background-color: rgb(255, 50, 50);"></span>
            <span>低值</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: rgb(50, 255, 50);"></span>
            <span>高值</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background-color: {exclude_color}; border: 2px solid #dc3545;"></span>
            <span>排除区域</span>
        </div>
    </div>
</div>
''')

    return ''.join(html_parts)


# ============================================================================
# 2. 指标对比柱状图 (新老策略对比)
# ============================================================================

def generate_comparison_chart_html(old_metrics: Dict[str, float],
                                   new_metrics: Dict[str, float],
                                   metric_names: List[str] = None) -> str:
    """
    生成新老策略指标对比柱状图

    Args:
        old_metrics: 老策略指标字典
        new_metrics: 新策略指标字典
        metric_names: 要显示的指标名称列表

    Returns:
        str: HTML/SVG字符串
    """
    if metric_names is None:
        metric_names = ['排除交易占比', '排除客群安全过件率', '保留客群安全过件率', '保留客群CPS']

    # 过滤存在的指标
    metric_names = [m for m in metric_names if m in old_metrics and m in new_metrics]

    if not metric_names:
        return '<p>无可用指标数据</p>'

    # SVG参数
    width = 800
    height = 400
    margin = {'top': 40, 'right': 120, 'bottom': 80, 'left': 80}
    chart_width = width - margin['left'] - margin['right']
    chart_height = height - margin['top'] - margin['bottom']

    # 计算柱状图参数
    n_metrics = len(metric_names)
    bar_group_width = chart_width / n_metrics
    bar_width = bar_group_width * 0.35
    bar_spacing = bar_group_width * 0.1

    # 计算Y轴范围
    all_values = [old_metrics[m] for m in metric_names] + [new_metrics[m] for m in metric_names]
    max_value = max(all_values) * 1.1
    min_value = min(0, min(all_values) * 0.9)

    def value_to_y(val):
        """将数值转换为Y坐标"""
        return chart_height - ((val - min_value) / (max_value - min_value) * chart_height)

    # 生成SVG
    html_parts = []
    html_parts.append(f'''
<div class="comparison-chart-container" style="margin: 20px 0;">
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <style>
                .chart-title {{ font-family: 'Microsoft YaHei', Arial, sans-serif; font-size: 16px; font-weight: bold; }}
                .axis-label {{ font-family: 'Microsoft YaHei', Arial, sans-serif; font-size: 12px; }}
                .bar-label {{ font-family: 'Microsoft YaHei', Arial, sans-serif; font-size: 10px; font-weight: bold; }}
                .legend-text {{ font-family: 'Microsoft YaHei', Arial, sans-serif; font-size: 12px; }}
                .old-bar {{ fill: #6c757d; opacity: 0.8; }}
                .old-bar:hover {{ opacity: 1; }}
                .new-bar {{ fill: #28a745; opacity: 0.8; }}
                .new-bar:hover {{ opacity: 1; }}
            </style>
        </defs>

        <!-- 标题 -->
        <text x="{width/2}" y="25" text-anchor="middle" class="chart-title">新老策略指标对比</text>

        <!-- 坐标轴 -->
        <g transform="translate({margin['left']}, {margin['top']})">
            <!-- Y轴 -->
            <line x1="0" y1="0" x2="0" y2="{chart_height}" stroke="#333" stroke-width="2"/>
            <!-- X轴 -->
            <line x1="0" y1="{chart_height}" x2="{chart_width}" y2="{chart_height}" stroke="#333" stroke-width="2"/>
''')

    # Y轴刻度
    n_ticks = 5
    for i in range(n_ticks + 1):
        tick_value = min_value + (max_value - min_value) * i / n_ticks
        y = value_to_y(tick_value)

        # 刻度线
        html_parts.append(f'            <line x1="-5" y1="{y}" x2="0" y2="{y}" stroke="#333" stroke-width="1"/>\n')

        # 刻度标签
        if tick_value < 1:
            label = f'{tick_value*100:.1f}%'
        else:
            label = f'{tick_value:.4f}'
        html_parts.append(f'            <text x="-10" y="{y+4}" text-anchor="end" class="axis-label">{label}</text>\n')

    # 绘制柱状图
    for i, metric_name in enumerate(metric_names):
        x_center = (i + 0.5) * bar_group_width

        # 老策略柱
        old_val = old_metrics[metric_name]
        old_bar_height = abs(value_to_y(old_val) - value_to_y(0))
        old_bar_y = min(value_to_y(old_val), value_to_y(0))
        old_bar_x = x_center - bar_width - bar_spacing/2

        old_val_display = f'{old_val*100:.2f}%' if old_val < 1 else f'{old_val:.4f}'
        html_parts.append(f'            <rect class="old-bar" x="{old_bar_x}" y="{old_bar_y}" ')
        html_parts.append(f'width="{bar_width}" height="{old_bar_height}">\n')
        html_parts.append(f'                <title>旧策略 - {metric_name}: {old_val_display}</title>\n')
        html_parts.append('            </rect>\n')

        # 新策略柱
        new_val = new_metrics[metric_name]
        new_bar_height = abs(value_to_y(new_val) - value_to_y(0))
        new_bar_y = min(value_to_y(new_val), value_to_y(0))
        new_bar_x = x_center + bar_spacing/2

        new_val_display = f'{new_val*100:.2f}%' if new_val < 1 else f'{new_val:.4f}'
        html_parts.append(f'            <rect class="new-bar" x="{new_bar_x}" y="{new_bar_y}" ')
        html_parts.append(f'width="{bar_width}" height="{new_bar_height}">\n')
        html_parts.append(f'                <title>新策略 - {metric_name}: {new_val_display}</title>\n')
        html_parts.append('            </rect>\n')

        # X轴标签
        label_lines = metric_name.split('客群')
        y_offset = chart_height + 20
        for line in label_lines:
            html_parts.append(f'            <text x="{x_center}" y="{y_offset}" text-anchor="middle" class="axis-label">{line}</text>\n')
            y_offset += 15

    # 图例
    legend_x = chart_width + 20
    legend_y = 20

    html_parts.append(f'''            <!-- 图例 -->
            <rect x="{legend_x}" y="{legend_y}" width="20" height="15" class="old-bar"/>
            <text x="{legend_x + 25}" y="{legend_y + 12}" class="legend-text">旧策略</text>

            <rect x="{legend_x}" y="{legend_y + 25}" width="20" height="15" class="new-bar"/>
            <text x="{legend_x + 25}" y="{legend_y + 37}" class="legend-text">新策略</text>
        </g>
    </svg>
</div>
''')

    return ''.join(html_parts)


# ============================================================================
# 3. 交叉分析矩阵 (置入置出分析)
# ============================================================================

def generate_cross_analysis_matrix_html(groups_data: Dict[str, Dict[str, Any]]) -> str:
    """
    生成2x2交叉分析矩阵

    Args:
        groups_data: 四个客群的数据字典

    Returns:
        str: HTML字符串
    """
    # 提取各客群数据
    both_exclude = groups_data.get('both_exclude', {})
    place_in = groups_data.get('place_in', {})
    place_out = groups_data.get('place_out', {})
    both_keep = groups_data.get('both_keep', {})

    # 格式化数值
    def format_metrics(data):
        amt = data.get('amt_ratio', 0) * 100
        spr = data.get('spr', 0) * 100
        cps = data.get('cps', 0)
        return amt, spr, cps

    both_exc_amt, both_exc_spr, both_exc_cps = format_metrics(both_exclude)
    place_in_amt, place_in_spr, place_in_cps = format_metrics(place_in)
    place_out_amt, place_out_spr, place_out_cps = format_metrics(place_out)
    both_keep_amt, both_keep_spr, both_keep_cps = format_metrics(both_keep)

    html = f'''
<div class="cross-matrix-container" style="margin: 20px 0;">
    <style>
        .matrix-table {{
            border-collapse: collapse;
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0 auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .matrix-table th {{
            background-color: #343a40;
            color: white;
            font-weight: bold;
            padding: 15px 20px;
            text-align: center;
            border: 1px solid #dee2e6;
            font-size: 13px;
        }}
        .matrix-table td {{
            padding: 20px;
            text-align: center;
            border: 1px solid #dee2e6;
            background-color: #fff;
            transition: all 0.2s;
        }}
        .matrix-table td:hover {{
            background-color: #f8f9fa;
            transform: scale(1.02);
        }}
        .matrix-label {{
            font-weight: bold;
            background-color: #6c757d !important;
            color: white !important;
        }}
        .cell-content {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }}
        .cell-title {{
            font-weight: bold;
            font-size: 14px;
            color: #343a40;
            margin-bottom: 5px;
        }}
        .metric-row {{
            display: flex;
            justify-content: space-between;
            width: 100%;
            font-size: 12px;
            padding: 3px 0;
        }}
        .metric-label {{
            color: #6c757d;
            font-weight: 500;
        }}
        .metric-value {{
            font-weight: bold;
            color: #212529;
        }}
        .highlight-place-in {{
            background-color: #d4edda !important;
        }}
        .highlight-place-out {{
            background-color: #f8d7da !important;
        }}
        .highlight-both-exclude {{
            background-color: #fff3cd !important;
        }}
        .highlight-both-keep {{
            background-color: #d1ecf1 !important;
        }}
    </style>

    <table class="matrix-table">
        <thead>
            <tr>
                <th style="width: 120px;">策略对比</th>
                <th style="width: 250px;">旧策略 <strong>排除</strong></th>
                <th style="width: 250px;">旧策略 <strong>不排除</strong></th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="matrix-label">新策略<br><strong>排除</strong></td>
                <td class="highlight-both-exclude">
                    <div class="cell-content">
                        <div class="cell-title">两策略都排除</div>
                        <div class="metric-row">
                            <span class="metric-label">交易占比:</span>
                            <span class="metric-value">{both_exc_amt:.2f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">安全过件率:</span>
                            <span class="metric-value">{both_exc_spr:.2f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">CPS:</span>
                            <span class="metric-value">{both_exc_cps:.4f}</span>
                        </div>
                    </div>
                </td>
                <td class="highlight-place-out">
                    <div class="cell-content">
                        <div class="cell-title">置出客群</div>
                        <div style="font-size: 11px; color: #856404; margin-bottom: 5px;">
                            (新策略新增排除)
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">交易占比:</span>
                            <span class="metric-value">{place_out_amt:.2f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">安全过件率:</span>
                            <span class="metric-value">{place_out_spr:.2f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">CPS:</span>
                            <span class="metric-value">{place_out_cps:.4f}</span>
                        </div>
                    </div>
                </td>
            </tr>
            <tr>
                <td class="matrix-label">新策略<br><strong>不排除</strong></td>
                <td class="highlight-place-in">
                    <div class="cell-content">
                        <div class="cell-title">置入客群</div>
                        <div style="font-size: 11px; color: #155724; margin-bottom: 5px;">
                            (新策略保留,旧策略误伤)
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">交易占比:</span>
                            <span class="metric-value">{place_in_amt:.2f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">安全过件率:</span>
                            <span class="metric-value">{place_in_spr:.2f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">CPS:</span>
                            <span class="metric-value">{place_in_cps:.4f}</span>
                        </div>
                    </div>
                </td>
                <td class="highlight-both-keep">
                    <div class="cell-content">
                        <div class="cell-title">两策略都保留</div>
                        <div class="metric-row">
                            <span class="metric-label">交易占比:</span>
                            <span class="metric-value">{both_keep_amt:.2f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">安全过件率:</span>
                            <span class="metric-value">{both_keep_spr:.2f}%</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">CPS:</span>
                            <span class="metric-value">{both_keep_cps:.4f}</span>
                        </div>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
</div>
'''

    return html


# ============================================================================
# 工具函数：从DataFrame计算四个客群数据
# ============================================================================

def calculate_groups_data(df_ctrl: pd.DataFrame,
                         exclude_region: List[Tuple[str, str]],
                         old_exclude_v8: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    从对照组数据计算四个客群的指标

    Args:
        df_ctrl: 对照组数据
        exclude_region: 新策略排除区域
        old_exclude_v8: 老策略排除规则

    Returns:
        dict: 四个客群的数据
    """
    # 标记老策略和新策略
    df_ctrl = df_ctrl.copy()
    df_ctrl['old_exclude'] = df_ctrl['V8_Q'].isin(old_exclude_v8)
    df_ctrl['new_exclude'] = df_ctrl.apply(
        lambda row: (row['V8_Q'], row['V9RN_Q']) in exclude_region, axis=1
    )

    # 分组
    both_exclude = df_ctrl[(df_ctrl['old_exclude']) & (df_ctrl['new_exclude'])]
    place_in = df_ctrl[(df_ctrl['old_exclude']) & (~df_ctrl['new_exclude'])]
    place_out = df_ctrl[(~df_ctrl['old_exclude']) & (df_ctrl['new_exclude'])]
    both_keep = df_ctrl[(~df_ctrl['old_exclude']) & (~df_ctrl['new_exclude'])]

    total_amt = df_ctrl['t3_loan_amt'].sum()

    def calc_metrics(df):
        """计算单个客群指标"""
        if len(df) == 0:
            return {'amt_ratio': 0, 'spr': 0, 'cps': 0}

        amt_ratio = df['t3_loan_amt'].sum() / total_amt if total_amt > 0 else 0
        spr = df['t3_safe_adt'].sum() / df['t3_ato'].sum() if df['t3_ato'].sum() > 0 else 0
        cps = df['cost'].sum() / df['t3_loan_amt'].sum() if df['t3_loan_amt'].sum() > 0 else 0

        return {'amt_ratio': amt_ratio, 'spr': spr, 'cps': cps}

    return {
        'both_exclude': calc_metrics(both_exclude),
        'place_in': calc_metrics(place_in),
        'place_out': calc_metrics(place_out),
        'both_keep': calc_metrics(both_keep)
    }


# ============================================================================
# 完整HTML报告生成器
# ============================================================================

def generate_full_html_report(result: Dict[str, Any],
                              old_exclude_rule: List[str],
                              output_path: str = None) -> str:
    """
    生成完整的HTML报告

    Args:
        result: 算法结果字典
        old_exclude_rule: 老策略排除规则
        output_path: 输出路径

    Returns:
        str: 生成的报告文件路径
    """
    from datetime import datetime
    from report_generator import (
        convert_old_rule_to_quantile, calc_spr, calc_cps
    )

    # 提取数据
    df_combined = result['df_combined']
    df_ctrl = result['df_ctrl']
    exclude_region = result['exclude_region']

    # 转换老策略规则
    old_exclude_v8 = convert_old_rule_to_quantile(old_exclude_rule)

    # 计算关键指标
    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()

    # 老策略指标
    old_exclude_data = df_ctrl[df_ctrl['V8_Q'].isin(old_exclude_v8)]
    old_metrics = {
        '排除交易占比': old_exclude_data['t3_loan_amt'].sum() / total_ctrl_amt,
        '排除客群安全过件率': calc_spr(old_exclude_data),
        '保留客群安全过件率': calc_spr(df_ctrl[~df_ctrl['V8_Q'].isin(old_exclude_v8)]),
        '保留客群CPS': calc_cps(df_ctrl[~df_ctrl['V8_Q'].isin(old_exclude_v8)])
    }

    # 新策略指标
    new_exclude_data = df_ctrl[df_ctrl.apply(
        lambda row: (row['V8_Q'], row['V9RN_Q']) in exclude_region, axis=1
    )]
    new_metrics = {
        '排除交易占比': new_exclude_data['t3_loan_amt'].sum() / total_ctrl_amt,
        '排除客群安全过件率': calc_spr(new_exclude_data),
        '保留客群安全过件率': calc_spr(df_ctrl[~df_ctrl.apply(
            lambda row: (row['V8_Q'], row['V9RN_Q']) in exclude_region, axis=1
        )]),
        '保留客群CPS': calc_cps(df_ctrl[~df_ctrl.apply(
            lambda row: (row['V8_Q'], row['V9RN_Q']) in exclude_region, axis=1
        )])
    }

    # 计算四个客群数据
    groups_data = calculate_groups_data(df_ctrl, exclude_region, old_exclude_v8)

    # 生成各个图表
    heatmap = generate_heatmap_html(df_combined, exclude_region, 'spr')
    comparison_chart = generate_comparison_chart_html(old_metrics, new_metrics)
    cross_matrix = generate_cross_analysis_matrix_html(groups_data)

    # 获取当前时间
    now = datetime.now()
    timestamp_display = now.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_file = now.strftime('%Y%m%d_%H%M%S')

    # 组装HTML
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RTA排除策略分析报告 - {now.strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #343a40;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .section h3 {{
            color: #495057;
            margin-top: 20px;
        }}
        .footer {{
            text-align: center;
            color: #6c757d;
            padding: 20px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>RTA排除策略分析报告</h1>
        <p>生成时间: {timestamp_display}</p>
    </div>

    <div class="section">
        <h2>一、核心结论</h2>
        <h3>1. 新老策略对比</h3>
        {comparison_chart}
    </div>

    <div class="section">
        <h2>二、排除策略制定</h2>
        <h3>1. V8 x V9RN 二维热力图(安全过件率)</h3>
        <p style="color: #6c757d; font-size: 13px;">
            颜色说明: 绿色表示高安全过件率,红色表示低安全过件率。红框标记为新策略排除区域。
        </p>
        {heatmap}
    </div>

    <div class="section">
        <h2>三、合理性评估</h2>
        <h3>1. 置入置出分析矩阵</h3>
        <p style="color: #6c757d; font-size: 13px;">
            矩阵展示了新老策略在四个客群上的表现差异,用于验证策略调整的合理性。
        </p>
        {cross_matrix}
    </div>

    <div class="footer">
        <p>本报告由 RTA 排除策略分析工具自动生成</p>
        <p>&copy; 2024 数禾科技 - Data Science Team</p>
    </div>
</body>
</html>
'''

    # 保存文件
    if output_path is None:
        output_path = '.'

    file_path = f'{output_path}/RTA排除策略报告_{timestamp_file}.html'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nHTML报告已生成: {file_path}")
    return file_path
