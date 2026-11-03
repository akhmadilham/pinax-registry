#!/usr/bin/env python3
r"""
Independent Adversarial Verification Suite:
PINAX Registry 171 & 121 Audit Schema, Parity, and Antislop R-02 Challenge.

Auditor / Adversarial Verifier: challenger_2_audit
Target Workspace: D:\02 CODE\Web Git Project\pinax-registry
"""

import os
import sys
import json
import re
import unittest
from pathlib import Path

# Paths to artifacts
REGISTRY_ROOT = Path(__file__).resolve().parent.parent

JSON_171_PATH = REGISTRY_ROOT / "audit_171_issues_report.json"
MD_171_PATH = REGISTRY_ROOT / "AUDIT_171_ISSUES_REPORT.md"
JSON_121_PATH = REGISTRY_ROOT / "audit_121_issues_report.json"
MD_121_PATH = REGISTRY_ROOT / "AUDIT_121_ISSUES_REPORT.md"
VERIFY_171_PY = REGISTRY_ROOT / "engine" / "verify_171_audit.py"
VERIFY_121_PY = REGISTRY_ROOT / "engine" / "verify_121_audit.py"

SCRATCH_DIR = Path(r"C:\Users\Akhmad Ilham\.gemini\antigravity\brain\67235fde-28d9-445b-9bb3-fce57e1fc57c\scratch")
SCRATCH_PARSED_171 = SCRATCH_DIR / "parsed_171_issues.json"
SCRATCH_ACCESS_171 = SCRATCH_DIR / "repo_accessibility_171.json"


class TestAntislopR02Strict(unittest.TestCase):
    """
    Antislop Rule R-02 Audit:
    Scans all files in pinax-registry created or modified during the audit using
    explicit UTF-8 encoding to guarantee zero em dashes (\\u2014), &mdash;, or &#8212;.
    Also verifies zero non-ASCII dash characters (\\u2013, \\u2015, \\u2212).
    """

    TARGET_FILES = [
        MD_171_PATH,
        MD_121_PATH,
        JSON_171_PATH,
        JSON_121_PATH,
        VERIFY_171_PY,
        VERIFY_121_PY,
    ]

    def test_all_target_files_exist(self):
        for fpath in self.TARGET_FILES:
            self.assertTrue(fpath.exists(), f"Target file must exist: {fpath}")

    def test_zero_em_dashes_in_all_target_files(self):
        em_dash_violations = {}
        for fpath in self.TARGET_FILES:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            u2014_count = content.count("\u2014")
            mdash_count = content.count("&mdash;")
            numeric_count = content.count("&#8212;")
            total_count = u2014_count + mdash_count + numeric_count

            if total_count > 0:
                em_dash_violations[fpath.name] = {
                    "\\u2014": u2014_count,
                    "&mdash;": mdash_count,
                    "&#8212;": numeric_count,
                    "total": total_count,
                }

        self.assertEqual(
            em_dash_violations,
            {},
            f"Antislop R-02 violation! Found em dashes in files: {em_dash_violations}"
        )

    def test_zero_other_non_ascii_dashes_in_all_target_files(self):
        other_dashes = {
            "\\u2013 (en dash)": "\u2013",
            "\\u2015 (horizontal bar)": "\u2015",
            "\\u2212 (minus sign)": "\u2212",
        }
        violations = {}
        for fpath in self.TARGET_FILES:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            for dname, ch in other_dashes.items():
                cnt = content.count(ch)
                if cnt > 0:
                    violations.setdefault(fpath.name, {})[dname] = cnt

        self.assertEqual(
            violations,
            {},
            f"Found non-ASCII dash characters in files: {violations}"
        )


