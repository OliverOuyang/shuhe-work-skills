"""
ILP最优排除区域求解器
基于0-1整数线性规划，在12x12网格中找到全局最优排除区域

相比贪心矩形扩充算法的优势：
- 全局最优（非局部贪心）
- 不受矩形约束（可选择任意形状区域）
- 自然处理多约束（SPR + 交易量）
- 144个二元变量，毫秒级求解
"""

import pandas as pd
import numpy as np

try:
    import pulp
    HAS_PULP = True
except ImportError:
    HAS_PULP = False

from utils import filter_by_region


def check_pulp_available():
    """检查PuLP是否可用"""
    return HAS_PULP


def run_ilp_algorithm(df_combined, df_ctrl, spr_threshold=0.10, max_exclude_ratio=0.20):
    """
    使用0-1整数线性规划求解最优排除区域

    Args:
        df_combined: 全量数据（实验组+对照组）
        df_ctrl: 对照组数据
        spr_threshold: 安全过件率阈值（默认0.10）
        max_exclude_ratio: 最大排除交易占比（默认0.20）

    Returns:
        dict: 包含算法结果的字典，与place_in_out_algorithm兼容
    """
    if not HAS_PULP:
        raise ImportError("PuLP未安装，请运行: pip install pulp")

    print("\n" + "="*100)
    print("ILP最优排除区域求解器")
    print("="*100)

    # 步骤1：预计算每个格子的指标
    print("\n步骤1：预计算网格指标")
    cell_stats = _precompute_cell_stats(df_combined, df_ctrl)

    # 步骤2：构建并求解ILP模型
    print("\n步骤2：构建ILP模型")
    exclude_cells = _solve_ilp(cell_stats, spr_threshold, max_exclude_ratio)

    # 步骤3：分析结果（与贪心算法对比用）
    print("\n步骤3：分析求解结果")
    result = _analyze_result(df_combined, df_ctrl, exclude_cells, cell_stats, spr_threshold)

    return result


def _precompute_cell_stats(df_combined, df_ctrl):
    """
    预计算每个(V8_Q, V9RN_Q)格子的聚合指标

    Returns:
        dict: {(v8, v9): {ato, safe_adt, loan_amt, cost, ctrl_ato, ctrl_safe_adt, ctrl_amt, ...}}
    """
    v8_list = [f'{i:02d}Q' for i in range(1, 13)]
    v9_list = [f'{i:02d}Q' for i in range(1, 13)]

    # 全量数据聚合
    combined_agg = df_combined.groupby(['V8_Q', 'V9RN_Q']).agg({
        't3_ato': 'sum',
        't3_safe_adt': 'sum',
        't3_loan_amt': 'sum',
        'cost': 'sum',
        'expo_cnt': 'sum'
    }).to_dict('index')

    # 对照组数据聚合
    ctrl_agg = df_ctrl.groupby(['V8_Q', 'V9RN_Q']).agg({
        't3_ato': 'sum',
        't3_safe_adt': 'sum',
        't3_loan_amt': 'sum',
        'cost': 'sum',
        'expo_cnt': 'sum'
    }).to_dict('index')

    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()

    cell_stats = {}
    for v8 in v8_list:
        for v9 in v9_list:
            key = (v8, v9)
            combined = combined_agg.get(key, {})
            ctrl = ctrl_agg.get(key, {})

            ato = combined.get('t3_ato', 0)
            safe_adt = combined.get('t3_safe_adt', 0)
            spr = safe_adt / ato if ato > 0 else 0

            ctrl_amt = ctrl.get('t3_loan_amt', 0)
            ctrl_ato = ctrl.get('t3_ato', 0)
            ctrl_safe_adt = ctrl.get('t3_safe_adt', 0)

            cell_stats[key] = {
                'ato': ato,
                'safe_adt': safe_adt,
                'spr': spr,
                'loan_amt': combined.get('t3_loan_amt', 0),
                'cost': combined.get('cost', 0),
                'expo_cnt': combined.get('expo_cnt', 0),
                'ctrl_ato': ctrl_ato,
                'ctrl_safe_adt': ctrl_safe_adt,
                'ctrl_amt': ctrl_amt,
                'ctrl_amt_ratio': ctrl_amt / total_ctrl_amt if total_ctrl_amt > 0 else 0,
            }

    # 打印网格概览
    non_empty = sum(1 for s in cell_stats.values() if s['ato'] > 0)
    print(f"  网格规模: 12x12 = 144 格子")
    print(f"  非空格子: {non_empty}")
    print(f"  对照组总交易额: {total_ctrl_amt:,.0f}")

    return cell_stats


