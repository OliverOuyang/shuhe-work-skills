# Notebook Conventions — Reference Specification

## 1. Cell Type Tags

Every code cell MUST have a tag comment as its first line.

| Tag | Meaning | When to Use |
|-----|---------|-------------|
| `# [CONFIG]` | User-adjustable parameters | Variable assignments the user should change |
| `# [SETUP]` | Environment initialization | `import`, `sys.path`, connection setup |
| `# [FUNC]` | Function definitions | `def` or `class` definitions |
| `# [RUN]` | Execution logic | Data loading, SQL, preprocessing, algorithms |
| `# [VIZ]` | Visualization | `fig = ...`, `fig.show()`, `plt.show()`, `display()` |
| `# [EXPORT]` | File output | `.to_csv()`, `.to_excel()`, file writing |

If a cell mixes types, use the dominant type.

**Example — CONFIG cell:**
```python
# [CONFIG]
CHANNEL = 'gdt'          # str: 分析渠道 | 'douyin' / 'gdt'
START_DATE = '20260301'  # str: 起始日期，格式 yyyymmdd
SPR_THRESHOLD = 0.10     # float: 安全过件率阈值，范围 0.05~0.20
DATA_MODE = "sql"        # str: "sql"=跑SQL取数 | "csv"=从已有CSV加载
ARCHETYPE = "problem-driven"  # str: "problem-driven" | "monitoring"
```

## 2. Parameter Comment Format

```python
VAR_NAME = value  # type: Chinese description | option1/option2
```

Rules:
- Type annotation first: `str`, `int`, `float`, `bool`, `list[str]`, `dict`
- Chinese description after colon
- Options/range after pipe `|`
- One param per line (no multi-assignment)

## 3. Markdown Cell Structure

### Section Header (Required)

```markdown
## N. Section Title

> One-sentence summary of what this section does and why.

**Input**: `df_raw` (800 rows)
**Output**: `df_combined`, `df_ctrl`
**Adjustable params**: `SPR_THRESHOLD`
```

### Subsection Headers

Use `### N.A Title` for subsections. Use concept tables for domain-specific sections:

```markdown
| Concept | Formula | Meaning |
|---------|---------|---------|
| SPR | t3_safe_adt / t3_ato | Quality rate (higher = better) |
```

## 4. Code Comment Patterns

**Import annotations:**
```python
from data_preprocessing import (
    load_data,           # CSV/Excel loading + column name mapping
    preprocess_data,     # Missing values + type conversion
)
```

**SQL comments** — annotate each CTE, JOIN, and CASE WHEN block.

**VIZ interpretation hints:**
```python
# [VIZ] 12x12 SPR Heatmap
# X axis = V9RN quantile (right = higher score = better)
# Color: green = high SPR, red = low SPR = exclusion candidates
```

**Algorithm comments** — explain business logic, not syntax.

## 5. Output Prefix Convention

All `print()` statements in [RUN]/[SETUP] cells use status prefixes:

```python
print(f'[OK] Data loaded: {len(df)} rows x {len(df.columns)} columns')
print(f'[WARN] Dataphin unavailable: {e}')
print(f'[SKIP] Section not applicable for channel={CHANNEL}')
```

## 6. Variable Naming

| Prefix | Usage | Example |
|--------|-------|---------|
| `df_` | DataFrame | `df_raw`, `df_ctrl`, `df_combined` |
| `_` | Temporary/scratch | `_t`, `_mask`, `_tmp` |
| `fig` | Plotly/matplotlib figure | `fig`, `fig_heatmap` |
| `UPPER_CASE` | Constants/config | `CHANNEL`, `SPR_THRESHOLD` |

Conventions:
- Descriptive over short: `exclude_region` not `er`
- Consistent suffixes: `_cnt` (count), `_pct` (percentage), `_amt` (amount)
- Boolean prefix: `is_`, `has_`, `use_` (e.g., `HAS_DP`, `USE_ONLINE`)

## 7. Notebook Structure Template

