#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uplift 因果推断排除框架（原型）

支持两种模式：
1. 个体级模式：有个体级实验数据时，使用 T-Learner（两个独立的 LogisticRegression）建模
2. 聚合级降级模式：只有聚合数据时，使用分组级 CATE 估计（纯 pandas/numpy）

核心思想：
- 传统方法：排除 SPR 低的格子（相关性决策）
- Uplift方法：排除"排除后效果提升最大"的格子（因果性决策）
  CATE = E[Y|T=1,X] - E[Y|T=0,X]
  T=1: 实验组（被排除/干预），T=0: 对照组
  Y: 是否安全授信（safe_adt / ato）
  正 CATE 表示排除该格子对安全过件率有正向因果效应
"""

import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import LabelEncoder
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


# ============================================================================
# 主类
# ============================================================================

class UpliftExcludeModel:
    """
    Uplift 排除模型

    两种运行模式：
    - individual: 个体级数据，使用 T-Learner（两个 LogisticRegression）
    - aggregate:  聚合级数据，使用分组级 CATE 估计（纯 pandas/numpy）

    运行模式通过 detect_data_level() 自动判断，或在 __init__ 中指定。
    """

    def __init__(self, mode='auto'):
        """
        Args:
            mode: 'auto'（自动检测）, 'individual', 'aggregate'
        """
        self.mode = mode
        self._resolved_mode = None   # 实际使用的模式，fit() 后确定
        self.model_t1 = None         # T-Learner: 实验组模型
        self.model_t0 = None         # T-Learner: 对照组模型
        self.cate_table = None       # pd.DataFrame: CATE估计结果
        self._fitted_df = None       # 训练用数据快照（��合模式备用）
        self._v8_col = 'V8_Q'
        self._v9_col = 'V9RN_Q'

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def detect_data_level(self, df):
        """
        自动检测数据粒度。

        判断逻辑：
        - 存在 'user_id' 列 AND 行数 >= 10 × 格子数（12×12=144）→ individual
        - 否则 → aggregate

        Returns:
            str: 'individual' or 'aggregate'
        """
        has_user_id = 'user_id' in df.columns
        n_cells = 144  # 12 x 12
        if has_user_id and len(df) >= 10 * n_cells:
            return 'individual'
        return 'aggregate'

    def fit(self, df, treatment_col='group', outcome_col='t3_safe_adt',
            cost_col='cost', volume_col='t3_ato', model_x='V8', model_y='V9RN'):
        """
        训练 Uplift 模型。

        individual 模式（需要 sklearn）：
          - 特征：V8_Q 和 V9RN_Q 的 one-hot 编码
          - Treatment：group 列中非对照组为 1，对照组为 0
          - Outcome：每行用户是否安全授信（outcome_col / volume_col，聚合行则为 SPR）
          - 使用 T-Learner：分别在 T=1 和 T=0 子集上拟合 LogisticRegression

        aggregate 模式：
          - 对每个 (V8_Q, V9RN_Q) 格子按 treatment 分组聚合
          - CATE = SPR_treatment - SPR_control
          - 标准误用比例差检验的渐近公式

        Args:
            df: 预处理后的 DataFrame（必须含 V8_Q, V9RN_Q, group 等列）
            treatment_col: 分组列名（默认 'group'）
            outcome_col: 结果列名（默认 't3_safe_adt'）
            cost_col: 成本列名（默认 'cost'）
            volume_col: 申完量列名（默认 't3_ato'）
            model_x: X轴模型名（默认 'V8'，对应 V8_Q 列）
            model_y: Y轴模型名（默认 'V9RN'，对应 V9RN_Q 列）
        """
        self._v8_col = f'{model_x}_Q' if f'{model_x}_Q' in df.columns else model_x
        self._v9_col = f'{model_y}_Q' if f'{model_y}_Q' in df.columns else model_y

        # 确定实际模式
        if self.mode == 'auto':
            detected = self.detect_data_level(df)
            # 即使检测为 individual，若 sklearn 不可用则降级
            if detected == 'individual' and not HAS_SKLEARN:
                print("[Uplift] 检测到个体级数据，但 sklearn 未安装，降级到聚合模式")
                self._resolved_mode = 'aggregate'
            else:
                self._resolved_mode = detected
        else:
            if self.mode == 'individual' and not HAS_SKLEARN:
                print("[Uplift] 指定 individual 模式，但 sklearn 未安装，降级到聚合模式")
                self._resolved_mode = 'aggregate'
            else:
                self._resolved_mode = self.mode

        print(f"[Uplift] 运行模式: {self._resolved_mode}")
        self._fitted_df = df.copy()

        if self._resolved_mode == 'individual':
            self._fit_individual(df, treatment_col, outcome_col, volume_col)
        else:
            self._fit_aggregate(df, treatment_col, outcome_col, volume_col)

        return self

    def predict_cate(self, df=None):
        """
        预测每个 (V8_Q, V9RN_Q) 格子的 CATE。

        Returns:
            pd.DataFrame: columns = ['v8', 'v9', 'cate', 'cate_se', 'significant']
              - cate:        条件平均处理效应（正值=排除有正向效果）
              - cate_se:     标准误（估计值）
              - significant: 是否统计显著（|cate| > 2 * cate_se）
        """
        if self.cate_table is None:
            raise RuntimeError("模型尚未训练，请先调用 fit()")
        return self.cate_table.copy()

    def recommend_exclusion(self, spr_threshold=0.10, max_exclude_ratio=0.20,
                            significance_level=0.05):
        """
        基于 CATE 推荐排除区域。

        排除标准（满足全部）：
          1. CATE > 0（排除有正因果效果）
          2. 格子整体 SPR < spr_threshold
          3. 统计显著（|cate| > 2 * cate_se）
          4. 累计排除交易占比不超过 max_exclude_ratio

        Returns:
            dict: 与 run_ilp_algorithm 格式兼容的结果字典
        """
        if self.cate_table is None:
            raise RuntimeError("模型尚未训练，请先调用 fit()")

        df = self._fitted_df
        total_ctrl_amt = df[df['group'] != df['group'].max()]['t3_loan_amt'].sum()
        if total_ctrl_amt <= 0:
            total_ctrl_amt = df['t3_loan_amt'].sum()

        # 合并 CATE 表与格子 SPR/交易量
        cell_agg = df.groupby([self._v8_col, self._v9_col]).agg(
            ato=('t3_ato', 'sum'),
            safe_adt=('t3_safe_adt', 'sum'),
            loan_amt=('t3_loan_amt', 'sum'),
        ).reset_index()
        cell_agg.columns = ['v8', 'v9', 'ato', 'safe_adt', 'loan_amt']
        cell_agg['spr'] = np.where(
            cell_agg['ato'] > 0,
            cell_agg['safe_adt'] / cell_agg['ato'],
            0.0
        )
        cell_agg['amt_ratio'] = cell_agg['loan_amt'] / cell_agg['loan_amt'].sum()

        merged = self.cate_table.merge(cell_agg, on=['v8', 'v9'], how='left')

        # 候选：CATE>0 且 SPR<阈值 且 显著
        candidates = merged[
            (merged['cate'] > 0) &
            (merged['spr'] < spr_threshold) &
            (merged['significant'])
        ].sort_values('cate', ascending=False)

        # 按交易占比上限贪心选取
        selected = []
        cumulative_ratio = 0.0
        for _, row in candidates.iterrows():
            cell_ratio = row['amt_ratio'] if not pd.isna(row['amt_ratio']) else 0
            if cumulative_ratio + cell_ratio <= max_exclude_ratio:
                selected.append((row['v8'], row['v9']))
                cumulative_ratio += cell_ratio

        exclude_region = selected

        # 构建兼容 run_ilp_algorithm 的返回格式
        cell_stats = self._build_cell_stats(df)

        return {
            'j': 0,
            'initial_region': [],
            'place_in_region': [],
            'place_out_region': [],
            'exclude_region': exclude_region,
            'df_combined': df,
            'df_ctrl': df,   # 调用者可覆盖
            'algorithm': f'uplift_{self._resolved_mode}',
            'cell_stats': cell_stats,
            'cate_table': self.cate_table,
        }

    def compare_with_baseline(self, baseline_region):
        """
        将 Uplift 推荐与基线策略（SPR-based）对比。

        Args:
            baseline_region: 基线排除区域，格式为 set 或 list of (v8, v9)

        Returns:
            dict: {
                'baseline_region': set,
                'uplift_region': set,
                'overlap': set,
                'uplift_only': set,
                'baseline_only': set,
                'estimated_improvement': float
            }
        """
        if self.cate_table is None:
            raise RuntimeError("模型尚未训练，请先调用 fit() 和 recommend_exclusion()")

        baseline_set = set(map(tuple, baseline_region))

        # uplift 推荐（使用上次 recommend 的缓存，若没有则重新生成）
        uplift_rec = self.recommend_exclusion()
        uplift_set = set(uplift_rec['exclude_region'])

        overlap = baseline_set & uplift_set
        uplift_only = uplift_set - baseline_set      # 因果证据支持但 SPR 未覆盖
        baseline_only = baseline_set - uplift_set    # 基线排除但无因果证据

        # 估计提升：uplift_only 格子的平均 CATE 之和（近似）
        cate_map = dict(zip(
            zip(self.cate_table['v8'], self.cate_table['v9']),
            self.cate_table['cate']
        ))
        estimated_improvement = sum(
            cate_map.get(cell, 0.0) for cell in uplift_only
        )

        return {
            'baseline_region': baseline_set,
            'uplift_region': uplift_set,
            'overlap': overlap,
            'uplift_only': uplift_only,
            'baseline_only': baseline_only,
            'estimated_improvement': estimated_improvement,
        }

    # ------------------------------------------------------------------
    # 内部方法：individual 模式
    # ------------------------------------------------------------------

    def _fit_individual(self, df, treatment_col, outcome_col, volume_col):
        """T-Learner 拟合：在对照组/实验组各训练一个 LogisticRegression"""
        v8_col, v9_col = self._v8_col, self._v9_col

        # 确定 treatment：非对照组=1，对照组=0
        ctrl_val = df[treatment_col].value_counts().idxmin()  # 样本最少的为对照组
        df = df.copy()
        df['_treatment'] = (df[treatment_col] != ctrl_val).astype(int)

        # 构造特征矩阵（one-hot 编码 V8_Q + V9RN_Q）
        v8_dummies = pd.get_dummies(df[v8_col], prefix='v8')
        v9_dummies = pd.get_dummies(df[v9_col], prefix='v9')
        X = pd.concat([v8_dummies, v9_dummies], axis=1).values.astype(float)

        # 结果变量：如果是聚合行则用 SPR，否则用二值结果
        if volume_col in df.columns and df[volume_col].max() > 1:
            # 聚合数据：用 SPR 作为连续结果（T-Learner 用 LogisticRegression 近似）
            y = np.where(
                df[volume_col] > 0,
                df[outcome_col] / df[volume_col],
                0.0
            )
        else:
            y = df[outcome_col].values.astype(float)

        # 分离对照组/实验组
        mask_t1 = df['_treatment'].values == 1
        mask_t0 = df['_treatment'].values == 0

        if mask_t1.sum() < 5 or mask_t0.sum() < 5:
            print("[Uplift] 样本量不足以拟合 T-Learner，降级到聚合模式")
            self._resolved_mode = 'aggregate'
            self._fit_aggregate(df, treatment_col, outcome_col, volume_col)
            return

        X_t1, y_t1 = X[mask_t1], y[mask_t1]
        X_t0, y_t0 = X[mask_t0], y[mask_t0]

        # 将连续 SPR 二值化用于 LogisticRegression
        threshold_y = np.median(y[y > 0]) if (y > 0).any() else 0.5
        y_t1_bin = (y_t1 >= threshold_y).astype(int)
        y_t0_bin = (y_t0 >= threshold_y).astype(int)

        self.model_t1 = LogisticRegression(max_iter=500, random_state=42)
        self.model_t0 = LogisticRegression(max_iter=500, random_state=42)

        try:
            self.model_t1.fit(X_t1, y_t1_bin)
            self.model_t0.fit(X_t0, y_t0_bin)
        except Exception as e:
            print(f"[Uplift] T-Learner 拟合失败 ({e})，降级到聚合模式")
            self._resolved_mode = 'aggregate'
            self._fit_aggregate(df, treatment_col, outcome_col, volume_col)
            return

        # 为每个格子预测 CATE
        v8_list = [f'{i:02d}Q' for i in range(1, 13)]
        v9_list = [f'{i:02d}Q' for i in range(1, 13)]

        records = []
        for v8 in v8_list:
            for v9 in v9_list:
                # 构造该格子的特征向量
                cell_row = {f'v8_{c}': (1 if c == v8 else 0) for c in v8_dummies.columns.str.replace('v8_', '')}
                cell_row.update({f'v9_{c}': (1 if c == v9 else 0) for c in v9_dummies.columns.str.replace('v9_', '')})
                # 确保列顺序与训练时一致
                feat_cols = list(v8_dummies.columns) + list(v9_dummies.columns)
                cell_feat = np.array([[cell_row.get(c, 0) for c in feat_cols]])

                p1 = self.model_t1.predict_proba(cell_feat)[0][1]
                p0 = self.model_t0.predict_proba(cell_feat)[0][1]
                cate = p1 - p0
                # 标准误：用 bootstrap 简化估计（delta method 近似）
                cate_se = np.sqrt(p1 * (1 - p1) / max(mask_t1.sum(), 1) +
                                  p0 * (1 - p0) / max(mask_t0.sum(), 1))
                significant = abs(cate) > 2 * cate_se

                records.append({
                    'v8': v8, 'v9': v9,
                    'cate': cate, 'cate_se': cate_se,
                    'significant': significant,
                })

        self.cate_table = pd.DataFrame(records)
        print(f"[Uplift] T-Learner 训练完成，共 {len(self.cate_table)} 个格子的 CATE 估计")

    # ------------------------------------------------------------------
    # 内部方法：aggregate 模式
    # ------------------------------------------------------------------

    def _fit_aggregate(self, df, treatment_col, outcome_col, volume_col):
        """
        聚合级 CATE 估计（纯 pandas/numpy，无额外依赖）。

        对每个 (v8, v9) 格子：
          CATE = SPR_treatment - SPR_control
          标准误使用比例差检验的渐近公式：
            SE = sqrt(p1*(1-p1)/n1 + p0*(1-p0)/n0)
          其中 p = safe_adt / ato，n = ato（近似样本量）
        """
        v8_col, v9_col = self._v8_col, self._v9_col

        # 识别对照组：group 列唯一值中出现次数最少的（或值最小的）
        group_counts = df[treatment_col].value_counts()
        ctrl_val = group_counts.idxmin()
        df = df.copy()
        df['_is_ctrl'] = (df[treatment_col] == ctrl_val)

        v8_list = [f'{i:02d}Q' for i in range(1, 13)]
        v9_list = [f'{i:02d}Q' for i in range(1, 13)]

        # 对照组聚合
        ctrl_agg = (
            df[df['_is_ctrl']]
            .groupby([v8_col, v9_col])
            .agg(ctrl_ato=(volume_col, 'sum'), ctrl_safe=(outcome_col, 'sum'))
            .reset_index()
        )
        ctrl_agg.columns = ['v8', 'v9', 'ctrl_ato', 'ctrl_safe']

        # 实验组聚合（全量 - 对照）
        treat_agg = (
            df[~df['_is_ctrl']]
            .groupby([v8_col, v9_col])
            .agg(treat_ato=(volume_col, 'sum'), treat_safe=(outcome_col, 'sum'))
            .reset_index()
        )
        treat_agg.columns = ['v8', 'v9', 'treat_ato', 'treat_safe']

        # 构建完整格子网格（确保每个格子都有记录）
        grid = pd.DataFrame(
            [(v8, v9) for v8 in v8_list for v9 in v9_list],
            columns=['v8', 'v9']
        )
        merged = (
            grid
            .merge(ctrl_agg, on=['v8', 'v9'], how='left')
            .merge(treat_agg, on=['v8', 'v9'], how='left')
            .fillna(0)
        )

        # 计算 SPR
        merged['spr_ctrl'] = np.where(
            merged['ctrl_ato'] > 0,
            merged['ctrl_safe'] / merged['ctrl_ato'],
            np.nan
        )
        merged['spr_treat'] = np.where(
            merged['treat_ato'] > 0,
            merged['treat_safe'] / merged['treat_ato'],
            np.nan
        )

        # CATE = SPR_treat - SPR_ctrl
        merged['cate'] = merged['spr_treat'] - merged['spr_ctrl']

        # 标准误：比例差的渐近 SE
        p1 = merged['spr_treat'].fillna(0.5)
        p0 = merged['spr_ctrl'].fillna(0.5)
        n1 = merged['treat_ato'].clip(lower=1)
        n0 = merged['ctrl_ato'].clip(lower=1)
        merged['cate_se'] = np.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)

        # 统计显著：|CATE| > 2 * SE（约 95% 置信水平）
        merged['significant'] = (
            merged['cate'].notna() &
            (merged['cate'].abs() > 2 * merged['cate_se'])
        )

        # 数据不足的格子标记为不显著
        insufficient = (merged['ctrl_ato'] < 5) | (merged['treat_ato'] < 5)
        merged.loc[insufficient, 'significant'] = False

        # CATE 缺失时填 0
        merged['cate'] = merged['cate'].fillna(0.0)
        merged['cate_se'] = merged['cate_se'].fillna(1.0)

        self.cate_table = merged[['v8', 'v9', 'cate', 'cate_se', 'significant']].copy()
        n_sig = merged['significant'].sum()
        print(f"[Uplift] 聚合模式 CATE 估计完成，{n_sig}/{len(merged)} 个格子统计显著")

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _build_cell_stats(self, df):
        """构建与 ILP 兼容的 cell_stats 字典"""
        v8_list = [f'{i:02d}Q' for i in range(1, 13)]
        v9_list = [f'{i:02d}Q' for i in range(1, 13)]
        v8_col, v9_col = self._v8_col, self._v9_col

        agg = df.groupby([v8_col, v9_col]).agg(
            ato=('t3_ato', 'sum'),
            safe_adt=('t3_safe_adt', 'sum'),
            loan_amt=('t3_loan_amt', 'sum'),
            cost=('cost', 'sum'),
            expo_cnt=('expo_cnt', 'sum'),
        ).to_dict('index')

        total_amt = df['t3_loan_amt'].sum()
        cell_stats = {}
        for v8 in v8_list:
            for v9 in v9_list:
                key = (v8, v9)
                rec = agg.get((v8, v9), {})
                ato = rec.get('ato', 0)
                safe = rec.get('safe_adt', 0)
                amt = rec.get('loan_amt', 0)
                cell_stats[key] = {
                    'ato': ato,
                    'safe_adt': safe,
                    'spr': safe / ato if ato > 0 else 0.0,
                    'loan_amt': amt,
                    'cost': rec.get('cost', 0),
                    'expo_cnt': rec.get('expo_cnt', 0),
                    'ctrl_ato': ato,
                    'ctrl_safe_adt': safe,
                    'ctrl_amt': amt,
                    'ctrl_amt_ratio': amt / total_amt if total_amt > 0 else 0.0,
                }
        return cell_stats


# ============================================================================
# 便捷入口
# ============================================================================

def run_uplift_analysis(df_combined, df_ctrl, exclude_region,
                        spr_threshold=0.10, max_exclude_ratio=0.20,
                        model_x='V8', model_y='V9RN'):
    """
    运行 Uplift 因果推断分析的便捷入口。

    自动检测数据级别，训练模型，生成推荐，并与基线 SPR 策略对比。

    Args:
        df_combined: 全量数据（含所有实验组）
        df_ctrl:     对照组数据
        exclude_region: 基线排除区域（SPR-based），list of (v8, v9) tuples
        spr_threshold:  SPR 阈值（默认 0.10）
        max_exclude_ratio: 最大排除交易占比（默认 0.20）
        model_x: X轴模型名（默认 'V8'）
        model_y: Y轴模型名（默认 'V9RN'）

    Returns:
        dict: {
            'mode': str,                    # 'individual' or 'aggregate'
            'cate_table': pd.DataFrame,     # CATE 估计结果
            'uplift_recommendation': dict,  # 推荐排除区域（兼容 ILP 格式）
            'comparison': dict,             # 与基线对比
            'model': UpliftExcludeModel,    # 模型实例
        }
    """
    print("\n" + "=" * 80)
    print("Uplift 因果推断分析")
    print("=" * 80)

    model = UpliftExcludeModel(mode='auto')
    model.fit(df_combined, model_x=model_x, model_y=model_y)

    cate_table = model.predict_cate()

    uplift_rec = model.recommend_exclusion(
        spr_threshold=spr_threshold,
        max_exclude_ratio=max_exclude_ratio,
    )
    # 注入正确的 df_ctrl
    uplift_rec['df_ctrl'] = df_ctrl

    comparison = model.compare_with_baseline(exclude_region)

    # 打印对比摘要
    print(f"\n[Uplift] 基线排除格子数: {len(comparison['baseline_region'])}")
    print(f"[Uplift] Uplift 推荐排除格子数: {len(comparison['uplift_region'])}")
    print(f"[Uplift] 重叠格子数: {len(comparison['overlap'])}")
    print(f"[Uplift] 仅 Uplift 新增（因果证据支持）: {len(comparison['uplift_only'])}")
    print(f"[Uplift] 仅基线排除（无因果证据）: {len(comparison['baseline_only'])}")
    print(f"[Uplift] 估计效果提升（CATE 累计）: {comparison['estimated_improvement']:.4f}")

    return {
        'mode': model._resolved_mode,
        'cate_table': cate_table,
        'uplift_recommendation': uplift_rec,
        'comparison': comparison,
        'model': model,
    }


# ============================================================================
# HTML 报告生成
# ============================================================================

def generate_uplift_html(uplift_result):
    """
    生成 Uplift 分析 HTML 片段。

    包含：
    - 模式说明（个体级 / 聚合级降级提示）
    - CATE 热力图（ECharts，颜色编码处理效应大小）
    - 统计显著性标注
    - Uplift vs 基线策略差异摘要表

    Returns:
        str: 可直接嵌入 HTML 报告的片段
    """
    mode = uplift_result.get('mode', 'aggregate')
    cate_table = uplift_result.get('cate_table')
    comparison = uplift_result.get('comparison', {})

    if cate_table is None or cate_table.empty:
        return "<section><p>Uplift 分析数据不足，无法生成报告</p></section>"

    # ---- 构建 ECharts CATE 热力图数据 ----
    v8_list = [f'{i:02d}Q' for i in range(1, 13)]
    v9_list = [f'{i:02d}Q' for i in range(1, 13)]

    cate_map = {
        (row['v8'], row['v9']): {
            'cate': row['cate'],
            'cate_se': row['cate_se'],
            'significant': bool(row['significant']),
        }
        for _, row in cate_table.iterrows()
    }

    # 显著 / 不显著分两组
    sig_data = []       # [v9_idx, v8_idx, cate_pct]
    insig_data = []
    for v8_idx, v8 in enumerate(v8_list):
        for v9_idx, v9 in enumerate(v9_list):
            info = cate_map.get((v8, v9), {'cate': 0, 'cate_se': 0, 'significant': False})
            cate_pct = round(info['cate'] * 100, 3)
            if info['significant']:
                sig_data.append([v9_idx, v8_idx, cate_pct])
            else:
                insig_data.append([v9_idx, v8_idx, cate_pct])

    # Uplift_only / baseline_only 标注
    uplift_only = comparison.get('uplift_only', set())
    baseline_only = comparison.get('baseline_only', set())
    overlap = comparison.get('overlap', set())

    diff_data = []
    diff_labels = {'uplift_only': [], 'baseline_only': [], 'overlap': [], 'normal': []}
    for v8_idx, v8 in enumerate(v8_list):
        for v9_idx, v9 in enumerate(v9_list):
            cell = (v8, v9)
            if cell in uplift_only:
                diff_labels['uplift_only'].append([v9_idx, v8_idx, 1])
            elif cell in baseline_only:
                diff_labels['baseline_only'].append([v9_idx, v8_idx, 2])
            elif cell in overlap:
                diff_labels['overlap'].append([v9_idx, v8_idx, 3])
            else:
                diff_labels['normal'].append([v9_idx, v8_idx, 0])

    v8_labels_json = json.dumps(v8_list)
    v9_labels_json = json.dumps(v9_list)
    sig_data_json = json.dumps(sig_data)
    insig_data_json = json.dumps(insig_data)
    uplift_only_json = json.dumps(diff_labels['uplift_only'])
    baseline_only_json = json.dumps(diff_labels['baseline_only'])
    overlap_json = json.dumps(diff_labels['overlap'])
    normal_json = json.dumps(diff_labels['normal'])

    mode_label = '个体级（T-Learner）' if mode == 'individual' else '聚合级（分组 CATE 估计）'
    mode_note = ''
    if mode == 'aggregate':
        mode_note = """
        <div style="background:#fffbeb; border-left:4px solid #d69e2e; padding:0.75rem 1rem;
                    border-radius:6px; margin-bottom:1rem; font-size:0.875rem; color:#744210;">
            <strong>聚合模式提示：</strong>
            当前数据为聚合级（无个体级 user_id），CATE 基于分组 SPR 差值估计，
            因果推断精度低于个体级 T-Learner。建议优先获取个体级实验数据以提升估计精度。
        </div>
        """

    estimated_improvement = comparison.get('estimated_improvement', 0.0)
    n_uplift_only = len(uplift_only)
    n_baseline_only = len(baseline_only)
    n_overlap = len(overlap)

    chart_cate_id = 'uplift_cate_heatmap'
    chart_diff_id = 'uplift_diff_heatmap'

    html = f"""
