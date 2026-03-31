# Changelog

All notable changes to this project will be documented in this file.

## [1.4.0] - 2026-03-31

### Added
- **sql-optimizer** - SQL 优化和清理工具
  - 添加结构化文档注释（文件头、章节标记、术语表）
  - 改进 SQL 格式（一致缩进、CASE 语句格式化）
  - Hive/MaxCompute 语法验证
  - 支持变量占位符（${bizdate}、${pt}）
- **sql-runner** - SQL 执行工具
  - 使用 Dataphin MCP 工具自动提交查询
  - 轮询查询状态（5秒间隔，5分钟超时）
  - 自动保存结果为 CSV（带时间戳文件名）
  - 完���的错误处理和边界测试
- **html-report-framework** - HTML 报告通用框架
  - PPT 风格排版模板
  - 响应式布局方案和配色方案库
  - 图表自动配置和布局引擎
  - 常见问题诊断清单和修复模式库
- **monthly-report-html-generator** - 月报 HTML 生成器
  - 从 Excel/CSV/Dataphin 自动生成交互式报告
  - Chart.js 集成（27+ 图表类型）
  - 侧边栏导航和可编辑内容
  - 数据准确性校验工具

### Changed
- 更新 package.json 版本至 1.4.0
- 更新 README.md 新增数据工具 Skills 分类
- Skills 总数：33 → 37（3 数禾定制 + 4 数据工具 + 30 OMC）
- 更新 .gitignore 添加 .omc/ 和生成文件规则

## [1.3.0] - 2026-03-30

### Added
- **rta-exclude-strategy** - RTA排除策略自动分析工具
  - 基于V8和V9RN模型的二维交叉分析
  - 置入置出算法自动生成排除策略
  - 企业规范的Excel分析报告输出
  - 支持安全过件率阈值自动计算
  - 完整的约束验证和合理性评估

### Changed
- 更新 package.json 版本至 1.3.0
- 更新 README.md 新增 rta-exclude-strategy 说明
- Skills 总数：32 → 33（3 数禾定制 + 30 OMC）

## [1.1.0] - 2026-03-30

### Added
- **oh-my-claudecode v4.9.3 完整集成** - 添加了 30+ oh-my-claudecode skills
  - 核心工作流：autopilot, ralph, ultrawork, ultraqa
  - 规划与分析：plan, ralplan, deep-interview, deep-dive, trace
  - 团队协作：team, omc-teams, sciomc
  - 开发工具：project-session-manager, deepinit, ai-slop-cleaner, visual-verdict
  - AI 模型集成：ask, ccg
  - 配置管理：setup, omc-setup, omc-doctor, mcp-setup, configure-notifications, hud, skill
  - 实用工具：cancel, learner, writer-memory, external-context, omc-reference, release

### Changed
- 更新 package.json 版本至 1.1.0
- 增强 README.md，添加完整的 skills 列表和使用示例
- 添加 `autoDiscoverSkills: true` 以自动发现 skills 目录中的所有技能

### Enhanced
- 关键词扩展：添加 oh-my-claudecode, omc, workflow, agents
- 描述更新：反映完整工具链集成

## [1.0.0] - 2026-03-30

### Added
- 初始化项目结构
- guanyuan-data-fetcher skill - 观远数据平台查询和报告生成
- 基础项目文档（README, CONTRIBUTING, INSTALLATION）
- package.json 配置
- .gitignore 和 .claudeplugin 配置
