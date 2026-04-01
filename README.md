# 数禾工作场景 Skills 库

专为数禾 DS 团队设计的 Claude Code Skills Plugin，集成数据分析、报告生成、自动化工具。

**目标用户**: 数禾数据分析师、企业级数据平台用户（观远、Dataphin）、需要自动化数据分析和报告生成的团队成员

**版本**: v1.8.0 | **核心 Skills**: 15 个（3 数禾定制 + 4 数据工具 + 3 治理规范 + 3 OMC 核心 + 2 测试工具）

---

## 🚀 快速开始

### 1. 安装

```bash
# 从 GitHub 克隆
git clone https://github.com/OliverOuyang/shuhe-work-skills.git
cd shuhe-work-skills

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
| **html-report-framework** | HTML报告通用框架（ECharts + 动态居中 + 侧栏折叠 + 结论引擎） | • ECharts 图表渲染<br>• CSS max() 动态居中<br>• 可折叠侧栏<br>• 规则驱动结论 | `/html-report-framework` |
| **monthly-report-html-generator** | 月报HTML生成器（V04：f-string + ECharts + 14结论） | • 单脚本生成<br>• 23个ECharts图表<br>• 14个结论生成器<br>• 侧栏导航 | `/monthly-report-html-generator` |

**依赖**: sql-runner 需要配置 Dataphin MCP（MCP: `sh_dp_mcp`）

---

### 治理与规范 Skills

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **skill-governance** | Skills 库治理规范 - 强制性守门流程 | • 新增 skill 时遵循标准流程<br>• 更新 skill 时确保文档同步<br>• 删除 skill 时清理所有引用 | `/skill-governance` |
| **claude-dir-governance** | .claude 目录配置治理和性能优化 | • CLAUDE.md 变更管理<br>• MCP 服务器配置规范<br>• Skills 和 Hooks 治理<br>• 性能优化和验证 | `/claude-dir-governance` |
| **skill-lifecycle-manager** | Skills 生命周期管理器 | • 版��管理和升级<br>• 依赖检查和可视化<br>• 使用统计和健康报告 | `/skill-lifecycle-manager` |
| **skill-auto-evolver** | Skills 自动进化器 | • 性能数据收集<br>• 自动优化建议<br>• A/B测试和版本迭代 | `/skill-auto-evolver` |

**说明**: 任何 CC session 操作 skills/ 目录时，`.claude/rules/skill-governance.md` 会自动加载治理约束

---

### oh-my-claudecode 核心工具

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **autopilot** | 从想法到工作代码的全自动执行 | • 快速原型开发<br>• 端到端功能实现<br>• 自动化需求分析到代码生成 | `/autopilot` |
| **plan** | 战略规划与访谈工作流 | • 项目实施计划<br>• 重构方案设计<br>• 技术架构规划 | `/plan` |
| **team** | N 个协调 agent 共享任务列表 | • 多人协作开发<br>• 复杂项目分工<br>• 并行功能开发 | `/team` |

**说明**: 完整的 oh-my-claudecode 工具链包含 30+ skills，以上仅列出核心功能。完整列表见 `package.json`。

---

### 测试与调试 Skills

| Skill 名称 | 功能描述 | 使用场景 | 命令 |
|-----------|---------|---------|------|
| **systematic-debugging** | 系统化调试方法论 - 根因分析优先 | • Bug 修复前的根因调查<br>• 测试失败分析<br>• 多组件系统故障排查<br>• 防止随机修复和症状掩盖 | `/systematic-debugging` |
| **python-testing-patterns** | Python 测试最佳实践 - pytest/fixtures/mocking | • 编写单元测试<br>• 集成测试和 E2E 测试<br>• Mock 外部依赖<br>• TDD 开发流程 | `/python-testing-patterns` |

**说明**:
- **systematic-debugging** (45.1K 安装量，来自 obra/superpowers) - 强制根因调查流程，禁止未分析就修复
- **python-testing-patterns** (10.8K 安装量，来自 wshobson/agents) - 全面的 pytest 测试模式和最佳实践

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

# 创建实现计划
/plan "重构报告生成模块"

# 团队协作模式（3个 agent 并行开发）
/team "实现新的数据分析功能"
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

- **GitHub Issues**: [创建 Issue](https://github.com/OliverOuyang/shuhe-work-skills/issues)
- **团队支持**: 联系数禾 DS 团队
- **紧急问题**: 直接联系仓库维护者

---

## 📜 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🔖 版本信息

- **当前版本**: v1.8.0
- **发布日期**: 2026-04-01
- **oh-my-claudecode 版本**: v4.9.3
- **最后更新**: 2026-04-01

**更新日志**: 查看 [CHANGELOG.md](CHANGELOG.md) 了解详细变更

---

<p align="center">
  <sub>专为数禾 DS 团队打造 | 基于 oh-my-claudecode 强化</sub>
</p>
