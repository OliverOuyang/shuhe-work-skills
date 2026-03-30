"""
置入置出算法模块
实现基于安全过件率的二维排除区域识别算法
"""

import pandas as pd
import numpy as np


def run_place_in_out_algorithm(df_combined, df_ctrl, spr_threshold=0.10, max_exclude_ratio=0.20):
    """
    执行完整的置入置出算法

    Args:
        df_combined: 全量数据（实验组+对照组）
        df_ctrl: 对照组数据
        spr_threshold: 安全过件率阈值（默认0.10）
        max_exclude_ratio: 最大排除交易占比（默认0.20）

    Returns:
        dict: 包含算法结果的字典
    """
    print("\n" + "="*100)
    print("RTA排除策略算法（置入置出版）")
    print("="*100)

    # 步骤1：初始圈选
    j, initial_region = step1_initial_selection(df_combined, df_ctrl, spr_threshold, max_exclude_ratio)

    # 步骤2：置入
    place_in_region = step2_place_in(df_combined, initial_region, j, spr_threshold)

    # 步骤3：置出
    place_out_region = step3_place_out(df_combined, j, spr_threshold)

    # 步骤4：计算最终排除区域
    exclude_region = step4_final_exclusion(initial_region, place_in_region, place_out_region)

    # 步骤5：约束条件验证
    is_valid = step5_validate_constraints(df_ctrl, exclude_region, max_exclude_ratio)

    # 如果不满足约束，尝试调整
    if not is_valid:
        print("\n排除交易占比超过20%，尝试调整阈值...")
        exclude_region, place_out_region = adjust_threshold(
            df_combined, df_ctrl, initial_region, place_in_region,
            j, spr_threshold, max_exclude_ratio
        )

    return {
        'j': j,
        'initial_region': initial_region,
        'place_in_region': place_in_region,
        'place_out_region': place_out_region,
        'exclude_region': exclude_region,
        'df_combined': df_combined,
        'df_ctrl': df_ctrl
    }


def step1_initial_selection(df_combined, df_ctrl, spr_threshold, max_exclude_ratio):
    """
    步骤1：初始圈选

    在V8 x V9RN二维交叉中圈选V9RN单个分组下安全过件率<=阈值的客群

    Args:
        df_combined: 全量数据
        df_ctrl: 对照组数据
        spr_threshold: 安全过件率阈值
        max_exclude_ratio: 最大排除交易占比

    Returns:
        tuple: (j, initial_region)
    """
    print("\n" + "="*100)
    print("步骤1：初始圈选")
    print("="*100)

    # 计算V9RN各分位的安全过件率
    v9rn_stats = df_combined.groupby('V9RN_Q').agg({
        't3_ato': 'sum',
        't3_safe_adt': 'sum'
    }).reset_index()
    v9rn_stats['safe_rate'] = v9rn_stats['t3_safe_adt'] / v9rn_stats['t3_ato']

    # 找到最大的j，使得V9RN=01Q到j的所有分组安全过件率都<=阈值
    j = 0
    for i in range(1, 13):
        v9rn_q = f'{i:02d}Q'
        rate = v9rn_stats[v9rn_stats['V9RN_Q'] == v9rn_q]['safe_rate'].values
        if len(rate) > 0 and rate[0] <= spr_threshold:
            j = i
        else:
            break

    print(f"\n初始圈选: j = {j}")
    print(f"初始区域: [V8: 01Q-12Q] x [V9RN: 01Q-{j:02d}Q]")

    # 生成初始区域的所有格子
    initial_region = [(f'{v8:02d}Q', f'{v9:02d}Q') for v8 in range(1, 13) for v9 in range(1, j+1)]
    print(f"初始格子数: {len(initial_region)}")

    # 计算初始区域的安全过件率
    initial_data = df_combined[df_combined.apply(
        lambda row: (row['V8_Q'], row['V9RN_Q']) in initial_region, axis=1
    )]
    initial_safe_rate = initial_data['t3_safe_adt'].sum() / initial_data['t3_ato'].sum()
    print(f"初始SPR: {initial_safe_rate*100:.2f}%")

    # 检查对照组排除交易占比
    initial_ctrl = df_ctrl[df_ctrl.apply(
        lambda row: (row['V8_Q'], row['V9RN_Q']) in initial_region, axis=1
    )]
    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()
    initial_ctrl_ratio = initial_ctrl['t3_loan_amt'].sum() / total_ctrl_amt
    print(f"对照组排除交易占比: {initial_ctrl_ratio*100:.2f}%")

    if initial_ctrl_ratio >= max_exclude_ratio:
        raise ValueError(f"错误：V9RN单维排除交易已超出{max_exclude_ratio*100:.0f}%")

    return j, initial_region


