#!/usr/bin/env python3
"""
Unit tests for PINAX Scrapers (engine/scrapers/github_scraper.py and x_scraper.py).
Tests frontmatter markdown parsing and social signal URL extraction without network calls.
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
from scrapers.github_scraper import parse_skill_markdown, inspect_repository
from scrapers.x_scraper import (
    extract_github_repos_from_text,
    parse_tweet_dump,
    search_x_api
)


class TestScrapers(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_skill_markdown_with_yaml_frontmatter(self):
        sample_md = """---
name: "Clean Code Assistant"
description: "High signal AI coding skill for clean refactoring."
license: "Apache-2.0"
category: "Engineering"
---

# Clean Code Assistant

This skill guides coding agents through modular architectural refactoring.
"""
        meta, body = parse_skill_markdown(sample_md)

        self.assertEqual(meta.get("name"), "Clean Code Assistant")
        self.assertEqual(meta.get("description"), "High signal AI coding skill for clean refactoring.")
        self.assertEqual(meta.get("license"), "Apache-2.0")
        self.assertEqual(meta.get("category"), "Engineering")
        self.assertIn("# Clean Code Assistant", body)

    def test_parse_skill_markdown_fallback_to_headline_and_paragraphs(self):
        sample_md = """# Specialized Motion Graphic Engine

A comprehensive programmatic animation suite built on GSAP and HTML5 Canvas.

Features include zero-lag rendering and timeline orchestration.
"""
        meta, body = parse_skill_markdown(sample_md)

        self.assertEqual(meta.get("name"), "Specialized Motion Graphic Engine")
        self.assertEqual(
            meta.get("description"),
            "A comprehensive programmatic animation suite built on GSAP and HTML5 Canvas."
        )

    def test_parse_skill_markdown_empty_or_minimal(self):
        meta, body = parse_skill_markdown("")
        self.assertEqual(meta, {})
        self.assertEqual(body, "")

    def test_extract_github_repos_from_text(self):
        tweet_text = (
            "Discovered amazing agent skills today!\n"
            "Try https://github.com/upstash/context7-mcp and "
            "https://github.com/obra/superpowers.git for Claude Code.\n"
            "Also https://github.com/facebook/react (should be ignored) and "
            "https://github.com/torvalds/linux#readme (should be ignored).\n"
            "Another great repo: https://github.com/akhmadilham/pinax-registry?tab=readme."
        )

        repos = extract_github_repos_from_text(tweet_text)

        # Expected extracted repos: upstash/context7-mcp, obra/superpowers.git, akhmadilham/pinax-registry
        # Filtered out: facebook/react, torvalds/linux
        self.assertIn("upstash/context7-mcp", repos)
        self.assertIn("obra/superpowers.git", repos)
        self.assertIn("akhmadilham/pinax-registry", repos)
        self.assertNotIn("facebook/react", repos)
        self.assertNotIn("torvalds/linux", repos)

    def test_extract_github_repos_no_matches(self):
        text = "Just a general tweet about artificial intelligence and agents without URLs."
        repos = extract_github_repos_from_text(text)
        self.assertEqual(repos, [])

    def test_parse_tweet_dump_from_file(self):
        dump_path = Path(self.temp_dir) / "tweets.txt"
        with open(dump_path, "w", encoding="utf-8") as f:
            f.write("Thread 1: check https://github.com/owner-one/skill-one\n")
            f.write("Thread 2: check https://github.com/owner-two/skill-two/\n")

        extracted = parse_tweet_dump(dump_path)
        self.assertEqual(len(extracted), 2)
        self.assertIn("owner-one/skill-one", extracted)
        self.assertIn("owner-two/skill-two", extracted)

    def test_search_x_api_without_token_skips_network(self):
        # Must return empty list immediately without throwing any exception
        results = search_x_api("test query", bearer_token=None)
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
