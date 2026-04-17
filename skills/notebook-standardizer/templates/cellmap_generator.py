# [EXPORT] 生成 cellmap.md 侧车导航文件
# 输入: notebook_path (ipynb 文件路径)
# 输出: {notebook_stem}.cellmap.md, 打印行数

import json
from pathlib import Path
import re

# 从 notebook JSON 提取 cell 信息，生成导航表格
TAG_RE = re.compile(r'^#\s*\[(CONFIG|SETUP|FUNC|RUN|VIZ|EXPORT)\](.*)$', re.M)
FIG_RE = re.compile(r'\b(fig_\w+)\s*=')
DF_RE = re.compile(r'\b(df_\w+)\s*=')


def generate_cellmap(notebook_path):
    """读取 ipynb 并输出 cellmap.md 侧车文件"""
    nb_path = Path(notebook_path)
    with open(nb_path, encoding="utf-8") as f:
        nb = json.load(f)

    rows = ["| Cell Idx | Tag | Name | Produces | Used By |",
            "|----------|-----|------|----------|---------|"]

    # 逐 cell 提取标签、标题、产出物
    for idx, cell in enumerate(nb.get("cells", [])):
        src = "".join(cell.get("source", []))
        ctype = cell.get("cell_type", "code")

        if ctype == "markdown":
            # markdown cell: 取第一行作为名称
            first_line = src.split("\n")[0].strip().lstrip("#").strip()[:30]
            rows.append(f"| {idx} | md | {first_line} | — | — |")
        else:
            # code cell: 提取 tag 和产出物
            m = TAG_RE.search(src)
            tag = f"[{m.group(1)}]" if m else "—"
            title = m.group(2).strip()[:30] if m else "untitled"

            # 提取 fig_ 和 df_ 变量名作为产出物
            figs = FIG_RE.findall(src)
            dfs = DF_RE.findall(src)
            produces = ", ".join(figs + dfs)[:40] or "—"

            rows.append(f"| {idx} | {tag} | {title} | {produces} | — |")

    # 写入 cellmap.md
    out_path = nb_path.with_suffix(".cellmap.md")
    out_path.write_text("\n".join(rows), encoding="utf-8")
    print(f"[OK] cellmap 已生成: {out_path.name} ({len(rows)-2} cells)")
    return out_path


# 独立运行: python cellmap_generator.py notebook.ipynb
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <notebook.ipynb>")
        sys.exit(1)
    generate_cellmap(sys.argv[1])
