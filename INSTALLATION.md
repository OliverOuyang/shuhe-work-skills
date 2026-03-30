# 安装指南 (Installation Guide)

本文档说明如何安装和配置 **shuhe-work-skills** Claude Code Skills 插件。

## 前置要求 (Prerequisites)

### Claude Code 版本
- **Claude Code**: 最新版本（推荐 v1.0.0+）
- 检查版本：
  ```bash
  claude --version
  ```

### Python 环境
- **Python**: 3.8+ (推荐 3.10 或更高)
- **pip**: 最新版本
- 检查环境：
  ```bash
  python --version
  pip --version
  ```

### 系统要求
- Windows 10+ / macOS 10.14+ / Linux (Ubuntu 18.04+)
- 网络连接（用于依赖安装和工具调用）

## 安装步骤 (Installation Steps)

### 方式 1: 从 Claude Code Marketplace 安装（推荐）

1. 在 Claude Code 中执行：
   ```bash
   claude plugin marketplace install shuhe-work-skills
   ```

2. 系统将自动：
   - 下载最新版本的插件
   - 安装所有必需的 Python 依赖
   - 配置环境变量和权限

3. 安装完成后，验证插件已加载：
   ```bash
   claude plugin list
   ```

### 方式 2: 从本地目录安装

1. 克隆或下载本仓库：
   ```bash
   git clone https://github.com/shuhe/work-skills.git
   cd work-skills
   ```

2. 安装插件：
   ```bash
   claude plugin install .
   ```

3. 或使用开发模式（开发和调试时使用）：
   ```bash
   claude plugin install . --dev
   ```

### 方式 3: 从源代码开发安装

用于本地开发和贡献新 Skill：

```bash
# 1. 克隆仓库
git clone https://github.com/shuhe/work-skills.git
cd work-skills

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装开发依赖
pip install -r requirements-dev.txt

# 5. 在开发模式下安装插件
claude plugin install . --dev
```

## 依赖安装 (Dependency Installation)

### 核心依赖

插件自动安装以下 Python 包：

| 包名 | 版本 | 用途 |
|------|------|------|
| openpyxl | >=3.0.0 | Excel 文件读写 |
| pandas | >=1.3.0 | 数据处理和分析 |
| requests | >=2.27.0 | HTTP 请求 |
| python-dotenv | >=0.20.0 | 环境变量管理 |
| pydantic | >=1.9.0 | 数据验证 |

### 可选依赖

根据使用的 Skill 选择安装：

```bash
# 数据科学扩展（用于高级分析）
pip install scikit-learn numpy scipy

# 数据库连接（如需直接连接数据库）
pip install sqlalchemy pymysql

# 可视化（用于生成图表）
pip install matplotlib seaborn
```

### 自动依赖安装

在第一次使用某个 Skill 时，系统会自动检查并提示安装缺失的依赖：

```bash
# ��果缺失依赖，Claude Code 会提示：
# ⚠️ Missing dependencies for guanyuan-data-fetcher
# Run: pip install openpyxl pandas requests

# 按提示安装即可
pip install openpyxl pandas requests
```

## 权限配置 (Permission Configuration)

### 观远数据权限申请

某些 Skill（如 `guanyuan-data-fetcher`）需要调用观远数据平台 API。

#### 步骤 1: 联系观远平台管理员

向观远数据平台管理员申请以下权限：

- **数据查询权限**：数据卡片和报告访问
- **指标查询权限**：指标元数据和数值查询
- **表元数据权限**：数据表结构和字段查询

#### 步骤 2: 配置 API 凭证

申请获得权限后，配置以下环境变量：

```bash
# 创建 .env 文件（项目根目录）
cat > .env << EOF
# 观远数据平台
GUANYUAN_USER_ID=your_user_id
GUANYUAN_API_TOKEN=your_api_token

# 可选：代理配置
HTTP_PROXY=
HTTPS_PROXY=
EOF
```

**重要**: `.env` 文件包含敏感信息，**不要提交到 Git**。已在 `.gitignore` 中配置排除。

#### 步骤 3: 验证权限

在 Claude Code 中运行验证命令：

```bash
/guanyuan-auth-check
```

预期输出：
```
✓ 观远数据权限验证成功
✓ 用户ID: your_user_id
✓ 有效期: 2026-12-31
✓ 可访问的卡片数: 45
```

### Dataphin 权限配置（如适用）

类似地为 Dataphin 配置权限：

