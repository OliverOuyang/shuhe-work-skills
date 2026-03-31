# visualization.py 使用说明

## 概述

`visualization.py` 模块为 RTA 排除策略分析提供交互式 HTML 图表生成功能。使用纯 HTML/CSS/SVG 实现,不依赖外部 JavaScript 库。

## 主要功能

### 1. 二维热力图 (`generate_heatmap_html`)

生成 V8 x V9RN 二维交叉表热力图,用于可视化不同维度组合的指标表现。

**参数:**
- `df_combined`: 全量数据 DataFrame
- `exclude_region`: 排除区域列表,格式为 `[(V8, V9RN), ...]`
- `metric`: 显示指标,可选值:
  - `'spr'`: 安全过件率(默认)
  - `'count'`: 样本量
  - `'amt'`: 交易金额

**返回:**
- HTML 字符串,包含完整的热力图表格和图例

**特性:**
- 颜色渐变(低值红色 → 高值绿色)
- 鼠标悬停显示详细数值
- 红色边框标记排除区域
- 自适应单元格大小

**示例:**
```python
from visualization import generate_heatmap_html

html = generate_heatmap_html(
    df_combined=df,
    exclude_region=[('01Q', '01Q'), ('01Q', '02Q')],
    metric='spr'
)
```

---

### 2. 指标对比柱状图 (`generate_comparison_chart_html`)

生成新老策略关键指标的并排对比柱状图。

**参数:**
- `old_metrics`: 老策略指标字典,格式:
  ```python
  {
      '排除交易占比': 0.15,
      '排除客群安全过件率': 0.08,
      '保留客群安全过件率': 0.65,
      '保留客群CPS': 0.0234
  }
  ```
- `new_metrics`: 新策略指标字典,格式同上
- `metric_names`: 可选,指定要显示的指标名称列表

**返回:**
- HTML/SVG 字符串,包含对比柱状图

**特性:**
- 灰色柱(旧策略) vs 绿色柱(新策略)
- 自动格式化数值(百分比 vs 小数)
- 鼠标悬停显示精确值
- 图例说明

**示例:**
```python
from visualization import generate_comparison_chart_html

old = {'排除交易占比': 0.15, '安全过件率': 0.65}
new = {'排除交易占比': 0.18, '安全过件率': 0.68}

html = generate_comparison_chart_html(old, new)
```

---

### 3. 交叉分析矩阵 (`generate_cross_analysis_matrix_html`)

生成 2x2 置入置出分析矩阵,展示四个客群的表现差异。

**参数:**
- `groups_data`: 四个客群的数据字典,格式:
  ```python
  {
      'both_exclude': {'amt_ratio': 0.10, 'spr': 0.08, 'cps': 0.025},
      'place_in': {'amt_ratio': 0.05, 'spr': 0.12, 'cps': 0.022},
      'place_out': {'amt_ratio': 0.08, 'spr': 0.07, 'cps': 0.028},
      'both_keep': {'amt_ratio': 0.77, 'spr': 0.65, 'cps': 0.020}
  }
  ```

**返回:**
- HTML 字符串,包含 2x2 矩阵表格

**特性:**
- 颜色编码区分四个客群
- 清晰标注置入/置出客群
- 显示三项关键指标(交易占比、安全过件率、CPS)
- 响应式布局

**客群说明:**
- `both_exclude`: 两策略都排除
- `place_in`: 置入客群(新策略保留,旧策略误伤)
- `place_out`: 置出客群(新策略新增排除)
- `both_keep`: 两策略都保留

**示例:**
```python
from visualization import calculate_groups_data, generate_cross_analysis_matrix_html

# 计算四个客群数据
groups_data = calculate_groups_data(
    df_ctrl=df_ctrl,
    exclude_region=[('01Q', '01Q'), ('01Q', '02Q')],
    old_exclude_v8=['01Q', '02Q']
)

# 生成矩阵
html = generate_cross_analysis_matrix_html(groups_data)
```

---

### 4. 计算客群数据 (`calculate_groups_data`)

从对照组数据计算四个客群的指标,供交叉分析矩阵使用。

