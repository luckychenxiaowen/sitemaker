---
title: "飞站 - 一键网站生成器"
summary: "通过提示词或可视化界面一键生成公司官网/产品官网/作品集/博客/论坛"
read_when:
  - 用户要一键生成网站时使用
---

# 飞站skill - 一键网站生成器

## 功能概述

通过提示词prompt或可视化界面，一键生成各类网站：
- **网站类型**: 公司官网、产品众筹、个人作品集、博客、论坛
- **设计风格**: 10种流行CSS风格
- **功能模块**: 公司介绍、产品介绍、作品介绍、成功案例、收费方式、咨询联系
- **层级深度**: 1-3层可选

## 使用方式

### 方式一：Prompt模式
```bash
# 通过命令行提示词生成
python feizhan.py --type company --style modern --pages 2 --features intro,product,contact
```

### 方式二：可视化界面模式
```bash
# 启动可视化界面
python feizhan.py --ui
```

## 参数说明

| 参数 | 说明 | 可选值 |
|------|------|--------|
| --type | 网站类型 | company/product/portfolio/blog/forum |
| --style | 设计风格 | modern/minimal/bento/brutalist/glass/neumorphic/gradient/dark/cyber/nature |
| --pages | 层级深度 | 1/2/3 |
| --features | 功能模块 | intro/product/portfolio/case/pricing/contact/chat |
| --ui | 启动可视化界面 | bool |

## 输出结构

生成的网站保存在 `outputs/` 目录，包含：
- `index.html` - 首页
- `css/style.css` - 样式文件
- `js/main.js` - 交互脚本
- `images/` - 图片资源