```bash
# .env 文件中添加
DATAPHIN_WORKSPACE_ID=your_workspace_id
DATAPHIN_ACCESS_KEY=your_access_key
DATAPHIN_SECRET_KEY=your_secret_key
```

## 验证安装 (Verification)

### 快速验证

在 Claude Code 中运行以下命令验证安装：

```bash
# 1. 列出所有已安装的 Skills
/skills list

# 预期输出：
# Available Skills:
# - guanyuan-data-fetcher (v1.0.0) ✓
# - model-evaluation-report (v1.0.0) - Not installed
# - dataphin-query (v1.0.0) - Not installed
```

### 详细验证

```bash
# 1. 检查插件状态
claude plugin status shuhe-work-skills

# 2. 检查 Python 环境
python -m shuhe_work_skills.check_env

# 3. 测试观远数据连接
/guanyuan-test-connection
```

### 测试命令

```bash
# 运行内置测试
pytest tests/ -v

# 运行特定 Skill 的测试
pytest tests/test_guanyuan_fetcher.py -v

# 生成测试覆盖率报告
pytest tests/ --cov=skills --cov-report=html
```

## 故障排除 (Troubleshooting)

### 问题 1: 安装失败 - "找不到 Claude Code"

```
Error: Claude Code not found. Please install Claude Code first.
```

**解决方案:**
```bash
# 更新 Claude Code
claude self-update

# 验证安装
claude --version
```

### 问题 2: Python 依赖冲突

```
ERROR: pip's dependency resolver does not currently take into account...
```

**解决方案:**
```bash
# 使用虚拟环境隔离依赖
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 重新安装
pip install -r requirements.txt --force-reinstall
```

### 问题 3: 权限错误 - "Permission denied"

```
Error: Permission denied: /usr/local/lib/python...
```

**解决方案:**
```bash
# 使用用户级安装（推荐）
pip install --user -r requirements.txt

# 或在虚拟环境中安装
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 问题 4: 观远 API 认证失败

```
Error: Authentication failed for Guanyuan API
```

**解决方案:**
1. 检查 `.env` 文件中的凭证是否正确
2. 确保凭证未过期
3. 验证网络连接到观远平台
4. 运行 `/guanyuan-auth-check` 获得详细错误信息

### 问题 5: 超时问题

```
Error: Request timeout calling Guanyuan API
```

**解决方案:**
- 检查网络连接
- 增加超时时间（在 config 中配置）
- 联系观远平台管理员检查 API 可用性

## 更新和维护 (Updates & Maintenance)

### 检查更新

```bash
# 检查是否有新版本
claude plugin update-check shuhe-work-skills

# 自动更新
claude plugin upgrade shuhe-work-skills
```

### 版本锁定

如需固定特定版本：

```bash
# 指定版本安装
claude plugin install shuhe-work-skills==1.0.0

# 查看已安装版本
claude plugin show shuhe-work-skills
```

### 卸载

```bash
# 卸载插件
claude plugin uninstall shuhe-work-skills

# 清理缓存
claude plugin cache clear
```

## 高级配置 (Advanced Configuration)

### 自定义配置目录

```bash
# 设置配置文件位置
export SHUHE_SKILLS_CONFIG_DIR=/custom/config/path
```

### 启用调试日志

```bash
# 设置日志级别
export SHUHE_SKILLS_LOG_LEVEL=DEBUG

# 保存日志到文件
export SHUHE_SKILLS_LOG_FILE=/path/to/logfile.log
```

### 代理配置

如在公司网络中需使用代理：

```bash
# .env 文件中配置
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
NO_PROXY=localhost,127.0.0.1,*.company.com
```

## 获取帮助 (Getting Help)

- **文档**: [README.md](./README.md)
- **贡献指南**: [CONTRIBUTING.md](./CONTRIBUTING.md)
- **问题报告**: 创建 GitHub Issue
- **团队联系**: 数禾 DS 团队内部沟通群

## 安装清单 (Installation Checklist)

在使用插件前，请确认已完成：

- [ ] Claude Code 已安装且版本 ≥ 1.0.0
- [ ] Python 版本 ≥ 3.8
- [ ] 插件已安装：`claude plugin list` 显示 shuhe-work-skills
- [ ] Python 依赖已安装：`pip list | grep openpyxl pandas`
- [ ] 权限已配置（如需要）：`.env` 文件配置完成
- [ ] 验证命令通过：`/skills list` 显示可用 Skills
- [ ] 测试运行成功：选择一个 Skill 进行测试运行

完成以上步骤后，插件即可正常使用。

---

**最后更新**: 2026-03-30
**版本**: 1.0.0
