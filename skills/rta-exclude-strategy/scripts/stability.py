"""
PSI (Population Stability Index) 时序稳定性检验模块
用于评估排除策略在不同时间段的稳定性
"""
import json
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np

from data_preprocessing import load_data, preprocess_data, split_control_group
from utils import make_region_mask, filter_by_region, calc_spr


# ============================================================================
# PSI 核心计算
# ============================================================================

def calc_psi(expected, actual, bins=10):
    """
    计算 PSI (Population Stability Index)

    Args:
        expected: 基准期分布（array-like，如各格子的交易占比）
        actual: 对比期分布（array-like）
        bins: 分箱数（当传入原始数值序列而非已归一化占比时使用）

    Returns:
        float: PSI 值
        - < 0.1: 稳定
        - 0.1-0.25: 需关注
        - > 0.25: 不稳定

    Notes:
        若传入已归一化的占比向量（sum≈1），直接按公式计算。
        若传入原始数值序列（sum>>1），先分箱归一化再计算。
        0 值用 0.0001 替换防止 log(0)。
    """
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)

    # 判断是否已是归一化占比（各元素之和接近 1）
    if abs(expected.sum() - 1.0) < 0.01 and abs(actual.sum() - 1.0) < 0.01:
        # 已是占比向量，直接计算
        exp_pct = expected
        act_pct = actual
    else:
        # 原始数值序列，按分位数分箱
        combined = np.concatenate([expected, actual])
        breakpoints = np.percentile(combined, np.linspace(0, 100, bins + 1))
        breakpoints = np.unique(breakpoints)

        exp_counts, _ = np.histogram(expected, bins=breakpoints)
        act_counts, _ = np.histogram(actual, bins=breakpoints)

        exp_pct = exp_counts / (expected.sum() if expected.sum() > 0 else 1)
        act_pct = act_counts / (actual.sum() if actual.sum() > 0 else 1)

    # 防止 log(0)
    exp_pct = np.where(exp_pct == 0, 0.0001, exp_pct)
    act_pct = np.where(act_pct == 0, 0.0001, act_pct)

    psi = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return float(psi)


def _stability_level(psi_value):
    """PSI 值转换为稳定性等级字符串"""
    if psi_value < 0.1:
        return 'stable'
    elif psi_value <= 0.25:
        return 'warning'
    else:
        return 'unstable'


# ============================================================================
# 策略级 PSI 计算
# ============================================================================

