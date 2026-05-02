# Changelog

All notable changes to Feizhan (飞站) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-05-02

### Added
- **Visual UI**: 4-step guided wizard for website generation
- **HTTP API**: RESTful endpoints for programmatic access
- **10 CSS Styles**: Each with truly distinct CSS (modern/minimal/bento/brutalist/glass/neumorphic/gradient/dark/cyber/nature)
- **12 Feature Modules**: Full coverage including articles, categories, topics, users, and chat
- **History Management**: localStorage-based, support regenerate from history
- **Code Structure View**: In-UI code tree display
- **Export as ZIP**: One-click code export

### Changed
- Complete rewrite of `generate_css()` for 10 distinct visual styles
- `generate_sections()` now covers all 12 feature modules (was 5)
- `generate_nav_items()` now correctly shows nav items based on selected features
- README rewritten following 2026 GitHub best practices

### Fixed
- CSS/JS paths using relative URLs → changed to absolute paths
- Navigation items not matching selected features (P1)
- Feature modules not generating corresponding sections (P0)
- `unhashable type: 'dict'` when passing style_config incorrectly
- UTF-8 decoding fallback for API requests

## [1.0.0] - 2026-05-02

### Added
- Initial release
- Core website generator engine
- CLI mode with argparse
- 5 website types: company, product, portfolio, blog, forum
- 10 CSS styles (basic color-only differentiation)
- 1-3 page levels
- Basic feature module support (5 of 12)

[2.0.0]: https://github.com/luckychenxiaowen/feizhan/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/luckychenxiaowen/feizhan/releases/tag/v1.0.0
