# Changelog

All notable changes to this project will be documented in this file.

## [1.9.0] - 2026-04-01

### Added
- **systematic-debugging** (45.1K 安装量，来自 obra/superpowers) - 系统化调试方法论，强制根因分析流程
- **python-testing-patterns** (10.8K 安装量，来自 wshobson/agents) - Python 测试最佳实践（pytest/fixtures/mocking）
- **README.md**: 新增"测试与调试 Skills"分类，包含 systematic-debugging 和 python-testing-patterns
- **README.md**: Skills 总数更��为 15 个（3 数禾定制 + 4 数据工具 + 3 治理规范 + 3 OMC 核心 + 2 测试工具）

### Changed
- **skill-governance**: 完善治理体系，新增三大流程
  - 阶段 2.5: 安全检测流程（skill-vetter 集成）- 强制红旗检测、权限范围、依赖安全
  - 阶段 3.5: 版本与依赖管理（skill-lifecycle-manager 集成）- semver 规范、依赖冲突检测
  - 新增"持续优化与自我进化"章节（skill-auto-evolver 集成）- 性能分析、A/B 测试、持续监控
  - 更新快速参考：包含安全检测、依赖检查、性能优化三个完整流程
  - 提交前检查清单新增：安全检测通过、依赖冲突检查、性能基准建立
- **.claude/rules/skill-governance.md**: 同步更新治理约束规则
  - 新增 skill 必须完成 6 个阶段（含安全检测）
  - 更新 skill 必须执行版本管理和依赖检查
  - 快速检查命令新增安全检测项

### Fixed
- **sql-optimizer**: 修复 validate_sql.py 第176行 `'NVLNVL'` 拼写错误为 `'NVL'`
- **sql-optimizer**: 添加文件路径安全验证（Path.resolve()）和10MB文件大小限制
- **sql-optimizer**: 修复 SKILL.md 文档路径示例（Windows兼容格式）
- **sql-optimizer**: 新增 evals/test_data/ 测试SQL文件（messy/commented/valid/syntax_error）
- **sql-runner**: SKILL.md 顶部添加 `⚠️ PROTOTYPE` 警告区块，明确 MCP 为 mock 实现
- **sql-runner**: sanitize_filename() 增强路径遍历防护（过滤 `..` 和绝对路径前缀）
- **guanyuan-monitor**: SKILL.md 和 README.md 标记为 IN DEVELOPMENT 原型状态
- **guanyuan-monitor**: 删除误导性文档 TEST_REPORT.md、simplified_test.py、test_skill.py
- **guanyuan-data-fetcher**: card_config.py 添加 validate_date() 日期验证（拒绝如 2026-02-29 的无效日期）
- **rta-exclude-strategy**: 提取共享工具函数到 utils.py（calc_spr、calc_cps、convert_old_rule_to_quantile）
- **rta-exclude-strategy**: report_generator.py 和 html_report_generator.py 改为从 utils 导入，消除代码重复

### Changed
- 更新 package.json 版本至 1.9.0

## [1.8.0] - 2026-03-31

### Added
- **Complete Advanced Features for skill-lifecycle-manager**
  - `marketplace.py`: NPX skills marketplace integration (search, install, update)
  - `rollback.py`: Git-based snapshot and rollback mechanism
  - `health_reporter.py`: Comprehensive health reports with Excel export (openpyxl)
  - New CLI commands: market-search, market-install, market-update, snapshot-create, snapshot-list, rollback, health-report

- **Complete Advanced Features for skill-auto-evolver**
  - `optimizer.py`: Skill optimization analysis and optimized version generation
  - `analyzer.py`: Performance bottleneck identification and analysis
  - `regression.py`: Regression testing framework with baseline comparison
  - `ab_testing.py`: A/B testing framework with traffic routing and winner determination
  - New CLI commands: optimize, analyze, regression-setup, regression-test, ab-create, ab-status, ab-promote

### Changed
- Updated skill-lifecycle-manager CLI with full feature integration
- Updated skill-auto-evolver CLI with complete analysis and testing capabilities
- Enhanced status commands to show all available features

### Technical Details
- All modules include comprehensive error handling and Windows compatibility
- CLI integration tested and verified for all new commands
- Optimization strategies: caching, parallel execution, error handling improvements
- A/B testing uses hash-based deterministic routing
- Regression testing supports baseline setup and version comparison
- Health reports support both console output and Excel export

## [1.7.0] - 2026-03-31 (Previous)

### Added
- **Complete Implementation of skill-lifecycle-manager**
  - Functional CLI with version management, dependency checking, and statistics tracking
  - `dependency_checker.py`: Check Python packages and MCP dependencies, generate dependency graphs
  - `stats_tracker.py`: SQLite-based execution tracking and performance statistics
  - `version_manager.py`: Enhanced with full CRUD operations for skill metadata
  - Working CLI commands: list, info, bump, check-deps, dep-graph, stats, health

- **Complete Implementation of skill-auto-evolver**
  - Functional CLI with execution tracking and performance analysis
  - `data_collector.py`: SQLite-based metrics collection with execution history
  - Working CLI commands: record, metrics, history, analyze, suggest, status
  - Performance metrics: success rate, latency percentiles (P50/P95/P99), execution counts
  - Basic optimization suggestions based on metrics

### Changed
- Updated package.json version to 1.7.0
- Updated README.md with complete feature descriptions
- Skills now have working implementations instead of placeholders

### Technical Details
- Infrastructure: `.omc/stats/` and `.omc/evolution/` directories with SQLite databases
- Both skills are production-ready with error handling and user-friendly CLI interfaces
- Full Python 3.8+ compatibility with proper encoding handling

### Notes
- External skills installation (self-improving-agent, skill-vetter) deferred due to network connectivity issues
- Can be added in future releases once network access is restored

## [1.6.0] - 2026-03-31

### Added
- **skill-lifecycle-manager** - Skills 生命周期管理器
  - 版本管理和语义化版本升级
  - 依赖检查和依赖图可视化
  - 使用统计和性能监控
  - Skills 库健康报告生成
  - 与 npx skills 市场集成（搜索、安装、更新）
  - 批量更新和安全回滚机制
- **skill-auto-evolver** - Skills 自动进化器
  - 自动收集 skill 执行数据（成功率、执行时间、错误模式）
  - 识别性能瓶颈和优化机会
  - 基于使用模式自动建议改进
  - 自动生成优化后的 skill 版本
  - A/B 测试框架（对比新旧版本效果）
  - 自动版本迭代和回归测试

### Changed
- 更新 package.json 版本至 1.6.0
- 更新 README.md 新增生命周期管理 Skills 分类
- Skills 总数：38 → 40（3 数禾定制 + 4 数据工具 + 30 OMC + 1 治理规范 + 2 生命周期管理）

## [1.5.0] - 2026-03-31

### Added
- **skill-governance** - Skills 库治理规范（强制性守门 skill）
  - 5 阶段治理流程：需求确认 → 结构创建 → 注册校验 → 文档同步 → 提交规范
  - 覆盖新增、更新、删除三种场景
  - 两种 SKILL.md 模板（执行型 / 工作流型）
  - 命名规范、注册规范、提交规范定义
  - `.claude/rules/skill-governance.md` 自动加载规则，确保 CC session 操作 skills/ 时强制遵循

### Changed
- 更新 package.json 版本至 1.5.0
- 更新 README.md 新增治理与规范 Skills 分类
- Skills 总数：37 → 38（3 数禾定制 + 4 数据工具 + 30 OMC + 1 治理规范）

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
