"""
信息增益自动分箱模块
基于信息增益（Information Gain）自动确定模型分组的最优合并方案

约定：
- "好客户"（good）= 安全授信客户，即 t3_safe_adt
- "坏客户"（bad）= 非安全授信客户，即 t3_ato - t3_safe_adt
- SPR（Safe Pass Rate）= t3_safe_adt / t3_ato
- IV（Information Value）= Σ (good_pct - bad_pct) × ln(good_pct / bad_pct)
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


# 原始分箱顺序（低分→高分，SPR 从低到高）
RAW_BIN_ORDER = [f'{i:02d}q' for i in range(1, 21)]  # ['01q', '02q', ..., '20q']

# 固定映射中 01q-09q 被合并为 01Q，对应原始分组标签
FIXED_FIRST_BIN = [f'{i:02d}q' for i in range(1, 10)]  # 01q~09q


# ---------------------------------------------------------------------------
# 内部辅助函数
# ---------------------------------------------------------------------------

def _safe_log(a, b):
    """安全计算 ln(a/b)，避免除零和 log(0)"""
    if a <= 0 or b <= 0:
        return 0.0
    return float(np.log(a / b))


def _bin_stats_from_counts(good_count, bad_count, total_good, total_bad):
    """
    根据单箱的好/坏客户数计算 IV 贡献

    Returns:
        (good_pct, bad_pct, woe, iv_contrib) - 若总量为零返回全零
    """
    good_pct = good_count / total_good if total_good > 0 else 0.0
    bad_pct = bad_count / total_bad if total_bad > 0 else 0.0
    woe = _safe_log(good_pct, bad_pct)
    iv_contrib = (good_pct - bad_pct) * woe
    return good_pct, bad_pct, woe, iv_contrib


def _aggregate_df_by_bins(df, model_col, bin_edges, target_col, total_col):
    """
    按 bin_edges 聚合 df，返回每箱的 good/bad 计数列表

    Args:
        df: 包含 model_col、target_col、total_col 的 DataFrame
        model_col: 原始分组列（值形如 '01q'~'20q' 或 '01Q'~'12Q'）
        bin_edges: list of list，每个子列表是该箱包含的原始分组标签
        target_col: 安全授信数列
        total_col: ATO 总量列

    Returns:
        list of dict: 每箱 {'labels': [...], 'good': float, 'bad': float, 'total': float}
    """
    result = []
    for labels in bin_edges:
        subset = df[df[model_col].isin(labels)]
        good = subset[target_col].sum()
        total = subset[total_col].sum()
        bad = max(total - good, 0.0)
        result.append({'labels': labels, 'good': good, 'bad': bad, 'total': total})
    return result


def _total_iv(bin_data):
    """
    计算所有箱的总 IV

    Args:
        bin_data: list of dict，含 good/bad

    Returns:
        float: 总 IV
    """
    total_good = sum(b['good'] for b in bin_data)
    total_bad = sum(b['bad'] for b in bin_data)
    iv = 0.0
    for b in bin_data:
        _, _, _, iv_c = _bin_stats_from_counts(b['good'], b['bad'], total_good, total_bad)
        iv += iv_c
    return iv


def _merge_two_bins(bin_data, idx):
    """合并 bin_data[idx] 和 bin_data[idx+1]，返回新的 bin_data 列表"""
    new_data = bin_data[:idx]
    merged = {
        'labels': bin_data[idx]['labels'] + bin_data[idx + 1]['labels'],
        'good': bin_data[idx]['good'] + bin_data[idx + 1]['good'],
        'bad': bin_data[idx]['bad'] + bin_data[idx + 1]['bad'],
        'total': bin_data[idx]['total'] + bin_data[idx + 1]['total'],
    }
    new_data.append(merged)
    new_data.extend(bin_data[idx + 2:])
    return new_data


# ---------------------------------------------------------------------------
# 公共 API
# ---------------------------------------------------------------------------

def calc_entropy(labels):
    """
    计算二分类熵（好/坏客户）

    Args:
        labels: array-like，元素为 0（坏）或 1（好）

    Returns:
        float: Shannon 熵值，范围 [0, 1]
    """
    labels = np.asarray(labels)
    n = len(labels)
    if n == 0:
        return 0.0
    p_good = labels.sum() / n
    p_bad = 1.0 - p_good
    if p_good == 0 or p_bad == 0:
        return 0.0
    return float(-p_good * np.log2(p_good) - p_bad * np.log2(p_bad))


def calc_information_gain(df, split_point, target_col='t3_safe_adt', total_col='t3_ato'):
    """
    计算在某个分割点的信息增益

    将 df 按 split_point 行索引拆分为左右两组，计算相对于未分割时的熵减少量。
    df 应已按某一维度排序（行代表有序分箱），split_point 是分割后左侧的行数。

    Args:
        df: 聚合后的 DataFrame，每行代表一个分箱，含 target_col 和 total_col
        split_point: int，分割点，左侧取 [0, split_point)，右侧取 [split_point, end)
        target_col: 安全授信数列名
        total_col: ATO 总量列名

    Returns:
        float: 信息增益（>0 表示有信息量，越大越好）
    """
    total_good = df[target_col].sum()
    total_total = df[total_col].sum()
    if total_total <= 0:
        return 0.0
    total_bad = max(total_total - total_good, 0.0)

    def _entropy_from_counts(g, b):
        n = g + b
        if n <= 0:
            return 0.0
        pg = g / n
        pb = b / n
        if pg == 0 or pb == 0:
            return 0.0
        return float(-pg * np.log2(pg) - pb * np.log2(pb))

    # 父节点熵
    h_parent = _entropy_from_counts(total_good, total_bad)

    # 左子节点
    left = df.iloc[:split_point]
    left_good = left[target_col].sum()
    left_total = left[total_col].sum()
    left_bad = max(left_total - left_good, 0.0)

    # 右子节点
    right = df.iloc[split_point:]
    right_good = right[target_col].sum()
    right_total = right[total_col].sum()
    right_bad = max(right_total - right_good, 0.0)

    w_left = left_total / total_total
    w_right = right_total / total_total

    h_children = (w_left * _entropy_from_counts(left_good, left_bad) +
                  w_right * _entropy_from_counts(right_good, right_bad))

    return float(h_parent - h_children)


def find_optimal_bins(df, model_col, target_col='t3_safe_adt', total_col='t3_ato',
                      min_bins=4, max_bins=12, min_bin_pct=0.03):
    """
    使用自底向上合并 + 信息增益找到最优分箱

    算法：
    1. 起始：每个原始分组 (01q-20q) 为一个箱（UNK 始终独立，不参与合并）
    2. 计算相邻箱合并后的信息增益损失（IV 减少量）
    3. 合并信息增益损失最小的相邻箱，同时满足 min_bin_pct 约束
    4. 重复直到达到 min_bins 或所有合并的信息增益损失都超过阈值

    Args:
        df: 数据（含原始 01q-20q 分组，或已聚合的 01Q-12Q 分组）
        model_col: 模型列名（如 'V8' 或 'V9RN'，值为原始 01q-20q 格式；
                   也接受 'V8_Q'/'V9RN_Q'，值为 01Q-12Q 格式）
        target_col: 目标列（安全授信数）
        total_col: 总量列（ATO 数）
        min_bins: 最少箱数（不含 UNK 箱）
        max_bins: 最多箱数（不含 UNK 箱）
        min_bin_pct: 每箱最低样本占比（相对于非 UNK 总量）

    Returns:
        dict: {
            'bin_edges': list of list,   # 分箱边界
            'bin_labels': list of str,   # 分箱标签 ['01Q', '02Q', ...]
            'n_bins': int,               # 最终箱数（含 UNK 箱）
            'total_iv': float,           # 总信息价值 (IV)
            'bin_stats': pd.DataFrame,   # 每箱统计
            'merge_history': list        # 合并历史记录
        }
    """
    # ------------------------------------------------------------------
    # 1. 识别列中的原始分组标签并排序
    # ------------------------------------------------------------------
    col_values = df[model_col].dropna().astype(str).unique()

    # 判断是原始格式（01q）还是聚合格式（01Q）
    is_raw = any(v.endswith('q') for v in col_values)

    if is_raw:
        # 原始格式：按数字排序，UNK 分离
        non_unk = sorted(
            [v for v in col_values if v.endswith('q')],
            key=lambda x: int(x[:-1])
        )
    else:
        # 聚合格式：按数字排序
        non_unk = sorted(
            [v for v in col_values if v.endswith('Q') and v != 'UNK'],
            key=lambda x: int(x[:-1])
        )

    has_unk = 'UNK' in col_values

    if len(non_unk) == 0:
        raise ValueError(f"列 {model_col} 中未找到有效分组（01q-20q 或 01Q-12Q）")

    # ------------------------------------------------------------------
    # 2. 初始化每个原始分组为独立箱
    # ------------------------------------------------------------------
    # 先按分组聚合统计
    grp_stats = (
        df[df[model_col].isin(non_unk)]
        .groupby(model_col)[[target_col, total_col]]
        .sum()
        .reindex(non_unk)
        .fillna(0)
    )

    total_non_unk = grp_stats[total_col].sum()
    if total_non_unk <= 0:
        raise ValueError(f"列 {model_col} 非 UNK 分组总量为零，无法分箱")

    # 初始 bin_data：每个原始分组一箱
    bin_data = [
        {
            'labels': [grp],
            'good': float(grp_stats.loc[grp, target_col]),
            'bad': float(max(grp_stats.loc[grp, total_col] - grp_stats.loc[grp, target_col], 0)),
            'total': float(grp_stats.loc[grp, total_col]),
        }
        for grp in non_unk
    ]

    # 最大箱数不超过现有分组数
    effective_max_bins = min(max_bins, len(bin_data))
    effective_min_bins = min(min_bins, effective_max_bins)

    merge_history = []

    # ------------------------------------------------------------------
    # 3. 自底向上合并循环
    # ------------------------------------------------------------------
    while len(bin_data) > effective_min_bins:
        n = len(bin_data)
        best_idx = None
        best_iv_loss = float('inf')
        current_iv = _total_iv(bin_data)

        for i in range(n - 1):
            # 尝试合并 i 和 i+1
            candidate = _merge_two_bins(bin_data, i)

            # 检查 min_bin_pct 约束
            merged_pct = candidate[i]['total'] / total_non_unk
            if merged_pct < min_bin_pct:
                # 如果合并后仍低于阈值且是强制合并情况则不跳过
                # 但如果当前单箱就已经低于阈值，允许合并（修复小箱）
                left_pct = bin_data[i]['total'] / total_non_unk
                right_pct = bin_data[i + 1]['total'] / total_non_unk
                if left_pct >= min_bin_pct and right_pct >= min_bin_pct:
                    # 两箱都达标，合并后反而低于阈值？不可能（合并只会增加），跳过
                    continue

            candidate_iv = _total_iv(candidate)
            iv_loss = current_iv - candidate_iv

            if iv_loss < best_iv_loss:
                best_iv_loss = iv_loss
                best_idx = i

        if best_idx is None:
            # 所有相邻合并都被 min_bin_pct 阻止
            # ���制合并：找样本量最小的箱（不考虑 pct 约束）
            min_total_idx = min(range(len(bin_data) - 1),
                                key=lambda i: bin_data[i]['total'] + bin_data[i + 1]['total'])
            best_idx = min_total_idx
            best_iv_loss = current_iv - _total_iv(_merge_two_bins(bin_data, best_idx))

        # 记录合并历史
        merge_history.append({
            'step': len(merge_history) + 1,
            'merged_bins': bin_data[best_idx]['labels'] + bin_data[best_idx + 1]['labels'],
            'left_labels': bin_data[best_idx]['labels'],
            'right_labels': bin_data[best_idx + 1]['labels'],
            'iv_loss': round(best_iv_loss, 6),
            'bins_after': len(bin_data) - 1,
        })

        bin_data = _merge_two_bins(bin_data, best_idx)

        # 若已达最大箱数限制，继续减少至 effective_min_bins（已由 while 控制）
        if len(bin_data) <= effective_max_bins:
            # 额外检查：是否所有箱都满足 min_bin_pct
            all_ok = all(b['total'] / total_non_unk >= min_bin_pct for b in bin_data)
            if all_ok and len(bin_data) <= effective_max_bins:
                # 如果已在目标箱数范围内且所有箱达标，可以停止
                if len(bin_data) == effective_min_bins:
                    break
                # 否则继续合并至 min_bins
                pass

    # ------------------------------------------------------------------
    # 4. 生成分箱标签（01Q, 02Q, ...）
    # ------------------------------------------------------------------
    n_regular_bins = len(bin_data)
    bin_labels = [f'{i + 1:02d}Q' for i in range(n_regular_bins)]

    # 添加 UNK 箱
    all_bin_edges = [b['labels'] for b in bin_data]
    all_bin_labels = bin_labels[:]
    if has_unk:
        unk_stats = df[df[model_col] == 'UNK']
        unk_good = float(unk_stats[target_col].sum())
        unk_total = float(unk_stats[total_col].sum())
        all_bin_edges.append(['UNK'])
        all_bin_labels.append('UNK')
        bin_data.append({
            'labels': ['UNK'],
            'good': unk_good,
            'bad': max(unk_total - unk_good, 0.0),
            'total': unk_total,
        })

    # ------------------------------------------------------------------
    # 5. 计算 bin_stats DataFrame
    # ------------------------------------------------------------------
    total_good = sum(b['good'] for b in bin_data)
    total_bad = sum(b['bad'] for b in bin_data)
    total_all = sum(b['total'] for b in bin_data)

    rows = []
    for label, b in zip(all_bin_labels, bin_data):
        good_pct, bad_pct, woe, iv_contrib = _bin_stats_from_counts(
            b['good'], b['bad'], total_good, total_bad
        )
        rows.append({
            'bin_label': label,
            'raw_groups': ', '.join(b['labels']),
            'good_count': b['good'],
            'bad_count': b['bad'],
            'total_count': b['total'],
            'bin_pct': b['total'] / total_all if total_all > 0 else 0.0,
            'spr': b['good'] / b['total'] if b['total'] > 0 else 0.0,
            'good_pct': good_pct,
            'bad_pct': bad_pct,
            'woe': woe,
            'iv_contrib': iv_contrib,
        })

    bin_stats = pd.DataFrame(rows)
    total_iv = bin_stats['iv_contrib'].sum()

    return {
        'bin_edges': all_bin_edges,
        'bin_labels': all_bin_labels,
        'n_bins': len(all_bin_labels),
        'total_iv': float(total_iv),
        'bin_stats': bin_stats,
        'merge_history': merge_history,
    }


def apply_custom_bins(df, model_col, bin_edges, bin_labels):
    """
    将自定义分箱方案应用到数据上

    Args:
        df: 原始数据 DataFrame
        model_col: 模型列名（值为原始 01q-20q 或 01Q-12Q 格式，含 UNK）
        bin_edges: find_optimal_bins 返回的 bin_edges（list of list）
        bin_labels: find_optimal_bins 返回的 bin_labels（list of str）

    Returns:
        pd.Series: 与 df 等长的分箱标签列
    """
    if len(bin_edges) != len(bin_labels):
        raise ValueError("bin_edges 和 bin_labels 长度必须相同")

    # 构建原始分组 → 新标签的映射字典
    mapping = {}
    for label, edge_groups in zip(bin_labels, bin_edges):
        for grp in edge_groups:
            mapping[grp] = label

    col = df[model_col].astype(str)
    result = col.map(mapping)

    # 未映射的值（不在 bin_edges 中）标记为 UNK
    unmapped_mask = result.isna() & col.notna()
    if unmapped_mask.any():
        result = result.fillna('UNK')

    return result


def auto_bin_report(df, model_x='V8', model_y='V9RN'):
    """
    对两个模型分别做自动分箱，返回完整报告

    自动检测 df 中的列名格式：
    - 若有 'V8' 列（原始 01q 格式），使用 'V8'
    - 若有 'V8_Q' 列（聚合 01Q 格式），使用 'V8_Q'
    - 对 V9RN 同理

    Args:
        df: 预处理后的 DataFrame
        model_x: X 轴模型名称（默认 'V8'）
        model_y: Y 轴模型名称（默认 'V9RN'）

    Returns:
        dict: {
            'model_x_bins': find_optimal_bins 结果,
            'model_y_bins': find_optimal_bins 结果,
            'comparison': {
                'fixed_bins': 12,
                'auto_x_bins': int,
                'auto_y_bins': int,
                'fixed_iv_x': float,
                'fixed_iv_y': float,
                'auto_iv_x': float,
                'auto_iv_y': float,
                'iv_improvement_x': float,  # IV 提升百分比（相对固定分箱）
                'iv_improvement_y': float,
            }
        }
    """
    def _resolve_col(model_name):
        """在 df 中找到对应的列名"""
        candidates = [model_name, f'{model_name}_Q', model_name.lower(),
                      f'{model_name.lower()}_q']
        for c in candidates:
            if c in df.columns:
                return c
        raise ValueError(f"在 df 中找不到模型 {model_name} 对应的列")

    col_x = _resolve_col(model_x)
    col_y = _resolve_col(model_y)

    # 自动分箱
    bins_x = find_optimal_bins(df, col_x)
    bins_y = find_optimal_bins(df, col_y)

    # 计算固定分箱（12Q）的 IV 作为基准对比
    def _fixed_bin_iv(col):
        """计算固定 12Q 分箱方案下的 IV"""
        col_values = df[col].dropna().astype(str).unique()
        is_raw = any(v.endswith('q') for v in col_values)
        if is_raw:
            # 固定映射：01q-09q→01Q, 10q→02Q, ..., 20q→12Q
            def _fixed_map(v):
                if v.endswith('q'):
                    try:
                        n = int(v[:-1])
                        if 1 <= n <= 9:
                            return '01Q'
                        elif 10 <= n <= 20:
                            return f'{n - 8:02d}Q'
                    except ValueError:
                        pass
                return 'UNK'
            tmp = df[[col, 't3_safe_adt', 't3_ato']].copy()
            tmp['_bin'] = tmp[col].astype(str).apply(_fixed_map)
        else:
            tmp = df[[col, 't3_safe_adt', 't3_ato']].copy()
            tmp['_bin'] = tmp[col].astype(str)

        grp = tmp[tmp['_bin'] != 'UNK'].groupby('_bin')[['t3_safe_adt', 't3_ato']].sum()
        total_good = grp['t3_safe_adt'].sum()
        total_bad = max(grp['t3_ato'].sum() - total_good, 0.0)
        iv = 0.0
        for _, row in grp.iterrows():
            good = row['t3_safe_adt']
            bad = max(row['t3_ato'] - good, 0.0)
            _, _, _, iv_c = _bin_stats_from_counts(good, bad, total_good, total_bad)
            iv += iv_c
        return float(iv)

    try:
        fixed_iv_x = _fixed_bin_iv(col_x)
        fixed_iv_y = _fixed_bin_iv(col_y)
    except Exception:
        fixed_iv_x = 0.0
        fixed_iv_y = 0.0

    def _pct_improvement(auto_iv, fixed_iv):
        if fixed_iv <= 0:
            return 0.0
        return float((auto_iv - fixed_iv) / fixed_iv * 100)

    return {
        'model_x_bins': bins_x,
        'model_y_bins': bins_y,
        'comparison': {
            'fixed_bins': 12,
            'auto_x_bins': bins_x['n_bins'],
            'auto_y_bins': bins_y['n_bins'],
            'fixed_iv_x': round(fixed_iv_x, 6),
            'fixed_iv_y': round(fixed_iv_y, 6),
            'auto_iv_x': round(bins_x['total_iv'], 6),
            'auto_iv_y': round(bins_y['total_iv'], 6),
            'iv_improvement_x': round(_pct_improvement(bins_x['total_iv'], fixed_iv_x), 2),
            'iv_improvement_y': round(_pct_improvement(bins_y['total_iv'], fixed_iv_y), 2),
        },
    }


def generate_binning_html(binning_result):
    """
    生成分箱报告 HTML 片段
    包含：分箱方案对比表、IV 值柱状图（ECharts）、合并历史可视化

    Args:
        binning_result: find_optimal_bins 的返回值，或 auto_bin_report 的返回值

    Returns:
        str: HTML 字符串（可嵌入完整 HTML 页面的 <body> 内）
    """
    # 兼容两种输入格式
    if 'model_x_bins' in binning_result:
        # auto_bin_report 格式
        return _generate_dual_model_html(binning_result)
    else:
        # find_optimal_bins 格式
        return _generate_single_model_html(binning_result, model_name='模型')


def _generate_single_model_html(result, model_name='模型'):
    """生成单模型分箱报告 HTML"""
    bin_stats = result['bin_stats']
    merge_history = result['merge_history']
    total_iv = result['total_iv']
    n_bins = result['n_bins']

    # --- 分箱统计表 ---
    table_rows = ''
    for _, row in bin_stats.iterrows():
        spr_pct = f"{row['spr'] * 100:.2f}%"
        bin_pct = f"{row['bin_pct'] * 100:.2f}%"
        woe_str = f"{row['woe']:.4f}"
        iv_str = f"{row['iv_contrib']:.6f}"
        table_rows += f"""
        <tr>
          <td>{row['bin_label']}</td>
          <td style="font-size:12px;color:#666">{row['raw_groups']}</td>
          <td style="text-align:right">{int(row['total_count'])}</td>
          <td style="text-align:right">{bin_pct}</td>
          <td style="text-align:right">{spr_pct}</td>
          <td style="text-align:right">{woe_str}</td>
          <td style="text-align:right">{iv_str}</td>
        </tr>"""

    # --- 合并历史表 ---
    history_rows = ''
    for h in merge_history:
        left_str = ', '.join(h['left_labels'])
        right_str = ', '.join(h['right_labels'])
        history_rows += f"""
        <tr>
          <td style="text-align:center">{h['step']}</td>
          <td>{left_str}</td>
          <td>{right_str}</td>
          <td style="text-align:right">{h['iv_loss']:.6f}</td>
          <td style="text-align:center">{h['bins_after']}</td>
        </tr>"""

    # --- ECharts 数据 ---
    labels_js = str([row['bin_label'] for _, row in bin_stats.iterrows()])
    spr_js = str([round(row['spr'] * 100, 2) for _, row in bin_stats.iterrows()])
    iv_js = str([round(row['iv_contrib'], 6) for _, row in bin_stats.iterrows()])
    pct_js = str([round(row['bin_pct'] * 100, 2) for _, row in bin_stats.iterrows()])

    chart_id_spr = 'chart_spr_' + model_name.replace(' ', '_')
    chart_id_iv = 'chart_iv_' + model_name.replace(' ', '_')

    html = f"""
