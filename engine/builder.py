#!/usr/bin/env python3
"""
PINAX Skills Catalog Builder
Compiles modular data/skills/*.json, data/categories.json, and data/conflicts.json
into the canonical distribution manifest data/catalog.json.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

# Ensure engine path is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validator import validate_skill_data, validate_conflicts


def compute_sha256(content_bytes):
    return hashlib.sha256(content_bytes).hexdigest()


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
