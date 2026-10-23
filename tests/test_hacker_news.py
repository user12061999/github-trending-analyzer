"""Unit tests for Hacker News trending scraper module."""

import json
import unittest
from unittest.mock import MagicMock, patch

from src.hacker_news import get_hn_trending_repos, parse_hn_story
from src.scraper import TrendingRepo


class TestHackerNews(unittest.TestCase):
    def test_parse_hn_story_valid(self):
        hit = {
            "title": "Show HN: Esp32sim - Run ESP32 firmware in the browser",
            "url": "https://github.com/mikroverk/esp32sim",
            "points": 210,
            "num_comments": 45,
            "objectID": "41234567",
        }
        parsed = parse_hn_story(hit)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["owner"], "mikroverk")
        self.assertEqual(parsed["repo"], "esp32sim")
        self.assertEqual(parsed["name"], "mikroverk/esp32sim")
        self.assertEqual(parsed["points"], 210)
        self.assertEqual(parsed["comments"], 45)
        self.assertIn("item?id=41234567", parsed["hn_url"])

    def test_parse_hn_story_strips_git_suffix(self):
        hit = {
            "title": "A cool tool",
            "url": "https://github.com/owner/cool-tool.git",
            "points": 50,
            "num_comments": 12,
            "objectID": "123",
        }
        parsed = parse_hn_story(hit)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["repo"], "cool-tool")

    def test_parse_hn_story_ignores_non_repo_urls(self):
        invalid_hits = [
            {"url": "https://news.ycombinator.com/item?id=123"},
            {"url": "https://github.com/blog/2338-sha-1"},
            {"url": "https://github.com/pricing"},
            {"url": "https://github.com/features/actions"},
            {"url": ""},
        ]
        for hit in invalid_hits:
            self.assertIsNone(parse_hn_story(hit))

    @patch("src.hacker_news.urllib.request.urlopen")
    def test_get_hn_trending_repos_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_data = {
            "hits": [
                {
                    "title": "Show HN: Project A",
                    "url": "https://github.com/alice/project-a",
                    "points": 150,
                    "num_comments": 30,
                    "objectID": "1",
                },
                {
                    "title": "Duplicate Project A with different query",
                    "url": "https://github.com/alice/project-a",
                    "points": 10,
                    "num_comments": 2,
                    "objectID": "2",
                },
                {
                    "title": "Project B",
                    "url": "https://github.com/bob/project-b",
                    "points": 300,
                    "num_comments": 80,
                    "objectID": "3",
                },
            ]
        }
        mock_response.read.return_value = json.dumps(mock_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repos = get_hn_trending_repos(timeframe="weekly", limit=2)
        self.assertEqual(len(repos), 2)
        # Should be sorted by points descending (Bob's project 300 first, then Alice's 150)
        self.assertEqual(repos[0].name, "bob/project-b")
        self.assertEqual(repos[0].stars_since, "300")
        self.assertEqual(repos[0].timeframe, "hn_weekly")
        self.assertEqual(repos[1].name, "alice/project-a")
        self.assertIsInstance(repos[0], TrendingRepo)

    @patch("src.hacker_news.urllib.request.urlopen")
    def test_get_hn_trending_repos_network_failure(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("Connection timed out")
        repos = get_hn_trending_repos()
        self.assertEqual(repos, [])


if __name__ == "__main__":
    unittest.main()
