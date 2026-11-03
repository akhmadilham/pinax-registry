# PINAX Registry

> Open-source database of verified skills for AI coding agents.

[![Live Catalog](https://img.shields.io/badge/Live%20Catalog-pinax--skills.vercel.app-blue.svg)](https://pinax-skills.vercel.app/)
[![Skills Count](https://img.shields.io/badge/skills-145%20verified-cyan.svg)](data/skills)
[![Categories](https://img.shields.io/badge/categories-8%20domains-blueviolet.svg)](data/categories.json)
[![Schema](https://img.shields.io/badge/schema-Draft--2020--12-blue.svg)](schema/skill.schema.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Validation Suite](https://img.shields.io/badge/Quality%20Gate-4--Stage%20Passed-emerald.svg)](tests)

---

> [!TIP]
> **Looking for the interactive web catalog?**  
> Browse the visual atlas, filter by domain, resolve tool conflicts, 
and copy 1-click install prompts at 
>**[pinax-skills.vercel.app](https://pinax-skills.vercel.app/)**.

---

## Overview

<!-- PINAX_STATS:START -->
PINAX currently tracks **145 verified skills** across **8 domains** for autonomous coding agents (Claude Code, Cursor, Codex, and Antigravity). Every skill is audited for safe commands, validated against a formal JSON schema, and checked for tool overlaps.
<!-- PINAX_STATS:END -->

Agent skills give coding agents specialized domain workflows. However, community skills often run into three practical issues:

1. **Fragmented discovery**: Skills are scattered across gists, repositories, and social announcements without standard installation formats.
2. **Instruction conflicts**: Installing multiple skills that overlap in scope confuses agent reasoning and degrades code output.
3. **Unvetted execution**: Community prompts may bundle unsafe terminal execution, hidden network calls, or unclear licenses.

PINAX provides a transparent, schema-governed database to solve these issues. Each entry includes tested install commands, verified commit hashes, and conflict rules to ensure reliable execution.

---

## Verified Domains

<!-- PINAX_DOMAINS:START -->
| Domain | Skills | Lead Skill | Core Focus |
| :--- | :---: | :--- | :--- |
| 🎨 **Design** | 48 | `hallmark` | Make every detail intentional |
| ⚙️ **Engineering** | 34 | `superpowers` | Go from idea to implementation with confidence |
| 💼 **Business** | 19 | `founder-skill` | Build a smarter workflow around the tools and vendors you actually use |
| ✍️ **Writing** | 13 | `no-ai-slop` | Turn ideas into writing worth reading |
| 🎬 **Video** | 11 | `ffmpeg-skill` | Create, process, and refine video with reliable workflows |
| 🔍 **SEO** | 9 | `seranking-seo-skills` | Audit, fix, and measure search and AI answer visibility, from technical checks to content and ranking |
| 🛡️ **Security** | 8 | `trailofbits/skills` | Find vulnerabilities before they become problems |
| 🧭 **Discovery** | 3 | `awesome-agent-skills` | Explore new capabilities beyond the atlas |
| **Total** | **145** | | |
<!-- PINAX_DOMAINS:END -->

---

## Core Architecture

| Pillar | How it works |
| :--- | :--- |
| **8 Curated Domains** | Grouped into real developer roles (Design, Engineering, Video, Business, Writing, Security, Discovery). |
| **Conflict Matrix** | Automatically catches hard incompatibilities and soft overlaps between tools in `data/conflicts.json`. |
| **Deterministic Standards** | Enforces JSON Schema (Draft-2020-12) typing, open-source licenses, and tested CLI commands. |
| **Headless Catalog** | Releases a single, machine-readable manifest (`data/catalog.json`) with a SHA-256 integrity checksum. |

---

## Ecosystem Navigation

| Platform | Role | Description |
| :--- | :--- | :--- |
| **[pinax-skills.vercel.app](https://pinax-skills.vercel.app/)** | Interactive Web Catalog | Visual explorer with category filters, multi-skill checkout, and single-prompt generation. |
| **PINAX Registry** *(This Repository)* | Canonical Database | Headless Git database with modular JSON skill files, automated validation, and compiler engine. |

---

## How to Submit a Skill

Submissions from authors and maintainers are welcome.

### Option 1: Submit via GitHub Issue (Recommended)

1. Open a new issue in this repository using the [Skill Submission Template](../../issues/new?template=skill_submission.md).
2. Fill in the key details:
   - **Skill Name & GitHub Repository URL**
   - **Domain Category** (`Business`, `Design`, `Discovery`, `Engineering`, `Security`, `SEO`, `Video`, or `Writing`)
   - **Type** (`Skill`, `Collection`, `Workflow`, `Plugin`, `Tool`, `Vendor`, or `Index`)
   - **Concise Description** explaining real utility
   - **Installation Command** (e.g. `npx skills add owner/repo`)
3. The maintainers will review the submission against verification criteria, run automated validation, and merge it into the catalog.

### Option 2: Submit via Pull Request

If you prefer to submit directly:

1. Fork this repository and create a new branch.
2. Add a new JSON file under `data/skills/` following the schema format:
   ```json
   {
     "id": "example-skill",
     "index": "050",
     "name": "example-skill",
     "repo": "owner/repo",
     "category": "Engineering",
     "type": "Skill",
     "license": "MIT",
     "status": "INSTALL",
     "pinned_commit": null,
     "description": "Functional description of capabilities and agent triggers.",
     "install": "npx skills add owner/repo",
     "tags": ["tag1", "tag2"],
     "provenance": {
       "verified_at": "2026-11-02",
       "source": "https://github.com/owner/repo"
     }
   }
   ```
3. Test your entry locally using the validation suite:
   ```bash
   python engine/validator.py --root .
   ```
4. Build the catalog (automatically updates `data/catalog.json` and `README.md` metrics):
   ```bash
   python engine/builder.py .
   ```
5. Open a Pull Request.

---

## Verification Standards

Every skill submitted to PINAX Registry passes through a 4-stage verification gate before publication:

### 1. Schema & Structural Integrity
- **Strict Typing**: All entries conform to `schema/skill.schema.json` (JSON Schema Draft-2020-12).
- **Mandatory Fields**: Required identifiers, author attribution, public repository URL, license type, and execution tier.
- **Valid Taxonomy**: Categorized accurately into one of the 8 Pantheon domains without arbitrary categorization drift.

### 2. Security & Safety Screening
- **Public & Auditable**: Repositories must be public with open-source licenses (MIT, Apache 2.0, BSD, etc.).
- **No Malicious Patterns**: Submissions are screened against prompt injection exploits, hidden surveillance telemetry, obfuscated network requests, and unvetted root execution scripts.
- **Reproducible Installation**: Installation instructions must point to legitimate packages or verified repository paths.

### 3. Practical Utility & Clarity Standards
- **High-Signal Documentation**: Documentation must be functional and focused on concrete developer tasks.
- **Antislop Policy**: Vague marketing fluff, hyperbolic promises, and generic AI buzzwords are rejected.
- **Typographic Precision**: In adherence to Antislop R-02 standards, Unicode em dashes (`\u2014`) are disallowed across all descriptions and metadata.

### 4. Conflict & Compatibility Matrix
- **Mutual Exclusion Check**: Potential conflicts with existing skills (e.g., competing frontend scaffolding tools) are identified and recorded in `data/conflicts.json`.
- **Resolution Advice**: Soft overlaps receive clear scoping guidance to help developers choose the appropriate tool for their workflow.

---

## Accessing the Data

### Canonical Catalog Download
The complete, compiled registry is released as a single verified JSON manifest with a SHA-256 integrity checksum:

```bash
# Fetch latest compiled catalog
curl -s https://raw.githubusercontent.com/akhmadilham/pinax-registry/main/data/catalog.json | jq .
```

### JSON Schema
Validate third-party skill definitions directly against the official schema:

```
schema/skill.schema.json
```

---

## Repository Layout

```
pinax-registry/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── skill_submission.md   # GitHub Issue template for proposals
│   └── workflows/
│       ├── validate.yml          # Automated 4-stage quality gate CI
│       └── build.yml             # Release compiler and checksum validator
├── data/
│   ├── skills/                   # Modular skill definitions (001 to 145+)
│   ├── categories.json           # 8 domain categories and visual tokens
│   ├── conflicts.json            # Hard and soft conflict matrix rules
│   └── catalog.json              # Canonical compiled distribution manifest
├── engine/
│   ├── validator.py              # CLI validation engine
│   └── builder.py                # Release compiler and README metrics updater
├── schema/
│   └── skill.schema.json         # Formal JSON Schema specification
├── tests/
│   └── test_validator.py         # Unit tests for validation logic
├── CONTRIBUTING.md               # Guidelines for contributors
├── LICENSE                       # MIT License
├── README.md                     # Project documentation
└── changelog.md                  # Version history
```

---

## License

This registry and all associated schemas are released under the [MIT License](LICENSE).