def _solve_ilp(cell_stats, spr_threshold, max_exclude_ratio):
    """
    构建并求解0-1 ILP模型

    目标函数: 最大化排除区域中低于阈值的SPR"收益"
      max Σ x[i,j] * (spr_threshold - spr[i,j]) * ato[i,j]
      即：优先排除SPR低且申完量大的格子

    约束条件:
      1. 排除区域整体SPR <= spr_threshold（线性化）
      2. 对照组排除交易占比 <= max_exclude_ratio
      3. 只排除SPR <= spr_threshold的格子（合理性约束）

    Returns:
        list: 被选中排除的格子列表 [(v8, v9), ...]
    """
    cells = list(cell_stats.keys())

    # 创建问题
    prob = pulp.LpProblem("RTA_Exclude_Optimal", pulp.LpMaximize)

    # 决策变量: x[cell] ∈ {0, 1}
    x = pulp.LpVariable.dicts("cell", cells, cat='Binary')

    # 目标函数: 最大化排除效果
    # 对每个格子，排除收益 = (阈值 - 该格子SPR) * 申完量
    # 正值 = SPR低于阈值的格子（应该排除），负值 = SPR高于阈值的格子（不应排除）
    prob += pulp.lpSum(
        x[cell] * (spr_threshold - cell_stats[cell]['spr']) * cell_stats[cell]['ato']
        for cell in cells
        if cell_stats[cell]['ato'] > 0
    ), "Maximize_Exclude_Benefit"

    # 约束1: 排除区域整体SPR <= spr_threshold（线性化形式）
    # Σ safe_adt * x <= spr_threshold * Σ ato * x
    # 即: Σ (safe_adt - spr_threshold * ato) * x <= 0
    prob += (
        pulp.lpSum(
            x[cell] * (cell_stats[cell]['safe_adt'] - spr_threshold * cell_stats[cell]['ato'])
            for cell in cells
            if cell_stats[cell]['ato'] > 0
        ) <= 0,
        "SPR_Constraint"
    )

    # 约束2: 对照组排除交易占比 <= max_exclude_ratio
    prob += (
        pulp.lpSum(
            x[cell] * cell_stats[cell]['ctrl_amt_ratio']
            for cell in cells
        ) <= max_exclude_ratio,
        "Volume_Constraint"
    )

    # 约束3: 只允许排除SPR <= 2*阈值的格子（避免排除明显高质量格子）
    # 这是一个合理性约束，防止数学上的退化解
    for cell in cells:
        if cell_stats[cell]['ato'] > 0 and cell_stats[cell]['spr'] > 2 * spr_threshold:
            prob += x[cell] == 0, f"Quality_Guard_{cell[0]}_{cell[1]}"

    # 约束4: 必须排除至少1个格子（避免空解）
    prob += (
        pulp.lpSum(x[cell] for cell in cells if cell_stats[cell]['ato'] > 0) >= 1,
        "Non_Empty"
    )

    # 求解
    print(f"  变量数: {len(cells)}")
    print(f"  约束数: {len(prob.constraints)}")

    # 使用CBC求解器，抑制输出
    solver = pulp.PULP_CBC_CMD(msg=0)
    status = prob.solve(solver)

    print(f"  求解状态: {pulp.LpStatus[status]}")
    print(f"  目标函数值: {pulp.value(prob.objective):.4f}")

    if status != pulp.constants.LpStatusOptimal:
        print("  [WARNING] 未找到最优解，返回空排除区域")
        return []

    # 提取被选中的格子
    exclude_cells = [cell for cell in cells if pulp.value(x[cell]) > 0.5]

    print(f"  最优排除格子数: {len(exclude_cells)}")

    return exclude_cells


