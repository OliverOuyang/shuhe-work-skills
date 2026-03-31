---
name: skill-governance
description: "Skills 库治理规范 - 新增、更新、删除 skill 的强制性守门流程。当 CC session 操作 skills/ 目录时自动触发。"
triggers:
  - "新增 skill"
  - "添加 skill"
  - "创建 skill"
  - "更新 skill"
  - "修改 skill"
  - "删除 skill"
  - "add skill"
  - "create skill"
  - "update skill"
  - "remove skill"
level: 3
---

# Skill Governance - Skills 库治理规范

## 概述

本 skill 是 **shuhe-work-skills** 仓库的强制性治理规范。任�� CC session 在本仓库中新增、更新或删除 skill 时，**必须遵循本文档定义的流程**。

本规范的目的：
- 确保所有 skill 质量一致、文档完整
- 防止不规范的变更破坏现有 skill 生态
- 为团队协作提供可预期的标准化流程

## 触发条件

以下场景**必须**执行本规范流程：

| 场景 | 触发条件 | 必须执行的阶段 |
|------|---------|---------------|
| **新增 skill** | 在 `skills/` 下创建新目录 | 全部 5 个阶段 |
| **更新 skill** | 修改现有 skill 的 SKILL.md 或实现代码 | 阶段 2（变更评估）+ 阶段 4（文档同步）+ 阶段 5（提交） |
| **删除 skill** | 移除 `skills/` 下的目录 | 阶段 2（影响评估）+ 阶段 4（清理引���）+ 阶段 5（提交） |
| **修改 package.json skills 注册** | 变更 `claudePlugin.skills` 数组 | 阶段 3（一致性校验）+ 阶段 5（提交） |

---

## 阶段 1：需求确认（仅新增时必须）

在动手写任何代码或文档之前，必须完成以下确认。

### 1.1 功能定义检查清单

回答以下问题（可用 AskUserQuestion 工具向用户确认）：

- [ ] **问题定义**：这个 skill 解决什么具体问题？
- [ ] **目标用户**：谁会使用这个 skill？（数禾 DS 团队 / 全部 CC 用户 / 特定角色）
- [ ] **输入/输出**：核心输入是什么？预期输出是什么格式？
- [ ] **命名确认**：skill 名称使用 kebab-case（如 `my-new-skill`），且不与现有 37 个 skill 冲突

### 1.2 依赖和约束确认

- [ ] **MCP 依赖**：是否依赖 MCP 工具？列出具体名称（如 `sh_dp_mcp`、`sh_guanyuan_data`）
- [ ] **Python 依赖**：是否需要额外 Python 包？列出包名和最低版本
- [ ] **权限要求**：是否需要特定 API 权限或认证？
- [ ] **性能约束**：超时设置、数据量上限、内存限制

### 1.3 重复检查

**强制要求**：在创建前，必须检查现有 skill 是否已覆盖该需求。

```
检查步骤：
1. 读取 package.json 中 claudePlugin.skills 数组，列出所有已注册 skill
2. 搜索 skills/ 目录下所有 SKILL.md，检查功能描述是否有重叠
3. 如有重叠，向用户确认是新增还是扩展现有 skill
```

---

## 阶段 2：结构创建与校验

### 2.1 目录结构（新增时）

在 `skills/` 下创建以下结构：

```
skills/<skill-name>/
├── SKILL.md              # [必需] 完整文档（见 2.2 节模板）
├── main.py               # [按需] 有执行逻辑时必需
├── config.json           # [可选] 配置文件
├── requirements.txt      # [按需] 有 Python 依赖时必需
├── __init__.py           # [按需] 有 Python 代码时必需
├── resources/            # [可选] 参考资料、算法文档
└── tests/                # [按需] 有执行逻辑时必需
    ├── __init__.py
    ├── test_main.py
    └── fixtures/         # [可选] 测试数据
```

### 2.2 SKILL.md 模板

根据 skill 类型选择对应模板：

#### 模板 A：数禾定制 / 数据工具 Skill（有执行逻辑）

```markdown
# <Skill 名称>

## 1. 概述
一句话描述 skill 的目的和核心价值。

## 2. 功能说明
### 核心功能
- 功能 1
- 功能 2

### 支持的场景
- 场景 1
- 场景 2

### 限制和约束
- 限制 1
- 限制 2

## 3. 调用方式
### 命令格式
/<skill-name> [参数] [选项]

### 必需参数
| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| param1 | string | 说明 | "value" |

### 可选参数
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| --option1 | string | "default" | 说明 |

## 4. 输出格式
### 成功输出
（描述输出结构和示例）

### 错误输出
（描述错误码和错误信息格式）

## 5. 使用示例
### 基础用法
（具体命令示例）

### 高级用法
（带多参数的完整示例）

## 6. 依赖
### MCP 工具
- 工具名称：用途说明

### Python 包
- package>=version：用途说明

## 7. 错误处理
### 常见错误场景
- 场景 1：原因和解决方案
- 场景 2：原因和解决方案

## 8. 版本历史
### v1.0.0 (YYYY-MM-DD)
- 初始版本
```

