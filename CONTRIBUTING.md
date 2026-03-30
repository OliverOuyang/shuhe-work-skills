# 贡献指南 (Contributing Guide)

感谢你有兴趣为 **shuhe-work-skills** 贡献新的 Skills！本指南说明如何为这个项目添加新 Skill。

## 快速开始

### 开发环境设置

```bash
# 1. 克隆仓库
git clone https://github.com/shuhe/work-skills.git
cd work-skills

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装开发依赖
pip install -r requirements-dev.txt

# 5. 在开发模式下安装插件
claude plugin install . --dev
```

## 添加新 Skill：完整流程

### 第 1 步：需求确认

在开始开发前，请明确回答以下问题：

**功能定义：**
- [ ] Skill 解决的具体问题是什么？
- [ ] 目标用户是谁？
- [ ] Skill 的核心输入和输出是什么？

**依赖和约束：**
- [ ] 是否依赖某个 MCP 工具（观远、Dataphin 等）？
- [ ] 是否需要特定的 Python 包？
- [ ] 性能、超时和错误处理的要求？

**示例场景：**
- [ ] 能否用一个真实场景描述使用方式？
- [ ] 预期的调用方式和参数？

### 第 2 步：目录结构创建

在 `skills/` 目录下创建新的 Skill 目录：

```bash
skills/
└── <skill-name>/           # 使用 kebab-case 命名，如 guanyuan-data-fetcher
    ├── SKILL.md            # (必填) Skill 说明文档
    ├── main.py             # (必填) 主执行逻辑
    ├── config.json         # (可选) 配置文件
    ├── requirements.txt    # (可选) Python 依赖
    ├── __init__.py         # (必填) Python 包标记
    └── tests/              # (必填) 测试目录
        ├── __init__.py
        ├── test_main.py
        └── fixtures/       # (可选) 测试数据
```

### 第 3 步：编写 SKILL.md

这是最关键的文档，完整的 Skill.md 应包含以下部分：

```markdown
# Skill 名称

## 1. 概述

用一句话描述这个 Skill 的目的。

示例：
> 自动从观远数据平台查询指定卡片的数据，支持日期范围和筛选条件，生成 Excel 报告。

## 2. 功能说明

详细说明 Skill 的功能和使用场景。

### 核心功能
- 功能点 1
- 功能点 2
- 功能点 3

### 支持的场景
- 场景 1
- 场景 2

### 限制和约束
- 限制 1
- 限制 2

## 3. 调用方式

### 命令格式
```bash
/skill-name [参数] [选项]
```

### 必需参数
- `param1` (类型): 参数说明，示例值
- `param2` (类型): 参数说明，示例值

### 可选参数
- `--option1` (类型): 选项说明，默认值为 X
- `--option2` (bool): 选项说明

### 参数验证规则
- param1：必填，长度 > 0
- param2：可选，范围 [1, 100]

## 4. 输出格式

### 成功响应
```json
{
  "status": "success",
  "data": {
    "records": [...],
    "total": 100,
    "generated_file": "/path/to/report.xlsx"
  },
  "metadata": {
    "query_time": "2026-03-30 10:00:00",
    "execution_time_ms": 1234
  }
}
```

### 错误响应
```json
{
  "status": "error",
  "error_code": "INVALID_PARAMETER",
  "error_message": "参数验证失败",
  "details": {...}
}
```

### 常见错误码
- `INVALID_PARAMETER`: 参数验证失败
- `API_ERROR`: 调用外部 API 失败
- `PERMISSION_DENIED`: 权限不足

## 5. 使用示例

### 基础用法
```bash
/guanyuan-data-fetcher --card-id 12345 --date-range "2026-01-01,2026-01-31"
```

### 高级用法（带多个筛选条件）
```bash
/guanyuan-data-fetcher \
  --card-id 12345 \
  --date-range "2026-01-01,2026-01-31" \
  --filters "region=北京,type=新客" \
  --output-format xlsx \
  --output-path ./reports/
