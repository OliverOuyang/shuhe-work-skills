"""Validate a Jupyter notebook against the V2 Mandatory Cell Manifest.

Usage:
    python validate_notebook.py <notebook.ipynb>

Exit codes: 0=all pass, 1=errors exist, 2=warnings only

Checks 1-4 (preserved): nbformat, syntax, tag coverage, markdown ratio >= 25%
Checks 5-9 (new): M-sequence, M5 before M6, M8 after M6, archetype, chapter completeness
Checks 10-15 (readability): cell length, docstring header, output contract,
    comment density, chart registry consistency, html_slot uniqueness
"""

import sys, ast, json, re

VALID_TAGS = {'CONFIG', 'SETUP', 'FUNC', 'RUN', 'VIZ', 'EXPORT'}
TAG_RE = re.compile(r'^#\s*\[(' + '|'.join(VALID_TAGS) + r')\]')
ARCHETYPE_RE = re.compile(r'ARCHETYPE\s*=\s*["\'](\w[\w-]*)["\']')
SQL_REF_RE = re.compile(r'\.sql["\'\s]|load_sql_file|sql_file', re.I)
CH_RE = re.compile(r'Ch\.(\d+)\.(\d+)', re.I)
DIM_RE = re.compile(r'Dim\.(\d+)\.(\d+)', re.I)

# Readability check patterns (checks 10-15)
CHINESE_RE = re.compile(r'[\u4e00-\u9fff]')
CHART_REG_KEY_RE = re.compile(r'CHART_REGISTRY\[(["\'])(.+?)\1\]')
FIG_VAR_RE = re.compile(r'"fig_var"\s*:\s*["\'](\w+)["\']')
HTML_SLOT_RE = re.compile(r'"html_slot"\s*:\s*["\'](\w+)["\']')
OUTPUT_RE = re.compile(r'\b(?:print|display)\s*\(')
SHOW_RE = re.compile(r'(?:plt|fig)\.show\(\)|\.show\(\)')

# M-cell detection: (cell_type_filter, pattern)
M_DETECT = {
    'M1': ('markdown', re.compile(r'^#\s+\S')),
    'M2': ('code', re.compile(r'\[SETUP\]')),
    'M3': ('code', re.compile(r'\[CONFIG\]')),
    'M4': ('code', re.compile(r'TABLES_TO_VALIDATE|Field.Validation', re.I)),
    'M5': ('code', re.compile(r'SQL.Transparency|print.*sql', re.I)),
    'M6': ('code', re.compile(r'pipe\.run|Data.Execution|\.run\(sql', re.I)),
    'M7': ('code', re.compile(r'Quality.Gate|quality_gate', re.I)),
    'M8': ('code', re.compile(r'value_counts|\.describe\(\)|EDA', re.I)),
}

warnings_list = []
errors_list = []

def w(msg): warnings_list.append(msg); print(f'[WARN] {msg}')
def ok(msg): print(f'[OK]   {msg}')
def err(msg): errors_list.append(msg); print(f'[ERROR] {msg}')


def load_cells(path):
    try:
        import nbformat
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        ok('nbformat valid')
        return nb.cells
    except ImportError:
        w('nbformat not installed — format validation skipped')
    except Exception as e:
        err(f'nbformat validation failed: {e}')
    with open(path, encoding='utf-8') as f:
        nb_dict = json.load(f)
    class C:
        def __init__(self, d):
            self.cell_type = d.get('cell_type', 'code')
            s = d.get('source', '')
            self.source = ''.join(s) if isinstance(s, list) else s
    return [C(d) for d in nb_dict.get('cells', [])]


def check_syntax(cells):
    code = [c for c in cells if c.cell_type == 'code']
    bad = []
    for i, c in enumerate(cells):
        if c.cell_type != 'code' or c.source.strip().startswith('%%'):
            continue
        try:
            ast.parse(c.source)
        except SyntaxError as e:
            bad.append(f'cell {i}: {e}')
    if bad:
        [err(b) for b in bad]
    else:
        ok(f'{len(code)}/{len(code)} code cells pass syntax check')


def check_tags(cells):
    untagged = []
    counts = {}
    for i, c in enumerate(cells):
        if c.cell_type != 'code' or not c.source.strip():
            continue
        m = TAG_RE.match(c.source.strip().split('\n')[0])
        if m:
            counts[m.group(1)] = counts.get(m.group(1), 0) + 1
        else:
            untagged.append(i)
    if untagged:
        w(f'{len(untagged)} code cells without tags: indices {untagged}')
    else:
        ok(f'All non-empty code cells tagged — {dict(sorted(counts.items()))}')


