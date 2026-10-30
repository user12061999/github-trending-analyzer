"""Unit tests for Playground, Docker Manifest & 1-Click Cloud Execution Generator."""

import unittest
from src.playground import (
    generate_cloud_links,
    generate_docker_manifest,
    generate_local_scripts,
    generate_playground_manifest,
    infer_runtime_env,
)


class TestPlayground(unittest.TestCase):
    def test_infer_runtime_node_react(self):
        env = infer_runtime_env(
            repo_name="shadcn/ui",
            language="TypeScript",
            description="Beautifully designed components built with Radix UI and Tailwind CSS.",
            topics=["react", "tailwind", "nextjs"],
        )
        self.assertEqual(env["port"], 3000)
        self.assertEqual(env["category"], "frontend")
        self.assertIn("npm", env["install_cmd"])
        self.assertIn("npm run dev", env["run_cmd"])

    def test_infer_runtime_python_fastapi(self):
        env = infer_runtime_env(
            repo_name="tiangolo/fastapi",
            language="Python",
            description="FastAPI framework, high performance, easy to learn, fast to code, ready for production",
            topics=["fastapi", "python", "pydantic"],
            tech_stack=["FastAPI", "Uvicorn"],
        )
        self.assertEqual(env["port"], 8000)
        self.assertEqual(env["framework"], "FastAPI")
        self.assertIn("requirements.txt", env["install_cmd"])
        self.assertIn("uvicorn", env["run_cmd"])

    def test_infer_runtime_ai_ollama(self):
        env = infer_runtime_env(
            repo_name="ollama/ollama",
            language="Go",
            description="Get up and running with Llama 3, Mistral, and other large language models.",
            topics=["ai", "llm"],
            quick_run="docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama",
        )
        self.assertEqual(env["port"], 11434)
        self.assertEqual(env["framework"], "Ollama / Local LLM")
        self.assertEqual(env["category"], "ai")

    def test_infer_runtime_go(self):
        env = infer_runtime_env(
            repo_name="gin-gonic/gin",
            language="Go",
            description="Gin is a HTTP web framework written in Go.",
            topics=["go", "web"],
        )
        self.assertEqual(env["port"], 8080)
        self.assertIn("go mod download", env["install_cmd"])
        self.assertIn("go run .", env["run_cmd"])

    def test_infer_runtime_rust(self):
        env = infer_runtime_env(
            repo_name="tokio-rs/axum",
            language="Rust",
            description="Ergonomic and modular web framework built with Tokio, Tower, and Hyper",
            topics=["rust", "async", "web"],
        )
        self.assertEqual(env["port"], 8080)
        self.assertIn("cargo build", env["install_cmd"])
        self.assertIn("cargo run", env["run_cmd"])

    def test_infer_runtime_streamlit(self):
        env = infer_runtime_env(
            repo_name="user/streamlit-app",
            language="Python",
            description="Interactive dashboard built with streamlit",
            topics=["data-visualization"],
        )
        self.assertEqual(env["port"], 8501)
        self.assertEqual(env["framework"], "Streamlit")
        self.assertIn("streamlit run", env["run_cmd"])

    def test_infer_runtime_gradio(self):
        env = infer_runtime_env(
            repo_name="gradio-app/gradio",
            language="Python",
            description="Build and share delightful machine learning apps with gradio",
        )
        self.assertEqual(env["port"], 7860)
        self.assertEqual(env["framework"], "Gradio")

    def test_cloud_links_generation(self):
        links_python = generate_cloud_links(
            repo_name="pytorch/pytorch",
            language="Python",
            description="Tensors and Dynamic neural networks in Python",
            topics=["deep-learning", "machine-learning"],
        )
        link_ids = [l["id"] for l in links_python]
        self.assertIn("codespaces", link_ids)
        self.assertIn("gitpod", link_ids)
        self.assertIn("github_dev", link_ids)
        self.assertIn("colab", link_ids)  # Colab enabled for AI/Python

        links_web = generate_cloud_links(
            repo_name="vercel/next.js",
            language="JavaScript",
            description="The React Framework for the Web",
            topics=["react", "nextjs"],
        )
        web_link_ids = [l["id"] for l in links_web]
        self.assertIn("stackblitz", web_link_ids)  # StackBlitz enabled for Web

    def test_docker_manifest_generation(self):
        runtime = infer_runtime_env(
            repo_name="sample/node-service",
            language="TypeScript",
            description="Web microservice",
            topics=["node"],
        )
        manifest = generate_docker_manifest("sample/node-service", runtime)
        self.assertIn("version: '3.8'", manifest["docker_compose"])
        self.assertIn("FROM node:20-alpine", manifest["dockerfile"])
        self.assertIn("EXPOSE 3000", manifest["dockerfile"])
        self.assertIn("docker compose up", manifest["docker_run_cmd"])

    def test_docker_manifest_with_official_image(self):
        runtime = infer_runtime_env(
            repo_name="ollama/ollama",
            language="Go",
            description="Local LLMs",
            quick_run="docker run -d -p 11434:11434 ollama/ollama",
        )
        manifest = generate_docker_manifest("ollama/ollama", runtime)
        self.assertIn("image: ollama/ollama", manifest["docker_compose"])

    def test_local_scripts_generation(self):
        runtime = infer_runtime_env(
            repo_name="owner/mytool",
            language="Python",
            description="CLI productivity tool",
        )
        scripts = generate_local_scripts("owner/mytool", runtime)
        self.assertIn("#!/usr/bin/env bash", scripts["bash"])
        self.assertIn("git clone \"$URL\"", scripts["bash"])
        self.assertIn("$ErrorActionPreference = \"Stop\"", scripts["powershell"])
        self.assertIn("git clone $Url", scripts["powershell"])
        self.assertTrue(scripts["one_liner"].startswith("git clone https://github.com/owner/mytool.git"))

    def test_generate_playground_manifest_full(self):
        manifest = generate_playground_manifest(
            repo_name="facebook/react",
            language="JavaScript",
            description="A declarative, efficient, and flexible JavaScript library for building user interfaces.",
            topics=["javascript", "react", "ui"],
        )
        self.assertEqual(manifest["repo_name"], "facebook/react")
        self.assertEqual(manifest["slug"], "react")
        self.assertTrue(len(manifest["cloud_links"]) >= 3)
        self.assertIn("docker_compose", manifest["docker"])
        self.assertIn("bash", manifest["scripts"])
        self.assertIn("powershell", manifest["scripts"])


if __name__ == "__main__":
    unittest.main()
