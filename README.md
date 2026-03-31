# 数禾工作场景 Skills 库

专为数禾 DS 团队设计的 Claude Code Skills Plugin，集成数据分析、报告生成、自动化工具和 oh-my-claudecode 完整工具链。

**目标用户**: 数禾数据分析师、企业级数据平台用户（观远、Dataphin）、需要自动化数据分析和报告生成的团队成员

**版本**: v1.4.0 | **Skills 总数**: 37 个（3 数禾定制 + 4 数据工具 + 30 oh-my-claudecode）

---

## 🚀 快速开始

### 1. 安装

```bash
# 从 GitLab 克隆
git clone git@gitlab.caijj.net:ouyangyi/claude-skills.git
cd claude-skills

# 安装插件
claude plugin install .
```

### 2. 验证安装

```bash
# 检查插件状态
claude plugin list | grep shuhe-work-skills

# 应该看到：
# ❯ shuhe-work-skills
#   Version: 1.1.0
#   Status: ✔ enabled
```

### 3. 开始使用

```bash
# 启动 Claude Code
claude

# 在对话中使用 skills
> /guanyuan-data-fetcher --help
> /autopilot "创建一个数据分析脚本"
> /plan "优化报告生成流程"
```

---

## 📚 已有 Skills

### 数禾定制 Skills

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **guanyuan-data-fetcher** | 自动化观远数据平台查询和报告生成 | • 定期数据报告生成<br>• 卡片数据批量导出<br>• Excel 报告自动化 | `/guanyuan-data-fetcher` |
| **guanyuan-monitor** | 自动化数据监控系统，基于规则告警 | • 指标异常监��<br>• 告警阈值设置<br>• 钉钉自动通知 | `/guanyuan-monitor` |
| **rta-exclude-strategy** | RTA排除策略自动分析工具 - 基于V8/V9RN二维交叉分析 | • 广告投放排除策略制定<br>• 模型分组交叉分析<br>• 自动生成Excel分析报告 | `/rta-exclude-strategy` |

**依赖**: 需要配置观远 API 权限（MCP: `guanyuan-data`）和钉钉通知（MCP: `messagengine-dingtalk`）

---

### 数据工具 Skills

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **sql-optimizer** | 优化和清理SQL查询，添加结构化注释和格式改进 | • SQL代码规范化<br>• 添加文档注释<br>• Hive/MaxCompute语法验证 | `/sql-optimizer` |
| **sql-runner** | 使用Dataphin MCP工具执行SQL文件 | • 自动提交查询<br>• 轮询结果<br>• 保存为CSV文件 | `/sql-runner` |
| **html-report-framework** | HTML报告生成通用框架 | • 报告设计美化<br>• 内容生成<br>• 排版调整 | `/html-report-framework` |
| **monthly-report-html-generator** | 自动生成月度运营数据HTML报告 | • 数据可视化<br>• 图表渲染<br>• 交互式报告 | `/monthly-report-html-generator` |

**依赖**: sql-runner 需要配置 Dataphin MCP（MCP: `sh_dp_mcp`）

---

### oh-my-claudecode 工具链

#### 🔄 核心工作流

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **autopilot** | 从想法到工作代码的全自动执行 | • 快速原型开发<br>• 端到端功能实现<br>• 自动化需求分析到代码生成 | `/autopilot` |
| **ralph** | 自我参照循环直到任务完成 | • 循环修复直到测试通过<br>• 持续优化直到达标<br>• 自动化调试修复 | `/ralph` |
| **ultrawork** | 高吞吐量并行执行引擎 | • 批量任务并行处理<br>• 多文件同时修改<br>• 大规模重构 | `/ultrawork` |
| **ultraqa** | QA 循环工作流（测试-验证-修复） | • 持续集成测试<br>• 自动化质量保证<br>• 回归测试修复 | `/ultraqa` |

#### 📋 规划与分析

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **plan** | 战略规划与可选访谈工作流 | • 项目实施计划<br>• 重构方案设计<br>• 技术架构规划 | `/plan` |
| **ralplan** | 共识规划入口，自动门控模糊请求 | • 需求不明确时自动引导<br>• 多方案评估<br>• 决策支持 | `/ralplan` |
| **deep-interview** | Socratic 深度访谈与数学歧义门控 | • 需求深度挖掘<br>• 复杂问题澄清<br>• 技术细节确认 | `/deep-interview` |
| **deep-dive** | 两阶段管道：trace + deep-interview | • 根因分析<br>• 复杂问题诊断<br>• 系统性调查 | `/deep-dive` |
| **trace** | 证据驱动的追踪，支持竞争假设 | • Bug 根因追踪<br>• 性能问题分析<br>• 代码逻辑验证 | `/trace` |

