# 快速开始指南

## 安装

### 方法 1：本地安装（推荐用于开发）

```bash
# 克隆或进入仓库目录
cd /path/to/shuhe-work-skills

# 直接安装
claude plugin install .
```

### 方法 2：从 Git URL 安装

```bash
claude plugin install <git-repository-url>
```

### 方法 3：通过 Marketplace 安装（需要先发布）

```bash
claude plugin marketplace install shuhe-work-skills
```

## 验证安装

安装后，验证 skills 是否可用：

```bash
# 检查已安装的插件
claude plugin list

# 应该看到：
# ❯ shuhe-work-skills
#   Version: 1.1.0
#   Status: ✔ enabled
```

## 使用测试

尝试运行一些基础命令：

```bash
# 测试 oh-my-claudecode skills
claude
> /omc-doctor

# 测试规划功能
claude
> /plan "测试任务规划"

# 测试数据查询（需要配置观远 API）
claude
> /guanyuan-data-fetcher --help
```

## 下一步

- 查看 [README.md](README.md) 了解所有可用 skills
- 阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何贡献新 skills
- 参考 [INSTALLATION.md](INSTALLATION.md) 获取详细安装说明

## 常见问题

### Q: 安装后 skills 不可用？

A: 尝试重新加载 Claude Code：
```bash
# 禁用后重新启用插件
claude plugin disable shuhe-work-skills
claude plugin enable shuhe-work-skills

# 或者重启 Claude Code
```

### Q: 如何更新到最新版本？

A: 如果是本地安装，拉取最新代码后重新安装：
```bash
git pull
claude plugin install . --force
```

### Q: 如何卸载？

A:
```bash
claude plugin uninstall shuhe-work-skills
```

## 技术支持

遇到问题？
- 查看 [issues](../../issues)
- 联系数禾 DS 团队
- 运行 `/omc-doctor` 诊断 oh-my-claudecode 相关问题
