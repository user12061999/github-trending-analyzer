"""Unit tests for watchlist and personalization scoring."""

import unittest
from src.watchlist import (
    compute_repo_match_score,
    load_watchlist,
    parse_match_argument,
    merge_watchlists,
)


class TestWatchlist(unittest.TestCase):

    def setUp(self):
        self.watchlist = {
            "keywords": ["agent", "rag", "mcp", "security"],
            "languages": ["Python", "Rust"],
            "categories": ["AI & Machine Learning", "Security & Privacy"],
        }

    def test_compute_match_score_full(self):
        score, matched = compute_repo_match_score(
            name="cool-agent",
            description="A modern multi-agent framework with RAG capabilities",
            language="Python",
            category="AI & Machine Learning",
            extra_text="Built with MCP protocol",
            watchlist=self.watchlist,
        )
        # Should match keywords (agent, rag, mcp), language (Python: 25), category (AI: 25)
        # Keywords: 3 * 15 = 45. Total = 45 + 25 + 25 = 95
        self.assertGreaterEqual(score, 80)
        self.assertIn("agent", matched)
        self.assertIn("rag", matched)
        self.assertIn("Lang:Python", matched)
        self.assertIn("Cat:AI & Machine Learning", matched)

    def test_compute_match_score_none(self):
        score, matched = compute_repo_match_score(
            name="frontend-lib",
            description="CSS utility classes for web styling",
            language="JavaScript",
            category="Web & Frontend",
            watchlist=self.watchlist,
        )
        self.assertEqual(score, 0)
        self.assertEqual(matched, [])

    def test_parse_match_argument(self):
        parsed = parse_match_argument("agent, rust, security")
        self.assertEqual(parsed["keywords"], ["agent", "rust", "security"])

    def test_merge_watchlists(self):
        wl1 = {"keywords": ["agent"], "languages": ["Python"], "categories": []}
        wl2 = {"keywords": ["rag"], "languages": ["Rust"], "categories": ["AI"]}
        merged = merge_watchlists(wl1, wl2)
        self.assertEqual(merged["keywords"], ["agent", "rag"])
        self.assertEqual(merged["languages"], ["Python", "Rust"])
        self.assertEqual(merged["categories"], ["AI"])


if __name__ == "__main__":
    unittest.main()
