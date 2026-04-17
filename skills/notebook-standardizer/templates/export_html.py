# [EXPORT] HTML 报告生成 — 基于 CHART_REGISTRY 声明式渲染
# 输入: CHART_REGISTRY dict, starter-template.html, START_MONTH/END_MONTH
# 输出: report_排除包效果回收_By月.html, 打印文件大小和图表清单

from pathlib import Path

# 读取 html-report-framework starter template（统一样式基座）
_framework_dir = Path.home() / ".claude/skills/omc-learned/html-report-framework/resources"
_starter = (_framework_dir / "starter-template.html").read_text(encoding="utf-8")

# 报告元信息（来自 CONFIG cell 的全局变量）
_report_title    = "排除包效果回收分析"
_report_subtitle = f"{START_MONTH} ~ {END_MONTH} | By 月"

# 遍历 CHART_REGISTRY，逐图表构建 ECharts JS 配置
_chart_configs_parts = []
for chart_id, spec in CHART_REGISTRY.items():
    # 从全局变量取对应 DataFrame，调用 build_echart_config 生成 JS 字符串
    _data_df = globals()[spec["data_var"]]
    _chart_js = build_echart_config(spec, _data_df)   # 在 [FUNC] cell 中定义
    _chart_configs_parts.append(f'    "{chart_id}": {_chart_js}')

_chart_configs = ",\n".join(_chart_configs_parts)

# --- 若超限，从此处拆为新 cell ---

# 替换 starter template 中的占位符，生成完整 HTML
_html = (_starter
    .replace("__REPORT_TITLE__",    _report_title)
    .replace("__REPORT_SUBTITLE__", _report_subtitle)
    .replace("__CHART_CONFIGS__",   _chart_configs))

# 写入输出文件
_output = os.path.join(PROJECT_DIR, "report_排除包效果回收_By月.html")
Path(_output).write_text(_html, encoding="utf-8")

# 打印生成摘要：文件路径、大小、图表数量
print(f"[OK] HTML 报告已生成: {_output}")
print(f"     文件大小: {Path(_output).stat().st_size / 1024:.1f} KB")
print(f"     图表数: {len(CHART_REGISTRY)}")
for k, v in CHART_REGISTRY.items():
    print(f"     {k}: {v['source_cell']} → {v['html_slot']}")
