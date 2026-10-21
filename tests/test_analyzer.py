"""Unit tests for Analyzer Engine."""

import unittest
from src.analyzer import (
    analyze_repo_heuristic,
    detect_category,
    extract_features_from_markdown,
)
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


if __name__ == "__main__":
    unittest.main()
