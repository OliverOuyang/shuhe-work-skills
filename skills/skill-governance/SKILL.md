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
| **新增 skill** | 在 `skills/` 下创建新目录 | 全部 6 个阶段（含安全检测） |
| **更新 skill** | 修改现有 skill 的 SKILL.md 或实现代码 | 阶段 2（变更评估）+ 阶段 2.5（安全检测，按需）+ 阶段 3.5（版本管理）+ 阶段 4（文档同步）+ 阶段 5（提交） |
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

**文档长度要求**：200-400 行（推荐），硬性上限 500 行

```markdown
---
name: skill-name
description: 简短描述（一句话，包含关键词）
argument-hint: "命令行参数提示"
version: 1.0.0
level: 3
tags:
  - category1
  - category2
---

# <Skill 名称>

简短描述（1-2 句话）

## Description

详细功能说明（2-3 段，控制在 100 字内）

## Usage

```bash
/skill-name --param1 value1 [--option1 value2]
```

## Parameters

### Required
| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| param1 | string | 说明 | "value" |

### Optional
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| --option1 | string | "default" | 说明 |

## Examples

### 基础用法
```bash
/skill-name --param1 "example"
```

### 高级用法
```bash
/skill-name --param1 "example" --option1 "custom"
```

## Output

成功输出格式说明（简洁描述）

## Dependencies

### MCP Tools
- tool-name: 用途

### Python Packages
- package>=version: 用途

## Troubleshooting

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 错误 1 | 原因 | 方案 |

## Version History

- 1.0.0 (YYYY-MM-DD): 初始版本
```

**如果文档超过 500 行**，拆分为：
- `SKILL.md` - 核心使用文档（< 500 行）
- `ARCHITECTURE.md` - 架构设计
- `resources/` - 算法说明和参考资料

#### 模板 B：工作流 / 规范类 Skill（纯文档，无执行逻辑）

**文档长度要求**：150-300 行（推荐），硬性上限 400 行

```markdown
---
name: skill-name
description: 简短描述，包含触发关键词
level: 3
tags:
  - workflow
  - governance
---

# Skill 名称

## Purpose
简短说明目的（2-3 句话）

## When to Use
- 触发条件 1
- 触发条件 2

## Workflow
### Step 1: 步骤名称
简洁说明（避免冗长段落）

### Step 2: 步骤名称
简洁说明

## Guidelines
- 规则 1（一行一条）
- 规则 2

## Checklist
- [ ] 检查项 1
- [ ] 检查项 2

## Examples
**Good**: 正确示例（代码块）
**Bad**: 错误示例及原因（简短说明）
```

**文档精简原则**：
- 用表格代替长段落
- 用清单代替详细说明
- 示例控制在 10 行以内
- 避免重复内容

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

### 3.1 package.json 注册（新增时）

在 `package.json` 的 `claudePlugin.skills` 数组中添加条目。

**必需字段**：
```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "简短描述",
  "docPath": "skills/skill-name/SKILL.md",
  "command": "/skill-name",
  "tags": ["tag1", "tag2"]
}
```

**可选字段**：
```json
{
  "status": "prototype",          // 原型状态（核心功能未实现时必须）
  "mainPath": "skills/skill-name/main.py",
  "dependencies": {
    "mcp": ["tool-name"],
    "python": ["package>=version"]
  }
}
```

**关键检查**（基于质量审查发现）：
- ✅ YAML frontmatter 存在（SKILL.md 前 3 行是 `---`）
- ✅ 版本号存在（不能缺少 `version` 字段）
- ✅ 原型已标记（核心功能未实现时添加 `"status": "prototype"` 并在 description 前加 `[PROTOTYPE]`）
- ✅ 命令名一致（package.json 的 `command` 与目录名、YAML 的 `name` 一致）

### 3.2 一致性校验命令

**验证 JSON 语法**：
```bash
node -e "require('./package.json'); console.log('✓ JSON valid')"
```

**验证所有 skills 已注册**：
```bash
node -e "
const pkg = require('./package.json');
const fs = require('fs');
const registered = new Set(pkg.claudePlugin.skills.map(s => s.name));
const dirs = fs.readdirSync('skills', {withFileTypes: true})
  .filter(d => d.isDirectory() && d.name !== 'AGENTS.md')
  .map(d => d.name);
const unregistered = dirs.filter(d => !registered.has(d));
if (unregistered.length > 0) {
  console.log('❌ 未注册:', unregistered.join(', '));
} else {
  console.log('✓ 所有 skills 已注册');
}
"
```

