#!/usr/bin/env python3
"""
飞站 - 一键网站生成器 v2
通过Prompt或可视化界面生成各类网站
"""

import os, sys, json, argparse, webbrowser, threading, traceback
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')
UI_DIR = os.path.join(PROJECT_ROOT, 'src', 'ui')
for d in [OUTPUTS_DIR, UI_DIR, os.path.join(PROJECT_ROOT, 'src', 'templates'), os.path.join(PROJECT_ROOT, 'src', 'generators'), os.path.join(PROJECT_ROOT, 'src', 'core')]:
    os.makedirs(d, exist_ok=True)

WEBSITE_TYPES = {
    'company': {'name':'公司官网','description':'展示公司形象、产品服务、联系方式','default_features':['intro','product','case','contact']},
    'product': {'name':'产品众筹','description':'产品展示、众筹进度、预订购买','default_features':['intro','product','pricing','case','contact']},
    'portfolio':{'name':'个人作品集','description':'个人作品展示、技能展示、联系方式','default_features':['intro','portfolio','case','contact']},
    'blog':     {'name':'博客','description':'文章发布、分类浏览、评论互动','default_features':['intro','article','category','about']},
    'forum':    {'name':'论坛','description':'主题讨论、用户互动、版块管理','default_features':['intro','topic','category','user','contact']},
}

DESIGN_STYLES = {
    'modern':    {'name':'现代简约','primary':'#2563eb','bg':'#ffffff','text':'#1e293b','secondary':'#f1f5f9'},
    'minimal':   {'name':'极简主义','primary':'#000000','bg':'#ffffff','text':'#333333','secondary':'#fafafa'},
    'bento':     {'name':'卡片网格','primary':'#8b5cf6','bg':'#f8fafc','text':'#0f172a','secondary':'#e2e8f0'},
    'brutalist': {'name':'粗犷野性','primary':'#dc2626','bg':'#fef2f2','text':'#18181b','secondary':'#fee2e2'},
    'glass':     {'name':'毛玻璃','primary':'#0ea5e9','bg':'#0f172a','text':'#f1f5f9','secondary':'#1e293b'},
    'neumorphic':{'name':'柔光拟态','primary':'#6366f1','bg':'#e0e7ff','text':'#1e1b4b','secondary':'#c7d2fe'},
    'gradient':  {'name':'渐变色彩','primary':'#f97316','bg':'#fff7ed','text':'#7c2d12','secondary':'#fed7aa'},
    'dark':      {'name':'暗黑模式','primary':'#22d3d1','bg':'#09090b','text':'#e4e4e7','secondary':'#18181b'},
    'cyber':     {'name':'赛博朋克','primary':'#ff0080','bg':'#0a0a0f','text':'#00ff9f','secondary':'#1a0033'},
    'nature':    {'name':'自然清新','primary':'#16a34a','bg':'#f0fdf4','text':'#14532d','secondary':'#dcfce7'},
}

FEATURES = {
    'intro':    {'name':'公司/个人介绍','icon':'🏢'},
    'product':  {'name':'产品服务介绍','icon':'📦'},
    'portfolio':{'name':'作品展示','icon':'🎨'},
    'case':     {'name':'成功案例','icon':'✅'},
    'pricing':  {'name':'收费方式','icon':'💰'},
    'contact':  {'name':'联系方式','icon':'📞'},
    'article':  {'name':'文章列表','icon':'📝'},
    'category': {'name':'分类目录','icon':'📂'},
    'about':    {'name':'关于我们','icon':'ℹ️'},
    'topic':    {'name':'话题讨论','icon':'💬'},
    'user':     {'name':'用户中心','icon':'👤'},
    'chat':     {'name':'在线咨询','icon':'💡'},
}

# ============ API ============
class FeizhanAPI:
    def __init__(self):
        self.status = {'status':'idle','progress':0,'message':'','output':'','error_detail':''}
    def get_config(self):
        return {
            'website_types':{k:{'name':v['name'],'description':v['description']} for k,v in WEBSITE_TYPES.items()},
            'design_styles':{k:{'name':v['name'],'description':v.get('description','')} for k,v in DESIGN_STYLES.items()},
            'features':{k:v['name'] for k,v in FEATURES.items()},
            'page_levels':[1,2,3]
        }
    def generate(self, config):
        try:
            self.status = {'status':'generating','progress':0,'message':'初始化...','output':'','error_detail':''}
            wt = config.get('type','company')
            style = config.get('style','modern')
            pages = int(config.get('pages',2))
            features = config.get('features',[])
            if not features: features = []
            elif isinstance(features, str): features = [features]
            elif not isinstance(features, list): features = list(features or [])
            # Add intro if not present (always required)
            if 'intro' not in features: features.insert(0, 'intro')
            if wt not in WEBSITE_TYPES: raise ValueError(f"未知类型: {wt}")
            if style not in DESIGN_STYLES: raise ValueError(f"未知风格: {style}")
            if pages not in [1,2,3]: raise ValueError(f"无效层级: {pages}")
            self.status['progress']=10
            self.status['message']='生成页面结构...'
            output_path = generate_website(website_type=wt, style=style, pages=pages, features=features, custom_content=config.get('content',{}))
            self.status = {'status':'success','progress':100,'message':'完成!','output':output_path,'error_detail':''}
            return {'success':True,'output':output_path}
        except Exception as e:
            self.status = {'status':'error','progress':0,'message':f'失败:{e}','output':'','error_detail':traceback.format_exc()}
            return {'success':False,'error':str(e),'detail':traceback.format_exc()}
    def get_status(self): return self.status

# ============ 生成器核心 ============
def generate_website(website_type, style, pages, features, custom_content=None):
    if custom_content is None: custom_content = {}
    if not features: features = WEBSITE_TYPES[website_type].get('default_features',['intro','contact'])
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_name = f'{website_type}_{style}_{timestamp}'
    output_dir = os.path.join(OUTPUTS_DIR, output_name)
    os.makedirs(output_dir, exist_ok=True)
    type_config = WEBSITE_TYPES[website_type]
    style_config = DESIGN_STYLES[style]
    html_content = generate_html(website_type, type_config, style_config, pages, features, custom_content)
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f: f.write(html_content)
    css_content = generate_css(style, style_config)
    css_path = os.path.join(output_dir, 'css'); os.makedirs(css_path, exist_ok=True)
    with open(os.path.join(css_path, 'style.css'), 'w', encoding='utf-8') as f: f.write(css_content)
    js_content = generate_js(website_type, features)
    js_path = os.path.join(output_dir, 'js'); os.makedirs(js_path, exist_ok=True)
    with open(os.path.join(js_path, 'main.js'), 'w', encoding='utf-8') as f: f.write(js_content)
    with open(os.path.join(output_dir, 'site.json'), 'w', encoding='utf-8') as f:
        json.dump({'name':output_name,'type':website_type,'style':style,'pages':pages,'features':features,'created':timestamp}, f, ensure_ascii=False, indent=2)
    return output_dir

def generate_html(website_type, type_config, style_config, pages, features, custom_content):
    nav_items = generate_nav_items(pages, features)
    sections = generate_sections(website_type, features, custom_content)
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{type_config['name']} - 飞站生成</title>
<link rel="stylesheet" href="css/style.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap" rel="stylesheet">
</head>
<body>
<header class="header"><nav class="nav"><a href="#" class="logo">Logo</a><ul class="nav-list">{nav_items}</ul><button class="menu-toggle" aria-label="菜单"><span></span><span></span><span></span></button></nav></header>
<main class="main">{sections}</main>
<footer class="footer"><div class="footer-content"><p>&copy; 2026 飞站生成器 · {type_config['name']}</p><p class="footer-links"><a href="#">隐私政策</a> · <a href="#">服务条款</a> · <a href="#">联系我们</a></p></div></footer>
<script src="js/main.js"></script>
</body>
</html>'''

def generate_nav_items(pages, features):
    """生成导航 - 根据用户选择的功能动态生成"""
    nav_items = [['首页', '#hero']]
    
    # 关于导航 - 不论层级，只要选了 intro/about 就显示
    if 'intro' in features or 'about' in features:
        nav_items.append(['关于', '#about'])
    
    # 基础导航按层级
    if pages >= 2 and not ('intro' in features or 'about' in features):
        nav_items.append(['关于', '#about'])
    if pages >= 3:
        nav_items.append(['服务', '#services'])
    
    # 根据用户选择的功能模块添加导航
    feature_nav_map = {
        'product':  ['产品', '#products'],
        'portfolio':['作品', '#portfolio'],
        'case':     ['案例', '#cases'],
        'pricing':  ['价格', '#pricing'],
        'article':  ['文章', '#articles'],
        'topic':    ['话题', '#topics'],
        'contact':  ['联系', '#contact'],
        'chat':     ['咨询', '#chat'],
        'user':     ['用户', '#user'],
        'category': ['分类', '#categories'],
    }
    for fkey in features:
        if fkey in feature_nav_map:
            nav_items.append(feature_nav_map[fkey])
    
    html_parts = []
    for name, href in nav_items:
        html_parts.append(f'<li><a href="{href}" class="nav-link">{name}</a></li>')
    return '\n'.join(html_parts)

def generate_sections(website_type, features, custom_content):
    """生成所有区块 - 完整覆盖12个功能模块"""
    sections = []
    title = custom_content.get('title', '欢迎来到我们的网站')
    subtitle = custom_content.get('subtitle', '专业、专注、值得信赖')
    about_text = custom_content.get('about', '我们是一家专注于为客户提供优质服务的企业')

    # ---- Hero ----
    sections.append(f'''
<section id="hero" class="hero">
<div class="hero-content">
<h1>{title}</h1>
<p>{subtitle}</p>
<div class="hero-buttons">
<a href="#contact" class="btn btn-primary">立即咨询</a>
<a href="#about" class="btn btn-secondary">了解更多</a>
</div>
</div>
</section>''')

    # ---- 关于 (intro / about) ----
    if 'intro' in features or 'about' in features:
        sections.append(f'''
<section id="about" class="section about">
<div class="container">
<h2 class="section-heading">关于我们</h2>
<div class="about-grid">
<div class="about-text"><p>{about_text}</p><p>我们拥有专业的团队、丰富的经验和创新的理念，致力于为每一位客户提供最优质的服务。</p></div>
<div class="about-stats">
<div class="stat"><span class="stat-num">500+</span><span class="stat-label">服务客户</span></div>
<div class="stat"><span class="stat-num">10年</span><span class="stat-label">行业经验</span></div>
<div class="stat"><span class="stat-num">99%</span><span class="stat-label">客户满意度</span></div>
</div>
</div>
</div>
</section>''')

    # ---- 产品服务 (product) ----
    if 'product' in features:
        sections.append(f'''
