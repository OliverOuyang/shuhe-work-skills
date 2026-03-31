# sh_dp_mcp 边界条件测试报告

**版本**: 1.0
**日期**: 2026-03-31
**测试工具**: sh_dp_mcp (数据平台即席查询工具)
**目标**: 验证数据平台 SQL 查询接口在边界条件下的表现、错误处理和限制约束

---

## 测试环境

| 项目 | 说明 |
|------|------|
| 测试工具 | mcp__sh_dp_mcp__submit_dp_query / mcp__sh_dp_mcp__get_dp_query_status |
| 数据平台 | 数禾数据平台(DP) |
| 查询类型 | SELECT 语句（仅支持 SELECT，不支持 DDL/DML） |
| 执行模式 | 异步查询，通过 taskId 轮询获取结果 |
| 网络环境 | 企业内网 |

---

## 测试场景设计

### 场景 1: 简单查询 - 少量数据

**目标**: 验证基础查询功能和返回数据结构

**测试用例**:
```sql
SELECT 'test' as col1, 123 as col2
```

**预期行为**:
- 返回状态: `SUCCESS`
- 数据行数: 1
- 字段结构:
  ```json
  {
    "columns": ["col1", "col2"],
    "rows": [["test", 123]],
    "rowCount": 1
  }
  ```
- 返回时间: < 1 秒

**验证方式**:
1. 调用 `submit_dp_query(sql="SELECT 'test' as col1, 123 as col2")`
2. 获取 taskId
3. 调用 `get_dp_query_status(taskId=...)` 轮询直到完成
4. 验证返回字段和数据类型是否正确

**可能的问题**:
- 返回的数据类型是否保持原类型（字符串、整数、浮点数等）
- 是否支持 NULL 值返回

---

### 场景 2: 查询不存在的表

**目标**: 验证错误处理和错误信息的可读性

**测试用例**:
```sql
SELECT * FROM nonexistent_table_12345
```

**预期行为**:
- 返回状态: `FAILED` 或 `ERROR`
- 错误消息格式: 应包含表明原因的清晰信息
  ```json
  {
    "taskId": "...",
    "queryStatus": "FAILED",
    "errorMessage": "Table not found: nonexistent_table_12345",
    "errorCode": "TABLE_NOT_FOUND"
  }
  ```
- 返回时间: < 2 秒

**验证方式**:
1. 调用 `submit_dp_query(sql="SELECT * FROM nonexistent_table_12345")`
2. 轮询获取状态直到完成（FAILED）
3. 验证错误消息的清晰度和可操作性

**可能的问题**:
- 错误信息是否太技术化或不清晰
- 是否提供表名提示（如"你是不是想查询 xxx_table？"）
- 权限错误是否与表不存在的错误区分清楚

---

### 场景 3: 超长查询 - 10000+ 行数据

**目标**: 验证大数据结果的处理、分页机制和截断策略

**测试用例**:
```sql
SELECT
  id,
  name,
  value
FROM large_table
LIMIT 15000
```

**预期行为**:
- 返回状态: `SUCCESS` 或 `PARTIAL`（如果有分页）
- 数据限制: 根据平台配置，可能返回最多 10000 行
  ```json
  {
    "taskId": "...",
    "queryStatus": "SUCCESS",
    "rows": [...],
    "rowCount": 10000,
    "totalRowCount": 15000,
    "isPartial": true,
    "nextToken": "offset_10000"
  }
  ```
- 内存占用: 监控是否有内存泄漏

**验证方式**:
1. 构建返回 10000+ 行的查询
2. 调用 `submit_dp_query(sql=...)`
3. 监控轮询时间和返回数据大小
4. 验证是否返回分页标记（如 nextToken）
5. 尝试获取下一页数据（如果支持）

**可能的问题**:
- 是否硬性限制在 10000 行，超出部分是否会报错还是无声截断
- 返回结果的大小是否会导致网络超时（如 response > 100MB）
- 客户端是否能正确处理大 JSON 响应

**限制条件**:
- 单次查询最大返回行数: **10000 行**（根据工具描述）
- 建议分页大小: 1000-5000 行

---

### 场景 4: 查询超时 - 模拟慢查询

**目标**: 验证查询超时处理和用户友好的超时提示

**测试用例**:
```sql
-- 模拟耗时查询（如全表扫描、复杂 JOIN）
SELECT *
FROM large_fact_table a
JOIN large_dim_table b ON a.id = b.id
WHERE a.date >= '2024-01-01'
GROUP BY a.category
HAVING COUNT(*) > 100000
```

或使用 SQL 函数模拟延迟（如果平台支持）：
```sql
SELECT SLEEP(3600) as slow_col  -- 1小时延迟
```

