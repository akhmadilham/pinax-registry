#!/usr/bin/env python3
"""
PINAX Skills Catalog Builder
Compiles modular data/skills/*.json, data/categories.json, and data/conflicts.json
into the canonical distribution manifest data/catalog.json.
"""

import os
import sys
import json
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

# Ensure engine path is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validator import validate_skill_data, validate_conflicts


def compute_sha256(content_bytes):
    return hashlib.sha256(content_bytes).hexdigest()


def update_readme(registry_root, compiled_skills, categories_data):
    """
    Auto-updates README.md with live skill and category metrics:
      - Badges: skills count and categories count
      - Dynamic description paragraph (wrapped in <!-- PINAX_STATS:START/END -->)
      - Category breakdown table (wrapped in <!-- PINAX_DOMAINS:START/END -->)
      - File tree modular range comment
    Guarantees strict Antislop R-02 compliance (0 em dashes).
    """
    root = Path(registry_root).resolve()
    readme_file = root / "README.md"
    if not readme_file.exists():
        return

    try:
        with open(readme_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"[WARN] Unable to read README.md for auto-update: {e}")
        return

    total_skills = len(compiled_skills)
    categories = categories_data.get("categories", [])
    total_categories = len(categories)
    cat_counts = Counter(s.get("category") for s in compiled_skills)
    max_index = compiled_skills[-1].get("index", f"{total_skills:03d}") if compiled_skills else "001"

    # 1. Update badges
    content = re.sub(
        r"badge/skills-\d+%20verified-cyan\.svg",
        f"badge/skills-{total_skills}%20verified-cyan.svg",
        content
    )
    content = re.sub(
        r"badge/categories-\d+%20domains-blueviolet\.svg",
        f"badge/categories-{total_categories}%20domains-blueviolet.svg",
        content
    )

    # 2. Update directory tree line
    content = re.sub(
        r"(data/skills/\s+# Modular skill definitions \(001 to )\d+\+(\))",
        rf"\g<1>{max_index}+\2",
        content
    )

    # 3. Dynamic Stats Block
    stats_block = (
        "<!-- PINAX_STATS:START -->\n"
        f"PINAX currently tracks **{total_skills} verified skills** across **{total_categories} domains** "
        f"for autonomous coding agents (Claude Code, Cursor, Codex, and Antigravity). "
        f"Every skill is audited for safe commands, validated against a formal JSON schema, "
        f"and checked for tool overlaps.\n"
        "<!-- PINAX_STATS:END -->"
    )

    if "<!-- PINAX_STATS:START -->" in content and "<!-- PINAX_STATS:END -->" in content:
        content = re.sub(
            r"<!-- PINAX_STATS:START -->.*?<!-- PINAX_STATS:END -->",
            stats_block,
            content,
            flags=re.DOTALL
        )

    # 4. Dynamic Domains Table
    category_icons = {
        "Business": "💼",
        "Design": "🎨",
        "Discovery": "🧭",
        "Engineering": "⚙️",
        "Security": "🛡️",
        "SEO": "🔍",
        "Video": "🎬",
        "Writing": "✍️"
    }

    sorted_cats = sorted(categories, key=lambda c: cat_counts.get(c.get("name"), 0), reverse=True)

    table_lines = [
        "<!-- PINAX_DOMAINS:START -->",
        "| Domain | Skills | Lead Skill | Core Focus |",
        "| :--- | :---: | :--- | :--- |"
    ]
    for c in sorted_cats:
        cname = c.get("name", "")
        icon = category_icons.get(cname, "📦")
        count = cat_counts.get(cname, 0)
        lead = f"`{c.get('lead_skill')}`" if c.get("lead_skill") else "-"
        desc = c.get("description", "")
        first_sentence = desc.split(".")[0].strip() if desc else ""
        table_lines.append(f"| {icon} **{cname}** | {count} | {lead} | {first_sentence} |")

    table_lines.append(f"| **Total** | **{total_skills}** | | |")
    table_lines.append("<!-- PINAX_DOMAINS:END -->")
    domains_block = "\n".join(table_lines)

    if "<!-- PINAX_DOMAINS:START -->" in content and "<!-- PINAX_DOMAINS:END -->" in content:
        content = re.sub(
            r"<!-- PINAX_DOMAINS:START -->.*?<!-- PINAX_DOMAINS:END -->",
            domains_block,
            content,
            flags=re.DOTALL
        )

    # Antislop check: guarantee zero em dashes
    content = content.replace("\u2014", ": ")

    try:
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[SUCCESS] Updated README.md metrics ({total_skills} skills, {total_categories} domains).")
    except Exception as e:
        print(f"[WARN] Failed to write updated README.md: {e}")