def _analyze_result(df_combined, df_ctrl, exclude_cells, cell_stats, spr_threshold):
    """
    分析ILP求解结果，生成与贪心算法兼容的输出格式

    Returns:
        dict: 与run_place_in_out_algorithm输出格式兼容
    """
    exclude_region = exclude_cells
    exclude_set = set(exclude_cells)

    # 计算排除区域统计
    if exclude_cells:
        exclude_data = filter_by_region(df_combined, exclude_cells)
        exclude_ctrl = filter_by_region(df_ctrl, exclude_cells)

        total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()
        exclude_spr = exclude_data['t3_safe_adt'].sum() / exclude_data['t3_ato'].sum() if exclude_data['t3_ato'].sum() > 0 else 0
        exclude_ctrl_ratio = exclude_ctrl['t3_loan_amt'].sum() / total_ctrl_amt if total_ctrl_amt > 0 else 0

        print(f"\n排除区域统计:")
        print(f"  排除格子数: {len(exclude_cells)}")
        print(f"  排除区域SPR: {exclude_spr*100:.2f}%")
        print(f"  对照组排除交易占比: {exclude_ctrl_ratio*100:.2f}%")
    else:
        print("\n[WARNING] 排除区域为空")

    # 推断initial_region, place_in_region, place_out_region用于报告兼容
    # ILP不区分这三步，但为了兼容报告格式，做近似映射
    initial_region, place_in_region, place_out_region, j = _infer_place_in_out_regions(
        exclude_set, cell_stats, spr_threshold
    )

    print(f"\n区域映射（报告兼容）:")
    print(f"  推断初始j: {j}")
    print(f"  初始区域: {len(initial_region)} 格子")
    print(f"  置入区域: {len(place_in_region)} 格子")
    print(f"  置出区域: {len(place_out_region)} 格子")
    print(f"  最终排除: {len(exclude_region)} 格子")

    return {
        'j': j,
        'initial_region': initial_region,
        'place_in_region': place_in_region,
        'place_out_region': place_out_region,
        'exclude_region': exclude_region,
        'df_combined': df_combined,
        'df_ctrl': df_ctrl,
        'algorithm': 'ilp',
        'cell_stats': cell_stats,
    }