<div class="binning-report" style="font-family:Arial,sans-serif;margin:20px 0">
  <h3 style="color:#1a5276;border-bottom:2px solid #2e86c1;padding-bottom:8px">
    {model_name} 自动分箱报告
    <span style="font-size:14px;color:#666;margin-left:12px">
      最终箱数: {n_bins} | 总 IV: {total_iv:.6f}
    </span>
  </h3>

  <!-- 分箱统计表 -->
  <h4 style="color:#2e4057;margin-top:20px">分箱统计</h4>
  <table style="border-collapse:collapse;width:100%;font-size:13px">
    <thead>
      <tr style="background:#2e86c1;color:white">
        <th style="padding:8px 12px;text-align:left">分箱</th>
        <th style="padding:8px 12px;text-align:left">原始分组</th>
        <th style="padding:8px 12px;text-align:right">样本数</th>
        <th style="padding:8px 12px;text-align:right">占比</th>
        <th style="padding:8px 12px;text-align:right">SPR</th>
        <th style="padding:8px 12px;text-align:right">WoE</th>
        <th style="padding:8px 12px;text-align:right">IV 贡献</th>
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
    <tfoot>
      <tr style="background:#f0f0f0;font-weight:bold">
        <td colspan="2" style="padding:8px 12px">合计</td>
        <td style="padding:8px 12px;text-align:right">{int(bin_stats['total_count'].sum())}</td>
        <td style="padding:8px 12px;text-align:right">100.00%</td>
        <td colspan="2"></td>
        <td style="padding:8px 12px;text-align:right">{total_iv:.6f}</td>
      </tr>
    </tfoot>
  </table>

  <!-- SPR 折线图 -->
  <h4 style="color:#2e4057;margin-top:24px">各箱 SPR 趋势</h4>
  <div id="{chart_id_spr}" style="width:100%;height:300px"></div>

  <!-- IV 柱状图 -->
  <h4 style="color:#2e4057;margin-top:24px">各箱 IV 贡献</h4>
  <div id="{chart_id_iv}" style="width:100%;height:260px"></div>

  <!-- 合并历史 -->
  <h4 style="color:#2e4057;margin-top:24px">合并历史（共 {len(merge_history)} 步）</h4>
  <table style="border-collapse:collapse;width:100%;font-size:13px">
    <thead>
      <tr style="background:#5d6d7e;color:white">
        <th style="padding:7px 12px;text-align:center">步骤</th>
        <th style="padding:7px 12px;text-align:left">左侧分组</th>
        <th style="padding:7px 12px;text-align:left">右侧分组</th>
        <th style="padding:7px 12px;text-align:right">IV 损失</th>
        <th style="padding:7px 12px;text-align:center">合并后箱数</th>
      </tr>
    </thead>
    <tbody>
      {history_rows}
    </tbody>
  </table>

  <script>
  (function() {{
    if (typeof echarts === 'undefined') return;

    var labels = {labels_js};
    var sprData = {spr_js};
    var ivData = {iv_js};
    var pctData = {pct_js};

    // SPR 折线图
    var chartSpr = echarts.init(document.getElementById('{chart_id_spr}'));
    chartSpr.setOption({{
      tooltip: {{ trigger: 'axis' }},
      legend: {{ data: ['SPR (%)', '样本占比 (%)'] }},
      xAxis: {{ type: 'category', data: labels }},
      yAxis: [
        {{ type: 'value', name: 'SPR (%)', axisLabel: {{ formatter: '{{value}}%' }} }},
        {{ type: 'value', name: '占比 (%)', axisLabel: {{ formatter: '{{value}}%' }} }}
      ],
      series: [
        {{
          name: 'SPR (%)',
          type: 'line',
          data: sprData,
          smooth: true,
          lineStyle: {{ color: '#2e86c1', width: 2 }},
          itemStyle: {{ color: '#2e86c1' }},
          label: {{ show: true, formatter: '{{c}}%' }}
        }},
        {{
          name: '样本占比 (%)',
          type: 'bar',
          yAxisIndex: 1,
          data: pctData,
          barMaxWidth: 40,
          itemStyle: {{ color: 'rgba(46,134,193,0.25)' }}
        }}
      ]
    }});

    // IV 柱状图
    var chartIv = echarts.init(document.getElementById('{chart_id_iv}'));
    chartIv.setOption({{
      tooltip: {{ trigger: 'axis' }},
      xAxis: {{ type: 'category', data: labels }},
      yAxis: {{ type: 'value', name: 'IV 贡献' }},
      series: [{{
        name: 'IV 贡献',
        type: 'bar',
        data: ivData,
        barMaxWidth: 40,
        itemStyle: {{ color: '#1a8a6e' }},
        label: {{ show: true, position: 'top', formatter: function(p) {{ return p.value.toFixed(4); }} }}
      }}]
    }});
  }})();
  </script>