**预期行为**:
- 查询启动: taskId 立即返回
- 轮询过程:
  - 0-5 秒: 状态为 `RUNNING`
  - 300-600 秒: 状态为 `TIMEOUT` 或自动 KILL
- 超时错误消息:
  ```json
  {
    "taskId": "...",
    "queryStatus": "TIMEOUT",
    "errorMessage": "Query execution timeout after 600 seconds",
    "errorCode": "QUERY_TIMEOUT",
    "executionTime": 600
  }
  ```

**验证方式**:
1. 构建一个已知耗时较长的真实查询（如月级别大表 JOIN）
2. 调用 `submit_dp_query(sql=...)`
3. 不断轮询 `get_dp_query_status`，记录每次返回的 executionTime
4. 等待超时或手动 KILL（见下一条）
5. 验证超时消息的清晰度

**可能的问题**:
- 超时时间是否可配置
- 是否支持用户主动 KILL（通过 `kill_dp_query` 工具）
- 超时后的资源释放是否干净（是否有孤立的查询进程）

**限制条件**:
- 查询默认超时时间: **600 秒**（10 分钟，根据工具描述）
- 建议查询应在 **30-60 秒内完成**

---

### 场景 5: KILL 查询 - 中断长时间运行的查询

**目标**: 验证查询中断机制和资源释放

**测试用例**:
1. 启动一个超长查询（预计运行 > 60 秒）
2. 在 10 秒后主动 KILL 该查询

```python
# 伪代码
task_id = submit_dp_query("SELECT SLEEP(3600)")
time.sleep(10)
kill_dp_query(task_id=task_id)
status = get_dp_query_status(task_id=task_id)
```

**预期行为**:
- 查询立即中断: 状态变为 `KILLED` 或 `CANCELED`
- KILL 响应:
  ```json
  {
    "taskId": "...",
    "killStatus": "SUCCESS",
    "message": "Query killed successfully after 10 seconds"
  }
  ```
- 资源释放: 数据库连接和内存应该被完全释放

**验证方式**:
1. 使用工具 `kill_dp_query(taskId=...)`
2. 立即调用 `get_dp_query_status` 验证状态
3. 检查数据库日志确认查询进程已释放

**可能的问题**:
- KILL 是否可靠（有无竞态条件）
- KILL 后是否产生孤立事务
- 用户是否只能 KILL 自己的查询（权限隔离）

---

### 场景 6: 权限错误 - 查询无权限表

**目标**: 验证权限检查和错误区分

**测试用例**:
```sql
SELECT * FROM sensitive_finance_table
```

或尝试访问其他部门的数据表。

**预期行为**:
- 返回状态: `FAILED`
- 错误消息: 明确指出权限问题（不应泄露表结构或字段信息）
  ```json
  {
    "taskId": "...",
    "queryStatus": "FAILED",
    "errorMessage": "Permission denied: You do not have SELECT privilege on table 'sensitive_finance_table'",
    "errorCode": "PERMISSION_DENIED"
  }
  ```

**验证方式**:
1. 使用低权限用户账号执行测试
2. 尝试查询已知无权限的表
3. 验证错误消息不会泄露表结构或内容

**可能的问题**:
- 权限错误是否与表不存在的错误区分清楚
- 是否会在错误消息中意外泄露敏感信息
- 权限检查是否发生在 SQL 解析阶段还是执行阶段

---

### 场景 7: SQL 语法错误

**目标**: 验证语法检查和错误诊断

**测试用例**:
```sql
SELECT * FOM table_name  -- 拼写错误
```

**预期行为**:
- 返回状态: `FAILED` 或 `PARSE_ERROR`
- 错误消息: 应指出具体的语法问题
  ```json
  {
    "taskId": "...",
    "queryStatus": "FAILED",
    "errorMessage": "Syntax error near 'FOM': expected keyword 'FROM'",
    "errorCode": "SYNTAX_ERROR",
    "position": 8
  }
  ```

**验证方式**:
1. 提交多个包含不同语法错误的 SQL
2. 验证错误消息是否清晰指出问题位置

---

### 场景 8: 不支持的 SQL 操作

**目标**: 验证仅 SELECT 限制的执行

**测试用例**:
```sql
INSERT INTO table_name VALUES (1, 'test')
```

```sql
UPDATE table_name SET col = 'value' WHERE id = 1
```

```sql
DELETE FROM table_name WHERE id = 1
```

**预期行为**:
- 返回状态: `FAILED`
- 错误消息: 明确说明不支持该操作类型
  ```json
  {
    "taskId": "...",
    "queryStatus": "FAILED",
    "errorMessage": "Operation not supported: INSERT statements are not allowed. Only SELECT queries are supported.",
    "errorCode": "UNSUPPORTED_OPERATION"
  }
  ```