def step2_place_in(df_combined, initial_region, j, spr_threshold):
    """
    步骤2：置入（从右下往左上扩充）- 矩形扩充版本

    从初始排除区域���右下角[12,j]开始，向左上方扩充
    保持置入区域为矩形，优先向左扩充，其次向上扩充

    算法逻辑：
    1. 检查[12,j]的SPR
       - 如果SPR<10%且j>1，检查[12,j-1]和[11,j]的整体SPR是否都<10%，若是则置入为空
    2. 如果[12,j]的SPR>=10%
       - 从[12,j]开始作为置入区域起点
       - 优先向左扩充，扩充区域高度=当前置入区域高度（保持矩形）
       - 若无法向左扩充，则向上扩充，扩充区域宽度=当前置入区域宽度
       - 重复直到无法扩充

    Args:
        df_combined: 全量数据
        initial_region: 初始排除区域
        j: 初始V9RN的最大分位
        spr_threshold: 安全过件率阈值

    Returns:
        list: 置入区域（从初始排除区域中移除的格子）
    """
    print("\n" + "="*100)
    print("步骤2：置入（从右下往左上扩充）- 矩形扩充版本")
    print("="*100)

    place_in_region = []

    # 置入区域的边界（初始为空，从[12,j]开始）
    place_v8_min = 12  # 置入区域的V8最小值（上边界）
    place_v8_max = 12  # 置入区域的V8最大值（下边界）
    place_v9_min = j   # 置入区域的V9RN最小值（左边界）
    place_v9_max = j   # 置入区域的V9RN最大值（右边界）

    print(f"\n初始检查点: [V8: 12Q, V9RN: {j:02d}Q]")

    # 步骤1: 检查[12,j]的SPR
    cell_12_j = [('12Q', f'{j:02d}Q')]
    data_12_j = df_combined[df_combined.apply(
        lambda row: (row['V8_Q'], row['V9RN_Q']) in cell_12_j, axis=1
    )]

    if data_12_j['t3_ato'].sum() > 0:
        spr_12_j = data_12_j['t3_safe_adt'].sum() / data_12_j['t3_ato'].sum()
        print(f"[12Q, {j:02d}Q] SPR: {spr_12_j*100:.2f}%")

        # 情况1: [12,j]的SPR<10%
        if spr_12_j < spr_threshold:
            print(f"\n[12Q, {j:02d}Q] SPR < {spr_threshold*100:.0f}%")

            if j > 1:
                # 检查[12,j]到[12,j-1]的整体SPR
                cells_12_j_to_j_minus_1 = [('12Q', f'{j:02d}Q'), ('12Q', f'{j-1:02d}Q')]
                data_left = df_combined[df_combined.apply(
                    lambda row: (row['V8_Q'], row['V9RN_Q']) in cells_12_j_to_j_minus_1, axis=1
                )]
                spr_left = data_left['t3_safe_adt'].sum() / data_left['t3_ato'].sum() if data_left['t3_ato'].sum() > 0 else 0

                # 检查[12,j]到[11,j]的整体SPR
                cells_12_to_11_j = [('12Q', f'{j:02d}Q'), ('11Q', f'{j:02d}Q')]
                data_up = df_combined[df_combined.apply(
                    lambda row: (row['V8_Q'], row['V9RN_Q']) in cells_12_to_11_j, axis=1
                )]
                spr_up = data_up['t3_safe_adt'].sum() / data_up['t3_ato'].sum() if data_up['t3_ato'].sum() > 0 else 0

                print(f"  检查[12Q,{j:02d}Q]到[12Q,{j-1:02d}Q]整体SPR: {spr_left*100:.2f}%")
                print(f"  检查[12Q,{j:02d}Q]到[11Q,{j:02d}Q]整体SPR: {spr_up*100:.2f}%")

                if spr_left < spr_threshold and spr_up < spr_threshold:
                    print(f"  两个方向整体SPR均<{spr_threshold*100:.0f}%, 置入为空")
                    print(f"\n置入区域: 0 个格子")
                    return place_in_region
                else:
                    print(f"  不满足置入为空条件（至少一个方向SPR>={spr_threshold*100:.0f}%）")

            elif j == 1:
                # j=1时，只检查[12,j]到[11,j]的整体SPR
                cells_12_to_11_j = [('12Q', f'{j:02d}Q'), ('11Q', f'{j:02d}Q')]
                data_up = df_combined[df_combined.apply(
                    lambda row: (row['V8_Q'], row['V9RN_Q']) in cells_12_to_11_j, axis=1
                )]
                spr_up = data_up['t3_safe_adt'].sum() / data_up['t3_ato'].sum() if data_up['t3_ato'].sum() > 0 else 0

                print(f"  j=1，检查[12Q,{j:02d}Q]到[11Q,{j:02d}Q]整体SPR: {spr_up*100:.2f}%")

                if spr_up < spr_threshold:
                    print(f"  整体SPR<{spr_threshold*100:.0f}%, 置入为空")
                    print(f"\n置入区域: 0 个格子")
                    return place_in_region
                else:
                    print(f"  不满足置入为空条件（整体SPR>={spr_threshold*100:.0f}%）")

        # 情况2: 开始扩充（不管SPR是多少，只要不满足置入为空条件就扩充）
        print(f"\n开始置入扩充")

        # 将[12,j]加入置入区域
        place_in_region.append(('12Q', f'{j:02d}Q'))
        print(f"  [12Q, {j:02d}Q] 加入置入区域")
        print(f"  当前置入区域: [V8: {place_v8_min:02d}Q-{place_v8_max:02d}Q] x [V9RN: {place_v9_min:02d}Q-{place_v9_max:02d}Q]")

        step = 0
        while True:
            expanded = False

            # 优先1: 向左扩充（V9RN减少）
            if place_v9_min > 1:
                new_v9 = place_v9_min - 1
                # 扩充区域的高度等于当前置入区域的高度
                new_cells = [(f'{v8:02d}Q', f'{new_v9:02d}Q')
                            for v8 in range(place_v8_min, place_v8_max + 1)]

                new_data = df_combined[df_combined.apply(
                    lambda row: (row['V8_Q'], row['V9RN_Q']) in new_cells, axis=1
                )]

                if new_data['t3_ato'].sum() > 0:
                    new_spr = new_data['t3_safe_adt'].sum() / new_data['t3_ato'].sum()
                    step += 1
                    print(f"\n步骤{step}: 尝试向左扩充到V9RN={new_v9:02d}Q")
                    print(f"  扩充区域: [V8: {place_v8_min:02d}Q-{place_v8_max:02d}Q] x [V9RN: {new_v9:02d}Q]")
                    print(f"  扩充区域SPR: {new_spr*100:.2f}%")

                    if new_spr >= spr_threshold:
                        place_in_region.extend(new_cells)
                        place_v9_min = new_v9
                        expanded = True
                        print(f"  [OK] SPR>={spr_threshold*100:.0f}%, 向左扩充成功")
                        print(f"  当前置入区域: [V8: {place_v8_min:02d}Q-{place_v8_max:02d}Q] x [V9RN: {place_v9_min:02d}Q-{place_v9_max:02d}Q]")
                        continue  # 继续尝试向左扩充
                    else:
                        print(f"  [NO] SPR<{spr_threshold*100:.0f}%, 无法向左扩充")

            # 优先2: 向上扩充（V8减少）
            if not expanded and place_v8_min > 1:
                new_v8 = place_v8_min - 1
                # 扩充区域的宽度等于当前置入区域的宽度
                new_cells = [(f'{new_v8:02d}Q', f'{v9:02d}Q')
                            for v9 in range(place_v9_min, place_v9_max + 1)]

                new_data = df_combined[df_combined.apply(
                    lambda row: (row['V8_Q'], row['V9RN_Q']) in new_cells, axis=1
                )]

                if new_data['t3_ato'].sum() > 0:
                    new_spr = new_data['t3_safe_adt'].sum() / new_data['t3_ato'].sum()
                    step += 1
                    print(f"\n步骤{step}: 尝试向上扩充到V8={new_v8:02d}Q")
                    print(f"  扩充区域: [V8: {new_v8:02d}Q] x [V9RN: {place_v9_min:02d}Q-{place_v9_max:02d}Q]")
                    print(f"  扩充区域SPR: {new_spr*100:.2f}%")

                    if new_spr >= spr_threshold:
                        place_in_region.extend(new_cells)
                        place_v8_min = new_v8
                        expanded = True
                        print(f"  [OK] SPR>={spr_threshold*100:.0f}%, 向上扩充成功")
                        print(f"  当前置入区域: [V8: {place_v8_min:02d}Q-{place_v8_max:02d}Q] x [V9RN: {place_v9_min:02d}Q-{place_v9_max:02d}Q]")
                        continue  # 继续流程2
                    else:
                        print(f"  [NO] SPR<{spr_threshold*100:.0f}%, 无法向上扩充")

            # 无法继续扩充
            if not expanded:
                print(f"\n无法继续扩充，置入完成")
                break

    print(f"\n置入区域: {len(place_in_region)} 个格子")
    if place_in_region:
        print(f"置入区域范围: [V8: {place_v8_min:02d}Q-{place_v8_max:02d}Q] x [V9RN: {place_v9_min:02d}Q-{place_v9_max:02d}Q]")

    return place_in_region


