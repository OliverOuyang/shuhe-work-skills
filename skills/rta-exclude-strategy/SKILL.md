---
name: rta-exclude-strategy
description: RTA排除策略分析技能 - 基于V8和V9RN双模型交叉分析的智能排除策略生成
argument-hint: "--data_path <path> --ctrl_group_value <value> [options]"
version: 1.1.0
level: 3
tags:
  - data-analysis
  - rta
  - strategy
  - chinese
---

# rta-exclude-strategy

RTA排除策略分析技能 - 基于V8和V9RN双模型交叉分析的智能排除策略生成

## Description

自动化RTA（Real-Time Advertising）排除策略分析系统，支持：
- 基于V8和V9RN模型的二维交叉分析
- 智能置入置出算法自动生成排除区域
- 新老策略全面对比评估
- 生成企业规范Excel分析报告
- 安全过件率阈值约束和交易占比约束

## Dependencies

### Python Packages
- pandas>=1.3.0
- numpy>=1.20.0
- openpyxl>=3.0.0

### Installation
```bash
pip install -r scripts/requirements.txt
```

## Usage

```bash
/rta-exclude-strategy --data_path <path> --ctrl_group_value <value> [options]
```

## Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `--data_path` | string | 数据文件路径（CSV或Excel） | `data.csv` |
| `--ctrl_group_value` | string | 对照组标识值 | `ctrl` |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--old_exclude_rule` | string | `01q-10q` | 老策略排除规则（逗号分隔） |
| `--spr_threshold` | float | `0.10` | 安全过件率阈值（10%） |
| `--max_exclude_ratio` | float | `0.20` | 最大排除交易占比（20%） |
| `--output_path` | string | `.` | 输出文件路径 |
| `--output_format` | string | `both` | 输出格式选择（excel/html/both） |

## Data Requirements

### Required Fields

| Field | Description | Format |
|-------|-------------|--------|
| `V8` | V8模型分组 | 01q-20q, UNK |
| `V9RN` | V9RN模型分组 | 01q-20q, UNK |
| `group` | 实验分组标识 | string |
| `expo_cnt` | 曝光数 | numeric |
| `cost` | 成本 | numeric |
| `t3_ato` | T3申完数 | numeric |
| `t3_safe_adt` | T3安全授信数 | numeric |
| `t3_loan_amt` | T3交易金额 | numeric |

### Data Format
- 支持CSV和Excel格式
- 模型分组必须为01q-20q格式（允许UNK）
- 数值字段允许缺失（自动处理为0）
- 缺失值标记：`/N`, `#N/A`, `\N`

## Algorithm Overview

### 数据预处理

1. **缺失值处理**：替换 `/N`, `#N/A`, `\N` 为 0
2. **类型转换**：确保数值列类型正确
3. **模型分组聚合**：
   - 01q-09q → 01Q
   - 10q → 02Q
   - 11q → 03Q
   - 12q → 04Q
   - ...
   - 20q → 12Q
   - UNK → UNK

### 置入置出算法

详细算法逻辑见 `resources/置入置出算法.txt`

**核心步骤**：

1. **初始圈选**：圈选安全过件率≤阈值的客群
2. **置入扩充**：从右下往左上扩充，添加安全过件率≥阈值的区域
3. **置出扩充**：从左上往右下扩充，添加安全过件率≤阈值的区域
4. **计算排除区域**：排除区域 = 初始区域 - 置入区域 + 置出区域
5. **约束验证**：验证排除交易占比≤最大值

### 报告生成

**一、核心结论**
- 新老策略关键指标对比
- 策略优劣评价

**二、排除策略制定**
1. 排除策略现状（老策略，使用全量数据）
2. 排除策略制定
   - 新老策略指标差异对比（使用对照组数据）
   - 新策略排除规则（二维热力图，使用全量数据）

**三、合理性评估**
1. 置入置出合理性分析
2. 交叉表展示
   - 交易占比交叉表
   - 安全过件率交叉表
   - CPS交叉表

## Examples

### Basic Usage

```bash
# 最简单的使用方式
/rta-exclude-strategy \
  --data_path data.csv \
  --ctrl_group_value ctrl
```

### Custom Parameters

```bash
# 自定义所有参数
/rta-exclude-strategy \
  --data_path data.xlsx \
  --ctrl_group_value control \
  --old_exclude_rule "01q,02q,03q" \
  --spr_threshold 0.08 \
  --max_exclude_ratio 0.15 \
  --output_path ./reports/
```

### Typical Workflow

```bash
# 1. 准备数据文件
# 确保包含必需字段：V8, V9RN, group, expo_cnt, cost, t3_ato, t3_safe_adt, t3_loan_amt

# 2. 运行分析（使用默认参数）
/rta-exclude-strategy \
  --data_path experiment_data.csv \
  --ctrl_group_value ctrl

# 3. 查看生成的Excel报告
# 报告包含：核心结论、排除策略制定、合理性评估
```

### HTML Output Example