---

## 阶段 2.5：安全检测（新增 skill 且包含执行代码时必须）

### 触发条件

当满足以下**任一条件**时，必须执行安全检测：

1. **新增 skill** 且包含可执行代码（Python、JavaScript、Bash 脚本等）
2. **更新 skill** 且修改了执行逻辑或添加了新的代码文件
3. **引入外部依赖**（npm packages、Python 库等）

### 使用 skill-vetter 进行安全检测

```bash
# 对新增或更新的 skill 执行安全检测
/skill-vetter

# skill-vetter 会自动检测当前操作的 skill 并执行：
# - Gen AI 安全评估（识别恶意代码模式）
# - Socket Security 分析（网络请求、文件操作风险）
# - Snyk 漏洞扫描（已知 CVE 检查）
```

### 检查标准

#### 1. 红旗检测（Red Flags）
- ❌ 硬编码的 API 密钥、密码、令牌
- ❌ 可疑的网络请求（未知域名、非 HTTPS）
- ❌ 文件系统危险操作（递归删除、权限修改）
- ❌ 代码混淆或编码的可执行代码
- ❌ eval() 或 exec() 等动态执行

#### 2. 权限范围（Permission Scope）
- 文件系统访问范围（只读 vs 读写）
- 网络访问需求（API 调用、外部服务）
- 环境变量使用（是否需要敏感配置）
- 系统命令执行（Bash、shell 命令）

#### 3. 依赖安全（Dependency Safety）
- 第三方库的安全评级（Snyk、Socket 评分）
- 已知漏洞检查（CVE 数据库）
- 依赖版本是否过时
- 传递依赖风险评估

### 处理流程

#### ✅ 安全检测通过
```
检测结果示例：
- Gen AI Assessment: Safe
- Socket Security: 0 alerts
- Snyk Vulnerability: Low Risk / No issues

下一步：
1. 在 SKILL.md 中添加 "## 安全检测" 章节记录结果
2. 继续阶段 3（注册校验）
```

#### ⚠️ 发现安全问题
```
1. 记录问题详情（风险类型、等级、受影响文件）
2. 修复安全问题：
   - 移除硬编码的敏感信息
   - 限制文件系统访问范围
   - 更新不安全的依赖版本
   - 添加输入验证和错误处理
3. 重新执行 /skill-vetter
4. 确认所有问题已解决后继续
```

#### ❌ 无法通过安全检测
如果 skill 设计本身存在不可避免的安全风险：
- 在 SKILL.md 中明确说明风险和使用限制
- 添加警告标签（如 "⚠️ 需要管理员权限"）
- 提供安全使用指南
- 与团队讨论是否应该开发该 skill

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

## 阶段 3.5：版本与依赖管理

### 版本号规范（Semantic Versioning）

所有 skills 必须遵循语义化版本规范（semver）：

```
MAJOR.MINOR.PATCH (例如: 1.2.3)

- MAJOR: 不兼容的 API 变更
- MINOR: 向后兼容的功能新增
- PATCH: 向后兼容的 bug 修复
```

### 何时使用 skill-lifecycle-manager

在以下场景中使用 `/skill-lifecycle-manager` 进行版本管理：

#### 1. 依赖检查
```bash
# 检查 skill 的依赖关系
/skill-lifecycle-manager deps check <skill-name>

# 输出示例：
# ✓ guanyuan-data-fetcher
#   依赖 MCP: guanyuan-data, messagengine-dingtalk
#   被依赖: 无
#   状态: 健康
```

**何时执行**：
- 新增 skill 时，检查是否引入循环依赖
- 更新 skill 时，确认依赖变更不影响其他 skills
- 删除 skill 前，确认没有被其他 skills 依赖

#### 2. 版本升级
```bash
# 升级 skill 版本
/skill-lifecycle-manager version bump <skill-name> <major|minor|patch>

# 示例：修复 bug 后执行
/skill-lifecycle-manager version bump sql-runner patch
# 版本从 1.2.3 → 1.2.4

# 示例：新增功能后执行
/skill-lifecycle-manager version bump guanyuan-monitor minor
# 版本从 1.2.3 → 1.3.0

# 示例：破坏性变更后执行
/skill-lifecycle-manager version bump skill-governance major
# 版本从 1.2.3 → 2.0.0
```