```
M1  markdown   Title Card          # {Title} + summary table
M2  [SETUP]    Environment         imports, paths, clients, dp.ping()
M3  [CONFIG]   Parameters          all adjustable params + ARCHETYPE + DATA_MODE
M4  [RUN]      Field Validation    TABLES_TO_VALIDATE dict + meta loop
M5  [RUN]      SQL Transparency    print full parameterized SQL before execution
M6  [RUN]      Data Execution      pipe.run() + auto CSV save
M7  [RUN]      Data Quality Gate   row count, nulls, value range checks
M8  [RUN]+[VIZ] EDA               describe, value_counts, null check

--- Problem-driven archetype ---
M9  markdown   Analysis Framework  Mermaid flowchart TD (questions + data sources)
Ch.X.0  markdown  Chapter Header   ## X. {Question} + Data + Method
Ch.X.1  [RUN]     Data Preparation filter/transform/aggregate, print shape
Ch.X.2  [VIZ]     Visualization    charts + reading hints
Ch.X.3  [RUN]     Agent Conclusion CONDITIONAL — omit for descriptive chapters
Ch.X.4  [RUN]     Chapter Summary  key metrics + trend + recommendation

--- Monitoring archetype ---
Dim.X.0  markdown  Dimension Header  ## X. {Dimension} + scope
Dim.X.1  [VIZ]     Visualization + Table  charts, pivot tables, trend lines
Dim.X.2  [RUN]     Brief Takeaway    2-5 bullets: what changed, what's notable

--- Shared closing ---
S1  [RUN]     Cross-Chapter Synthesis  executive summary (skip if 1 chapter)
S2  [EXPORT]  CSV Export               save to data/ with standard naming
S3  [EXPORT]  HTML Report              html-report-framework protocol (optional)
S4  markdown  Appendix                 quick reference, structure map, glossary
```

## 8. Appendix Section Template

```markdown
---

## Appendix

### A. Quick Parameter Reference

| Parameter | Location | Default | Range |
|-----------|----------|---------|-------|
| CHANNEL | Section 2 | 'gdt' | 'douyin' / 'gdt' |
| SPR_THRESHOLD | Section 2 | 0.10 | 0.05~0.20 |

### B. Common Operations

- **Switch channel**: Change `CHANNEL` in Section 2, re-run from Section 3
- **Adjust threshold**: Change `SPR_THRESHOLD`, re-run from Section 6

### C. Glossary

| Term | Formula | Meaning |
|------|---------|---------|
| SPR | t3_safe_adt / t3_ato | Safe approval rate |
```

## 9. Code Templates

See `templates/` directory for copy-paste-ready code patterns for each manifest cell:

| Template File | Manifest Cell | Content |
|---------------|---------------|---------|
| `config_block.py` | M3 | CONFIG cell with ARCHETYPE + DATA_MODE |
| `field_validation.py` | M4 | TABLES_TO_VALIDATE dict + meta loop |
| `sql_transparency.py` | M5 | print full parameterized SQL |
| `data_execution.py` | M6 | pipe.run() + parallel + CSV save |
| `quality_gate.py` | M7 | quality check function |
| `eda.py` | M8 | EDA pattern |
| `chapter_summary.py` | Ch.X.4 | chapter summary format |
| `dim_takeaway.py` | Dim.X.2 | monitoring takeaway format |
| `export_html.py` | S3 | html-report-framework protocol |
| `chart_registry.py` | M9.5 | CHART_REGISTRY dict + print |
| `cellmap_generator.py` | Build util | cellmap.md sidecar generation |

## 10. File Naming & Folder Convention

### Folder Structure

```
project_dir/
  sql/              — SQL source files (read-only, version-controlled)
  data/             — All CSV outputs (auto-saved + final exports)
  *.ipynb           — Notebooks (project root)
  report_*.html     — HTML reports (project root)
```

Rules:
- SQL files > 20 lines MUST be in `sql/`, not inline in notebook cells
- All CSV output MUST go to `data/`, never project root
- `data/` and `sql/` created by [SETUP] cell via `os.makedirs(exist_ok=True)`

### File Naming Patterns