**参数:**
- `df_ctrl`: 对照组 DataFrame
- `exclude_region`: 新策略排除区域
- `old_exclude_v8`: 老策略排除规则列表

**返回:**
- 字典,包含四个客群的指标数据

**计算指标:**
- `amt_ratio`: 交易占比
- `spr`: 安全过件率
- `cps`: CPS

---

### 5. 完整 HTML 报告 (`generate_full_html_report`)

生成包含所有可视化图表的完整 HTML 报告文件。

**参数:**
- `result`: 算法结果字典(来自 `place_in_out_algorithm.py`)
- `old_exclude_rule`: 老策略排除规则列表
- `output_path`: 可选,输出目录路径

**返回:**
- 生成的 HTML 文件路径

**报告包含:**
1. 新老策略指标对比柱状图
2. V8 x V9RN 二维热力图
3. 置入置出分析矩阵
4. 专业的样式和布局

**示例:**
```python
from visualization import generate_full_html_report

file_path = generate_full_html_report(
    result=algorithm_result,
    old_exclude_rule=['01q', '02q', '03q'],
    output_path='./output'
)

print(f"HTML报告已生成: {file_path}")
```

---

## 集成到现有工作流

### 在 main.py 中添加 HTML 报告生成

```python
# 在 main.py 中
from visualization import generate_full_html_report

# 在生成 Excel 报告后添加
html_path = generate_full_html_report(
    result,
    old_exclude_rule,
    output_path=args.output_path
)

print(f"\nHTML 报告: {html_path}")
```

### 单独使用可视化函数

```python
from visualization import (
    generate_heatmap_html,
    generate_comparison_chart_html
)

# 生成热力图并保存
heatmap_html = generate_heatmap_html(df, exclude_region)

with open('heatmap.html', 'w', encoding='utf-8') as f:
    f.write(f'''
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"></head>
    <body>{heatmap_html}</body>
    </html>
    ''')
```

---

## 技术实现

### 技术栈
- **纯 HTML/CSS**: 所有样式和布局
- **SVG**: 柱状图绘制
- **原生 JavaScript**: 无(仅使用 CSS 实现交互)

### 优势
1. **无外部依赖**: 不依赖 D3.js、Plotly 等库
2. **轻量级**: 生成的 HTML 文件体积小
3. **兼容性好**: 可在任何现代浏览器中打开
4. **易于分享**: 单个 HTML 文件包含所有内容

### 颜色方案
- **热力图**: 红绿渐变(低值红色 → 高值绿色)
- **排除标记**: 浅红色背景 + 红色边框
- **柱状图**: 灰色(旧策略) vs 绿色(新策略)
- **矩阵**: 四种不同颜色区分客群

---

## 测试

运行测试脚本验证所有功能:

```bash
cd scripts
python test_visualization.py
```

测试覆盖:
1. 热力图 HTML 生成
2. 对比柱状图生成
3. 交叉分析矩阵生成
4. 客群数据计算准确性

---

## 数据要求

### DataFrame 必需字段
- `V8_Q`: V8 分位(格式: '01Q', '02Q', ...)
- `V9RN_Q`: V9RN 分位(格式: '01Q', '02Q', ...)
- `t3_ato`: 申完数
- `t3_safe_adt`: 安全通过数
- `t3_loan_amt`: 交易金额
- `cost`: 成本

### 排除区域格式
```python
exclude_region = [
    ('01Q', '01Q'),  # (V8分位, V9RN分位)
    ('01Q', '02Q'),
    ('02Q', '01Q')
]
```

---

## 注意事项

1. **编码**: 生成的 HTML 使用 UTF-8 编码,确保正确显示中文
2. **数值格式化**:
   - 小于 1 的值自动显示为百分比
   - 大于等于 1 的值保留 4 位小数
3. **浏览器兼容性**: 建议使用 Chrome/Edge/Firefox 等现代浏览器
4. **性能**: 热力图最多支持 12x12=144 个单元格,性能良好

---

## 版本历史

**v1.0** (2024-03-31)
- 实现三种核心可视化:热力图、对比图、交叉矩阵
- 纯 HTML/CSS/SVG 实现,无外部依赖
- 完整的测试覆盖
