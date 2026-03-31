# SQL Optimizer Skill

优化和清理Hive/MaxCompute SQL查询的智能技能。

## 功能特性

- ✅ 移除重复查询和冗余注释
- ✅ 添加结构化文档(文件头、字段说明、术语解释)
- ✅ 改进代码格式和可读性
- ✅ 自动语法验证(Hive/MaxCompute)
- ✅ 保持业务逻辑完全不变

## 触发方式

当用户提到以下关键词时自动触发:
- "优化SQL" / "optimize SQL"
- "清理SQL" / "clean SQL"
- "格式化SQL" / "format SQL"
- "添加SQL注释" / "add comments"
- "重构SQL" / "refactor SQL"

## 使用示例

```
用户: 帮我优化一下这个SQL,加上注释
Claude: [自动调用sql-optimizer skill]
```

## 优化效果

### 优化前
```sql
select a.date_key, b.platform,
sum(a.user_count) as cnt -- 用户数
from table1 a
LEFT JOIN table2 b on a.id=b.id
where a.ds='${bizdate}'
group BY a.date_key, b.platform
```

### 优化后
```sql
/*******************************************************************************
 * Query Name: Daily User Count by Platform
 * Purpose: Calculate daily active users grouped by platform
 * Granularity: date + platform
 * Data Range: Current business date
 * Update Frequency: Daily
 ******************************************************************************/

SELECT
    -- ==================== Dimensions ====================
    a.date_key,                    -- Date
    b.platform,                    -- Platform type

    -- ==================== Metrics ====================
    SUM(a.user_count) AS cnt      -- Total user count

FROM
    table1 a

    -- Join platform dimension
    LEFT JOIN table2 b
        ON a.id = b.id

WHERE
    -- Partition filter
    a.ds = '${bizdate}'

GROUP BY
    a.date_key,
    b.platform
;
```

## 技术实现

- 语法验证脚本: `scripts/validate_sql.py`
- 支持的SQL方言: Hive, MaxCompute
- 编码处理: UTF-8 + Windows兼容

## 版本历史

- v1.0 (2026-03-31): 初始版本
  - 基础SQL优化功能
  - Hive/MaxCompute语法验证
  - 结构化注释模板