<section id="section_uplift" style="background:white; border-radius:10px; padding:2rem 2.5rem;
    margin-bottom:1.5rem; box-shadow:0 1px 3px rgba(0,0,0,0.08); border-left:4px solid #6b46c1;">

    <h1 style="font-size:1.5rem; color:#1a365d; margin-bottom:1.5rem; padding-bottom:0.75rem;
               border-bottom:2px solid #6b46c1; font-weight:700;">
        四、Uplift 因果推断分析（原型）
    </h1>

    {mode_note}

    <div style="background:#f7fafc; border-radius:8px; padding:1rem 1.5rem; margin-bottom:1.5rem;
                font-size:0.875rem; color:#4a5568;">
        <strong>运行模式：</strong>{mode_label}
        <strong>分析格子数：</strong>{len(cate_table)}
        <strong>统计显著格子：</strong>{cate_table['significant'].sum()}
    </div>

    <!-- CATE 热力图 -->
    <h2 style="font-size:1.25rem; color:#1a365d; margin:1.5rem 0 0.75rem; font-weight:600;">
        4.1 CATE 热力图（条件平均处理效应）
    </h2>
    <p style="font-size:0.85rem; color:#718096; margin-bottom:0.5rem;">
        颜色越暖（红）代表排除效果越正向（CATE 越大）；深色边框标注统计显著格子。
        正 CATE = 排除该格子可提升整体安全过件率。
    </p>
    <div id="{chart_cate_id}" style="width:100%; height:520px;"></div>

    <!-- 差异对比热力图 -->
    <h2 style="font-size:1.25rem; color:#1a365d; margin:1.5rem 0 0.75rem; font-weight:600;">
        4.2 Uplift 推荐 vs 基线策略差异
    </h2>
    <p style="font-size:0.85rem; color:#718096; margin-bottom:0.5rem;">
        紫色=仅 Uplift 新增（因果证据支持但 SPR 未覆盖），
        橙色=仅基线排除（无因果证据），
        绿色=双方重叠，灰色=双方保留。
    </p>
    <div id="{chart_diff_id}" style="width:100%; height:520px;"></div>

    <!-- 摘要统计 -->
    <h2 style="font-size:1.25rem; color:#1a365d; margin:1.5rem 0 0.75rem; font-weight:600;">
        4.3 策略对比摘要
    </h2>
    <div style="overflow-x:auto; margin:1rem 0;">
        <table style="width:100%; border-collapse:separate; border-spacing:0; border-radius:8px;
                      overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
            <thead style="background:linear-gradient(135deg,#553c9a 0%,#6b46c1 100%); color:white;">
                <tr>
                    <th style="padding:0.75rem 1rem; text-align:center; font-size:0.825rem;">指标</th>
                    <th style="padding:0.75rem 1rem; text-align:center; font-size:0.825rem;">数值</th>
                    <th style="padding:0.75rem 1rem; text-align:center; font-size:0.825rem;">说明</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:0.875rem 1rem; text-align:center;">仅 Uplift 新增格子</td>
                    <td style="padding:0.875rem 1rem; text-align:center; font-weight:600;
                                color:#553c9a;">{n_uplift_only}</td>
                    <td style="padding:0.875rem 1rem; text-align:center; font-size:0.85rem;
                                color:#718096;">因果证据支持但 SPR 阈值未覆盖的格子</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:0.875rem 1rem; text-align:center;">仅基线排除格子</td>
                    <td style="padding:0.875rem 1rem; text-align:center; font-weight:600;
                                color:#c05621;">{n_baseline_only}</td>
                    <td style="padding:0.875rem 1rem; text-align:center; font-size:0.85rem;
                                color:#718096;">SPR 低但无显著因果证据，建议谨慎排除</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:0.875rem 1rem; text-align:center;">新旧策略重叠格子</td>
                    <td style="padding:0.875rem 1rem; text-align:center; font-weight:600;
                                color:#276749;">{n_overlap}</td>
                    <td style="padding:0.875rem 1rem; text-align:center; font-size:0.85rem;
                                color:#718096;">两种方法均支持排除，置信度最高</td>
                </tr>
                <tr>
                    <td style="padding:0.875rem 1rem; text-align:center;">估计效果提升（CATE 累计）</td>
                    <td style="padding:0.875rem 1rem; text-align:center; font-weight:600;
                                color:{'#276749' if estimated_improvement >= 0 else '#9b2c2c'};">
                        {'+' if estimated_improvement >= 0 else ''}{estimated_improvement*100:.2f}pct
                    </td>
                    <td style="padding:0.875rem 1rem; text-align:center; font-size:0.85rem;
                                color:#718096;">Uplift 新增格子的因果效应总和（估计值）</td>
                </tr>
            </tbody>
        </table>
    </div>

