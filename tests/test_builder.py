#!/usr/bin/env python3
"""
Unit tests for PINAX Catalog Builder (engine/builder.py).
Tests catalog compilation, SHA-256 integrity checksum, and timestamp idempotency.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

# Add engine directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))
from builder import build_catalog, compute_sha256


class TestCatalogBuilder(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root = Path(self.temp_dir)
        self.data_dir = self.root / "data"
        self.skills_dir = self.data_dir / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)

        # Standard categories
        self.categories_data = {
            "categories": [
                {"id": "Engineering", "name": "Engineering"},
                {"id": "Design", "name": "Design"},
                {"id": "Writing", "name": "Writing"},
                {"id": "Security", "name": "Security"},
                {"id": "Video", "name": "Video"},
                {"id": "Business", "name": "Business"},
                {"id": "Discovery", "name": "Discovery"}
            ]
        }
        with open(self.data_dir / "categories.json", "w", encoding="utf-8") as f:
            json.dump(self.categories_data, f, indent=2)

        # Standard conflicts
        self.conflicts_data = {
            "hard_conflicts": [],
            "soft_conflicts": []
        }
        with open(self.data_dir / "conflicts.json", "w", encoding="utf-8") as f:
            json.dump(self.conflicts_data, f, indent=2)

        # Create two sample valid skills
        self.skill_1 = {
            "id": "skill-alpha",
            "index": "001",
            "name": "Skill Alpha",
            "repo": "owner-a/skill-alpha",
            "category": "Engineering",
            "type": "Skill",
            "license": "MIT",
            "status": "INSTALL",
            "pinned_commit": "abc1234",
            "description": "First test skill providing automated coding assistance.",
            "install": "npx skills add owner-a/skill-alpha"
        }
        self.skill_2 = {
            "id": "skill-beta",
            "index": "002",
            "name": "Skill Beta",
            "repo": "owner-b/skill-beta",
            "category": "Design",
            "type": "Tool",
            "license": "Apache-2.0",
            "status": "INSTALL",
            "pinned_commit": None,
            "description": "Second test skill providing visual styling components.",
            "install": "npx skills add owner-b/skill-beta"
        }

        with open(self.skills_dir / "001_skill_alpha.json", "w", encoding="utf-8") as f:
            json.dump(self.skill_1, f, indent=2)
        with open(self.skills_dir / "002_skill_beta.json", "w", encoding="utf-8") as f:
            json.dump(self.skill_2, f, indent=2)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compute_sha256(self):
        # Known SHA-256 for empty string
        empty_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(compute_sha256(b""), empty_hash)

        # Checksum is deterministic
        test_bytes = b"PINAX Agent Skills Standard"
        self.assertEqual(compute_sha256(test_bytes), compute_sha256(test_bytes))
        self.assertEqual(len(compute_sha256(test_bytes)), 64)

    def test_build_catalog_success(self):
        exit_code = build_catalog(self.root)
        self.assertEqual(exit_code, 0)

        catalog_path = self.data_dir / "catalog.json"
        self.assertTrue(catalog_path.exists())

        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)

        self.assertEqual(catalog.get("version"), "1.0.0")
        self.assertIn("generated_at", catalog)
        self.assertIn("integrity", catalog)
        self.assertEqual(catalog["integrity"]["algorithm"], "SHA-256")
        self.assertEqual(len(catalog["integrity"]["skills_sha256"]), 64)

        # Stats verification
        stats = catalog.get("stats", {})
        self.assertEqual(stats.get("total_skills"), 2)
        self.assertEqual(stats.get("pinned_skills"), 1)
        self.assertEqual(stats.get("categories", {}).get("Engineering"), 1)
        self.assertEqual(stats.get("categories", {}).get("Design"), 1)

        # Skills list verification
        skills = catalog.get("skills", [])
        self.assertEqual(len(skills), 2)
        self.assertEqual(skills[0]["id"], "skill-alpha")
        self.assertEqual(skills[1]["id"], "skill-beta")

    def test_build_catalog_timestamp_idempotency(self):
        # First build
        code_1 = build_catalog(self.root)
        self.assertEqual(code_1, 0)

        catalog_path = self.data_dir / "catalog.json"
        with open(catalog_path, "r", encoding="utf-8") as f:
            cat_1 = json.load(f)

        initial_timestamp = cat_1.get("generated_at")
        initial_checksum = cat_1.get("integrity", {}).get("skills_sha256")
        self.assertIsNotNone(initial_timestamp)

        # Second build without changing skills
        code_2 = build_catalog(self.root)
        self.assertEqual(code_2, 0)

        with open(catalog_path, "r", encoding="utf-8") as f:
            cat_2 = json.load(f)

        second_timestamp = cat_2.get("generated_at")
        second_checksum = cat_2.get("integrity", {}).get("skills_sha256")

        # Checksums and timestamps must be strictly identical (zero diff)
        self.assertEqual(initial_checksum, second_checksum)
        self.assertEqual(initial_timestamp, second_timestamp)

    def test_build_catalog_updates_timestamp_on_skill_change(self):
        # First build
        code_1 = build_catalog(self.root)
        self.assertEqual(code_1, 0)

        catalog_path = self.data_dir / "catalog.json"
        with open(catalog_path, "r", encoding="utf-8") as f:
            cat_1 = json.load(f)
        initial_checksum = cat_1.get("integrity", {}).get("skills_sha256")

        # Modify a skill
        self.skill_1["description"] = "Updated functional scope for automated coding assistance."
        with open(self.skills_dir / "001_skill_alpha.json", "w", encoding="utf-8") as f:
            json.dump(self.skill_1, f, indent=2)

        # Force a distinct timestamp in existing catalog to ensure detection
        cat_1["generated_at"] = "2020-01-01T00:00:00.000000+00:00"
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(cat_1, f, indent=2)

        # Rebuild
        code_2 = build_catalog(self.root)
        self.assertEqual(code_2, 0)

        with open(catalog_path, "r", encoding="utf-8") as f:
            cat_2 = json.load(f)

        new_checksum = cat_2.get("integrity", {}).get("skills_sha256")
        new_timestamp = cat_2.get("generated_at")

        self.assertNotEqual(initial_checksum, new_checksum)
        self.assertNotEqual(new_timestamp, "2020-01-01T00:00:00.000000+00:00")

    def test_missing_manifests_abort_build(self):
        # Missing categories.json
        (self.data_dir / "categories.json").unlink()
        code = build_catalog(self.root)
        self.assertEqual(code, 1)

        # Restore categories, delete conflicts.json
        with open(self.data_dir / "categories.json", "w", encoding="utf-8") as f:
            json.dump(self.categories_data, f)
        (self.data_dir / "conflicts.json").unlink()
        code = build_catalog(self.root)
        self.assertEqual(code, 1)

    def test_invalid_skill_aborts_build(self):
        # Create an invalid skill (missing required repo field)
        invalid_skill = {
            "id": "invalid-skill",
            "index": "003",
            "name": "Invalid Skill",
            "category": "Engineering",
            "type": "Skill",
            "license": "MIT",
            "status": "INSTALL",
            "description": "Skill missing required repository attribute.",
            "install": "npx skills add invalid/repo"
        }
        with open(self.skills_dir / "003_invalid.json", "w", encoding="utf-8") as f:
            json.dump(invalid_skill, f, indent=2)

        code = build_catalog(self.root)
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
