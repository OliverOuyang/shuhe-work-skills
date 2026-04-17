---
name: html-report-framework
description: "HTML 报告生成通用框架 - CSS 变量设计系统、专业组件库、ECharts 图表、Mermaid 流程图、动态居中布局、可折叠侧栏、规则驱动结论。当用户需要生成 HTML 报告、数据看板、SOP 文档、KPI dashboard 或任何自包含网页报告时使用。"
version: 3.1.0
---

# HTML 报告通用框架

## Purpose

提供 HTML 报告生成的完整工具链和最佳实践。涵盖 CSS 变量设计系统、专业级组件库、ECharts 图表渲染、动态居中布局、可折叠侧栏导航、规则驱动结论生成和 Python f-string 模板。从月报 V04 项目和 SOP 文档中心项目提炼。

## When to Activate

当用户需要创建或优化任何 HTML 格式的数据报告时激活，特别适用于：
- 数据可视化报告（ECharts 图表）
- 定期业务报告（月报、周报）
- SOP 文档 / 技术文档
- KPI dashboard
- 自包含单文件 HTML 报告

## 强制规则（MUST）

生成 HTML 报告时，**必须从 starter-template 复制，禁止从零手写**：

1. **读取骨架**：`Read` 文件 `resources/starter-template.html`（本 skill 目录下）
2. **复制全文**：将完整 HTML 复制为新文件（保留所有 CSS/JS/布局基础设施）
3. **替换占位符**：搜索所有 `__PLACEHOLDER__` 并替换为实际内容
4. **添加内容**：在 Section 2+ 区域添加详细分析，使用 `golden-template.html` 中的组件作为参考
5. **添加图表**：在 `<script>` 区域的 `chartConfigs` 中定义 ECharts 配置

### 禁止行为
- 禁止从空白 `<!DOCTYPE html>` 开始手写 CSS/JS
- 禁止修改 `:root` CSS 变量（除非用户明确要求换主题）
- 禁止删除侧栏、滚动高亮、自动 resize 等基础设施代码
- 禁止使用 Chart.js（已废弃，统一使用 ECharts 5.5.0）

### 文件说明
| 文件 | 用途 |
|------|------|
| `resources/starter-template.html` | **空白骨架** — 复制此文件开始新报告 |
| `resources/golden-template.html` | **完整示例** — 查看组件的实际使用方式 |

### 生成质量要求
- **MUST-CONCLUSION**: 每个 ECharts 图表的**同一 subsection 内**必须有 `blockquote.conclusion` 或 `callout` 解读数据含义。图表不能孤立存在。
- **SHOULD-VISUAL**: 每个 Section 至少包含 1 个可视化组件（Mermaid / ECharts / flow-diagram / table / info-card）。纯文字 Section 应避免。
- **SHOULD-MERMAID**: 当报告涉及流程、链路、排期时，应使用 Mermaid 图。纯数据对比类报告可豁免。

### Quality Gate（交付前必须执行）
生成完成后，运行验证脚本：
```bash
python resources/validate_report.py output.html
```
必须全部 PASS 才能交付。验证项包括：
1. 无 `__PLACEHOLDER__` 残留
2. 结论数 ≥ 图表数（每个图表有对应结论）
3. 无 UTF-8 乱码
4. 侧栏存在
5. ECharts CDN 存在
6. 每 Section 至少 1 个可视化组件
7. 每个 conclusion-item 有支撑图表（`details.chart-detail`）
8. 使用 Mermaid 时 CDN 已加载

## 报告结构规范

Section 1（项目概述）的结构是**强制**的，所有报告必须包含：

```
Section 1: 项目概述 (Executive Summary)
├── 1.1 项目背景
│   ├── callout.info — 项目/周期/口径/范围/粒度/目标
│   ├── pre.mermaid — 分析框架流程图（主线 → 子维度 → 核心指标）
│   └── table — 核心问题列表（#/问题/对应结论/详细分析跳转）
├── 1.2 核心结论 — 每个 conclusion-item 带折叠支撑图表（details.chart-detail）
└── 1.3 下一步行动 — 紧急/重点/持续 三级优先级（callout.danger/warning/info）
```

### 1.1 项目背景必备组件

1. **项目信息 callout**（`callout.info`）：包含项目名称、分析周期、指标口径、数据范围、分析粒度、分析目标。字段用 `<strong>` 标签加粗标注。
2. **分析框架 Mermaid 图**（`pre.mermaid`）：替代静态 def-card 卡片组。用 `flowchart TD` 展示分析主线分支、子维度节点、汇聚到核心指标。节点使用语义化配色（`style` 指令）。
3. **核心问题导航表**（`<table>`）：列 = `#` / `核心问题` / `对应结论` / `详细分析`。"对应结论"列链接到 `#sub-conclusions`（有结论时用颜色区分严重程度），"详细分析"列链接到具体 section/subsection 的 `id`。无对应结论的问题用 `—` 占位。

