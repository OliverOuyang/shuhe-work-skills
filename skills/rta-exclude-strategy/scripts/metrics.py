"""
RTA Exclude Strategy - Shared Metrics Calculations

Centralizes all indicator computation logic used by both report_generator.py
and html_report_generator.py to avoid duplication.
"""

import pandas as pd
from utils import calc_spr, calc_cps, make_region_mask, filter_by_region


# ============================================================================
# Strategy-level metrics
# ============================================================================

def calc_old_strategy_metrics(df_ctrl, old_exclude_v8):
    """
    Compute all old-strategy indicators on the control group.

    Returns a dict with:
        old_exclude_data_ctrl   - filtered DataFrame (old exclude segment)
        old_remain_data_ctrl    - filtered DataFrame (old remain segment)
        total_ctrl_expo         - total expo_cnt
        total_ctrl_ato          - total t3_ato
        total_ctrl_amt          - total t3_loan_amt
        old_exclude_expo_ratio
        old_exclude_ato_ratio
        old_exclude_amt_ratio
        old_exclude_spr
        old_remain_spr
        old_remain_cps
    """
    old_exclude_data_ctrl = df_ctrl[df_ctrl['V8_Q'].isin(old_exclude_v8)]
    old_remain_data_ctrl = df_ctrl[~df_ctrl['V8_Q'].isin(old_exclude_v8)]

    total_ctrl_expo = df_ctrl['expo_cnt'].sum()
    total_ctrl_ato = df_ctrl['t3_ato'].sum()
    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()

    old_exclude_expo_ratio = old_exclude_data_ctrl['expo_cnt'].sum() / total_ctrl_expo
    old_exclude_ato_ratio = old_exclude_data_ctrl['t3_ato'].sum() / total_ctrl_ato
    old_exclude_amt_ratio = old_exclude_data_ctrl['t3_loan_amt'].sum() / total_ctrl_amt
    old_exclude_spr = calc_spr(old_exclude_data_ctrl)
    old_remain_spr = calc_spr(old_remain_data_ctrl)
    old_remain_cps = calc_cps(old_remain_data_ctrl)

    return {
        'old_exclude_data_ctrl': old_exclude_data_ctrl,
        'old_remain_data_ctrl': old_remain_data_ctrl,
        'total_ctrl_expo': total_ctrl_expo,
        'total_ctrl_ato': total_ctrl_ato,
        'total_ctrl_amt': total_ctrl_amt,
        'old_exclude_expo_ratio': old_exclude_expo_ratio,
        'old_exclude_ato_ratio': old_exclude_ato_ratio,
        'old_exclude_amt_ratio': old_exclude_amt_ratio,
        'old_exclude_spr': old_exclude_spr,
        'old_remain_spr': old_remain_spr,
        'old_remain_cps': old_remain_cps,
    }


def calc_new_strategy_metrics(df_ctrl, exclude_region, total_ctrl_expo, total_ctrl_ato, total_ctrl_amt):
    """
    Compute all new-strategy indicators on the control group.

    Args:
        df_ctrl: control group DataFrame
        exclude_region: set/list of (v8, v9) tuples
        total_ctrl_expo: pre-computed total expo_cnt (from calc_old_strategy_metrics)
        total_ctrl_ato:  pre-computed total t3_ato
        total_ctrl_amt:  pre-computed total t3_loan_amt

    Returns a dict with:
        new_exclude_data_ctrl   - filtered DataFrame (new exclude segment)
        new_remain_data_ctrl    - filtered DataFrame (new remain segment)
        new_exclude_expo_ratio
        new_exclude_ato_ratio
        new_exclude_amt_ratio
        new_exclude_spr
        new_remain_spr
        new_remain_cps
    """
    new_exclude_data_ctrl = filter_by_region(df_ctrl, exclude_region)
    new_remain_data_ctrl = df_ctrl[~make_region_mask(df_ctrl, exclude_region)]

    new_exclude_expo_ratio = new_exclude_data_ctrl['expo_cnt'].sum() / total_ctrl_expo
    new_exclude_ato_ratio = new_exclude_data_ctrl['t3_ato'].sum() / total_ctrl_ato
    new_exclude_amt_ratio = new_exclude_data_ctrl['t3_loan_amt'].sum() / total_ctrl_amt
    new_exclude_spr = calc_spr(new_exclude_data_ctrl)
    new_remain_spr = calc_spr(new_remain_data_ctrl)
    new_remain_cps = calc_cps(new_remain_data_ctrl)

    return {
        'new_exclude_data_ctrl': new_exclude_data_ctrl,
        'new_remain_data_ctrl': new_remain_data_ctrl,
        'new_exclude_expo_ratio': new_exclude_expo_ratio,
        'new_exclude_ato_ratio': new_exclude_ato_ratio,
        'new_exclude_amt_ratio': new_exclude_amt_ratio,
        'new_exclude_spr': new_exclude_spr,
        'new_remain_spr': new_remain_spr,
        'new_remain_cps': new_remain_cps,
    }