def step3_place_out(df_combined, j, spr_threshold):
    """
    步骤3：置出（从左上往右下扩充）- 矩形扩充版本

    从[1, j+1]位置开始，向右下方扩充
    保持置出区域为矩形，优先向下扩充，其次向右扩充

    算法逻辑：
    1. 检查[1,j+1]的SPR
       - 如果SPR>10%，检查[1,j+1]到[2,j+1]和[1,j+1]到[1,j+2]的整体SPR是否都>10%，若是则置出为空
    2. 如果[1,j+1]的SPR<=10%
       - 从[1,j+1]开始作为置出区域起点
       - 优先向下扩充，扩充区域宽度=当前置出区域宽度（保持矩形）
       - 若无法向下扩充，则向右扩充，扩充区域高度=当前置出区域高度
       - 重复直到无法扩充

    Args:
        df_combined: 全量数据
        j: 初始V9RN的最大分位
        spr_threshold: 安全过件率阈值

    Returns:
        list: 置出区域（新增到排除区域的格子）
    """
    print("\n" + "="*100)
    print("步骤3：置出（从左上往右下扩充）- 矩形扩充版本")
    print("="*100)

    place_out_region = []

    if j >= 12:
        print("\nj>=12, 无置出空间")
        return place_out_region

    # 置出区域的边界（初始为空，从[1,j+1]开始）
    place_v8_min = 1   # 置出区域的V8最小值（上边界）
    place_v8_max = 1   # 置出区域的V8最大值（下边界）
    place_v9_min = j+1 # 置出区域的V9RN最小值（左边界）
    place_v9_max = j+1 # 置出区域的V9RN最大值（右边界）

    print(f"\n初始检查点: [V8: 01Q, V9RN: {j+1:02d}Q]")

    # 步骤1: 检查[1,j+1]的SPR
    cell_1_j_plus_1 = [('01Q', f'{j+1:02d}Q')]
    data_1_j_plus_1 = df_combined[df_combined.apply(
        lambda row: (row['V8_Q'], row['V9RN_Q']) in cell_1_j_plus_1, axis=1
    )]

    if data_1_j_plus_1['t3_ato'].sum() > 0:
        spr_1_j_plus_1 = data_1_j_plus_1['t3_safe_adt'].sum() / data_1_j_plus_1['t3_ato'].sum()
        print(f"[01Q, {j+1:02d}Q] SPR: {spr_1_j_plus_1*100:.2f}%")

        # 情况1: [1,j+1]的SPR>10%
        if spr_1_j_plus_1 > spr_threshold:
            print(f"\n[01Q, {j+1:02d}Q] SPR > {spr_threshold*100:.0f}%")

            # 检查[1,j+1]到[2,j+1]的整体SPR
            cells_down = [('01Q', f'{j+1:02d}Q'), ('02Q', f'{j+1:02d}Q')]
            data_down = df_combined[df_combined.apply(
                lambda row: (row['V8_Q'], row['V9RN_Q']) in cells_down, axis=1
            )]
            spr_down = data_down['t3_safe_adt'].sum() / data_down['t3_ato'].sum() if data_down['t3_ato'].sum() > 0 else 0

            # 检查[1,j+1]到[1,j+2]的整体SPR
            if j+1 < 12:
                cells_right = [('01Q', f'{j+1:02d}Q'), ('01Q', f'{j+2:02d}Q')]
                data_right = df_combined[df_combined.apply(
                    lambda row: (row['V8_Q'], row['V9RN_Q']) in cells_right, axis=1
                )]
                spr_right = data_right['t3_safe_adt'].sum() / data_right['t3_ato'].sum() if data_right['t3_ato'].sum() > 0 else 0

                print(f"  检查[01Q,{j+1:02d}Q]到[02Q,{j+1:02d}Q]整体SPR: {spr_down*100:.2f}%")
                print(f"  检查[01Q,{j+1:02d}Q]到[01Q,{j+2:02d}Q]整体SPR: {spr_right*100:.2f}%")

                if spr_down > spr_threshold and spr_right > spr_threshold:
                    print(f"  两个方向整体SPR均>{spr_threshold*100:.0f}%, 置出为空")
                    print(f"\n置出区域: 0 个格子")
                    return place_out_region
                else:
                    print(f"  不满足置出为空条件（至少一个方向SPR<={spr_threshold*100:.0f}%）")
            else:
                # j+1=12时，只检查向下方向
                print(f"  j+1=12，检查[01Q,{j+1:02d}Q]到[02Q,{j+1:02d}Q]整体SPR: {spr_down*100:.2f}%")
                if spr_down > spr_threshold:
                    print(f"  整体SPR>{spr_threshold*100:.0f}%, 置出为空")
                    print(f"\n置出区域: 0 个格子")
                    return place_out_region
                else:
                    print(f"  不满足置出为空条件（整体SPR<={spr_threshold*100:.0f}%）")

        # 情况2: [1,j+1]的SPR<=10%，开始扩充
        if spr_1_j_plus_1 <= spr_threshold:
            print(f"\n[01Q, {j+1:02d}Q] SPR <= {spr_threshold*100:.0f}%, 开始置出扩充")

            # 将[1,j+1]加入置出区域
            place_out_region.append(('01Q', f'{j+1:02d}Q'))
            print(f"  [01Q, {j+1:02d}Q] 加入置出区域")
            print(f"  当前置出区域: [V8: {place_v8_min:02d}Q-{place_v8_max:02d}Q] x [V9RN: {place_v9_min:02d}Q-{place_v9_max:02d}Q]")

            step = 0
            while True:
                expanded = False

                # 优先1: 向下扩充（V8增加）
                if place_v8_max < 12:
                    new_v8 = place_v8_max + 1
                    # 扩充区域的宽度等于当前置出区域的宽度
                    new_cells = [(f'{new_v8:02d}Q', f'{v9:02d}Q')
                                for v9 in range(place_v9_min, place_v9_max + 1)]

                    new_data = df_combined[df_combined.apply(
                        lambda row: (row['V8_Q'], row['V9RN_Q']) in new_cells, axis=1
                    )]

                    if new_data['t3_ato'].sum() > 0:
                        new_spr = new_data['t3_safe_adt'].sum() / new_data['t3_ato'].sum()
                        step += 1
                        print(f"\n步骤{step}: 尝试向下扩充到V8={new_v8:02d}Q")
                        print(f"  扩充区域: [V8: {new_v8:02d}Q] x [V9RN: {place_v9_min:02d}Q-{place_v9_max:02d}Q]")
                        print(f"  扩充区域SPR: {new_spr*100:.2f}%")

                        if new_spr <= spr_threshold:
                            place_out_region.extend(new_cells)
                            place_v8_max = new_v8
                            expanded = True
                            print(f"  [OK] SPR<={spr_threshold*100:.0f}%, 向下扩充成功")
                            print(f"  当前置出区域: [V8: {place_v8_min:02d}Q-{place_v8_max:02d}Q] x [V9RN: {place_v9_min:02d}Q-{place_v9_max:02d}Q]")
                            continue  # 继续尝试向下扩充
                        else:
                            print(f"  [NO] SPR>{spr_threshold*100:.0f}%, 无法向下扩充")

                # 优先2: 向右扩充（V9RN增加）
                if not expanded and place_v9_max < 12:
                    new_v9 = place_v9_max + 1
                    # 扩充区域的高度等于当前置出区域的高度
                    new_cells = [(f'{v8:02d}Q', f'{new_v9:02d}Q')
                                for v8 in range(place_v8_min, place_v8_max + 1)]

                    new_data = df_combined[df_combined.apply(
                        lambda row: (row['V8_Q'], row['V9RN_Q']) in new_cells, axis=1
                    )]

                    if new_data['t3_ato'].sum() > 0:
                        new_spr = new_data['t3_safe_adt'].sum() / new_data['t3_ato'].sum()
                        step += 1
                        print(f"\n步骤{step}: 尝试向右扩充到V9RN={new_v9:02d}Q")
                        print(f"  扩充区域: [V8: {place_v8_min:02d}Q-{place_v8_max:02d}Q] x [V9RN: {new_v9:02d}Q]")
                        print(f"  扩充区域SPR: {new_spr*100:.2f}%")

                        if new_spr <= spr_threshold:
                            place_out_region.extend(new_cells)
                            place_v9_max = new_v9
                            expanded = True
                            print(f"  [OK] SPR<={spr_threshold*100:.0f}%, 向右扩充成功")
                            print(f"  当前置出区域: [V8: {place_v8_min:02d}Q-{place_v8_max:02d}Q] x [V9RN: {place_v9_min:02d}Q-{place_v9_max:02d}Q]")
                            continue  # 继续流程2
                        else:
                            print(f"  [NO] SPR>{spr_threshold*100:.0f}%, 无法向右扩充")

                # 无法继续扩充
                if not expanded:
                    print(f"\n无法继续扩充，置出完成")
                    break

    print(f"\n置出区域: {len(place_out_region)} 个格子")
    if place_out_region:
        print(f"置出区域范围: [V8: {place_v8_min:02d}Q-{place_v8_max:02d}Q] x [V9RN: {place_v9_min:02d}Q-{place_v9_max:02d}Q]")

    return place_out_region


