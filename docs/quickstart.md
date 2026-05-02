# Quick Start Guide

> ⚡ Get your first website up in 30 seconds.

## 1. Install

```bash
git clone https://github.com/YOUR_NAME/sitemaker.git
cd feizhan/飞站skill
```

Zero dependencies required! Feizhan uses only Python standard library.

## 2. Launch the Visual UI

```bash
python feizhan.py --ui
```

Open **http://localhost:8765** in your browser.

## 3. Create Your First Site

Follow the 4-step wizard:

1. **Select Type** → Company, Product, Portfolio, Blog, or Forum
2. **Pick Style** → 10 CSS styles to choose from
3. **Configure Features** → Check the modules you need (About, Products, Contact, etc.)
4. **Generate** → One click and your site is ready!

## 4. Preview & Export

- Click **Preview** to see your generated website
- Click **View Source** to inspect the code structure
- Click **Export** to download as ZIP

## CLI Quick Start

Prefer the command line?

```bash
# Company website, modern style, 2-level depth
python feizhan.py -t company -s modern -p 2

# Portfolio, glass-morphism style, single page
python feizhan.py -t portfolio -s glass -p 1

# Blog, dark theme
python feizhan.py -t blog -s dark -p 2 -f article category contact
```

## Generated Structure

```
outputs/company_modern_20260502_102450/
├── index.html      # Main page
├── css/
│   └── style.css   # Generated stylesheet
├── js/
│   └── main.js     # Interactions
└── site.json       # Site configuration
```

## Next Steps

- [API Reference](api.md) — Integrate Feizhan into your workflow
- [CSS Styles Guide](styles.md) — Preview all 10 design styles
- [Feature Modules](features.md) — Learn about available modules
