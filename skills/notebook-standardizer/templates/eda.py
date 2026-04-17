# [RUN] 快速 EDA — 排除包数据基础统计与分布
# 输入: df_precise (精准排除包), df_api (API排除包)
# 输出: 每个 DataFrame 的 shape/维度分布/数值统计/空值报告

# 待探索的 DataFrame 列表（名称 + 变量）
DF_PAIRS = [
    ("精准排除包 (V8+V7)", df_precise),
    ("API排除包 (撞库)",   df_api),
]

# 关注的分类维度列
CAT_COLS = ["channel", "pkg_type", "month"]

for name, df in DF_PAIRS:
    if df.empty:
        print(f"[SKIP] {name}: 无数据")
        continue
    print(f"\n{'='*50}")
    print(f"{name} — 基础统计")
    print(f"{'='*50}")
    print(f"Shape: {df.shape[0]} 行 x {df.shape[1]} 列")

    # 各分类维度的值分布，快速确认渠道/包类型/月份覆盖是否完整
    for col in CAT_COLS:
        if col in df.columns:
            print(f"\n{col} 分布:")
            print(df[col].value_counts().to_string())

    # 数值指标的描述统计（首登量/申请量/过件率等）
    _num_cols = df.select_dtypes(include="number").columns.tolist()
    if _num_cols:
        print(f"\n数值列统计 ({len(_num_cols)} 列):")
        display(df[_num_cols].describe().round(2))

    # 空值汇总：有空值的列单独列出
    _nulls = df.isna().sum()
    _nulls = _nulls[_nulls > 0]
    print(f"\n空值列: {_nulls.to_string() if not _nulls.empty else '无'}")

print(f"\n[OK] EDA 完成，共检查 {len(DF_PAIRS)} 个 DataFrame")