def check_md_ratio(cells):
    total = len(cells)
    md = sum(1 for c in cells if c.cell_type == 'markdown')
    ratio = md / total * 100 if total else 0
    msg = f'Markdown ratio: {ratio:.0f}% ({md}/{total}, target >= 25%)'
    ok(msg) if ratio >= 25 else w(msg)


def find_m_cells(cells):
    found = {k: [] for k in M_DETECT}
    for i, c in enumerate(cells):
        for label, (ctype, pat) in M_DETECT.items():
            if ctype == 'markdown' and c.cell_type == 'markdown':
                if pat.search(c.source.split('\n')[0] if c.source else ''):
                    found[label].append(i)
            elif ctype == 'code' and c.cell_type == 'code' and pat.search(c.source):
                found[label].append(i)
    return found


def check_m_sequence(found):
    present = {k: v[0] for k, v in found.items() if v}
    missing = [k for k in ['M1','M2','M3','M4','M5','M6','M7','M8'] if k not in present]
    if missing:
        w(f'M-sequence: {len(present)}/8 cells found — missing {missing}')
    # Check order
    ordered = sorted(present.items(), key=lambda x: x[0])
    for j in range(len(ordered) - 1):
        a_lbl, a_idx = ordered[j]
        b_lbl, b_idx = ordered[j+1]
        if a_idx > b_idx:
            w(f'M-sequence order: {a_lbl}(cell {a_idx}) appears after {b_lbl}(cell {b_idx})')
    if not missing and all(ordered[j][1] < ordered[j+1][1] for j in range(len(ordered)-1)):
        ok(f'M-sequence: {" ".join(k for k,_ in ordered)} (8/8 in order)')


def check_m5_m6(cells, found):
    m6 = found.get('M6', [])
    m5 = found.get('M5', [])
    if not m6:
        ok('M5/M6: no M6 found (skipped)'); return
    has_sql = any(SQL_REF_RE.search(cells[i].source) for i in m6)
    if not has_sql:
        ok('M5: M6 has no .sql references — M5 not required'); return
    if not m5:
        w('M5 missing: M6 references .sql files but M5 (SQL Transparency) not found'); return
    m5f, m6f = min(m5), min(m6)
    ok(f'M5(cell {m5f}) before M6(cell {m6f})') if m5f < m6f else w(f'M5(cell {m5f}) must precede M6(cell {m6f})')


def check_m8_m6(found):
    m6, m8 = found.get('M6', []), found.get('M8', [])
    if not m6:
        ok('M8: no M6 found (skipped)'); return
    if not m8:
        w('M8 (EDA) not found after M6 (data execution)'); return
    m6f, m8f = min(m6), min(m8)
    ok(f'M8(cell {m8f}) after M6(cell {m6f})') if m8f > m6f else w(f'M8(cell {m8f}) must follow M6(cell {m6f})')


def detect_archetype(cells):
    for c in cells:
        if c.cell_type == 'code' and '[CONFIG]' in c.source:
            m = ARCHETYPE_RE.search(c.source)
            if m:
                arch = m.group(1).lower()
                ok(f'Archetype: {arch} (explicit in CONFIG)')
                return arch
    has_ch = any(CH_RE.search(c.source) for c in cells)
    has_dim = any(DIM_RE.search(c.source) for c in cells)
    if has_ch and not has_dim:
        w('Archetype: inferred "problem-driven" (no ARCHETYPE in CONFIG)')
        return 'problem-driven'
    if has_dim and not has_ch:
        w('Archetype: inferred "monitoring" (no ARCHETYPE in CONFIG)')
        return 'monitoring'
    w('Archetype: unknown — no ARCHETYPE in CONFIG, no Ch/Dim markers')
    return None


def check_chapters(cells, archetype):
    if archetype is None:
        w('Chapter completeness: skipped (unknown archetype)'); return
    groups = {}
    pat = CH_RE if archetype == 'problem-driven' else DIM_RE
    label = 'Ch' if archetype == 'problem-driven' else 'Dim'
    required_subs = ['1', '2', '4'] if archetype == 'problem-driven' else ['1', '2']
    for c in cells:
        for m in pat.finditer(c.source):
            num, sub = m.group(1), m.group(2)
            groups.setdefault(num, set()).add(sub)
    if not groups:
        w(f'Check 9 ({archetype}): no {label}.X.Y markers found'); return
    for num in sorted(groups, key=int):
        subs = groups[num]
        missing = [s for s in required_subs if s not in subs]
        present_str = '+'.join(f'{label}.{num}.{s}' for s in sorted(subs, key=int))
        if missing:
            w(f'{label}.{num}: {present_str} — missing {[f"{label}.{num}.{s}" for s in missing]}')
        else:
            ok(f'{label}.{num}: {present_str} — required cells present')


