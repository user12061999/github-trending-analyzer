"""Unit tests for Repository Type Taxonomy and Classification."""

import unittest

from src.repo_type import REPO_TYPES, detect_repo_type
from src.maturity import evaluate_maturity, extract_quick_run
from src.analyzer import RepoAnalysis, analyze_repository
from src.scraper import TrendingRepo


class TestRepoType(unittest.TestCase):
    def test_detect_course_tutorial(self):
        # 1. By repository name containing coursebook
        t1, b1 = detect_repo_type("cs341-illinois/coursebook", "Systems programming course book")
        self.assertEqual(t1, "course_tutorial")
        self.assertIn("Khóa học", b1)

        # 2. By description containing syllabus and lecture notes
        t2, b2 = detect_repo_type("mit/distributed-systems", "Spring 2026 lecture notes, labs and syllabus")
        self.assertEqual(t2, "course_tutorial")

        # 3. By tutorial guide keyword
        t3, b3 = detect_repo_type("jwasham/coding-interview-university", "A complete computer science study plan to become a software engineer")
        self.assertEqual(t3, "course_tutorial")

    def test_detect_awesome_list(self):
        # 1. By prefix awesome-
        t1, b1 = detect_repo_type("sindresorhus/awesome-nodejs", "Awesome Node.js packages")
        self.assertEqual(t1, "awesome_list")
        self.assertIn("Awesome List", b1)

        # 2. By description curated list
        t2, b2 = detect_repo_type("vinta/useful-python-stuff", "A curated list of awesome Python frameworks and libraries")
        self.assertEqual(t2, "awesome_list")

    def test_detect_ai_model(self):
        t1, b1 = detect_repo_type("bartowski/Llama-3-8B-GGUF", "GGUF model weights for local inference")
        self.assertEqual(t1, "ai_model")
        self.assertIn("AI Model", b1)

        t2, b2 = detect_repo_type("org/stable-diffusion-weights", "Pretrained model weights and safetensors format checkpoints")
        self.assertEqual(t2, "ai_model")

    def test_detect_dataset_benchmark(self):
        t1, b1 = detect_repo_type("eval-group/llm-benchmark", "Evaluation benchmark suite for reasoning models")
        self.assertEqual(t1, "dataset_benchmark")
        self.assertIn("Dataset", b1)

    def test_detect_library_sdk(self):
        t1, b1 = detect_repo_type("org/stripe-python", "Python client library and SDK for Stripe API")
        self.assertEqual(t1, "library_sdk")
        self.assertIn("Library", b1)

    def test_detect_tool_app_default(self):
        t1, b1 = detect_repo_type("fastfetch-cli/fastfetch", "A fast, highly customizable system information tool")
        self.assertEqual(t1, "tool_app")
        self.assertIn("Tool", b1)

    def test_course_maturity_not_production_ready(self):
        # Even with docker and CI keywords, coursebook should NOT be marked Production Ready
        readme = """
        # CS341 Coursebook
        Continuous integration with badge.svg.
        docker run -it cs341/env
        pip install syllabus-tools
        ## Table of Contents
        - Chapter 1: Processes
        - Chapter 2: Threads
        """
        level, badge = evaluate_maturity(
            "cs341-illinois/coursebook",
            "University course materials",
            readme_raw=readme,
            stars_total_str="8,500",
            repo_type="course_tutorial",
        )
        self.assertNotEqual(level, "production")
        self.assertNotIn("Production Ready", badge)
        self.assertEqual(level, "comprehensive")
        self.assertIn("Giáo trình", badge)

    def test_quick_run_suppressed_for_non_software(self):
        # In a course or awesome list, random pip install commands are not the application
        readme = """
        # Awesome Python
        Installation of something:
        `pip install some-tool`
        """
        qr_course = extract_quick_run(readme, language="Python", repo_type="course_tutorial")
        self.assertIsNone(qr_course)

        qr_list = extract_quick_run(readme, language="Python", repo_type="awesome_list")
        self.assertIsNone(qr_list)

        # For tool_app, it should extract normally
        qr_tool = extract_quick_run(readme, language="Python", repo_type="tool_app")
        self.assertEqual(qr_tool, "pip install some-tool")

    def test_analyze_repository_populates_repo_type(self):
        repo = TrendingRepo(
            name="cs341-illinois/coursebook",
            owner="cs341-illinois",
            repo="coursebook",
            url="https://github.com/cs341-illinois/coursebook",
            description="Systems programming course book",
            language="C",
            language_color="#fff",
            stars_total="1200",
            forks_total="300",
            stars_since="45",
            timeframe="daily",
        )
        analysis = analyze_repository(repo, fetch_readme=False)
        self.assertEqual(analysis.repo_type, "course_tutorial")
        self.assertIn("Khóa học", analysis.repo_type_badge)
        self.assertNotEqual(analysis.maturity_level, "production")


if __name__ == "__main__":
    unittest.main()
