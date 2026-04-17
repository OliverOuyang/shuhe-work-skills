# [RUN] 图表注册表 — 连接 notebook 可视化与 HTML 报告
# 输入: 无 (声明式配置，引用已在各 Ch.X.2 cell 中生成的 fig_var 和 data_var)
# 输出: CHART_REGISTRY dict, 打印注册条目数和槽位映射

# 图表注册表：每个 Ch.X.2 / Dim.X.1 产出的图表必须在此注册
# 格式: chart_id → {source_cell, fig_var, data_var, html_slot, caption, chart_type}
CHART_REGISTRY = {}

# 第1章: 精准排除包溢出效果（V8 + V7 月度趋势）
CHART_REGISTRY["ch1_v8_spillover"] = {
    "source_cell": "Ch.1.2",
    "fig_var":     "fig_v8_spillover",
    "data_var":    "df_v8_month",
    "html_slot":   "section_1_chart_a",
    "caption":     "V8精准排除包月度溢出率趋势（抖音渠道）",
    "chart_type":  "line",
}

CHART_REGISTRY["ch1_v7_spillover"] = {
    "source_cell": "Ch.1.3",
    "fig_var":     "fig_v7_spillover",
    "data_var":    "df_v7_month",
    "html_slot":   "section_1_chart_b",
    "caption":     "V7精准排除包月度溢出率趋势（抖音+腾讯）",
    "chart_type":  "line",
}

# --- 若超限，从此处拆为新 cell ---

# 第2章: API排除包撞库命中效果
CHART_REGISTRY["ch2_api_hit_rate"] = {
    "source_cell": "Ch.2.2",
    "fig_var":     "fig_api_hit",
    "data_var":    "df_api_month",
    "html_slot":   "section_2_chart_a",
    "caption":     "API排除包撞库命中率月度趋势",
    "chart_type":  "bar",
}

# 第3章: 排除包对过件率的影响（命中 vs 未命中对比）
CHART_REGISTRY["ch3_pass_rate_compare"] = {
    "source_cell": "Ch.3.2",
    "fig_var":     "fig_pass_compare",
    "data_var":    "df_pass_compare",
    "html_slot":   "section_3_chart_a",
    "caption":     "命中排除包 vs 未命中用户过件率对比",
    "chart_type":  "bar",
}

# 打印注册摘要，方便在 S3 export cell 中核对图表是否齐全
print(f"[OK] 注册 {len(CHART_REGISTRY)} 个图表")
for k, v in CHART_REGISTRY.items():
    print(f"  {k}: {v['source_cell']} → {v['html_slot']} ({v['chart_type']})")