def calc_strategy_psi(df_base, df_compare, exclude_region):
    """
    计算排除策略在两期数据间的 PSI

    对比维度：
    1. 各格子交易占比分布的 PSI
    2. 各格子 SPR 分布的 PSI
    3. 排除区域内交易占比的变化

    Args:
        df_base: 基准期 DataFrame（已预处理，含 V8_Q / V9RN_Q / t3_loan_amt / t3_ato / t3_safe_adt）
        df_compare: 对比期 DataFrame（同上）
        exclude_region: 排除区域，list/set of (v8_q, v9rn_q) tuples

    Returns:
        dict: {
            'volume_psi': float,            # 交易占比分布 PSI
            'spr_psi': float,               # SPR 分布 PSI
            'exclude_volume_change': float,  # 排除区域交易占比变化率（对比期 - 基准期）
            'stability_level': str,          # 'stable' / 'warning' / 'unstable'（基于 volume_psi）
            'details': pd.DataFrame          # 逐格子对比明细
        }
    """
    v8_list = [f'{i:02d}Q' for i in range(1, 13)]
    v9_list = [f'{i:02d}Q' for i in range(1, 13)]
    cells = [(v8, v9) for v8 in v8_list for v9 in v9_list]

    base_total_amt = df_base['t3_loan_amt'].sum()
    cmp_total_amt = df_compare['t3_loan_amt'].sum()

    rows = []
    base_vol_pcts = []
    cmp_vol_pcts = []
    base_sprs = []
    cmp_sprs = []

    for v8, v9 in cells:
        base_cell = df_base[(df_base['V8_Q'] == v8) & (df_base['V9RN_Q'] == v9)]
        cmp_cell = df_compare[(df_compare['V8_Q'] == v8) & (df_compare['V9RN_Q'] == v9)]

        base_amt = base_cell['t3_loan_amt'].sum()
        cmp_amt = cmp_cell['t3_loan_amt'].sum()

        base_vol_pct = base_amt / base_total_amt if base_total_amt > 0 else 0.0
        cmp_vol_pct = cmp_amt / cmp_total_amt if cmp_total_amt > 0 else 0.0

        base_spr = calc_spr(base_cell) if len(base_cell) > 0 else 0.0
        cmp_spr = calc_spr(cmp_cell) if len(cmp_cell) > 0 else 0.0

        is_excluded = (v8, v9) in exclude_region

        base_vol_pcts.append(base_vol_pct)
        cmp_vol_pcts.append(cmp_vol_pct)
        base_sprs.append(base_spr)
        cmp_sprs.append(cmp_spr)

        rows.append({
            'V8_Q': v8,
            'V9RN_Q': v9,
            'is_excluded': is_excluded,
            'base_vol_pct': base_vol_pct,
            'cmp_vol_pct': cmp_vol_pct,
            'vol_pct_change': cmp_vol_pct - base_vol_pct,
            'base_spr': base_spr,
            'cmp_spr': cmp_spr,
            'spr_change': cmp_spr - base_spr,
        })

    details = pd.DataFrame(rows)

    # 交易占比分布 PSI（按格子归一化向量）
    volume_psi = calc_psi(
        np.array(base_vol_pcts),
        np.array(cmp_vol_pcts)
    )

    # SPR 分布 PSI（仅考虑有数据的格子）
    valid_mask = (np.array(base_sprs) > 0) | (np.array(cmp_sprs) > 0)
    if valid_mask.sum() >= 2:
        spr_psi = calc_psi(
            np.array(base_sprs)[valid_mask],
            np.array(cmp_sprs)[valid_mask]
        )
    else:
        spr_psi = 0.0

    # 排除区域交易占比变化
    excl_mask = make_region_mask(df_base, exclude_region)
    base_excl_vol = df_base[excl_mask]['t3_loan_amt'].sum() / base_total_amt if base_total_amt > 0 else 0.0

    excl_mask_cmp = make_region_mask(df_compare, exclude_region)
    cmp_excl_vol = df_compare[excl_mask_cmp]['t3_loan_amt'].sum() / cmp_total_amt if cmp_total_amt > 0 else 0.0

    exclude_volume_change = cmp_excl_vol - base_excl_vol

    stability_level = _stability_level(volume_psi)

    return {
        'volume_psi': volume_psi,
        'spr_psi': spr_psi,
        'exclude_volume_change': exclude_volume_change,
        'stability_level': stability_level,
        'details': details,
    }


# ============================================================================
# 多期稳定性分析
# ============================================================================

def run_stability_analysis(data_paths, ctrl_group_value, exclude_region,
                            model_x='V8', model_y='V9RN'):
    """
    多期稳定性分析

    以第一期数据作为基准期，逐期与基准期对比计算 PSI。

    Args:
        data_paths: list of str，多期数据文件路径（按时间排序）
        ctrl_group_value: 对照组标识
        exclude_region: 排除区域（来自主算法输出），list/set of (v8_q, v9rn_q) tuples
        model_x: X 轴模型名称（默认 V8）
        model_y: Y 轴模型名称（默认 V9RN）

    Returns:
        dict: {
            'psi_series': list[dict],   # 每期的 PSI 结果（含 period_label）
            'overall_stability': str,    # 总体稳定性评估
            'trend': str,               # 'improving' / 'stable' / 'degrading'
            'recommendation': str        # 建议
        }

    Raises:
        ValueError: 当 data_paths 少于 2 个时
    """
    if len(data_paths) < 2:
        raise ValueError("多期稳定性分析至少需要 2 个数据文件路径")

    # 加载并预处理所有期数据（对照组）
    period_dfs = []
    for path in data_paths:
        df = load_data(path, model_x=model_x, model_y=model_y)
        df = preprocess_data(df)
        _, df_ctrl = split_control_group(df, ctrl_group_value)
        period_dfs.append(df_ctrl)

    # 基准期为第一期
    df_base = period_dfs[0]

    psi_series = []
    for i, df_compare in enumerate(period_dfs[1:], start=1):
        period_label = f'T{i} vs T0'
        psi_result = calc_strategy_psi(df_base, df_compare, exclude_region)
        psi_result['period_label'] = period_label
        psi_result['period_index'] = i
        # details 不序列化到 psi_series 顶层，保留在字典中
        psi_series.append(psi_result)

    # 总体稳定性：取所有期 volume_psi 的最大值判断
    max_volume_psi = max(r['volume_psi'] for r in psi_series)
    overall_stability = _stability_level(max_volume_psi)

    # 趋势判断：基于 volume_psi 序列的线性方向
    if len(psi_series) >= 2:
        first_psi = psi_series[0]['volume_psi']
        last_psi = psi_series[-1]['volume_psi']
        delta = last_psi - first_psi
        if delta < -0.02:
            trend = 'improving'
        elif delta > 0.02:
            trend = 'degrading'
        else:
            trend = 'stable'
    else:
        trend = 'stable'

    # 建议文本
    recommendation = _generate_recommendation(overall_stability, trend, psi_series)

    return {
        'psi_series': psi_series,
        'overall_stability': overall_stability,
        'trend': trend,
        'recommendation': recommendation,
    }


