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
from html_report_generator import generate_html_report

try:
    from ilp_solver import run_ilp_algorithm, run_multi_objective_ilp, check_pulp_available
    ILP_AVAILABLE = check_pulp_available()
except ImportError:
    ILP_AVAILABLE = False

from auto_binning import auto_bin_report, find_optimal_bins, apply_custom_bins
from stability import run_stability_analysis, generate_stability_html
from backtester import run_backtest, generate_backtest_html
from uplift_model import run_uplift_analysis, generate_uplift_html


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

    parser.add_argument(
        '--output_format',
        type=str,
        choices=['excel', 'html', 'both'],
        default='both',
        help='输出报告格式：excel、html或both（默认：both）'
    )

    parser.add_argument(
        '--model_x',
        type=str,
        default='V8',
        help='X轴模型名称（默认：V8）'
    )

    parser.add_argument(
        '--model_y',
        type=str,
        default='V9RN',
        help='Y轴模型名称（默认：V9RN）'
    )

    parser.add_argument(
        '--algorithm',
        type=str,
        choices=['greedy', 'ilp', 'both'],
        default='ilp' if ILP_AVAILABLE else 'greedy',
        help='排除算法选择：greedy（贪心矩形扩充）、ilp（整数线性规划最优解）、both（两者对比）'
    )

    # v2.1 新增参数
    parser.add_argument(
        '--objective',
        type=str,
        choices=['spr_only', 'multi_objective'],
        default='spr_only',
        help='优化目标：spr_only（仅SPR）、multi_objective（SPR+CPS Pareto前沿）'
    )

    parser.add_argument(
        '--auto_bin',
        action='store_true',
        help='启用信息增益自动分箱（替代固定20q→12Q映射）'
    )

    parser.add_argument(
        '--uplift',
        action='store_true',
        help='启用Uplift因果推断分析'
    )

    parser.add_argument(
        '--stability_data',
        type=str,
        default=None,
        help='多期稳定性检验数据路径（逗号分隔多个文件路径）'
    )

    parser.add_argument(
        '--backtest_dir',
        type=str,
        default=None,
        help='批量回测数据目录（启用回测模式）'
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
    print(f"  输出格式: {args.output_format}")
    print(f"  X轴模型: {args.model_x}")
    print(f"  Y轴模型: {args.model_y}")
    print(f"  排除算法: {args.algorithm}")
    if args.objective != 'spr_only':
        print(f"  优化目标: {args.objective}")
    if args.auto_bin:
        print(f"  自动分箱: 启用")
    if args.uplift:
        print(f"  Uplift分析: 启用")
    if args.stability_data:
        print(f"  稳定性数据: {args.stability_data}")
    if args.backtest_dir:
        print(f"  回测目录: {args.backtest_dir}")

    try:
        # 回测模式（独立流程）
        if args.backtest_dir:
            print("\n" + "="*100)
            print("批量回测模式")
            print("="*100)
            backtest_result = run_backtest(
                args.backtest_dir,
                args.ctrl_group_value,
                spr_threshold=args.spr_threshold,
                max_exclude_ratio=args.max_exclude_ratio,
                algorithm=args.algorithm,
                model_x=args.model_x,
                model_y=args.model_y
            )
            backtest_html = generate_backtest_html(backtest_result)
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            out_path = f'{args.output_path}/RTA回测报告_{timestamp}.html'
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(backtest_html)
            print(f"\n回测报告已生成: {out_path}")
            print(f"  回测期数: {backtest_result['summary']['n_periods']}")
            print(f"  平均排除格子: {backtest_result['summary']['avg_exclude_cells']:.1f}")
            print(f"  策略一致性: {backtest_result['summary']['strategy_consistency']:.2%}")
            return 0

        # 步骤1：加载数据
        print("\n" + "="*100)
        print("步骤1：加载数据")
        print("="*100)
        df = load_data(args.data_path, model_x=args.model_x, model_y=args.model_y)

        # 步骤2：数据预处理
        df = preprocess_data(df)

        # 步骤3：验证数据
        validate_data(df)

        # 步骤4：分离对照组
        df_combined, df_ctrl = split_control_group(df, args.ctrl_group_value)

        # 步骤5：执行排除算法
        algorithm = args.algorithm
        if algorithm == 'ilp' and not ILP_AVAILABLE:
            print("\n[WARNING] PuLP未安装，回退到greedy算法")
            algorithm = 'greedy'

        if algorithm == 'greedy':
            result = run_place_in_out_algorithm(
                df_combined,
                df_ctrl,
                spr_threshold=args.spr_threshold,
                max_exclude_ratio=args.max_exclude_ratio
            )
            result['algorithm'] = 'greedy'
        elif algorithm == 'ilp':
            result = run_ilp_algorithm(
                df_combined,
                df_ctrl,
                spr_threshold=args.spr_threshold,
                max_exclude_ratio=args.max_exclude_ratio
            )
        elif algorithm == 'both':
            # 运行两种算法并对比
            print("\n" + "="*100)
            print("运行贪心算法...")
            result_greedy = run_place_in_out_algorithm(
                df_combined,
                df_ctrl,
                spr_threshold=args.spr_threshold,
                max_exclude_ratio=args.max_exclude_ratio
            )
            result_greedy['algorithm'] = 'greedy'

            if ILP_AVAILABLE:
                print("\n" + "="*100)
                print("运行ILP最优算法...")
                result_ilp = run_ilp_algorithm(
                    df_combined,
                    df_ctrl,
                    spr_threshold=args.spr_threshold,
                    max_exclude_ratio=args.max_exclude_ratio
                )

                # 对比两种算法
                print("\n" + "="*100)
                print("算法对比")
                print("="*100)
                print(f"  贪心算法排除格子数: {len(result_greedy['exclude_region'])}")
                print(f"  ILP算法排除格子数: {len(result_ilp['exclude_region'])}")

                greedy_set = set(result_greedy['exclude_region'])
                ilp_set = set(result_ilp['exclude_region'])
                print(f"  重叠格子: {len(greedy_set & ilp_set)}")
                print(f"  仅贪心: {len(greedy_set - ilp_set)}")
                print(f"  仅ILP: {len(ilp_set - greedy_set)}")

                # 使用ILP结果作为最终输出
                result = result_ilp
                result['greedy_result'] = result_greedy
            else:
                print("\n[WARNING] PuLP未安装，仅展示greedy结果")
                result = result_greedy

        # 添加模型名称到结果(供报告显示)
        result['model_x_name'] = args.model_x
        result['model_y_name'] = args.model_y

        # 步骤6：扩展分析（可选）

        # 6a: 自动分箱分析
        if args.auto_bin:
            print("\n" + "="*100)
            print("自动分箱分析")
            print("="*100)
            binning_result = auto_bin_report(df, model_x=args.model_x, model_y=args.model_y)
            result['binning_result'] = binning_result
            print(f"  X轴最优箱数: {binning_result['model_x_bins']['n_bins']}")
            print(f"  Y轴最优箱数: {binning_result['model_y_bins']['n_bins']}")

        # 6b: 多目标优化
        if args.objective == 'multi_objective' and ILP_AVAILABLE:
            print("\n" + "="*100)
            print("多目标优化 (SPR + CPS Pareto前沿)")
            print("="*100)
            pareto_solutions = run_multi_objective_ilp(
                df_combined, df_ctrl,
                spr_threshold=args.spr_threshold,
                max_exclude_ratio=args.max_exclude_ratio
            )
            result['pareto_solutions'] = pareto_solutions
            print(f"  Pareto方案数: {len(pareto_solutions)}")
            for i, sol in enumerate(pareto_solutions):
                print(f"  方案{i+1}: {sol.get('pareto_rank', i+1)} - "
                      f"排除{len(sol['exclude_region'])}格子, "
                      f"CPS={sol.get('objective_cps', 0):.4f}")

        # 6c: Uplift因果分析
        if args.uplift:
            print("\n" + "="*100)
            print("Uplift因果推断分析")
            print("="*100)
            uplift_result = run_uplift_analysis(
                df_combined, df_ctrl,
                exclude_region=result['exclude_region'],
                spr_threshold=args.spr_threshold,
                max_exclude_ratio=args.max_exclude_ratio,
                model_x=args.model_x, model_y=args.model_y
            )
            result['uplift_result'] = uplift_result
            print(f"  分析模式: {uplift_result['mode']}")
            comparison = uplift_result.get('comparison', {})
            if comparison:
                print(f"  Uplift推荐排除: {len(comparison.get('uplift_region', []))} 格子")
                print(f"  与基线重叠: {len(comparison.get('overlap', []))} 格子")
                print(f"  仅Uplift: {len(comparison.get('uplift_only', []))} 格子")

        # 6d: 稳定性检验
        if args.stability_data:
            print("\n" + "="*100)
            print("PSI稳定性检验")
            print("="*100)
            stability_paths = [p.strip() for p in args.stability_data.split(',')]
            stability_result = run_stability_analysis(
                stability_paths,
                args.ctrl_group_value,
                exclude_region=result['exclude_region'],
                model_x=args.model_x, model_y=args.model_y
            )
            result['stability_result'] = stability_result
            print(f"  总体稳定性: {stability_result['overall_stability']}")
            print(f"  趋势: {stability_result['trend']}")

        # 步骤7：生成报告
        report_paths = []

        if args.output_format in ['excel', 'both']:
            excel_report_path = generate_report(
                result,
                old_exclude_rule,
                output_path=args.output_path
            )
            report_paths.append(excel_report_path)

        if args.output_format in ['html', 'both']:
            html_report_path = generate_html_report(
                result,
                old_exclude_rule,
                output_path=args.output_path
            )
            report_paths.append(html_report_path)

        print("\n" + "="*100)
        print("分析完成！")
        print("="*100)
        print(f"\n报告已生成:")
        for path in report_paths:
            print(f"  {path}")
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