#### 模板 B：工作流 / 规范类 Skill（纯文档，无执行逻辑）

```markdown
---
name: skill-name
description: 简短描述，包含触发关键词
---

# Skill 名称

## Purpose
这个 skill 的目的和解决的问题。

## When to Use
- 触发条件 1
- 触发条件 2

## Workflow
### Step 1: 步骤名称
详细说明

### Step 2: 步骤名称
详细说明

## Guidelines
关键规则和约束。

## Examples
### Good
正确使用示例

### Bad
错误使用示例及原因

## Checklist
- [ ] 检查项 1
- [ ] 检查项 2
```

### 2.3 命名规范校验

| 规则 | 正确 | 错误 |
|------|------|------|
| 目录名 | `my-new-skill` (kebab-case) | `MyNewSkill`, `my_new_skill` |
| 命令名 | `/my-new-skill` (带斜杠前缀) | `my-new-skill`, `/MyNewSkill` |
| 文档文件名 | `SKILL.md` (全大写) | `skill.md`, `Skill.md` |
| 代码文件名 | `main.py` (全小写) | `Main.py`, `main.PY` |
| 配置文件名 | `config.json` (全小写) | `Config.json` |

### 2.4 变更评估（更新/删除时）

**更新 skill 时**，必须检查：
- [ ] 变更是否向后兼容（参数签名、输出格式）
- [ ] 如有 breaking change，是否更新了版本号（遵循 semver）
- [ ] 相关文档是否同步更新

**删除 skill 时**，必须检查：
- [ ] 是否有其他 skill 依赖此 skill
- [ ] package.json 中是否已移除注册
- [ ] README.md 中是否已移除条目
- [ ] CHANGELOG.md 中是否记录了删除原因

---

## 阶段 3：注册与一致性校验

### 3.1 package.json 注册

在 `claudePlugin.skills` 数组中添加条目，遵循以下格式：

```json
{
  "name": "<skill-name>",
  "version": "1.0.0",
  "description": "简短功能描述 - 包含核心特性关键词",
  "docPath": "skills/<skill-name>/SKILL.md",
  "command": "/<skill-name>",
  "mainPath": "skills/<skill-name>/main.py",
  "dependencies": {
    "mcp": ["mcp-server-name"],
    "python": ["package>=version"]
  },
  "tags": ["tag1", "tag2"],
  "requiresAuth": false,
  "authType": ""
}
```

**字段规则**：
| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | kebab-case，与目录名一致 |
| `description` | 是 | 一句话描述，50 字以内 |
| `docPath` | 是 | 指向 SKILL.md 的相对路径 |
| `command` | 是 | 以 `/` 开头，与 name 一致 |
| `version` | 按需 | 有执行逻辑的 skill 必填 |
| `mainPath` | 按需 | 有 Python 入口时必填 |
| `dependencies` | 按需 | 有外部依赖时必填 |
| `tags` | 推荐 | 用于搜索和分类 |
| `requiresAuth` | 按需 | 需要认证时设为 true |

### 3.2 一致性校验检查清单

执行以下校验，**全部通过才能继续**：

- [ ] `package.json` 中的 `name` 与 `skills/` 下的目录名一致
- [ ] `package.json` 中的 `docPath` 指向的文件真实存在
- [ ] `package.json` 中的 `mainPath`（如有）指向的文件真实存在
- [ ] `package.json` 中的 `command` 不与现有 skill 重复
- [ ] `package.json` 中的 `version`（如有）与 SKILL.md 中的版本历史一致
- [ ] SKILL.md 中引用的所有 MCP 工具已在 `dependencies.mcp` 中声明

---

## 阶段 4：文档同步

### 4.1 README.md 更新

在 README.md 的对应分类表格中添加一行：

**数禾定制 Skills** 分类下：
```markdown
| **<skill-name>** | 功能描述 | • 场景1<br>• 场景2 | `/<skill-name>` |
```

**数据工具 Skills** 分类下：
```markdown
| **<skill-name>** | 功能描述 | • 场景1<br>• 场景2 | `/<skill-name>` |
```

**分类判断规则**：
| 分类 | 条件 |
|------|------|
| 数禾定制 Skills | 依赖观远/Dataphin MCP，面向数禾特定业务 |
| 数据工具 Skills | 通用数据处理工具（SQL、报告、可视化） |
| oh-my-claudecode 工具链 | OMC 生态的工作流 skill |
| 治理与规范 | 流程规范、质量控制类 skill |

### 4.2 CHANGELOG.md 更新

在文件顶部添加新版本记录：

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added（新增 skill 时）
- **<skill-name>** - 简短描述
  - 特性 1
  - 特性 2

### Changed（更新 skill 时）
- **<skill-name>** - 变更描述

