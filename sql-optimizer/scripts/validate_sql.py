#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL语法验证脚本 - 专门针对Hive/MaxCompute SQL
检查常见语法错误,不执行实际查询
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Windows环境编码修复
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class SQLValidator:
    """Hive/MaxCompute SQL语法验证器"""

    def __init__(self, sql_content: str):
        self.sql = sql_content
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """执行所有验证检查"""
        # 移除注释以便分析
        sql_no_comments = self._remove_comments(self.sql)

        # 基础语法检查
        self._check_balanced_parentheses()
        self._check_balanced_quotes()
        self._check_keyword_order(sql_no_comments)
        self._check_select_syntax(sql_no_comments)
        self._check_join_syntax(sql_no_comments)
        self._check_partition_syntax()
        self._check_common_typos(sql_no_comments)

        # Hive/MaxCompute特定检查
        self._check_hive_functions()
        self._check_variables()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _remove_comments(self, sql: str) -> str:
        """移除SQL注释"""
        # 移除块注释 /* ... */
        sql = re.sub(r'/\*.*?\*/', ' ', sql, flags=re.DOTALL)
        # 移除行注释 --
        sql = re.sub(r'--[^\n]*', ' ', sql)
        return sql

    def _check_balanced_parentheses(self):
        """检查括号是否配对"""
        stack = []
        for i, char in enumerate(self.sql):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if not stack:
                    self.errors.append(f"多余的右括号 ')' 在位置 {i}")
                else:
                    stack.pop()

        if stack:
            self.errors.append(f"缺少 {len(stack)} 个右括号 ')'")

    def _check_balanced_quotes(self):
        """检查引号是否配对"""
        # 检查单引号
        single_quotes = [i for i, c in enumerate(self.sql) if c == "'" and (i == 0 or self.sql[i-1] != '\\')]
        if len(single_quotes) % 2 != 0:
            self.errors.append("单引号 ' 未配对")

        # 检查双引号
        double_quotes = [i for i, c in enumerate(self.sql) if c == '"' and (i == 0 or self.sql[i-1] != '\\')]
        if len(double_quotes) % 2 != 0:
            self.errors.append("双引号 \" 未配对")

    def _check_keyword_order(self, sql: str):
        """检查SQL关键字顺序"""
        sql_upper = sql.upper()

        # 查找主要关键字位置
        keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT']
        positions: Dict[str, int] = {}

        for kw in keywords:
            match = re.search(r'\b' + kw + r'\b', sql_upper)
            if match:
                positions[kw] = match.start()

        # 验证顺序
        if 'SELECT' in positions and 'FROM' in positions:
            if positions['SELECT'] > positions['FROM']:
                self.errors.append("SELECT 必须在 FROM 之前")

        if 'FROM' in positions and 'WHERE' in positions:
            if positions['FROM'] > positions['WHERE']:
                self.errors.append("FROM 必须在 WHERE 之前")

        if 'WHERE' in positions and 'GROUP BY' in positions:
            if positions['WHERE'] > positions['GROUP BY']:
                self.errors.append("WHERE 必须在 GROUP BY 之前")

        if 'GROUP BY' in positions and 'HAVING' in positions:
            if positions['GROUP BY'] > positions['HAVING']:
                self.errors.append("GROUP BY 必须在 HAVING 之前")

        if 'HAVING' in positions and 'ORDER BY' in positions:
            if positions['HAVING'] > positions['ORDER BY']:
                self.errors.append("HAVING 必须在 ORDER BY 之前")

    def _check_select_syntax(self, sql: str):
        """检查SELECT语句语法"""
        sql_upper = sql.upper()

        # 确保有SELECT关键字
        if 'SELECT' not in sql_upper:
            self.errors.append("缺少 SELECT 关键字")
            return

        # 检查SELECT后面是否直接跟FROM(没有字段)
        if re.search(r'\bSELECT\s+FROM\b', sql_upper):
            self.errors.append("SELECT 后面缺少字段列表")

        # 检查是否有重复的逗号
        if re.search(r',,+', sql):
            self.warnings.append("发现连续的逗号")

    def _check_join_syntax(self, sql: str):
        """检查JOIN语法"""
        sql_upper = sql.upper()

        # 查找所有JOIN
        joins = re.finditer(r'\b(LEFT|RIGHT|INNER|OUTER|FULL|CROSS)?\s*JOIN\b', sql_upper)

        for match in joins:
            join_pos = match.start()
            # 在JOIN后面查找ON或USING
            after_join = sql_upper[join_pos:join_pos+200]  # 查找后续200字符

            # CROSS JOIN不需要ON
            if 'CROSS' in match.group():
                continue

            if 'ON' not in after_join and 'USING' not in after_join:
                self.warnings.append(f"JOIN 后面可能缺少 ON 或 USING 条件 (位置: {join_pos})")

    def _check_partition_syntax(self):
        """检查分区语法"""
        # 检查常见的分区谓词
        partition_patterns = [
            (r'\bds\s*=\s*[\'"]?\$\{bizdate\}[\'"]?', 'ds分区'),
            (r'\bpt\s*=\s*[\'"]?\$\{pt\}[\'"]?', 'pt分区'),
            (r'\bds\s*=\s*[\'"]?\d{8}[\'"]?', 'ds分区(日期)'),
        ]

        for pattern, desc in partition_patterns:
            if re.search(pattern, self.sql, re.IGNORECASE):
                # 分区使用正常
                pass

    def _check_hive_functions(self):
        """检查Hive/MaxCompute函数使用"""
        sql_upper = self.sql.upper()

        # 常见的Hive函数
        hive_functions = [
            'TO_DATE', 'DATE_SUB', 'DATE_ADD', 'DATEDIFF',
            'SUBSTR', 'CONCAT', 'CONCAT_WS',
            'IF', 'COALESCE', 'NVLNVL',
            'ROW_NUMBER', 'RANK', 'DENSE_RANK',
            'LEAD', 'LAG',
            'PERCENTILE', 'PERCENTILE_APPROX'
        ]

        # 检查函数后是否跟了括号
        for func in hive_functions:
            pattern = r'\b' + func + r'\s*\('
            if re.search(r'\b' + func + r'\b', sql_upper):
                if not re.search(pattern, sql_upper):
                    self.warnings.append(f"函数 {func} 可能缺少括号")

    def _check_variables(self):
        """检查变量使用"""
        # 查找所有 ${...} 变量
        variables = re.findall(r'\$\{([^}]+)\}', self.sql)

        # 常见的MaxCompute变量
        common_vars = ['bizdate', 'pt', 'yyyymmdd', 'yyyy-mm-dd']

        for var in variables:
            if var not in common_vars:
                self.warnings.append(f"发现非标准变量: ${{{var}}}")

    def _check_common_typos(self, sql: str):
        """检查常见拼写错误"""
        sql_upper = sql.upper()

        # 常见错误模式
        typos = [
            (r'\bSELCT\b', 'SELECT 拼写错误(SELCT)'),
            (r'\bFORM\b', 'FROM 可能拼写错误(FORM)'),
            (r'\bWHERE\s+AND\b', 'WHERE 后面不能直接跟 AND'),
            (r'\bGROUP\s+ON\b', 'GROUP BY 可能写成了 GROUP ON'),
        ]

        for pattern, message in typos:
            if re.search(pattern, sql_upper):
                self.errors.append(message)


def validate_sql_file(file_path: str) -> bool:
    """验证SQL文件"""
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return False

        if not path.suffix.lower() == '.sql':
            print(f"⚠️  警告: 文件扩展名不是.sql")

        # 读取文件
        with open(path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        if not sql_content.strip():
            print("❌ SQL文件为空")
            return False

        # 执行验证
        validator = SQLValidator(sql_content)
        is_valid, errors, warnings = validator.validate()

        # 输出结果
        print(f"\n{'='*60}")
        print(f"SQL文件验证: {path.name}")
        print(f"{'='*60}\n")

        if errors:
            print("❌ 发现语法错误:\n")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
            print()

        if warnings:
            print("⚠️  警告信息:\n")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. {warning}")
            print()

        if is_valid:
            if warnings:
                print("✅ 语法验证通过(有警告)")
            else:
                print("✅ 语法验证通过,无错误和警告")
            return True
        else:
            print(f"❌ 验证失败: 发现 {len(errors)} 个错误")
            return False

    except Exception as e:
        print(f"❌ 验证过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python validate_sql.py <sql_file_path>")
        sys.exit(1)

    sql_file = sys.argv[1]
    success = validate_sql_file(sql_file)
    sys.exit(0 if success else 1)
