# [RUN] 数据取数 — load_sql_file → pipe.run → CSV 缓存
# 输入: SQL_DIR/精准排除包.sql + API排除包.sql, PARAMS, DATA_MODE
# 输出: df_precise (精准排除包), df_api (API排除包), 打印行数和文件名

from data_client import load_sql_file, QueryPipeline
from datetime import datetime as _dt

# 主查询：精准排除包（V8+V7 合并，按渠道+月+包类型聚合）
if DATA_MODE == "sql":
    _sql_precise = load_sql_file(os.path.join(SQL_DIR, "精准排除包.sql"), PARAMS)
    df_precise, _ = pipe.run(_sql_precise, use_cache=True)
    # 带时间戳落盘，保留历史版本不覆盖
    _ts = _dt.now().strftime("%Y%m%d_%H%M")
    _csv_p = os.path.join(DATA_DIR, f"精准排除包_{_ts}.csv")
    df_precise.to_csv(_csv_p, index=False, encoding="utf-8-sig")
    print(f"[OK] df_precise: {df_precise.shape} → {os.path.basename(_csv_p)}")

elif DATA_MODE == "csv":
    # 加载最新缓存文件（文件名按时间戳排序取最后一个）
    _files = sorted([f for f in os.listdir(DATA_DIR)
                     if f.startswith("精准排除包_") and f.endswith(".csv")])
    if _files:
        df_precise = pd.read_csv(os.path.join(DATA_DIR, _files[-1]))
        print(f"[OK] 加载缓存: {_files[-1]} ({df_precise.shape[0]} 行)")
    else:
        print("[WARN] 无缓存，请先用 DATA_MODE='sql' 取数")
        df_precise = pd.DataFrame()

print(f"df_precise shape: {df_precise.shape}")

# --- 多查询并行模式 (可选) ---
# 如需同时拉取精准排除包 + API排除包，取消下方注释
# from concurrent.futures import ThreadPoolExecutor
# SQL_TASKS = {"精准排除包": "精准排除包.sql", "API排除包": "API排除包.sql"}
# results = {}
# if DATA_MODE == "sql":
#     def _run_one(name, fname):
#         _sql = load_sql_file(os.path.join(SQL_DIR, fname), PARAMS)
#         _df, _ = pipe.run(_sql, use_cache=True)
#         _csv = os.path.join(DATA_DIR, f"{name}_{_dt.now().strftime('%Y%m%d_%H%M')}.csv")
#         _df.to_csv(_csv, index=False, encoding="utf-8-sig")
#         return name, _df
#     with ThreadPoolExecutor(max_workers=2) as pool:
#         for name, df in [f.result() for f in
#                          [pool.submit(_run_one, n, f) for n, f in SQL_TASKS.items()]]:
#             results[name] = df
#             print(f"[OK] {name}: {df.shape[0]} 行")
# df_precise = results.get("精准排除包", pd.DataFrame())
# df_api     = results.get("API排除包",  pd.DataFrame())
