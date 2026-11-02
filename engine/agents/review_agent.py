#!/usr/bin/env python3
"""
PINAX Autonomous Review Agent
Evaluates candidate skills discovered by scrapers or submitted via PR.
Applies automated quality scoring, safety auditing, taxonomy classification,
and conflict detection.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path

# Category keyword heuristics
CATEGORY_KEYWORDS = {
    "Design": ["design", "ui", "ux", "visual", "figma", "typography", "layout", "color", "styling", "css"],
    "Writing": ["writing", "copy", "prose", "grammar", "slop", "editorial", "article", "documentation"],
    "Engineering": ["code", "refactor", "git", "test", "debug", "architecture", "api", "backend", "frontend", "typescript", "python"],
    "Security": ["security", "vulnerability", "audit", "scanner", "cve", "auth", "secret", "guard", "snyk"],
    "Video": ["video", "motion", "remotion", "ffmpeg", "render", "animation", "audio", "sfx", "shot"],
    "Business": ["business", "stripe", "payment", "founder", "saas", "client", "sales", "crm", "invoice"],
    "Discovery": ["discovery", "awesome", "index", "catalog", "directory", "curated", "collection"]
}

# Dangerous patterns in prompt or install instructions
MALICIOUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r":\(\)\{\s*:\|:&\s*\};:",
    r"curl\s+.*\|\s*(?:bash|sh)",
    r"wget\s+.*\|\s*(?:bash|sh)",
    r"cat\s+~/\.ssh",
    r"cat\s+~/\.aws",
    r"env\s*\|\s*curl",
    r"eval\s*\(base64"
]


class SkillReviewer:
    def __init__(self, registry_root):
        self.root = Path(registry_root).resolve()
        self.skills_dir = self.root / "data" / "skills"
        self.catalog_file = self.root / "data" / "catalog.json"
        self.existing_skills = self._load_existing_skills()

    def _load_existing_skills(self):
        skills = []
        for sf in self.skills_dir.glob("*.json"):
            try:
                with open(sf, "r", encoding="utf-8") as f:
                    skills.append(json.load(f))
            except Exception:
                pass
        return skills

    def audit_security(self, candidate):
        issues = []
        text_corpus = (
            candidate.get("name", "") + " " +
            candidate.get("description", "") + " " +
            candidate.get("install", "")
        )
        for pattern in MALICIOUS_PATTERNS:
            if re.search(pattern, text_corpus, re.IGNORECASE):
                issues.append(f"Security hazard detected matching pattern: '{pattern}'")
        return issues

    def classify_category(self, candidate):
        current_cat = candidate.get("category")
        corpus = (candidate.get("name", "") + " " + candidate.get("description", "")).lower()

        scores = {}
        for cat, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in corpus)
            scores[cat] = score

        best_cat = max(scores, key=scores.get)
        if scores[best_cat] > 0:
            return best_cat, scores
        return current_cat or "Engineering", scores

    def detect_conflicts(self, candidate):
        warnings = []
        c_repo = candidate.get("repo", "").lower()
        c_name = candidate.get("name", "").lower()

        for ex in self.existing_skills:
            ex_repo = ex.get("repo", "").lower()
            ex_name = ex.get("name", "").lower()

            if c_repo == ex_repo:
                warnings.append(f"Exact duplicate repository already registered: '{ex.get('id')}' ({ex.get('name')})")
            elif c_name == ex_name:
                warnings.append(f"Exact name match already registered: '{ex.get('id')}'")
            elif candidate.get("category") == ex.get("category") and c_name in ex_name:
                warnings.append(f"Potential semantic overlap with existing skill: '{ex.get('id')}'")

        return warnings

    def evaluate(self, candidate):
        report = {
            "candidate_id": candidate.get("id"),
            "candidate_repo": candidate.get("repo"),
            "score": 100,
            "verdict": "ACCEPT",
            "security_passed": True,
            "category_assigned": candidate.get("category"),
            "checks": {},
            "recommendations": []
        }

        # 1. Security Check
        sec_issues = self.audit_security(candidate)
        if sec_issues:
            report["score"] -= 70
            report["security_passed"] = False
            report["checks"]["security"] = {"passed": False, "issues": sec_issues}
            report["verdict"] = "REJECT"
            return report
        else:
            report["checks"]["security"] = {"passed": True}

        # 2. Antislop R-02 Check
        desc = candidate.get("description", "")
        if "\u2014" in desc or "\u2014" in candidate.get("name", ""):
            report["score"] -= 15
            report["recommendations"].append("Remove em dash (\u2014) from text to comply with Antislop R-02.")
            candidate["description"] = desc.replace("\u2014", " - ")

        if len(desc) < 20:
            report["score"] -= 10
            report["recommendations"].append("Expand description to provide functional scope and usage tips.")

        # 3. Category Validation
        best_cat, cat_scores = self.classify_category(candidate)
        if best_cat != candidate.get("category"):
            report["recommendations"].append(f"Suggested category reclassification: '{candidate.get('category')}' -> '{best_cat}'.")
            report["category_assigned"] = best_cat

        # 4. Overlap & Conflict Check
        conflicts = self.detect_conflicts(candidate)
        if conflicts:
            report["score"] -= 20
            report["checks"]["conflicts"] = conflicts
            report["recommendations"].extend(conflicts)
            if any("Exact duplicate" in c for c in conflicts):
                report["verdict"] = "REJECT"
                return report

        # Final Verdict Determination
        if report["score"] >= 85 and report["verdict"] != "REJECT":
            report["verdict"] = "ACCEPT"
        elif report["score"] >= 60:
            report["verdict"] = "NEEDS_HUMAN_REVIEW"
        else:
            report["verdict"] = "REJECT"

        return report

    def get_next_index(self):
        max_idx = 0
        for s in self.existing_skills:
            try:
                idx = int(s.get("index", 0))
                if idx > max_idx:
                    max_idx = idx
            except ValueError:
                pass
        return f"{max_idx + 1:03d}"

    def stage_for_acceptance(self, candidate, report):
        next_idx = self.get_next_index()
        clean_id = candidate.get("id").lower().replace("/", "-")
        candidate["index"] = next_idx
        candidate["category"] = report["category_assigned"]

        # Ensure minimal required fields
        if not candidate.get("license"):
            candidate["license"] = "MIT"
        if not candidate.get("status"):
            candidate["status"] = "INSTALL"

        # Sanitize text
        candidate["description"] = candidate.get("description", "").replace("\u2014", " - ")

        # Remove ephemeral scraper fields not allowed by schema (additionalProperties: false)
        candidate.pop("metrics", None)
        candidate.pop("candidate_source", None)

        target_file = self.skills_dir / f"{next_idx}_{clean_id.replace('-', '_')}.json"
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(candidate, f, indent=2, ensure_ascii=False)
            f.write("\n")

        return target_file


def main():
    parser = argparse.ArgumentParser(description="PINAX Autonomous Review Agent")
    parser.add_argument("--candidate", required=True, help="Path to staged candidate JSON file")
    parser.add_argument("--root", default=os.getcwd(), help="Root directory of pinax-registry")
    parser.add_argument("--auto-accept", action="store_true", help="Auto-commit to data/skills if verdict is ACCEPT")
    args = parser.parse_args()

    candidate_file = Path(args.candidate)
    if not candidate_file.exists():
        print(f"[ERROR] Candidate file not found: {candidate_file}")
        sys.exit(1)

    with open(candidate_file, "r", encoding="utf-8") as f:
        candidate_data = json.load(f)

    reviewer = SkillReviewer(args.root)
    report = reviewer.evaluate(candidate_data)

    print("=" * 60)
    print("PINAX AUTONOMOUS REVIEW REPORT")
    print(f"Candidate: {candidate_data.get('name')} ({candidate_data.get('repo')})")
    print(f"Score:     {report['score']} / 100")
    print(f"Verdict:   {report['verdict']}")
    print(f"Category:  {report['category_assigned']}")
    print("=" * 60)

    if report["recommendations"]:
        print("Findings & Recommendations:")
        for r in report["recommendations"]:
            print(f"  * {r}")
        print("-" * 60)

    if report["verdict"] == "ACCEPT" and args.auto_accept:
        saved_path = reviewer.stage_for_acceptance(candidate_data, report)
        print(f"[COMMITTED] Skill staged into canonical registry: {saved_path}")

    # Output machine-readable JSON if requested
    out_report = candidate_file.parent / f"{candidate_file.stem}_review.json"
    with open(out_report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[REPORT] Saved review report to {out_report}")

    sys.exit(0 if report["verdict"] in ("ACCEPT", "NEEDS_HUMAN_REVIEW") else 1)


if __name__ == "__main__":
    main()