def step4_final_exclusion(initial_region, place_in_region, place_out_region):
    """
    步骤4：计算最终排除区域

    最终排除 = 初始区域 - 置入区域 + 置出区域

    Args:
        initial_region: 初始排除区域
        place_in_region: 置入区域
        place_out_region: 置出区域

    Returns:
        list: 最终排除区域
    """
    print("\n" + "="*100)
    print("步骤4：计算最终排除区域")
    print("="*100)

    exclude_region = list((set(initial_region) - set(place_in_region)) | set(place_out_region))

    print(f"\n公式: 最终排除 = 初始区域 - 置入区域 + 置出区域")
    print(f"  初始区域: {len(initial_region)} 个格子")
    print(f"  置入区域: {len(place_in_region)} 个格子")
    print(f"  置出区域: {len(place_out_region)} 个格子")
    print(f"  最终排除: {len(exclude_region)} 个格子")

    return exclude_region


def step5_validate_constraints(df_ctrl, exclude_region, max_exclude_ratio):
    """
    步骤5：约束条件验证

    验证对照组排除交易占比是否<=最大排除比例

    Args:
        df_ctrl: 对照组数据
        exclude_region: 最终排除区域
        max_exclude_ratio: 最大排除交易占比

    Returns:
        bool: 是否满足约束条件
    """
    print("\n" + "="*100)
    print("步骤5：约束条件验证")
    print("="*100)

    exclude_ctrl = df_ctrl[df_ctrl.apply(
        lambda row: (row['V8_Q'], row['V9RN_Q']) in exclude_region, axis=1
    )]

    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()
    exclude_ctrl_ratio = exclude_ctrl['t3_loan_amt'].sum() / total_ctrl_amt
    exclude_ctrl_spr = exclude_ctrl['t3_safe_adt'].sum() / exclude_ctrl['t3_ato'].sum()

    print(f"\n约束条件:")
    print(f"  1. 排除交易占比 <= {max_exclude_ratio*100:.0f}%")
    print(f"  2. 排除SPR <= 10% (目标)")

    print(f"\n实际结果:")
    print(f"  排除交易占比: {exclude_ctrl_ratio*100:.2f}%")
    print(f"  排除SPR: {exclude_ctrl_spr*100:.2f}%")

    if exclude_ctrl_ratio <= max_exclude_ratio:
        print(f"  [PASS] 排除交易占比满足约束")
        return True
    else:
        print(f"  [FAIL] 排除交易占比超过{max_exclude_ratio*100:.0f}%")
        return False


