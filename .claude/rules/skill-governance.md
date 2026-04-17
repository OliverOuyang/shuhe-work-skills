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

- **新增 skill**：必须完成 6 个阶段（需求确认 → 结构创建 → 安全检测 → 注册校验 → 文档同步 → 提交规范）
- **更新 skill**：必须完成变更评估 + 文档同步 + 版本管理 + 提交规范
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
✓ skills/<name>/SKILL.md    → 内容完整且有 YAML frontmatter
✓ package.json              → skills 数组已注册且版本号正确
✓ README.md                 → 对应分类表格已添加
✓ CHANGELOG.md              → 变更记录已添加
✓ package.json.version      → 版本号已递增
✓ 安全检测通过（skill-vetter）→ 新增 skill 且包含执行代码时必须
✓ 原型 skill 已标记 status  → 核心功能未实现时必须添加 "status": "prototype"
✓ 文档长度合理              → SKILL.md 控制在 500 行以内
```

### SKILL.md 文档规范

**长度限制**（基于质量审查结果）：
- **推荐长度**：200-400 行（如 guanyuan-data-fetcher: 312 行）
- **硬性上限**：500 行
- **超长处理**：如超过 500 行，拆分为：
  - `SKILL.md` - 核心使用文档（< 500 行）
  - `ARCHITECTURE.md` - 架构设计详细说明
  - `ALGORITHM.md` - 算法原理和实现细节
  - `resources/` - 参考资料和示例

**必需组成部分**：
1. **YAML frontmatter**（必须，10-15 行）
   ```yaml
   ---
   name: skill-name
   description: 简短描述（一句话）
   argument-hint: "命令行参数提示"
   version: 1.0.0
   level: 3
   tags:
     - tag1
     - tag2
   ---
   ```

2. **核心章节**（按需，总计 < 500 行）
   - 功能描述（Description）
   - 使用方法（Usage）
   - 参数说明（Parameters）
   - 示例（Examples）
   - 输出格式（Output）
   - 故障排除（Troubleshooting）

---

## 质量审查发现的关键问题（2026-04-01）

基于 43 个 skills 的全面审查，以下是必须避免的常见问题：

### 🚨 严重问题（阻止提交）

1. **未注册 Skill**
   - 问题：目录存在但未在 package.json 中注册
   - 检查：`node -e "console.log(require('./package.json').claudePlugin.skills.map(s=>s.name))"`
   - 影响：无法通过命令调用，用户无法发现

2. **缺少 YAML Frontmatter**
   - 问题：SKILL.md 使用普通 Markdown 标题而非 YAML frontmatter
   - 检查：文件前 3 行必须是 `---`
   - 示例：
     ```yaml
     ---
     name: my-skill
     description: 简短描述
     version: 1.0.0
     tags: [tag1, tag2]
     ---
     ```

### ⚠️ 警告问题（建议修复）

3. **原型未标注**
   - 问题：核心功能未实现但未标记为 prototype
   - 修复：在 package.json 中添加 `"status": "prototype"` 字段
   - 修复：在 description 前添加 `[PROTOTYPE]` 标记

4. **缺少版本号**
   - 问题：package.json 注册条目缺少 version 字段
   - 修复：添加 `"version": "1.0.0"`

### ℹ️ 文档优化建议

5. **文档过长**
   - 问题：部分 SKILL.md 超过 500 行，难以维护
   - 标准：推荐 200-400 行，硬性上限 500 行
   - 超长处理：拆分为 SKILL.md + ARCHITECTURE.md + 资源文件

6. **数据清理不足**
   - 问题：用户输入未充分验证和清理
   - 建议：添加明确的输入验证和转义步骤

---

## 阶段 2.5: 安全检测（新增 skill 时必须）

### 触发条件

当满足以下**任一条件**时，必须执行安全检测：

1. **新增 skill** 且包含可执行代码（Python、JavaScript、Bash 脚本等）
2. **更新 skill** 且修改了执行逻辑或添加了新的代码文件
3. **引入外部依赖**（npm packages、Python 库等）

### 检查标准

使用 `/skill-vetter` 命令对 skill 进行安全检测，检查以下方面：

#### 1. 红旗检测（Red Flags）
- 硬编码的 API 密钥、密码、令牌
- 可疑的网络请求（未知域名、非 HTTPS）
- 文件系统危险操作（递归删除、权限修改）
- 代码混淆或编码的可执行代码
- eval() 或 exec() 等动态执行

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

#### 安全检测通过
```bash
# 1. 执行安全检测
/skill-vetter

# 2. 查看检测报告
# - Gen AI Assessment: Safe/Low Risk
# - Socket Security: 0 alerts
# - Snyk Vulnerability: Low Risk/No issues

# 3. 记录检测结果到 skill 文档
# 在 SKILL.md 中添加 "## 安全检测" 章节

# 4. 继续后续流程（注册校验、文档同步等）
```

#### 发现安全问题
```bash
# 1. 记录问题详情
# - 具体风险类型（红旗、权限、依赖）
# - 风险等级（Critical/High/Medium/Low）
# - 受影响的文件和代码行

# 2. 修复安全问题
# - 移除硬编码的敏感信息
# - 限制文件系统访问范围
# - 更新不安全的依赖版本
# - 添加输入验证和错误处理

# 3. 重新执行安全检测
/skill-vetter

# 4. 确认所有问题已解决后继续
```

#### 无法通过安全检测
如果 skill 设计本身存在不可避免的安全风险：
- 在 SKILL.md 中明确说明风险和使用限制
- 添加警告标签（如 "⚠️ 需要管理员权限"）
- 提供安全使用指南
- 考虑是否应该开发该 skill

---

## 阶段 3.5: 版本与依赖管理

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

### 命令示例

```bash
# 完整的版本管理工作流
# 1. 修改代码后，检查依赖
/skill-lifecycle-manager deps check my-skill

# 2. 确认变更类型，升级版本
/skill-lifecycle-manager version bump my-skill minor

# 3. 更新文档
# 编辑 SKILL.md 添加版本说明
# 编辑 CHANGELOG.md 记录变更

# 4. 验证依赖图
/skill-lifecycle-manager deps visualize

# 5. 提交变更
git add .
git commit -m "feat: update my-skill to v1.3.0"
```

---

## 附加流程: 持续优化与自我进化

### 何时触发

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

### 优化标准

使用 skill-auto-evolver 分析以下性能指标：

#### 1. 执行性能
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

#### 3. 资源使用
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

### 优化示例

```bash
# 完整的自我进化工作流
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

### 持续监控

建议为高频 skills 设置自动监控：

```bash
# 启用自动性能监控
/skill-auto-evolver monitor enable <skill-name> --threshold "execution_time>30s OR error_rate>5%"

# 触发条件示例：
# - 执行时间超过 30 秒时发送告警
# - 错误率超过 5% 时自动创建分析报告
# - 每月自动生成性能趋势报告
```

### 参考文档

- 完整治理流程：`skills/skill-governance/SKILL.md`
- 贡献指南：`CONTRIBUTING.md`
- 变更记录：`CHANGELOG.md`