def _get_tag(cell):
    """Extract the tag from the first non-blank line of a code cell, or None."""
    if cell.cell_type != 'code':
        return None
    for line in cell.source.splitlines():
        if line.strip():
            m = TAG_RE.match(line.strip())
            return m.group(1) if m else None
    return None


def check_cell_length(cells):
    """Check 10: Enforce per-cell executable line limits.

    Executable lines = non-blank lines that don't start with '#'.
    <= 25 lines: OK
    26-40 lines: WARN
    > 40 lines: ERROR
    Prints a summary of pass/warn/error counts.
    """
    n_pass = n_warn = n_error = 0
    for i, c in enumerate(cells):
        if c.cell_type != 'code' or not c.source.strip():
            continue
        lines = c.source.splitlines()
        exec_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        count = len(exec_lines)
        if count <= 25:
            n_pass += 1
        elif count <= 40:
            w(f'Check 10: cell {i} has {count} executable lines (26-40, target <= 25)')
            n_warn += 1
        else:
            err(f'Check 10: cell {i} has {count} executable lines (> 40, must split)')
            n_error += 1
    total = n_pass + n_warn + n_error
    ok(f'Check 10 cell length: {n_pass}/{total} pass, {n_warn} warn, {n_error} error')


def check_docstring_header(cells):
    """Check 11: Enforce 3-line docstring header in code cells.

    Line 1: # [TAG] — required for all non-empty code cells
    Line 2: # 输入: — required for RUN/VIZ/FUNC/EXPORT
    Line 3: # 输出: — required for RUN/VIZ/FUNC/EXPORT
    CONFIG/SETUP cells: only Line 1 required.
    Cells with %% magic: skipped entirely.
    """
    OPTIONAL_TAGS = {'CONFIG', 'SETUP'}
    header_line1_re = re.compile(r'^#\s*\[(?:CONFIG|SETUP|FUNC|RUN|VIZ|EXPORT)\]')
    header_line2_re = re.compile(r'^#\s*输入[:：]')
    header_line3_re = re.compile(r'^#\s*输出[:：]')

    for i, c in enumerate(cells):
        if c.cell_type != 'code' or not c.source.strip():
            continue
        if c.source.strip().startswith('%%'):
            continue

        # Collect first 3 non-blank lines
        non_blank = [l for l in c.source.splitlines() if l.strip()]
        if not non_blank:
            continue

        tag = _get_tag(c)

        line1 = non_blank[0].strip() if len(non_blank) >= 1 else ''
        line2 = non_blank[1].strip() if len(non_blank) >= 2 else ''
        line3 = non_blank[2].strip() if len(non_blank) >= 3 else ''

        if not header_line1_re.match(line1):
            err(f'Check 11: cell {i} missing [TAG] header on first non-blank line')
            continue

        if tag in OPTIONAL_TAGS:
            continue

        if not header_line2_re.match(line2):
            w(f'Check 11: cell {i} ({tag}) missing "# 输入:" on line 2')
        if not header_line3_re.match(line3):
            w(f'Check 11: cell {i} ({tag}) missing "# 输出:" on line 3')

    ok('Check 11 docstring header scan complete')


def check_output_contract(cells):
    """Check 12: Enforce output contract per cell type.

    [RUN] cells: last 10 lines must contain print( or display(.
    [VIZ] cells: must contain plt.show/fig.show/.show() AND a print( after the show call.
    CONFIG/SETUP/EXPORT/FUNC: skipped.
    Violations are warnings (backward compat).
    """
    SKIP_TAGS = {'CONFIG', 'SETUP', 'EXPORT', 'FUNC'}

    for i, c in enumerate(cells):
        if c.cell_type != 'code' or not c.source.strip():
            continue
        tag = _get_tag(c)
        if tag is None or tag in SKIP_TAGS:
            continue

        source = c.source
        lines = source.splitlines()

        if tag == 'RUN':
            last10 = '\n'.join(lines[-10:])
            if not OUTPUT_RE.search(last10):
                w(f'Check 12: [RUN] cell {i} last 10 lines have no print(/display(')

        elif tag == 'VIZ':
            show_match = SHOW_RE.search(source)
            if not show_match:
                w(f'Check 12: [VIZ] cell {i} missing plt.show()/fig.show()/.show()')
            else:
                after_show = source[show_match.end():]
                if not OUTPUT_RE.search(after_show):
                    w(f'Check 12: [VIZ] cell {i} missing print( after show call (reading takeaway)')

    ok('Check 12 output contract scan complete')


