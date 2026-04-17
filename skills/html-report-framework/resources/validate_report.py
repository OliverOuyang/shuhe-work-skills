#!/usr/bin/env python3
"""HTML Report Quality Gate Validator
Usage: python validate_report.py <file.html>
Returns exit code 0 on PASS, 1 on FAIL.
"""
import sys
import re
from html.parser import HTMLParser


class ReportValidator(HTMLParser):
    """Parse HTML and count content elements, skipping style/script blocks."""

    def __init__(self):
        super().__init__()
        self.in_style = False
        self.in_script = False
        self.charts = 0
        self.conclusions = 0
        self.mermaid = 0
        self.sections = 0
        self.visuals = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get("class", "")
        id_ = d.get("id", "")

        if tag == "style":
            self.in_style = True
        if tag == "script":
            self.in_script = True
        if self.in_style or self.in_script:
            return

        # Charts
        if "chart-container" in cls or id_.startswith("chart-"):
            self.charts += 1
            self.visuals += 1

        # Conclusions (blockquote.conclusion, div.callout, div.conclusion-item)
        if tag == "blockquote" and "conclusion" in cls:
            self.conclusions += 1
        if "conclusion-item" in cls:
            self.conclusions += 1
        # callout with space-separated class (e.g., "callout info")
        cls_parts = cls.split()
        if "callout" in cls_parts and tag == "div":
            self.conclusions += 1

        # Mermaid
        if tag == "pre" and "mermaid" in cls:
            self.mermaid += 1
            self.visuals += 1

        # Sections
        if "section-number" in cls:
            self.sections += 1

        # Other visual components
        for v in [
            "flow-diagram", "chain-container", "info-card", "metric-grid",
            "def-grid", "timeline", "formula-block",
        ]:
            if v in cls:
                self.visuals += 1

        if tag == "table":
            self.visuals += 1

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        if tag == "script":
            self.in_script = False


def validate(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    p = ReportValidator()
    p.feed(html)

    checks = []

    # 1. No remaining placeholders
    placeholders = len(re.findall(r"__[A-Z_]+__", html))
    checks.append(("No placeholders", placeholders == 0, f"{placeholders} remaining"))

    # 2. Conclusions >= Charts
    checks.append((
        "Conclusions >= Charts",
        p.conclusions >= p.charts,
        f"conclusions={p.conclusions} charts={p.charts}",
    ))

    # 3. No broken UTF-8
    broken = html.count("\ufffd")
    checks.append(("No broken chars", broken == 0, f"{broken} found"))

    # 4. Sidebar present
    checks.append(("Sidebar present", 'id="sidebar"' in html, ""))

    # 5. ECharts CDN in <head>
    head = html.split("</head>")[0] if "</head>" in html else html[:3000]
    checks.append(("ECharts CDN", "echarts" in head, ""))

    # 6. Visuals per section >= 1
    ratio = p.visuals / max(p.sections, 1)
    checks.append((
        "Visuals/Section >= 1",
        ratio >= 1.0,
        f"{p.visuals} visuals / {p.sections} sections = {ratio:.1f}",
    ))

    passed = sum(1 for _, ok, _ in checks if ok)
    failed = sum(1 for _, ok, _ in checks if not ok)

    print(f"\n  HTML Report Quality Gate -- {filepath}\n")
    for name, ok, detail in checks:
        sym = "PASS" if ok else "FAIL"
        extra = f" ({detail})" if detail else ""
        print(f"  {sym} {name}{extra}")

    print(f"\n  Result: {passed} passed, {failed} failed")
    status = "PASS" if failed == 0 else "FAIL"
    print(f"  QUALITY GATE: {status}\n")
    return failed == 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_report.py <file.html>")
        sys.exit(1)
    ok = validate(sys.argv[1])
    sys.exit(0 if ok else 1)
