---
name: skill-lifecycle-manager
description: Skills 生命周期管理器 - 版本管理、依赖检查、使用统计和健康报告
triggers:
  - skill管理
  - 版本管理
  - lifecycle
argument-hint: <command> [args]
version: 1.0.0
---

# Skill Lifecycle Manager

Skills 生命周期管理器，提供版本管理、依赖检查、使用统计和健康报告功能。

## 功能概览

### 1. 版本管理
- 查看 skills 版本信息
- 语义化版本升级（major/minor/patch）
- 版本历史追踪
- 自动生成 CHANGELOG

### 2. 依赖管理
- 解析和检查 Python 依赖（requirements.txt）
- 解析和检查 MCP 依赖（package.json）
- 检测依赖冲突
- 生成依赖报告

### 3. 使用统计
- 记录 skill 调用次数
- 统计执行时间
- 追踪成功率和失败率
- 生成使用趋势报告

### 4. 健康报告
- 生成 Skills 库健康报告
- 识别过时或未使用的 skills
- 提供改进建议
- 导出为 Markdown 格式

## 使用方法

### 版本管理

```bash
# 查看所有 skills 版本
/skill-lifecycle-manager version list

# 查看特定 skill 版本信息
/skill-lifecycle-manager version info <skill-name>

# 升级版本
/skill-lifecycle-manager version bump <skill-name> <major|minor|patch>
```

### 依赖管理

```bash
# 检查所有依赖
/skill-lifecycle-manager deps check

# 查看特定 skill 的依赖
/skill-lifecycle-manager deps show <skill-name>

# 检测依赖冲突
/skill-lifecycle-manager deps conflicts
```

### 使用统计

```bash
# 查看统计摘要
/skill-lifecycle-manager stats summary

# 查看特定 skill 统计
/skill-lifecycle-manager stats show <skill-name>

# 导出统计数据
/skill-lifecycle-manager stats export <output-file>
```

### 健康报告

```bash
# 生成完整健康报告
/skill-lifecycle-manager health report

# 查看 skill 健康评分
/skill-lifecycle-manager health score <skill-name>

# 获取改进建议
/skill-lifecycle-manager health suggest
```

## 使用示例

### 示例 1: 检查依赖并生成报告

```bash
# 1. 检查所有依赖
/skill-lifecycle-manager deps check

# 2. 如果发现问题，查看详情
/skill-lifecycle-manager deps show <problematic-skill>

# 3. 生成依赖报告
/skill-lifecycle-manager deps conflicts
```

### 示例 2: 版本升级工作流

```bash
# 1. 查看当前版本
/skill-lifecycle-manager version info my-skill

# 2. 升级补丁版本
/skill-lifecycle-manager version bump my-skill patch

# 3. 验证版本已更新
/skill-lifecycle-manager version info my-skill
```

### 示例 3: 生成健康报告

```bash
# 生成完整报告
/skill-lifecycle-manager health report

# 查看输出的 Markdown 文件
# 报告位置: data/health-report-YYYYMMDD.md
```

## 数据存储

所有数据存储在 `skills/skill-lifecycle-manager/data/` 目录下：

- `usage_stats.db` - SQLite 数据库（使用统计）
- `health-report-*.md` - 健康报告（Markdown 格式）
- `dependency-report.json` - 依赖分析结果

## 配置

可以通过配置文件自定义行为（可选）：

```json
{
  "stats_retention_days": 90,
  "health_score_threshold": 70,
  "auto_backup": true
}
```

配置文件位置：`data/config.json`

## 技术说明

### 依赖

- Python 3.8+
- click >= 8.0
- sqlalchemy >= 1.4
- pydantic >= 1.8

### 性能

- 统计收集开销: < 5%
- 依赖检查时间: < 3秒
- 健康报告生成: < 10秒

## 故障排查

### 问题：数据库文件损坏

```bash
# 删除并重新初始化数据库
rm data/usage_stats.db
/skill-lifecycle-manager stats summary
```

### 问题：版本信息不准确

```bash
# 清理缓存并重新扫描
/skill-lifecycle-manager version list --refresh
```

## 开发和测试

```bash
# 运行单元测试
cd skills/skill-lifecycle-manager
pytest tests/

# 运行特定测试
pytest tests/test_version_manager.py

# 查看覆盖率
pytest --cov=scripts tests/
```

## 版本历史

- v1.0.0 (2026-03-31): 初始版本，包含核心功能

## 相关 Skills

- `/skill` - 基础 skill 管理
- `/learner` - 从对话中提取新 skill
- `/skill-auto-evolver` - Skills 自动进化器
