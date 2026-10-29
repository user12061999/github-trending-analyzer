"""Unit tests for Analyzer Engine."""

import unittest
from src.analyzer import (
    analyze_repo_heuristic,
    analyze_repository,
    detect_category,
    extract_features_from_markdown,
    generate_architecture_mermaid,
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



if __name__ == "__main__":
    unittest.main()
