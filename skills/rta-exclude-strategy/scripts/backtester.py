"""
批量回测框架
支持多期数据自动执行排除策略分析，输出时序趋势对比
"""

import pandas as pd
import numpy as np
import os
import glob
import sys
from datetime import datetime

# 确保当前目录在路径中（与 main.py 保持一致）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_preprocessing import load_data, preprocess_data, split_control_group, validate_data
from place_in_out_algorithm import run_place_in_out_algorithm
from utils import filter_by_region, calc_spr, calc_cps

try:
    from ilp_solver import run_ilp_algorithm, check_pulp_available
    ILP_AVAILABLE = check_pulp_available()
except ImportError:
    ILP_AVAILABLE = False


# ---------------------------------------------------------------------------
# 文件发现
# ---------------------------------------------------------------------------

def discover_data_files(data_dir, pattern='*.csv'):
    """
    发现目录下的数据文件，按文件名排序（假设文件名包含日期信息）

    支持多个 glob 模式，用逗号分隔（如 '*.csv,*.xlsx'）。

    Args:
        data_dir: 数据目录路径
        pattern: glob 模式字符串，多个模式用逗号分隔（默认 '*.csv'）

    Returns:
        list[dict]: [{'path': str, 'name': str, 'period': str}, ...]
            period 取文件名（不含扩展名），用于图表和报告中的时间轴标签
    """
    if not os.path.isdir(data_dir):
        return []

    patterns = [p.strip() for p in pattern.split(',')]
    found_paths = set()
    for pat in patterns:
        matched = glob.glob(os.path.join(data_dir, pat))
        found_paths.update(matched)

    # 按文件名字母序排序（文件名含日期时自然升序）
    sorted_paths = sorted(found_paths, key=lambda p: os.path.basename(p))

    result = []
    for path in sorted_paths:
        name = os.path.basename(path)
        period = os.path.splitext(name)[0]  # 去掉扩展名作为期次标签
        result.append({'path': path, 'name': name, 'period': period})

    return result


# ---------------------------------------------------------------------------
# 单期分析
# ---------------------------------------------------------------------------

def run_single_period(data_path, ctrl_group_value, spr_threshold=0.10,
                      max_exclude_ratio=0.20, algorithm='ilp',
                      model_x='V8', model_y='V9RN'):
    """
    对单期数据运行完整分析流程

    Args:
        data_path: 数据文件路径（CSV 或 Excel）
        ctrl_group_value: 对照组标识值
        spr_threshold: 安全过件率阈值（默认 0.10）
        max_exclude_ratio: 最大排除交易占比（默认 0.20）
        algorithm: 'greedy' | 'ilp'（默认 'ilp'，不可用时回退 greedy）
        model_x: X 轴模型名称（默认 'V8'）
        model_y: Y 轴模型名称（默认 'V9RN'）

    Returns:
        dict: {
            'period': str,          # 期次标签（文件名不含扩展名）
            'data_path': str,       # 原始文件路径
            'exclude_region': set,  # 最终排除格子集合（frozenset of tuples）
            'n_exclude_cells': int, # 排除格子数
            'spr': float,           # 排除区域 SPR
            'cps': float,           # 排除区域 CPS
            'exclude_ratio': float, # 对照组排除交易占比
            'total_volume': float,  # 对照组总交易额
            'exclude_volume': float,# 对照组被排除交易额
            'algorithm': str,       # 实际使用的算法
            'result': dict,         # 完整的算法结果 dict
            'error': None           # 正常时为 None，失败时为错误信息字符串
        }
    """
    period = os.path.splitext(os.path.basename(data_path))[0]

    # 失败时的占位返回结构
    def _error_record(msg):
        return {
            'period': period,
            'data_path': data_path,
            'exclude_region': set(),
            'n_exclude_cells': 0,
            'spr': float('nan'),
            'cps': float('nan'),
            'exclude_ratio': float('nan'),
            'total_volume': float('nan'),
            'exclude_volume': float('nan'),
            'algorithm': algorithm,
            'result': {},
            'error': msg,
        }

    try:
        # 1. 加载数据
        df = load_data(data_path, model_x=model_x, model_y=model_y)

        # 2. 预处理
        df = preprocess_data(df)

        # 3. 验证
        validate_data(df)

        # 4. 分离对照组
        df_combined, df_ctrl = split_control_group(df, ctrl_group_value)

        # 5. 选择算法（ILP 不可用时自动回退）
        actual_algorithm = algorithm
        if algorithm == 'ilp' and not ILP_AVAILABLE:
            actual_algorithm = 'greedy'

        if actual_algorithm == 'ilp':
            result = run_ilp_algorithm(
                df_combined, df_ctrl,
                spr_threshold=spr_threshold,
                max_exclude_ratio=max_exclude_ratio
            )
        else:
            result = run_place_in_out_algorithm(
                df_combined, df_ctrl,
                spr_threshold=spr_threshold,
                max_exclude_ratio=max_exclude_ratio
            )
            result['algorithm'] = 'greedy'

        # 6. 计算摘要指标
        exclude_region = result.get('exclude_region', [])
        exclude_set = set(map(tuple, exclude_region))

        total_volume = df_ctrl['t3_loan_amt'].sum()

        if exclude_set:
            exclude_data = filter_by_region(df_combined, exclude_set)
            exclude_ctrl_data = filter_by_region(df_ctrl, exclude_set)

            spr_val = calc_spr(exclude_data)
            cps_val = calc_cps(exclude_data)
            exclude_volume = exclude_ctrl_data['t3_loan_amt'].sum()
            exclude_ratio = exclude_volume / total_volume if total_volume > 0 else 0.0
        else:
            spr_val = float('nan')
            cps_val = float('nan')
            exclude_volume = 0.0
            exclude_ratio = 0.0

        return {
            'period': period,
            'data_path': data_path,
            'exclude_region': exclude_set,
            'n_exclude_cells': len(exclude_set),
            'spr': spr_val,
            'cps': cps_val,
            'exclude_ratio': exclude_ratio,
            'total_volume': float(total_volume),
            'exclude_volume': float(exclude_volume),
            'algorithm': actual_algorithm,
            'result': result,
            'error': None,
        }

    except Exception as exc:
        return _error_record(str(exc))


