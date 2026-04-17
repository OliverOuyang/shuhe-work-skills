# [RUN] 字段验证 — SQL 执行前确认核心表结构
# 输入: Dataphin dp 客户端, 排除包相关表名
# 输出: 每张表的字段校验结果, 打印 [OK]/[WARN]

# 待验证表及其必须存在的字段
TABLES_TO_VALIDATE = {
    # 广告配置宽表：排除包配置字段
    ("pdm_marketing", "pdm_marketing_channel_level_4_ad_config_info_di"): [
        "ds", "channel", "exclude_audience_package", "placement", "region",
    ],
    # 用户归因主表：首登/申请/授信指标
    ("dwt", "dwt_marketing_attribution_user_comprehensive_info_df"): [
        "ds", "channel", "first_login_date", "apply_cnt", "credit_cnt",
    ],
}

# 逐表查询元数据并比对字段列表
_all_ok = True
for (proj, tbl), fields in TABLES_TO_VALIDATE.items():
    try:
        _meta = dp.get_table_meta(tbl, proj)
        _cols = [c.get("name", "") for c in _meta.get("data", {}).get("columns", [])
                 if isinstance(c, dict)]
        _missing = [f for f in fields if f not in _cols]
        if _missing:
            print(f"[WARN] {proj}.{tbl}: 缺失字段 {_missing}")
            _all_ok = False
        else:
            print(f"[OK]   {proj}.{tbl}: {len(fields)} 个字段全部存在")
    except Exception as e:
        print(f"[WARN] {proj}.{tbl}: 元数据查询失败 — {e}")
        _all_ok = False

# 打印汇总结论（Join 逻辑：配置表 LEFT JOIN 归因表 ON channel+ds，包类型由 exclude_audience_package 解析）
print(f"\n{'[OK] 全部验证通过' if _all_ok else '[WARN] 存在问题，请修复后再执行 M5/M6'}")
print("Join: 广告配置表 LEFT JOIN 用户归因表 ON channel+ds | 包类型由 exclude_audience_package 解析")