def _generate_recommendation(overall_stability, trend, psi_series):
    """根据稳定性等级和趋势生成建议文本"""
    level_desc = {
        'stable': '稳定（PSI < 0.1）',
        'warning': '需关注（0.1 ≤ PSI ≤ 0.25）',
        'unstable': '不稳定（PSI > 0.25）',
    }
    trend_desc = {
        'improving': '逐期改善',
        'stable': '保持平稳',
        'degrading': '逐期恶化',
    }

    base = f"策略整体稳定性为【{level_desc.get(overall_stability, overall_stability)}】，趋势{trend_desc.get(trend, trend)}。"

    if overall_stability == 'stable':
        action = "当前排除策略跨期稳定性良好，可继续沿用。"
    elif overall_stability == 'warning':
        action = "建议关注各期人群分布变化，排查是否存在数据漂移，适时复盘策略阈值。"
    else:
        action = "策略稳定性不足，人群分布跨期变化显著，建议重新评估排除阈值或重新训练模型。"

    # 找出 PSI 最大的期
    if psi_series:
        worst = max(psi_series, key=lambda r: r['volume_psi'])
        detail = f"PSI 最大出现在 {worst['period_label']}，volume_psi={worst['volume_psi']:.4f}。"
    else:
        detail = ""

    return f"{base}{action}{detail}"


# ============================================================================
# HTML 报告片段生成
# ============================================================================