# ---------------------------------------------------------------------------
# 批量回测主函数
# ---------------------------------------------------------------------------

def run_backtest(data_dir, ctrl_group_value, spr_threshold=0.10,
                 max_exclude_ratio=0.20, algorithm='ilp',
                 model_x='V8', model_y='V9RN', pattern='*.csv'):
    """
    批量回测主函数

    遍历 data_dir 中匹配 pattern 的所有文件，对每期数据调用
    run_single_period，汇总时序趋势和策略一致性。

    Args:
        data_dir: 包含多期数据文件的目录
        ctrl_group_value: 对照组标识值
        spr_threshold: 安全过件率阈值（默认 0.10）
        max_exclude_ratio: 最大排除交易占比（默认 0.20）
        algorithm: 'greedy' | 'ilp'（默认 'ilp'）
        model_x: X 轴模型名称（默认 'V8'）
        model_y: Y 轴模型名称（默认 'V9RN'）
        pattern: 文件匹配模式，多模式用逗号分隔（默认 '*.csv'）

    Returns:
        dict: {
            'periods': list[dict],        # 每期的 run_single_period 返回值
            'summary': dict,              # 汇总统计
            'trend': pd.DataFrame,        # 时序趋势表（每期一行）
            'consistency_matrix': pd.DataFrame  # 两两期 Jaccard 相似度矩阵
        }
    """
    # 发现文件
    files = discover_data_files(data_dir, pattern=pattern)

    if not files:
        return {
            'periods': [],
            'summary': {
                'n_periods': 0,
                'avg_exclude_cells': float('nan'),
                'avg_spr': float('nan'),
                'avg_cps': float('nan'),
                'avg_exclude_ratio': float('nan'),
                'strategy_consistency': float('nan'),
            },
            'trend': pd.DataFrame(),
            'consistency_matrix': pd.DataFrame(),
        }

    print(f"\n{'='*80}")
    print(f"批量回测：发现 {len(files)} 个数据文件")
    print(f"{'='*80}")

    # 逐期执行
    period_results = []
    for i, file_info in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] 处理期次: {file_info['period']}")
        print(f"  文件: {file_info['path']}")
        rec = run_single_period(
            data_path=file_info['path'],
            ctrl_group_value=ctrl_group_value,
            spr_threshold=spr_threshold,
            max_exclude_ratio=max_exclude_ratio,
            algorithm=algorithm,
            model_x=model_x,
            model_y=model_y,
        )
        if rec['error']:
            print(f"  [ERROR] 期次 {file_info['period']} 分析失败: {rec['error']}")
        else:
            print(f"  排除格子: {rec['n_exclude_cells']}, "
                  f"SPR: {rec['spr']*100:.2f}%, "
                  f"排除占比: {rec['exclude_ratio']*100:.2f}%")
        period_results.append(rec)

    # 仅取成功的期次用于统计
    valid_results = [r for r in period_results if not r['error']]

    # 构建趋势 DataFrame
    trend_rows = []
    for r in period_results:
        trend_rows.append({
            'period': r['period'],
            'n_exclude_cells': r['n_exclude_cells'],
            'spr': r['spr'],
            'cps': r['cps'],
            'exclude_ratio': r['exclude_ratio'],
            'total_volume': r['total_volume'],
            'exclude_volume': r['exclude_volume'],
            'algorithm': r['algorithm'],
            'status': 'ok' if not r['error'] else 'error',
        })
    trend_df = pd.DataFrame(trend_rows)

    # 策略一致性矩阵（Jaccard）
    regions_list = [(r['period'], r['exclude_region']) for r in valid_results]
    consistency_matrix = _build_consistency_matrix(regions_list)

    # 汇总统计
    if valid_results:
        avg_exclude_cells = float(np.mean([r['n_exclude_cells'] for r in valid_results]))
        avg_spr = float(np.nanmean([r['spr'] for r in valid_results]))
        avg_cps = float(np.nanmean([r['cps'] for r in valid_results]))
        avg_exclude_ratio = float(np.nanmean([r['exclude_ratio'] for r in valid_results]))
        strategy_consistency = calc_strategy_consistency(
            [r['exclude_region'] for r in valid_results]
        )
    else:
        avg_exclude_cells = float('nan')
        avg_spr = float('nan')
        avg_cps = float('nan')
        avg_exclude_ratio = float('nan')
        strategy_consistency = float('nan')

    summary = {
        'n_periods': len(files),
        'n_valid_periods': len(valid_results),
        'avg_exclude_cells': avg_exclude_cells,
        'avg_spr': avg_spr,
        'avg_cps': avg_cps,
        'avg_exclude_ratio': avg_exclude_ratio,
        'strategy_consistency': strategy_consistency,
    }

    print(f"\n{'='*80}")
    print("批量回测完成")
    print(f"  有效期次: {len(valid_results)} / {len(files)}")
    print(f"  平均排除格子数: {avg_exclude_cells:.1f}")
    print(f"  平均 SPR: {avg_spr*100:.2f}%")
    print(f"  平均排除占比: {avg_exclude_ratio*100:.2f}%")
    print(f"  策略一致性: {strategy_consistency:.4f}")
    print(f"{'='*80}")

    return {
        'periods': period_results,
        'summary': summary,
        'trend': trend_df,
        'consistency_matrix': consistency_matrix,
    }