class TestAuditParity171(unittest.TestCase):
    """
    1:1 Cross-Deliverable Parity Challenge:
    Verifies that every single issue in audit_171_issues_report.json matches
    the corresponding row in AUDIT_171_ISSUES_REPORT.md across issue number,
    skill name, classification, category, type, license, and security status.
    """

    @classmethod
    def setUpClass(cls):
        with open(JSON_171_PATH, "r", encoding="utf-8") as f:
            cls.json_data = json.load(f)
        with open(MD_171_PATH, "r", encoding="utf-8") as f:
            cls.md_content = f.read()

        cls.issues = cls.json_data.get("issues", [])
        cls.issue_map = {x["issue_number"]: x for x in cls.issues}

    def test_json_structure_and_counts(self):
        self.assertEqual(len(self.issues), 171, "Expected exactly 171 issues in JSON")
        issue_nums = [x["issue_number"] for x in self.issues]
        self.assertEqual(min(issue_nums), 99, "Minimum issue number must be 99")
        self.assertEqual(max(issue_nums), 269, "Maximum issue number must be 269")
        self.assertEqual(len(set(issue_nums)), 171, "Issue numbers must be unique")

    def test_master_assessment_table_row_count(self):
        self.assertIn("## 6. Master Assessment Index", self.md_content)
        sec6 = self.md_content.split("## 6. Master Assessment Index")[1]
        rows = [line.strip() for line in sec6.splitlines() if line.strip().startswith("| #")]
        self.assertEqual(len(rows), 171, f"Expected 171 table rows in Section 6, found {len(rows)}")

    def test_master_table_1_to_1_parity(self):
        sec6 = self.md_content.split("## 6. Master Assessment Index")[1]
        rows = [line.strip() for line in sec6.splitlines() if line.strip().startswith("| #")]

        mismatches = []
        for line in rows:
            # Table format: | Issue # | Skill Name | Category | Type | Verdict | License | Security | Guardrails / Operational Notes |
            cells = [c.strip() for c in line.split("|")[1:-1]]
            self.assertGreaterEqual(len(cells), 8, f"Row has fewer than 8 columns: {line}")

            issue_str = cells[0]
            issue_num = int(issue_str.replace("#", ""))
            skill_name = cells[1].replace("`", "").strip()
            category = cells[2].strip()
            item_type = cells[3].strip()
            verdict = cells[4].replace("*", "").strip()
            license_str = cells[5].strip()
            security_str = cells[6].strip()

            j_item = self.issue_map.get(issue_num)
            if not j_item:
                mismatches.append(f"Issue #{issue_num} from MD table not found in JSON")
                continue

            # Compare issue_number
            if j_item["issue_number"] != issue_num:
                mismatches.append(f"Issue #{issue_num}: number mismatch")
            # Compare skill_name
            if j_item["skill_name"] != skill_name:
                mismatches.append(f"Issue #{issue_num}: skill_name mismatch (MD: '{skill_name}', JSON: '{j_item['skill_name']}')")
            # Compare category
            if j_item["category"] != category:
                mismatches.append(f"Issue #{issue_num}: category mismatch (MD: '{category}', JSON: '{j_item['category']}')")
            # Compare type
            if j_item["type"] != item_type:
                mismatches.append(f"Issue #{issue_num}: type mismatch (MD: '{item_type}', JSON: '{j_item['type']}')")
            # Compare classification / verdict
            if j_item["classification"] != verdict:
                mismatches.append(f"Issue #{issue_num}: verdict mismatch (MD: '{verdict}', JSON: '{j_item['classification']}')")

            # Check license correspondence (exact match with license_check.license_type)
            lc = j_item.get("license_check", {})
            expected_license = lc.get("license_type") or "Missing"
            self.assertEqual(
                license_str,
                expected_license,
                f"Issue #{issue_num} license mismatch: MD '{license_str}' vs JSON '{expected_license}'"
            )

            # Check security correspondence
            sc = j_item.get("security_check", {})
            if sc.get("passed"):
                self.assertEqual(security_str, "Clean", f"Issue #{issue_num} clean security mismatch in MD: '{security_str}'")
            else:
                self.assertNotEqual(security_str, "Clean", f"Issue #{issue_num} security failed but MD marked 'Clean'")

        self.assertEqual(mismatches, [], f"Found {len(mismatches)} 1:1 parity mismatches between MD and JSON:\n" + "\n".join(mismatches))

    def test_reject_section_parity(self):
        # Section 3: REJECT Classification Findings (6 Issues)
        self.assertIn("## 3. REJECT Classification Findings", self.md_content)
        sec3 = self.md_content.split("## 3. REJECT Classification Findings")[1].split("## 4.")[0]
        rows = [line.strip() for line in sec3.splitlines() if line.strip().startswith("| #")]
        self.assertEqual(len(rows), 6, f"Expected 6 REJECT rows in Section 3, found {len(rows)}")

        reject_nums = []
        for line in rows:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            issue_num = int(cells[0].replace("#", ""))
            reject_nums.append(issue_num)

        json_reject_nums = [x["issue_number"] for x in self.issues if x["classification"] == "REJECT"]
        self.assertEqual(sorted(reject_nums), sorted(json_reject_nums), "REJECT issue numbers must match exactly between MD Section 3 and JSON")
        self.assertEqual(sorted(reject_nums), [119, 133, 137, 142, 159, 260])

    def test_pass_section_parity(self):
        # Section 5: PASS Clean Candidate Registry (17 Issues)
        self.assertIn("## 5. PASS Clean Candidate Registry", self.md_content)
        sec5 = self.md_content.split("## 5. PASS Clean Candidate Registry")[1].split("## 6.")[0]
        rows = [line.strip() for line in sec5.splitlines() if line.strip().startswith("| #")]
        self.assertEqual(len(rows), 17, f"Expected 17 PASS rows in Section 5, found {len(rows)}")

        pass_nums = []
        for line in rows:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            issue_num = int(cells[0].replace("#", ""))
            pass_nums.append(issue_num)

        json_pass_nums = [x["issue_number"] for x in self.issues if x["classification"] == "PASS"]
        self.assertEqual(sorted(pass_nums), sorted(json_pass_nums), "PASS issue numbers must match exactly between MD Section 5 and JSON")

    def test_summary_metrics_match(self):
        summary = self.json_data.get("summary", {})
        self.assertEqual(summary.get("total_assessed"), 171)
        self.assertEqual(summary.get("unassessed_count"), 0)
        self.assertEqual(summary.get("classifications", {}).get("PASS"), 17)
        self.assertEqual(summary.get("classifications", {}).get("CAUTION"), 148)
        self.assertEqual(summary.get("classifications", {}).get("REJECT"), 6)


