"""
Mock数据生成器 - 生成RTA排除策略分析用模拟数据
支持多模型列(V8, V9RN, V10等)
"""

import argparse
import os
import numpy as np
import pandas as pd


# 模型名到原始列名的映射
MODEL_COLUMN_NAMES = {
    'V8': 'v8_ato_safe_bin_req',
    'V9RN': 'merge_ato_safe_v9_rn_bin_req',
    'V10': 'v10_model_bin_req',
}


def get_column_name(model_name):
    """获取模型对应的原始列名"""
    if model_name in MODEL_COLUMN_NAMES:
        return MODEL_COLUMN_NAMES[model_name]
    return f'{model_name.lower()}_bin_req'


def get_safe_rate_range(quantile_num):
    """根据分位数返回安全过件率范围 (low, high)"""
    if quantile_num is None:  # UNK
        return (0.05, 0.10)
    elif 1 <= quantile_num <= 5:
        return (0.03, 0.08)
    elif 6 <= quantile_num <= 9:
        return (0.08, 0.12)
    elif 10 <= quantile_num <= 14:
        return (0.12, 0.18)
    elif 15 <= quantile_num <= 20:
        return (0.18, 0.30)
    return (0.05, 0.10)


def parse_quantile(label):
    """从分位标签提取数字, UNK返回None"""
    if label == 'UNK':
        return None
    return int(label.replace('q', ''))


def generate_mock_data(n_rows=5000, models=None, groups=None, seed=42):
    """
    生成模拟数据

    Args:
        n_rows: 总行数
        models: 模型列名列表, 如 ['V8', 'V9RN']
        groups: 实验分组列表, 如 ['ctrl', 'test']
        seed: 随机种子

    Returns:
        DataFrame: 生成的模拟数据
    """
    if models is None:
        models = ['V8', 'V9RN']
    if groups is None:
        groups = ['ctrl', 'test']

    rng = np.random.default_rng(seed)

    # 分位标签
    quantile_labels = [f'{i:02d}q' for i in range(1, 21)] + ['UNK']

    data = {}

    # 为每个模型生成分位列
    for model in models:
        col_name = get_column_name(model)
        data[col_name] = rng.choice(quantile_labels, size=n_rows)

    # 实验分组: 均匀分配
    data['act_type'] = rng.choice(groups, size=n_rows)

    # 数值字段
    data['expo_cnt'] = rng.integers(100, 10001, size=n_rows)
    data['cost'] = data['expo_cnt'] * rng.uniform(0.1, 0.5, size=n_rows)
    data['t3_ato'] = data['expo_cnt'] * rng.uniform(0.05, 0.3, size=n_rows)

    # t3_safe_adt: 由前两个模型的分位共同决定安全过件率
    model_a = models[0]
    model_b = models[1] if len(models) > 1 else models[0]
    col_a = get_column_name(model_a)
    col_b = get_column_name(model_b)

    safe_adt = np.zeros(n_rows)
    for i in range(n_rows):
        q_a = parse_quantile(data[col_a][i])
        q_b = parse_quantile(data[col_b][i])

        range_a = get_safe_rate_range(q_a)
        range_b = get_safe_rate_range(q_b)

        # 取两个模型分位的较低安全率范围(更保守)
        low = min(range_a[0], range_b[0])
        high = min(range_a[1], range_b[1])
        if high <= low:
            high = low + 0.02

        safe_rate = rng.uniform(low, high)
        safe_adt[i] = data['t3_ato'][i] * safe_rate

    data['t3_safe_adt'] = safe_adt
    data['t3_loan_amt'] = data['t3_ato'] * rng.uniform(5000, 50000, size=n_rows)

    # 构建DataFrame
    df = pd.DataFrame(data)

    # 转换数值列为合理类型
    df['expo_cnt'] = df['expo_cnt'].astype(int)
    df['cost'] = df['cost'].round(2)
    df['t3_ato'] = df['t3_ato'].round(0).astype(int)
    df['t3_safe_adt'] = df['t3_safe_adt'].round(0).astype(int)
    df['t3_loan_amt'] = df['t3_loan_amt'].round(2)

    return df


def main():
    parser = argparse.ArgumentParser(
        description='Mock数据生成器 - 生成RTA排除策略分析用模拟数据'
    )
    parser.add_argument(
        '--n_rows', type=int, default=5000,
        help='总行数 (默认: 5000)'
    )
    parser.add_argument(
        '--models', type=str, default='V8,V9RN',
        help='模型列名，逗号分隔 (默认: V8,V9RN)'
    )
    parser.add_argument(
        '--output', type=str, default='mock_data.csv',
        help='输出文件路径 (默认: mock_data.csv)'
    )
    parser.add_argument(
        '--groups', type=str, default='ctrl,test',
        help='实验分组，逗号分隔 (默认: ctrl,test)'
    )
    parser.add_argument(
        '--seed', type=int, default=42,
        help='随机种子 (默认: 42)'
    )

    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(',')]
    groups = [g.strip() for g in args.groups.split(',')]

    print(f"生成参数:")
    print(f"  行数: {args.n_rows}")
    print(f"  模型: {models}")
    print(f"  分组: {groups}")
    print(f"  输出: {args.output}")

    df = generate_mock_data(
        n_rows=args.n_rows,
        models=models,
        groups=groups,
        seed=args.seed
    )

    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    df.to_csv(args.output, index=False)

    print(f"\n数据生成完成:")
    print(f"  文件: {args.output}")
    print(f"  行数: {len(df)}")
    print(f"  列: {list(df.columns)}")
    print(f"\n前5行预览:")
    print(df.head().to_string(index=False))


if __name__ == '__main__':
    main()
