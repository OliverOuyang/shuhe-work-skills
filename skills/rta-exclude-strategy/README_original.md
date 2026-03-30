# RTA排除策略分析Skill - 快速开始

## 简介

本skill用于RTA（Real-Time Advertising）排除策略分析，基于V8和V9RN两个模型的二维交叉分析，通过置入置出算法自动生成排除策略，并输出完整的Excel分析报告。

## 核心功能

- **自动数据预处理**：处理缺失值、类型转换、模型分组聚合
- **智能置入置出算法**：基于安全过件率阈值的排除区域识别
- **新老策略对比**：全面对比分析新老策略的效果
- **Excel报告生成**：生成符合企业规范的分析报告

## 安装依赖

```bash
pip install pandas numpy openpyxl
```

或使用requirements.txt：

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 准备数据

确保数据文件包含以下必需字段：
- `V8`：V8模型分组（01q-20q格式）
- `V9RN`：V9RN模型分组（01q-20q格式）
- `group`：实验分组标识
- `expo_cnt`：曝光数
- `cost`：成本
- `t3_ato`：T3申完数
- `t3_safe_adt`：T3安全授信数
- `t3_loan_amt`：T3交易金额

### 2. 基本使用

```bash
python main.py --data_path data.csv --ctrl_group_value ctrl
```

### 3. 自定义参数

```bash
python main.py \
  --data_path data.xlsx \
  --ctrl_group_value control \
  --old_exclude_rule "01q,02q,03q" \
  --spr_threshold 0.08 \
  --max_exclude_ratio 0.15 \
  --output_path ./reports/
```

## 参数说明

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--data_path` | 数据文件路径 | `data.csv` |
| `--ctrl_group_value` | 对照组标识值 | `ctrl` |

### 可选参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--old_exclude_rule` | 老策略排除规则（逗号分隔） | `01q-10q` |
| `--spr_threshold` | 安全过件率阈值 | `0.10` |
| `--max_exclude_ratio` | 最大排除交易占比 | `0.20` |
| `--output_path` | 输出文件路径 | `.` |

## 输出说明

程序会生成一个Excel报告，包含三个主要部分：

### 一、核心结论
- 新老策略关键指标对比
- 策略优劣评价

### 二、排除策略制定
1. 排除策略现状（老策略表格）
2. 排除策略制定
   - 新老策略指标差异对比
   - 新策略排除规则（二维热力图）

### 三、合理性评估
1. 置入置出合理性分析
2. 交叉表展示
   - 交易占比交叉表
   - 安全过件率交叉表
   - CPS交叉表

## 常见问题

### Q1: 数据中没有UNK分组怎么办？
A: 算法会自动处理，不影响分析结果。

### Q2: 如何指定老策略排除规则？
A: 使用`--old_exclude_rule`参数，格式为逗号分隔的分组列表，如`"01q,02q,03q"`。

### Q3: 排除交易占比超过20%怎么办？
A: 算法会自动尝试调整阈值。如果仍无法满足约束，会在报告中标注风险提示。

### Q4: 报告生成失败怎么办？
A: 检查以下几点：
- 输出路径是否存在且有写入权限
- 文件是否被其他程序打开
- 查看错误日志获取详细信息

### Q5: 模型分组格式不正确怎么办？
A: 确保模型分组格式为`01q-20q`（小写q），程序会自动聚合为`01Q-12Q`。

## 算法说明

详细算法说明请参考：
- [skill.md](skill.md) - 完整的skill文档
- [resources/置入置出算法.txt](resources/置入置出算法.txt) - 算法详细说明

## 文件结构

```
rta_exclude_strategy/
├── skill.md                    # Skill完整文档
├── README.md                   # 本文档
├── main.py                     # 主执行脚本
├── data_preprocessing.py       # 数据预处理模块
├── place_in_out_algorithm.py   # 置入置出算法模块
├── report_generator.py         # 报告生成模块
└── resources/
    ├── 分析框架.txt            # 分析框架说明
    ├── 输出要求.txt            # 输出格式要求
    └── 置入置出算法.txt        # 算法详细说明
```

## 技术支持

如有问题或建议，请联系相关负责人。
