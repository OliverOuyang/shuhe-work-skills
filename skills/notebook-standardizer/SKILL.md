---
name: notebook-standardizer
description: "Standardize Jupyter notebooks (.ipynb) for interactive data analysis workflows. Enforces a mandatory cell manifest (M1-M8 + archetype chapters) with tags ([CONFIG]/[SETUP]/[FUNC]/[RUN]/[VIZ]/[EXPORT]), structured markdown sections, and output prefixes ([OK]/[WARN]/[SKIP]). Use when the user wants to standardize, clean up, or create a notebook from scratch. Two archetypes: problem-driven (question-answer analysis) and monitoring (dimension-based periodic reporting)."
---

# Notebook Standardizer V3

Transform notebooks into standardized, self-documenting analysis tools following a mandatory cell manifest.

## When to Use

- "Standardize/clean up/format this notebook" or "add comments to notebook"
- Converting ad-hoc analysis into a reusable, shareable notebook
- User mentions "notebook conventions", "cell tags", "notebook formatting"
- Making a notebook easier to debug, re-run, or hand off

---

## Shared Infrastructure Manifest (Both Archetypes)

| Cell | Tag | Name | Content Summary | Skip Condition |
|------|-----|------|-----------------|----------------|
| M1 | markdown | Title Card | `# {Title}` + summary table: type, source, output paths, SQL files, `ARCHETYPE` | Never |
| M2 | [SETUP] | Environment | Imports, paths, clients, `dp.ping()` health check | Never |
| M3 | [CONFIG] | Parameters | All adjustable params with type annotations. `ARCHETYPE = "problem-driven" \| "monitoring"`, `DATA_MODE = "sql" \| "csv"` | Never |
| M4 | [RUN] | Field Validation | `TABLES_TO_VALIDATE` dict + meta loop; print `[OK]`/`[WARN]` per table | `DATA_MODE="csv"` |
| M5 | [RUN] | SQL Transparency | Print full parameterized SQL before execution | No SQL files used |
| M6 | [RUN] | Data Execution | `pipe.run()` or parallel execution + auto CSV save to `data/` | Never |
| M7 | [RUN] | Data Quality Gate | Row count, null ratio, value range, cross-dataset checks; halt on critical issues | Never |
| M8 | [RUN]+[VIZ] | EDA | Per-DataFrame: shape, dtypes, describe, value_counts, null check | Never |

See `templates/` for code patterns for each cell (field_validation.py, sql_transparency.py, etc.).

---

## Problem-Driven Archetype (`ARCHETYPE = "problem-driven"`)

Used when: explicit business questions drive the analysis (e.g., "What is the spillover trend?").

**Example**: 排除包效果回收_By月.ipynb

### Analysis Framework

| Cell | Tag | Name | Content Summary | Skip Condition |
|------|-----|------|-----------------|----------------|
| M9 | markdown | Analysis Framework | Mermaid `flowchart TD`: question nodes, data source nodes, flow edges | Single-question notebook |
| M9.5 | [RUN] | Chart Registry | `CHART_REGISTRY` dict mapping fig_var → html_slot | No HTML report |

### Analysis Chapters (repeat per question, X = chapter number)

| Cell | Tag | Name | Content Summary | Skip Condition |
|------|-----|------|-----------------|----------------|
| Ch.X.0 | markdown | Chapter Header | `## X. {Question}` + one-sentence question + Data + Method | Never |
| Ch.X.1 | [RUN] | Data Preparation | Filter/transform/aggregate; split into sub-cells (Ch.X.1a/1b/1c) if > 25 lines; print shape + preview per sub-cell | Never |
| Ch.X.2 | [VIZ] | Visualization | Charts and/or formatted tables; include chart reading hints | Never |
| Ch.X.3 | [RUN] | Agent Conclusion | Agent interprets viz output, prints structured findings | **CONDITIONAL**: include only when analysis requires explanatory interpretation. Omit for purely descriptive chapters. Validator does NOT flag its absence. |
| Ch.X.4 | [RUN] | Chapter Summary | Consolidate findings: key metrics + trend + recommendation. Reader only needs this cell. | Never |

When Ch.X.3 is omitted, Ch.X.2 connects directly to Ch.X.4.

### Synthesis + Export

| Cell | Tag | Name | Content Summary | Skip Condition |
|------|-----|------|-----------------|----------------|
| S1 | [RUN] | Cross-Chapter Synthesis | Executive summary consolidating all chapter summaries | 1 chapter only |
| S2 | [EXPORT] | CSV Export | Save to `data/` with standard naming (`data_{topic}_{granularity}.csv`) | Never |
| S3 | [EXPORT] | HTML Report | Follow html-report-framework protocol (see S3 Spec below) | Optional |
| S4 | markdown | Appendix | Quick reference, structure map, glossary | Never |

---

## Monitoring Archetype (`ARCHETYPE = "monitoring"`)

Used when: periodic trend reporting or dashboard refresh with no single guiding question.

**Example**: 定向配置分析_By周.ipynb

Note: No M9 (analysis framework) — dimensions are parallel, not sequential.

### Analysis Dimensions (repeat per dimension, X = dimension number)