def generate_stability_html(stability_result):
    """
    生成稳定性报告 HTML 片段（可嵌入主报告）

    返回 HTML 字符串，包含：
    - PSI 趋势折线图（ECharts）
    - 稳定性等级色标
    - 逐期对比表

    Args:
        stability_result: run_stability_analysis() 的返回值

    Returns:
        str: HTML 片段字符串
    """
    psi_series = stability_result['psi_series']
    overall_stability = stability_result['overall_stability']
    trend = stability_result['trend']
    recommendation = stability_result['recommendation']

    if not psi_series:
        return "<p>无稳定性数据</p>"

    # ---- ECharts 折线图数据 ----
    period_labels = [r['period_label'] for r in psi_series]
    volume_psi_values = [round(r['volume_psi'], 4) for r in psi_series]
    spr_psi_values = [round(r['spr_psi'], 4) for r in psi_series]
    exclude_vol_changes = [round(r['exclude_volume_change'] * 100, 2) for r in psi_series]

    labels_json = json.dumps(period_labels, ensure_ascii=False)
    vol_psi_json = json.dumps(volume_psi_values)
    spr_psi_json = json.dumps(spr_psi_values)
    excl_change_json = json.dumps(exclude_vol_changes)

    chart_id = "stability_psi_trend"

    # ---- 稳定性等级色标 ----
    level_color = {
        'stable': '#38a169',
        'warning': '#d69e2e',
        'unstable': '#e53e3e',
    }
    level_label = {
        'stable': '稳定',
        'warning': '需关注',
        'unstable': '不稳定',
    }
    trend_label = {
        'improving': '逐期改善',
        'stable': '保持平稳',
        'degrading': '逐期恶化',
    }
    overall_color = level_color.get(overall_stability, '#718096')
    overall_text = level_label.get(overall_stability, overall_stability)
    trend_text = trend_label.get(trend, trend)

    # ---- 逐期对比表行 ----
    table_rows = ""
    for r in psi_series:
        vol_psi = r['volume_psi']
        spr_psi = r['spr_psi']
        excl_chg = r['exclude_volume_change'] * 100
        lvl = r['stability_level']
        lvl_color = level_color.get(lvl, '#718096')
        lvl_text = level_label.get(lvl, lvl)
        chg_sign = '+' if excl_chg >= 0 else ''
        table_rows += f"""
                <tr>
                    <td>{r['period_label']}</td>
                    <td>{vol_psi:.4f}</td>
                    <td>{spr_psi:.4f}</td>
                    <td>{chg_sign}{excl_chg:.2f}%</td>
                    <td><span style="color:{lvl_color}; font-weight:600;">{lvl_text}</span></td>
                </tr>"""

    # ---- PSI 参考线标注数据 ----
    mark_line_data = json.dumps([
        {"yAxis": 0.1, "name": "警戒线 0.1", "lineStyle": {"color": "#d69e2e", "type": "dashed"}},
        {"yAxis": 0.25, "name": "不稳定线 0.25", "lineStyle": {"color": "#e53e3e", "type": "dashed"}},
    ])

    html = f"""
<div style="background:white; border-radius:10px; padding:2rem 2.5rem; margin-bottom:1.5rem;
            box-shadow:0 1px 3px rgba(0,0,0,0.08); border-left:4px solid #2b6cb0;">

    <h1 style="font-size:1.5rem; color:#1a365d; margin-bottom:1.5rem; padding-bottom:0.75rem;
               border-bottom:2px solid #2b6cb0; font-weight:700;">
        PSI 时序稳定性检验
    </h1>

    <!-- 总体评估标签 -->
    <div style="display:flex; gap:1rem; margin-bottom:1.5rem; flex-wrap:wrap;">
        <div style="background:#f7fafc; border-radius:8px; padding:0.75rem 1.5rem;
                    border-left:4px solid {overall_color};">
            <span style="font-size:0.85rem; color:#718096;">总体稳定性</span><br>
            <span style="font-size:1.25rem; font-weight:700; color:{overall_color};">{overall_text}</span>
        </div>
        <div style="background:#f7fafc; border-radius:8px; padding:0.75rem 1.5rem;
                    border-left:4px solid #2b6cb0;">
            <span style="font-size:0.85rem; color:#718096;">趋势</span><br>
            <span style="font-size:1.25rem; font-weight:700; color:#2b6cb0;">{trend_text}</span>
        </div>
    </div>

    <!-- 建议文本 -->
    <div style="background:#f7fafc; padding:1rem 1.5rem; border-radius:8px;
                border-left:4px solid #2b6cb0; margin-bottom:1.5rem; font-size:0.9rem; line-height:1.8;">
        {recommendation}
    </div>

    <!-- PSI 趋势折线图 -->
    <h2 style="font-size:1.25rem; color:#1a365d; margin:1.5rem 0 1rem; font-weight:600;">
        PSI 趋势图
    </h2>
    <p style="font-size:0.85rem; color:#718096; margin-bottom:0.5rem;">
        交互式折线图（鼠标悬停查看各期 PSI 值）。橙色虚线=0.1警戒，红色虚线=0.25不稳定线。
    </p>
    <div id="{chart_id}" style="width:100%; height:380px;"></div>
    <script>
    (function() {{
        var chartDom = document.getElementById('{chart_id}');
        var myChart = echarts.init(chartDom);

        var periodLabels = {labels_json};
        var volPsiData = {vol_psi_json};
        var sprPsiData = {spr_psi_json};
        var exclChangeData = {excl_change_json};

        var option = {{
            tooltip: {{
                trigger: 'axis',
                formatter: function(params) {{
                    var period = params[0].axisValue;
                    var lines = ['<strong>' + period + '</strong>'];
                    params.forEach(function(p) {{
                        lines.push(p.marker + p.seriesName + ': ' + p.value);
                    }});
                    return lines.join('<br/>');
                }}
            }},
            legend: {{
                data: ['交易占比PSI', 'SPR分布PSI', '排除区域交易占比变化(%)'],
                top: 5,
                textStyle: {{ fontSize: 11 }}
            }},
            grid: {{
                left: '60px',
                right: '20px',
                top: '50px',
                bottom: '40px'
            }},
            xAxis: {{
                type: 'category',
                data: periodLabels,
                axisLabel: {{ fontSize: 11 }}
            }},
            yAxis: [
                {{
                    type: 'value',
                    name: 'PSI',
                    nameTextStyle: {{ fontSize: 11 }},
                    axisLabel: {{ fontSize: 11 }},
                    splitLine: {{ lineStyle: {{ type: 'dashed', color: '#e2e8f0' }} }}
                }},
                {{
                    type: 'value',
                    name: '变化(%)',
                    nameTextStyle: {{ fontSize: 11 }},
                    axisLabel: {{ fontSize: 11, formatter: '{{value}}%' }},
                    splitLine: {{ show: false }}
                }}
            ],
            series: [
                {{
                    name: '交易占比PSI',
                    type: 'line',
                    data: volPsiData,
                    yAxisIndex: 0,
                    symbol: 'circle',
                    symbolSize: 7,
                    lineStyle: {{ color: '#2b6cb0', width: 2 }},
                    itemStyle: {{ color: '#2b6cb0' }},
                    markLine: {{
                        silent: true,
                        symbol: 'none',
                        data: [
                            {{ yAxis: 0.1,  lineStyle: {{ color: '#d69e2e', type: 'dashed' }},
                               label: {{ formatter: '警戒 0.1', color: '#d69e2e', fontSize: 10 }} }},
                            {{ yAxis: 0.25, lineStyle: {{ color: '#e53e3e', type: 'dashed' }},
                               label: {{ formatter: '不稳定 0.25', color: '#e53e3e', fontSize: 10 }} }}
                        ]
                    }}
                }},
                {{
                    name: 'SPR分布PSI',
                    type: 'line',
                    data: sprPsiData,
                    yAxisIndex: 0,
                    symbol: 'diamond',
                    symbolSize: 7,
                    lineStyle: {{ color: '#38a169', width: 2 }},
                    itemStyle: {{ color: '#38a169' }}
                }},
                {{
                    name: '排除区域交易占比变化(%)',
                    type: 'bar',
                    data: exclChangeData,
                    yAxisIndex: 1,
                    barMaxWidth: 30,
                    itemStyle: {{
                        color: function(params) {{
                            return params.value >= 0 ? '#fc8d59' : '#2166ac';
                        }}
                    }}
                }}
            ]
        }};
        myChart.setOption(option);
        window.addEventListener('resize', function() {{ myChart.resize(); }});
    }})();
    </script>

    <!-- 稳定性等级说明 -->
    <div style="display:flex; gap:1rem; margin:1rem 0; flex-wrap:wrap; font-size:0.82rem;">
        <span style="background:#c6f6d5; color:#276749; padding:3px 10px; border-radius:10px;">
            PSI &lt; 0.1：稳定
        </span>
        <span style="background:#fefcbf; color:#744210; padding:3px 10px; border-radius:10px;">
            0.1 ≤ PSI ≤ 0.25：需关注
        </span>
        <span style="background:#fed7d7; color:#9b2c2c; padding:3px 10px; border-radius:10px;">
            PSI &gt; 0.25：不稳定
        </span>
    </div>

    <!-- 逐期对比表 -->
    <h2 style="font-size:1.25rem; color:#1a365d; margin:1.5rem 0 1rem; font-weight:600;">
        逐期 PSI 对比明细
    </h2>
    <div style="overflow-x:auto; margin:0.5rem 0;">
        <table style="width:100%; border-collapse:separate; border-spacing:0;
                      border-radius:8px; overflow:hidden;
                      box-shadow:0 1px 3px rgba(0,0,0,0.1);">
            <thead style="background:linear-gradient(135deg,#1a365d 0%,#2d4a7a 100%); color:white;">
                <tr>
                    <th style="padding:0.75rem 1rem; text-align:center; font-size:0.825rem;">期次</th>
                    <th style="padding:0.75rem 1rem; text-align:center; font-size:0.825rem;">交易占比PSI</th>
                    <th style="padding:0.75rem 1rem; text-align:center; font-size:0.825rem;">SPR分布PSI</th>
                    <th style="padding:0.75rem 1rem; text-align:center; font-size:0.825rem;">排除区域交易变化</th>
                    <th style="padding:0.75rem 1rem; text-align:center; font-size:0.825rem;">稳定性等级</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
</div>
"""
    return html
