# Guanyuan Data Fetcher

通用观远数据看板抓取工具，支持任意看板和卡片配置。

## 版本

**v2.0.0** - 泛化版本，支持JSON配置文件和CLI参数

## 快速开始

### 安装

1. 将此skill复制到你的项目的 `.claude/skills/` 目录
2. 将 `scripts/guanyuan_fetch/` 目录复制到项目根目录的 `scripts/` 下
3. 安装依赖: `pip install -r scripts/guanyuan_fetch/requirements.txt`

### 基本使用

```bash
# 使用默认配置 (1.2 核心指标看板, 5个卡片)
/guanyuan-data-fetcher

# 使用自定义配置
/guanyuan-data-fetcher --config=configs/my_dashboard.json

# 指定日期范围
/guanyuan-data-fetcher --start-date=2026-01-01 --end-date=2026-03-31

# CSV格式输出
/guanyuan-data-fetcher --format=csv
```

## 配置文件

### 创建自定义配置

1. 复制 `scripts/guanyuan_fetch/configs/template.json`
2. 填写你的看板和卡片信息
3. 保存到 `scripts/guanyuan_fetch/configs/` 目录
4. 运行: `/guanyuan-data-fetcher --config=configs/your_config.json`

### 配置示例

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

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--config` | JSON配置文件路径 | (内置默认) |
| `--start-date` | 开始日期 (YYYY-MM-DD) | 2025-12-01 |
| `--end-date` | 结束日期 (YYYY-MM-DD) | 今天 |
| `--format` | 输出格式 (csv/excel) | excel |
| `--output-dir` | 输出目录 | Data/guanyuan |
| `--page-id` | 覆盖看板ID | (来自配置) |

## 筛选器模板

- **Template A**: 2个筛选器 (日期维度 + 日期区间)
- **Template B**: 5个筛选器 (日期维度 + T+N口径 + 日期区间 + 一级渠道 + 二级渠道)

## 依赖

- MCP Server: `sh_guanyuan_data`
- Python: `openpyxl>=3.0.0`, `pandas>=1.3.0`

## 变更日志

### v2.0.0 (2026-03-30)
- 泛化为通用版本，支持任意看板和卡片
- 新增JSON配置文件支持
- 新增CLI参数覆盖功能
- 保持向后兼容性

### v1.0.0
- 初始版本，硬编码5个卡片配置

## 许可

内部使用 - 数禾DS团队
