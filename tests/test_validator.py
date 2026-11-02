#!/usr/bin/env python3
"""
Unit tests for PINAX Validation Engine.
Run with: python3 -m unittest discover tests
"""

import unittest
import sys
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))
from validator import validate_skill_data, validate_conflicts


class TestSkillValidator(unittest.TestCase):
    def setUp(self):
        self.valid_skill = {
            "id": "sample-skill",
            "index": "999",
            "name": "Sample Agent Skill",
            "repo": "sample-owner/sample-skill",
            "category": "Engineering",
            "type": "Skill",
            "license": "MIT",
            "status": "INSTALL",
            "pinned_commit": "abc1234",
            "description": "A well-crafted, focused AI coding assistant skill for testing purposes.",
            "install": "npx skills add sample-owner/sample-skill"
        }

    def test_valid_skill_passes(self):
        errors = validate_skill_data(self.valid_skill)
        self.assertEqual(len(errors), 0, f"Expected no errors, got: {[str(e) for e in errors]}")

    def test_missing_required_fields_fails_stage_1(self):
        bad_skill = self.valid_skill.copy()
        del bad_skill["repo"]
        errors = validate_skill_data(bad_skill)
        self.assertTrue(any(e.stage == 1 and "repo" in e.message for e in errors))

    def test_invalid_category_fails_stage_1(self):
        bad_skill = self.valid_skill.copy()
        bad_skill["category"] = "Magic"
        errors = validate_skill_data(bad_skill)
        self.assertTrue(any(e.stage == 1 and "category" in e.message for e in errors))

    def test_em_dash_ban_antislop_fails_stage_2(self):
        bad_skill = self.valid_skill.copy()
        bad_skill["description"] = "A powerful tool \u2014 perfect for your agentic workflow."
        errors = validate_skill_data(bad_skill)
        self.assertTrue(any(e.stage == 2 and "em dash" in e.message for e in errors))

    def test_banned_buzzwords_fail_stage_2(self):
        bad_skill = self.valid_skill.copy()
        bad_skill["description"] = "Delve into the codebase and supercharge your workflow today."
        errors = validate_skill_data(bad_skill)
        self.assertTrue(any(e.stage == 2 and "buzzword" in e.message for e in errors))

    def test_invalid_repo_fails_stage_3(self):
        bad_skill = self.valid_skill.copy()
        bad_skill["repo"] = "https://github.com/invalid/repo/format"
        errors = validate_skill_data(bad_skill)
        self.assertTrue(any(e.stage == 3 and "repo format" in e.message for e in errors))

    def test_conflict_matrix_validation(self):
        conflicts = {
            "hard_conflicts": [
                {
                    "skills": ["known-skill-a", "known-skill-b"],
                    "reason": "Test collision"
                }
            ]
        }
        registered = {"known-skill-a", "known-skill-b"}
        errors = validate_conflicts(conflicts, registered)
        self.assertEqual(len(errors), 0)

        # Missing skill reference
        errors_bad = validate_conflicts(conflicts, {"known-skill-a"})
        self.assertEqual(len(errors_bad), 1)


if __name__ == "__main__":
    unittest.main()