| Type | Pattern | Example |
|------|---------|---------|
| SQL source | `{业务描述}.sql` | `精准排除包.sql` |
| Query CSV (timestamped) | `{业务描述}_{YYYYMMDD_HHMM}.csv` | `精准排除包_20260414_1530.csv` |
| Export CSV (final) | `data_{业务描述}_{粒度}.csv` | `data_精准排除包_月度回收.csv` |
| HTML report | `report_{主题}_{粒度}.html` | `report_排除包效果回收_By月.html` |
| Notebook | `{分析主题}_{粒度}.ipynb` | `排除包效果回收_By月.ipynb` |

Output path config pattern (always use `os.path.join`, no hardcoded absolute paths):
```python
OUTPUT_HTML   = os.path.join(PROJECT_DIR, "report_排除包效果回收_By月.html")
OUTPUT_CSV_JZ = os.path.join(DATA_DIR, "data_精准排除包_月度回收.csv")
```

### Anti-patterns

```python
# BAD: hardcoded absolute path
df.to_csv(r"C:\Users\Oliver\Desktop\...\output.csv")
# BAD: saving CSV to project root
df.to_csv("result.csv")
# BAD: no timestamp on auto-saved files (overwrites previous)
df.to_csv(os.path.join(DATA_DIR, "精准排除包.csv"))

# GOOD: timestamp auto-save + explicit final export
_ts = _dt.now().strftime("%Y%m%d_%H%M")
df.to_csv(os.path.join(DATA_DIR, f"精准排除包_{_ts}.csv"))     # accumulate
df.to_csv(os.path.join(DATA_DIR, "data_精准排除包_月度回收.csv"))  # final
```

## 11. Build via Python Script

For reliability, generate notebooks programmatically using nbformat to avoid JSON encoding issues with Chinese characters and complex code strings:

```python
import nbformat
nb = nbformat.v4.new_notebook()
cells = []
def md(src): cells.append(nbformat.v4.new_markdown_cell(src))
def code(src): cells.append(nbformat.v4.new_code_cell(src))
# ... build cells ...
nb.cells = cells
nbformat.write(nb, 'output.ipynb')
```

See `templates/` for cell-level patterns. Delete `_build_notebook.py` after successful validation.

## 12. Logic Review Checklist

Run after end-to-end execution succeeds.

| Category | Check |
|----------|-------|
| Variable flow | Every variable used is defined in a prior cell |
| DataFrame shape | merge/concat don't produce unexpected row duplication |
| Aggregation | GROUP BY matches intended granularity |
| JOIN keys | Same hash/encoding on both sides |
| Filter conditions | Date ranges match CONFIG parameters |
| Business rules | CASE WHEN matches documented logic |
| Metrics | Numerator/denominator correct, no div-by-zero |
| Edge cases | Empty df guards (`if df.empty`), NaN handling |

Use Agent review when: complex business rules, cross-project SQL, first-time notebook creation.

## 13. End-to-End Verification

After building or modifying a notebook, verify with:
```bash
jupyter nbconvert --to notebook --execute notebook.ipynb --output _test_run.ipynb
```

Checks:
- No cell raised an exception
- All `[OK]` messages printed, no unexpected `[WARN]`
- DataFrames are non-empty where expected
- Output files exist and have reasonable size

See `templates/` for assertion patterns. Remove `_test_run.ipynb` after verification.

## 14. Cell 粒度规则

- 单个 `[RUN]`/`[VIZ]` cell 可执行代码行（排除 `#` 注释行和空行）≤ 25 行 → validator warning；> 40 行 → validator error
- 超限时拆为子 cell，命名格式：`Ch.X.1a` / `Ch.X.1b` / `Ch.X.1c`（或 `Dim.X.1a`）
- 拆分原则：每个子 cell 承担一个职责（筛选 / 聚合 / 透视 / 可视化）
- 子 cell 之间保持独立：各有自己的 docstring header 和尾部输出

示例（Ch.2.1 超限时拆分）：
```
Ch.2.1a [RUN] 筛选抖音排除包数据        → ~12 行
Ch.2.1b [RUN] 按月聚合消耗量            → ~15 行
Ch.2.1c [RUN] 透视为渠道×月份矩阵       → ~10 行
```

## 15. Cell 头部 Docstring 三件套