```

### 与其他 Claude Code 功能集成
```bash
# 查询数据后自动生成报告
/guanyuan-data-fetcher --card-id 12345 | /model-evaluation
```

## 6. 性能和限制

- **单次查询限制**: 最多 10,000 条记录
- **API 速率限制**: 每秒 10 个请求
- **超时设置**: 默认 30 秒，支持自定义
- **内存占用**: 典型场景 < 500 MB

## 7. 依赖的工具

### 必需 MCP 工具
- **guanyuan-api**: 版本 ≥ 1.0.0
  - 功能：卡片查询、数据获取
  - 权限要求：观远数据查询权限
  - 失败处理：重试 3 次后放弃

### 可选 Python 包
- openpyxl >= 3.0.0 (for Excel generation)
- pandas >= 1.3.0 (for data processing)

### 环境要求
- Python >= 3.8
- 网络连接到观远数据平台
- `.env` 中配置 GUANYUAN_USER_ID 和 GUANYUAN_API_TOKEN

## 8. 错误处理

### 常见错误场景

**场景 1: API 超时**
- 自动重试 3 次，指数退避
- 最终失败返回错误响应，用户可手动调整参数重试

**场景 2: 权限不足**
- 检测到权限错���时，提示用户申请权限
- 提供权限申请链接和说明

**场景 3: 网络异常**
- 连续失败 3 次后提示用户
- 提供离线缓存方案（如果适用）

## 9. 更新日志

### v1.0.0 (2026-03-30)
- 初始版本发布
- 支持基本的卡片查询和 Excel 生成
```

### SKILL.md 最小化示例

如果你的 Skill 比较简单，可以简化：

```markdown
# <Skill 名称>

## 概述
一句话说明这个 Skill 的目的。

## 使用

### 命令
```bash
/<skill-name> [参数]
```

### 参数
- `param`: 说明

### 示例
```bash
/<skill-name> --param value
```

## 输出
成功返回 JSON 格式的结果，错误返回错误信息。

## 依赖
- 依赖项 1
- 依赖项 2
```

### 第 4 步：实现 main.py

```python
"""
Skill 主模块

说明：[一句话说明此 Skill 的目的]
版本：1.0.0
"""

import sys
import json
import logging
from typing import Dict, Any, List
from argparse import ArgumentParser

# 配置日志
logger = logging.getLogger(__name__)


class SkillExecutor:
    """执行器类，包含 Skill 的核心逻辑"""

    def __init__(self, **kwargs):
        """初始化执行器"""
        self.config = kwargs
        self._validate_config()

    def _validate_config(self) -> None:
        """验证配置参数"""
        # 验证逻辑
        pass

    def execute(self, **params) -> Dict[str, Any]:
        """
        执行 Skill 的核心逻辑

        Args:
            **params: 传入的参数字典

        Returns:
            Dict containing:
            - status: "success" or "error"
            - data: 执行结果数据
            - error_code: 错误代码（仅在 status=error 时）
            - error_message: 错误信息（仅在 status=error 时）
        """
        try:
            # 参数验证
            self._validate_params(params)

            # 核心逻辑
            result = self._execute_core(params)

            return {
                "status": "success",
                "data": result
            }

        except ValidationError as e:
            return {
                "status": "error",
                "error_code": "INVALID_PARAMETER",
                "error_message": str(e)
            }

        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error_code": "EXECUTION_ERROR",
                "error_message": str(e)
            }

    def _validate_params(self, params: Dict[str, Any]) -> None:
        """验证传入参数"""
        required_params = ["param1"]
        for param in required_params:
            if param not in params:
                raise ValidationError(f"Missing required parameter: {param}")

    def _execute_core(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """核心逻辑实现"""
        # 实现你的 Skill 逻辑
        return {}


class ValidationError(Exception):
    """参数验证错误"""
    pass


def parse_arguments():
    """解析命令行参数"""
    parser = ArgumentParser(description="Skill 说明")

    # 必需参数
    parser.add_argument("param1", help="参数1 说明")

    # 可选参数
    parser.add_argument("--option1", default="default_value", help="选项1 说明")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")

    return parser.parse_args()


def main():
    """主入口"""
    # 解析参数
    args = parse_arguments()

    # 配置日志
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)

    # 执行
    executor = SkillExecutor()
    result = executor.execute(
        param1=args.param1,
        option1=args.option1
    )

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 返回退出码
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
```