<section id="products" class="section products">
<div class="container">
<h2 class="section-heading">产品服务</h2>
<div class="grid">
<div class="card"><div class="card-icon">&#x1F4E6;</div><h3>核心产品</h3><p>为您提供高品质的产品解决方案，满足多样化需求</p></div>
<div class="card"><div class="card-icon">&#x2699;&#xFE0F;</div><h3>定制服务</h3><p>根据需求量身定制，灵活适配各类场景</p></div>
<div class="card"><div class="card-icon">&#x1F3AF;</div><h3>技术支持</h3><p>7x24小时专业技术支持，快速响应</p></div>
<div class="card"><div class="card-icon">&#x1F52C;</div><h3>研发创新</h3><p>持续技术研发，引领行业前沿</p></div>
</div>
</div>
</section>''')

    # ---- 作品集 (portfolio) ----
    if 'portfolio' in features:
        sections.append(f'''
<section id="portfolio" class="section portfolio">
<div class="container">
<h2 class="section-heading">作品展示</h2>
<div class="gallery">
<div class="gallery-item"><div class="gi-img">01</div><h4>品牌设计</h4><p>企业VI视觉识别系统</p></div>
<div class="gallery-item"><div class="gi-img">02</div><h4>网站开发</h4><p>响应式全栈网站</p></div>
<div class="gallery-item"><div class="gi-img">03</div><h4>移动应用</h4><p>iOS/Android App</p></div>
<div class="gallery-item"><div class="gi-img">04</div><h4>数据平台</h4><p>大数据可视化系统</p></div>
</div>
</div>
</section>''')

    # ---- 成功案例 (case) ----
    if 'case' in features:
        sections.append(f'''
<section id="cases" class="section cases">
<div class="container">
<h2 class="section-heading">成功案例</h2>
<div class="cases-grid">
<div class="case-card"><div class="case-tag">数字化转型</div><h3>某大型制造企业</h3><p>帮助客户实现全流程数字化，效率提升40%</p><div class="case-result">成果: 年节省成本800万</div></div>
<div class="case-card"><div class="case-tag">智能升级</div><h3>某金融机构</h3><p>AI驱动的风控系统，准确率提升至99.5%</p><div class="case-result">成果: 风险损失降低60%</div></div>
<div class="case-card"><div class="case-tag">品牌重塑</div><h3>某零售集团</h3><p>全渠道品牌升级方案，线上销售增长200%</p><div class="case-result">成果: GMV突破10亿</div></div>
</div>
</div>
</section>''')

    # ---- 收费方式 (pricing) ----
    if 'pricing' in features:
        sections.append(f'''
<section id="pricing" class="section pricing">
<div class="container">
<h2 class="section-heading">收费方案</h2>
<div class="pricing-grid">
<div class="price-card"><h3>基础版</h3><p class="price"><span class="symbol">¥</span>999<span class="period">/月</span></p><ul><li>核心功能模块</li><li>基础技术支持</li><li>月报数据分析</li><li>5个用户账号</li></ul><a href="#contact" class="btn btn-outline">选择方案</a></div>
<div class="price-card featured"><div class="badge">推荐</div><h3>专业版</h3><p class="price"><span class="symbol">¥</span>2,999<span class="period">/月</span></p><ul><li>全部功能模块</li><li>优先技术支持</li><li>周报+数据分析</li><li>20个用户账号</li><li>API接口对接</li></ul><a href="#contact" class="btn btn-primary">立即开通</a></div>
<div class="price-card"><h3>企业版</h3><p class="price"><span class="symbol">¥</span>9,999<span class="period">/月</span></p><ul><li>功能完全定制</li><li>专属客户经理</li><li>实时数据看板</li><li>不限用户数</li><li>私有化部署可选</li></ul><a href="#contact" class="btn btn-outline">咨询方案</a></div>
</div>
</div>
</section>''')

    # ---- 联系方式 (contact) ----
    if 'contact' in features:
        sections.append(f'''
<section id="contact" class="section contact">
<div class="container">
<h2 class="section-heading">联系我们</h2>
<div class="contact-grid">
<div class="contact-info"><h3>联系方式</h3><p>&#x1F4CD; 北京市朝阳区XX大厦</p><p>&#x1F4DE; 400-000-0000</p><p>&#x2709;&#xFE0F; contact@example.com</p><p>&#x1F310; www.example.com</p></div>
<form class="contact-form"><input type="text" placeholder="您的姓名" required><input type="email" placeholder="电子邮箱" required><input type="text" placeholder="公司名称"><textarea placeholder="留言内容" rows="5" required></textarea><button type="submit" class="btn btn-primary">提交留言</button></form>
</div>
</div>
</section>''')

    # ---- 文章列表 (article) ----
    if 'article' in features:
        sections.append(f'''
<section id="articles" class="section articles">
<div class="container">
<h2 class="section-heading">最新文章</h2>
<div class="article-grid">
<article class="article-card"><div class="article-date">2026.05.01</div><h3>行业数字化转型趋势报告</h3><p>深度分析2026年各行业数字化转型的最新趋势与挑战...</p><a href="#" class="read-more">阅读更多 →</a></article>
<article class="article-card"><div class="article-date">2026.04.28</div><h3>AI如何改变传统业务模式</h3><p>人工智能正在重塑各行各业的业务流程和商业模式...</p><a href="#" class="read-more">阅读更多 →</a></article>
<article class="article-card"><div class="article-date">2026.04.25</div><h3>产品设计中的用户体验原则</h3><p>好的用户体验是产品成功的基石，聊聊设计中那些关键原则...</p><a href="#" class="read-more">阅读更多 →</a></article>
</div>
</div>
</section>''')

    # ---- 分类目录 (category) ----
    if 'category' in features:
        sections.append(f'''
<section id="categories" class="section categories">
<div class="container">
<h2 class="section-heading">分类目录</h2>
<div class="category-grid">
<a href="#" class="category-card"><span class="cat-icon">&#x1F4CA;</span><span>数据分析</span><span class="cat-count">12篇</span></a>
<a href="#" class="category-card"><span class="cat-icon">&#x1F4BB;</span><span>技术开发</span><span class="cat-count">8篇</span></a>
<a href="#" class="category-card"><span class="cat-icon">&#x1F3A8;</span><span>设计创意</span><span class="cat-count">15篇</span></a>
<a href="#" class="category-card"><span class="cat-icon">&#x1F4C8;</span><span>商业策略</span><span class="cat-count">6篇</span></a>
<a href="#" class="category-card"><span class="cat-icon">&#x1F4D6;</span><span>行业资讯</span><span class="cat-count">20篇</span></a>
<a href="#" class="category-card"><span class="cat-icon">&#x1F393;</span><span>教程指南</span><span class="cat-count">10篇</span></a>
</div>
</div>
</section>''')

    # ---- 话题讨论 (topic) ----
    if 'topic' in features:
        sections.append(f'''
<section id="topics" class="section topics">
<div class="container">
<h2 class="section-heading">热门话题</h2>
<div class="topic-list">
<div class="topic-item"><div class="topic-avatar">A</div><div class="topic-content"><h4>如何选择合适的技术栈？</h4><p>前端React还是Vue？后端Node还是Python？</p><div class="topic-meta"><span>48回复</span><span>2小时前</span></div></div></div>
<div class="topic-item"><div class="topic-avatar">B</div><div class="topic-content"><h4>2026年AI行业前景讨论</h4><p>大模型时代的创业机会在哪里？</p><div class="topic-meta"><span>126回复</span><span>5小时前</span></div></div></div>
<div class="topic-item"><div class="topic-avatar">C</div><div class="topic-content"><h4>远程办公的最佳实践</h4><p>如何提高远程团队的协作效率？</p><div class="topic-meta"><span>89回复</span><span>1天前</span></div></div></div>
</div>
</div>
</section>''')

    # ---- 用户中心 (user) ----
    if 'user' in features:
        sections.append(f'''
<section id="user" class="section user">
<div class="container">
<h2 class="section-heading">用户中心</h2>
<div class="user-grid">
<div class="user-card"><div class="avatar">&#x1F464;</div><h3>欢迎回来</h3><p>登录以管理您的账户和设置</p><a href="#" class="btn btn-primary">登录 / 注册</a></div>
<div class="user-card"><div class="avatar">&#x1F4CA;</div><h3>我的数据</h3><p>查看使用统计和历史记录</p></div>
<div class="user-card"><div class="avatar">&#x2699;&#xFE0F;</div><h3>账户设置</h3><p>个人信息、安全设置、偏好</p></div>
</div>
</div>
</section>''')

    # ---- 在线咨询 (chat) ----
    if 'chat' in features:
        sections.append(f'''
<section id="chat" class="section chat-section">
<div class="container">
<h2 class="section-heading">在线咨询</h2>
<div class="chat-box">
<div class="chat-messages">
<div class="chat-msg assistant"><div class="msg-avatar">&#x1F916;</div><div class="msg-bubble">您好！有什么可以帮助您的？</div></div>
<div class="chat-msg assistant"><div class="msg-avatar">&#x1F916;</div><div class="msg-bubble">您可以咨询产品详情、技术问题或合作事宜。</div></div>
<div class="chat-msg user-msg"><div class="msg-avatar">&#x1F464;</div><div class="msg-bubble">你好，我想了解一下你们的产品</div></div>
</div>
<div class="chat-input"><input type="text" placeholder="输入您的问题..."><button class="btn btn-primary">发送</button></div>
</div>
<p class="chat-tip">&#x1F4DE; 或直接拨打: <strong>400-000-0000</strong></p>
</div>
</section>''')

    return '\n'.join(sections)


# ============ 10种差异化CSS风格 ============
def generate_css(style_name, style):
    """根据风格生成真正不同的CSS"""
    base = f'''/* 飞站生成器 - {style['name']} */
