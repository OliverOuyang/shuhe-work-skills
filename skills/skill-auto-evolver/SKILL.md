---
name: skill-auto-evolver
description: Skills 自动进化器 - 数据驱动的性能分析和自动优化
triggers:
  - 自动优化
  - 性能分析
  - skill evolution
argument-hint: <command> [args]
version: 1.0.0
---

# Skill Auto Evolver

Skills 自动进化器，通过数据驱动的方式分析 skill 性能，识别优化机会，并提供自动化改进建议。

## 功能概览

### 1. 数据收集
- 透明的执行追踪（无侵入）
- 自动记录执行时间、状态、错误
- 捕获输入输出模式
- 最小性能开销（< 5%）

### 2. 性能分析
- 执行时间分布分析
- 识别性能瓶颈
- 错误模式识别
- 资源使用分析

### 3. 优化建议
- 基于数据生成优化建议
- 识别常见优化模式
- 提供具体改进方案
- 优先级排序

### 4. 实验追踪
- A/B 测试框架（基础版）
- 对���优化前后效果
- 记录实验结果
- 回滚机制

## 使用方法

### 数据收集

```bash
# 为特定 skill 启动数据收集
/skill-auto-evolver collect start <skill-name>

# 停止数据收集
/skill-auto-evolver collect stop <skill-name>

# 查看收集报告
/skill-auto-evolver collect report <skill-name>
```

### 性能分析

```bash
# 分析 skill 性能
/skill-auto-evolver analyze <skill-name>

# 识别性能瓶颈
/skill-auto-evolver analyze bottleneck <skill-name>

# 查看错误模式
/skill-auto-evolver analyze errors <skill-name>
```

### 优化建议

```bash
# 生成优化建议
/skill-auto-evolver suggest <skill-name>

# 查看详细建议
/skill-auto-evolver suggest detail <skill-name>

# 导出建议到文件
/skill-auto-evolver suggest export <skill-name> <output-file>
```

### 实验管理

```bash
# 创建优化实验
/skill-auto-evolver experiment create <skill-name> <experiment-name>

# 查看实验状态
/skill-auto-evolver experiment status <experiment-name>

# 比较实验结果
/skill-auto-evolver experiment compare <experiment-name>

# 应用优化或回滚
/skill-auto-evolver experiment apply <experiment-name>
/skill-auto-evolver experiment rollback <experiment-name>
```

## 使用示例

### 示例 1: 完整的性能优化流程

```bash
# Step 1: 启动数据收集
/skill-auto-evolver collect start my-slow-skill

# Step 2: 让 skill 运行一段时间（收集足够数据）
# ... 正常使用 skill ...

# Step 3: 停止收集并查看报告
/skill-auto-evolver collect stop my-slow-skill
/skill-auto-evolver collect report my-slow-skill

# Step 4: 分析性能瓶颈
/skill-auto-evolver analyze bottleneck my-slow-skill

# Step 5: 生成优化建议
/skill-auto-evolver suggest my-slow-skill

# Step 6: 审查建议并手动应用优化
# （查看输出的建议文件）
```

### 示例 2: A/B 测试优化效果

```bash
# 创建优化实验
/skill-auto-evolver experiment create my-skill opt-v1

# 应用优化版本并测试
/skill-auto-evolver experiment apply opt-v1

# 运行一段时间后比较结果
/skill-auto-evolver experiment compare opt-v1

# 如果效果好则保留，否则回滚
/skill-auto-evolver experiment rollback opt-v1
```

### 示例 3: 错误模式分析

```bash
# 分析错误模式
/skill-auto-evolver analyze errors problematic-skill

# 查看具体的错误类型和频率
# 输出包含：
# - 错误类型统计
# - 常见错误堆栈
# - 失败场景模式
```

## 工作原理

### 数据收集机制

使用 Python 装饰器在 skill 执行前后注入追踪代码：

```python
@track_execution(skill_name="my-skill")
def my_skill_function():
    # skill 实现
    pass
```

数据包括：
- 开始/结束时间戳
- 执行时长
- 成功/失败状态
- 错误信息（如果失败）
- 输入参数（可选）

### 性能分析算法

1. **统计分析**: 计算 P50/P95/P99 执行时间
2. **异常检测**: 识别异常慢的执行
3. **模式识别**: 发现性能与输入的关联

### 优化建议生成

基于规则库和数据分析：
- 慢 I/O 操作 → 建议缓存
- 重复计算 → 建议记忆化
- 大数据处理 → 建议分批处理
- 同步操作 → 建议异步化

## 数据存储

数据存储在 `skills/skill-auto-evolver/data/` 目录下：

- `execution_logs.db` - SQLite 数据库（执行日志）
- `experiments/` - 实验记录和结果
- `suggestions/` - 优化建议文档

## 配置

配置文件：`data/config.json`

```json
{
  "sampling_rate": 1.0,
  "retention_days": 30,
  "bottleneck_threshold_ms": 1000,
  "auto_suggest": false
}
```

- `sampling_rate`: 采样率（1.0 = 100%）
- `retention_days`: 数据保留天数
- `bottleneck_threshold_ms`: 瓶颈判定阈值（毫秒）
- `auto_suggest`: 是否自动生成建议

## 技术说明

### 依赖

- Python 3.8+
- click >= 8.0
- sqlalchemy >= 1.4
- pandas >= 1.3
- numpy >= 1.20

### 性能

- 数据收集开销: < 5%
- 分析时间: < 5秒
- 数据库大小: ~10MB/1000次执行

### 隐私

- 不收集敏感数据
- 输入参数默认不记录（可配置）
- 数据仅存储在本地

## 故障排查

### 问题：性能开销过高

```bash
# 降低采样率
# 编辑 data/config.json
# 设置 "sampling_rate": 0.1  # 仅采样 10%
```

### 问题：数据库过大

```bash
# 清理旧数据
/skill-auto-evolver collect cleanup --days 7

# 或直接删除数据库
rm data/execution_logs.db
```

### 问题：建议不准确

```bash
# 收集更多数据
/skill-auto-evolver collect start <skill> --extended

# 运行更多样化的场景
# 然后重新分析
```

## 开发和测试

```bash
# 运行测试
cd skills/skill-auto-evolver
pytest tests/

# 测试数据收集
pytest tests/test_data_collector.py

# 测试性能分析
pytest tests/test_analyzer.py
```

## 版本历史

- v1.0.0 (2026-03-31): 初始版本，MVP 功能

## 相关 Skills

- `/skill-lifecycle-manager` - Skills 生命周期管理器
- `/learner` - 从对话中提取新 skill
- `/skill` - 基础 skill 管理

## 未来计划

### P1 功能
- 机器学习驱动的优化建议
- 自动代码生成
- 更高级的 A/B 测试框架

### P2 功能
- 实时性能监控
- 告警机制
- 集成到 CI/CD 流程
