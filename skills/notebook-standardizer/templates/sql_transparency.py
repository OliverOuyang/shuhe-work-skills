# [RUN] SQL 透明审查 — 执行前查看完整参数化 SQL
# 输入: SQL_DIR 下的 .sql 文件, PARAMS 字典
# 输出: 每个 SQL 文件的行数 + 完整内容预览, 确认后再执行 M6

# 本项目涉及的 SQL 文件清单
SQL_FILES = {
    "精准排除包": "精准排除包.sql",    # V8/V7 精准排除包月度溢出+回收指标
    "API排除包":  "API排除包.sql",     # 撞库排除包命中率+过件率
}

# PARAMS 来自 M3 CONFIG cell，含 bizdate/start_month/end_month

for name, filename in SQL_FILES.items():
    _path = os.path.join(SQL_DIR, filename)
    # 读取原始 SQL，用 load_sql_file 做占位符替换（去注释+去SET语句）
    try:
        _rendered = load_sql_file(_path, PARAMS)
    except FileNotFoundError:
        print(f"[WARN] {name}: 文件不存在 — {_path}")
        continue
    except KeyError as e:
        print(f"[WARN] {name}: 参数缺失 {e}，显示原始内容")
        with open(_path, encoding="utf-8") as fh:
            _rendered = fh.read()

    # 打印行数与完整 SQL，方便逐行审查分区条件和字段名
    _line_count = _rendered.count("\n") + 1
    print(f"\n{'='*60}")
    print(f"[SQL] {name} ({filename}, {_line_count} 行)")
    print(f"{'='*60}")
    print(_rendered)

print(f"\n[OK] 共展示 {len(SQL_FILES)} 个 SQL 文件，审查通过后执行 M6 取数")
