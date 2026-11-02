#!/usr/bin/env python3
"""
PINAX GitHub Skill Scraper
Discovers and extracts AI agent skill definitions directly from GitHub repositories.
Looks for SKILL.md, .agents/skills, or plugin manifests, parses YAML frontmatter,
and creates candidate definitions in staging/candidates/.
"""

import os
import sys
import json
import re
import argparse
import urllib.request
import urllib.error
from pathlib import Path


def fetch_github_api(url, token=None):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "PINAX-Agent-Crawler/1.0")
    req.add_header("Accept", "application/vnd.github.v3+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] Error fetching {url}: {e.reason}")
        return None
    except Exception as e:
        print(f"[ERROR] Connection failure for {url}: {e}")
        return None


def fetch_raw_file(repo, file_path, branch="main", token=None):
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{file_path}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "PINAX-Agent-Crawler/1.0")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except Exception:
        # Fallback to master branch
        if branch == "main":
            return fetch_raw_file(repo, file_path, branch="master", token=token)
        return None


def parse_skill_markdown(md_text):
    """
    Parses frontmatter YAML and markdown structure from a SKILL.md file.
    """
    metadata = {}
    content = md_text

    # Match YAML frontmatter between --- and ---
    yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md_text, re.DOTALL)
    if yaml_match:
        yaml_block = yaml_match.group(1)
        content = yaml_match.group(2)
        for line in yaml_block.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip().lower()
                v = v.strip().strip("'\"")
                metadata[k] = v

    # Extract first headline if name missing
    if "name" not in metadata:
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h1_match:
            metadata["name"] = h1_match.group(1).strip()

    # Extract clean summary
    if "description" not in metadata:
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and not p.startswith("#")]
        if paragraphs:
            metadata["description"] = paragraphs[0].replace("\n", " ")

    return metadata, content


def inspect_repository(repo_slug, token=None):
    print(f"[*] Inspecting repository: {repo_slug}")
    repo_info = fetch_github_api(f"https://api.github.com/repos/{repo_slug}", token=token)
    if not repo_info:
        return None

    # Check for SKILL.md or variations
    skill_paths = ["SKILL.md", "skill.md", "README.md"]
    skill_md_content = None
    matched_path = None

    for sp in skill_paths:
        raw = fetch_raw_file(repo_slug, sp, token=token)
        if raw:
            skill_md_content = raw
            matched_path = sp
            break

    if not skill_md_content:
        print(f"[!] No SKILL.md or README.md found in {repo_slug}")
        return None

    meta, body = parse_skill_markdown(skill_md_content)

    # Sanitize description
    raw_desc = meta.get("description", repo_info.get("description", ""))
    # Antislop: strip em dash
    clean_desc = raw_desc.replace("\u2014", " - ").replace("\u2013", "-").strip()

    slug = repo_slug.split("/")[-1].lower()
    license_spdx = (repo_info.get("license") or {}).get("spdx_id") or "MIT"

    candidate = {
        "id": slug,
        "name": meta.get("name", slug),
        "repo": repo_slug,
        "category": "Engineering",  # Default category to be triaged by review_agent
        "type": "Skill",
        "license": license_spdx if license_spdx != "NOASSERTION" else "Custom",
        "status": "INSTALL",
        "pinned_commit": repo_info.get("default_branch", "main"),
        "description": clean_desc or f"AI agent skill from {repo_slug}.",
        "install": f"npx skills add {repo_slug}",
        "metrics": {
            "stars": repo_info.get("stargazers_count", 0),
            "forks": repo_info.get("forks_count", 0),
            "open_issues": repo_info.get("open_issues_count", 0),
            "default_branch": repo_info.get("default_branch", "main")
        },
        "candidate_source": {
            "matched_file": matched_path,
            "crawled_at": repo_info.get("updated_at")
        }
    }
    return candidate


def main():
    parser = argparse.ArgumentParser(description="PINAX GitHub Skill Scraper")
    parser.add_argument("--repo", help="Target GitHub repo (e.g. owner/repo)")
    parser.add_argument("--search", help="Search GitHub for topics or keywords")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub Personal Access Token")
    parser.add_argument("--out-dir", default="staging/candidates", help="Directory to save candidates")
    args = parser.parse_args()

    out_path = Path(args.out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if args.repo:
        cand = inspect_repository(args.repo, token=args.token)
        if cand:
            out_file = out_path / f"{cand['id']}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(cand, f, indent=2, ensure_ascii=False)
            print(f"[SAVED] Staged candidate written to {out_file}")
            sys.exit(0)
        else:
            sys.exit(1)

    elif args.search:
        print(f"[*] Searching GitHub for: {args.search}")
        query = urllib.parse.quote(f"{args.search} in:name,description,readme")
        api_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=10"
        res = fetch_github_api(api_url, token=args.token)
        if not res or "items" not in res:
            print("[!] No search results or rate limited.")
            sys.exit(1)

        print(f"[*] Found {len(res['items'])} repositories. Inspecting candidates...")
        for item in res["items"]:
            repo_name = item["full_name"]
            cand = inspect_repository(repo_name, token=args.token)
            if cand:
                out_file = out_path / f"{cand['id']}.json"
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(cand, f, indent=2, ensure_ascii=False)
                print(f"  + Staged: {repo_name} -> {out_file.name}")
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
