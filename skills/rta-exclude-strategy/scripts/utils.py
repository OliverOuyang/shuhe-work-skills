#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTA Exclude Strategy - Shared Utility Functions

Common functions used across all modules.
"""

import pandas as pd


def convert_old_rule_to_quantile(old_exclude_rule):
    """将老策略规则转换为聚合后的分位格式 (['01q', '02q'] -> ['01Q', '02Q'])"""
    def map_to_quantile(value):
        if isinstance(value, str) and value.endswith('q'):
            try:
                num = int(value[:-1])
                if 1 <= num <= 9:
                    return '01Q'
                elif 10 <= num <= 20:
                    q_num = num - 8
                    return f'{q_num:02d}Q'
            except ValueError:
                return None
        return None

    quantiles = set()
    for rule in old_exclude_rule:
        q = map_to_quantile(rule)
        if q:
            quantiles.add(q)
    return sorted(list(quantiles))


def calc_spr(df):
    if df['t3_ato'].sum() > 0:
        return df['t3_safe_adt'].sum() / df['t3_ato'].sum()
    return 0


def calc_cps(df):
    if df['t3_loan_amt'].sum() > 0:
        return df['cost'].sum() / df['t3_loan_amt'].sum()
    return 0


# ============================================================================
# Vectorized region lookup helpers
# ============================================================================

def make_region_mask(df, region, v8_col='V8_Q', v9_col='V9RN_Q'):
    """
    Vectorized boolean mask for (V8, V9RN) region membership.

    Replaces the slow pattern:
        df.apply(lambda row: (row['V8_Q'], row['V9RN_Q']) in region, axis=1)

    Uses pd.MultiIndex.isin() for O(n) with set lookup instead of O(n*m).

    Args:
        df: DataFrame with V8/V9RN columns
        region: collection of (v8, v9) tuples (list, set, etc.)
        v8_col: V8 column name
        v9_col: V9RN column name

    Returns:
        pd.Series[bool]: boolean mask aligned to df.index
    """
    if not region:
        return pd.Series(False, index=df.index)
    region_set = set(region) if not isinstance(region, set) else region
    idx = pd.MultiIndex.from_arrays([df[v8_col], df[v9_col]])
    return pd.Series(idx.isin(region_set), index=df.index)


def filter_by_region(df, region, v8_col='V8_Q', v9_col='V9RN_Q'):
    """
    Return rows whose (V8, V9RN) pair is in the given region.

    Args:
        df: DataFrame
        region: collection of (v8, v9) tuples

    Returns:
        DataFrame: filtered rows
    """
    return df[make_region_mask(df, region, v8_col, v9_col)]