### 第 5 步：编写测试

```python
# tests/test_main.py

import pytest
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import SkillExecutor, ValidationError


class TestSkillExecutor:
    """Skill 执行器的测试"""

    def setup_method(self):
        """每个测试前的初始化"""
        self.executor = SkillExecutor()

    def test_execute_success(self):
        """测试成功执行"""
        result = self.executor.execute(param1="test_value")
        assert result["status"] == "success"
        assert "data" in result

    def test_execute_missing_required_param(self):
        """测试缺失必需参数"""
        result = self.executor.execute()
        assert result["status"] == "error"
        assert result["error_code"] == "INVALID_PARAMETER"

    def test_execute_invalid_param_type(self):
        """测试参数类型验证"""
        result = self.executor.execute(param1=123)  # 应为字符串
        assert result["status"] == "error"

    def test_validate_params_success(self):
        """测试参数验证成功"""
        # 不应抛出异常
        self.executor._validate_params({"param1": "value"})

    def test_validate_params_missing(self):
        """测试参数验证失败"""
        with pytest.raises(ValidationError):
            self.executor._validate_params({})


@pytest.mark.integration
class TestSkillIntegration:
    """集成测试"""

    def test_end_to_end_execution(self):
        """端到端测试"""
        executor = SkillExecutor()
        result = executor.execute(param1="integration_test")
        assert result["status"] == "success"
```

运行测试：
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_main.py -v

# 运行特定测试
pytest tests/test_main.py::TestSkillExecutor::test_execute_success -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

### 第 6 步：注册 Skill 到 package.json

编辑 `package.json`，在 `claudePlugin.skills` 数组中添加新 Skill：

```json
{
  "claudePlugin": {
    "type": "skills",
    "skills": [
      {
        "name": "guanyuan-data-fetcher",
        "version": "1.0.0",
        "description": "自动化观远数据平台查询和报告生成",
        "mainPath": "skills/guanyuan-data-fetcher/main.py",
        "docPath": "skills/guanyuan-data-fetcher/SKILL.md",
        "command": "/guanyuan-data-fetcher",
        "dependencies": {
          "mcp": ["guanyuan-api"],
          "python": ["openpyxl>=3.0.0", "pandas>=1.3.0"]
        },
        "tags": ["data", "guanyuan", "reporting"]
      }
    ]
  }
}
```

### 第 7 步：创建 requirements.txt（如需特定依赖）

```
openpyxl>=3.0.0
pandas>=1.3.0
requests>=2.27.0
python-dotenv>=0.20.0
pydantic>=1.9.0
```

### 第 8 步：本地测试

```bash
# 1. 在开发模式下测试 Skill
claude plugin install . --dev

# 2. 测试 Skill 调用
/your-skill-name --param value

# 3. 运行单元测试
pytest tests/ -v

# 4. 检查代码质量
pylint skills/your-skill-name/main.py
flake8 skills/your-skill-name/

# 5. 类型检查（可选）
mypy skills/your-skill-name/main.py
```

### 第 9 步：更新文档

- 更新 README.md，在 "Skills 列表" 部分添加新 Skill
- 如果有特殊的使用示例，添加到 README.md 的 "使用示例" 部分

### 第 10 步：提交代码

```bash
# 1. 创建特性分支
git checkout -b feature/add-your-skill-name

# 2. 添加文件
git add skills/your-skill-name/
git add package.json
git add README.md

# 3. 提交代码（遵循约定式提交）
git commit -m "feat: add your-skill-name skill

This commit adds:
- Core skill implementation
- SKILL.md documentation
- Comprehensive test suite
- Integration with guanyuan-api

Closes #123"

# 4. 推送分支
git push origin feature/add-your-skill-name

# 5. 创建 Pull Request
```

## Skill 开发规范

### 代码规范

**遵循 PEP 8:**
```python
# 好的例子
def fetch_data(user_id: str, start_date: str) -> Dict[str, Any]:
    """获取用户数据"""
    pass

# 不好的例子
def FetchData(userID,startDate):
    # 获取用户数据
    pass
```

