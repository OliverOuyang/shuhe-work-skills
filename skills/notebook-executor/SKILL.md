---
name: notebook-executor
description: Execute Jupyter notebooks end-to-end with SQL pre-validation, error diagnosis, and auto-fix loops. Use when "run notebook", "execute notebook", "test notebook", or "validate notebook execution".
---

# Notebook Executor

A 3-phase pipeline: **Validate SQL -> Execute Notebook -> Diagnose & Fix Errors**.

Does NOT overlap with:
- `sql-runner` (submits individual SQL queries to Dataphin)
- `notebook-standardizer` (restructures/formats notebooks, not executes them)

## When to Use This Skill

- "Run this notebook" or "execute notebook end-to-end"
- "Test if this notebook works" or "validate notebook execution"
- "Fix notebook errors and re-run"
- User wants to verify a notebook produces correct output after changes

## Arguments

```
/notebook-executor path/to/notebook.ipynb [--skip-sql-check] [--timeout=900] [--max-retries=3]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `notebook_path` | (required) | Path to the `.ipynb` file |
| `--skip-sql-check` | false | Skip Phase 1 SQL pre-validation |
| `--timeout` | 900 | Execution timeout in seconds (SQL queries can take 5+ min) |
| `--max-retries` | 3 | Maximum fix-and-retry iterations |

---

## Phase 1: Pre-flight SQL Validation

Before running the notebook, validate SQL files it depends on.

### Step 1: Find SQL Dependencies

Scan notebook code cells for ALL SQL reference patterns. Real notebooks use many styles:

```python
import nbformat, re, ast

nb = nbformat.read(notebook_path, as_version=4)
sql_files = []
for cell in nb.cells:
    if cell.cell_type == 'code':
        src = cell.source
        # Pattern 1: load_sql_file(..., "path.sql") or pipe.run_file(..., "path.sql", ...)
        # Greedy scan past os.path.join() and other intermediate arguments
        sql_files += re.findall(r'(?:load_sql_file|run_file)\s*\([^)]*["\']([^"\']+\.sql)["\']', src)
        # Pattern 2: os.path.join(SQL_DIR, "name.sql") — extract the .sql filename
        sql_files += re.findall(r'os\.path\.join\s*\([^)]*["\']([^"\']+\.sql)["\']', src)
        # Pattern 3: Variable dict/list building — {"label": ("filename.sql", ...)}
        sql_files += re.findall(r'["\']([^"\']+\.sql)["\']', src)
        # Pattern 4: pipe.run_files_parallel([...]) — list of (path, params) tuples
        if 'run_files_parallel' in src:
            sql_files += re.findall(r'["\']([^"\']*\.sql)["\']', src)

# Deduplicate while preserving order
sql_files = list(dict.fromkeys(sql_files))
```

### Step 1b: Resolve Dynamic SQL Paths

The regex patterns above catch static string literals. Real notebooks also use dynamic patterns that need manual resolution:

- **f-string templates**: `f"{_dname}.sql"` in a `for _dname in ["name1", "name2"]` loop — trace the loop variable to get actual filenames
- **Dict/tuple references**: `_fname` from `{"label": ("filename.sql", params)}` — extract the `.sql` values from the data structure
- **Variable path arguments**: `pipe.run_file(os.path.join(SQL_DIR, _fname), ...)` where `_fname` is a variable — trace back to its string literal assignment

If regex finds `{variable}.sql` patterns or `pipe.run_file(variable)` calls, trace the variable assignment in the same cell to resolve actual filenames.

**Fallback**: If no `.sql` literals are found but the notebook references `SQL_DIR`, check the `sql/` directory for all `.sql` files and cross-reference with the notebook's import/execution patterns.

### Step 2: Validate Table/Field Existence

For each SQL file:

1. Parse table names from `FROM` / `JOIN` clauses
2. Use `mcp__sh_dp_mcp__get_dp_table_meta` to verify tables exist and fields are correct
3. Flag any `SELECT *` (should be explicit columns)

### Step 3: Dry-run SQL (Optional)

Submit each SQL with `LIMIT 10` appended via `mcp__sh_dp_mcp__submit_dp_query` to verify syntax without fetching full data.

### Step 4: Report

Print `[OK]` / `[WARN]` per SQL file. Example:

```
[Phase 1] SQL Pre-validation
  [OK] 定向配置分析_By月.sql -- 24 columns verified
  [OK] 定向配置_排除包明细.sql -- 6 columns verified
  [WARN] 定向配置_地域明细.sql -- field 'xxx' not found