**验证方式**:
1. 依次提交 INSERT、UPDATE、DELETE 语句
2. 验证平台是否在解析阶段就拒绝这些操作

---

### 场景 9: 空查询结果

**目标**: 验证无结果的查询处理

**测试用例**:
```sql
SELECT * FROM table_name WHERE 1 = 0  -- 恒真条件，返回 0 行
```

**预期行为**:
- 返回状态: `SUCCESS`
- 数据结构:
  ```json
  {
    "taskId": "...",
    "queryStatus": "SUCCESS",
    "columns": [...],
    "rows": [],
    "rowCount": 0
  }
  ```

**验证方式**:
1. 提交返回 0 行的查询
2. 验证是否仍返回正确的列定义

---

### 场景 10: 特殊数据类型处理

**目标**: 验证 NULL、日期、浮点数等的正确序列化

**测试用例**:
```sql
SELECT
  NULL as null_col,
  '2026-03-31' as date_col,
  3.14159 as float_col,
  CURRENT_TIMESTAMP as timestamp_col,
  '' as empty_string_col
FROM dual
```

**预期行为**:
- NULL 值: 应返回 JSON `null`
- 日期格式: 应返回 ISO 8601 格式（YYYY-MM-DD）
- 浮点数: 精度损失是否可接受
  ```json
  {
    "rowCount": 1,
    "rows": [[null, "2026-03-31", 3.14159, "2026-03-31T12:34:56Z", ""]]
  }
  ```

**验证方式**:
1. 查询包含各种数据类型的表
2. 验证 JSON 序列化是否正确
3. 检查前端反序列化是否成功

---

## 测试执行流程

### 前置条件

```python
# 1. 验证账号权限
user = current_user()
assert user.has_permission("select_from_dp"), "No SELECT privilege"

# 2. 准备测试数据表
test_tables = [
    "large_table",           # > 10000 行的表
    "dim_table",             # 维度表
    "nonexistent_table",     # 不存在（用于错误测试）
]
for table in test_tables:
    assert table_exists(table) or table == "nonexistent_table"
```

### 测试执行

```python
import time
import json

class DPQueryBoundaryTest:
    def __init__(self):
        self.results = []
        self.start_time = time.time()

    def test_scenario(self, scenario_name, sql, expected_status=None, timeout=10):
        """执行单个测试场景"""
        print(f"\n[测试] {scenario_name}")
        print(f"SQL: {sql}")

        try:
            # 1. 提交查询
            task_id = submit_dp_query(sql=sql)
            print(f"✓ taskId: {task_id}")

            # 2. 轮询结果
            max_polls = int(timeout / 0.5)
            for poll_count in range(max_polls):
                status_resp = get_dp_query_status(taskId=task_id)
                status = status_resp.get("queryStatus")

                if status in ["SUCCESS", "FAILED", "TIMEOUT", "KILLED"]:
                    print(f"✓ 查询完成: {status}")
                    self.results.append({
                        "scenario": scenario_name,
                        "sql": sql,
                        "status": status,
                        "response": status_resp,
                        "poll_count": poll_count,
                        "duration": (poll_count + 1) * 0.5
                    })
                    return status_resp

                time.sleep(0.5)

            # 超时
            print(f"✗ 轮询超时（{timeout}秒）")
            self.results.append({
                "scenario": scenario_name,
                "sql": sql,
                "status": "POLL_TIMEOUT",
                "duration": timeout
            })

        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            self.results.append({
                "scenario": scenario_name,
                "sql": sql,
                "status": "ERROR",
                "error": str(e)
            })

    def generate_report(self):
        """生成测试报告"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r["status"] == "SUCCESS"),
            "failed": sum(1 for r in self.results if r["status"] == "FAILED"),
            "errors": sum(1 for r in self.results if r["status"] == "ERROR"),
            "details": self.results
        }
        return json.dumps(report, indent=2, ensure_ascii=False)
```

### 轮询逻辑

```python
def poll_query_result(task_id, timeout=600, interval=0.5):
    """通用轮询函数"""
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"Query timeout after {timeout}s")

        status = get_dp_query_status(taskId=task_id)
        query_status = status.get("queryStatus")

        print(f"[{elapsed:.1f}s] Status: {query_status}")

        if query_status in ["SUCCESS", "FAILED", "TIMEOUT", "KILLED"]:
            return status

        time.sleep(interval)
```

---

## 预期的限制条件总结

