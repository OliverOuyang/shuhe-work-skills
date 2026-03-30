#!/bin/bash
# 验证 skills 插件结构

echo "=== 数禾工作场景 Skills 库验证 ==="
echo ""

# 检查必需文件
echo "检查必需文件..."
files=(".claudeplugin" "package.json" "README.md" "CONTRIBUTING.md")
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "✓ $file"
  else
    echo "✗ $file 缺失"
  fi
done
echo ""

# 检查 skills 目录
echo "检查 skills 目录..."
if [ -d "skills" ]; then
  skill_count=$(find skills -maxdepth 1 -type d ! -name "skills" ! -name ".*" | wc -l)
  echo "✓ skills 目录存在"
  echo "  发现 $skill_count 个 skills"
else
  echo "✗ skills 目录缺失"
fi
echo ""

# 验证每个 skill 是否有 SKILL.md
echo "验证 skill 文档..."
missing_docs=0
for skill_dir in skills/*/; do
  skill_name=$(basename "$skill_dir")
  if [ "$skill_name" != ".*" ]; then
    if [ ! -f "${skill_dir}SKILL.md" ]; then
      echo "  ⚠ $skill_name 缺少 SKILL.md"
      missing_docs=$((missing_docs + 1))
    fi
  fi
done

if [ $missing_docs -eq 0 ]; then
  echo "✓ 所有 skills 都有文档"
else
  echo "✗ $missing_docs 个 skills 缺少文档"
fi
echo ""

# 验证 package.json
echo "验证 package.json..."
if [ -f "package.json" ]; then
  if grep -q "shuhe-work-skills" package.json; then
    echo "✓ package name 正确"
  fi
  if grep -q "oh-my-claudecode" package.json; then
    echo "✓ 包含 oh-my-claudecode 关键词"
  fi
  version=$(grep -o '"version": "[^"]*"' package.json | head -1 | cut -d'"' -f4)
  echo "  版本: $version"
fi
echo ""

echo "=== 验证完成 ==="
echo ""
echo "安装命令："
echo "  claude plugin install $(pwd)"
