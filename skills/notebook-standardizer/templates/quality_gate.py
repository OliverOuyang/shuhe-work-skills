# [RUN] 数据质量检查 — 分析开始前必须通过
# 输入: df_precise (精准排除包), df_api (API排除包)
# 输出: 每个 DataFrame 的质量报告, 打印 [OK]/[WARN]

def quality_check(df, name, expected_cols=None):
    """对 DataFrame 执行行数/字段/空值/负值检查，返回 True 表示通过。"""
    issues = []
    if df.empty:
        print(f"[WARN] {name}: DataFrame 为空")
        return False
    # 检查必须存在的列是否齐全
    if expected_cols:
        missing = set(expected_cols) - set(df.columns)
        if missing:
            issues.append(f"缺失列: {missing}")
    # 检查空值率：超过 50% 视为异常
    for col in df.columns:
        null_pct = df[col].isna().mean()
        if null_pct > 0.5:
            issues.append(f"{col} 空值率 {null_pct:.0%}")
    # 检查数值列是否存在负值（首登量/申请量不应为负）
    for col in df.select_dtypes(include="number").columns:
        if (df[col] < 0).any():
            issues.append(f"{col} 存在负值")
    if issues:
        print(f"[WARN] {name}: {'; '.join(issues)}")
        return False
    print(f"[OK]   {name}: {len(df)} 行, {len(df.columns)} 列, 质量通过")
    return True

# --- 若超限，从此处拆为新 cell ---

# 对排除包两张表依次执行质量检查
_qc_pass = all([
    quality_check(df_precise, "精准排除包",
                  expected_cols=["month", "channel", "pkg_type", "first_login_cnt", "apply_cnt", "credit_cnt"]),
    quality_check(df_api, "API排除包",
                  expected_cols=["month", "channel", "hit_cnt", "apply_cnt", "pass_cnt"]),
])
print(f"\n{'[OK] 数据质量全部通过，可继续分析' if _qc_pass else '[WARN] 存在质量问题，请修复后再执行后续 cell'}")
