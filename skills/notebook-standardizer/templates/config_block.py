# [CONFIG] 项目参数 — 运行前检查并按需修改
# 输入: 无 (手动设置)
# 输出: 全局变量 ARCHETYPE/DATA_MODE/START_MONTH/END_MONTH/PARAMS/CHART_REGISTRY

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# 分析模式参数
ARCHETYPE   = "problem-driven"  # str: 分析类型 | "problem-driven"=问题驱动 / "monitoring"=监控周报
DATA_MODE   = "sql"             # str: 取数方式 | "sql"=在线查询 / "csv"=加载本地缓存

# 分析时间范围 (yyyymm 格式)
START_MONTH = "202501"          # str: 分析起始月
END_MONTH   = "202503"          # str: 分析截止月
BIZDATE     = "20250331"        # str: 业务日期，对应最新分区

# 项目路径 (设置一次，全 notebook 复用)
PROJECT_DIR = os.path.dirname(os.path.abspath("__file__"))
DATA_DIR    = os.path.join(PROJECT_DIR, "data")
SQL_DIR     = os.path.join(PROJECT_DIR, "sql")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SQL_DIR,  exist_ok=True)

# SQL 参数字典，传给 load_sql_file 做占位符替换
PARAMS = {
    "bizdate":     BIZDATE,
    "start_month": START_MONTH,
    "end_month":   END_MONTH,
}

# 排除包项目专用参数
CHANNEL_LIST   = ["抖音", "腾讯", "其他"]   # list: 渠道维度
PKG_TYPES      = ["V8精准排除包", "V7精准排除包", "API排除包"]  # list: 排除包类型

# 图表注册表占位（由 M9.5 chart_registry cell 填充）
CHART_REGISTRY = {}

print(f"[OK] CONFIG 已加载: {START_MONTH} ~ {END_MONTH}, DATA_MODE={DATA_MODE}")