</section>

<script>
(function() {{
    // ---- CATE 热力图 ----
    var cateDom = document.getElementById('{chart_cate_id}');
    var cateChart = echarts.init(cateDom);

    var v8Labels = {v8_labels_json};
    var v9Labels = {v9_labels_json};
    var sigData = {sig_data_json};
    var insigData = {insig_data_json};

    var cateOption = {{
        tooltip: {{
            position: 'top',
            formatter: function(params) {{
                var v9 = v9Labels[params.data[0]];
                var v8 = v8Labels[params.data[1]];
                var cate = params.data[2];
                var isSig = params.seriesName === '显著';
                return 'V8: ' + v8 + '<br/>V9RN: ' + v9 +
                       '<br/>CATE: ' + cate.toFixed(2) + '%' +
                       '<br/>显著性: ' + (isSig ?
                           '<span style="color:#553c9a;font-weight:600;">显著</span>' :
                           '<span style="color:#999;">不显著</span>');
            }}
        }},
        legend: {{
            data: ['显著', '不显著'],
            top: 5,
            textStyle: {{ fontSize: 11 }}
        }},
        grid: {{ left: '80px', right: '130px', top: '45px', bottom: '60px' }},
        xAxis: {{
            type: 'category', data: v9Labels,
            name: 'V9RN', nameLocation: 'middle', nameGap: 35,
            axisLabel: {{ fontSize: 11 }}, splitArea: {{ show: true }}
        }},
        yAxis: {{
            type: 'category', data: v8Labels,
            name: 'V8', nameLocation: 'middle', nameGap: 50,
            axisLabel: {{ fontSize: 11 }}, splitArea: {{ show: true }}
        }},
        visualMap: {{
            type: 'continuous',
            min: -15, max: 15,
            inRange: {{
                color: ['#2166ac', '#92c5de', '#f7f7f7', '#f4a582', '#b2182b']
            }},
            orient: 'vertical',
            right: 10, top: 'center',
            textStyle: {{ fontSize: 11 }},
            text: ['CATE高\n(排除有效)', 'CATE低\n(排除有害)'],
            dimension: 2,
            seriesIndex: [0, 1]
        }},
        series: [
            {{
                name: '显著',
                type: 'heatmap',
                data: sigData,
                label: {{
                    show: true, fontSize: 9,
                    formatter: function(p) {{ return p.data[2].toFixed(1) + '%'; }}
                }},
                itemStyle: {{
                    borderColor: '#333', borderWidth: 2
                }},
                emphasis: {{ itemStyle: {{ shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }} }}
            }},
            {{
                name: '不显著',
                type: 'heatmap',
                data: insigData,
                label: {{
                    show: true, fontSize: 8, opacity: 0.7,
                    formatter: function(p) {{ return p.data[2].toFixed(1) + '%'; }}
                }},
                emphasis: {{ itemStyle: {{ shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' }} }}
            }}
        ]
    }};
    cateChart.setOption(cateOption);
    window.addEventListener('resize', function() {{ cateChart.resize(); }});

    // ---- 差异对比热力图 ----
    var diffDom = document.getElementById('{chart_diff_id}');
    var diffChart = echarts.init(diffDom);

    var upliftOnlyData = {uplift_only_json};
    var baselineOnlyData = {baseline_only_json};
    var overlapData = {overlap_json};
    var normalData2 = {normal_json};

    var diffOption = {{
        tooltip: {{
            position: 'top',
            formatter: function(params) {{
                var v9 = v9Labels[params.data[0]];
                var v8 = v8Labels[params.data[1]];
                var labels = {{'仅Uplift新增': '因果证据支持，SPR阈值未覆盖',
                               '仅基线排除': '无显著因果证据，SPR低于阈值',
                               '双方重叠': '两种方法均支持排除',
                               '双方保留': '均不排除'}};
                return 'V8: ' + v8 + '<br/>V9RN: ' + v9 +
                       '<br/>状态: <strong>' + params.seriesName + '</strong>' +
                       '<br/>' + (labels[params.seriesName] || '');
            }}
        }},
        legend: {{
            data: ['仅Uplift新增', '仅基线排除', '双方重叠', '双方保留'],
            top: 5, textStyle: {{ fontSize: 11 }}
        }},
        grid: {{ left: '80px', right: '20px', top: '45px', bottom: '60px' }},
        xAxis: {{
            type: 'category', data: v9Labels,
            name: 'V9RN', nameLocation: 'middle', nameGap: 35,
            axisLabel: {{ fontSize: 11 }}, splitArea: {{ show: true }}
        }},
        yAxis: {{
            type: 'category', data: v8Labels,
            name: 'V8', nameLocation: 'middle', nameGap: 50,
            axisLabel: {{ fontSize: 11 }}, splitArea: {{ show: true }}
        }},
        series: [
            {{
                name: '仅Uplift新增',
                type: 'heatmap', data: upliftOnlyData,
                itemStyle: {{ color: '#553c9a' }},
                label: {{ show: true, fontSize: 9, color: '#fff',
                          formatter: function() {{ return 'Uplift'; }} }},
                emphasis: {{ itemStyle: {{ shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.4)' }} }}
            }},
            {{
                name: '仅基线排除',
                type: 'heatmap', data: baselineOnlyData,
                itemStyle: {{ color: '#fc8d59' }},
                label: {{ show: true, fontSize: 9, color: '#fff',
                          formatter: function() {{ return '基线'; }} }},
                emphasis: {{ itemStyle: {{ shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.4)' }} }}
            }},
            {{
                name: '双方重叠',
                type: 'heatmap', data: overlapData,
                itemStyle: {{ color: '#38a169' }},
                label: {{ show: true, fontSize: 9, color: '#fff',
                          formatter: function() {{ return '重叠'; }} }},
                emphasis: {{ itemStyle: {{ shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.4)' }} }}
            }},
            {{
                name: '双方保留',
                type: 'heatmap', data: normalData2,
                itemStyle: {{ color: '#e0e0e0' }},
                label: {{ show: false }},
                emphasis: {{ itemStyle: {{ shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.4)' }} }}
            }}
        ]
    }};
    diffChart.setOption(diffOption);
    window.addEventListener('resize', function() {{ diffChart.resize(); }});
}})();
</script>
"""
    return html