| 限制项 | 值 | 说明 |
|------|-----|------|
| 最大返回行数 | 10000 | 超出自动截断，需分页查询 |
| 默认查询超时 | 600 秒 | 10 分钟，可通过 `kill_dp_query` 手动中断 |
| 支持的语句类型 | SELECT 仅 | INSERT/UPDATE/DELETE/DDL 不支持 |
| 查询并发数 | TBD | 需测试平台支持的并发查询数 |
| 响应 JSON 大小 | TBD | 需测试超大结果是否会压缩或分块返回 |
| 权限隔离 | 按表 | 基于用户角色的表级权限 |
| 错误消息格式 | JSON | 包含 errorCode 和 errorMessage |

---

## 已知限制和注意事项

### 平台限制

1. **仅支持 SELECT**: 任何修改操作都会被拒绝
2. **异步执行模式**: 必须通过轮询获取结果，不支持同步阻塞调用
3. **10000 行硬限制**: 大查询需要分页或优化
4. **无 JOIN 优化提示**: 复杂 JOIN 容易超时，建议预处理成宽表

### 错误处理建议

1. **区分错误类型**:
   - `TABLE_NOT_FOUND`: 表不存在，可能需要检查表名或权限
   - `PERMISSION_DENIED`: 无权限，联系数据管理员
   - `SYNTAX_ERROR`: SQL 语法问题，检查 SQL 语句
   - `QUERY_TIMEOUT`: 查询过于复杂，考虑分解或预聚合

2. **客户端重试策略**:
   - 轮询间隔: 0.5-2 秒（根据查询复杂度调整）
   - 最大重试次数: 1200 次（对应 600 秒超时）
   - 指数退避: 对于网络不稳定的环境

3. **资源清理**:
   - 查询完成后立即释放 taskId
   - 对于长时间运行的查询，需要手动 KILL 以释放资源

---

## 测试工具和依赖

| 工具 | 功能 | 调用方式 |
|------|------|---------|
| `mcp__sh_dp_mcp__submit_dp_query` | 提交异步查询 | `submit_dp_query(sql=...)` |
| `mcp__sh_dp_mcp__get_dp_query_status` | 查询状态和结果 | `get_dp_query_status(taskId=...)` |
| `mcp__sh_dp_mcp__kill_dp_query` | 中断查询 | `kill_dp_query(taskId=...)` |
| `mcp__sh_dp_mcp__get_dp_table_meta` | 获取表元数据 | `get_dp_table_meta(projectName=..., tableName=...)` |

---

## 测试成功标准

| 场景 | 成功标准 |
|------|---------|
| 简单查询 | 返回正确的行数和列名，< 1秒 |
| 不存在的表 | 返回 FAILED，错误消息清晰 |
| 超长查询 | 返回 10000 行，提示数据被截断 |
| 查询超时 | 自动 KILL，返回 TIMEOUT 状态 |
| KILL 查询 | 查询立即中断，资源释放 |
| 权限错误 | 返回 PERMISSION_DENIED，不泄露敏感信息 |
| SQL 错误 | 返回 SYNTAX_ERROR，指出问题位置 |
| 不支持操作 | 返回 UNSUPPORTED_OPERATION，拒绝执行 |
| 空结果集 | 返回 SUCCESS，列定义正确，rows=[] |
| 特殊数据类型 | 正确序列化 NULL、日期、浮点数等 |

---

## 后续行动

### 立即可执行的测试

1. **场景 1, 7, 8, 9**: 这些无需特殊权限或特殊表，可立即执行
2. **场景 2**: 尝试查询一个不存在的表名
3. **场景 10**: 使用 `SELECT NULL, '2026-03-31', 3.14` 测试数据类型

### 需要数据准备的测试

4. **场景 3**: 找一个已知超过 15000 行的表进行测试
5. **场景 4**: 使用真实的慢查询（JOIN 大表）进行测试
6. **场景 5**: 基于场景 4 的慢查询进行 KILL 测试

### 需要权限验证的测试

7. **场景 6**: 使用低权限账号测试权限隔离

---

## 附录: 测试数据表参考

建议使用以下表进行测试（根据实际数据平台调整）：

```sql
-- 查询表列表（需运行权限检查）
SELECT
  table_name,
  table_schema,
  row_count,
  data_length
FROM information_schema.tables
WHERE table_schema = 'test_db'
ORDER BY row_count DESC;
```

**候选表**:
- 大表（> 100000 行）: 用于场景 3（超长查询）、场景 4（超时）
- 小表（< 100 行）: 用于场景 1（简单查询）
- 维度表: 用于场景 10（数据类型）
- 权限受限表: 用于场景 6（权限错误）

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-03-31 | 初版，包含 10 个测试场景 |

---

## 联系方式

如有问题或需要补充测试场景，请联系数据平台团队或提交 Issue。

**文档维护**: 预算平台项目
**最后更新**: 2026-03-31
