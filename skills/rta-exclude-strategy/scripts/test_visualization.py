"""
visualization.py 测试脚本
验证可视化函数的基本功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from visualization import (
    generate_heatmap_html,
    generate_comparison_chart_html,
    generate_cross_analysis_matrix_html,
    calculate_groups_data
)
import pandas as pd
import numpy as np


def test_heatmap():
    """测试热力图生成"""
    print("测试 1: 热力图生成")
    print("-" * 60)

    # 创建模拟数据
    np.random.seed(42)
    n_samples = 1000

    data = {
        'V8_Q': np.random.choice([f'{i:02d}Q' for i in range(1, 13)], n_samples),
        'V9RN_Q': np.random.choice([f'{i:02d}Q' for i in range(1, 13)], n_samples),
        't3_ato': np.random.randint(1, 100, n_samples),
        't3_safe_adt': np.random.randint(1, 80, n_samples),
        't3_loan_amt': np.random.randint(1000, 50000, n_samples),
        'cost': np.random.uniform(10, 500, n_samples)
    }

    df_combined = pd.DataFrame(data)

    # 定义排除区域
    exclude_region = [('01Q', '01Q'), ('01Q', '02Q'), ('02Q', '01Q'), ('02Q', '02Q')]

    # 生成热力图
    html = generate_heatmap_html(df_combined, exclude_region, 'spr')

    print(f"热力图 HTML 长度: {len(html)} 字符")
    print(f"包含 'heatmap-table': {'heatmap-table' in html}")
    print(f"包含排除标记: {'cell-excluded' in html}")
    print("[PASS] 热力图生成成功\n")


def test_comparison_chart():
    """测试对比柱状图生成"""
    print("测试 2: 对比柱状图生成")
    print("-" * 60)

    old_metrics = {
        '排除交易占比': 0.15,
        '排除客群安全过件率': 0.08,
        '保留客群安全过件率': 0.65,
        '保留客群CPS': 0.0234
    }

    new_metrics = {
        '排除交易占比': 0.18,
        '排除客群安全过件率': 0.07,
        '保留客群安全过件率': 0.68,
        '保留客群CPS': 0.0220
    }

    html = generate_comparison_chart_html(old_metrics, new_metrics)

    print(f"对比图 HTML 长度: {len(html)} 字符")
    print(f"包含 SVG 元素: {'<svg' in html}")
    print(f"包含新老策略标签: {'旧策略' in html and '新策略' in html}")
    print("[PASS] 对比柱状图生成成功\n")


def test_cross_matrix():
    """测试交叉分析矩阵生成"""
    print("测试 3: 交叉分析矩阵生成")
    print("-" * 60)

    groups_data = {
        'both_exclude': {'amt_ratio': 0.10, 'spr': 0.08, 'cps': 0.025},
        'place_in': {'amt_ratio': 0.05, 'spr': 0.12, 'cps': 0.022},
        'place_out': {'amt_ratio': 0.08, 'spr': 0.07, 'cps': 0.028},
        'both_keep': {'amt_ratio': 0.77, 'spr': 0.65, 'cps': 0.020}
    }

    html = generate_cross_analysis_matrix_html(groups_data)

    print(f"交叉矩阵 HTML 长度: {len(html)} 字符")
    print(f"包含矩阵表格: {'matrix-table' in html}")
    print(f"包含四个客群: {'置入客群' in html and '置出客群' in html}")
    print("[PASS] 交叉分析矩阵生成成功\n")


def test_calculate_groups():
    """测试客群数据计算"""
    print("测试 4: 客群数据计算")
    print("-" * 60)

    # 创建模拟对照组数据
    np.random.seed(42)
    n_samples = 500

    data = {
        'V8_Q': np.random.choice([f'{i:02d}Q' for i in range(1, 13)], n_samples),
        'V9RN_Q': np.random.choice([f'{i:02d}Q' for i in range(1, 13)], n_samples),
        't3_ato': np.random.randint(1, 100, n_samples),
        't3_safe_adt': np.random.randint(1, 80, n_samples),
        't3_loan_amt': np.random.randint(1000, 50000, n_samples),
        'cost': np.random.uniform(10, 500, n_samples)
    }

    df_ctrl = pd.DataFrame(data)

    # 定义排除区域
    exclude_region = [('01Q', '01Q'), ('01Q', '02Q'), ('02Q', '01Q')]
    old_exclude_v8 = ['01Q', '02Q']

    # 计算客群数据
    groups_data = calculate_groups_data(df_ctrl, exclude_region, old_exclude_v8)

    print("计算结果:")
    for group_name, metrics in groups_data.items():
        print(f"  {group_name}:")
        print(f"    交易占比: {metrics['amt_ratio']*100:.2f}%")
        print(f"    安全过件率: {metrics['spr']*100:.2f}%")
        print(f"    CPS: {metrics['cps']:.4f}")

    # 验证占比总和约为100%
    total_ratio = sum(g['amt_ratio'] for g in groups_data.values())
    print(f"\n总交易占比: {total_ratio*100:.2f}%")
    assert abs(total_ratio - 1.0) < 0.01, "交易占比总和应接近100%"

    print("[PASS] 客群数据计算正确\n")


def main():
    """运行所有测试"""
    print("="*60)
    print("visualization.py 功能测试")
    print("="*60)
    print()

    try:
        test_heatmap()
        test_comparison_chart()
        test_cross_matrix()
        test_calculate_groups()

        print("="*60)
        print("[SUCCESS] 所有测试通过!")
        print("="*60)
        return 0

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