def build_catalog(registry_root):
    root = Path(registry_root).resolve()
    skills_dir = root / "data" / "skills"
    categories_file = root / "data" / "categories.json"
    conflicts_file = root / "data" / "conflicts.json"
    catalog_file = root / "data" / "catalog.json"

    print("=" * 60)
    print("PINAX REGISTRY CATALOG BUILDER")
    print(f"Target Root: {root}")
    print("=" * 60)

    # 1. Load categories
    if not categories_file.exists():
        print(f"[ERROR] Missing categories manifest: {categories_file}")
        return 1
    with open(categories_file, "r", encoding="utf-8") as f:
        categories_data = json.load(f)

    # 2. Load conflicts
    if not conflicts_file.exists():
        print(f"[ERROR] Missing conflicts manifest: {conflicts_file}")
        return 1
    with open(conflicts_file, "r", encoding="utf-8") as f:
        conflicts_data = json.load(f)

    # 3. Load & validate individual skill files
    skill_files = sorted(list(skills_dir.glob("*.json")))
    if not skill_files:
        print(f"[ERROR] No skill JSON files found in {skills_dir}")
        return 1

    compiled_skills = []
    registered_ids = set()
    registered_names = set()
    validation_failures = 0

    for sf in skill_files:
        try:
            with open(sf, "r", encoding="utf-8") as f:
                skill = json.load(f)
        except Exception as e:
            print(f"[FAIL] Error reading {sf.name}: {e}")
            validation_failures += 1
            continue

        errors = validate_skill_data(skill, sf)
        if errors:
            print(f"[FAIL] Validation errors in {sf.name}:")
            for err in errors:
                print(f"  - {err}")
            validation_failures += 1
            continue

        sid = skill.get("id")
        sname = skill.get("name")
        if sid:
            registered_ids.add(sid)
        if sname:
            registered_names.add(sname)

        compiled_skills.append(skill)

    # Validate conflicts against registered skills
    c_errors = validate_conflicts(conflicts_data, registered_ids | registered_names)
    if c_errors:
        print("[FAIL] Conflict matrix consistency errors:")
        for err in c_errors:
            print(f"  - {err}")
        validation_failures += 1

    if validation_failures > 0:
        print(f"[ERROR] Build aborted due to {validation_failures} failure(s).")
        return 1

    # Sort skills by sequential index
    compiled_skills.sort(key=lambda s: s.get("index", "999"))

    # Compute statistics
    cat_counts = Counter(s.get("category") for s in compiled_skills)
    type_counts = Counter(s.get("type") for s in compiled_skills)
    lic_counts = Counter(s.get("license") for s in compiled_skills)
    pinned_count = sum(1 for s in compiled_skills if s.get("pinned_commit") is not None)

    # Compute checksum of normalized skills array
    skills_json_str = json.dumps(compiled_skills, sort_keys=True, separators=(',', ':'))
    skills_sha256 = compute_sha256(skills_json_str.encode("utf-8"))

    # Preserve existing generated_at timestamp if catalog exists and checksum matches
    generated_at = None
    if catalog_file.exists():
        try:
            with open(catalog_file, "r", encoding="utf-8") as f_old:
                existing_catalog = json.load(f_old)
                if existing_catalog.get("integrity", {}).get("skills_sha256") == skills_sha256:
                    generated_at = existing_catalog.get("generated_at")
        except Exception:
            pass

    if not generated_at:
        generated_at = datetime.now(timezone.utc).isoformat()

    catalog = {
        "$schema": "../schema/skill.schema.json",
        "version": "1.0.0",
        "generated_at": generated_at,
        "integrity": {
            "skills_sha256": skills_sha256,
            "algorithm": "SHA-256"
        },
        "stats": {
            "total_skills": len(compiled_skills),
            "pinned_skills": pinned_count,
            "categories": dict(cat_counts),
            "types": dict(type_counts),
            "licenses": dict(lic_counts)
        },
        "categories": categories_data.get("categories", []),
        "conflicts": conflicts_data,
        "skills": compiled_skills
    }

    # Write compiled catalog
    with open(catalog_file, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Auto-update README.md metrics and domains table
    update_readme(root, compiled_skills, categories_data)

    print(f"[SUCCESS] Compiled {len(compiled_skills)} skills into {catalog_file}")
    print(f"Checksum: {skills_sha256}")
    print("-" * 60)
    print("STATISTICS:")
    print(f"  Total Skills:   {len(compiled_skills)}")
    print(f"  Pinned Commits: {pinned_count} ({pinned_count*100//len(compiled_skills)}%)")
    print("  By Category:")
    for cat, count in cat_counts.most_common():
        print(f"    - {cat:<14}: {count:>2} skills")
    print("  By Type:")
    for t, count in type_counts.most_common():
        print(f"    - {t:<14}: {count:>2}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    registry_root = os.getcwd() if len(sys.argv) < 2 else sys.argv[1]
    code = build_catalog(registry_root)
    sys.exit(code)
