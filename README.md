# PINAX Registry

> Open-source database and verification framework for AI coding agent skills.

[![Live Catalog](https://img.shields.io/badge/Live%20Catalog-pinax--skills.vercel.app-blue.svg)](https://pinax-skills.vercel.app/)
[![Skills Count](https://img.shields.io/badge/skills-32%20verified-cyan.svg)](data/skills)
[![Categories](https://img.shields.io/badge/categories-7%20domains-blueviolet.svg)](data/categories.json)
[![Schema](https://img.shields.io/badge/schema-Draft--2020--12-blue.svg)](schema/skill.schema.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Validation Suite](https://img.shields.io/badge/Quality%20Gate-4--Stage%20Passed-emerald.svg)](tests)

---

> [!TIP]
> **Looking for the interactive web catalog?**  
> Explore the visual atlas, test category filters, resolve skill conflicts, and generate 1-click install prompts at **[pinax-skills.vercel.app](https://pinax-skills.vercel.app/)**.

---

## About PINAX

The word *pinax* (Greek: πίναξ) refers to the classical tablets displayed in ancient libraries and sanctuaries to index monumental knowledge and public catalogs. **PINAX Registry** applies that foundational standard to the modern ecosystem of AI coding agents.

As autonomous engineering agents (Claude Code, Cursor, Codex, Antigravity) become central to modern software development, agent capabilities ("skills") are proliferating rapidly. However, developers and teams frequently encounter three critical hurdles:

1. **Discovery Fragmentation**: Useful skills remain buried across scattered repositories, personal gists, and transient social announcements without clear documentation.
2. **Instruction Conflicts**: Installing multiple skills that overlap in scope (such as competing UI frameworks or conflicting code review directives) confuses agent reasoning and degrades output quality.
3. **Security and Safety Risks**: Community-sourced skill prompts may introduce hidden prompt injections, unsafe bash execution pipes, or undisclosed tracking.

**PINAX Registry** provides a curated, transparent, and schema-governed database to solve these challenges. Every skill is audited, categorized, and cross-referenced with a conflict matrix to guarantee reliable agent execution.

---

## Core Architectural Pillars

| Pillar | Description |
| :--- | :--- |
| 🏛️ **7 Pantheon Domains** | Curated across **Business**, **Design**, **Discovery**, **Engineering**, **Security**, **Video**, and **Writing** to map cleanly to real developer jobs. |
| ⚖️ **Conflict Matrix** | Proactively identifies hard exclusions and soft overlaps between tools, offering clear resolution recommendations. |
| 🔒 **Deterministic Standards** | Enforces strict JSON Schema (Draft-2020-12) validation, verified license declarations, and tested CLI install commands. |
| 🌐 **Headless Distribution** | Cleanly separated machine-readable manifests (`data/catalog.json`) designed for consumption by CLIs, web interfaces, and automated agent workflows. |

---

## Ecosystem Navigation

| Platform | Role | Description |
| :--- | :--- | :--- |
| **[pinax-skills.vercel.app](https://pinax-skills.vercel.app/)** | Interactive Web Catalog | Visual explorer with responsive Pantheon cards, multi-skill selection checkout, and 1-click single-prompt generation. |
| **PINAX Registry** *(This Repository)* | Canonical Data Source | Headless Git database containing modular JSON skill definitions, JSON schemas, and automated validation gates. |

---

## How to Submit a Skill

We welcome submissions from creators, open-source developers, and teams building agent tools. You can submit skills through either of the following methods:

### Option 1: Submit via GitHub Issue (Recommended)

1. Open a new issue in this repository using the [Skill Submission Template](../../issues/new?template=skill_submission.md).
2. Fill in the key details:
   - **Skill Name & GitHub Repository URL**
   - **Domain Category** (`Business`, `Design`, `Discovery`, `Engineering`, `Security`, `Video`, or `Writing`)
   - **Type** (`Skill`, `Collection`, `Workflow`, `Plugin`, `Tool`, `Vendor`, or `Index`)
   - **Concise Description** explaining real utility
   - **Installation Command**
3. The maintainers will review the submission against the verification criteria below, run automated validation, and merge it into the catalog.

### Option 2: Submit via Pull Request

If you prefer to submit directly:

1. Fork this repository and create a new branch.
2. Add a new JSON file under `data/skills/` following the schema format:
   ```json
   {
     "id": "example-skill",
     "index": "033",
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
4. Open a Pull Request.

---

## Verification Methodology & Quality Standards

Every skill submitted to PINAX Registry passes through a 4-stage verification gate before publication:

### 1. Schema & Structural Integrity
- **Strict Typing**: All entries conform to `schema/skill.schema.json` (JSON Schema Draft-2020-12).
- **Mandatory Fields**: Required identifiers, author attribution, public repository URL, license type, and execution tier.
- **Valid Taxonomy**: Categorized accurately into one of the 7 Pantheon domains without arbitrary categorization drift.

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
│   ├── skills/                   # Modular skill definitions (001 to 032+)
│   ├── categories.json           # 7 domain categories and visual tokens
│   ├── conflicts.json            # Hard and soft conflict matrix rules
│   └── catalog.json              # Canonical compiled distribution manifest
├── engine/
│   ├── validator.py              # CLI validation engine
│   └── builder.py                # Release manifest compiler and hash verifier
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