### 1.2 核心结论必备规则

- 每个 conclusion-item **必须**包含 `<details class="collapsible chart-detail">` 折叠图表
- 图表通过 `chartConfigs` 对象懒加载（toggle 时初始化 ECharts）
- bullet 颜色语义：`success`=绿色验证通过、`warning`=橙色需关注、`danger`=红色需行动

**设计原则**：读者看完 Section 1 就能掌握全貌（做什么 → 什么结论 → 下一步）。Section 2+ 是对 Section 1 的展开和深入。

## 质量原则

生成 HTML 应达到"专业内部产品文档"水准：

1. **信息可视化优先**：决策逻辑用流程图、数据对比用颜色编码表格、步骤用带连接线的编号——能画出来就不要写出来
2. **渐进式披露**：概述（流程图+callout）→ 细节（定义卡片+公式块）→ 操作（步骤列表+平台tab）→ 参考（信息卡+字段表）
3. **颜色即语义**：蓝色=标准流程/信息、绿色=通过/推荐、红色=关键/排除、黄色=决策点/警告、灰色=辅助/已废弃
4. **双重编码**：关键信息同时用颜色和文字标注（如红色背景 + "低" badge）
5. **每个 section 至少一个非文字组件**（表格/流程图/卡片/callout），避免大段纯文字

## Common Issues & Fixes

详细代码示例见 `ARCHITECTURE.md`。

| # | 问题 | 一行修复 |
|---|------|---------|
| 1 | 图表顶部被标题遮挡 | `grid.top` 从 20 改为 45 |
| 2 | 页面内容偏左不居中 | 改用 `margin-left: max(260px, calc((100vw - 1200px) / 2))` |
| 3 | 微小值精度丢失（CVR 全显示 0.0） | 对极小值改用 `to_js_array(series * 100, 4)` |
| 4 | f-string 中 `NameError` | 所有变量在 f-string 之前预计算，不在 f-string 内调用函数 |
| 5 | 中文乱码（U+FFFD） | `grep "?" file.py` 逐一替换为正确中文 |
| 6 | `KeyError: 'month'` | 用 `get_month_col(df)` 兼容 `month` / `date_month` 两种字段名 |
| 7 | 折叠侧栏后图表不自适应 | `toggleSidebar()` 末尾加 `setTimeout(() => window.dispatchEvent(new Event('resize')), 350)` |
| 8 | 图表与结论精度矛盾 | 统一所有百分比/比率数据输出为 2 位小数 |
| 9 | JS 选择器与 HTML class 不匹配 | HTML class 重命名时全局搜索 JS/CSS 同步更新 |
| 10 | 死代码 — JS 引用不存在的 DOM | HTML 结构变更后 grep 清理所有孤立 `getElementById` 引用 |
| 11 | Mermaid 图表不渲染 | 确认 CDN `mermaid@10`、`startOnLoad: true`、检查语法缩进 |
| 12 | Mermaid 主题与页面风格不一致 | 用 `theme: 'base'` + 自定义 `themeVariables` 匹配 CSS `:root` 变量 |

## Golden Template

完整参考模板见 `resources/golden-template.html`，包含所有组件的实际使用示例：
- CSS 变量设计系统 + deepBlue 主题
- 可折叠侧栏 + 滚动高亮导航
- ECharts 图表（堆叠柱状图+折线、双折线、柱状图+多折线）
- Mermaid 图（flowchart、sequenceDiagram、gantt）
- 全部组件（callout、metric-card、info-card、flow-diagram、chain-pipeline、table、formula-block、def-card、timeline、collapsible、checklist）
- 响应式布局 + 打印样式
- HTML 导出功能

## Related Skills

- `/monthly-report-html-generator` - 月报 HTML 专用生成器
- `/dp-explorer` - Dataphin 数据探索
- `/document-skills:xlsx` - Excel 数据处理
- `/document-skills:frontend-design` - 前端设计优化

## Notes

- **ECharts 5.5.0**：CDN 双源加载（bootcdn + jsdelivr fallback），替代 Chart.js
- **单文件输出**：HTML 自包含所有 CSS + JS + 数据，无外部依赖文件
- **Python f-string**：数据直接嵌入 JS 数组，无需中间 JSON 文件
- **规则驱动结论**：基于环比计算自动生成，非 AI 生成
- **Windows 兼容**：`encoding="utf-8"` 写入，避免 GBK 终端乱码
- **组件参考**：所有核心模块的完整 CSS/JS 代码见 `ARCHITECTURE.md`
