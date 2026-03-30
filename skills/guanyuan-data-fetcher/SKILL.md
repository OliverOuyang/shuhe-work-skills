# Guanyuan Data Fetcher

通用观远数据看板抓取工具，支持任意看板和卡片配置，输出CSV或Excel格式。

## 功能描述

从观远数据平台的任意看板抓取卡片数据。支持:

- **JSON配置文件驱动**: 通过配置文件定义看板、卡片、筛选模板
- **CLI参数覆盖**: 运行时覆盖日期范围、输出目录、看板ID等
- **多输出格式**: CSV (每卡片一个文件) 或 Excel (多Sheet单文件)
- **向后兼容**: 无参数调用时使用内置默认配置 (1.2 核心指标看板, 5个卡片)

### 默认配置 (内置)

当不指定 `--config` 时，默认抓取看板 `1.2 核心指标` 的以下5个卡片:

1. **首借交易额_重主营_by 6大客群** (默认tab, Template A)
2. **首借交易金额** (规模tab, Template B)
3. **过件率-排年龄_分渠道** (质量tab, Template B)
4. **1-3过件率-排年龄_分渠道** (质量tab, Template B)
5. **申完成本_排年龄_分渠道** (效率tab, Template B)

## 使用方法

### 基本用法 (使用默认配置)

```bash
/guanyuan-data-fetcher
```

等价于旧版 `/fetch-guanyuan-monthly`，使用内置5卡片配置，Excel格式输出。

### 指定输出格式

```bash
# Excel格式 (默认)
/guanyuan-data-fetcher --format=excel

# CSV格式
/guanyuan-data-fetcher --format=csv
```

### 指定日期范围

```bash
/guanyuan-data-fetcher --start-date=2026-01-01 --end-date=2026-03-31
```

### 使用自定义配置文件

```bash
/guanyuan-data-fetcher --config=configs/my_dashboard.json
```

### 完整参数示例

```bash
/guanyuan-data-fetcher \
  --config=configs/my_dashboard.json \
  --start-date=2026-01-01 \
  --end-date=2026-03-31 \
  --format=excel \
  --output-dir=Data/custom_output \
  --page-id=override_page_id
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--config` | string | (内置默认) | JSON配置文件路径 |
| `--start-date` | YYYY-MM-DD | 2025-12-01 | 开始日期 |
| `--end-date` | YYYY-MM-DD | 今天 | 结束日期 |
| `--format` | csv/excel | excel | 输出格式 |
| `--output-dir` | string | Data/guanyuan | 输出目录 |
| `--page-id` | string | (来自配置) | 覆盖看板ID |
| `--excel` | flag | - | 等价于 --format=excel (向后兼容) |

## 配置文件

### 结构

```json
{
  "page_id": "wac63dff1a9ee41988f87507",
  "page_name": "1.2 核心指标",
  "default_date_range": {
    "start": "2025-12-01",
    "end": "today"
  },
  "cards": [
    {
      "card_id": "jf7c4b4828db24159b573a32",
      "card_name": "首借交易额_重主营_by 6大客群",
      "filter_template": "A",
      "output_filename": "首借交易额_重主营_by6大客群.csv",
      "tab_name": "默认"
    }
  ]
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `page_id` | 是 | 观远看板页面ID |
| `page_name` | 是 | 看板名称 (用于生成文件名) |
| `default_date_range.start` | 否 | 默认开始日期 (可被CLI覆盖) |
| `default_date_range.end` | 否 | 默认结束日期, "today"表示当天 |
| `cards[].card_id` | 是 | 卡片ID (从观远看板URL获取) |
| `cards[].card_name` | 是 | 卡片名称 (用作Sheet名) |
| `cards[].filter_template` | 是 | 筛选器模板: "A" 或 "B" |
| `cards[].output_filename` | 否 | CSV输出文件名 (默认: 卡片名.csv) |
| `cards[].tab_name` | 否 | 所在Tab名称 (仅描述用) |

### 筛选器模板

- **Template A**: 2个筛选器 (日期维度 + 日期区间)
- **Template B**: 5个筛选器 (日期维度 + T+N口径 + 日期区间 + 一级渠道 + 二级渠道)

### 自定义看板配置步骤

1. 在观远数据平台找到目标看板，从URL获取 `page_id`
2. 使用 `get_page_cards` MCP工具获取卡片列表和 `card_id`
3. 使用 `get_card_filters` MCP工具确定卡片的筛选器模板类型
4. 编写配置文件，放入 `scripts/guanyuan_fetch/configs/` 目录
5. 运行: `/guanyuan-data-fetcher --config=configs/your_config.json`

### 配置文件位置

```
scripts/guanyuan_fetch/configs/
├── default.json          # 默认配置 (1.2 核心指标)
├── template.json         # 空白模板
└── <your_config>.json    # 自定义配置
```

## 输出结构

**Excel格式 (默认)**:
```
Data/guanyuan/
├── 核心指标_20251201_20260330.xlsx
│   ├── Sheet: 首借交易额_重主营_by6大客群
│   ├── Sheet: 首借交易金额
│   ├── ...
└── _metadata.json
```

**CSV格式**:
```
Data/guanyuan/
├── 首借交易额_重主营_by6大客群.csv
├── 首借交易金额.csv
├── ...
└── _metadata.json
```

## 执行流程

当用户调用 `/guanyuan-data-fetcher` 时, Claude Code将执行以下步骤:

### Step 1: 加载配置并初始化

```python
import sys
sys.path.insert(0, 'C:/Users/Oliver/Desktop/数禾工作/16_AI项目/2_预算MMM模型')