### Removed（删除 skill 时）
- **<skill-name>** - 删除原因
```

**版本号递增规则**：
| 变更类型 | 版本递增 | 示例 |
|---------|---------|------|
| 新增 skill | MINOR (X.Y+1.0) | 1.4.0 → 1.5.0 |
| 更新 skill（非 breaking） | PATCH (X.Y.Z+1) | 1.4.0 → 1.4.1 |
| 更新 skill（breaking change） | MINOR (X.Y+1.0) | 1.4.0 → 1.5.0 |
| 删除 skill | MINOR (X.Y+1.0) | 1.4.0 → 1.5.0 |

### 4.3 package.json 版本同步

`package.json` 根级别的 `version` 字段必须与 CHANGELOG.md 最新版本号一致。

### 4.4 Skills 计数更新

README.md 头部的 Skills 总数必须更新：
```
**版本**: vX.Y.Z | **Skills 总数**: N 个（X 数禾定制 + Y 数据工具 + Z oh-my-claudecode + W 治理规范）
```

---

## 阶段 5：提交规范

### 5.1 Git 提交消息格式

遵循 Conventional Commits：

```
<type>(<scope>): <description>

<body>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**type 取值**：
| type | 场景 |
|------|------|
| `feat` | 新增 skill |
| `fix` | 修复 skill bug |
| `docs` | 仅文档变更 |
| `refactor` | 重构 skill 实现（不改功能） |
| `chore` | 维护性变更（依赖更新、配置调整） |

**scope 取值**：skill 名称，如 `feat(guanyuan-monitor): add threshold alerting`

### 5.2 必须提交的文件

**新增 skill 时**：
```
git add skills/<skill-name>/
git add package.json
git add README.md
git add CHANGELOG.md
```

**更新 skill 时**：
```
git add skills/<skill-name>/   # 变更的文件
git add package.json           # 如版本号变更
git add CHANGELOG.md           # 变更记录
```

### 5.3 提交前最终检查清单

**全部通过才能提交**：

#### 结构完整性
- [ ] SKILL.md 存在且内容完整（非空模板）
- [ ] SKILL.md 包含：概述、功能说明/工作流、使用示���、依赖说明
- [ ] 目录命名为 kebab-case
- [ ] 文件命名符合规范

#### 注册完整性
- [ ] package.json 中已注册（name, description, docPath, command）
- [ ] README.md 中已添加到对应分类表格
- [ ] CHANGELOG.md 中已添加变更记录
- [ ] 版本号已递增且三处一致（package.json, CHANGELOG, README 头部）

#### 质量要求（有执行逻辑时）
- [ ] 有测试文件（tests/test_main.py）
- [ ] 测试覆盖率 ≥ 80%
- [ ] 错误处理完善（不吞异常、使用 logging）
- [ ] 无硬编码密钥或敏感信息
- [ ] 代码通过 pylint/flake8 检查

#### 文档质量
- [ ] 使用示例可直接复制执行
- [ ] 参数说明包含类型、默认值、示例值
- [ ] 错误场景有解决方案
- [ ] 中英文一致（数禾定制 skill 用中文，工具类 skill 中英均可）

---

## 快速参考

### 新增 Skill 最小化流程

```
1. 确认需求 → 回答功能/依赖/场景三组问题
2. 创建目录 → skills/<name>/SKILL.md（必需）+ 实现文件（按需）
3. 注册 → package.json 添加条目
4. 文档 → README.md 添加表格行 + CHANGELOG.md 添加记录
5. 版本 → 递增 MINOR 版本号，三处同步
6. 提交 → feat(<name>): add <name> skill
```

### 更新 Skill 最小化流程

```
1. 评估变更 → 是否 breaking change？是否需要版本递增？
2. 修改文件 → 更新 SKILL.md + 实现代码
3. 文档同步 → CHANGELOG.md 添加记录
4. 版本 → 按需递增 PATCH 或 MINOR
5. 提交 → fix/feat(<name>): <description>
```

### 当前仓库状态参考

| 指标 | 值 |
|------|-----|
| 当前版本 | v1.6.0 |
| Skills 总数 | 40 |
| 数禾定制 | 3 (guanyuan-data-fetcher, guanyuan-monitor, rta-exclude-strategy) |
| 数据工具 | 4 (sql-optimizer, sql-runner, html-report-framework, monthly-report-html-generator) |
| OMC 工具链 | 30 |
| 治理规范 | 1 (skill-governance) |
| 生命周期管理 | 2 (skill-lifecycle-manager, skill-auto-evolver) |
| GitLab 地址 | gitlab.caijj.net/ouyangyi/claude-skills |

---

## ���规处理

如果检测到以下情况，**必须中止操作并提示用户**：

1. **无 SKILL.md**：在 skills/ 下创建了目录但没有 SKILL.md → 中止，提示补充
2. **未注册**：有 SKILL.md 但 package.json 未注册 → 中止，提示注册
3. **命名冲突**：新 skill 的 command 与现有 skill 重复 → 中止，提示改名
4. **版本未递增**：有实质性变更但版本号未更新 → 警告，提示更新
5. **文档不同步**：package.json 已更新但 README/CHANGELOG 未更新 → 警告，提示同步

---

## 版本历史

### v1.0.0 (2026-03-31)
- 初始版本
- 定义 5 阶段治理流程
- 覆盖新增、更新、删除三种场景
- 提供两种 SKILL.md 模板（执行型 / 工作流型）
- 定义命名规范、注册规范、提交规范