**错误处理:**
```python
# 好的例子
try:
    result = api_call()
except APIError as e:
    logger.error(f"API 调用失败: {e}")
    return {"status": "error", "error_code": "API_ERROR"}

# 不好的例子
try:
    result = api_call()
except:
    pass  # 吞掉异常！
```

**日志记录:**
```python
# 使用 logging 而不是 print
import logging
logger = logging.getLogger(__name__)

logger.info("开始处理请求")
logger.debug(f"参数: {params}")
logger.error("处理失败", exc_info=True)
```

### 测试规范

**覆盖率要求:**
- 至少 80% 的代码覆盖率
- 必须覆盖：正常路径、边界条件、异常处理

**测试命名:**
```python
# 好的例子
def test_execute_with_valid_parameters(self):
def test_execute_raises_error_when_missing_required_param(self):
def test_validate_date_range_with_invalid_format(self):

# 不好的例子
def test_1(self):
def test_execute(self):  # 太模糊
```

### 文档规范

**SKILL.md 必须包含:**
- [ ] 功能描述
- [ ] 使用示例
- [ ] 参数说明
- [ ] 输出格式
- [ ] 常见错误和解决方案
- [ ] 依赖说明

**代码注释:**
```python
# 好的例子：说明"为什么"而不是"是什么"
# 使用指数退避策略重试，避免频繁请求导致速率限制
retry_count = 0
while retry_count < MAX_RETRIES:
    ...

# 不好的例子：冗余注释
# 将 result 赋值给 r
r = result
```

## 常见问题 (FAQ)

### Q1: 我的 Skill 依赖某个 MCP 工具，用户没有权限怎么办？

**A:** 在 Skill 执行前检查权限，并提供清晰的错误提示和权限申请说明：

```python
def _check_permissions(self):
    """检查 MCP 工具权限"""
    try:
        api.verify_access()
    except PermissionError:
        return {
            "status": "error",
            "error_code": "PERMISSION_DENIED",
            "error_message": "缺少观远数据查询权限",
            "help": "请向观远平台管理员申请权限: https://guanyuan.platform/permission"
        }
```

### Q2: 如何处理 Skill 运行时间过长的问题？

**A:** 在 SKILL.md 中明确性能限制，并在代码中添加进度报告：

```python
def execute(self, **params):
    total_items = len(items)
    for i, item in enumerate(items):
        # 处理
        if i % 100 == 0:
            logger.info(f"进度: {i}/{total_items}")
```

### Q3: 如何让我的 Skill 支持批处理？

**A:** 在参数中接受列表，返回批处理结果：

```python
def execute(self, card_ids: List[str], date_range: str):
    results = []
    for card_id in card_ids:
        result = self._fetch_data(card_id, date_range)
        results.append(result)
    return {"batch_results": results}
```

### Q4: 如何在 Claude Code 中测试我正在开发的 Skill？

**A:** 使用开发模式安装并测试：

```bash
# 在 Skill 目录修改后，自动重新加载
claude plugin reload shuhe-work-skills

# 测试 Skill
/<your-skill-name> --param value
```

### Q5: 如何处理 Skill 之间的依赖？

**A:** 一个 Skill 可以调用另一个 Skill 的结果：

```python
# 在 SKILL.md 中明确记录依赖关系
# Depends on: guanyuan-data-fetcher
```

## 质量检查清单

提交 PR 前，请确认：

- [ ] 代码通过 `pylint` 和 `flake8` 检查
- [ ] 单元测试覆盖率 > 80%
- [ ] 所有测试通过：`pytest tests/ -v`
- [ ] SKILL.md 文档完整
- [ ] 在 package.json 中注册了 Skill
- [ ] README.md 已更新
- [ ] 本地测试成功：`/your-skill-name`
- [ ] 没有打印调试信息（使用 logger）
- [ ] 没有硬编码的 API 密钥或敏感信息
- [ ] 遵循了代码规范和最佳实践

## 获取帮助

- **问题讨论**: 在 GitHub Issues 中提问
- **设计评审**: 在 Pull Request 中讨论设计
- **团队沟通**: 内部 Slack / 钉钉 群组

---

感谢你的贡献！你的 Skill 将帮助整个团队提高工作效率。