#### 👥 团队协作

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **team** | N 个协调 agent 共享任务列表 | • 多人协作开发<br>• 复杂项目分工<br>• 并行功能开发 | `/team` |
| **omc-teams** | CLI 团队运行时（tmux 面板） | • 进程级并行执行<br>• 多模型协同工作<br>• 大规模任务编排 | `/omc-teams` |
| **sciomc** | 编排并行 scientist agents 进行综合分析 | • 多维度数据分析<br>• 并行研究实验<br>• 综合报告生成 | `/sciomc` |

#### 🛠️ 开发工具

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **project-session-manager** | Worktree 优先的开发环境管理器 | • Issue/PR 独立工作区<br>• 多分支并行开发<br>• Tmux 会话管理 | `/project-session-manager` |
| **deepinit** | 深度代码库初始化，带层次化 AGENTS.md | • 新项目结构初始化<br>• 文档体系构建<br>• Agent 协作配置 | `/deepinit` |
| **ai-slop-cleaner** | 清理 AI 生成的代码冗余 | • 移除冗余注释<br>• 清理无用代码<br>• 代码质量提升 | `/ai-slop-cleaner` |
| **visual-verdict** | 结构化视觉 QA 判定 | • UI 截图对比<br>• 视觉回归测试<br>• 界面验收 | `/visual-verdict` |

#### 🤖 AI 模型集成

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **ask** | 路由到 Claude/Codex/Gemini 的顾问 | • 多模型咨询<br>• 第二意见验证<br>• 模型能力对比 | `/ask` |
| **ccg** | Claude-Codex-Gemini 三模型编排 | • 多模型协同决策<br>• 综合技术方案<br>• 交叉验证结果 | `/ccg` |

#### ⚙️ 配置与管理

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **setup** | 安装/更新路由 | • 首次环境配置<br>• 工具链安装 | `/setup` |
| **omc-setup** | 安装或刷新 oh-my-claudecode | • OMC 初始化<br>• 版本更新 | `/omc-setup` |
| **omc-doctor** | 诊断和修复安装问题 | • 环境问题排查<br>• 配置验证<br>• 依赖检查 | `/omc-doctor` |
| **mcp-setup** | 配置流行的 MCP 服务器 | • MCP 工具安装<br>• 服务器配置<br>• 能力扩展 | `/mcp-setup` |
| **configure-notifications** | 配置通知集成（Telegram/Discord/Slack） | • 任务完成通知<br>• 错误告警<br>• 协作提醒 | `/configure-notifications` |
| **hud** | 配置 HUD 显示选项 | • 界面定制<br>• 显示偏好设置 | `/hud` |
| **skill** | 管理本地 skills（列出、添加、删除、搜索、编辑） | • Skills 生命周期管理<br>• 自定义 skill 开发 | `/skill` |
| **omc-reference** | OMC agent 目录和工具参考 | • 工具文档查询<br>• Agent 能力查看 | `/omc-reference` |

#### 🔧 实用工具

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **cancel** | 取消任何活动的 OMC 模式 | • 中止长时间运行任务<br>• 紧急停止 | `/cancel` |
| **learner** | 从当前对话中提取学习的 skill | • 知识沉淀<br>• 技能积累<br>• 模式复用 | `/learner` |
| **writer-memory** | 作家的代理记忆系统 | • 文档写作辅助<br>• 内容连贯性维护<br>• 上下文记忆 | `/writer-memory` |
| **external-context** | 调用并行文档专家 agents | • 外部文档搜索<br>• API 文档查询<br>• 知识库检索 | `/external-context` |
| **release** | oh-my-claudecode 自动发布工作流 | • 版本发布自动化<br>• 变更日志生成 | `/release` |

---

## 🎯 待开发 Skills（数禾定制）

| 优先级 | Skill 名称 | 功能描述 | 预期使用场景 |
|-------|-----------|---------|------------|
| **P0** | **dataphin-analyzer** | Dataphin 数据表检索、查询和指标分析 | • 表结构探索<br>• 字段分析<br>• 数据质量检查 |
| **P0** | **model-evaluation-report** | 自动生成标准化模型评估报告 | • 区分度分析<br>• 稳定性评估（PSI）<br>• 模型对比报告 |
| **P1** | **weekly-monthly-report** | 基于规则的周报月报自动化生成 | • 定期业务报告<br>• 指标汇总<br>• 趋势分析 |
| **P1** | **anomaly-attribution** | CPS/LTV 等指标的异常检测和归因 | • 指标异常监控<br>• 根因定位<br>• 归因分析 |
| **P2** | **budget-optimizer** | MMM 模型驱动的预算优化建议 | • 营销预算分配<br>• ROI 优化<br>• 渠道配置推荐 |

