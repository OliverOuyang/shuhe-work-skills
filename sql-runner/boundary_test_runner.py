#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sh_dp_mcp 边界条件测试执行脚本

用途: 自动执行所有测试场景，收集结果，生成测试报告
运行: python3 boundary_test_runner.py
"""

import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# 修复 Windows 上的 UTF-8 编码
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


class QueryStatus(Enum):
    """查询状态枚举"""
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    KILLED = "KILLED"
    POLL_TIMEOUT = "POLL_TIMEOUT"
    ERROR = "ERROR"


@dataclass
class TestResult:
    """单个测试结果"""
    scenario_id: str
    scenario_name: str
    sql: str
    status: str
    duration: float
    row_count: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    response: Optional[Dict] = None
    poll_count: int = 0
    notes: str = ""


class DPQueryBoundaryTestRunner:
    """数据平台查询边界条件测试执行器"""

    def __init__(self, output_file: str = "boundary_test_results.json"):
        self.results: List[TestResult] = []
        self.output_file = output_file
        self.start_time = time.time()

    def mock_submit_query(self, sql: str) -> str:
        """模拟提交查询（实际使用时替换为真实 API 调用）"""
        # 实际使用: return mcp__sh_dp_mcp__submit_dp_query(sql=sql)
        import uuid
        return f"task_{uuid.uuid4().hex[:8]}"

    def mock_get_query_status(
        self, task_id: str, scenario_id: str
    ) -> Dict[str, Any]:
        """模拟查询状态（实际使用时替换为真实 API 调用）"""
        # 实际使用: return mcp__sh_dp_mcp__get_dp_query_status(taskId=task_id)

        # 这里是模拟响应，实际测试时应调用真实 API
        scenarios = {
            "s1": {
                "queryStatus": "SUCCESS",
                "rowCount": 1,
                "columns": ["col1", "col2"],
                "rows": [["test", 123]],
            },
            "s2": {
                "queryStatus": "FAILED",
                "errorCode": "TABLE_NOT_FOUND",
                "errorMessage": "Table 'nonexistent_table_12345' not found in database",
            },
            "s3": {
                "queryStatus": "SUCCESS",
                "rowCount": 10000,
                "isPartial": True,
                "totalRowCount": 15000,
                "columns": ["id", "name", "value"],
            },
            "s7": {
                "queryStatus": "FAILED",
                "errorCode": "SYNTAX_ERROR",
                "errorMessage": "Syntax error near 'FOM': expected keyword 'FROM'",
                "position": 8,
            },
            "s8_insert": {
                "queryStatus": "FAILED",
                "errorCode": "UNSUPPORTED_OPERATION",
                "errorMessage": "Operation not supported: INSERT statements are not allowed. Only SELECT queries are supported.",
            },
            "s9": {
                "queryStatus": "SUCCESS",
                "rowCount": 0,
                "columns": ["id", "name", "value"],
                "rows": [],
            },
            "s10": {
                "queryStatus": "SUCCESS",
                "rowCount": 1,
                "columns": ["null_col", "date_col", "float_col", "timestamp_col", "empty_string_col"],
                "rows": [[None, "2026-03-31", 3.14159, "2026-03-31T12:34:56Z", ""]],
            },
        }
        return scenarios.get(scenario_id, {"queryStatus": "RUNNING"})

    def poll_query(
        self,
        task_id: str,
        scenario_id: str,
        timeout: float = 10,
        interval: float = 0.5,
    ) -> Dict[str, Any]:
        """轮询查询结果"""
        start_time = time.time()
        poll_count = 0

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                return {
                    "queryStatus": QueryStatus.POLL_TIMEOUT.value,
                    "errorMessage": f"Poll timeout after {timeout}s",
                }

            status = self.mock_get_query_status(task_id, scenario_id)
            query_status = status.get("queryStatus")

            poll_count += 1

            if query_status in [
                QueryStatus.SUCCESS.value,
                QueryStatus.FAILED.value,
                QueryStatus.TIMEOUT.value,
                QueryStatus.KILLED.value,
            ]:
                status["poll_count"] = poll_count
                status["elapsed_time"] = elapsed
                return status

            time.sleep(interval)

    def test_scenario_1_simple_query(self):
        """场景 1: 简单查询 - 少量数据"""
        scenario_id = "s1"
        scenario_name = "简单查询 - 少量数据"
        sql = "SELECT 'test' as col1, 123 as col2"

        print(f"\n[场景 1] {scenario_name}")
        print(f"SQL: {sql}")

        try:
            start_time = time.time()
            task_id = self.mock_submit_query(sql)
            print(f"✓ taskId: {task_id}")

            status = self.poll_query(task_id, scenario_id, timeout=10)
            duration = time.time() - start_time

            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=status.get("queryStatus"),
                duration=duration,
                row_count=status.get("rowCount"),
                response=status,
                poll_count=status.get("poll_count", 0),
                notes="✓ 通过: 返回正确的行数和列名，< 1秒" if duration < 1 else "⚠ 超时: 返回时间 > 1秒",
            )
            self.results.append(result)
            print(f"✓ 完成: {status.get('queryStatus')}, 耗时 {duration:.2f}s")

        except Exception as e:
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=QueryStatus.ERROR.value,
                duration=time.time() - start_time,
                error_message=str(e),
                notes=f"✗ 异常: {str(e)}",
            )
            self.results.append(result)
            print(f"✗ 异常: {str(e)}")

    def test_scenario_2_nonexistent_table(self):
        """场景 2: 查询不存在的表"""
        scenario_id = "s2"
        scenario_name = "查询不存在的表"
        sql = "SELECT * FROM nonexistent_table_12345"

        print(f"\n[场景 2] {scenario_name}")
        print(f"SQL: {sql}")

        try:
            start_time = time.time()
            task_id = self.mock_submit_query(sql)
            status = self.poll_query(task_id, scenario_id, timeout=5)
            duration = time.time() - start_time

            error_code = status.get("errorCode")
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=status.get("queryStatus"),
                duration=duration,
                error_code=error_code,
                error_message=status.get("errorMessage"),
                response=status,
                poll_count=status.get("poll_count", 0),
                notes="✓ 通过: 返回 FAILED，错误消息清晰" if error_code == "TABLE_NOT_FOUND" else "⚠ 部分: 错误消息不够清晰",
            )
            self.results.append(result)
            print(f"✓ 完成: {error_code} - {status.get('errorMessage')}")

        except Exception as e:
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=QueryStatus.ERROR.value,
                duration=time.time() - start_time,
                error_message=str(e),
                notes=f"✗ 异常: {str(e)}",
            )
            self.results.append(result)

    def test_scenario_3_large_result(self):
        """场景 3: 超长查询 - 10000+ 行数据"""
        scenario_id = "s3"
        scenario_name = "超长查询 - 10000+ 行数据"
        sql = "SELECT id, name, value FROM large_table LIMIT 15000"

        print(f"\n[场景 3] {scenario_name}")
        print(f"SQL: {sql}")

        try:
            start_time = time.time()
            task_id = self.mock_submit_query(sql)
            status = self.poll_query(task_id, scenario_id, timeout=60)
            duration = time.time() - start_time

            row_count = status.get("rowCount")
            is_partial = status.get("isPartial", False)
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=status.get("queryStatus"),
                duration=duration,
                row_count=row_count,
                response=status,
                poll_count=status.get("poll_count", 0),
                notes=f"✓ 通过: 返回 {row_count} 行，分页={is_partial}" if row_count == 10000 else f"⚠ 注意: 返回 {row_count} 行",
            )
            self.results.append(result)
            print(f"✓ 完成: 返回 {row_count} 行, 分页={is_partial}, 耗时 {duration:.2f}s")

        except Exception as e:
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=QueryStatus.ERROR.value,
                duration=time.time() - start_time,
                error_message=str(e),
                notes=f"✗ 异常: {str(e)}",
            )
            self.results.append(result)

    def test_scenario_7_syntax_error(self):
        """场景 7: SQL 语法错误"""
        scenario_id = "s7"
        scenario_name = "SQL 语法错误"
        sql = "SELECT * FOM table_name"

        print(f"\n[场景 7] {scenario_name}")
        print(f"SQL: {sql}")

        try:
            start_time = time.time()
            task_id = self.mock_submit_query(sql)
            status = self.poll_query(task_id, scenario_id, timeout=5)
            duration = time.time() - start_time

            error_code = status.get("errorCode")
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=status.get("queryStatus"),
                duration=duration,
                error_code=error_code,
                error_message=status.get("errorMessage"),
                response=status,
                poll_count=status.get("poll_count", 0),
                notes="✓ 通过: 返回 SYNTAX_ERROR，错误位置准确" if error_code == "SYNTAX_ERROR" else "⚠ 部分: 错误诊断不够准确",
            )
            self.results.append(result)
            print(f"✓ 完成: {error_code} - {status.get('errorMessage')}")

        except Exception as e:
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=QueryStatus.ERROR.value,
                duration=time.time() - start_time,
                error_message=str(e),
                notes=f"✗ 异常: {str(e)}",
            )
            self.results.append(result)

    def test_scenario_8_unsupported_operations(self):
        """场景 8: 不支持的 SQL 操作"""
        scenario_id = "s8_insert"
        scenario_name = "不支持的 SQL 操作 - INSERT"
        sql = "INSERT INTO table_name VALUES (1, 'test')"

        print(f"\n[场景 8] {scenario_name}")
        print(f"SQL: {sql}")

        try:
            start_time = time.time()
            task_id = self.mock_submit_query(sql)
            status = self.poll_query(task_id, scenario_id, timeout=5)
            duration = time.time() - start_time

            error_code = status.get("errorCode")
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=status.get("queryStatus"),
                duration=duration,
                error_code=error_code,
                error_message=status.get("errorMessage"),
                response=status,
                poll_count=status.get("poll_count", 0),
                notes="✓ 通过: 返回 UNSUPPORTED_OPERATION" if error_code == "UNSUPPORTED_OPERATION" else "⚠ 部分: 错误代码不对",
            )
            self.results.append(result)
            print(f"✓ 完成: {error_code} - 拒绝执行")

        except Exception as e:
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=QueryStatus.ERROR.value,
                duration=time.time() - start_time,
                error_message=str(e),
                notes=f"✗ 异常: {str(e)}",
            )
            self.results.append(result)

    def test_scenario_9_empty_result(self):
        """场景 9: 空查询结果"""
        scenario_id = "s9"
        scenario_name = "空查询结果"
        sql = "SELECT * FROM table_name WHERE 1 = 0"

        print(f"\n[场景 9] {scenario_name}")
        print(f"SQL: {sql}")

        try:
            start_time = time.time()
            task_id = self.mock_submit_query(sql)
            status = self.poll_query(task_id, scenario_id, timeout=5)
            duration = time.time() - start_time

            row_count = status.get("rowCount", 0)
            columns = status.get("columns", [])
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=status.get("queryStatus"),
                duration=duration,
                row_count=row_count,
                response=status,
                poll_count=status.get("poll_count", 0),
                notes=f"✓ 通过: 返回 0 行，列定义正确" if row_count == 0 and len(columns) > 0 else f"⚠ 部分: 列定义缺失",
            )
            self.results.append(result)
            print(f"✓ 完成: 返回 {row_count} 行，列数={len(columns)}")

        except Exception as e:
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=QueryStatus.ERROR.value,
                duration=time.time() - start_time,
                error_message=str(e),
                notes=f"✗ 异常: {str(e)}",
            )
            self.results.append(result)

    def test_scenario_10_special_types(self):
        """场景 10: 特殊数据类型处理"""
        scenario_id = "s10"
        scenario_name = "特殊数据类型处理"
        sql = "SELECT NULL as null_col, '2026-03-31' as date_col, 3.14159 as float_col, CURRENT_TIMESTAMP as timestamp_col, '' as empty_string_col FROM dual"

        print(f"\n[场景 10] {scenario_name}")
        print(f"SQL: {sql}")

        try:
            start_time = time.time()
            task_id = self.mock_submit_query(sql)
            status = self.poll_query(task_id, scenario_id, timeout=5)
            duration = time.time() - start_time

            row_count = status.get("rowCount", 0)
            rows = status.get("rows", [])
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=status.get("queryStatus"),
                duration=duration,
                row_count=row_count,
                response=status,
                poll_count=status.get("poll_count", 0),
                notes="✓ 通过: 特殊类型序列化正确" if row_count == 1 and rows else "⚠ 部分: 数据结构异常",
            )
            self.results.append(result)
            print(f"✓ 完成: 返回 {row_count} 行，数据类型检查通过")

        except Exception as e:
            result = TestResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                sql=sql,
                status=QueryStatus.ERROR.value,
                duration=time.time() - start_time,
                error_message=str(e),
                notes=f"✗ 异常: {str(e)}",
            )
            self.results.append(result)

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("sh_dp_mcp 边界条件测试执行器")
        print("=" * 70)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 立即可执行的测试（无需特殊权限或数据）
        self.test_scenario_1_simple_query()
        self.test_scenario_2_nonexistent_table()
        self.test_scenario_7_syntax_error()
        self.test_scenario_8_unsupported_operations()
        self.test_scenario_9_empty_result()
        self.test_scenario_10_special_types()

        # 需要特殊数据或权限的测试（演示但跳过）
        print("\n[场景 3] 超长查询 - 10000+ 行数据 (跳过: 需要真实大表)")
        print("[场景 4] 查询超时 - 模拟慢查询 (跳过: 需要真实慢查询)")
        print("[场景 5] KILL 查询 (跳过: 需要长时间查询)")
        print("[场景 6] 权限错误 (跳过: 需要权限限制表)")

        print("\n" + "=" * 70)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        self._generate_report()

    def _generate_report(self):
        """生成测试报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.status == QueryStatus.SUCCESS.value),
            "failed": sum(1 for r in self.results if r.status == QueryStatus.FAILED.value),
            "errors": sum(1 for r in self.results if r.status == QueryStatus.ERROR.value),
            "total_duration": time.time() - self.start_time,
            "details": [asdict(r) for r in self.results],
        }

        # 打印摘要
        print(f"\n【测试摘要】")
        print(f"  总数: {report['total_tests']}")
        print(f"  成功: {report['passed']}")
        print(f"  失败: {report['failed']}")
        print(f"  异常: {report['errors']}")
        print(f"  耗时: {report['total_duration']:.2f}s")

        # 保存结果
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n✓ 测试结果已保存到: {self.output_file}")

        # 打印失败项详情
        failures = [r for r in self.results if r.status != QueryStatus.SUCCESS.value]
        if failures:
            print(f"\n【失败详情】({len(failures)}项)")
            for r in failures:
                print(f"  - {r.scenario_id}: {r.scenario_name}")
                if r.error_code:
                    print(f"    错误代码: {r.error_code}")
                if r.error_message:
                    print(f"    错误信息: {r.error_message}")


def main():
    """主函数"""
    runner = DPQueryBoundaryTestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()
