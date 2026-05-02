# Contributing to Feizhan (飞站)

>  🛸 Thank you for your interest in contributing! We aim to make Feizhan the best one-click website generator.

## Code of Conduct

Be respectful. Be constructive. Be kind.

## How to Contribute

### 🐛 Bug Reports

1. Search [existing issues](https://github.com/luckychenxiaowen/feizhan/issues) first
2. Use the Bug Report template
3. Include: Python version, OS, error message, steps to reproduce

### ✨ Feature Requests

1. Check [existing requests](https://github.com/luckychenxiaowen/feizhan/issues)
2. Describe the problem your feature solves
3. Suggest an approach if you have one

### 🔧 Pull Requests

```bash
# 1. Fork & clone
git clone https://github.com/YOUR_USERNAME/feizhan.git
cd feizhan

# 2. Create a branch
git checkout -b feature/your-feature-name

# 3. Make changes
# - Follow existing code style (PEP 8)
# - Add comments for complex logic
# - Test your changes

# 4. Commit (Conventional Commits)
git commit -m "feat: add dark mode toggle"

# 5. Push & open PR
git push origin feature/your-feature-name
```

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

| Type | When to Use |
|------|------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `style:` | Code style (formatting, etc.) |
| `refactor:` | Code refactoring |
| `test:` | Adding tests |
| `chore:` | Maintenance tasks |

## Development Setup

```bash
# Feizhan uses only Python stdlib — no pip install needed!
cd feizhan/飞站skill
python feizhan.py --ui    # Launch dev server
python feizhan.py --help  # See all commands
```

## Style Guide

- **Python**: PEP 8, 4-space indentation
- **HTML/CSS/JS**: 2-space indentation
- **Comments**: Chinese for domain concepts, English for code internals
- **Naming**: snake_case for Python, camelCase for JS

## Getting Help

- Open a [Discussion](https://github.com/luckychenxiaowen/feizhan/discussions)
- Tag maintainers in issues
- Response time: within 48 hours

---

# 中文贡献指南

## 如何参与

1. **报告Bug** → 在 Issues 中使用 Bug 模板
2. **功能建议** → 描述问题 + 建议方案
3. **提交PR** → Fork → Branch → Commit → PR

## 提交规范

使用约定式提交（Conventional Commits）：
- `feat: 添加XX功能`
- `fix: 修复XX问题`
- `docs: 更新文档`
- `refactor: 重构XX模块`

## 代码风格

- Python: PEP 8
- HTML/CSS/JS: 2空格缩进
- 注释：中文用于领域概念，英文用于代码细节

## 联系我们

- Issue 或 Discussion 中提问题
- 通常在48小时内回复

---

**Feizhan is a community project. Every contribution matters. Thank you! 🛸**
