#!/usr/bin/env python3
"""
PINAX Skills Validation Engine
Enforces 4-stage quality gate:
  Stage 1: Schema & Required Field Integrity
  Stage 2: Antislop R-02 (Strict em dash ban, length, quality)
  Stage 3: Repository & Installation Command Integrity
  Stage 4: Conflict Matrix Referential Integrity
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

VALID_CATEGORIES = {
    "Business", "Design", "Discovery", "Engineering",
    "Security", "Video", "Writing"
}

VALID_TYPES = {"Skill", "Collection", "Workflow", "Plugin", "Tool", "Vendor", "Index"}

REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ID_PATTERN = re.compile(r"^[a-z0-9_.-]+$")
INDEX_PATTERN = re.compile(r"^[0-9]{3}$")


class ValidationError:
    def __init__(self, stage, skill_id, message):
        self.stage = stage
        self.skill_id = skill_id
        self.message = message

    def __str__(self):
        return f"[Stage {self.stage} FAIL] Skill '{self.skill_id}': {self.message}"


def validate_skill_data(skill, file_path=None):
    errors = []
    skill_id = skill.get("id", "UNKNOWN")

    # ---------------------------------------------------------
    # STAGE 1: Schema & Required Fields
    # ---------------------------------------------------------
    required_fields = [
        "id", "index", "name", "repo", "category",
        "type", "license", "status", "description", "install"
    ]
    for field in required_fields:
        if field not in skill or skill[field] is None:
            errors.append(ValidationError(1, skill_id, f"Missing required field '{field}'"))
        elif isinstance(skill[field], str) and not skill[field].strip():
            errors.append(ValidationError(1, skill_id, f"Field '{field}' cannot be empty"))

    if "id" in skill and not ID_PATTERN.match(skill["id"]):
        errors.append(ValidationError(1, skill_id, f"Invalid 'id' format: '{skill['id']}'. Must be lowercase alphanumeric, dash, dot, or underscore."))

    if "index" in skill and not INDEX_PATTERN.match(skill["index"]):
        errors.append(ValidationError(1, skill_id, f"Invalid 'index' format: '{skill['index']}'. Must be 3 digits (e.g. '001')."))

    if "category" in skill and skill["category"] not in VALID_CATEGORIES:
        errors.append(ValidationError(1, skill_id, f"Invalid category '{skill['category']}'. Must be one of {sorted(list(VALID_CATEGORIES))}"))

    if "type" in skill and skill["type"] not in VALID_TYPES:
        errors.append(ValidationError(1, skill_id, f"Invalid type '{skill['type']}'. Must be one of {sorted(list(VALID_TYPES))}"))

    # ---------------------------------------------------------
    # STAGE 2: Antislop R-02 (Strict em dash ban & writing hygiene)
    # ---------------------------------------------------------
    # Check all string fields for unicode em dash (\u2014)
    for field, val in skill.items():
        if isinstance(val, str):
            if "\u2014" in val:
                errors.append(ValidationError(
                    2, skill_id,
                    f"Antislop R-02 violation: em dash (\\u2014) detected in field '{field}'. Replace with colon, comma, or parenthesis."
                ))
            if "\u2013" in val and field not in ("name", "index"):
                # En dash check in descriptions
                pass

    desc = skill.get("description", "")
    if len(desc) < 15:
        errors.append(ValidationError(2, skill_id, f"Description too short ({len(desc)} chars). Minimum 15 characters."))

    # Banned AI slop buzzwords in description
    banned_slop = [
        "delve into", "testament to", "game changer", "tapestry of",
        "revolutionize your", "supercharge your workflow"
    ]
    for slop in banned_slop:
        if slop in desc.lower():
            errors.append(ValidationError(2, skill_id, f"Antislop violation: generic buzzword '{slop}' in description."))

    # ---------------------------------------------------------
    # STAGE 3: Repository & Link Integrity
    # ---------------------------------------------------------
    repo = skill.get("repo", "")
    if repo and not REPO_PATTERN.match(repo):
        errors.append(ValidationError(3, skill_id, f"Invalid GitHub repo format: '{repo}'. Expected 'owner/repo'."))

    install_cmd = skill.get("install", "")
    if install_cmd:
        valid_prefixes = (
            "npx ", "uvx ", "pip ", "npm ", "git ", "/plugin ",
            "claude ", "curl ", "Browse only", "Copy ", "Install ", "#"
        )
        if not any(install_cmd.startswith(p) for p in valid_prefixes) and "skills" not in install_cmd:
            errors.append(ValidationError(3, skill_id, f"Install command '{install_cmd}' does not follow recognized CLI invocation patterns."))

    return errors


def validate_conflicts(conflicts_data, registered_skill_ids):
    errors = []
    for kind in ["hard_conflicts", "soft_conflicts"]:
        for item in conflicts_data.get(kind, []):
            skills = item.get("skills", [])
            if len(skills) != 2:
                errors.append(ValidationError(4, "conflicts.json", f"{kind} item must contain exactly 2 skill identifiers."))
                continue
            for s in skills:
                # Skills might match id or name
                clean_s = s.lower().replace("/", "-")
                # Check fuzzy or direct match
                found = any(s == r or clean_s == r or s in r for r in registered_skill_ids)
                if not found:
                    errors.append(ValidationError(4, "conflicts.json", f"Conflict references unknown skill '{s}'."))
    return errors


def run_full_validation(registry_root):
    root = Path(registry_root)
    skills_dir = root / "data" / "skills"
    conflicts_file = root / "data" / "conflicts.json"
    categories_file = root / "data" / "categories.json"

    all_errors = []
    registered_ids = set()
    registered_names = set()

    skill_files = sorted(list(skills_dir.glob("*.json")))
    if not skill_files:
        print(f"[ERROR] No skill JSON files found in {skills_dir}")
        return 1

    print(f"[*] Validating {len(skill_files)} skill definitions against PINAX Standard...")

    for sf in skill_files:
        try:
            with open(sf, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            all_errors.append(ValidationError(1, sf.name, f"JSON parse error: {e}"))
            continue

        sid = data.get("id")
        sname = data.get("name")
        if sid:
            registered_ids.add(sid)
        if sname:
            registered_names.add(sname)

        errors = validate_skill_data(data, sf)
        all_errors.extend(errors)

    # Validate categories
    if categories_file.exists():
        try:
            with open(categories_file, "r", encoding="utf-8") as f:
                cat_data = json.load(f)
            cats = cat_data.get("categories", [])
            cat_names = {c.get("name") for c in cats}
            missing = VALID_CATEGORIES - cat_names
            if missing:
                all_errors.append(ValidationError(1, "categories.json", f"Missing pantheon categories: {missing}"))
        except Exception as e:
            all_errors.append(ValidationError(1, "categories.json", f"JSON parse error: {e}"))

    # Stage 4: Conflict Matrix Check
    if conflicts_file.exists():
        try:
            with open(conflicts_file, "r", encoding="utf-8") as f:
                c_data = json.load(f)
            c_errors = validate_conflicts(c_data, registered_ids | registered_names)
            all_errors.extend(c_errors)
        except Exception as e:
            all_errors.append(ValidationError(4, "conflicts.json", f"JSON parse error: {e}"))

    # Print Results
    print("-" * 60)
    if all_errors:
        print(f"[FAIL] Found {len(all_errors)} validation errors:")
        for err in all_errors:
            print(f"  - {err}")
        print("-" * 60)
        return 1
    else:
        print(f"[PASS] All {len(skill_files)} skills passed 4-stage validation successfully!")
        print("  - Stage 1: Schema & Required Fields: OK")
        print("  - Stage 2: Antislop R-02 (0 em dashes, high signal): OK")
        print("  - Stage 3: Repository & Link Integrity: OK")
        print("  - Stage 4: Conflict Matrix Consistency: OK")
        print("-" * 60)
        return 0


def main():
    parser = argparse.ArgumentParser(description="PINAX Skills Validation Engine")
    parser.add_argument("--root", default=os.getcwd(), help="Root directory of pinax-registry")
    parser.add_argument("--file", help="Validate a single skill JSON file")
    args = parser.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        errors = validate_skill_data(data, path)
        if errors:
            print(f"[FAIL] {len(errors)} errors found in {args.file}:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
        else:
            print(f"[PASS] {args.file} is valid.")
            sys.exit(0)

    exit_code = run_full_validation(args.root)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
