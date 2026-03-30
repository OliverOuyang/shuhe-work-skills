"""
RTA排除策略分析主程序
"""

import argparse
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_preprocessing import load_data, preprocess_data, split_control_group, validate_data
from place_in_out_algorithm import run_place_in_out_algorithm
from report_generator import generate_report


def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        description='RTA排除策略分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py --data_path data.csv --ctrl_group_value ctrl
  python main.py --data_path data.xlsx --ctrl_group_value control --old_exclude_rule 01q,02q,03q
  python main.py --data_path data.csv --ctrl_group_value ctrl --spr_threshold 0.08 --max_exclude_ratio 0.15
        """
    )

    # 必需参数
    parser.add_argument(
        '--data_path',
        type=str,
        required=True,
        help='数据文件路径（支持CSV或Excel格式）'
    )

    parser.add_argument(
        '--ctrl_group_value',
        type=str,
        required=True,
        help='对照组标识值（如ctrl、control等）'
    )

    # 可选参数
    parser.add_argument(
        '--old_exclude_rule',
        type=str,
        default='01q,02q,03q,04q,05q,06q,07q,08q,09q,10q',
        help='老策略排除规则，逗号分隔（默认：01q-10q）'
    )

    parser.add_argument(
        '--spr_threshold',
        type=float,
        default=0.10,
        help='安全过件率阈值（默认：0.10）'
    )

    parser.add_argument(
        '--max_exclude_ratio',
        type=float,
        default=0.20,
        help='最大排除交易占比（默认：0.20）'
    )

    parser.add_argument(
        '--output_path',
        type=str,
        default='.',
        help='输出文件路径（默认：当前目录）'
    )

    return parser.parse_args()


def main():
    """
    主函数
    """
    print("="*100)
    print("RTA排除策略分析工具")
    print("="*100)

    # 解析参数
    args = parse_arguments()

    # 转换老策略规则
    old_exclude_rule = [x.strip() for x in args.old_exclude_rule.split(',')]

    print(f"\n配置参数:")
    print(f"  数据文件: {args.data_path}")
    print(f"  对照组标识: {args.ctrl_group_value}")
    print(f"  老策略排除规则: {old_exclude_rule}")
    print(f"  安全过件率阈值: {args.spr_threshold*100:.0f}%")
    print(f"  最大排除交易占比: {args.max_exclude_ratio*100:.0f}%")
    print(f"  输出路径: {args.output_path}")

    try:
        # 步骤1：加载数据
        print("\n" + "="*100)
        print("步骤1：加载数据")
        print("="*100)
        df = load_data(args.data_path)

        # 步骤2：数据预处理
        df = preprocess_data(df)

        # 步骤3：验证数据
        validate_data(df)

        # 步骤4：分离对照组
        df_combined, df_ctrl = split_control_group(df, args.ctrl_group_value)

        # 步骤5：执行置入置出算法
        result = run_place_in_out_algorithm(
            df_combined,
            df_ctrl,
            spr_threshold=args.spr_threshold,
            max_exclude_ratio=args.max_exclude_ratio
        )

        # 步骤6：生成报告
        report_path = generate_report(
            result,
            old_exclude_rule,
            output_path=args.output_path
        )

        print("\n" + "="*100)
        print("分析完成！")
        print("="*100)
        print(f"\n报告已生成: {report_path}")
        print(f"\n关键结果:")
        print(f"  初始圈选: {len(result['initial_region'])} 个格子")
        print(f"  置入区域: {len(result['place_in_region'])} 个格子")
        print(f"  置出区域: {len(result['place_out_region'])} 个格子")
        print(f"  最终排除: {len(result['exclude_region'])} 个格子")

        return 0

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