class TestBackwardCompatibility121(unittest.TestCase):
    """
    Backward Compatibility Challenge:
    Verifies that audit_121_issues_report.json and AUDIT_121_ISSUES_REPORT.md
    accurately cover the dataset without corruption and that legacy entrypoints work.
    """

    @classmethod
    def setUpClass(cls):
        with open(JSON_121_PATH, "r", encoding="utf-8") as f:
            cls.json_121 = json.load(f)
        with open(MD_121_PATH, "r", encoding="utf-8") as f:
            cls.md_121 = f.read()

        cls.issues_121 = cls.json_121.get("issues", [])
        cls.map_121 = {x["issue_number"]: x for x in cls.issues_121}

    def test_121_json_covers_original_range(self):
        # Original request required issues #99 through #219 (121 issues)
        original_range = set(range(99, 220))
        present_keys = set(self.map_121.keys())
        missing_from_original = original_range - present_keys
        self.assertEqual(missing_from_original, set(), f"audit_121_issues_report.json missing original issues: {missing_from_original}")

    def test_121_json_issues_integrity(self):
        # Check integrity of all original 121 issues (#99 to #219)
        for num in range(99, 220):
            item = self.map_121[num]
            self.assertIn("issue_number", item)
            self.assertIn("skill_name", item)
            self.assertIn("repo_url", item)
            self.assertIn("category", item)
            self.assertIn("type", item)
            self.assertIn("classification", item)
            self.assertIn(item["classification"], {"PASS", "CAUTION", "REJECT"})
            self.assertIn("license_check", item)
            self.assertIn("security_check", item)
            self.assertIn("conflict_check", item)
            self.assertIn("guardrails", item)
            self.assertTrue(len(item["skill_name"]) > 0, f"Skill name empty in #{num}")
            self.assertTrue(item["repo_url"].startswith("https://github.com/"), f"Invalid repo url in #{num}")

    def test_121_json_and_md_not_corrupted(self):
        self.assertGreater(len(self.issues_121), 120)
        self.assertGreater(len(self.md_121), 10000)
        self.assertIn("## 6. Master Assessment Index", self.md_121)

    def test_verify_121_audit_py_delegation(self):
        with open(VERIFY_121_PY, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("from verify_171_audit import main", content)


class TestScratchDataParity(unittest.TestCase):
    """
    Ground-Truth Parity against Scratch Files:
    Cross-checks the audit report against parsed scratch data and git accessibility results.
    """

    def test_scratch_parsed_issues_all_accounted_for(self):
        if not SCRATCH_PARSED_171.exists():
            self.skipTest(f"Scratch file not found: {SCRATCH_PARSED_171}")

        with open(SCRATCH_PARSED_171, "r", encoding="utf-8") as f:
            scratch_issues = json.load(f)

        with open(JSON_171_PATH, "r", encoding="utf-8") as f:
            audit_data = json.load(f)

        audit_map = {x["issue_number"]: x for x in audit_data["issues"]}

        self.assertEqual(len(scratch_issues), 171)
        for s in scratch_issues:
            num = s.get("number") or s.get("issue_number")
            self.assertIn(num, audit_map, f"Scratch issue #{num} missing from audit report")
            a_item = audit_map[num]
            s_url = s.get("repo_url") or s.get("repository_url")
            if s_url:
                self.assertEqual(
                    a_item["repo_url"].lower().rstrip("/"),
                    s_url.lower().rstrip("/"),
                    f"Repo URL mismatch for issue #{num}"
                )


class TestSchemaAndFieldValidation(unittest.TestCase):
    """
    Schema completeness and validity checks on JSON reports.
    """

    def test_schema_keys(self):
        with open(JSON_171_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_top = ["$schema", "audit_metadata", "summary", "issues"]
        for k in required_top:
            self.assertIn(k, data, f"Missing top-level key: {k}")

        meta = data["audit_metadata"]
        self.assertEqual(meta["target_repository"], "https://github.com/akhmadilham/pinax-registry")
        self.assertEqual(meta["issue_range"]["start"], 99)
        self.assertEqual(meta["issue_range"]["end"], 269)
        self.assertEqual(meta["issue_range"]["total_issues"], 171)

        for iss in data["issues"]:
            num = iss["issue_number"]
            self.assertTrue(99 <= num <= 269, f"Issue number {num} out of bounds")
            self.assertIn(iss["classification"], ["PASS", "CAUTION", "REJECT"])
            self.assertIsInstance(iss["guardrails"], dict)
            self.assertIsInstance(iss["license_check"], dict)
            self.assertIsInstance(iss["security_check"], dict)
            self.assertIsInstance(iss["conflict_check"], dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)
