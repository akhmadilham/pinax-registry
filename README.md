# PINAX Registry

> Headless open-source database, verification engine, and autonomous scraping pipeline for AI coding agent skills.

[![Validate PINAX Skills](https://github.com/akhmadilham/pinax-registry/actions/workflows/validate.yml/badge.svg)](https://github.com/akhmadilham/pinax-registry/actions/workflows/validate.yml)
[![Skills Count](https://img.shields.io/badge/skills-32%20verified-cyan.svg)](data/skills)
[![Categories](https://img.shields.io/badge/categories-7%20pantheon-blueviolet.svg)](data/categories.json)
[![Schema](https://img.shields.io/badge/schema-Draft--2020--12-blue.svg)](schema/skill.schema.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

**PINAX Registry** is the canonical, open-source database powering the PINAX ecosystem. It provides structured, peer-reviewed, and cryptographically verified metadata for AI coding skills used across Claude Code, Cursor, Codex, Antigravity, and other agentic environments.

This repository operates as a **headless data provider**. The user interface lives separately in [pinax-skills](https://github.com/akhmadilham/pinax-skills).

```
   ┌────────────────────────────────────────────────────────┐
   │                    SIGNAL DISCOVERY                    │
   │   GitHub Search Crawler   │   X (Twitter) Signal Parser │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │                 AUTONOMOUS REVIEW AGENT                │
   │   Security Audit  •  Quality Score  •  Taxonomy Match   │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │                 4-STAGE QUALITY GATE                   │
   │   Stage 1: Schema Integrity                            │
   │   Stage 2: Antislop R-02 (Zero Em Dashes, Clean Prose) │
   │   Stage 3: Repository & Installation Command Integrity │
   │   Stage 4: Conflict Matrix Referential Consistency     │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │               CANONICAL CATALOG COMPILATION            │
   │        data/catalog.json (with SHA-256 Checksum)       │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
                   CONSUMERS & WEB INTERFACES
              (PINAX Skills Web UI, CLIs, Agents)
```

---

## Repository Layout

```
pinax-registry/
├── .github/
│   └── workflows/
│       ├── validate.yml          # Runs 4-stage quality gate on all PRs & pushes
│       └── build.yml             # Compiles data/catalog.json and validates checksum
├── data/
│   ├── skills/                   # 32 modular, schema-compliant skill definitions
│   │   ├── 001_addyosmani_agent_skills.json
│   │   ├── 002_agent_scan.json
│   │   └── ...
│   ├── categories.json           # 7 Pantheon domain categories and color tokens
│   ├── conflicts.json            # Hard exclusive and soft compatibility matrices
│   └── catalog.json              # Compiled release manifest with SHA-256 checksum
├── engine/
│   ├── validator.py              # 4-stage validation engine and CLI
│   ├── builder.py                # Catalog compiler, statistics generator, and hash verifier
│   ├── scrapers/
│   │   ├── github_scraper.py     # GitHub API crawler extracting SKILL.md metadata
│   │   └── x_scraper.py          # X / Twitter signal scraper for trending skill repos
│   └── agents/
│       └── review_agent.py       # Autonomous LLM/agent auditor and scoring engine
├── schema/
│   └── skill.schema.json         # Formal JSON Schema specification (Draft-2020-12)
├── tests/
│   └── test_validator.py         # Unit test suite for validation rules
├── CONTRIBUTING.md               # Guidelines for human contributors and AI agents
├── LICENSE                       # MIT License
├── README.md                     # Project documentation
└── changelog.md                  # Release history and updates
```

---

## Using the Data

### Consuming the Full Catalog
You can fetch the latest verified catalog directly from GitHub raw content or any CDN:

```bash
curl -s https://raw.githubusercontent.com/akhmadilham/pinax-registry/main/data/catalog.json | jq .
```

### JSON Schema
All skill definitions strictly conform to `schema/skill.schema.json`:
- **Categories**: `Business`, `Design`, `Discovery`, `Engineering`, `Security`, `Video`, `Writing`
- **Archetypes**: `Skill`, `Collection`, `Workflow`, `Plugin`, `Tool`, `Vendor`, `Index`
- **Tiers**: `INSTALL`, `INSTALL-PINNED`, `INSTALL (tool)`, `INDEX ONLY`, `MANUAL`

---

## Development & Tooling

### 1. Validate All Skills
Run the 4-stage quality gate locally:
```bash
python engine/validator.py --root .
```

### 2. Run Test Suite
```bash
python -m unittest discover -s tests
```

### 3. Rebuild Catalog
Compile modular files into `data/catalog.json`:
```bash
python engine/builder.py .
```

### 4. Crawl GitHub Repositories
Extract skills from a specific repository:
```bash
python engine/scrapers/github_scraper.py --repo owner/repo
```

### 5. Audit Candidate with Review Agent
Run autonomous safety and quality scoring on a staged candidate:
```bash
python engine/agents/review_agent.py --candidate staging/candidates/repo.json
```

---

## Quality Principles

1. **Deterministic Quality**: Every skill must have a verified author, clear license, and concrete install command.
2. **Antislop Standards**: Prose must be functional, compact, and free of generic AI puffery. Unicode em dashes (`\u2014`) are strictly disallowed.
3. **Decoupled Autonomy**: Autonomous agents can crawl, review, validate, and propose skills via standard Git pull requests without human bottleneck.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