:root{{--primary:{style['primary']};--bg:{style['bg']};--text:{style['text']};--secondary:{style['secondary']};}}'''

    # 每种风格的核心差异CSS
    style_css_map = {
        'modern': f'''
{base}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;}}
.container{{max-width:1200px;margin:0 auto;padding:0 20px;}}
.header{{position:fixed;top:0;left:0;right:0;z-index:1000;background:rgba(255,255,255,0.9);backdrop-filter:blur(10px);border-bottom:1px solid rgba(0,0,0,0.05);}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:14px 40px;}}
.logo{{font-size:1.5rem;font-weight:700;color:var(--primary);text-decoration:none;}}
.nav-list{{display:flex;gap:28px;list-style:none;}}
.nav-link{{color:var(--text);text-decoration:none;font-size:0.9rem;transition:color .3s;}}
.nav-link:hover{{color:var(--primary);}}
.menu-toggle{{display:none;flex-direction:column;gap:5px;background:none;border:none;cursor:pointer;}}
.menu-toggle span{{width:24px;height:2px;background:var(--text);}}
.hero{{min-height:90vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 20px;background:linear-gradient(135deg,var(--bg) 0%,var(--secondary) 100%);}}
.hero h1{{font-size:3rem;font-weight:900;margin-bottom:16px;}}
.hero p{{font-size:1.15rem;opacity:0.75;margin-bottom:28px;}}
.hero-buttons{{display:flex;gap:14px;justify-content:center;}}
.btn{{padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:500;font-size:0.95rem;transition:all .3s;display:inline-block;}}
.btn-primary{{background:var(--primary);color:#fff;border:none;}}
.btn-primary:hover{{opacity:0.9;transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,0.15);}}
.btn-secondary{{background:transparent;border:2px solid var(--primary);color:var(--primary);}}
.btn-secondary:hover{{background:var(--primary);color:#fff;}}
.btn-outline{{background:transparent;border:2px solid var(--primary);color:var(--primary);padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:500;}}
.section{{padding:80px 0;}}
.section-heading{{font-size:2.2rem;text-align:center;margin-bottom:12px;font-weight:700;}}
.section-heading::after{{content:'';display:block;width:60px;height:4px;background:var(--primary);margin:12px auto 36px;border-radius:2px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px;}}
.card{{padding:32px 24px;border-radius:12px;background:var(--bg);border:1px solid rgba(0,0,0,0.08);transition:all .3s;text-align:center;}}
.card:hover{{transform:translateY(-4px);box-shadow:0 12px 24px rgba(0,0,0,0.08);}}
.card-icon{{font-size:2.2rem;margin-bottom:12px;}}
.card h3{{font-size:1.1rem;margin-bottom:8px;}}
.card p{{font-size:0.85rem;opacity:0.7;}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;}}
.gallery-item{{border-radius:12px;overflow:hidden;border:1px solid rgba(0,0,0,0.08);text-align:center;padding-bottom:16px;}}
.gi-img{{height:160px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--primary),#818cf8);color:#fff;font-size:3rem;font-weight:900;}}
.gallery-item h4{{margin:12px 0 4px;font-size:0.95rem;}}
.gallery-item p{{font-size:0.8rem;opacity:0.6;}}
.cases-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;}}
.case-card{{padding:28px;border-radius:12px;background:var(--bg);border:1px solid rgba(0,0,0,0.08);}}
.case-tag{{display:inline-block;background:rgba(37,99,235,0.1);color:var(--primary);padding:4px 12px;border-radius:20px;font-size:0.75rem;margin-bottom:12px;}}
.case-card h3{{margin-bottom:8px;}}
.case-card p{{font-size:0.85rem;opacity:0.7;line-height:1.5;}}
.case-result{{margin-top:12px;padding:8px 12px;background:rgba(16,185,129,0.1);border-radius:6px;font-size:0.8rem;color:#047857;}}
.pricing-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;max-width:960px;margin:0 auto;}}
.price-card{{padding:36px 28px;border-radius:12px;background:var(--bg);border:1px solid rgba(0,0,0,0.08);text-align:center;position:relative;}}
.price-card.featured{{border:2px solid var(--primary);transform:scale(1.03);}}
.badge{{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--primary);color:#fff;padding:4px 16px;border-radius:20px;font-size:0.75rem;font-weight:500;}}
.price{{font-size:2.5rem;font-weight:900;color:var(--primary);margin:16px 0;}}
.symbol{{font-size:1.2rem;vertical-align:super;}}
.period{{font-size:0.9rem;color:var(--text);opacity:0.5;font-weight:400;}}
.price-card ul{{list-style:none;text-align:left;margin:20px 0;}}
.price-card li{{padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.05);font-size:0.85rem;}}
.price-card li::before{{content:'✓ ';color:var(--primary);font-weight:700;}}
.contact-grid{{display:grid;grid-template-columns:1fr 2fr;gap:40px;align-items:start;}}
.contact-info h3{{margin-bottom:16px;}}
.contact-info p{{margin-bottom:10px;font-size:0.9rem;}}
.contact-form{{display:flex;flex-direction:column;gap:12px;}}
.contact-form input,.contact-form textarea{{padding:14px;border:1px solid rgba(0,0,0,0.15);border-radius:8px;font-size:0.9rem;font-family:inherit;}}
.contact-form button{{cursor:pointer;}}
.about-grid{{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center;}}
.about-text p{{margin-bottom:12px;line-height:1.7;}}
.about-stats{{display:flex;gap:30px;justify-content:center;}}
.stat{{text-align:center;}}
.stat-num{{display:block;font-size:2rem;font-weight:900;color:var(--primary);}}
.stat-label{{font-size:0.8rem;opacity:0.6;}}
.article-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;}}
.article-card{{padding:24px;border-radius:12px;background:var(--bg);border:1px solid rgba(0,0,0,0.08);}}
.article-date{{font-size:0.75rem;color:var(--primary);margin-bottom:8px;}}
.article-card h3{{font-size:1.05rem;margin-bottom:8px;}}
.article-card p{{font-size:0.85rem;opacity:0.7;line-height:1.5;}}
.read-more{{color:var(--primary);text-decoration:none;font-size:0.85rem;font-weight:500;display:inline-block;margin-top:8px;}}
.category-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;}}
.category-card{{padding:20px 16px;border-radius:10px;background:var(--bg);border:1px solid rgba(0,0,0,0.06);text-align:center;text-decoration:none;color:var(--text);transition:all .3s;display:flex;flex-direction:column;gap:6px;}}
.category-card:hover{{border-color:var(--primary);transform:translateY(-2px);}}
.cat-icon{{font-size:1.5rem;}}
.cat-count{{font-size:0.7rem;opacity:0.5;}}
.topic-list{{display:flex;flex-direction:column;gap:14px;max-width:800px;margin:0 auto;}}
.topic-item{{display:flex;gap:14px;padding:18px;border-radius:10px;background:var(--bg);border:1px solid rgba(0,0,0,0.06);}}
.topic-avatar{{width:44px;height:44px;border-radius:50%;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;}}
.topic-content h4{{font-size:0.95rem;margin-bottom:4px;}}
.topic-content p{{font-size:0.8rem;opacity:0.6;}}
.topic-meta{{display:flex;gap:12px;margin-top:6px;font-size:0.7rem;opacity:0.5;}}
.user-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;}}
.user-card{{padding:28px;border-radius:12px;background:var(--bg);border:1px solid rgba(0,0,0,0.08);text-align:center;}}
.user-card .avatar{{font-size:3rem;margin-bottom:12px;}}
.user-card h3{{font-size:1rem;margin-bottom:6px;}}
.user-card p{{font-size:0.8rem;opacity:0.6;margin-bottom:14px;}}
.chat-box{{max-width:600px;margin:0 auto;border:1px solid rgba(0,0,0,0.1);border-radius:12px;overflow:hidden;}}
.chat-messages{{padding:20px;min-height:200px;display:flex;flex-direction:column;gap:12px;}}
.chat-msg{{display:flex;gap:10px;align-items:flex-start;}}
.chat-msg.user-msg{{flex-direction:row-reverse;}}
.msg-avatar{{width:36px;height:36px;border-radius:50%;background:var(--secondary);display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;}}
.msg-bubble{{padding:10px 16px;border-radius:12px;background:var(--secondary);font-size:0.85rem;max-width:80%;}}
.user-msg .msg-bubble{{background:var(--primary);color:#fff;}}
.chat-input{{display:flex;padding:12px;border-top:1px solid rgba(0,0,0,0.1);gap:8px;}}
.chat-input input{{flex:1;padding:10px;border:1px solid rgba(0,0,0,0.15);border-radius:8px;font-size:0.85rem;}}
.chat-input button{{padding:10px 20px;}}
.chat-tip{{text-align:center;margin-top:12px;font-size:0.85rem;opacity:0.7;}}
.footer{{padding:40px 0;text-align:center;border-top:1px solid rgba(0,0,0,0.06);}}
.footer-links{{margin-top:8px;}}
.footer-links a{{color:var(--text);opacity:0.6;text-decoration:none;font-size:0.85rem;margin:0 8px;}}
@media(max-width:768px){{
.nav-list{{display:none;}}
.menu-toggle{{display:flex;}}
.hero h1{{font-size:1.8rem;}}
.about-grid,.contact-grid{{grid-template-columns:1fr;}}
.grid,.gallery,.cases-grid,.pricing-grid,.article-grid,.category-grid,.user-grid{{grid-template-columns:1fr;}}
}}''',

        'minimal': f'''
{base}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);line-height:1.8;font-weight:300;}}
.container{{max-width:800px;margin:0 auto;padding:0 32px;}}
.header{{position:fixed;top:0;left:0;right:0;z-index:1000;background:var(--bg);border-bottom:1px solid rgba(0,0,0,0.06);}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:20px 48px;}}
.logo{{font-size:1.1rem;font-weight:700;color:var(--text);text-decoration:none;letter-spacing:2px;text-transform:uppercase;}}
.nav-list{{display:flex;gap:40px;list-style:none;}}
.nav-link{{color:var(--text);text-decoration:none;font-size:0.8rem;letter-spacing:1px;text-transform:uppercase;opacity:0.5;transition:opacity .3s;}}
.nav-link:hover{{opacity:1;}}
.menu-toggle{{display:none;flex-direction:column;gap:4px;background:none;border:none;cursor:pointer;}}
.menu-toggle span{{width:20px;height:1px;background:var(--text);}}
.hero{{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:120px 32px;}}
.hero h1{{font-size:4rem;font-weight:300;letter-spacing:-1px;margin-bottom:20px;line-height:1.2;}}
.hero p{{font-size:1.1rem;opacity:0.4;margin-bottom:36px;letter-spacing:1px;}}
.hero-buttons{{display:flex;gap:20px;justify-content:center;}}
.btn{{padding:14px 36px;text-decoration:none;font-size:0.8rem;letter-spacing:1.5px;text-transform:uppercase;transition:all .3s;font-weight:400;}}
.btn-primary{{background:var(--text);color:var(--bg);}}
.btn-primary:hover{{background:var(--primary);}}
.btn-secondary{{background:transparent;border:1px solid var(--text);color:var(--text);}}
.btn-secondary:hover{{background:var(--text);color:var(--bg);}}
.btn-outline{{background:transparent;border:1px solid var(--text);color:var(--text);padding:12px 28px;text-decoration:none;font-size:0.8rem;letter-spacing:1px;}}
.section{{padding:100px 0;}}
.section-heading{{font-size:2rem;text-align:center;margin-bottom:48px;font-weight:300;letter-spacing:2px;text-transform:uppercase;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:40px;}}
.card{{padding:0;background:none;border:none;text-align:left;}}
.card-icon{{font-size:2rem;margin-bottom:16px;}}
.card h3{{font-size:1.1rem;font-weight:500;margin-bottom:8px;}}
.card p{{font-size:0.85rem;opacity:0.5;line-height:1.7;}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:32px;}}
.gallery-item{{text-align:left;padding:0;border:none;}}
.gi-img{{height:200px;display:flex;align-items:center;justify-content:center;background:var(--text);color:var(--bg);font-size:2rem;font-weight:300;letter-spacing:3px;margin-bottom:16px;}}
.gallery-item h4{{font-size:0.9rem;font-weight:500;}}
.gallery-item p{{font-size:0.8rem;opacity:0.4;}}
.cases-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:32px;}}
.case-card{{border:none;padding:0;background:none;}}
.case-tag{{font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;color:var(--primary);margin-bottom:12px;display:block;}}
.case-card h3{{font-size:1.1rem;font-weight:500;margin-bottom:8px;}}
.case-card p{{font-size:0.85rem;opacity:0.5;line-height:1.7;}}
.case-result{{margin-top:12px;font-size:0.8rem;font-weight:500;color:var(--primary);background:none;padding:0;}}
.pricing-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:32px;max-width:900px;margin:0 auto;}}
.price-card{{border:none;text-align:left;padding:0;background:none;}}
.price-card.featured{{transform:none;border:none;}}
.badge{{position:static;display:inline-block;color:var(--primary);background:none;padding:0;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;}}
.price{{font-size:2rem;font-weight:300;margin:12px 0;}}
.price-card ul{{list-style:none;margin:16px 0;}}
.price-card li{{padding:6px 0;border:none;font-size:0.85rem;opacity:0.5;}}
.price-card li::before{{display:none;}}
.contact-grid{{display:grid;grid-template-columns:1fr 1fr;gap:64px;}}
.contact-info p{{font-size:0.85rem;opacity:0.5;margin-bottom:8px;}}
.contact-form{{display:flex;flex-direction:column;gap:16px;}}
.contact-form input,.contact-form textarea{{padding:12px 0;border:none;border-bottom:1px solid rgba(0,0,0,0.15);border-radius:0;font-size:0.9rem;font-family:inherit;}}
.contact-form input:focus,.contact-form textarea:focus{{outline:none;border-bottom-color:var(--text);}}
.about-grid{{display:grid;grid-template-columns:1fr 1fr;gap:64px;}}
.about-text p{{font-size:0.9rem;line-height:1.8;opacity:0.6;margin-bottom:16px;}}
.about-stats{{display:flex;gap:48px;}}
.stat-num{{font-size:2.5rem;font-weight:300;letter-spacing:-1px;}}
.stat-label{{font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;opacity:0.4;}}
.article-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:32px;}}
.article-card{{border:none;padding:0;background:none;}}
.article-date{{font-size:0.7rem;opacity:0.4;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;}}
.article-card h3{{font-size:1.1rem;font-weight:500;margin-bottom:8px;}}
.article-card p{{font-size:0.85rem;opacity:0.5;line-height:1.7;}}
.read-more{{color:var(--text);font-size:0.8rem;font-weight:500;}}
.category-grid{{grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;}}
.category-card{{background:none;border:none;padding:12px 0;flex-direction:row;gap:12px;justify-content:flex-start;opacity:0.5;transition:opacity .3s;}}
.category-card:hover{{transform:none;opacity:1;border:none;}}
.cat-count{{display:none;}}
.topic-list{{display:flex;flex-direction:column;gap:0;max-width:700px;}}
.topic-item{{border:none;border-bottom:1px solid rgba(0,0,0,0.06);padding:24px 0;background:none;border-radius:0;}}
.topic-avatar{{background:var(--text);}}
.user-grid{{grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:32px;}}
.user-card{{border:none;background:none;padding:0;text-align:left;}}
.chat-box{{border:1px solid rgba(0,0,0,0.1);}}
.msg-bubble{{background:rgba(0,0,0,0.03);}}
.user-msg .msg-bubble{{background:var(--text);}}
.footer{{padding:60px 0;border-top:1px solid rgba(0,0,0,0.06);}}
@media(max-width:768px){{.hero h1{{font-size:2.5rem;}}.about-grid,.contact-grid{{grid-template-columns:1fr;}}}}''',

        'bento': f'''
{base}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;}}
.container{{max-width:1200px;margin:0 auto;padding:0 16px;}}
.header{{position:fixed;top:0;left:0;right:0;z-index:1000;background:rgba(255,255,255,0.95);backdrop-filter:blur(20px);border-bottom:1px solid rgba(0,0,0,0.04);}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:16px 32px;}}
.logo{{font-size:1.3rem;font-weight:800;color:var(--primary);background:rgba(139,92,246,0.1);padding:6px 16px;border-radius:20px;text-decoration:none;}}
.nav-list{{display:flex;gap:8px;list-style:none;}}
.nav-link{{color:var(--text);text-decoration:none;font-size:0.85rem;padding:8px 16px;border-radius:20px;transition:all .3s;font-weight:500;}}
.nav-link:hover{{background:rgba(139,92,246,0.1);color:var(--primary);}}
.menu-toggle{{display:none;}}
.menu-toggle span{{width:22px;height:2px;background:var(--text);display:block;margin:5px 0;border-radius:1px;}}
.hero{{min-height:80vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:80px 16px;}}
.hero h1{{font-size:3.2rem;font-weight:900;margin-bottom:12px;background:linear-gradient(135deg,var(--primary),#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.hero p{{font-size:1.05rem;opacity:0.65;margin-bottom:32px;}}
.hero-buttons{{display:flex;gap:12px;justify-content:center;}}
.btn{{padding:14px 32px;border-radius:40px;text-decoration:none;font-weight:600;font-size:0.9rem;transition:all .3s;}}
.btn-primary{{background:var(--primary);color:#fff;box-shadow:0 4px 20px rgba(139,92,246,0.3);}}
.btn-primary:hover{{transform:translateY(-2px);box-shadow:0 8px 30px rgba(139,92,246,0.4);}}
.btn-secondary{{background:var(--bg);color:var(--text);border:2px solid var(--secondary);}}
.btn-secondary:hover{{border-color:var(--primary);}}
.btn-outline{{background:var(--bg);border:2px solid var(--primary);color:var(--primary);padding:10px 24px;border-radius:40px;text-decoration:none;font-weight:600;font-size:0.85rem;}}
.section{{padding:60px 0;}}
.section-heading{{font-size:1.8rem;text-align:center;margin-bottom:32px;font-weight:800;position:relative;}}
.section-heading::after{{content:'';display:block;width:40px;height:3px;background:var(--primary);margin:10px auto 0;border-radius:2px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;}}
.card{{padding:28px 20px;border-radius:20px;background:var(--bg);border:1px solid var(--secondary);transition:all .3s;text-align:center;}}
.card:hover{{transform:translateY(-6px);box-shadow:0 16px 40px rgba(0,0,0,0.06);border-color:var(--primary);}}
.card-icon{{font-size:2rem;margin-bottom:12px;}}
.card h3{{font-size:1rem;font-weight:700;margin-bottom:6px;}}
.card p{{font-size:0.8rem;opacity:0.6;line-height:1.5;}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;}}
.gallery-item{{border-radius:20px;overflow:hidden;background:var(--bg);border:1px solid var(--secondary);transition:all .3s;}}
.gallery-item:hover{{transform:translateY(-4px);box-shadow:0 12px 30px rgba(0,0,0,0.08);}}
.gi-img{{height:140px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--primary),#a78bfa);color:#fff;font-size:2.5rem;font-weight:900;}}
.gallery-item h4{{margin:12px 14px 4px;font-size:0.9rem;}}
.gallery-item p{{margin:0 14px 14px;font-size:0.75rem;opacity:0.5;}}
.cases-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;}}
.case-card{{padding:24px;border-radius:20px;background:var(--bg);border:1px solid var(--secondary);}}
.case-tag{{display:inline-block;background:rgba(139,92,246,0.1);color:var(--primary);padding:4px 12px;border-radius:20px;font-size:0.7rem;font-weight:600;margin-bottom:12px;}}
.case-card h3{{font-size:1rem;font-weight:700;margin-bottom:6px;}}
.case-card p{{font-size:0.8rem;opacity:0.6;line-height:1.5;}}
.case-result{{margin-top:12px;padding:10px 14px;background:rgba(16,185,129,0.08);border-radius:12px;font-size:0.78rem;color:#047857;font-weight:500;}}
.pricing-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;max-width:960px;margin:0 auto;}}
.price-card{{padding:32px 24px;border-radius:24px;background:var(--bg);border:1px solid var(--secondary);text-align:center;position:relative;}}
.price-card.featured{{border:2px solid var(--primary);background:linear-gradient(135deg,rgba(139,92,246,0.03),rgba(139,92,246,0.08));box-shadow:0 8px 30px rgba(139,92,246,0.1);}}
.badge{{position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:var(--primary);color:#fff;padding:4px 14px;border-radius:20px;font-size:0.7rem;font-weight:700;}}
.price{{font-size:2.2rem;font-weight:900;color:var(--primary);margin:16px 0;}}
.price-card ul{{list-style:none;text-align:left;margin:20px 0;}}
.price-card li{{padding:12px 0;border-bottom:1px solid rgba(0,0,0,0.04);font-size:0.82rem;}}
.price-card li::before{{content:'✦ ';color:var(--primary);}}
.contact-grid{{display:grid;grid-template-columns:1fr 2fr;gap:24px;}}
.contact-info{{background:var(--bg);padding:24px;border-radius:20px;border:1px solid var(--secondary);}}
.contact-form{{display:flex;flex-direction:column;gap:12px;}}
.contact-form input,.contact-form textarea{{padding:14px 18px;border:1px solid var(--secondary);border-radius:14px;font-size:0.88rem;font-family:inherit;background:var(--bg);}}
.about-grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px;}}
.about-stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}}
.stat{{background:var(--bg);padding:20px;border-radius:16px;text-align:center;border:1px solid var(--secondary);}}
.article-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;}}
.article-card{{padding:24px;border-radius:20px;background:var(--bg);border:1px solid var(--secondary);}}
.category-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;}}
.category-card{{padding:20px 14px;border-radius:16px;background:var(--bg);border:1px solid var(--secondary);text-align:center;text-decoration:none;color:var(--text);transition:all .3s;}}
.category-card:hover{{border-color:var(--primary);background:rgba(139,92,246,0.04);}}
.user-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;}}
.user-card{{padding:28px;border-radius:20px;background:var(--bg);border:1px solid var(--secondary);text-align:center;}}
.chat-box{{border-radius:20px;overflow:hidden;border:1px solid var(--secondary);max-width:600px;margin:0 auto;}}
.msg-bubble{{border-radius:14px;background:var(--secondary);}}
.chat-msg .msg-bubble{{background:var(--secondary);}}
.user-msg .msg-bubble{{background:var(--primary);color:#fff;}}
.footer{{padding:40px 0;text-align:center;border-top:1px solid var(--secondary);}}
@media(max-width:768px){{.hero h1{{font-size:2rem;}}.about-grid,.contact-grid{{grid-template-columns:1fr;}}}}''',

        'brutalist': f'''
{base}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Noto Sans SC',monospace;background:var(--bg);color:var(--text);line-height:1.5;}}
.container{{max-width:1200px;margin:0 auto;padding:0 24px;}}
.header{{position:fixed;top:0;left:0;right:0;z-index:1000;background:var(--bg);border-bottom:4px solid var(--text);}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;}}
.logo{{font-size:1.4rem;font-weight:900;color:var(--text);text-decoration:none;border:3px solid var(--text);padding:6px 16px;}}
.nav-list{{display:flex;gap:0;list-style:none;}}
.nav-link{{color:var(--text);text-decoration:none;font-size:0.85rem;font-weight:700;padding:8px 16px;border:3px solid transparent;transition:all .2s;}}
.nav-link:hover{{border-color:var(--text);}}
.menu-toggle{{display:none;}}
.hero{{min-height:80vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:80px 24px;background:var(--primary);color:#fff;}}
.hero h1{{font-size:3.5rem;font-weight:900;text-transform:uppercase;margin-bottom:16px;text-shadow:4px 4px 0 rgba(0,0,0,0.2);}}
.hero p{{font-size:1.1rem;opacity:0.9;margin-bottom:28px;}}
.hero-buttons{{display:flex;gap:12px;justify-content:center;}}
.btn{{padding:14px 32px;text-decoration:none;font-weight:900;font-size:0.9rem;transition:all .2s;display:inline-block;text-transform:uppercase;}}
.btn-primary{{background:#fff;color:var(--primary);border:3px solid #fff;}}
.btn-primary:hover{{background:var(--primary);color:#fff;box-shadow:6px 6px 0 rgba(0,0,0,0.3);}}
.btn-secondary{{background:transparent;color:#fff;border:3px solid #fff;}}
.btn-secondary:hover{{background:#fff;color:var(--primary);}}
.btn-outline{{background:transparent;color:var(--text);border:3px solid var(--text);padding:10px 24px;text-decoration:none;font-weight:900;font-size:0.8rem;text-transform:uppercase;}}
.section{{padding:80px 0;}}
.section-heading{{font-size:2.2rem;text-align:center;margin-bottom:36px;font-weight:900;text-transform:uppercase;}}
.section-heading::after{{content:'';display:block;width:80px;border-bottom:6px solid var(--primary);margin:12px auto 0;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:0;}}
.card{{padding:32px 20px;border:3px solid var(--text);text-align:center;margin:-3px 0 0 -3px;transition:all .2s;background:var(--bg);}}
.card:hover{{background:var(--primary);color:#fff;border-color:var(--primary);}}
.card-icon{{font-size:2rem;margin-bottom:12px;}}
.card h3{{font-size:1.1rem;font-weight:900;margin-bottom:6px;}}
.card p{{font-size:0.8rem;opacity:0.7;}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0;}}
.gallery-item{{border:3px solid var(--text);margin:-3px 0 0 -3px;padding:0 0 16px;text-align:center;}}
.gi-img{{height:160px;display:flex;align-items:center;justify-content:center;background:var(--primary);color:#fff;font-size:3rem;font-weight:900;}}
.gallery-item h4{{font-size:0.95rem;font-weight:900;margin:12px 0 4px;}}
.gallery-item p{{font-size:0.75rem;opacity:0.6;}}
.cases-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:0;}}
.case-card{{padding:24px;border:3px solid var(--text);margin:-3px 0 0 -3px;background:var(--bg);}}
.case-tag{{display:inline-block;background:var(--primary);color:#fff;padding:2px 12px;font-size:0.7rem;font-weight:900;text-transform:uppercase;margin-bottom:12px;}}
.case-card h3{{font-size:1.1rem;font-weight:900;margin-bottom:6px;}}
.case-card p{{font-size:0.8rem;opacity:0.6;}}
.case-result{{margin-top:12px;padding:8px 12px;border:3px solid var(--primary);font-size:0.8rem;font-weight:900;}}
.pricing-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:0;max-width:960px;margin:0 auto;}}
.price-card{{padding:36px 24px;border:3px solid var(--text);margin:-3px 0 0 -3px;text-align:center;background:var(--bg);}}
.price-card.featured{{border-color:var(--primary);border-width:6px;margin-top:-6px;position:relative;}}
.badge{{position:absolute;top:-14px;left:50%;transform:translateX(-50%);background:var(--primary);color:#fff;padding:4px 16px;font-size:0.75rem;font-weight:900;text-transform:uppercase;}}
.price{{font-size:2rem;font-weight:900;margin:16px 0;color:var(--primary);}}
.price-card ul{{list-style:none;text-align:left;margin:20px 0;}}
.price-card li{{padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.1);font-size:0.8rem;}}
.contact-grid{{display:grid;grid-template-columns:1fr 2fr;gap:0;}}
.contact-info{{border:3px solid var(--text);padding:24px;}}
.contact-form{{display:flex;flex-direction:column;gap:0;}}
.contact-form input,.contact-form textarea{{padding:14px;border:3px solid var(--text);margin-top:-3px;font-size:0.9rem;font-family:inherit;background:var(--bg);}}
.about-grid{{display:grid;grid-template-columns:1fr 1fr;gap:0;}}
.about-stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:0;}}
.stat{{border:3px solid var(--text);padding:20px;text-align:center;margin:-3px 0 0 -3px;}}
.article-grid,.category-grid{{gap:0;}}
.article-card{{border:3px solid var(--text);padding:24px;margin:-3px 0 0 -3px;}}
.category-card{{border:3px solid var(--text);padding:20px 14px;text-align:center;text-decoration:none;color:var(--text);margin:-3px 0 0 -3px;display:block;}}
.category-card:hover{{background:var(--primary);color:#fff;}}
.chat-box{{border:3px solid var(--text);max-width:600px;margin:0 auto;}}
.msg-bubble{{border:2px solid var(--text);border-radius:2px;}}
.user-msg .msg-bubble{{background:var(--primary);color:#fff;border-color:var(--primary);}}
.footer{{padding:40px 0;text-align:center;border-top:6px solid var(--text);}}
@media(max-width:768px){{.hero h1{{font-size:2rem;}}.about-grid,.contact-grid{{grid-template-columns:1fr;}}}}''',

        'glass': f'''
{base}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;}}
.container{{max-width:1200px;margin:0 auto;padding:0 20px;}}
.header{{position:fixed;top:0;left:0;right:0;z-index:1000;background:rgba(15,23,42,0.6);backdrop-filter:blur(24px);border-bottom:1px solid rgba(255,255,255,0.06);}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:16px 32px;}}
.logo{{font-size:1.4rem;font-weight:800;color:#fff;text-decoration:none;text-shadow:0 0 20px rgba(14,165,233,0.5);}}
.nav-list{{display:flex;gap:24px;list-style:none;}}
.nav-link{{color:rgba(255,255,255,0.7);text-decoration:none;font-size:0.85rem;transition:all .3s;}}
.nav-link:hover{{color:#fff;text-shadow:0 0 10px rgba(14,165,233,0.5);}}
.menu-toggle{{display:none;}}
.hero{{min-height:90vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 20px;position:relative;}}
.hero::before{{content:'';position:absolute;top:10%;right:10%;width:300px;height:300px;background:radial-gradient(circle,rgba(14,165,233,0.2),transparent);filter:blur(60px);}}
.hero::after{{content:'';position:absolute;bottom:10%;left:10%;width:300px;height:300px;background:radial-gradient(circle,rgba(139,92,246,0.2),transparent);filter:blur(60px);}}
.hero-content{{position:relative;z-index:1;}}
.hero h1{{font-size:3.5rem;font-weight:900;margin-bottom:16px;background:linear-gradient(135deg,#fff,rgba(255,255,255,0.7));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.hero p{{font-size:1.15rem;opacity:0.6;margin-bottom:28px;}}
.hero-buttons{{display:flex;gap:14px;justify-content:center;}}
.btn{{padding:14px 32px;border-radius:14px;text-decoration:none;font-weight:600;font-size:0.9rem;transition:all .3s;backdrop-filter:blur(10px);}}
.btn-primary{{background:rgba(14,165,233,0.3);border:1px solid rgba(14,165,233,0.5);color:#fff;}}
.btn-primary:hover{{background:rgba(14,165,233,0.5);box-shadow:0 0 30px rgba(14,165,233,0.3);}}
.btn-secondary{{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.2);color:rgba(255,255,255,0.8);}}
.btn-secondary:hover{{background:rgba(255,255,255,0.1);}}
.btn-outline{{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.2);color:rgba(255,255,255,0.8);padding:10px 24px;border-radius:14px;text-decoration:none;font-weight:600;font-size:0.85rem;}}
.section{{padding:80px 0;}}
.section-heading{{font-size:2.2rem;text-align:center;margin-bottom:36px;font-weight:800;color:#fff;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;}}
.card{{padding:28px;border-radius:16px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);backdrop-filter:blur(10px);transition:all .3s;text-align:center;}}
.card:hover{{background:rgba(255,255,255,0.08);transform:translateY(-4px);}}
.card-icon{{font-size:2rem;margin-bottom:12px;}}
.card h3{{font-size:1.05rem;color:#fff;margin-bottom:6px;}}
.card p{{font-size:0.82rem;opacity:0.5;}}
.gallery-item,.case-card,.article-card,.category-card,.user-card,.price-card{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);backdrop-filter:blur(10px);border-radius:16px;}}
.price-card.featured{{border-color:var(--primary);background:rgba(14,165,233,0.08);}}
.badge{{background:var(--primary);color:#fff;border-radius:12px;}}
.price{{color:var(--primary);}}
.contact-form input,.contact-form textarea,.chat-input input{{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:var(--text);border-radius:12px;}}
.chat-box{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:16px;}}
.msg-bubble{{background:rgba(255,255,255,0.08);}}
.user-msg .msg-bubble{{background:rgba(14,165,233,0.3);}}
.footer{{padding:40px 0;text-align:center;border-top:1px solid rgba(255,255,255,0.06);}}
@media(max-width:768px){{.hero h1{{font-size:2rem;}}.about-grid,.contact-grid{{grid-template-columns:1fr;}}}}''',

        'neumorphic': f'''
{base}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;}}
.container{{max-width:1200px;margin:0 auto;padding:0 20px;}}
.header{{position:fixed;top:0;left:0;right:0;z-index:1000;background:var(--bg);box-shadow:8px 8px 16px rgba(0,0,0,0.05),-8px -8px 16px rgba(255,255,255,0.8);padding:12px 0;}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:8px 32px;border-radius:20px;margin:8px 16px;background:var(--bg);box-shadow:inset 3px 3px 6px rgba(0,0,0,0.03),inset -3px -3px 6px rgba(255,255,255,0.8);}}
.logo{{font-size:1.3rem;font-weight:800;color:var(--primary);text-decoration:none;}}
.nav-list{{display:flex;gap:8px;list-style:none;}}
.nav-link{{color:var(--text);text-decoration:none;font-size:0.85rem;padding:8px 16px;border-radius:14px;transition:all .3s;}}
.nav-link:hover{{box-shadow:3px 3px 6px rgba(0,0,0,0.05),-3px -3px 6px rgba(255,255,255,0.8);}}
.hero{{min-height:85vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 20px;}}
.hero h1{{font-size:3.2rem;font-weight:800;margin-bottom:16px;}}
.hero p{{font-size:1.1rem;opacity:0.6;margin-bottom:28px;}}
.hero-buttons{{display:flex;gap:14px;justify-content:center;}}
.btn{{padding:16px 36px;border-radius:16px;text-decoration:none;font-weight:600;font-size:0.9rem;transition:all .3s;}}
.btn-primary{{background:var(--primary);color:#fff;box-shadow:6px 6px 12px rgba(0,0,0,0.1),-6px -6px 12px rgba(255,255,255,0.8);}}
.btn-primary:hover{{box-shadow:3px 3px 6px rgba(0,0,0,0.1),-3px -3px 6px rgba(255,255,255,0.8);transform:translateY(2px);}}
.btn-secondary{{background:var(--bg);color:var(--text);box-shadow:6px 6px 12px rgba(0,0,0,0.05),-6px -6px 12px rgba(255,255,255,0.8);}}
.btn-secondary:hover{{box-shadow:3px 3px 6px rgba(0,0,0,0.05),-3px -3px 6px rgba(255,255,255,0.8);transform:translateY(2px);}}
.btn-outline{{background:var(--bg);color:var(--primary);box-shadow:4px 4px 8px rgba(0,0,0,0.05),-4px -4px 8px rgba(255,255,255,0.8);padding:12px 24px;border-radius:14px;text-decoration:none;font-weight:600;font-size:0.85rem;}}
.section{{padding:70px 0;}}
.section-heading{{font-size:2rem;text-align:center;margin-bottom:32px;font-weight:800;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px;}}
.card{{padding:32px 24px;border-radius:20px;background:var(--bg);box-shadow:8px 8px 16px rgba(0,0,0,0.04),-8px -8px 16px rgba(255,255,255,0.9);text-align:center;transition:all .3s;}}
.card:hover{{box-shadow:4px 4px 8px rgba(0,0,0,0.04),-4px -4px 8px rgba(255,255,255,0.9);transform:translateY(3px);}}
.card-icon{{font-size:2rem;margin-bottom:12px;}}
.card h3{{font-size:1rem;font-weight:700;margin-bottom:6px;}}
.card p{{font-size:0.8rem;opacity:0.55;}}
.gallery-item,.case-card,.article-card,.category-card,.user-card,.price-card,.topic-item{{background:var(--bg);box-shadow:8px 8px 16px rgba(0,0,0,0.04),-8px -8px 16px rgba(255,255,255,0.9);border-radius:20px;border:none;}}
.contact-form input,.contact-form textarea{{background:var(--bg);box-shadow:inset 4px 4px 8px rgba(0,0,0,0.04),inset -4px -4px 8px rgba(255,255,255,0.9);border:none;border-radius:14px;}}
.chat-box{{background:var(--bg);box-shadow:8px 8px 16px rgba(0,0,0,0.04),-8px -8px 16px rgba(255,255,255,0.9);border-radius:20px;border:none;}}
.footer{{padding:40px 0;text-align:center;}}
@media(max-width:768px){{.hero h1{{font-size:2rem;}}}}''',

        'gradient': f'''
{base}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;}}
.container{{max-width:1200px;margin:0 auto;padding:0 20px;}}
.header{{position:fixed;top:0;left:0;right:0;z-index:1000;background:linear-gradient(135deg,rgba(255,247,237,0.95),rgba(254,215,170,0.6));backdrop-filter:blur(10px);}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:16px 32px;}}
.logo{{font-size:1.4rem;font-weight:900;background:linear-gradient(135deg,#f97316,#ef4444,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-decoration:none;}}
.nav-list{{display:flex;gap:24px;list-style:none;}}
.nav-link{{color:var(--text);text-decoration:none;font-size:0.9rem;font-weight:500;transition:all .3s;}}
.nav-link:hover{{background:linear-gradient(135deg,var(--primary),#ef4444);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.hero{{min-height:90vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 20px;background:linear-gradient(135deg,#fff7ed 0%,#fed7aa 50%,#fde68a 100%);position:relative;overflow:hidden;}}
.hero::before{{content:'';position:absolute;top:-50%;right:-30%;width:500px;height:500px;background:radial-gradient(circle,rgba(249,115,22,0.15),transparent);border-radius:50%;}}
.hero h1{{font-size:3.5rem;font-weight:900;background:linear-gradient(135deg,#f97316,#dc2626,#7c2d12);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:16px;}}
.hero p{{font-size:1.15rem;opacity:0.7;margin-bottom:28px;}}
.hero-buttons{{display:flex;gap:14px;justify-content:center;}}
.btn{{padding:14px 32px;border-radius:30px;text-decoration:none;font-weight:700;font-size:0.9rem;transition:all .3s;}}
.btn-primary{{background:linear-gradient(135deg,#f97316,#ef4444);color:#fff;box-shadow:0 4px 20px rgba(249,115,22,0.4);}}
.btn-primary:hover{{transform:translateY(-2px);box-shadow:0 8px 30px rgba(249,115,22,0.5);}}
.btn-secondary{{background:rgba(255,255,255,0.8);color:var(--text);border:2px solid rgba(249,115,22,0.3);}}
.btn-outline{{background:transparent;border:2px solid var(--primary);color:var(--primary);padding:10px 24px;border-radius:30px;text-decoration:none;font-weight:600;font-size:0.85rem;}}
.section{{padding:70px 0;}}
.section-heading{{font-size:2.2rem;text-align:center;margin-bottom:32px;font-weight:900;background:linear-gradient(135deg,var(--primary),#ef4444);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;width:100%;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;}}
.card{{padding:32px 24px;border-radius:24px;background:linear-gradient(135deg,rgba(255,255,255,0.9),rgba(254,215,170,0.3));border:1px solid rgba(249,115,22,0.1);transition:all .3s;text-align:center;}}
.card:hover{{transform:translateY(-6px);box-shadow:0 20px 40px rgba(249,115,22,0.15);}}
.card-icon{{font-size:2.2rem;margin-bottom:12px;}}
.card h3{{font-size:1.05rem;font-weight:700;margin-bottom:6px;}}
.card p{{font-size:0.82rem;opacity:0.6;}}
.gallery-item,.case-card,.article-card,.category-card,.user-card,.price-card,.topic-item{{border-radius:24px;border:1px solid rgba(249,115,22,0.1);}}
.price-card.featured{{background:linear-gradient(135deg,rgba(249,115,22,0.08),rgba(239,68,68,0.05));border:2px solid var(--primary);}}
.badge{{background:linear-gradient(135deg,#f97316,#ef4444);border-radius:20px;}}
.chat-box{{border-radius:24px;border:1px solid rgba(249,115,22,0.15);}}
.contact-form input,.contact-form textarea{{border-radius:16px;border:1px solid rgba(249,115,22,0.2);}}
.footer{{background:linear-gradient(135deg,rgba(255,247,237,0.8),rgba(254,215,170,0.4));padding:40px 0;text-align:center;}}
@media(max-width:768px){{.hero h1{{font-size:2rem;}}}}''',

        'dark': f'''
{base}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;}}
.container{{max-width:1200px;margin:0 auto;padding:0 24px;}}
.header{{position:fixed;top:0;left:0;right:0;z-index:1000;background:rgba(9,9,11,0.9);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.04);}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:16px 32px;}}
.logo{{font-size:1.3rem;font-weight:800;color:var(--primary);text-decoration:none;}}
.nav-list{{display:flex;gap:28px;list-style:none;}}
.nav-link{{color:rgba(228,228,231,0.6);text-decoration:none;font-size:0.85rem;transition:all .3s;}}
.nav-link:hover{{color:var(--primary);}}
.hero{{min-height:90vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 24px;background:radial-gradient(ellipse at top,rgba(34,211,208,0.08),transparent 50%);}}
.hero h1{{font-size:3.5rem;font-weight:900;margin-bottom:16px;}}
.hero p{{font-size:1.1rem;opacity:0.5;margin-bottom:28px;}}
.hero-buttons{{display:flex;gap:14px;justify-content:center;}}
.btn{{padding:14px 32px;border-radius:10px;text-decoration:none;font-weight:600;font-size:0.9rem;transition:all .3s;}}
.btn-primary{{background:var(--primary);color:var(--bg);}}
.btn-primary:hover{{box-shadow:0 0 30px rgba(34,211,208,0.3);}}
.btn-secondary{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);color:var(--text);}}
.btn-outline{{background:transparent;border:1px solid var(--primary);color:var(--primary);padding:10px 24px;border-radius:10px;text-decoration:none;font-weight:600;font-size:0.85rem;}}
.section{{padding:80px 0;}}
.section-heading{{font-size:2.2rem;text-align:center;margin-bottom:36px;font-weight:800;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;}}
.card,.case-card,.article-card,.topic-item{{padding:28px 24px;border-radius:14px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);transition:all .3s;text-align:center;}}
.card:hover,.case-card:hover,.article-card:hover{{background:rgba(255,255,255,0.06);border-color:var(--primary);}}
.card-icon{{font-size:2rem;margin-bottom:12px;}}
.card h3{{font-size:1.05rem;color:#fff;margin-bottom:6px;}}
.card p{{font-size:0.82rem;opacity:0.45;}}
.gallery-item,.category-card,.user-card,.price-card{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:14px;}}
.price-card.featured{{border-color:var(--primary);background:rgba(34,211,208,0.06);}}
.badge{{background:var(--primary);color:var(--bg);border-radius:10px;}}
.price{{color:var(--primary);}}
.contact-form input,.contact-form textarea,.chat-input input{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);color:var(--text);border-radius:10px;}}
.chat-box{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:14px;}}
.msg-bubble{{background:rgba(255,255,255,0.06);}}
.user-msg .msg-bubble{{background:var(--primary);color:var(--bg);}}
.footer{{padding:40px 0;text-align:center;border-top:1px solid rgba(255,255,255,0.04);}}
@media(max-width:768px){{.hero h1{{font-size:2rem;}}}}''',

        'cyber': f'''
{base}
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Share Tech Mono','Noto Sans SC',monospace;background:var(--bg);color:var(--text);line-height:1.6;}}
.container{{max-width:1200px;margin:0 auto;padding:0 20px;}}
.header{{position:fixed;top:0;left:0;right:0;z-index:1000;background:rgba(10,10,15,0.95);border-bottom:2px solid var(--primary);box-shadow:0 0 20px rgba(255,0,128,0.2);}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:16px 32px;}}
.logo{{font-size:1.3rem;font-weight:900;color:var(--primary);text-decoration:none;text-shadow:0 0 10px var(--primary),0 0 30px var(--primary);animation:glow 2s ease-in-out infinite alternate;}}
@keyframes glow{{from{{text-shadow:0 0 10px var(--primary);}}to{{text-shadow:0 0 20px var(--primary),0 0 40px var(--primary);}}}}
.nav-list{{display:flex;gap:20px;list-style:none;}}
.nav-link{{color:var(--text);text-decoration:none;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;padding:6px 12px;border:1px solid transparent;transition:all .3s;}}
.nav-link:hover{{border-color:var(--primary);color:var(--primary);text-shadow:0 0 10px var(--primary);}}
.hero{{min-height:90vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 20px;position:relative;}}
.hero::before{{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(255,0,128,0.03) 2px,rgba(255,0,128,0.03) 4px);}}
.hero-content{{position:relative;z-index:1;border:2px solid var(--primary);padding:60px;box-shadow:0 0 30px rgba(255,0,128,0.2),inset 0 0 30px rgba(255,0,128,0.05);}}
.hero h1{{font-size:2.8rem;font-weight:900;color:var(--primary);text-shadow:0 0 10px var(--primary),0 0 40px var(--primary);margin-bottom:16px;text-transform:uppercase;letter-spacing:3px;}}
.hero p{{font-size:1rem;color:var(--text);opacity:0.7;margin-bottom:28px;}}
.hero-buttons{{display:flex;gap:12px;justify-content:center;}}
.btn{{padding:12px 28px;text-decoration:none;font-weight:700;font-size:0.85rem;transition:all .3s;text-transform:uppercase;letter-spacing:1px;position:relative;}}
.btn-primary{{background:var(--primary);color:var(--bg);border:2px solid var(--primary);clip-path:polygon(10px 0,100% 0,calc(100% - 10px) 100%,0 100%);}}
.btn-primary:hover{{box-shadow:0 0 20px var(--primary),0 0 40px var(--primary);}}
.btn-secondary{{background:transparent;border:2px solid var(--primary);color:var(--primary);clip-path:polygon(10px 0,100% 0,calc(100% - 10px) 100%,0 100%);}}
.btn-secondary:hover{{box-shadow:0 0 20px var(--primary);}}
.btn-outline{{background:transparent;border:2px solid var(--primary);color:var(--primary);padding:10px 20px;text-decoration:none;font-weight:600;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;}}
.section{{padding:70px 0;}}
.section-heading{{font-size:1.8rem;text-align:center;margin-bottom:32px;font-weight:900;color:var(--primary);text-shadow:0 0 10px rgba(255,0,128,0.4);text-transform:uppercase;letter-spacing:2px;}}
.section-heading::after{{content:'//';display:block;font-size:1rem;opacity:0.3;margin-top:8px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;}}
.card,.case-card,.article-card,.topic-item,.user-card,.price-card,.category-card{{padding:24px;border:1px solid rgba(255,0,128,0.2);background:rgba(10,10,15,0.8);transition:all .3s;text-align:center;}}
.card:hover,.case-card:hover,.article-card:hover{{border-color:var(--primary);box-shadow:0 0 15px rgba(255,0,128,0.15);}}
.card-icon{{font-size:1.8rem;margin-bottom:12px;}}
.card h3{{font-size:1rem;color:var(--primary);margin-bottom:6px;}}
.card p{{font-size:0.8rem;opacity:0.5;}}
.price-card.featured{{border-color:var(--primary);box-shadow:0 0 20px rgba(255,0,128,0.15);}}
.badge{{background:var(--primary);color:var(--bg);font-size:0.7rem;font-weight:900;text-transform:uppercase;}}
.price{{color:var(--primary);text-shadow:0 0 10px var(--primary);}}
.case-tag{{background:rgba(255,0,128,0.1);color:var(--primary);border:1px solid var(--primary);}}
.contact-form input,.contact-form textarea,.chat-input input{{background:rgba(10,10,15,0.8);border:1px solid rgba(255,0,128,0.2);color:var(--text);}}
.contact-form input:focus{{border-color:var(--primary);box-shadow:0 0 10px rgba(255,0,128,0.2);outline:none;}}
.chat-box{{border:1px solid rgba(255,0,128,0.2);}}
.msg-bubble{{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);}}
.user-msg .msg-bubble{{background:rgba(255,0,128,0.15);border-color:var(--primary);}}
.footer{{padding:40px 0;text-align:center;border-top:2px solid rgba(255,0,128,0.1);}}
@media(max-width:768px){{.hero h1{{font-size:1.8rem;}}.hero-content{{padding:30px;}}}}''',

        'nature': f'''
{base}
*{{margin:0;padding:0;box-sizing:border-box;}}
html{{scroll-behavior:smooth;}}
body{{font-family:'Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);line-height:1.7;}}
.container{{max-width:1200px;margin:0 auto;padding:0 24px;}}
.header{{position:fixed;top:0;left:0;right:0;z-index:1000;background:rgba(240,253,244,0.95);backdrop-filter:blur(10px);border-bottom:1px solid rgba(22,163,74,0.1);}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:16px 32px;}}
.logo{{font-size:1.3rem;font-weight:800;color:var(--primary);text-decoration:none;display:flex;align-items:center;gap:6px;}}
.logo::before{{content:'🌿';font-size:1.2rem;}}
.nav-list{{display:flex;gap:24px;list-style:none;}}
.nav-link{{color:var(--text);text-decoration:none;font-size:0.88rem;font-weight:500;transition:all .3s;}}
.nav-link:hover{{color:var(--primary);}}
.hero{{min-height:90vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:100px 24px;background:linear-gradient(180deg,#f0fdf4 0%,#dcfce7 50%,#bbf7d0 100%);}}
.hero h1{{font-size:3rem;font-weight:900;color:var(--text);margin-bottom:16px;}}
.hero p{{font-size:1.1rem;opacity:0.65;margin-bottom:28px;}}
.hero-buttons{{display:flex;gap:14px;justify-content:center;}}
.btn{{padding:14px 32px;border-radius:30px;text-decoration:none;font-weight:600;font-size:0.9rem;transition:all .3s;}}
.btn-primary{{background:var(--primary);color:#fff;box-shadow:0 4px 16px rgba(22,163,74,0.3);}}
.btn-primary:hover{{background:#15803d;transform:translateY(-2px);box-shadow:0 8px 24px rgba(22,163,74,0.4);}}
.btn-secondary{{background:rgba(255,255,255,0.8);border:2px solid var(--primary);color:var(--primary);}}
.btn-secondary:hover{{background:var(--primary);color:#fff;}}
.btn-outline{{background:transparent;border:2px solid var(--primary);color:var(--primary);padding:10px 24px;border-radius:30px;text-decoration:none;font-weight:600;font-size:0.85rem;}}
.section{{padding:70px 0;}}
.section-heading{{font-size:2rem;text-align:center;margin-bottom:32px;font-weight:800;}}
.section-heading::after{{content:'';display:block;width:50px;height:3px;background:var(--primary);margin:10px auto 0;border-radius:2px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;}}
.card,.case-card,.article-card,.topic-item,.user-card,.price-card,.category-card{{padding:28px 22px;border-radius:20px;background:rgba(255,255,255,0.7);border:1px solid rgba(22,163,74,0.08);transition:all .3s;text-align:center;}}
.card:hover,.case-card:hover{{transform:translateY(-4px);box-shadow:0 12px 28px rgba(22,163,74,0.08);border-color:var(--primary);}}
.card-icon{{font-size:2rem;margin-bottom:12px;}}
.card h3{{font-size:1rem;font-weight:700;margin-bottom:6px;}}
.card p{{font-size:0.82rem;opacity:0.6;}}
.price-card.featured{{border:2px solid var(--primary);background:rgba(22,163,74,0.03);}}
.badge{{background:var(--primary);color:#fff;border-radius:20px;}}
.gallery-item{{border-radius:20px;overflow:hidden;}}
.gi-img{{border-radius:20px 20px 0 0;}}
.contact-form input,.contact-form textarea,.chat-input input{{border:1px solid rgba(22,163,74,0.15);border-radius:14px;background:rgba(255,255,255,0.8);}}
.contact-form input:focus{{border-color:var(--primary);outline:none;}}
.chat-box{{border:1px solid rgba(22,163,74,0.1);border-radius:20px;}}
.footer{{background:#dcfce7;padding:40px 0;text-align:center;}}
@media(max-width:768px){{.hero h1{{font-size:2rem;}}}}''',
    }

    return style_css_map.get(style_name, style_css_map['modern']) + '''
/* ===== 通用辅助样式 ===== */
.section-heading{display:block;width:100%;}
.hero-content{position:relative;z-index:1;}
.pricing-grid .btn-outline,.pricing-grid .btn-primary{display:inline-block;margin-top:12px;width:100%;}
.topic-item{align-items:center;display:flex;padding:18px;gap:14px;}
.topic-avatar{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;}
.topic-content{flex:1;}
.topic-content h4{font-size:.95rem;margin-bottom:4px;}
.topic-content p{font-size:.8rem;opacity:.6;}
.topic-meta{display:flex;gap:12px;margin-top:6px;font-size:.7rem;opacity:.5;}
.category-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;}
.category-card{display:flex;flex-direction:column;gap:6px;align-items:center;}
.cat-icon{font-size:1.4rem;}
.cat-count{font-size:.7rem;opacity:.4;}
.user-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;}
.avatar{font-size:2.5rem;margin-bottom:10px;}
.user-card h3{font-size:1rem;margin-bottom:6px;}
.user-card p{font-size:.8rem;opacity:.5;margin-bottom:12px;}
.chat-box{max-width:600px;margin:0 auto;overflow:hidden;}
.chat-messages{padding:20px;min-height:180px;display:flex;flex-direction:column;gap:12px;}
.chat-msg{display:flex;gap:10px;align-items:flex-start;}
.chat-msg.user-msg{flex-direction:row-reverse;}
.msg-avatar{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;}
.msg-bubble{padding:10px 16px;border-radius:12px;font-size:.85rem;max-width:80%;}
.chat-input{display:flex;padding:12px;border-top:1px solid rgba(0,0,0,.08);gap:8px;}
.chat-input input{flex:1;padding:10px;border-radius:8px;font-size:.85rem;}
.chat-input button{padding:10px 20px;cursor:pointer;}
.chat-tip{text-align:center;margin-top:12px;font-size:.85rem;opacity:.65;}
.article-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;}
.article-card{padding:24px;}
.article-date{font-size:.7rem;opacity:.5;margin-bottom:8px;}
.article-card h3{font-size:1.05rem;margin-bottom:8px;}
.article-card p{font-size:.82rem;opacity:.6;line-height:1.5;}
.read-more{font-size:.82rem;font-weight:500;display:inline-block;margin-top:8px;}
.user-msg .msg-bubble{color:#fff;}
.about-grid,.contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;}
.about-text p{line-height:1.7;margin-bottom:12px;}
.about-stats{display:flex;gap:24px;justify-content:center;flex-wrap:wrap;}
.stat{text-align:center;padding:16px;}
.stat-num{display:block;font-size:2rem;font-weight:900;}
.stat-label{font-size:.75rem;opacity:.5;}
.cases-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;}
.case-card{padding:24px;}
.case-tag{display:inline-block;padding:4px 12px;border-radius:16px;font-size:.7rem;font-weight:600;margin-bottom:10px;}
.case-card h3{font-size:1.05rem;margin-bottom:6px;}
.case-card p{font-size:.82rem;opacity:.6;line-height:1.5;}
.case-result{margin-top:12px;padding:10px 12px;border-radius:8px;font-size:.78rem;font-weight:500;}
.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;}
.gallery-item{overflow:hidden;}
.gi-img{height:150px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;font-weight:900;}
.gallery-item h4{padding:12px 16px 4px;font-size:.9rem;}
.gallery-item p{padding:0 16px 14px;font-size:.75rem;opacity:.5;}
@media(max-width:768px){.about-grid,.contact-grid{grid-template-columns:1fr;}.pricing-grid,.grid,.gallery,.cases-grid,.article-grid,.category-grid,.user-grid{grid-template-columns:1fr;}}
'''


def generate_js(website_type, features):
    return f'''// 飞站生成器 - {website_type}
document.addEventListener('DOMContentLoaded',function(){{
var nav=document.querySelector('.header');
window.addEventListener('scroll',function(){{nav.style.background=window.scrollY>50?'rgba(255,255,255,0.98)':'rgba(255,255,255,0.9)';}});
document.querySelectorAll('a[href^="#"]').forEach(function(a){{a.addEventListener('click',function(e){{e.preventDefault();var t=document.querySelector(this.getAttribute('href'));if(t)t.scrollIntoView({{behavior:'smooth'}});}});}});
var form=document.querySelector('.contact-form');if(form)form.addEventListener('submit',function(e){{e.preventDefault();alert('感谢您的留言！');form.reset();}});
var toggle=document.querySelector('.menu-toggle'),navList=document.querySelector('.nav-list');
if(toggle&&navList)toggle.addEventListener('click',function(){{navList.style.display=navList.style.display==='flex'?'none':'flex';}});
}});'''


# ============ HTTP服务端 ============
class FeizhanServer(SimpleHTTPRequestHandler):
    def _json(self, data, s=200):
        self.send_response(s); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Access-Control-Allow-Origin','*'); self.end_headers()
        self.wfile.write(json.dumps(data,ensure_ascii=False).encode('utf-8'))
    def do_OPTIONS(self):
        self.send_response(200); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.end_headers()
    def do_POST(self):
        if self.path=='/api/generate': self._handle_generate()
        else: self._json({'error':'Not found'},404)
    def do_GET(self):
        if self.path=='/api/config': self._json(FeizhanAPI().get_config()); return
        if self.path=='/api/status': self._json(FeizhanAPI().get_status()); return
        if self.path.startswith('/api/tree'): self._handle_tree(); return
        if self.path.startswith('/api/open'): self._handle_open(); return
        if self.path.startswith('/api/download'): self._handle_download(); return
        if self.path=='/' or self.path=='/ui': self.path='/src/ui/index.html'
        super().do_GET()
    def _handle_generate(self):
        try:
            cl=int(self.headers.get('Content-Length',0)); raw=self.rfile.read(cl)
            try: txt=raw.decode('utf-8')
            except: txt=raw.decode('utf-8',errors='replace')
            r=FeizhanAPI().generate(json.loads(txt))
            self._json(r,200 if r.get('success') else 400)
        except Exception as e: self._json({'success':False,'error':str(e),'detail':traceback.format_exc()},500)
    def _handle_tree(self):
        import urllib.parse; qs=urllib.parse.urlparse(self.path).query; params=urllib.parse.parse_qs(qs); path=params.get('path',[None])[0]
        if not path or not os.path.isdir(path): self._json({'tree':'路径不存在'}); return
        lines=[os.path.basename(path)+'/']
        for root,dirs,files in os.walk(path):
            level=root.replace(path,'').count(os.sep)
            if level>0: lines.append('  '*level+os.path.basename(root)+'/')
            for f in files: lines.append('  '*(level+1)+f)
        self._json({'tree':'\\n'.join(lines)})
    def _handle_open(self):
        import urllib.parse; qs=urllib.parse.urlparse(self.path).query; params=urllib.parse.parse_qs(qs); path=params.get('path',[None])[0]
        if path and os.path.isdir(path):
            try: os.startfile(path); self._json({'success':True})
            except: self._json({'success':False})
        else: self._json({'success':False})
    def _handle_download(self):
        import urllib.parse,zipfile,io; qs=urllib.parse.urlparse(self.path).query; params=urllib.parse.parse_qs(qs); path=params.get('path',[None])[0]
        if not path or not os.path.isdir(path): self._json({'error':'路径无效'},400); return
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as zf:
            for root,dirs,files in os.walk(path):
                for f in files: zf.write(os.path.join(root,f),os.path.relpath(os.path.join(root,f),os.path.dirname(path)))
        buf.seek(0)
        self.send_response(200); self.send_header('Content-Type','application/zip'); self.send_header('Content-Disposition','attachment; filename="'+os.path.basename(path)+'.zip"'); self.end_headers()
        self.wfile.write(buf.read())
    def log_message(self,f,*a): print(f'[飞站] {a[0]}')

def start_server(port=8765):
    os.chdir(PROJECT_ROOT); server=HTTPServer(('0.0.0.0',port),FeizhanServer)
    print(f'\n{"="*50}\n  🛸 飞站 v2 已启动!\n  🌐 http://localhost:{port}\n{"="*50}\n')
    try: server.serve_forever()
    except KeyboardInterrupt: print('\n👋 飞站已停止'); server.shutdown()

def main():
    p=argparse.ArgumentParser(description='飞站 - 一键网站生成器')
    p.add_argument('-t','--type',choices=list(WEBSITE_TYPES.keys()))
    p.add_argument('-s','--style',choices=list(DESIGN_STYLES.keys()))
    p.add_argument('-p','--pages',type=int,choices=[1,2,3],default=2)
    p.add_argument('-f','--features',nargs='+')
    p.add_argument('--ui',action='store_true')
    p.add_argument('--port',type=int,default=8765)
    p.add_argument('--open',action='store_true')
    args=p.parse_args()
    if args.ui:
        if args.open: threading.Timer(1,lambda:webbrowser.open(f'http://localhost:{args.port}')).start()
        start_server(args.port); return
    if args.type and args.style:
        r=FeizhanAPI().generate({'type':args.type,'style':args.style,'pages':args.pages,'features':args.features or []})
        if r['success']: print(f'✅ 成功!\n📁 {r["output"]}')
        else: print(f'❌ {r["error"]}'); sys.exit(1)
    else: p.print_help()

if __name__=='__main__': main()