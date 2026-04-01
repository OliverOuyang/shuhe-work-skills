---
name: claude-dir-governance
description: .claude 目录配置治理和性能优化规范
version: 1.0.0
level: 3
tags:
  - governance
  - configuration
  - performance
  - claude-code
---

# Claude Directory Governance

.claude 目录配置治理框架，确保配置规范和性能优化。

## Description

此 skill 提供 .claude 目录的治理规范，包括 CLAUDE.md、MCP 服务器、Skills、Hooks 的变更管理流程，以及性能优化指导和自动化验证工具。

参考 skill-governance 的治理模式，适配用户级 Claude Code 配置管理。

## When to Use

当执行以下操作时自动触发：

- 修改 `~/.claude/CLAUDE.md`
- 修改 `~/.claude/mcp.json`
- 在 `~/.claude/skills/` 下新增/修改/删除 skill
- 修改 `~/.claude/rules/` 下的规则文件
- 修改 `~/.claude/settings.json` 中的 hooks 配置

## Usage

```bash
# 验证当前配置
/claude-dir-governance --validate

# 查看治理规则
/claude-dir-governance --rules

# 检查性能指标
/claude-dir-governance --performance
```

---

## 工作流 1：CLAUDE.md 变更

### 触发条件
- 修改 `~/.claude/CLAUDE.md` 内容
- 新增/删除 `~/.claude/rules/*.md` 文件

### 执行要求

#### 1. 变更前检查
- [ ] 确认变更目的（新增规则 / 优化结构 / 修复错误）
- [ ] 检查是否应拆分到 `rules/` 目录（单个主题 > 20 行）
- [ ] 验证交叉引用完整性（所有引用的文件存在）

#### 2. 内容规范
- **CLAUDE.md 作为索引**：保持精简（< 200 行），详细规则放 `rules/`
- **规则文件命名**：kebab-case（如 `report-workflow.md`）
- **交叉引用格式**：`详见 .claude/rules/<filename>.md`

#### 3. 变更后验证
```bash
# 检查所有交叉引用是否有效
grep -r "详见.*\.md" ~/.claude/CLAUDE.md | while read line; do
  file=$(echo "$line" | grep -oP '\.claude/rules/\K[^)]+')
  [ -f ~/.claude/rules/"$file" ] || echo "❌ 缺失: $file"
done
```

#### 4. 性能检查
- [ ] 确认 CLAUDE.md 行数未超过 200 行
- [ ] 确认单个 rules 文件未超过 100 行
- [ ] 避免重复内容（同一规则不应在多处出现）

---

## 工作流 2：MCP 服务器变更

### 触发条件
- 在 `mcp.json` 中新增/修改/删除 MCP 服务器配置

### 执行要求

#### 1. 新增 MCP 服务器

**步骤 1：需求确认**
- [ ] 明确 MCP 用途（数据查询 / 通知 / 文件操作等）
- [ ] 评估使用频率（高频 / 中频 / 低频）
- [ ] 检查是否有替代方案（已有 MCP 是否可满足）

**步骤 2：配置规范**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "command",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      },
      "disabled": false,
      "_comment": "用途说明和使用频率"
    }
  }
}
```

**步骤 3：性能评估**
- [ ] 低频 MCP（< 1次/天）应设置 `"disabled": true`
- [ ] 启用 Tool Search 功能（在 `settings.json` 中配置）
- [ ] 记录预期上下文占用（工具数量 × 平均描述长度）

**步骤 4：测试验证**
```bash
# 重启 Claude Code 后测试 MCP 连接
# 执行一次实际调用验证功能正常
```

#### 2. 禁用/删除 MCP 服务器

**评估影响**：
- [ ] 检查是否有 skills 依赖此 MCP
- [ ] 检查 CLAUDE.md 中是否有相关工作流引用
- [ ] 确认禁用后的替代方案

**操作规范**：
- 优先使用 `"disabled": true` 而非直接删除
- 在 `_comment` 中记录禁用原因和日期
- 更新相关文档中的 MCP 引用

---

## 工作流 3：Skills 变更

### 触发条件
- 在 `~/.claude/skills/` 下新增/修改/删除 skill 目录

### 执行要求

#### 1. 新增 Skill

**步骤 1：结构创建**
```
~/.claude/skills/<skill-name>/
├── SKILL.md          # 必需：skill 文档
├── scripts/          # 可选：执行脚本
└── resources/        # 可选：资源文件
```

**步骤 2：SKILL.md 规范**
```markdown
---
name: skill-name
description: 简短描述（一句话）
version: 1.0.0
---

# Skill 名称

## Description
详细功能说明

## Usage
/skill-name [参数]