**版本升级策略**：
- **Bug 修复** → PATCH 递增
- **新增功能**（向后兼容）→ MINOR 递增
- **破坏性变更**（不兼容旧版本）→ MAJOR 递增

#### 3. 依赖冲突解决
```bash
# 可视化依赖图
/skill-lifecycle-manager deps visualize

# 检测冲突
/skill-lifecycle-manager deps conflicts

# 输出示例：
# ⚠️ 检测到依赖冲突：
# - skill-A 和 skill-B 都依赖 MCP:service-X
# - skill-A 需要 v2.0，skill-B 需要 v1.5
# 建议：升级 skill-B 以兼容 MCP:service-X v2.0
```

### 更新时检查清单

**必查项**：
```
✓ 版本号是否正确递增（符合 semver）
✓ 依赖冲突检查通过（无循环依赖）
✓ CHANGELOG.md 记录版本变更
✓ SKILL.md 更新版本号和变更说明
✓ 向后兼容性测试（如果是 MINOR/PATCH 更新）
```

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

#### 安全与依赖（新增或更新含执行代码时）
- [ ] 安全检测通过（skill-vetter）→ Gen AI: Safe, Socket: 0 alerts, Snyk: Low Risk
- [ ] 依赖检查通过（skill-lifecycle-manager deps check）→ 无循环依赖，无冲突
- [ ] 版本号正确递增（遵循 semver）
- [ ] 性能基准已建立（对高频 skills）

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
3. 安全检测 → /skill-vetter（有执行代码时必须）
4. 注册 → package.json 添加条目
5. 依赖检查 → /skill-lifecycle-manager deps check <name>
6. 文档 → README.md 添加表格行 + CHANGELOG.md 添加记录
7. 版本 → 递增 MINOR 版本号，三处同步
8. 提交 → feat(<name>): add <name> skill
```

### 更新 Skill 最小化流程

```
1. 评估变更 → 是否 breaking change？是否需要版本递增？
2. 修改文件 → 更新 SKILL.md + 实现代码
3. 安全检测 → /skill-vetter（修改执行逻辑或添加依赖时）
4. 版本管理 → /skill-lifecycle-manager version bump <name> <major|minor|patch>
5. 依赖检查 → /skill-lifecycle-manager deps check <name>
6. 文档同步 → CHANGELOG.md 添加记录
7. 提交 → fix/feat(<name>): <description>
```

### 性能优化流程（定期执行）

```
1. 性能分析 → /skill-auto-evolver analyze <name>
2. 创建优化分支 → git checkout -b feat/<name>-optimization
3. 实现优化 → 根据分析建议修改代码
4. A/B 测试 → /skill-auto-evolver experiment create <name> "<description>"
5. 监控 7-14 天 → /skill-auto-evolver experiment status <exp-id>
6. 应用或回滚 → apply/rollback 基于统计数据
7. 版本升级 → /skill-lifecycle-manager version bump <name> minor
8. 提交 → feat(<name>): optimize <description> (XX% faster)
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

## 持续优化与自我进化

### 何时触发性能优化

当满足以下**任一条件**时，考虑使用 `/skill-auto-evolver` 进行性能分析和优化：

1. **使用频率达到阈值**
   - Skill 被调用次数 > 50 次
   - 近期频繁使用（7 天内调用 > 10 次）

2. **发现性能问题**
   - 执行时间过长（> 30 秒）
   - 错误率较高（> 5%）
   - 用户反馈体验不佳

3. **定期优化**
   - 每月对高频 skills 进行性能审查
   - 季度对所有 skills 进行健康检查

### 性能分析与优化

#### 1. 执行性能分析
```bash
# 收集性能数据
/skill-auto-evolver analyze <skill-name>

# 输出示例：
# 📊 sql-runner 性能分析
# - 平均执行时间: 12.3 秒
# - 95分位延迟: 25.8 秒
# - 最慢执行: 45.2 秒（2024-01-15）
#
# 🎯 优化建议：
# 1. 添加查询结果缓存（预计减少 40% 执行时间）
# 2. 优化轮询频率（当前 5s，建议调整为 3s）
```

#### 2. 错误率分析
```bash
# 分析错误模式
/skill-auto-evolver errors <skill-name>

# 输出示例：
# ⚠️ guanyuan-data-fetcher 错误分析
# - 总调用: 127 次
# - 失败次数: 8 次（6.3%）
# - 主要错误类型:
#   - API 超时: 5 次（62.5%）
#   - 数据格式错误: 2 次（25%）
#   - 权限不足: 1 次（12.5%）
#
# 🎯 优化建议：
# 1. 添加超时重试机制（指数退避）
# 2. 增强数据格式验证
```