# ---------------------------------------------------------------------------
# 一致性计算
# ---------------------------------------------------------------------------

def calc_strategy_consistency(regions_list):
    """
    计算多期策略的一致性（平均成对 Jaccard 系数）

    Jaccard(A, B) = |A ∩ B| / |A ∪ B|

    Args:
        regions_list: list[set]，每期的排除格子集合

    Returns:
        float: 平均成对 Jaccard 系数；
               0 个或 1 个非空集合时返回 NaN；
               全为空集时返回 NaN
    """
    # 过滤掉空集
    non_empty = [r for r in regions_list if r]
    n = len(non_empty)

    if n < 2:
        return float('nan')

    scores = []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = non_empty[i], non_empty[j]
            intersection = len(a & b)
            union = len(a | b)
            if union > 0:
                scores.append(intersection / union)
            else:
                scores.append(0.0)

    return float(np.mean(scores)) if scores else float('nan')


def _build_consistency_matrix(regions_list):
    """
    构建两两期 Jaccard 相似度矩阵

    Args:
        regions_list: list[(period_label, region_set)]

    Returns:
        pd.DataFrame: 对称矩阵，行列均为期次标签
    """
    if not regions_list:
        return pd.DataFrame()

    labels = [p for p, _ in regions_list]
    regions = [r for _, r in regions_list]
    n = len(labels)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 1.0
            elif regions[i] or regions[j]:
                a, b = regions[i], regions[j]
                union = len(a | b)
                matrix[i][j] = len(a & b) / union if union > 0 else 0.0
            # 若两者均空，保持 0.0

    return pd.DataFrame(matrix, index=labels, columns=labels)


