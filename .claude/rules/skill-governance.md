# Skill Governance 自动加载规则

> 本规则文件由 Claude Code 在操作本仓库时自动加载。
> 完整治理规范见 `skills/skill-governance/SKILL.md`。

## 强制约束

当你在本仓库（shuhe-work-skills）中执行以下操作时，**必须先读取并遵循 `skills/skill-governance/SKILL.md` 中的完整流程**：

### 触发操作

1. **在 `skills/` 目录下创建新文件夹或文件**
2. **修改任何 `skills/*/SKILL.md` 文件**
3. **修改 `package.json` 中的 `claudePlugin.skills` 数组**
4. **删除 `skills/` 下的任何目录**

### 执行要求

- **新增 skill**：必须完成 5 个阶段（需求确认 → 结构创建 → 注册校验 → 文档同步 → 提交规范）
- **更新 skill**：必须完成变更评估 + 文档同步 + 提交规范
- **删除 skill**：必须完成影响评估 + 清理引用 + 提交规范

### 禁止行为

- 禁止在 `skills/` 下创建目录但不包含 `SKILL.md`
- 禁止添加 skill 文件但不在 `package.json` 中注册
- 禁止修改 skill 内容但不更新 `CHANGELOG.md`
- 禁止使用非 kebab-case 命名 skill 目录
- 禁止提交与现有 skill command 重名的新 skill

### 快速检查命令

在提交前，确认以下内容已同步更新：

```
必查文件：
✓ skills/<name>/SKILL.md    → 内容完整
✓ package.json              → skills 数组已注册
✓ README.md                 → 对应分类表格已添加
✓ CHANGELOG.md              → 变更记录已添加
✓ package.json.version      → 版本号已递增
```

### 参考文档

- 完整治理流程：`skills/skill-governance/SKILL.md`
- 贡献指南：`CONTRIBUTING.md`
- 变更记录：`CHANGELOG.md`