def check_comment_density(cells):
    """Check 13: Enforce Chinese comment density in RUN/VIZ cells.

    chinese_comment_lines / executable_lines >= 1/5 (0.20): OK
    1/8 <= ratio < 1/5: WARN
    ratio < 1/8 (0.125): ERROR
    Skip cells with < 5 executable lines.
    Skip CONFIG/SETUP/EXPORT cells.
    """
    SKIP_TAGS = {'CONFIG', 'SETUP', 'EXPORT'}
    TARGET_TAGS = {'RUN', 'VIZ'}

    for i, c in enumerate(cells):
        if c.cell_type != 'code' or not c.source.strip():
            continue
        tag = _get_tag(c)
        if tag not in TARGET_TAGS:
            continue

        lines = c.source.splitlines()
        exec_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        chinese_comment_lines = [
            l for l in lines
            if l.strip().startswith('#') and CHINESE_RE.search(l)
        ]

        if len(exec_lines) < 5:
            continue

        ratio = len(chinese_comment_lines) / len(exec_lines)
        if ratio >= 0.20:
            pass  # OK, no output for passing cells
        elif ratio >= 0.125:
            w(f'Check 13: cell {i} ({tag}) comment density {ratio:.2f} (< 1/5, target >= 0.20)')
        else:
            err(f'Check 13: cell {i} ({tag}) comment density {ratio:.2f} (< 1/8, critically low)')

    ok('Check 13 comment density scan complete')


def check_chart_registry(cells):
    """Check 14: Verify CHART_REGISTRY fig_var references exist in VIZ cells.

    For each fig_var declared in CHART_REGISTRY, check that the variable name
    appears in at least one [VIZ] cell source. Missing references → WARN.
    If no CHART_REGISTRY found → skip with info message.
    """
    all_source = '\n'.join(c.source for c in cells if c.cell_type == 'code')

    if 'CHART_REGISTRY[' not in all_source:
        ok('Check 14: [SKIP] CHART_REGISTRY 未定义（可选功能）')
        return

    fig_vars = FIG_VAR_RE.findall(all_source)
    viz_source = '\n'.join(
        c.source for c in cells
        if c.cell_type == 'code' and _get_tag(c) == 'VIZ'
    )

    missing = [fv for fv in fig_vars if fv not in viz_source]
    if missing:
        for fv in missing:
            w(f'Check 14: fig_var "{fv}" declared in CHART_REGISTRY but not found in any [VIZ] cell')
    else:
        ok(f'Check 14: all {len(fig_vars)} CHART_REGISTRY fig_var(s) referenced in VIZ cells')


def check_html_slot_unique(cells):
    """Check 15: Enforce unique html_slot values in CHART_REGISTRY.

    Duplicate html_slot values → ERROR with the duplicated slot name.
    If no CHART_REGISTRY → skip silently.
    """
    all_source = '\n'.join(c.source for c in cells if c.cell_type == 'code')

    if 'CHART_REGISTRY[' not in all_source:
        return

    slots = HTML_SLOT_RE.findall(all_source)
    seen = {}
    for slot in slots:
        seen[slot] = seen.get(slot, 0) + 1

    duplicates = [slot for slot, count in seen.items() if count > 1]
    if duplicates:
        for slot in duplicates:
            err(f'Check 15: html_slot "{slot}" is duplicated in CHART_REGISTRY (must be unique)')
    else:
        ok(f'Check 15: all {len(slots)} html_slot value(s) are unique')


def validate(path):
    print(f'\nValidating: {path}\n{"=" * 50}')
    cells = load_cells(path)
    code_cells = [c for c in cells if c.cell_type == 'code']
    md_cells = [c for c in cells if c.cell_type == 'markdown']
    ok(f'Cells: {len(cells)} total (md={len(md_cells)}, code={len(code_cells)})\n')

    check_syntax(cells)
    check_tags(cells)
    check_md_ratio(cells)
    print()
    found = find_m_cells(cells)
    check_m_sequence(found)
    check_m5_m6(cells, found)
    check_m8_m6(found)
    archetype = detect_archetype(cells)
    check_chapters(cells, archetype)

    print()
    print("--- Readability Checks ---")
    check_cell_length(cells)
    check_docstring_header(cells)
    check_output_contract(cells)
    check_comment_density(cells)
    check_chart_registry(cells)
    check_html_slot_unique(cells)

    print(f'\n{"=" * 50}')
    if errors_list:
        print(f'Result: {len(errors_list)} error(s), {len(warnings_list)} warning(s)')
        return 1
    elif warnings_list:
        print(f'Result: 0 errors, {len(warnings_list)} warning(s)')
        return 2
    print('Result: all checks passed')
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: python {sys.argv[0]} <notebook.ipynb>')
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))