```

---

## Phase 2: Execute Notebook

Run the notebook and capture results.

### Pre-flight: Clean Up Stale Output

Before executing, check for and remove any stale `_test_run.ipynb` from a previous run:

```bash
# _test_run.ipynb is written NEXT TO the input notebook (--output is relative to input dir)
TEST_OUTPUT="{notebook_dir}/_test_run.ipynb"
if [ -f "$TEST_OUTPUT" ]; then
  rm -f "$TEST_OUTPUT" 2>/dev/null || echo "[WARN] Cannot delete stale _test_run.ipynb — Jupyter kernel may have it locked. Ask user to close it."
fi
```

### Execution Command

```bash
jupyter nbconvert --to notebook --execute "{notebook_path}" \
  --output "_test_run.ipynb" \
  --ExecutePreprocessor.timeout={timeout}
```

**Path note**: `--output "_test_run.ipynb"` writes the file **relative to the input notebook's directory**, not the CWD. So if the notebook is at `C:/project/analysis.ipynb`, the output is `C:/project/_test_run.ipynb`.

Default timeout: 900 seconds (SQL queries can take 5+ minutes).

### Verify Execution Success

Check both the exit code AND the output file existence:

```python
import os
test_output = os.path.join(os.path.dirname(notebook_path), "_test_run.ipynb")

# Exit code 0 but no output file = silent failure
if not os.path.exists(test_output):
    print("[FAIL] jupyter nbconvert exited but produced no output file")
    # Check if notebook has a kernel spec issue or empty cell list
```

**Windows note**: `CreateFile() Error: 5` in terminal output is a Windows terminal artifact, NOT a real error. Ignore it.

### Error Extraction

After execution, inspect the output notebook for errors:

```python
import nbformat

# Read from the CORRECT path (next to input notebook, not CWD)
test_output = os.path.join(os.path.dirname(notebook_path), "_test_run.ipynb")
nb = nbformat.read(test_output, as_version=4)
errors = []
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code' and cell.get('outputs'):
        for out in cell.outputs:
            if out.get('output_type') == 'error':
                errors.append((i, cell.get('id', ''), out['ename'], out['evalue']))
```

If no errors: report `[OK] All N cells passed`, clean up `_test_run.ipynb`, done.

If errors found: proceed to Phase 3.

---

## Phase 3: Diagnose & Auto-Fix

When errors are found, match against known patterns and apply targeted fixes.

### Error Pattern Catalog

| Pattern | Root Cause | Auto-Fix |
|---------|-----------|----------|
| `TypeError: Cannot use method 'nlargest' with dtype object` | Dataphin returns all columns as string. DataFrame numeric columns need conversion. | Add `pd.to_numeric(df[col], errors='coerce')` before the failing operation |
| `KeyError: '{column_name}'` | Column was renamed/removed in SQL refactoring but notebook cell still references old name. | Search notebook for the missing column, identify correct replacement from DataFrame columns |
| `ODPS-0420061: data is larger than rendering limitation` | SQL returns too much data (usually ARRAY fields expanded). | Rewrite SQL to use `SIZE()` scalar categories instead of raw ARRAY fields, or add LIMIT, or split into sub-queries |
| `ODPS-0130071` | CASE expressions used directly in GROUP BY (ODPS doesn't support this). | Wrap in CTE: pre-compute CASE in WITH clause, GROUP BY column aliases |
| `NameError: name 'xxx' is not defined` | Cell execution order issue, or variable defined in a cell that was skipped/failed. | Check if variable is defined in a prior cell that may have errored |
| `ModuleNotFoundError` | Missing Python package. | `pip install {package}` then retry |
| `ValueError: No objects to concatenate` | Empty DataFrame from a query that returned no data. | Add empty DataFrame guard: `if df.empty: print("[SKIP]"); return` |
| `AttributeError: 'NoneType' has no attribute` | Query returned None instead of DataFrame (timeout or error). | Add null check before operations |
| `CreateFile() Error: 5` | Windows terminal artifact from Python subprocess. | **Not a real error** — ignore it. Check actual cell outputs for real errors |
| Exit code 0 but no `_test_run.ipynb` | Kernel spec missing, empty notebook, or silent crash. | Check `jupyter kernelspec list`, verify notebook has code cells |
| `ODPS-*` SQL timeout / empty result | `ds` partition wrapped in functions (CONCAT/SUBSTR) preventing partition pruning. | Rewrite WHERE clause to compare `ds` directly: `ds >= '20260101'` |
| `run_files_parallel` failures | Multiple SQL files executed in parallel; one failure can mask others. | Check each SQL result individually, report all failures not just the first |

### Fix Application Strategy

1. **Backup first** (once, before any edits): Copy the original notebook to `{notebook_name}.backup.ipynb`. Never overwrite the backup.
2. Read the failing cell source from the **original notebook** via nbformat (NOT from `_test_run.ipynb` — the test output may have corrupted metadata)
3. Apply targeted fix (smallest change possible) to the **original notebook**
4. Write the edited notebook back via `nbformat.write(nb, original_path)`
5. Delete stale `_test_run.ipynb` before re-running (avoid Jupyter lock conflicts)
6. Re-run the notebook (loop back to Phase 2)
7. Maximum 3 fix iterations — if still failing after 3, report to user with full diagnosis and restore from backup if edits made things worse

---

## Workflow Summary

```
1. Parse arguments
2. Phase 1: SQL pre-validation (skip if --skip-sql-check)
3. Phase 2: Execute notebook
4. If success -> report [OK] -> clean up _test_run.ipynb -> done
5. If errors -> Phase 3: diagnose, apply fix, increment retry counter
6. Loop to Phase 2 (max retries)
7. If still failing -> report errors with diagnosis to user
```

---

## Output Format

```
=== Notebook Executor ===
Target: 定向配置分析_By月.ipynb

