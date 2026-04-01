#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTA Exclude Strategy - Shared Utility Functions

Common functions used across report_generator.py and html_report_generator.py.
"""


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
