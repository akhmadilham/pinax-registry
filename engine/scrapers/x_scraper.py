#!/usr/bin/env python3
"""
PINAX X / Twitter Signal Scraper
Monitors trending social signals and posts on X discussing new AI agent skills,
extracting GitHub repository links and queueing them for GitHub scraper analysis.
"""

import os
import sys
import json
import re
import argparse
import urllib.request
import urllib.parse
from pathlib import Path

GITHUB_URL_PATTERN = re.compile(r"https?://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")

PINAX_SEARCH_QUERIES = [
    '"npx skills add"',
    '"SKILL.md" (claude OR cursor OR antigravity)',
    '"agent skills" github.com',
    '"claude plugin" github.com',
    '"awesome-agent-skills"'
]


def extract_github_repos_from_text(text):
    matches = GITHUB_URL_PATTERN.findall(text)
    cleaned = []
    for m in matches:
        # Strip trailing punctuation or anchors
        repo = m.rstrip("/").split("#")[0].split("?")[0]
        # Ignore common non-skill repos
        if repo.lower() not in {"github/docs", "torvalds/linux", "facebook/react"}:
            cleaned.append(repo)
    return list(set(cleaned))


def parse_tweet_dump(file_path):
    """
    Parses an offline JSON dump or text export of tweets.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    repos = extract_github_repos_from_text(content)
    return repos


def search_x_api(query, bearer_token, max_results=20):
    """
    Queries X API v2 Recent Search endpoint if a bearer token is provided.
    """
    if not bearer_token:
        print("[!] No X_BEARER_TOKEN provided. Skipping live API call.")
        return []

    encoded_query = urllib.parse.quote(query)
    url = f"https://api.twitter.com/2/tweets/search/recent?query={encoded_query}&tweet.fields=public_metrics,entities,created_at&max_results={max_results}"

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {bearer_token}")
    req.add_header("User-Agent", "PINAX-Agent-SocialWatcher/1.0")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tweets = data.get("data", [])
            found_repos = set()
            for t in tweets:
                text = t.get("text", "")
                for r in extract_github_repos_from_text(text):
                    found_repos.add(r)
            return list(found_repos)
    except Exception as e:
        print(f"[!] X API request failed: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="PINAX X / Twitter Signal Scraper")
    parser.add_argument("--query", help="Custom search query")
    parser.add_argument("--file", help="Parse text or JSON dump file")
    parser.add_argument("--token", default=os.getenv("X_BEARER_TOKEN"), help="X API v2 Bearer Token")
    parser.add_argument("--out", default="staging/social_queue.json", help="Output queue file")
    args = parser.parse_args()

    discovered = set()

    if args.file:
        print(f"[*] Parsing input file: {args.file}")
        repos = parse_tweet_dump(args.file)
        discovered.update(repos)

    elif args.query:
        print(f"[*] Querying X API for: {args.query}")
        repos = search_x_api(args.query, args.token)
        discovered.update(repos)

    else:
        # Default query suggestions
        print("[*] Running standard PINAX social signal scan...")
        for q in PINAX_SEARCH_QUERIES[:2]:
            print(f"  > Query: {q}")
            repos = search_x_api(q, args.token)
            discovered.update(repos)

    print(f"[*] Total unique GitHub repositories discovered from X: {len(discovered)}")
    for r in sorted(list(discovered)):
        print(f"  - {r}")

    out_file = Path(args.out)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": str(Path(__file__).stat().st_mtime),
            "repositories": sorted(list(discovered))
        }, f, indent=2)
    print(f"[SAVED] Social discovery queue saved to {out_file}")


if __name__ == "__main__":
    main()