# ---------------------------------------------------------------------------
# HTML 报告生成
# ---------------------------------------------------------------------------

def generate_backtest_html(backtest_result):
    """
    生成回测报告 HTML 片段

    包含：
    - 趋势折线图（ECharts）：排除格子数、SPR、CPS、排除占比随时间变化
    - 策略一致性热力图（ECharts）：两两期 Jaccard 相似度
    - 汇总统计表

    Args:
        backtest_result: run_backtest 的返回值

    Returns:
        str: 完整的 HTML 字符串（含 <!DOCTYPE html> 外壳）
    """
    summary = backtest_result.get('summary', {})
    trend_df = backtest_result.get('trend', pd.DataFrame())
    consistency_matrix = backtest_result.get('consistency_matrix', pd.DataFrame())

    # ------------------------------------------------------------------
    # 汇总表数据
    # ------------------------------------------------------------------
    n_periods = summary.get('n_periods', 0)
    n_valid = summary.get('n_valid_periods', 0)
    avg_cells = summary.get('avg_exclude_cells', float('nan'))
    avg_spr = summary.get('avg_spr', float('nan'))
    avg_cps = summary.get('avg_cps', float('nan'))
    avg_ratio = summary.get('avg_exclude_ratio', float('nan'))
    consistency = summary.get('strategy_consistency', float('nan'))

    def _fmt_pct(v):
        return f"{v*100:.2f}%" if not (isinstance(v, float) and np.isnan(v)) else "N/A"

    def _fmt_num(v, decimals=1):
        return f"{v:.{decimals}f}" if not (isinstance(v, float) and np.isnan(v)) else "N/A"

    summary_rows_html = f"""
        <tr><td>回测期次数</td><td>{n_periods}</td></tr>
        <tr><td>有效期次数</td><td>{n_valid}</td></tr>
        <tr><td>平均排除格子数</td><td>{_fmt_num(avg_cells)}</td></tr>
        <tr><td>平均 SPR</td><td>{_fmt_pct(avg_spr)}</td></tr>
        <tr><td>平均 CPS</td><td>{_fmt_num(avg_cps, 4)}</td></tr>
        <tr><td>平均排除占比</td><td>{_fmt_pct(avg_ratio)}</td></tr>
        <tr><td>策略一致性（Jaccard）</td><td>{_fmt_num(consistency, 4)}</td></tr>
    """

    # ------------------------------------------------------------------
    # 趋势折线图数据
    # ------------------------------------------------------------------
    if not trend_df.empty:
        periods_json = str(list(trend_df['period'].astype(str))).replace("'", '"')
        cells_json = str([
            None if (isinstance(v, float) and np.isnan(v)) else round(float(v), 1)
            for v in trend_df['n_exclude_cells']
        ])
        spr_json = str([
            None if (isinstance(v, float) and np.isnan(v)) else round(float(v) * 100, 2)
            for v in trend_df['spr']
        ])
        cps_json = str([
            None if (isinstance(v, float) and np.isnan(v)) else round(float(v), 6)
            for v in trend_df['cps']
        ])
        ratio_json = str([
            None if (isinstance(v, float) and np.isnan(v)) else round(float(v) * 100, 2)
            for v in trend_df['exclude_ratio']
        ])
    else:
        periods_json = '[]'
        cells_json = '[]'
        spr_json = '[]'
        cps_json = '[]'
        ratio_json = '[]'

    # ------------------------------------------------------------------
    # 热力图数据
    # ------------------------------------------------------------------
    if not consistency_matrix.empty:
        heatmap_labels = str(list(consistency_matrix.columns.astype(str))).replace("'", '"')
        heatmap_data = []
        for i, row_label in enumerate(consistency_matrix.index):
            for j, col_label in enumerate(consistency_matrix.columns):
                val = consistency_matrix.iloc[i, j]
                heatmap_data.append([j, i, round(float(val), 4)])
        heatmap_data_json = str(heatmap_data)
        heatmap_n = len(consistency_matrix)
    else:
        heatmap_labels = '[]'
        heatmap_data_json = '[]'
        heatmap_n = 0

    # ------------------------------------------------------------------
    # 完整 HTML
    # ------------------------------------------------------------------
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RTA 排除策略 - 批量回测报告</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
      background: #0d1117;
      color: #c9d1d9;
      padding: 24px;
    }}
    h1 {{
      font-size: 22px;
      color: #58a6ff;
      margin-bottom: 6px;
    }}
    .subtitle {{
      font-size: 13px;
      color: #8b949e;
      margin-bottom: 24px;
    }}
    .section-title {{
      font-size: 15px;
      color: #79c0ff;
      font-weight: 600;
      margin: 28px 0 12px;
      padding-left: 10px;
      border-left: 3px solid #1f6feb;
    }}
    .chart-container {{
      background: #161b22;
      border: 1px solid #21262d;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 20px;
    }}
    .chart-box {{
      width: 100%;
      height: 340px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: #161b22;
      border: 1px solid #21262d;
      border-radius: 8px;
      overflow: hidden;
      font-size: 13px;
    }}
    th {{
      background: #1f6feb;
      color: #fff;
      padding: 10px 14px;
      text-align: left;
    }}
    td {{
      padding: 9px 14px;
      border-bottom: 1px solid #21262d;
      color: #c9d1d9;
    }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #1c2128; }}
  </style>
</head>
<body>
  <h1>RTA 排除策略 - 批量回测报告</h1>
  <div class="subtitle">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>

  <!-- 汇总统计 -->
  <div class="section-title">汇总统计</div>
  <table>
    <thead><tr><th>指标</th><th>数值</th></tr></thead>
    <tbody>{summary_rows_html}</tbody>
  </table>

  <!-- 趋势折线图 -->
  <div class="section-title">时序趋势</div>
  <div class="chart-container">
    <div id="trend-chart" class="chart-box"></div>
  </div>

  <!-- 策略一致性热力图 -->
  <div class="section-title">策略一致性热力图（Jaccard 系数）</div>
  <div class="chart-container">
    <div id="heatmap-chart" class="chart-box"></div>
  </div>

  <script>
    // ----------------------------------------------------------------
    // 趋势折线图
    // ----------------------------------------------------------------
    (function() {{
      var periods = {periods_json};
      var cellsData = {cells_json};
      var sprData = {spr_json};
      var cpsData = {cps_json};
      var ratioData = {ratio_json};

      var chart = echarts.init(document.getElementById('trend-chart'), 'dark');
      chart.setOption({{
        backgroundColor: 'transparent',
        tooltip: {{ trigger: 'axis' }},
        legend: {{
          data: ['排除格子数', 'SPR (%)', '排除占比 (%)'],
          textStyle: {{ color: '#c9d1d9' }}
        }},
        grid: {{ left: '3%', right: '4%', bottom: '3%', containLabel: true }},
        xAxis: {{
          type: 'category',
          data: periods,
          axisLabel: {{ color: '#8b949e', rotate: 30 }}
        }},
        yAxis: [
          {{
            type: 'value',
            name: '格子数',
            nameTextStyle: {{ color: '#8b949e' }},
            axisLabel: {{ color: '#8b949e' }}
          }},
          {{
            type: 'value',
            name: '%',
            nameTextStyle: {{ color: '#8b949e' }},
            axisLabel: {{ color: '#8b949e', formatter: '{{value}}%' }}
          }}
        ],
        series: [
          {{
            name: '排除格子数',
            type: 'line',
            yAxisIndex: 0,
            data: cellsData,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {{ color: '#58a6ff', width: 2 }},
            itemStyle: {{ color: '#58a6ff' }}
          }},
          {{
            name: 'SPR (%)',
            type: 'line',
            yAxisIndex: 1,
            data: sprData,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {{ color: '#3fb950', width: 2 }},
            itemStyle: {{ color: '#3fb950' }}
          }},
          {{
            name: '排除占比 (%)',
            type: 'line',
            yAxisIndex: 1,
            data: ratioData,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {{ color: '#f78166', width: 2 }},
            itemStyle: {{ color: '#f78166' }}
          }}
        ]
      }});
      window.addEventListener('resize', function() {{ chart.resize(); }});
    }})();

    // ----------------------------------------------------------------
    // 策略一致性热力图
    // ----------------------------------------------------------------
    (function() {{
      var labels = {heatmap_labels};
      var rawData = {heatmap_data_json};
      var n = {heatmap_n};

      if (n === 0) {{
        document.getElementById('heatmap-chart').innerHTML =
          '<div style="color:#8b949e;padding:40px;text-align:center;">无足够期次数据</div>';
        return;
      }}

      // ECharts heatmap 需要 [col_idx, row_idx, value]
      var data = rawData.map(function(item) {{
        return [item[0], item[1], item[2]];
      }});

      var chart = echarts.init(document.getElementById('heatmap-chart'), 'dark');
      chart.setOption({{
        backgroundColor: 'transparent',
        tooltip: {{
          position: 'top',
          formatter: function(p) {{
            return labels[p.data[0]] + ' × ' + labels[p.data[1]] +
                   '<br/>Jaccard: ' + p.data[2].toFixed(4);
          }}
        }},
        grid: {{ left: '10%', right: '10%', bottom: '15%', top: '5%' }},
        xAxis: {{
          type: 'category',
          data: labels,
          splitArea: {{ show: true }},
          axisLabel: {{ color: '#8b949e', rotate: 30 }}
        }},
        yAxis: {{
          type: 'category',
          data: labels,
          splitArea: {{ show: true }},
          axisLabel: {{ color: '#8b949e' }}
        }},
        visualMap: {{
          min: 0,
          max: 1,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '0%',
          inRange: {{ color: ['#0d1117', '#1f6feb', '#58a6ff'] }},
          textStyle: {{ color: '#8b949e' }}
        }},
        series: [{{
          name: 'Jaccard',
          type: 'heatmap',
          data: data,
          label: {{ show: n <= 8, formatter: function(p) {{ return p.data[2].toFixed(2); }} }},
          emphasis: {{ itemStyle: {{ shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }} }}
        }}]
      }});
      window.addEventListener('resize', function() {{ chart.resize(); }});
    }})();
  </script>
</body>
</html>"""

    return html


# ---------------------------------------------------------------------------
# CLI 入口（便于直接运行）
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='RTA 排除策略批量回测工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python backtester.py --data_dir ./data --ctrl_group_value ctrl
  python backtester.py --data_dir ./data --ctrl_group_value ctrl --pattern "*.csv,*.xlsx"
  python backtester.py --data_dir ./data --ctrl_group_value ctrl --algorithm greedy --output backtest_report.html
        """
    )
    parser.add_argument('--data_dir', type=str, required=True, help='包含多期数据文件的目录')
    parser.add_argument('--ctrl_group_value', type=str, required=True, help='对照组标���值')
    parser.add_argument('--spr_threshold', type=float, default=0.10, help='安全过件率阈值（默认 0.10）')
    parser.add_argument('--max_exclude_ratio', type=float, default=0.20, help='最大排除交易占比（默认 0.20）')
    parser.add_argument('--algorithm', type=str, choices=['greedy', 'ilp'], default='ilp', help='排除算法')
    parser.add_argument('--model_x', type=str, default='V8', help='X 轴模型名称')
    parser.add_argument('--model_y', type=str, default='V9RN', help='Y 轴模型名称')
    parser.add_argument('--pattern', type=str, default='*.csv', help='文件匹配模式（默认 *.csv）')
    parser.add_argument('--output', type=str, default='backtest_report.html', help='输出 HTML 路径')

    args = parser.parse_args()

    backtest_result = run_backtest(
        data_dir=args.data_dir,
        ctrl_group_value=args.ctrl_group_value,
        spr_threshold=args.spr_threshold,
        max_exclude_ratio=args.max_exclude_ratio,
        algorithm=args.algorithm,
        model_x=args.model_x,
        model_y=args.model_y,
        pattern=args.pattern,
    )

    html = generate_backtest_html(backtest_result)
    output_path = args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\nHTML 报告已写入: {output_path}")