[Phase 1] SQL Pre-validation
  [OK] 定向配置分析_By月.sql -- 24 columns verified
  [OK] 定向配置_排除包明细.sql -- 6 columns verified
  [WARN] 定向配置_地域明细.sql -- field 'xxx' not found

[Phase 2] Execution (attempt 1/3)
  [RUN] jupyter nbconvert --execute ...
  [FAIL] Cell 21 (id=82aace27): TypeError: Cannot use method 'nlargest' with dtype object

[Phase 3] Auto-Fix
  [FIX] Added pd.to_numeric() conversion for 'plan_cnt' column
  [WRITE] Updated cell 15 via nbformat

[Phase 2] Execution (attempt 2/3)
  [RUN] jupyter nbconvert --execute ...
  [OK] All 38 cells passed

[Cleanup] Removed _test_run.ipynb
```

---

## Relationship with Other Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `notebook-executor` (this) | **Run** a notebook end-to-end, diagnose runtime errors, auto-fix and retry | "Run this notebook", "Test if it works", "Fix errors and re-run" |
| `notebook-standardizer` | **Restructure** a notebook to follow cell manifest conventions | "Standardize this notebook", "Add proper cell tags" |
| `sql-runner` | Submit a **single SQL query** to Dataphin | "Run this SQL", "Check this query" |

**Key distinction**: `notebook-standardizer` Step 4 also runs `jupyter nbconvert --execute`, but only as a final validation after restructuring. If execution fails there, hand off to `notebook-executor` for diagnosis. The two skills are complementary, not competing.

## Important Notes

### Windows Path Handling

Use forward slashes in bash commands. Handle Chinese filenames with UTF-8 encoding. Example:

```bash
# Correct
jupyter nbconvert --execute "C:/Users/Oliver/Desktop/排除包效果回收_By月.ipynb"
# Incorrect (backslashes cause issues in bash)
jupyter nbconvert --execute "C:\Users\Oliver\Desktop\排除包效果回收_By月.ipynb"
```

### Jupyter Kernel Lock

`_test_run.ipynb` may be locked if Jupyter is running the same notebook in a browser session. Warn user to close the notebook in Jupyter before execution.

### DATA_MODE Toggle

Many notebooks have a `DATA_MODE = "sql" | "csv"` toggle in their CONFIG cell. If SQL validation fails and CSV data files exist, suggest switching to `DATA_MODE = "csv"` as a fallback.

### Timeout Guidance

SQL queries via QueryPipeline can take 2-5 minutes each. A notebook with multiple queries needs generous timeout. Default 900s is appropriate for most cases. For notebooks with 5+ SQL queries, consider `--timeout=1800`.

### Cleanup

Always try to delete `_test_run.ipynb` after a successful run. If deletion fails (file locked), warn user but do not treat as an error.

### nbformat Usage

Always use `nbformat.read(path, as_version=4)` and `nbformat.write(nb, path)` for reading and editing notebooks. Never edit `.ipynb` JSON directly -- the JSON structure is fragile and easy to corrupt.

### Partition Pruning (ds Field)

When validating or fixing SQL, remember: the `ds` partition field must be compared directly (`ds >= '20260101'`). Never wrap `ds` in functions like `CONCAT()` or `SUBSTR()` -- this prevents partition pruning and causes queries to timeout or return empty results.

### ARRAY Field Types

Tables like `pdm_marketing_channel_level_4_ad_config_info_di` have ARRAY-typed fields (`region`, `placement`, `exclude_audience_package`). If a query expands these with EXPLODE and hits the ODPS rendering limit, rewrite to use `SIZE()` for categorization instead.
