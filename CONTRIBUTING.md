# Contributing to PINAX Registry

We welcome contributions from both human developers and autonomous AI coding agents. PINAX Registry is an open-source, community-governed database of verified AI agent skills.

Every skill in the registry must meet rigorous engineering, security, and prompt-quality standards before inclusion.

---

## The 4-Stage Quality Gate

All pull requests run automated checks via GitHub Actions. A PR will only be merged when it passes all four verification stages:

```
[Stage 1: Schema]      -> Valid JSON, required fields present, matching enum types
[Stage 2: Antislop]    -> Zero em dashes (\u2014), no AI filler buzzwords, concise prose
[Stage 3: Repository]  -> Valid GitHub owner/repo format, verified CLI install command
[Stage 4: Conflicts]   -> Referential consistency with existing conflict matrices
```

---

## How to Propose a New Skill

### 1. Fork and Clone
Fork `akhmadilham/pinax-registry` and create a descriptive branch:
```bash
git checkout -b skill/your-skill-name
```

### 2. Create the Skill Definition
Add a new JSON file in `data/skills/`. The file name must follow the sequential convention:
`data/skills/<next_index>_<skill_id>.json` (for example: `data/skills/033_my_awesome_skill.json`).

Follow this structure:
```json
{
  "id": "my-awesome-skill",
  "index": "033",
  "name": "my-awesome-skill",
  "repo": "owner/repo",
  "category": "Engineering",
  "type": "Skill",
  "license": "MIT",
  "status": "INSTALL",
  "pinned_commit": null,
  "description": "Clear, practical functional description of what this skill does and when to use it.",
  "install": "npx skills add owner/repo",
  "tags": ["testing", "refactoring", "productivity"],
  "provenance": {
    "verified_at": "2026-11-02",
    "source": "https://github.com/owner/repo"
  }
}
```

### 3. Permitted Values
- **Categories**: `Business`, `Design`, `Discovery`, `Engineering`, `Security`, `SEO`, `Video`, `Writing`.
- **Types**: `Skill`, `Collection`, `Workflow`, `Plugin`, `Tool`, `Vendor`, `Index`.
- **Status**: `INSTALL`, `INSTALL-PINNED`, `INSTALL (tool)`, `INSTALL (per-area)`, `INSTALL (selective)`, `INDEX ONLY`, `MANUAL`.

---

## Local Verification

Before committing, run the local test suite and validator:

```bash
# Run unit tests
python -m unittest discover -s tests

# Run 4-stage validator
python engine/validator.py --root .

# Rebuild catalog and check stats
python engine/builder.py .
```

---

## Autonomous Agent Submissions

Autonomous agents (e.g. Gemini, Claude Code, Cursor) proposing skills on behalf of creators should:
1. Use `engine/scrapers/github_scraper.py --repo owner/repo` to extract repo data.
2. Run `engine/agents/review_agent.py --candidate staging/candidates/repo.json` to generate an audit report.
3. Include the generated review score and findings in the PR description.
4. Ensure strictly zero unicode em dashes (`\u2014`) in descriptions and metadata (Antislop R-02).
