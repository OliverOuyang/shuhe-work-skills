# RTA排除策略分析 Skill - 使用指南

## 概述

RTA（Real-Time Advertising）排除策略分析工具，基于V8和V9RN两个模型的二维交叉分析，通过智能置入置出算法自动生成排除策略，并输出完整的Excel分析报告。

本Skill包装层提供了友好的接口，封装了原始实现的复杂性，支持：
- ✅ 参数验证和错误处理
- ✅ 相对路径和绝对路径自动处理
- ✅ 友好的进度反馈
- ✅ 结构化的结果输出
- ✅ 配置验证功能

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基本使用

最简单的用法（使用默认参数）：

```bash
/rta-exclude-strategy --data-path=data.csv --ctrl-group=ctrl
```

### 3. 自定义参数

```bash
/rta-exclude-strategy \
  --data-path=data.xlsx \
  --ctrl-group=control \
  --output-dir=reports/ \
  --old-exclude="01q,02q,03q" \
  --spr-threshold=0.08 \
  --max-exclude=0.15
```

## 参数说明

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--data-path` | 数据文件路径（CSV或Excel） | `data.csv` |
| `--ctrl-group` | 对照组标识值 | `ctrl` |

### 可选参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--output-dir` | 输出目录 | 当前目录 |
| `--old-exclude` | 老策略排除规则（逗号分隔） | `01q-10q` |
| `--spr-threshold` | 安全过件率阈值 | `0.10` |
| `--max-exclude` | 最大排除交易占比 | `0.20` |
| `--verbose` | 是否显示详细日志 | `true` |

## Python API 使用

### 基本用法

```python
from scripts.rta_exclude import run_rta_exclude_strategy

result = run_rta_exclude_strategy(
    data_path="data.csv",
    ctrl_group_value="ctrl"
)

if result["success"]:
    print(f"分析完成！报告: {result['output_file']}")
    print(f"最终排除: {result['summary']['exclude_region']} 个格子")
else:
    print(f"分析失败: {result['error']}")
```

### 高级用法

```python
from scripts.rta_exclude import run_rta_exclude_strategy
from scripts.rta_exclude.skill_wrapper import validate_config

# 步骤1：验证配置
validation = validate_config(
    data_path="data.csv",
    ctrl_group_value="ctrl",
    output_dir="reports/"
)

if not validation["valid"]:
    print("配置错误:")
    for error in validation["errors"]:
        print(f"  - {error}")
    exit(1)

# 步骤2：执行分析
result = run_rta_exclude_strategy(
    data_path="data.csv",
    ctrl_group_value="ctrl",
    output_dir="reports/",
    old_exclude_rule=["01q", "02q", "03q"],  # 可以传列表
    spr_threshold=0.08,
    max_exclude_ratio=0.15,
    verbose=True
)

# 步骤3：处理结果
if result["success"]:
    # 成功
    summary = result["summary"]
    print(f"\n分析完成！")
    print(f"  报告: {result['output_file']}")
    print(f"  初始圈选: {summary['initial_region']} 个格子")
    print(f"  置入区域: {summary['place_in_region']} 个格子")
    print(f"  置出区域: {summary['place_out_region']} 个格子")
    print(f"  最终排除: {summary['exclude_region']} 个格子")
else:
    # 失败
    print(f"分析失败: {result['error']}")
```

## 数据要求

### 必需字段

| 字段名 | 说明 | 格式 |
|--------|------|------|
| `V8` 或 `v8_ato_safe_bin_req` | V8模型分组 | `01q`-`20q` |
| `V9RN` 或 `merge_ato_safe_v9_rn_bin_req` | V9RN模型分组 | `01q`-`20q` |
| `group` 或 `act_type` | 实验分组标识 | 包含对照组标识值 |
| `expo_cnt` | 曝光数 | 整数 |
| `cost` | 成本 | 数值 |
| `t3_ato` | T3申完数 | 整数 |
| `t3_safe_adt` | T3安全授信数 | 整数 |
| `t3_loan_amt` | T3交易金额 | 数值 |

### 数据示例

```csv
V8,V9RN,group,expo_cnt,cost,t3_ato,t3_safe_adt,t3_loan_amt
01q,01q,ctrl,1000,5000,500,450,100000
01q,02q,ctrl,1200,6000,600,540,120000
...
```

## 输出说明

### Excel 报告结构

生成的报告文件名格式：`RTA排除策略分析报告_YYYYMMDD_HHMMSS.xlsx`

报告包含三个主要部分：

#### 一、核心结论
- 新老策略关键指标对比表
- 策略优劣评价

#### 二、排除策略制定
1. 排除策略现状（老策略表格）
2. 排除策略制定
   - 新老策略指标差异对比
   - ��策略排除规则（二维热力图）

#### 三、合理性评估
1. 置入置出合理性分析
2. 交叉表展示
   - 交易占比交叉表
   - 安全过件率交叉表
   - CPS交叉表

