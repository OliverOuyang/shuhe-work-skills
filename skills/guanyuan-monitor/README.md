# 观远数据监控 Skill

## 功能概述

基于观远数据平台的自动化监控系统,支持:

1. **数据获取**: 通过观远数据 MCP 工具获取报表卡片数据
2. **告警规则**: 支持阈值、环比、同比等多种告警规则
3. **钉钉通知**: 自动发送告警消息到钉钉
4. **定时调度**: 支持按计划自动执行监控任务

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备配置文件

复制配置模板并修改:

```bash
cp configs/template.json configs/my_monitor.json
```

### 3. 运行监控

```bash
# 单次执行
python scripts/guanyuan_monitor/main.py --config configs/my_monitor.json --once

# 定时执行
python scripts/guanyuan_monitor/main.py --config configs/my_monitor.json
```

## 配置说明

详见 `configs/template.json` 中的注释

## 告警规则类型

- `threshold`: 阈值告警
- `change_rate`: 环比/同比变化率告警
- `range`: 区间告警

## 示例

见 `configs/examples/` 目录
