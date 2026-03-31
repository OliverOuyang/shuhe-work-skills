"""
测试 HTML 报告生成器
"""

import sys
import os
import pandas as pd
import numpy as np

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from html_report_generator import generate_html_report


def create_test_data():
    """创建测试数据"""
    np.random.seed(42)

    # 创建全量数据 (df_combined)
    v8_list = [f'{i:02d}Q' for i in range(1, 13)]
    v9_list = [f'{i:02d}Q' for i in range(1, 13)]

    data_combined = []
    for v8 in v8_list:
        for v9 in v9_list:
            # 模拟数据：V8和V9越小，安全过件率越低
            v8_num = int(v8[:2])
            v9_num = int(v9[:2])
            base_spr = 0.05 + (v8_num + v9_num) * 0.01

            expo_cnt = np.random.randint(500, 2000)
            t3_ato = int(expo_cnt * np.random.uniform(0.3, 0.6))
            t3_safe_adt = int(t3_ato * base_spr * np.random.uniform(0.9, 1.1))
            t3_loan_amt = t3_ato * np.random.uniform(8000, 15000)
            cost = t3_loan_amt * np.random.uniform(0.002, 0.005)

            data_combined.append({
                'V8_Q': v8,
                'V9RN_Q': v9,
                'expo_cnt': expo_cnt,
                't3_ato': t3_ato,
                't3_safe_adt': t3_safe_adt,
                't3_loan_amt': t3_loan_amt,
                'cost': cost
            })

    df_combined = pd.DataFrame(data_combined)

    # 创建对照组数据 (df_ctrl) - 随机采样50%
    df_ctrl = df_combined.sample(frac=0.5, random_state=42).reset_index(drop=True)

    # 定义排除区域（安全过件率低于10%的区域）
    exclude_region = set()
    for v8 in v8_list[:4]:  # 前4个V8分位
        for v9 in v9_list[:3]:  # 前3个V9分位
            exclude_region.add((v8, v9))

    # 构建结果字典
    result = {
        'df_combined': df_combined,
        'df_ctrl': df_ctrl,
        'exclude_region': exclude_region
    }

    return result


def test_html_report():
    """测试HTML报告生成"""
    print("="*100)
    print("测试HTML报告生成器")
    print("="*100)

    # 创建测试数据
    print("\n1. 创建测试数据...")
    result = create_test_data()
    print(f"   df_combined: {len(result['df_combined'])} 行")
    print(f"   df_ctrl: {len(result['df_ctrl'])} 行")
    print(f"   exclude_region: {len(result['exclude_region'])} 个区域")

    # 定义老策略规则
    old_exclude_rule = ['01q', '02q', '03q', '04q', '05q']
    print(f"\n2. 老策略规则: {old_exclude_rule}")

    # 生成HTML报告
    print("\n3. 生成HTML报告...")
    output_path = os.path.dirname(__file__)
    file_path = generate_html_report(result, old_exclude_rule, output_path)

    print("\n" + "="*100)
    print(f"测试完成！报告已生成: {file_path}")
    print("="*100)

    return file_path


if __name__ == '__main__':
    test_html_report()