**说明**:
- **P0**: 高优先级，正在开发或计划本季度完成
- **P1**: 中优先级，计划下季度开发
- **P2**: 低优先级，长期规划

---

## 💡 使用示例

### 数禾定制场景

```bash
# 查询观远数据并生成 Excel 报告
/guanyuan-data-fetcher --card-id 12345 --date-range "2024-01-01,2024-01-31"

# 启动观远数据监控（基于 JSON 配置文件）
/guanyuan-monitor --config configs/my_monitor.json

# RTA 排除策略分析
/rta-exclude-strategy --data_path data.csv --ctrl_group 0

# 未来：Dataphin 表检索
/dataphin-analyzer "用户行为表"

# 未来：生成模型评估报告
/model-evaluation-report --model "风控��型v2" --data "evaluation_data.csv"
```

### oh-my-claudecode 工作流

```bash
# 自动化开发：从想法到工作代码
/autopilot "创建一个用户认证系统，支持邮箱登录和JWT验证"

# 循环修复直到测试通过
/ralph "修复所有失败的单元测试"

# 深度需求访谈
/deep-interview "我想优化数据查询性能"

# 创建实现计划
/plan "重构报告生成模块"

# 团队协作模式（3个 agent 并行开发）
/team "实现新的数据分析功能"

# 配置 MCP 服务器
/mcp-setup

# 诊断安装问题
/omc-doctor
```

---

## 🤝 贡献指南

### 添加新 Skill

1. **创建 Skill 目录结构**
   ```
   skills/<skill-name>/
   ├── SKILL.md              # 必需：完整文档
   ├── main.py               # 必需：主执行逻辑
   ├── config.json           # 可选：配置文件
   ├── requirements.txt      # 可选：Python 依赖
   └── tests/                # 推荐：测试用例
   ```

2. **在 `package.json` 中注册**
   ```json
   {
     "name": "your-skill-name",
     "description": "简短功能描述",
     "docPath": "skills/your-skill-name/SKILL.md",
     "command": "/your-skill-name"
   }
   ```

3. **更新 README.md**：在对应分类的表格中添加一行

4. **测试并提交**
   ```bash
   # 运行验证脚本
   bash verify.sh

   # Git 提交
   git add .
   git commit -m "feat: add <skill-name> skill"
   git push origin master
   ```

### 质量标准

- ✅ 完整的 `SKILL.md` 文档（功能、参数、示例）
- ✅ 错误处理完善，边界条件清晰
- ✅ 测试覆盖率 > 80%（如果包含代码逻辑）
- ✅ 遵循团队编码规范

详细开发指南见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📖 文档资源

| 文档 | 说明 |
|-----|------|
| [QUICKSTART.md](QUICKSTART.md) | 快速开始指南，包含安装验证步骤 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 完整贡献指南和开发规范 |
| [CHANGELOG.md](CHANGELOG.md) | 版本变更记录 |
| [OMC_INTEGRATION_SUMMARY.md](OMC_INTEGRATION_SUMMARY.md) | oh-my-claudecode 集成详情 |
| [verify.sh](verify.sh) | 自动验证脚本 |

---

## 🆘 支持与反馈

### 问题排查

1. **Skills 不可用**
   ```bash
   # 检查插件状态
   claude plugin list

   # 重新启用插件
   claude plugin disable shuhe-work-skills
   claude plugin enable shuhe-work-skills

   # 运行诊断工具
   /omc-doctor
   ```

2. **MCP 工具失败**
   - 检查 MCP 配置：`/mcp-setup`
   - 查看权限设置
   - 参考 `~/.claude/CLAUDE.md` 第 16 节

3. **依赖问题**
   ```bash
   # 安装 Python 依赖
   cd skills/<skill-name>
   pip install -r requirements.txt
   ```

### 联系方式

- **GitLab Issues**: [创建 Issue](http://gitlab.caijj.net/ouyangyi/claude-skills/-/issues)
- **团队支持**: 联系数禾 DS 团队
- **紧急问题**: 直接联系仓库维护者

---

## 📜 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🔖 版本信息

- **当前版本**: v1.4.0
- **发布日期**: 2026-03-31
- **oh-my-claudecode 版本**: v4.9.3
- **最后更新**: 2026-03-31

**更新日志**: 查看 [CHANGELOG.md](CHANGELOG.md) 了解详细变更

---

<p align="center">
  <sub>专为数禾 DS 团队打造 | 基于 oh-my-claudecode 强化</sub>
</p>