每个 code cell 前 3 行（非空行）固定格式：
```python
# [TAG] 短标题（≤20字中文）
# 输入: df_xxx (行数/形状描述)
# 输出: df_yyy (行数/形状描述), 打印 xxx
```

规则：
- `[CONFIG]` / `[SETUP]` cell 可省略输入/输出行，但第1行标题必须有
- Validator 检查：前 3 行匹配 `# \[TAG\]` / `# 输入:` / `# 输出:`

具体例子：
```python
# [RUN] Ch.2.1b 按月聚合排除包消耗
# 输入: df_raw (150,000 行明细数据)
# 输出: df_month (12 行 月×渠道 聚合), 打印 head(3)
```

## 16. 输出契约

- 每个 `[RUN]` cell 结尾**必须**有 `print()` 或 `display()` 展示本 cell 产出物
  - DataFrame 示例: `print(f"[OK] df_month: {df_month.shape}"); display(df_month.head(3))`
  - 标量/字典: `print(f"[OK] 计算完成: metric = {value}")`
- 每个 `[VIZ]` cell 除 `plt.show()` / `fig.show()` 外，必须**额外**打印 3-5 行读图事实

```python
plt.show()
print("读图要点:")
print("  1. 抖音排除包消耗量3月起下降，环比-15%")
print("  2. 腾讯排除包消耗量保持稳定，月均2.3万")
print("  3. 其他渠道占比可忽略 (<5%)")
```

- `[CONFIG]` / `[SETUP]` / `[EXPORT]` cell 豁免

## 17. 注释密度规则

- `[RUN]` / `[VIZ]` cell 中，中文注释行 : 可执行代码行 ≥ 1:5 → OK；< 1:5 → warn；< 1:8 → error
- "中文注释行"定义：以 `#` 开头且包含至少一个中文字符 (`[\u4e00-\u9fff]`) 的行
- 每 5-8 行代码前至少一句中文注释说明"这段在做什么"
- `[CONFIG]` / `[SETUP]` / `[EXPORT]` cell 豁免（它们的 parameter comment 已足够）

## 18. CHART_REGISTRY（图表注册表）

用于打通 notebook 可视化 → HTML 报告的链路：
- 问题驱动型 notebook 在 M9 后新增 **M9.5** cell，统一定义所有图表注册信息
- 监控型 notebook 在 S1 前新增 **R1** 注册 cell
- 每个 Ch.X.2 / Dim.X.1 产生的图必须有对应 CHART_REGISTRY 条目
- S3 (HTML Export) 遍历 CHART_REGISTRY 注入 starter-template，不硬编码

Schema 示例：
```python
# [RUN] 图表注册表 — 连接 notebook 图表与 HTML 报告
# 输入: 无
# 输出: CHART_REGISTRY dict, 打印注册条目数

CHART_REGISTRY = {}

CHART_REGISTRY["ch2_spillover_trend"] = {
    "source_cell": "Ch.2.2",          # 产生该图的 cell
    "fig_var": "fig_spillover",        # 图变量名
    "data_var": "df_spillover_month",  # 数据源 DataFrame
    "html_slot": "section_2_chart_a",  # HTML 报告中的坑位 ID
    "caption": "抖音排除包溢出率3月起下降10pp",
    "chart_type": "line",              # ECharts 类型: line|bar|heatmap|pie|scatter
}

print(f"[OK] 注册 {len(CHART_REGISTRY)} 个图表")
for k, v in CHART_REGISTRY.items():
    print(f"  {k}: {v['source_cell']} → {v['html_slot']}")
```

## 19. cellmap.md 侧车导航

构建完成后自动生成 `{notebook_stem}.cellmap.md`，用于 Claude 修改 notebook 前快速定位目标 cell（避免扫描整个 .ipynb JSON）。

格式：
```markdown
| Cell Idx | Tag | Name | Produces | Used By |
|----------|-----|------|----------|---------|
| 0 | md | M1 Title Card | — | — |
| 1 | [SETUP] | M2 Environment | dp, pipe | M4-M6 |
| 14 | [VIZ] | Ch.2.2 溢出趋势图 | fig_spillover | S3:section_2_chart_a |
```

Build script (`_build_notebook.py`) 结尾自动调用 `cellmap_generator.py` 生成此文件。