| Cell | Tag | Name | Content Summary | Skip Condition |
|------|-----|------|-----------------|----------------|
| Dim.X.0 | markdown | Dimension Header | `## X. {Dimension Name}` + one-sentence scope | Never |
| Dim.X.1 | [VIZ] | Visualization + Table | Charts, pivot tables, trend lines for this dimension | Never |
| Dim.X.2 | [RUN] | Brief Takeaway | 2-5 bullets: what changed, what's notable, what needs attention | Never |

### Export (same as problem-driven)

| Cell | Tag | Name | Content Summary | Skip Condition |
|------|-----|------|-----------------|----------------|
| R1 | [RUN] | Chart Registry | `CHART_REGISTRY` dict mapping fig_var → html_slot | No HTML report |
| S2 | [EXPORT] | CSV Export | Save to `data/` with standard naming | Never |
| S3 | [EXPORT] | HTML Report | Follow html-report-framework protocol | Optional |
| S4 | markdown | Appendix | Quick reference | Never |

---

## S3 HTML Report [EXPORT] Cell Specification

S3 generates an HTML report following html-report-framework conventions. It does **NOT** invoke another skill at runtime — the agent applies html-report-framework knowledge at **notebook-build time**.

**Agent steps when building S3:**
1. Read `html-report-framework/SKILL.md` to understand the protocol
2. Read `html-report-framework/resources/starter-template.html`
3. Generate Python code in S3 that reads starter-template, replaces `__PLACEHOLDER__` markers with actual notebook data, adds ECharts configs, writes `report_{topic}_{granularity}.html`

**S3 must NOT:**
- Write raw HTML from scratch (no `<!DOCTYPE html>` literal in cell)
- Import from legacy `generate_report.py` / `generate_config_report.py`
- Call another skill at runtime

See `templates/export_html.py` for the pattern.

---

## 4-Step Workflow

### Step 1: Analyze
Read the target `.ipynb` file and report:
- Cell inventory (code vs markdown count), structural gaps
- Which manifest cells (M1-M8) are present vs missing
- Identify archetype from `ARCHETYPE` value in CONFIG cell (or infer from chapter/dimension markers)

### Step 2: Build
Follow the manifest for the detected archetype. For each cell:
- Read the corresponding template from `templates/` before writing code
- Apply naming conventions from `references/conventions.md`
- Use `_build_notebook.py` pattern (nbformat programmatic build) to avoid JSON encoding issues

### Step 3: Validate
Run the validation script:
```
python <skill-path>/scripts/validate_notebook.py <notebook.ipynb>
```
Fix all errors. Investigate warnings. Do NOT report completion while errors exist.

### Step 4: Execute
Run the full notebook end-to-end. Fix any runtime errors before completion:
```
jupyter nbconvert --to notebook --execute <notebook.ipynb> --output _test_run.ipynb
```
Skip execution only when `DATA_MODE="csv"` path is unavailable. After success, delete `_build_notebook.py` and `_test_run.ipynb`.

---

## Quality Gate

Before reporting completion, verify:

**Manifest completeness:**
- [ ] M1-M8 all present (M4 skipped only if `DATA_MODE="csv"`, M5 only if no SQL files)
- [ ] Correct archetype cells present (Ch.X.0-X.4 for problem-driven; Dim.X.0-X.2 for monitoring)
- [ ] S2, S4 present; S3 present if HTML report is expected

**Cell conventions:**
- [ ] Every code cell starts with a `# [TAG]` line
- [ ] Every logical section has a markdown header with `>` summary line
- [ ] M3 CONFIG params use `# type: description | options` format
- [ ] `print()` uses `[OK]` / `[WARN]` / `[SKIP]` prefixes

**Cell readability:**
- [ ] Every code cell ≤ 25 executable lines (40 hard limit)
- [ ] Every code cell has 3-line docstring header (# [TAG] / # 输入: / # 输出:)
- [ ] Every [RUN] cell ends with print/display of its output
- [ ] Every [VIZ] cell has plt.show + 3-5 line reading takeaway print
- [ ] Comment density ≥ 1:5 in [RUN]/[VIZ] cells

**Chart traceability:**
- [ ] CHART_REGISTRY present (M9.5 or R1) if S3 HTML export exists
- [ ] Every fig_var in CHART_REGISTRY is defined in a [VIZ] cell
- [ ] Every html_slot value is unique across the registry

**Output files:**
- [ ] CSV outputs in `data/` with correct naming (`data_{topic}_{granularity}.csv`)
- [ ] HTML reports have `report_` prefix in project root
- [ ] SQL files are in `sql/` directory; no inline SQL > 20 lines

**Execution:**
- [ ] Validator script: zero errors (warnings acceptable for pre-V2 notebooks)
- [ ] All cells execute without errors end-to-end

---

## References

- Cell tag rules, parameter format, markdown structure, variable naming, anti-patterns: `references/conventions.md`
- Code patterns per manifest cell: `templates/` (field_validation.py, sql_transparency.py, data_execution.py, quality_gate.py, eda.py, chapter_summary.py, dim_takeaway.py, export_html.py, config_block.py, chart_registry.py, cellmap_generator.py)
- HTML report generation: `html-report-framework/SKILL.md` + `html-report-framework/resources/starter-template.html`
