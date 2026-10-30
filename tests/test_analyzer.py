"""Unit tests for Analyzer Engine."""

import unittest
import json
from unittest.mock import patch, MagicMock
from src.analyzer import (
    analyze_repo_heuristic,
    analyze_repository,
    detect_category,
    extract_features_from_markdown,
    generate_architecture_mermaid,
)
from src.fetcher import extract_release_highlights, fetch_repo_release, calculate_pulse_status, fetch_repo_community_pulse
from src.scraper import TrendingRepo

SAMPLE_README = """
# Awesome AI Agent Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source autonomous agent framework designed for orchestrating multi-agent systems and LLMs with ease.

## Key Features

- Autonomous multi-agent coordination with specialized roles
- Built-in RAG integration with vector databases like Chroma and Pinecone
- Support for OpenAI, Claude, and local Ollama models
- Low-latency streaming responses with WebSocket support

## Getting Started

Run `pip install awesome-agent` to begin.
"""


class TestAnalyzerEngine(unittest.TestCase):

    def test_detect_category(self):
        cat1 = detect_category("Autonomous LLM agent and prompt chaining framework", "Python")
        self.assertEqual(cat1, "AI & Machine Learning")

        cat2 = detect_category("Blazingly fast terminal file manager and shell navigation", "Rust")
        self.assertEqual(cat2, "Developer Tooling & CLI")

        cat3 = detect_category("Next-generation Kubernetes cluster monitoring and deploy", "Go")
        self.assertEqual(cat3, "DevOps & Infrastructure")

    def test_extract_features_from_markdown(self):
        features = extract_features_from_markdown(SAMPLE_README)
        self.assertTrue(len(features) >= 3)
        self.assertTrue(any("Autonomous multi-agent coordination" in f for f in features))
        self.assertTrue(any("Built-in RAG integration" in f for f in features))

    def test_analyze_repo_heuristic(self):
        repo = TrendingRepo(
            name="cool-team/agent-orchestrator",
            owner="cool-team",
            repo="agent-orchestrator",
            url="https://github.com/cool-team/agent-orchestrator",
            description="Autonomous multi-agent orchestration framework for LLMs",
            language="Python",
            language_color="#3572A5",
            stars_total="5200",
            forks_total="450",
            stars_since="620",
            timeframe="daily",
        )

        analysis = analyze_repo_heuristic(repo, readme_raw=SAMPLE_README)
        self.assertEqual(analysis.category, "AI & Machine Learning")
        self.assertIn("agent", analysis.core_purpose.lower())
        self.assertTrue(len(analysis.key_features) >= 2)
        self.assertTrue(len(analysis.target_audience) > 0)
        self.assertTrue(len(analysis.use_cases) > 0)
        self.assertEqual(analysis.engine_used, "heuristic")

    def test_generate_architecture_mermaid_flows(self):
        # 1. RAG flow
        rag_m = generate_architecture_mermaid("org/rag-app", category="AI & Machine Learning", description="Advanced RAG vector retrieval")
        self.assertTrue(rag_m.startswith("flowchart TD"))
        self.assertIn("VectorDB", rag_m)
        self.assertIn("Retriever", rag_m)

        # 2. Multi-agent flow
        agent_m = generate_architecture_mermaid("org/agentic", category="AI & Machine Learning", description="Multi-agent orchestration system")
        self.assertTrue(agent_m.startswith("flowchart TD"))
        self.assertIn("Planner", agent_m)
        self.assertIn("ToolExec", agent_m)

        # 3. Compiler / AST Tooling flow
        ast_m = generate_architecture_mermaid("org/oxlint", category="Developer Tooling & CLI", description="Linter with AST parser")
        self.assertTrue(ast_m.startswith("flowchart LR"))
        self.assertIn("ASTParser", ast_m)

        # 4. CLI Tool flow
        cli_m = generate_architecture_mermaid("org/fast-cli", repo_type="tool_app", description="Fast terminal workspace tool")
        self.assertTrue(cli_m.startswith("flowchart LR"))
        self.assertIn("CLIParser", cli_m)

        # 5. Web / Frontend flow
        web_m = generate_architecture_mermaid("facebook/react", category="Web & Frontend", description="UI library for web apps")
        self.assertTrue(web_m.startswith("flowchart TD"))
        self.assertIn("UIComponent", web_m)
        self.assertIn("StateManager", web_m)

        # 6. Library / SDK flow
        sdk_m = generate_architecture_mermaid("stripe/stripe-python", repo_type="library_sdk", description="Official client SDK")
        self.assertTrue(sdk_m.startswith("flowchart LR"))
        self.assertIn("SDK", sdk_m)

    def test_architecture_mermaid_integrated_in_analysis(self):
        repo = TrendingRepo(
            name="cool-team/agent-orchestrator",
            owner="cool-team",
            repo="agent-orchestrator",
            url="https://github.com/cool-team/agent-orchestrator",
            description="Autonomous multi-agent orchestration framework for LLMs",
            language="Python",
            language_color="#3572A5",
            stars_total="5200",
            forks_total="450",
            stars_since="620",
            timeframe="daily",
        )
        analysis = analyze_repository(repo, fetch_readme=False)
        self.assertTrue(analysis.architecture_mermaid.startswith("flowchart"))
        self.assertIn("agent-orchestrator", analysis.architecture_mermaid)

        data = analysis.to_dict()
        self.assertIn("architecture_mermaid", data)
        self.assertEqual(data["architecture_mermaid"], analysis.architecture_mermaid)

    def test_extract_release_highlights(self):
        body = '''
## What's Changed
* Add new high-performance parser ([#123](https://github.com/foo/bar/pull/123))
- Fix memory leak in buffer allocation (a1b2c3d)
• Full Changelog: https://github.com/foo/bar/compare/v1.0...v1.1
* Enhanced CLI diagnostics with color support
        '''
        highlights = extract_release_highlights(body)
        self.assertEqual(len(highlights), 3)
        self.assertIn("Add new high-performance parser", highlights[0])
        self.assertIn("Fix memory leak in buffer allocation", highlights[1])
        self.assertIn("Enhanced CLI diagnostics with color support", highlights[2])

    @patch("src.fetcher.urllib.request.urlopen")
    def test_fetch_repo_release_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "tag_name": "v2.0.0",
            "name": "Major 2.0 Release",
            "published_at": "2026-10-25T12:00:00Z",
            "html_url": "https://github.com/org/repo/releases/tag/v2.0.0",
            "body": "- Revolutionary new architecture\n- 50% faster inference",
            "prerelease": False
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = fetch_repo_release("org", "repo", use_cache=False)
        self.assertIsNotNone(res)
        self.assertEqual(res["tag_name"], "v2.0.0")
        self.assertEqual(len(res["highlights"]), 2)
        self.assertFalse(res["is_tag_only"])

    @patch("src.fetcher.urllib.request.urlopen")
    def test_fetch_repo_release_tag_fallback(self, mock_urlopen):
        # 1st call to /releases/latest raises 404
        import urllib.error
        err_404 = urllib.error.HTTPError("url", 404, "Not Found", {}, None)

        mock_resp_tag = MagicMock()
        mock_resp_tag.status = 200
        mock_resp_tag.read.return_value = json.dumps([
            {"name": "v1.0.0-rc1"}
        ]).encode("utf-8")

        mock_urlopen.side_effect = [err_404, MagicMock(__enter__=MagicMock(return_value=mock_resp_tag))]

        res = fetch_repo_release("org", "repo-no-rel", use_cache=False)
        self.assertIsNotNone(res)
        self.assertEqual(res["tag_name"], "v1.0.0-rc1")
        self.assertTrue(res["is_tag_only"])

    def test_calculate_pulse_status(self):
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # 1. Pushed today -> active
        today_iso = now.isoformat()
        status, vi, en, days = calculate_pulse_status(today_iso)
        self.assertEqual(status, "active")
        self.assertIn("🟢", vi)
        self.assertEqual(days, 0)

        # 2. Pushed 15 days ago -> steady
        steady_iso = (now - datetime.timedelta(days=15)).isoformat()
        status, vi, en, days = calculate_pulse_status(steady_iso)
        self.assertEqual(status, "steady")
        self.assertIn("🟡", vi)
        self.assertEqual(days, 15)

        # 3. Pushed 50 days ago -> slow
        slow_iso = (now - datetime.timedelta(days=50)).isoformat()
        status, vi, en, days = calculate_pulse_status(slow_iso)
        self.assertEqual(status, "slow")
        self.assertIn("🟠", vi)

        # 4. Pushed 120 days ago -> dormant
        dormant_iso = (now - datetime.timedelta(days=120)).isoformat()
        status, vi, en, days = calculate_pulse_status(dormant_iso)
        self.assertEqual(status, "dormant")
        self.assertIn("🔴", vi)

        # 5. Invalid / empty -> unknown
        status, vi, en, days = calculate_pulse_status("")
        self.assertEqual(status, "unknown")
        self.assertEqual(days, -1)

    @patch("src.fetcher.urllib.request.urlopen")
    def test_fetch_repo_community_pulse(self, mock_urlopen):
        repo_data = {
            "pushed_at": "2026-10-28T10:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "default_branch": "main",
            "open_issues_count": 42,
            "subscribers_count": 150,
            "forks_count": 890,
            "license": {"key": "mit", "name": "MIT License", "spdx_id": "MIT"}
        }
        contrib_data = [
            {"login": "lead-dev", "avatar_url": "https://avatars.com/u1", "contributions": 120, "html_url": "https://github.com/lead-dev"}
        ]

        mock_resp_repo = MagicMock(status=200, read=MagicMock(return_value=json.dumps(repo_data).encode("utf-8")))
        mock_resp_contrib = MagicMock(status=200, read=MagicMock(return_value=json.dumps(contrib_data).encode("utf-8")))

        mock_urlopen.side_effect = [
            MagicMock(__enter__=MagicMock(return_value=mock_resp_repo)),
            MagicMock(__enter__=MagicMock(return_value=mock_resp_contrib)),
        ]

        pulse = fetch_repo_community_pulse("test-org", "test-repo", use_cache=False)
        self.assertIsNotNone(pulse)
        self.assertEqual(pulse["open_issues_count"], 42)
        self.assertEqual(pulse["license_spdx"], "MIT")
        self.assertEqual(pulse["watchers_count"], 150)
        self.assertEqual(len(pulse["top_contributors"]), 1)
        self.assertEqual(pulse["top_contributors"][0]["login"], "lead-dev")

    def test_repo_analysis_has_playground(self):
        repo = TrendingRepo(
            name="pallets/flask",
            owner="pallets",
            repo="flask",
            url="https://github.com/pallets/flask",
            description="The Python micro framework for building web applications.",
            language="Python",
            language_color="#3572A5",
            stars_total="68,000",
            forks_total="15,000",
            stars_since="150",
            timeframe="daily",
        )
        analysis = analyze_repository(repo, use_ai=False, fetch_readme=False)
        self.assertIsNotNone(analysis.playground)
        self.assertEqual(analysis.playground["port"], 5000)
        self.assertEqual(analysis.playground["framework"], "Flask")
        as_dict = analysis.to_dict()
        self.assertIn("playground", as_dict)
        self.assertIsNotNone(as_dict["playground"])





if __name__ == "__main__":
    unittest.main()
