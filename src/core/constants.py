# -*- coding: utf-8 -*-
"""
飞站 - 核心常量定义
"""

# 网站类型
WEBSITE_TYPES = {
    'company': {
        'name': '公司官网',
        'description': '展示公司形象、产品服务、联系方式',
        'default_features': ['intro', 'product', 'case', 'contact'],
        'page_structure': ['首页', '关于我们', '产品服务', '成功案例', '联系我们']
    },
    'product': {
        'name': '产品众筹',
        'description': '产品展示、众筹进度、预订购买',
        'default_features': ['intro', 'product', 'pricing', 'case', 'contact'],
        'page_structure': ['首页', '产品介绍', '众筹进度', '价格档位', '常见问题', '联系我们']
    },
    'portfolio': {
        'name': '个人作品集',
        'description': '个人作品展示、技能展示、联系方式',
        'default_features': ['intro', 'portfolio', 'case', 'contact'],
        'page_structure': ['首页', '关于我', '作品集', '技能展示', '联系我']
    },
    'blog': {
        'name': '博客',
        'description': '文章发布、分类浏览、评论互动',
        'default_features': ['intro', 'article', 'category', 'about'],
        'page_structure': ['首页', '文章列表', '分类目录', '关于博客', '留言板']
    },
    'forum': {
        'name': '论坛',
        'description': '主题讨论、用户互动、版块管理',
        'default_features': ['intro', 'topic', 'category', 'user', 'contact'],
        'page_structure': ['首页', '版块列表', '热门话题', '用户中心', '关于我们']
    }
}

# 设计风格
DESIGN_STYLES = {
    'modern': {
        'name': '现代简约',
        'description': '简洁大方，色彩纯净，留白充足',
        'primary_color': '#2563eb',
        'bg_color': '#ffffff',
        'text_color': '#1e293b'
    },
    'minimal': {
        'name': '极简主义',
        'description': '黑白灰调，极致精简，重点突出',
        'primary_color': '#000000',
        'bg_color': '#ffffff',
        'text_color': '#333333'
    },
    'bento': {
        'name': '卡片网格',
        'description': '卡片式布局，网格排列，层次分明',
        'primary_color': '#8b5cf6',
        'bg_color': '#f8fafc',
        'text_color': '#0f172a'
    },
    'brutalist': {
        'name': '粗犷野性',
        'description': '原始粗犷，线条硬朗，对比强烈',
        'primary_color': '#dc2626',
        'bg_color': '#fef2f2',
        'text_color': '#18181b'
    },
    'glass': {
        'name': '毛玻璃',
        'description': '磨砂玻璃效果，半透明模糊，现代科技感',
        'primary_color': '#0ea5e9',
        'bg_color': '#0f172a',
        'text_color': '#f1f5f9'
    },
    'neumorphic': {
        'name': '柔光拟态',
        'description': '柔和光影，凸凹立体，手感细腻',
        'primary_color': '#6366f1',
        'bg_color': '#e0e7ff',
        'text_color': '#1e1b4b'
    },
    'gradient': {
        'name': '渐变色彩',
        'description': '多彩渐变，流动感强，视觉冲击',
        'primary_color': '#f97316',
        'bg_color': '#fff7ed',
        'text_color': '#7c2d12'
    },
    'dark': {
        'name': '暗黑模式',
        'description': '深色背景，护眼舒适，高对比度',
        'primary_color': '#22d3d1',
        'bg_color': '#09090b',
        'text_color': '#e4e4e7'
    },
    'cyber': {
        'name': '赛博朋克',
        'description': '霓虹灯效，未来科技，赛博风格',
        'primary_color': '#ff0080',
        'bg_color': '#0a0a0f',
        'text_color': '#00ff9f'
    },
    'nature': {
        'name': '自然��新',
        'description': '自然色调，生机盎然，舒适放松',
        'primary_color': '#16a34a',
        'bg_color': '#f0fdf4',
        'text_color': '#14532d'
    }
}

# 功能模块
FEATURES = {
    'intro': {'name': '公司/个人介绍', 'required': True},
    'product': {'name': '产品服务介绍', 'required': False},
    'portfolio': {'name': '作品展示', 'required': False},
    'case': {'name': '成功案例', 'required': False},
    'pricing': {'name': '收费方式', 'required': False},
    'contact': {'name': '联系方式', 'required': False},
    'article': {'name': '文章列表', 'required': False},
    'category': {'name': '分类目录', 'required': False},
    'about': {'name': '关于我们', 'required': False},
    'topic': {'name': '话题讨论', 'required': False},
    'user': {'name': '用户中心', 'required': False},
    'chat': {'name': '在线咨询', 'required': False}
}

# 页面层级配置
PAGE_LEVELS = {
    1: {'name': '单页展示', 'nav_items': ['首页', '关于', '联系']},
    2: {'name': '标准官网', 'nav_items': ['首页', '关于', '产品', '案例', '联系']},
    3: {'name': '完整官网', 'nav_items': ['首页', '关于', '产品', '案例', '价格', '联系']}
}