## Examples
示例用法
```

**步骤 3：命名规范**
- 目录名：kebab-case（如 `my-skill`）
- 命令名：`/skill-name`（带斜杠前缀）
- 文档文件：`SKILL.md`（全大写）

#### 2. 更新 Skill

**变更评估**：
- [ ] 是否向后兼容（参数、输出格式）
- [ ] 是否需要更新版本号（遵循 semver）
- [ ] 相关文档是否同步更新

#### 3. 删除 Skill

**影响检查**：
- [ ] 是否有其他 skill 依赖
- [ ] CLAUDE.md 中是否有引用
- [ ] 是否需要迁移到其他 skill

---

## 工作流 4：Hooks 配置变更

### 触发条件
- 修改 `~/.claude/settings.json` 中的 hooks 配置

### 执行要求

#### 1. 新增 Hook

**安全检查**：
- [ ] 避免在 hook 中执行危险命令（rm -rf、git push --force 等）
- [ ] 使用 PowerShell 时注意路径转义和错误处理
- [ ] 设置合理的超时时间（默认 1000ms）

**配置规范**：
```json
{
  "hooks": {
    "PreToolUse:ToolName": {
      "command": "command",
      "timeout": 1000,
      "description": "Hook 用途说明"
    }
  }
}
```

#### 2. Hook 测试

**验证步骤**：
- [ ] 手动触发 hook 验证执行成功
- [ ] 检查错误日志（如有）
- [ ] 确认不影响正常工作流

---

## 性能优化原则

### 上下文管理
1. **CLAUDE.md 精简**：主文件 < 200 行，详细规则拆分到 `rules/`
2. **MCP 分层**：高频启用，低频禁用 + Tool Search
3. **渐进式加载**：核心规则始终加载，详细规则按需加载

### 优化目标
- CLAUDE.md 上下文：< 15K tokens
- MCP 工具上下文：< 20K tokens（启用 Tool Search 后）
- 总上下文占用：< 40K tokens

### 监控指标
- 首次响应延迟
- Token 使用量
- MCP 工具加载时间

---

## 验证工具

### 自动验证脚本

创建 `~/.claude/scripts/validate-config.sh`：

```bash
#!/bin/bash
# .claude 目录配置验证脚本

CLAUDE_DIR="${HOME}/.claude"

echo "=== .claude 配置验证 ==="

# 1. 检查 CLAUDE.md 交叉引用
echo "1. 检查 CLAUDE.md 交叉引用..."
grep -r "详见.*\.md" "$CLAUDE_DIR/CLAUDE.md" | while read line; do
  file=$(echo "$line" | grep -oP '\.claude/rules/\K[^)` ]+')
  [ -f "$CLAUDE_DIR/rules/$file" ] || echo "❌ 缺失: $file"
done

# 2. 检查 MCP 配置语法
echo "2. 检查 MCP 配置..."
if command -v jq &> /dev/null; then
  jq empty "$CLAUDE_DIR/mcp.json" && echo "✓ MCP 配置语法正确"
fi

# 3. 检查 skills 目录结构
echo "3. 检查 skills 目录..."
for skill_dir in "$CLAUDE_DIR/skills"/*/; do
  [ -f "$skill_dir/SKILL.md" ] || echo "❌ $(basename $skill_dir): 缺少 SKILL.md"
done

# 4. 性能检查
echo "4. 性能检查..."
lines=$(wc -l < "$CLAUDE_DIR/CLAUDE.md")
[ $lines -le 200 ] && echo "✓ CLAUDE.md 行数: $lines (≤ 200)" || echo "⚠ CLAUDE.md 行数: $lines (建议 ≤ 200)"

echo "=== 验证完成 ==="
```

---

## 禁止行为

- ❌ 在 CLAUDE.md 中堆砌超过 200 行的详细规则
- ❌ 启用所有 MCP 服务器（应按需启用）
- ❌ 在 skills 目录下创建无 SKILL.md 的目录
- ❌ 使用非 kebab-case 命名 skill 目录
- ❌ 在 hooks 中执行未经验证的危险命令
- ❌ 修改配置文件但不更新相关文档

---

## 回滚机制

### 变更前备份
```bash
# 备份 CLAUDE.md
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup.$(date +%Y%m%d_%H%M%S)

# 备份 mcp.json
cp ~/.claude/mcp.json ~/.claude/mcp.json.backup.$(date +%Y%m%d_%H%M%S)
```

### 快速回滚
```bash
# 恢复最近的备份
cp ~/.claude/CLAUDE.md.backup.YYYYMMDD_HHMMSS ~/.claude/CLAUDE.md
```

---

## Examples

### 基础用法：验证配置
```bash
/claude-dir-governance --validate
```

输出：
```
=== .claude 配置验证 ===
✓ 所有交叉引用有效
✓ MCP 配置语法正确
✓ 所有 skills 结构正确
✓ CLAUDE.md 行数: 146 (≤ 200)
=== 验证完成 ===
```

### 检查性能指标
```bash
/claude-dir-governance --performance
```

输出：
```
性能指标：
- CLAUDE.md: 146 行 (目标 < 200)
- 启用的 MCP: 4 个
- 预估上下文: ~35K tokens (目标 < 40K)
```

---

## Troubleshooting

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 交叉引用失效 | rules 文件被删除或重命名 | 更新 CLAUDE.md 中的引用路径 |
| MCP 配置语法错误 | JSON 格式不正确 | 使用 `jq` 验证语法 |
| Skills 缺少 SKILL.md | 创建目录���未添加文档 | 补充 SKILL.md 文件 |
| 性能下降 | CLAUDE.md 过长或 MCP 过多 | 拆分规则文件，禁用低频 MCP |

---

## Version History

- 1.0.0 (2026-04-01): 初始版本
  - 4 个工作流（CLAUDE.md、MCP、Skills、Hooks）
  - 性能优化原则和监控指标
  - 自动化验证工具