def adjust_threshold(df_combined, df_ctrl, initial_region, place_in_region,
                     j, spr_threshold, max_exclude_ratio, max_iterations=10):
    """
    调整阈值以满足约束条件

    如果排除交易占比超过最大值，降低置出阈值重新执行

    Args:
        df_combined: 全量数据
        df_ctrl: 对照组数据
        initial_region: 初始排除区域
        place_in_region: 置入区域
        j: 初始V9RN的最大分位
        spr_threshold: 原始安全过件率阈值
        max_exclude_ratio: 最大排除交易占比
        max_iterations: 最大迭代次数

    Returns:
        tuple: (exclude_region, place_out_region)
    """
    print("\n" + "="*100)
    print("调整阈值以满足约束条件")
    print("="*100)

    current_threshold = spr_threshold
    total_ctrl_amt = df_ctrl['t3_loan_amt'].sum()

    for iteration in range(max_iterations):
        # 降低阈值
        current_threshold = current_threshold * 0.9
        print(f"\n迭代{iteration+1}: 调整置出阈值为 {current_threshold*100:.2f}%")

        # 重新执行置出
        place_out_region = step3_place_out(df_combined, j, current_threshold)

        # 计算最终排除区域
        exclude_region = list((set(initial_region) - set(place_in_region)) | set(place_out_region))

        # 验证约束
        exclude_ctrl = df_ctrl[df_ctrl.apply(
            lambda row: (row['V8_Q'], row['V9RN_Q']) in exclude_region, axis=1
        )]
        exclude_ctrl_ratio = exclude_ctrl['t3_loan_amt'].sum() / total_ctrl_amt

        print(f"  排除交易占比: {exclude_ctrl_ratio*100:.2f}%")

        if exclude_ctrl_ratio <= max_exclude_ratio:
            print(f"  [SUCCESS] 满足约束条件")
            return exclude_region, place_out_region

    print(f"\n[WARNING] ���到最大迭代次数，仍无法满足约束条件")
    return exclude_region, place_out_region