#### 3. 资源使用监控
```bash
# 监控资源消耗
/skill-auto-evolver resources <skill-name>

# 输出示例：
# 💾 monthly-report-html-generator 资源使用
# - 平均内存: 256 MB
# - 峰值内存: 512 MB
# - CPU 使用: 平均 45%
# - 磁盘 I/O: 23 MB 读取，145 MB 写入
#
# 🎯 优化建议：
# 1. 使用流式处理减少内存占用
# 2. 优化图表渲染算法（减少 CPU 使用）
```

### A/B 测试流程

对于重大优化，使用 A/B 测试验证效果：

#### 创建实验
```bash
# 创建 A/B 测试
/skill-auto-evolver experiment create <skill-name> <optimization-description>

# 示例：
/skill-auto-evolver experiment create sql-runner "add query result caching"

# 输出：
# ✓ 实验创建成功：exp-20260401-001
# - 对照组: sql-runner v1.2.3 (current)
# - 实验组: sql-runner v1.3.0-beta (with caching)
# - 流量分配: 50% / 50%
# - 监控指标: 执行时间、错误率、缓存命中率
```

#### 监控实验
```bash
# 查看实验结果
/skill-auto-evolver experiment status exp-20260401-001

# 输出示例：
# 📈 实验进展（7 天数据）
#
# 对照组（v1.2.3）:
# - 平均执行时间: 12.3s
# - 错误率: 3.2%
# - 样本量: 245 次
#
# 实验组（v1.3.0-beta）:
# - 平均执行时间: 7.8s ⬇️ 36.6%
# - 错误率: 2.8% ⬇️ 12.5%
# - 缓存命中率: 72%
# - 样本量: 238 次
#
# 统计显著性: p < 0.01 ✓
# 建议: 应用实验组版本到生产环境
```

#### 应用或回滚
```bash
# 应用优化（实验成功）
/skill-auto-evolver experiment apply exp-20260401-001

# 回滚优化（实验失败）
/skill-auto-evolver experiment rollback exp-20260401-001
```

### 完整优化工作流示例

```bash
# 1. 定期分析性能（每月一次）
/skill-auto-evolver analyze sql-runner

# 2. 根据建议创建优化分支
git checkout -b feat/sql-runner-optimization

# 3. 实现优化（添加缓存、减少轮询等）
# 编辑代码文件...

# 4. 创建 A/B 测试
/skill-auto-evolver experiment create sql-runner "query result caching"

# 5. 监控 7-14 天
/skill-auto-evolver experiment status exp-xxx

# 6. 根据数据决定是否应用
# 如果成功：
/skill-auto-evolver experiment apply exp-xxx
/skill-lifecycle-manager version bump sql-runner minor
git add . && git commit -m "feat: optimize sql-runner with caching (36% faster)"

# 如果失败：
/skill-auto-evolver experiment rollback exp-xxx
git checkout main && git branch -D feat/sql-runner-optimization
```

### 持续监控设置

为高频 skills 设置自动监控：

```bash
# 启用自动性能监控
/skill-auto-evolver monitor enable <skill-name> --threshold "execution_time>30s OR error_rate>5%"

# 触发条件示例：
# - 执行时间超过 30 秒时发送告警
# - 错误率超过 5% 时自动创建分析报告
# - 每月自动生成性能趋势报告
```

---

## 版本历史

### v1.1.0 (2026-04-01)
- 新增阶段 2.5：安全检测（skill-vetter 集成）
- 新增阶段 3.5：版本与依赖管理（skill-lifecycle-manager 集成）
- 新增"持续优化与自我进化"章节（skill-auto-evolver 集成）
- 更新触发表格：新增 skill 需执行 6 个阶段（含安全检测）
- 更新快速参考：包含安全检测、依赖检查、性能优化三个完整流程
- 提交前检查清单新增：安全检测、依赖检查、性能基准项

### v1.0.0 (2026-03-31)
- 初始版本
- 定义 5 阶段治理流程
- 覆盖新增、更新、删除三种场景
- 提供两种 SKILL.md 模板（执行型 / 工作流型）
- 定义命名规范、注册规范、提交规范
