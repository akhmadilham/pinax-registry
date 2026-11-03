# PINAX Registry Changelog

All notable changes to the open-source PINAX Skills Database and Review Pipeline are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.6.0] - 2026-11-03

### Added
- **Community Skills Integration (Batch Issues #35 to #97, Index 085 to 145)**:
  - Added 61 verified open-source skills across 5 Pantheon domains (Design +30, Engineering +13, Business +10, Writing +4, Video +4).
  - Registry now hosts 145 canonical skills across all 8 Pantheon domains (74% commit-pinned).
  - Included notable tools and collections: `google/skills`, `alibaba/open-code-review`, `LottieFiles/motion-design-skill`, `awslabs/agent-plugins`, `Graphify-Labs/graphify`, `google/elephant-goldfish-model`, and `huashu-design`.
- **Enforced Safety and Language Guards**:
  - Pinned safety guardrails on Issue #91 (`spec-driven-develop` restricted strictly to Claude plugin route).
  - Injected security token leak warnings for auto-commit tools (Issue #92 `self-learning`).
  - Flagged billable cloud dependencies (Issue #93 `agent-plugins`) and live account posting requirements (Issue #76 `openclaw-marketing-skills`).
  - Explicitly tagged locale-specific skills for `zh-CN` (#94, #95, #96) and `zh-TW` (#97).

### Rejected
- **SOP Compliance Rejections**:
  - Issue #53 (`Youtube-clipper-skill`): Closed due to platform Terms of Service scraping risk.
  - Issue #81 (`cc-design`): Closed due to missing open-source LICENSE file in repository tree.
  - Issue #98 (`xiaohu-wechat-format`): Closed due to missing LICENSE file in repository root.

## [1.5.0] - 2026-11-02

### Added
- **Stageshow Integration (`benjitaylor/skills`, Index 084)**:
  - Integrated `084_stageshow.json` under Design domain (Skill, MIT, pinned at `8020574`).
  - Authored miniature product UI illustrations, interactive cursor walkthroughs, bento grids, and headless filming verification tools.
  - Re-compiled canonical `data/catalog.json` featuring 84 verified skills across 8 Pantheon domains (Design domain now holding 18 skills).

## [1.4.0] - 2026-11-02

### Added
- **Batch SEO Skills Integration (Issues #29 to #34, Index 078 to 083)**:
  - `078_seo_intelligence_skill.json`: `Trementdv/seo-intelligence-skill` (Issue #29, pinned at `f4b287f`).
  - `079_geo_seo_claude.json`: `zubair-trabzada/geo-seo-claude` (Issue #30, pinned at `989cae0`).
  - `080_seo_audit_skill.json`: `JeffLi1993/seo-audit-skill` (Issue #31, pinned at `523bdfb`).
  - `081_youtube_seo_skills.json`: `deeployCO/youtube-seo-skills` (Issue #32, pinned at `779b0f1`).
  - `082_claude_youtube.json`: `AgriciDaniel/claude-youtube` (Issue #33, pinned at `84c3fa6`).
  - `083_sv_seo_aeo.json`: `sva-admin/sv-seo-aeo` (Issue #34, pinned at `ca0ebcc`).
- **Conflict Matrix Extensions**:
  - Added soft conflict resolution in `data/conflicts.json` between `youtube-seo-skills` and `claude-youtube`.
  - Added soft conflict resolution between `seo-intelligence-skill` and `claude-seo`.
- **Catalog Compilation**:
  - Re-compiled canonical `data/catalog.json` with 83 verified skills across 8 Pantheon domains (SEO now holding 9 skills).

## [1.3.0] - 2026-11-02

### Added
- **Claude SEO Integration (`AgriciDaniel/claude-seo`)**:
  - Integrated `077_claude_seo.json` (SEO, Plugin, pinned at `6be93f4`).
  - Added soft conflict resolution matrix in `data/conflicts.json` between `claude-seo` (19-agent plugin) and `claude-seo-kit` (standalone Python engine).
  - Re-compiled canonical `data/catalog.json` featuring 77 verified skills across 8 Pantheon domains.

## [1.2.1] - 2026-11-02

### Changed
- **Documentation & Engine Synchronization**:
  - Expanded `engine/builder.py` auto-updating regex engine to dynamically maintain domain counts across `## Core Architecture` and `## Repository Layout` in `README.md`.
  - Added `SEO` category to the permitted submission categories in `CONTRIBUTING.md` and `README.md` issue proposal guide.
  - Synchronized taxonomy references to reflect all 8 Pantheon domains.

## [1.2.0] - 2026-11-02

### Added
- **New Domain Category: SEO (8th Pantheon Domain)**:
  - Registered `seo` domain in `data/categories.json` (Order 8, Color `#fb923c`, Icon `search`, Lead Skill `seranking-seo-skills`).
  - Updated `schema/skill.schema.json`, `engine/validator.py`, `engine/builder.py`, and `engine/agents/review_agent.py` to support `SEO`.
- **27 Verified Community Skills Integrated (Issues #2 to #28, Index 050 to 076)**:
  - Business (10 skills): `marketingskills`, `aaron-marketing-skills`, `openclaudia-skills`, `marketing-skills`, `closer-skill`, `agentic-sales-skills`, `hubspot-admin-skills`, `growth-today-claude-skills`, `openaccountant-skills`, `claude-code-startup-skills`.
  - Engineering (4 skills): `pulumi-agent-skills`, `cc-skills-golang`, `claude-postgres-skills`, `smell-check`.
  - Security (5 skills): `gitguardian-agent-skills`, `ai-repo-safety-skill`, `threat-modeling-agent-skills`, `secure-code-review-agent-skills`, `vulnerability-management-agent-skills`.
  - Writing (6 skills): `ux-writing-skill`, `humanize-text`, `docs-writing`, `google-developer-docs-style`, `ste-plain-writing`, `agent-writing-skills`.
  - SEO (2 skills): `seranking-seo-skills`, `claude-seo-kit`.
- **Conflict Matrix Extensions**:
  - Added soft conflict pairings and resolutions in `data/conflicts.json` for `seranking-seo-skills` vs `claude-seo-kit`, `docs-writing` vs `ste-plain-writing`, and `closer-skill` vs `agentic-sales-skills`.
- **Catalog Compilation**:
  - Re-compiled canonical manifest `data/catalog.json` with 76 verified skills across 8 domains.
  - Automatically updated README metrics and domain breakdown table via `engine/builder.py`.

## [1.1.0] - 2026-11-02

### Added
- **Emil Kowalski Design Engineering Skills Suite (17 verified definitions)**:
  - Integrated complete suite from `emilkowalski/skills` pinned at commit `a81dbca`:
    - `033_emilkowalski_skills.json`: `emilkowalski-skills` (Collection, Design) - Wholesale collection covering 16 design engineering skills.
    - `034_animate.json`: `animate` (Skill, Design) - Principled animation construction from scratch.
    - `035_animate_expo.json`: `animate-expo` (Skill, Design) - React Native and Expo animations with Reanimated and expo-haptics.
    - `036_animation_performance.json`: `animation-performance` (Skill, Engineering) - Frame budget, composite-only properties, and GPU offloading.
    - `037_animation_vocabulary.json`: `animation-vocabulary` (Skill, Writing) - Reverse-lookup glossary translating informal motion ideas to technical terms.
    - `038_apple_design.json`: `apple-design` (Skill, Design) - Apple WWDC fluid motion and interface design principles translated for web.
    - `039_ask_sonner.json`: `ask-sonner` (Skill, Engineering) - Complete guide and recipes for Sonner toast library.
    - `040_break_ui.json`: `break-ui` (Skill, Engineering) - UI stress-testing with worst-case edge data.
    - `041_emil_design_eng.json`: `emil-design-eng` (Skill, Design) - Core UI polish and design engineering philosophy.
    - `042_find_animation_opportunities.json`: `find-animation-opportunities` (Skill, Discovery) - Finding purposeful motion spots and rejecting noise.
    - `043_improve_animations.json`: `improve-animations` (Skill, Design) - Codebase animation audit and prioritized action roadmap.
    - `044_mobile_native.json`: `mobile-native` (Skill, Engineering) - Eliminating browser artifacts on mobile viewports.
    - `045_pick_ui_library.json`: `pick-ui-library` (Tool, Discovery) - Curated battle-tested UI library selector.
    - `046_prototype.json`: `prototype` (Skill, Design) - Multi-variant generation with interactive switcher.
    - `047_remove_animations.json`: `remove-animations` (Skill, Design) - Pruning redundant animations and over-motion.
    - `048_review_animations.json`: `review-animations` (Skill, Design) - Strict motion craft audit and easing validation.
    - `049_write_swift.json`: `write-swift` (Skill, Engineering) - Modern Swift 6 concurrency, value types, and testing.
  - Added soft conflict resolution matrix in `data/conflicts.json` for `emilkowalski-skills` collection vs individual sub-skills.
  - Re-compiled canonical manifest `data/catalog.json` with 49 verified skills across all 7 Pantheon domains.

## [1.0.3] - 2026-11-02

### Changed
- **Comprehensive About & Architecture Presentation**:
  - Replaced plain overview link with a styled GitHub tip callout, historical etymology context, and structured problem-solution narrative.
  - Added dedicated Core Architectural Pillars table (7 Pantheon Domains, Conflict Matrix, Deterministic Standards, Headless Distribution).
  - Added Ecosystem Navigation table distinguishing the interactive web explorer (pinax-skills.vercel.app) from the headless data registry.

## [1.0.2] - 2026-11-02

### Changed
- **Community-Focused README Rewrite**:
  - Restructured README to emphasize open-source community submissions and transparent verification methodology.
  - Added structured GitHub Issue submission template (.github/ISSUE_TEMPLATE/skill_submission.md).
  - Removed all frontend codebase references, personal metadata, and internal crawler/scraping mechanisms.
  - Highlighted 4-stage verification standards: Schema Integrity, Security & Safety Screening, Practical Utility & Antislop, and Conflict Matrix Analysis.

## [1.0.1] - 2026-11-02

### Changed
- **Documentation Refinement & Cross-Linking**:
  - Added direct links and badges to the live web application at https://pinax-skills.vercel.app/ and the frontend repository akhmadilham/pinax-skills.
  - Documented the automated Vercel Deploy Hook synchronization workflow in README.md.

## [1.0.0] - 2026-11-02

### Added
- **Canonical Skill Database**: 32 production-verified AI coding agent skills across 7 pantheon categories (`Business`, `Design`, `Discovery`, `Engineering`, `Security`, `Video`, `Writing`).
- **Modular Data Architecture**: Individual schema-compliant JSON files stored in `data/skills/` with sequential 3-digit identifiers.
- **Formal JSON Schema**: Draft-2020-12 specification in `schema/skill.schema.json` validating skill metadata, status tiers, repository links, and archetypes.
- **Compiled Distribution Catalog**: Consolidated `data/catalog.json` with SHA-256 integrity checksum, real-time statistics, and conflict matrices.
- **4-Stage Validation Engine**: `engine/validator.py` enforcing schema compliance, Antislop R-02 standards (zero em dashes, concise prose), repository link structure, and conflict matrix consistency.
- **Catalog Builder**: `engine/builder.py` for automated compilation, sorting, statistical auditing, and distribution packaging.
- **GitHub Scraper**: `engine/scrapers/github_scraper.py` crawling repositories for `SKILL.md` frontmatter, licenses, and stars.
- **Social Signal Scraper**: `engine/scrapers/x_scraper.py` extracting viral skill announcements and GitHub repositories from X (Twitter).
- **Autonomous Review Agent**: `engine/agents/review_agent.py` evaluating candidate skills for security exploits, prompt quality, taxonomy classification, and conflict warnings.
- **Continuous Integration Workflows**: GitHub Actions workflows in `.github/workflows/` for automated validation and catalog publishing on pull requests and commits.
- **Unit Test Suite**: `tests/test_validator.py` covering schema boundaries, Antislop rules, and conflict referential integrity.
