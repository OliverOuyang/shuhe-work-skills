# 数禾工作场景 Skills 库

专为数禾 DS 团队设计的 Claude Code Skills Plugin，集成数据分析、报告生成、自动化工具。

**目标用户**: 数禾数据分析师、企业级数据平台用户（Dataphin）、需要自动化数据分析和报告生成的团队成员

**版本**: v2.0.0 | **Skills**: 13 个（3 SQL工具 + 4 报告与Notebook + 1 Agent + 5 治理规范）

---

## 快速开始

### 1. 安装

```bash
# 从 GitLab 克隆
git clone git@gitlab.caijj.net:acquisition-strategy/acquisition-claude-skills.git
cd acquisition-claude-skills

# 安装插件
claude plugin install .
```

### 2. 验证安装

```bash
# 检查插件状态
claude plugin list | grep shuhe-work-skills
```

### 3. 开始使用

```bash
# 启动 Claude Code
claude

# 在对话中使用 skills
> /sql-optimizer --help
> /html-report-framework "生成分析报告"
```

---

## 已有 Skills

### SQL 工具

| Skill 名称 | 功能描述 | 命令 |
|-----------|---------|------|
| **sql-optimizer** | 优化和清理SQL查询，添加结构化注释和格式改进 | `/sql-optimizer` |
| **sql-runner** | 使用Dataphin MCP工具执行SQL文件，自动轮询结果 | `/sql-runner` |
| **sql-validate-and-export** | SQL 分段验证、自我修复、结果导出与智能可视化 | `/sql-validate-and-export` |

**依赖**: sql-runner / sql-validate-and-export 需要配置 Dataphin MCP（MCP: `sh_dp_mcp`）

---

### 报告与 Notebook

| Skill 名称 | 功能描述 | 命令 |
|-----------|---------|------|
| **html-report-framework** | HTML 报告通用框架（ECharts + 动态居中 + 侧栏折叠 + 结论引擎） | `/html-report-framework` |
| **monthly-report-html-generator** | 月报 HTML 生成器（f-string + ECharts + 14结论） | `/monthly-report-html-generator` |
| **notebook-standardizer** | Notebook 标准化规范（M1-M8 单元格规范 + 分析章节模板） | `/notebook-standardizer` |
| **notebook-executor** | Notebook 端到端执行器（SQL预校验 + 自动执行 + 错误诊断修复） | `/notebook-executor` |

---

### Agent

| Skill 名称 | 功能描述 | 命令 |
|-----------|---------|------|
| **self-improving-agent** | 通用自改进 Agent - 多记忆架构持续进化代码库 | `/self-improving-agent` |

---

### 治理与规范

| Skill 名称 | 功能描述 | 命令 |
|-----------|---------|------|
| **skill-governance** | Skills 库治理规范 - 强制性守门流程 | `/skill-governance` |
| **claude-dir-governance** | .claude 目录配置治理和性能优化 | `/claude-dir-governance` |
| **skill-lifecycle-manager** | Skills 生命周期管理器 - 版本管理、依赖检查 | `/skill-lifecycle-manager` |
| **skill-auto-evolver** | Skills 自动进化器 - 性能监控、A/B测试 | `/skill-auto-evolver` |
| **skill-vetter** | Skill 安全检测 - 红旗检测、权限范围扫描 | `/skill-vetter` |

**说明**: 操作 skills/ 目录时，`.claude/rules/skill-governance.md` 会自动加载治理约束

---

## 贡献指南

### 添加新 Skill

1. **创建 Skill 目录结构**
   ```
   skills/<skill-name>/
   ├── SKILL.md              # 必需：完整文档
   ├── scripts/              # 可选：执行脚本
   └── resources/            # 可选：资源文件
   ```

2. **在 `package.json` 中注册**

3. **更新 README.md 和 CHANGELOG.md**

4. **运行 `/skill-governance` 完成治理流程**

### 质量标准

- 完整的 `SKILL.md` 文档（含 YAML frontmatter）
- 错误处理完善，边界条件清晰
- 遵循团队编码规范

详细开发指南见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 文档资源

| 文档 | 说明 |
|-----|------|
| [CONTRIBUTING.md](CONTRIBUTING.md) | 完整贡献指南和开发规范 |
| [CHANGELOG.md](CHANGELOG.md) | 版本变更记录 |

---

## 版本信息

- **当前版本**: v2.0.0
- **发布日期**: 2026-04-17
- **最后更新**: 2026-04-17

**更新日志**: 查看 [CHANGELOG.md](CHANGELOG.md) 了解详细变更

---

<p align="center">
  <sub>专为数禾 DS 团队打造</sub>
</p>