</div>
"""
    return html


def _generate_dual_model_html(report):
    """生成双模型对比分箱报告 HTML"""
    comparison = report['comparison']

    # 对比摘要卡片
    summary_html = f"""
<div class="binning-summary" style="
  background:linear-gradient(135deg,#1a5276,#2e86c1);
  color:white;border-radius:8px;padding:20px;margin-bottom:24px
">
  <h3 style="margin:0 0 16px;font-size:18px">自动分箱 vs 固定分箱对比</h3>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;text-align:center">
    <div>
      <div style="font-size:28px;font-weight:bold">{comparison['fixed_bins']}</div>
      <div style="font-size:12px;opacity:.8">固定分箱数</div>
    </div>
    <div>
      <div style="font-size:28px;font-weight:bold">{comparison['auto_x_bins']}</div>
      <div style="font-size:12px;opacity:.8">V8 自动分箱数</div>
    </div>
    <div>
      <div style="font-size:28px;font-weight:bold">{comparison['auto_y_bins']}</div>
      <div style="font-size:12px;opacity:.8">V9RN 自动分箱数</div>
    </div>
    <div>
      <div style="font-size:28px;font-weight:bold">
        {comparison['iv_improvement_x']:+.1f}% / {comparison['iv_improvement_y']:+.1f}%
      </div>
      <div style="font-size:12px;opacity:.8">IV 提升 (X / Y)</div>
    </div>
  </div>
  <div style="margin-top:16px;display:grid;grid-template-columns:1fr 1fr;gap:16px;font-size:13px">
    <div>
      V8 固定 IV: {comparison['fixed_iv_x']:.6f} →
      自动 IV: <strong>{comparison['auto_iv_x']:.6f}</strong>
    </div>
    <div>
      V9RN 固定 IV: {comparison['fixed_iv_y']:.6f} →
      自动 IV: <strong>{comparison['auto_iv_y']:.6f}</strong>
    </div>
  </div>
</div>
"""

    html_x = _generate_single_model_html(report['model_x_bins'], model_name='V8')
    html_y = _generate_single_model_html(report['model_y_bins'], model_name='V9RN')

    return summary_html + html_x + html_y