def run_multi_objective_ilp(df_combined, df_ctrl, spr_threshold=0.10, max_exclude_ratio=0.20, n_solutions=5):
    """
    多目标ILP优化：SPR + CPS

    通过 epsilon-constraint 方法生成 Pareto 前沿：
    - 主目标：最大化排除区域的风险收益（同单目标）
    - 副目标：最小化排除区域的 CPS（cost/t3_loan_amt）
    - 通过逐步收紧 CPS 上界生成多个 Pareto 最优解

    Returns:
        list[dict]: 每个 dict 包含一个 Pareto 方案，格式同 run_ilp_algorithm 的返回值，
                    额外包含 'pareto_rank', 'objective_spr_score', 'objective_cps'
    """
    if not HAS_PULP:
        raise ImportError("PuLP未安装，请运行: pip install pulp")

    print("\n" + "="*100)
    print("多目标ILP求解器 (SPR + CPS Pareto前沿)")
    print("="*100)

    # 步骤1：预计算网格指标（复用现有函数）
    print("\n步骤1：预计算网格指标")
    cell_stats = _precompute_cell_stats(df_combined, df_ctrl)

    # 步骤2：求解纯SPR最优（获得该解下的CPS上界）
    print("\n步骤2：求解纯SPR最优（获取CPS上界）")
    exclude_spr_optimal = _solve_ilp(cell_stats, spr_threshold, max_exclude_ratio)
    cps_upper = _calc_cells_cps(exclude_spr_optimal, cell_stats)
    spr_score_upper = _calc_cells_spr_score(exclude_spr_optimal, cell_stats, spr_threshold)
    print(f"  纯SPR最优解 CPS: {cps_upper:.6f}")

    # 步骤3：求解纯CPS最优（获得CPS下界）
    print("\n步骤3：求解纯CPS最优（获取CPS下界）")
    exclude_cps_optimal = _solve_ilp_min_cps(cell_stats, spr_threshold, max_exclude_ratio)
    cps_lower = _calc_cells_cps(exclude_cps_optimal, cell_stats)
    print(f"  纯CPS最优解 CPS: {cps_lower:.6f}")

    # 如果上下界相同或下界高于上界，直接返回单个解
    if cps_upper <= cps_lower or abs(cps_upper - cps_lower) < 1e-10:
        print("\n  CPS上下界相同，返回单个Pareto解")
        result = _analyze_result(df_combined, df_ctrl, exclude_spr_optimal, cell_stats, spr_threshold)
        result['pareto_rank'] = 1
        result['objective_spr_score'] = spr_score_upper
        result['objective_cps'] = cps_upper
        return [result]

    # 步骤4：在 [CPS下界, CPS上界] 之间等距取 n_solutions 个 epsilon 并求解
    print(f"\n步骤4：epsilon-constraint 扫描 ({n_solutions} 个方案)")
    print(f"  CPS范围: [{cps_lower:.6f}, {cps_upper:.6f}]")

    epsilons = [cps_lower + (cps_upper - cps_lower) * i / (n_solutions - 1)
                for i in range(n_solutions)] if n_solutions > 1 else [cps_upper]

    pareto_solutions = []
    seen_signatures = set()

    for i, epsilon in enumerate(epsilons):
        print(f"\n  方案 {i+1}/{n_solutions}: CPS上界 = {epsilon:.6f}")
        exclude_cells = _solve_ilp_with_cps_constraint(
            cell_stats, spr_threshold, max_exclude_ratio, cps_epsilon=epsilon
        )
        if not exclude_cells:
            print(f"  [SKIP] 未找到可行解")
            continue

        # 去重：用排除格子集合作为签名
        sig = frozenset(exclude_cells)
        if sig in seen_signatures:
            print(f"  [SKIP] 与已有方案重复")
            continue
        seen_signatures.add(sig)

        spr_score = _calc_cells_spr_score(exclude_cells, cell_stats, spr_threshold)
        cps_val = _calc_cells_cps(exclude_cells, cell_stats)
        print(f"  SPR得分: {spr_score:.4f}, CPS: {cps_val:.6f}, 格子数: {len(exclude_cells)}")

        result = _analyze_result(df_combined, df_ctrl, exclude_cells, cell_stats, spr_threshold)
        result['objective_spr_score'] = spr_score
        result['objective_cps'] = cps_val
        pareto_solutions.append(result)

    # 步骤5：按SPR得分降序排列并分配pareto_rank
    pareto_solutions.sort(key=lambda r: r['objective_spr_score'], reverse=True)
    for rank, sol in enumerate(pareto_solutions, start=1):
        sol['pareto_rank'] = rank

    print(f"\n生成Pareto前沿方案数: {len(pareto_solutions)}")
    return pareto_solutions


def _calc_cells_cps(exclude_cells, cell_stats):
    """计算指定格子集合的整体CPS (cost / t3_loan_amt)"""
    if not exclude_cells:
        return float('inf')
    total_cost = sum(cell_stats[c]['cost'] for c in exclude_cells)
    total_loan_amt = sum(cell_stats[c]['loan_amt'] for c in exclude_cells)
    if total_loan_amt <= 0:
        return float('inf')
    return total_cost / total_loan_amt