### Python 返回值

```python
{
    "success": bool,           # 是否执行成功
    "output_file": str,        # 输出文件绝对路径
    "summary": {
        "initial_region": int,    # 初始圈选格子数
        "place_in_region": int,   # 置入区域格子数
        "place_out_region": int,  # 置出区域格子数
        "exclude_region": int,    # 最终排除格子数
    },
    "error": str | None        # 错误信息（如果失败）
}
```

## 常见问题

### Q1: 相对路径和绝对路径如何处理？

A: Skill wrapper会自动处理路径：
- 相对路径自动转换为相对于当前工作目录的绝对路径
- 绝对路径直接使用
- 输出路径也支持相对路径

```python
# 以下都是有效的
run_rta_exclude_strategy(data_path="data.csv", ...)           # 相对路径
run_rta_exclude_strategy(data_path="./data/data.csv", ...)   # 相对路径
run_rta_exclude_strategy(data_path="C:/path/data.csv", ...)  # 绝对路径
```

### Q2: 如何指定老策略排除规则？

A: 支持两种格式：

```python
# 格式1：逗号分隔字符串
run_rta_exclude_strategy(
    ...,
    old_exclude_rule="01q,02q,03q"
)

# 格式2：Python列表
run_rta_exclude_strategy(
    ...,
    old_exclude_rule=["01q", "02q", "03q"]
)
```

### Q3: 如何处理错误？

A: Skill wrapper 提供了完善的错误处理：

```python
result = run_rta_exclude_strategy(...)

if not result["success"]:
    # 分析失败时，error字段包含错误信息
    if "文件未找到" in result["error"]:
        print("请检查数据文件路径")
    elif "参数错误" in result["error"]:
        print("请检查参数设置")
    elif "模块导入失败" in result["error"]:
        print("请检查依赖安装")
```

### Q4: 如何验证配置是否正确？

A: 使用 `validate_config` 函数预先验证：

```python
from scripts.rta_exclude.skill_wrapper import validate_config

validation = validate_config(
    data_path="data.csv",
    ctrl_group_value="ctrl",
    output_dir="reports/"
)

print(f"配置有效: {validation['valid']}")
print(f"数据文件存在: {validation['data_file_exists']}")
print(f"输出目录可写: {validation['output_dir_writable']}")

if validation['errors']:
    print("错误:")
    for error in validation['errors']:
        print(f"  - {error}")
```

### Q5: 如何关闭详细日志？

A: 设置 `verbose=False`：

```python
result = run_rta_exclude_strategy(
    data_path="data.csv",
    ctrl_group_value="ctrl",
    verbose=False  # 关闭详细日志
)
```

## 测试

运行测试脚本验证 Skill wrapper 功能：

```bash
python test_wrapper.py
```

测试包括：
- 配置验证功能
- 参数处理和转换
- 错误处理机制

## 项目结构

```
rta-exclude-strategy/
├── SKILL.md                          # 完整文档
├── README.md                         # 本文档（使用指南）
├── README_original.md                # 原始实现说明
├── requirements.txt                  # Python依赖
├── test_wrapper.py                   # Wrapper测试脚本
├── scripts/
│   ├── rta_exclude/                  # Skill封装层
│   │   ├── __init__.py              # 模块入口
│   │   └── skill_wrapper.py         # 核心封装逻辑
│   ├── data_preprocessing.py        # 数据预处理模块
│   ├── place_in_out_algorithm.py    # 置入置出算法
│   ├── report_generator.py          # 报告生成模块
│   └── main.py                      # 原始CLI入口
└── resources/
    ├── 分析框架.txt
    ├── 输出要求.txt
    └── 置入置出算法.txt
```

## 技术细节

### Skill Wrapper 功能

1. **参数验证**：检查文件存在性、格式、权限等
2. **路径处理**：自动转换相对路径为绝对路径
3. **错误处理**：捕获并友好地呈现错误信息
4. **进度反馈**：可选的详细执行日志
5. **结果摘要**：结构化的分析结果输出

### 与原始实现的关系

- Skill wrapper 封装了原始 `main.py` 的功能
- 保留了原始实现的所有核心逻辑
- 添加了更友好的接口和错误处理
- 原始实现的 CLI 仍然可以直接使用

## 维护和更新

### 修改核心逻辑

如需修改核心分析逻辑，请编辑以下文件：
- `scripts/data_preprocessing.py` - 数据预处理
- `scripts/place_in_out_algorithm.py` - 置入置出算法
- `scripts/report_generator.py` - 报告生成

### 修改接口层

如需修改接口或添加新功能，请编辑：
- `scripts/rta_exclude/skill_wrapper.py`

修改后运行测试确保兼容性：
```bash
python test_wrapper.py
```

## 支持

如有问题或建议，请联系数禾DS团队。

---

**版本**: 1.0.0
**创建日期**: 2026-03-30
**作者**: 数禾DS团队
