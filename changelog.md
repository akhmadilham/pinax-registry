# PINAX Registry Changelog

All notable changes to the open-source PINAX Skills Database and Review Pipeline are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

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