from scripts.guanyuan_fetch.main import (
    build_runtime_config, get_all_cards, create_initial_metadata,
    prepare_fetch_params, process_card_response, fetch_all_cards_to_excel
)
from scripts.guanyuan_fetch.metadata_writer import write_metadata, add_card_result, add_error
from pathlib import Path
from datetime import datetime

# Parse skill arguments (passed from /guanyuan-data-fetcher invocation)
# config_path = None  # or "configs/my_dashboard.json"
# start_date = None   # or "2026-01-01"
# end_date = None     # or "2026-03-31"
# output_format = "excel"  # or "csv"
# output_dir = "Data/guanyuan"
# page_id = None

# Build runtime config
dashboard = build_runtime_config(
    config_path=config_path,
    start_date=start_date,
    end_date=end_date,
    page_id=page_id,
)

# Initialize metadata
metadata = create_initial_metadata(dashboard)
cards = get_all_cards(dashboard)
output_dir = Path(output_dir)

print(f"看板: {dashboard.page_name} ({dashboard.page_id})")
print(f"开始抓取 {len(cards)} 个卡片的数据...")
print(f"时间范围: {dashboard.start_date} 至 {dashboard.get_end_date()}")
print(f"输出格式: {output_format}")
```

### Step 2: 遍历每个卡片并抓取数据

对每个卡片,执行子步骤:

#### Step 2.1: 准备卡片参数

```python
card = cards[0]  # 使用实际索引
print(f"\n处理卡片 {card.card_name}...")

fetch_params = prepare_fetch_params(card, dashboard)
print(f"  - 卡片ID: {fetch_params['cardId']}")
print(f"  - 筛选器数量: {len(fetch_params['cardFilters'])}")
```

#### Step 2.2: 调用MCP获取数据

使用 `mcp__sh_guanyuan_data__get_card_data` 工具:

```python
response = mcp__sh_guanyuan_data__get_card_data(
    cardId=fetch_params['cardId'],
    cardFilters=fetch_params['cardFilters']
)
```

#### Step 2.3: 处理响应

**CSV模式**: 直接保存每个卡片的CSV
```python
try:
    result = process_card_response(response, card, output_dir)
    print(f"  OK: {result['row_count']} 行数据")
    add_card_result(metadata, result['card_id'], result['card_name'],
                    result['output_path'], result['row_count'],
                    result['column_count'], result['headers'])
except Exception as e:
    print(f"  FAIL: {str(e)}")
    add_error(metadata, card.card_id, card.card_name, str(e))
```

**Excel模式**: 收集所有响应后统一写入
```python
# 收集所有响应
all_responses.append({
    "card_name": card.card_name,
    "response_data": response
})
```

**重复 Step 2.1-2.3 对所有卡片**

### Step 3: 输出结果

**CSV模式**: 写入元数据
```python
metadata['fetch_timestamp'] = datetime.now().isoformat()
metadata_path = write_metadata(metadata, output_dir)
```

**Excel模式**: 统一写入Excel + 元数据
```python
result = fetch_all_cards_to_excel(all_responses, output_dir=output_dir, dashboard=dashboard)
```

### Step 4: 报告执行结果

```python
print(f"\n执行完成!")
print(f"成功: {metadata['cards_fetched']['success_count']}/{metadata['cards_fetched']['total_count']}")
if metadata['errors']:
    print("失败的卡片:")
    for error in metadata['errors']:
        print(f"  - {error['card_name']}: {error['error']}")
print(f"输出目录: {output_dir.absolute()}")
```

## 错误处理

- 部分卡片失败不影响其他卡片的抓取
- 所有错误记录在 `_metadata.json` 的 `errors` 字段
- 权限不足时自动提示申请权限

## 依赖

- **MCP Server**: `sh_guanyuan_data` (观远数据连接器)
- **Python Packages**:
  - `openpyxl>=3.0.0` (Excel multi-sheet支持)
  - `pandas>=1.3.0` (数据处理)
  - 详见 `scripts/guanyuan_fetch/requirements.txt`
- **Python Modules**: `scripts/guanyuan_fetch/` 下的工具模块

## 维护

如需修改筛选器模板逻辑,编辑:
- `scripts/guanyuan_fetch/filter_builder.py` (筛选器构建逻辑)

如需添加新的看板,创建JSON配置文件:
- `scripts/guanyuan_fetch/configs/<name>.json`

---

**版本**: 2.0.0
**作者**: 数禾DS团队
**创建日期**: 2026-03-30
**变更日志**:
- v2.0.0: 泛化为通用版本,支持JSON配置文件、CLI参数、任意看板
- v1.0.0: 初始版本,硬编码5个卡片配置
