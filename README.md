# 数禾工作场景 Skills 库

## 概述

这是一个专为数禾 DS 团队设计的 Claude Code Skills Plugin，包含数据分析、报告生成、自动化工具等常用工作场景的技能集合。

## ��标用户

- 数禾数据分析师
- 企业级数据平台用户（观远、Dataphin）
- 需要自动化数据分析和报告生成的团队成员

## 安装方法

### 通过 Claude Code Marketplace

```bash
claude plugin marketplace install shuhe-work-skills
```

### 手动安装

1. 克隆或下载本仓库到本地
2. 在 Claude Code 中运行：
   ```bash
   claude plugin install <path-to-this-directory>
   ```

## Skills 列表

### 数禾定制 Skills

1. **guanyuan-data-fetcher** - 自动化观远数据平台查询和报告生成

### oh-my-claudecode 完整工具链

本插件集成了 oh-my-claudecode (v4.9.3) 的所有 skills，提供企业级工作流自动化能力：

#### 核心工作流
- **autopilot** - 从想法到工作代码的全自动执行
- **ralph** - 自我参照循环直到任务完成
- **ultrawork** - 高吞吐量并行执行引擎
- **ultraqa** - QA 循环工作流（测试-验证-修复）

#### 规划与分析
- **plan** - 战略规划与可选访谈工作流
- **ralplan** - 共识规划入口，自动门控模糊请求
- **deep-interview** - Socratic 深度访谈与数学歧义门控
- **deep-dive** - 两阶段管道：trace + deep-interview
- **trace** - 证据驱动的追踪，支持竞争假设

#### 团队协作
- **team** - N 个协调 agent 共享任务列表
- **omc-teams** - CLI 团队运行时（tmux 面板）
- **sciomc** - 编排并行 scientist agents 进行综合分析

#### 开发工具
- **project-session-manager** - Worktree 优先的开发环境管理器
- **deepinit** - 深度代码库初始化，带层次化 AGENTS.md
- **ai-slop-cleaner** - 清理 AI 生成的代码冗余
- **visual-verdict** - 结构化视觉 QA 判定

#### AI 模型集成
- **ask** - 路由到 Claude/Codex/Gemini 的顾问
- **ccg** - Claude-Codex-Gemini 三模型编排

#### 配置与管理
- **setup** / **omc-setup** - 安装或刷新 oh-my-claudecode
- **omc-doctor** - 诊断和修复安装问题
- **mcp-setup** - 配置流行的 MCP 服务器
- **configure-notifications** - 配置通知集成（Telegram/Discord/Slack）
- **hud** - 配置 HUD 显示选项
- **skill** - 管理本地 skills（列出、添加、删除、搜索、编辑）

#### 实用工具
- **cancel** - 取消任何活动的 OMC 模式
- **learner** - 从当前对话中提取学习的 skill
- **writer-memory** - 作家的代理记忆系统
- **external-context** - 调用并行文档专家 agents
- **omc-reference** - OMC agent 目录和工具参考
- **release** - oh-my-claudecode 自动发布工作流

### 计划中的数禾 Skills

1. **Dataphin 分析** - Dataphin 数据表检索、查询和指标分析
2. **模型评估报告** - 自动生成标准化模型评估报告
3. **周报/月报生成** - 基于规则的周报月报自动化生成
4. **异常归因分析** - CPS/LTV 等指标的异常检测和归因
5. **预算分配优化** - MMM 模型驱动的预算优化建议

## 使用示例

### 基础用法

```bash
# 列出所有可用 Skills
/skills list

# 使用特定 Skill
/<skill-name> [arguments]
```

### 数禾定制场景

```bash
# 查询观远数据并生成报告
/guanyuan-data-fetcher --card-id 12345 --date-range "2024-01-01,2024-01-31"
```

### oh-my-claudecode 工作流示例

```bash
# 自动化开发：从想法到工作代码
/autopilot "创建一个用户认证系统，支持邮箱登录和JWT验证"

# 循环修复直到测试通过
/ralph "修复所有失败的单元测试"

# 并行执行多个独立任务
/ultrawork

# 深度需求访谈
/deep-interview "我想优化数据查询性能"

# 创建实现计划
/plan "重构报告生成模块"

# 团队协作模式
/team "实现新的数据分析功能"

# 配置 MCP 服务器
/mcp-setup

# 诊断安装问题
/omc-doctor
```

## 开发规范

### Skills 目录结构

每个 Skill 应包含：

```
skills/
└── <skill-name>/
    ├── SKILL.md          # Skill 说明文档
    ├── main.py           # 主执行逻辑
    ├── config.json       # 配置文件
    └── tests/            # 测试用例
```

### SKILL.md 必须包含

- Skill 名称和版本
- 功能描述
- 输入参数说明
- 输出格式
- 使用示例
- 依赖的 MCP 工具

### 代码规范

- 遵循 PEP 8 编码规范
- 必须包含完整的错误处理
- 必须包含测试用例
- 必须包含自测验证

## 贡献指南

### 添加新 Skill

1. 在 `skills/` 目录下创建新的 Skill 目录
2. 按照标准结构创建必要文件
3. 在 `package.json` 中注册 Skill
4. 编写完整的 `SKILL.md` 文档
5. 添加测试用例并确保通过
6. 提交 Pull Request

### Skill 开发流程

1. **需求确认** - 明确 Skill 要解决的具体问题
2. **设计文档** - 编写 SKILL.md，定义输入输出
3. **实现开发** - 编写主逻辑和错误处理
4. **自测验证** - 运行测试用例，确保全部通过
5. **文档完善** - 补充使用示例和注意事项
6. **代码审查** - 提交审查，获得批准后合并

### 质量标准

所有新增 Skill 必须满足：

- 功能完整，覆盖核心使用场景
- 错误处理完善，边界条件清晰
- 测试覆盖率 > 80%
- 文档清晰，包含使用示例
- 遵循团队编码规范

### 依赖管理

如果 Skill 依赖特定 MCP 工具：

- 在 SKILL.md 中明确列出依赖
- 提供 MCP 安装方法
- 处理 MCP 不可用的降级场景

## 维护和更新

### 版本管理

- 遵循语义化版本控制 (Semantic Versioning)
- 主版本号：不兼容的 API 变更
- 次版本号：向下兼容的功能新增
- 修订号：向下兼容的问题修复

### 更新流程

1. 更新对应 Skill 代码和文档
2. 更新 `package.json` 中的版本号
3. 更新 README.md 中的 Skills 列表
4. 测试所有相关 Skills 仍能正常工作
5. 发布新版本

## 常见问题

### Q: 如何调试 Skill？

A: 在 Skill 目录中运行：
```bash
python main.py --debug
```

### Q: 如何处理 MCP 工具失败？

A: 参考 CLAUDE.md 第 16 节 "MCP Tool Failure Recovery"

### Q: 如何添加依赖的 Python 包？

A: 在 Skill 目录下创建 `requirements.txt`

## 联系方式

- 问题反馈：创建 GitHub Issue
- 功能建议：创建 Feature Request
- 紧急问题：联系数禾 DS 团队

## License

MIT License - 详见 LICENSE 文件