```bash
# 只生成 HTML 报告
/rta-exclude-strategy \
  --data_path data.csv \
  --ctrl_group_value ctrl \
  --output_format html
```

## Output

### File Name Format
Excel: `RTA排除策略分析报告_YYYYMMDD_HHMMSS.xlsx`
HTML: `RTA排除策略分析报告_YYYYMMDD_HHMMSS.html`

### Report Structure

**Sheet: 分析报告**
- 核心结论（新老策略对比）
- 排除策略现状表
- 新老策略指标差异对比表
- 新策略排除规则热力图（红色标记排除区域）
- 置入置出合理性分析
- 交易占比/安全过件率/CPS交叉表

**HTML Report Features:**
- 左侧固定目录导航
- 响应式设计,支持移动端
- 交互式表格(排序、筛选)
- 热力图可视化
- 可编辑文本内容
- 单文件自包含,可离线使用

### Format Standards
- 字体：楷体
- 数值格式：<1的数值显示为百分比
- 排除区域：红色背景高亮
- 对齐方式：居中对齐

## Use Cases

### 场景1：定期策略优化
定期（如月度）运行分析，评估当前排除策略效果，生成优化建议。

### 场景2：实验效果评估
针对新实验数据，快速生成排除策略建议，评估策略改进空间。

### 场景3：模型升级评估
当模型版本升级时，评估新老策略在新模型下的表现差异。

### 场景4：阈值敏感性分析
通过调整安全过件率阈值，分析不同阈值下的策略效果。

## Notes

1. **数据质量**：确保模型分组格式正确（01q-20q），数值字段无异常值
2. **对照组标识**：必须准确指定对照组标识值，用于新老策略对比
3. **约束条件**：
   - 安全过件率阈值通常设为10%
   - 排除交易占比上限通常为20%
   - 如果约束无法满足，算法会尝试自动调整
4. **输出路径**：确保输出目录存在且有写权限
5. **文件命名**：输出文件自动添加时间戳，避免覆盖
6. **Excel兼容性**：生成的Excel文件使用openpyxl库，兼容Excel 2010+

## Troubleshooting

### Q: 数据中没有UNK分组怎么办？
A: 算法会自动处理，UNK分组为可选项，不影响分析结果。

### Q: 如何指定老策略排除规则？
A: 使用`--old_exclude_rule`参数，格式为逗号分隔的分组列表。例如：
```bash
--old_exclude_rule "01q,02q,03q,04q,05q"
```
算法会自动将其聚合为对应的Q分组（01q-09q → 01Q-02Q）。

### Q: 排除交易占比始终超过20%怎么办？
A: 算法会尝试调整阈值。如果仍无法满足：
1. 检查数据质量，确认安全过件率分布是否异常
2. 考虑放宽最大排除交易占比约束
3. 调整安全过件率阈值（如从10%调整为8%或12%）

### Q: 报告生成失败怎么办？
A: 检查以下几点：
- 输出路径是否存在且有写权限
- Excel文件是否被其他程序打开
- 查看终端错误日志获取详细信息
- 确认openpyxl库已正确安装

### Q: 模型分组格式不正确怎么办？
A: 确保数据中的V8和V9RN字段值为：
- 01q, 02q, ..., 20q（小写q）
- UNK（大写）
- 其他格式会导致预处理失败

### Q: 如何理解置入置出算法的结果？
A: 查看报告中的"置入置出合理性分析"部分：
- 初始区域：基于阈值的初始排除区域
- 置入区域：应该被包含（不排除）的区域
- 置出区域：应该被排除的额外区域
- 最终排除：初始 - 置入 + 置出

## File Structure

```
rta-exclude-strategy/
├── SKILL.md                    # 本文档
├── README_original.md          # 原始README（快速开始指南）
├── scripts/
│   ├── main.py                 # 主执行脚本
│   ├── data_preprocessing.py   # 数据预处理模块
│   ├── place_in_out_algorithm.py  # 置入置出算法模块
│   ├── report_generator.py     # 报告生成模块
│   └── requirements.txt        # Python依赖
└── resources/
    ├── 分析框架.txt            # 分析框架说明
    ├── 输出要求.txt            # 输出格式要求
    ├── 置入置出算法.txt        # 算法详细说明
    ├── cross_model.txt         # 交叉模型说明
    └── RTA排除策略报告参考.xlsx  # 报告格式参考
```

## Performance

- **数据处理速度**：~1000行/秒
- **典型分析时间**：10-30秒（取决于数据量）
- **内存占用**：~50-200MB（取决于数据大小）
- **支持数据规模**：建议≤100万行

## Author

Oliver

## Created

2026-03-30

## Version History

- 1.1.0 (2026-03-31)：添加 HTML 报告输出
  - 集成现代前端设计
  - 左侧目录导航
  - 交互式数据可视化
  - 可编辑 HTML 格式
- 1.0.0 (2026-03-30)：初始版本
  - 实现基础置入置出算法
  - 支持新老策略对比分析
  - 自动生成Excel分析报告
  - 支持自定义阈值和约束条件
