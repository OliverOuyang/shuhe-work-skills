# Changelog

All notable changes to this project will be documented in this file.

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