def calc_comparison_metrics(df_ctrl, exclude_region, old_exclude_v8):
    """
    Compute both old and new strategy metrics together, plus full totals.

    Convenience wrapper that calls calc_old_strategy_metrics and
    calc_new_strategy_metrics, merging the results into one flat dict.

    Returns a dict containing all keys from both sub-functions plus
    'total_ctrl_amt', 'total_ctrl_ato', 'total_ctrl_expo'.
    """
    old = calc_old_strategy_metrics(df_ctrl, old_exclude_v8)
    new = calc_new_strategy_metrics(
        df_ctrl, exclude_region,
        old['total_ctrl_expo'],
        old['total_ctrl_ato'],
        old['total_ctrl_amt'],
    )
    return {**old, **new}


# ============================================================================
# Four-quadrant segmentation (置入置出)
# ============================================================================

def calc_four_segments(df_ctrl, exclude_region, old_exclude_v8):
    """
    Split the control group into four mutually exclusive segments based on
    old vs new strategy exclusion.

    Adds two boolean columns to df_ctrl in-place:
        'old_exclude' - True if the row falls in the old exclude region
        'new_exclude' - True if the row falls in the new exclude region

    Returns a dict with:
        both_exclude  - old excluded AND new excluded
        only_old      - old excluded but new keeps  (置入 segment)
        only_new      - new excluded but old keeps  (置出 segment)
        both_keep     - both strategies keep
    """
    df_ctrl['old_exclude'] = df_ctrl['V8_Q'].isin(old_exclude_v8)
    df_ctrl['new_exclude'] = make_region_mask(df_ctrl, exclude_region)

    both_exclude = df_ctrl[(df_ctrl['old_exclude']) & (df_ctrl['new_exclude'])]
    only_old = df_ctrl[(df_ctrl['old_exclude']) & (~df_ctrl['new_exclude'])]
    only_new = df_ctrl[(~df_ctrl['old_exclude']) & (df_ctrl['new_exclude'])]
    both_keep = df_ctrl[(~df_ctrl['old_exclude']) & (~df_ctrl['new_exclude'])]

    return {
        'both_exclude': both_exclude,
        'only_old': only_old,
        'only_new': only_new,
        'both_keep': both_keep,
    }


def calc_segment_amt_ratios(both_exclude, only_old, only_new, total_ctrl_amt):
    """
    Compute new/old strategy exclude-amount ratios from the four segments.

    Returns:
        new_exclude_amt_ratio, old_exclude_amt_ratio
    """
    new_exclude_amt_ratio = (
        both_exclude['t3_loan_amt'].sum() + only_new['t3_loan_amt'].sum()
    ) / total_ctrl_amt
    old_exclude_amt_ratio = (
        both_exclude['t3_loan_amt'].sum() + only_old['t3_loan_amt'].sum()
    ) / total_ctrl_amt
    return new_exclude_amt_ratio, old_exclude_amt_ratio


# ============================================================================
# V8 marginal SPR table (used in section 2.1)
# ============================================================================

def calc_v8_spr_table(df_combined):
    """
    Compute per-V8-quantile SPR on the full (combined) dataset.

    Returns:
        v8_stats_all: DataFrame with columns ['V8_Q', 't3_ato', 't3_safe_adt', '安全过件率']
        v8_list:      list of V8 quantile labels ['01Q', ..., '12Q']
    """
    v8_list = [f'{i:02d}Q' for i in range(1, 13)]
    v8_stats_all = df_combined.groupby('V8_Q').agg({
        't3_ato': 'sum',
        't3_safe_adt': 'sum'
    }).reset_index()
    v8_stats_all['安全过件率'] = v8_stats_all['t3_safe_adt'] / v8_stats_all['t3_ato']
    return v8_stats_all, v8_list