def _calc_cells_spr_score(exclude_cells, cell_stats, spr_threshold):
    """计算指定格子集合的SPR排除得分（目标函数值）"""
    if not exclude_cells:
        return 0.0
    return sum(
        (spr_threshold - cell_stats[c]['spr']) * cell_stats[c]['ato']
        for c in exclude_cells
        if cell_stats[c]['ato'] > 0
    )


def _solve_ilp_min_cps(cell_stats, spr_threshold, max_exclude_ratio):
    """
    以最小化CPS为目标求解ILP（同时满足SPR约束和交易量约束）

    CPS = cost / loan_amt，非线性，通过线性化处理：
    对固定的 loan_amt 分母，最小化 cost/loan_amt 等价于最小化 Σ cost*x / Σ loan_amt*x。
    此处采用近似：最小化加权cost（权重为1/loan_amt归一化），实际上等价于
    最小化每单位放款额的成本，即min Σ (cost[i]/loan_amt[i]) * loan_amt[i] / total_loan_amt * x[i]，
    简化为 min Σ cost[i] * x[i]（在loan_amt约束下等价于最小化CPS）。
    """
    cells = list(cell_stats.keys())

    prob = pulp.LpProblem("RTA_Min_CPS", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("cell", cells, cat='Binary')

    # 目标：最小化总cost（在loan_amt约束下近似最小化CPS）
    prob += pulp.lpSum(
        x[cell] * cell_stats[cell]['cost']
        for cell in cells
        if cell_stats[cell]['ato'] > 0
    ), "Minimize_Cost"

    # 约束1: 排除区域整体SPR <= spr_threshold
    prob += (
        pulp.lpSum(
            x[cell] * (cell_stats[cell]['safe_adt'] - spr_threshold * cell_stats[cell]['ato'])
            for cell in cells
            if cell_stats[cell]['ato'] > 0
        ) <= 0,
        "SPR_Constraint"
    )

    # 约束2: 对照组排除交易占比 <= max_exclude_ratio
    prob += (
        pulp.lpSum(
            x[cell] * cell_stats[cell]['ctrl_amt_ratio']
            for cell in cells
        ) <= max_exclude_ratio,
        "Volume_Constraint"
    )

    # 约束3: 质量守卫（同主求解器）
    for cell in cells:
        if cell_stats[cell]['ato'] > 0 and cell_stats[cell]['spr'] > 2 * spr_threshold:
            prob += x[cell] == 0, f"Quality_Guard_{cell[0]}_{cell[1]}"

    # 约束4: 必须排除至少1个格子
    prob += (
        pulp.lpSum(x[cell] for cell in cells if cell_stats[cell]['ato'] > 0) >= 1,
        "Non_Empty"
    )

    solver = pulp.PULP_CBC_CMD(msg=0)
    status = prob.solve(solver)

    if status != pulp.constants.LpStatusOptimal:
        print(f"  [WARNING] 纯CPS最优未找到最优解，状态: {pulp.LpStatus[status]}")
        return []

    return [cell for cell in cells if pulp.value(x[cell]) > 0.5]


def _solve_ilp_with_cps_constraint(cell_stats, spr_threshold, max_exclude_ratio, cps_epsilon):
    """
    epsilon-constraint: 最大化SPR收益，同时约束 CPS <= cps_epsilon

    CPS线性化: cost / loan_amt <= epsilon
    <=> cost <= epsilon * loan_amt
    <=> Σ cost[i]*x[i] <= epsilon * Σ loan_amt[i]*x[i]
    <=> Σ (cost[i] - epsilon * loan_amt[i]) * x[i] <= 0
    """
    cells = list(cell_stats.keys())

    prob = pulp.LpProblem("RTA_SPR_CPS_Epsilon", pulp.LpMaximize)
    x = pulp.LpVariable.dicts("cell", cells, cat='Binary')

    # 目标：最大化SPR排除收益（同主求解器）
    prob += pulp.lpSum(
        x[cell] * (spr_threshold - cell_stats[cell]['spr']) * cell_stats[cell]['ato']
        for cell in cells
        if cell_stats[cell]['ato'] > 0
    ), "Maximize_Exclude_Benefit"

    # 约束1: 排除区域整体SPR <= spr_threshold
    prob += (
        pulp.lpSum(
            x[cell] * (cell_stats[cell]['safe_adt'] - spr_threshold * cell_stats[cell]['ato'])
            for cell in cells
            if cell_stats[cell]['ato'] > 0
        ) <= 0,
        "SPR_Constraint"
    )

    # 约束2: 对照组排除交易占比 <= max_exclude_ratio
    prob += (
        pulp.lpSum(
            x[cell] * cell_stats[cell]['ctrl_amt_ratio']
            for cell in cells
        ) <= max_exclude_ratio,
        "Volume_Constraint"
    )

    # 约束3: 质量守卫
    for cell in cells:
        if cell_stats[cell]['ato'] > 0 and cell_stats[cell]['spr'] > 2 * spr_threshold:
            prob += x[cell] == 0, f"Quality_Guard_{cell[0]}_{cell[1]}"

    # 约束4: 必须排除至少1个格子
    prob += (
        pulp.lpSum(x[cell] for cell in cells if cell_stats[cell]['ato'] > 0) >= 1,
        "Non_Empty"
    )

    # 约束5: CPS epsilon-constraint（线性化）
    # Σ cost[i]*x[i] <= epsilon * Σ loan_amt[i]*x[i]
    # <=> Σ (cost[i] - epsilon * loan_amt[i]) * x[i] <= 0
    prob += (
        pulp.lpSum(
            x[cell] * (cell_stats[cell]['cost'] - cps_epsilon * cell_stats[cell]['loan_amt'])
            for cell in cells
            if cell_stats[cell]['ato'] > 0
        ) <= 0,
        "CPS_Epsilon_Constraint"
    )

    solver = pulp.PULP_CBC_CMD(msg=0)
    status = prob.solve(solver)

    if status != pulp.constants.LpStatusOptimal:
        return []

    return [cell for cell in cells if pulp.value(x[cell]) > 0.5]


def _infer_place_in_out_regions(exclude_set, cell_stats, spr_threshold):
    """
    从ILP最优解反推初始区域/置入/置出，用于报告兼容

    逻辑：
    1. 找到最大的j使得V9RN=01Q..jQ各列的整体SPR <= 阈值 → initial_region
    2. initial_region中不在exclude_set中的 ��� place_in_region
    3. exclude_set中不在initial_region中的 → place_out_region
    """
    # 找j: V9RN各列的整体SPR
    j = 0
    for v9_idx in range(1, 13):
        v9 = f'{v9_idx:02d}Q'
        total_ato = sum(cell_stats[(f'{v8:02d}Q', v9)]['ato'] for v8 in range(1, 13))
        total_safe = sum(cell_stats[(f'{v8:02d}Q', v9)]['safe_adt'] for v8 in range(1, 13))
        if total_ato > 0 and (total_safe / total_ato) <= spr_threshold:
            j = v9_idx
        else:
            break

    # 初始区域: [V8: 01Q-12Q] x [V9RN: 01Q-jQ]
    initial_region = [(f'{v8:02d}Q', f'{v9:02d}Q') for v8 in range(1, 13) for v9 in range(1, j + 1)]
    initial_set = set(initial_region)

    # 置入: 在初始区域中但不在排除区域中
    place_in_region = [cell for cell in initial_region if cell not in exclude_set]

    # 置出: 在排除区域中但不在初始区域中
    place_out_region = [cell for cell in exclude_set if cell not in initial_set]

    return initial_region, place_in_region, place_out_region, j
