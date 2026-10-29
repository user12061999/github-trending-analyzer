"""Unit tests for Dynamic Few-Shot Learning & Grounded Self-Critique."""

import json
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.analyzer import RepoAnalysis, analyze_repo_ai
from src.few_shot import (
    CURATED_EXEMPLARS,
    find_liked_exemplar_from_db,
    format_few_shot_prompt,
    get_few_shot_exemplar,
)
from src.grounding import (
    detect_hype_terms,
    evaluate_grounding,
    sanitize_and_ground_analysis,
    soften_hype_phrases,
)
from src.history_db import get_connection, save_snapshot, set_repo_feedback
from src.scraper import TrendingRepo


class TestDynamicFewShotAndGrounding(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_few_shot.db")
        conn = get_connection(self.db_path)
        conn.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_curated_exemplar_fallback(self):
        # Audio / Speech category
        ex_audio, src_audio = get_few_shot_exemplar(category="Audio & Speech", repo_type="tool_app", db_path=self.db_path)
        self.assertIn("VoiceStudio", ex_audio["name"])
        self.assertIn("debpalash/VoiceStudio", src_audio)

        # Library / SDK type
        ex_lib, src_lib = get_few_shot_exemplar(category="Developer Tooling", repo_type="library_sdk", db_path=self.db_path)
        self.assertIn("uv", ex_lib["name"])
        self.assertIn("astral-sh/uv", src_lib)

        # Default tool / AI
        ex_tool, src_tool = get_few_shot_exemplar(category="AI & Machine Learning", repo_type="tool_app", db_path=self.db_path)
        self.assertIn("OpenShell", ex_tool["name"])
        self.assertIn("NVIDIA/OpenShell", src_tool)

    def test_sqlite_dynamic_few_shot_learning_from_user_like(self):
        # 1. Initially no liked repos in DB -> returns fallback
        ex, src = get_few_shot_exemplar(category="Web & Frontend", repo_type="tool_app", db_path=self.db_path)
        self.assertIn("curated", src)

        # 2. User likes a repo in DB
        custom_analysis = {
            "name": "my-org/super-web",
            "language": "TypeScript",
            "category": "Web & Frontend",
            "repo_type": "tool_app",
            "description": "Blazing web compiler",
            "core_purpose": "Trình biên dịch web thế hệ mới tối ưu bundle size [S1].",
            "key_features": ["Zero config [S1]", "Instant HMR [S1]"],
            "target_audience": "Frontend engineers",
            "use_cases": ["Build SPA"],
            "why_trending": "Tốc độ nhanh",
            "quick_verdict": "Nên dùng thử",
            "suitable_major": "Software Engineering",
            "target_roles": "Frontend Developer",
            "real_world_impact": "Giảm 50% thời gian build",
            "how_it_works": ["Phân tích AST và tree-shaking [S1]."],
            "practical_examples": ["Đo thời gian build 100 modules."],
            "limitations": ["Chưa hỗ trợ plugin legacy [S1]."],
            "adoption_notes": ["Node 18+ [S1]."],
            "comparisons": ["Nhanh hơn Webpack [S1]."],
            "research_gaps": ["Chưa test với monorepo lớn."],
        }
        save_snapshot(custom_analysis, db_path=self.db_path)
        set_repo_feedback("my-org/super-web", rating=1, db_path=self.db_path)

        # 3. Dynamic few-shot now retrieves the user-liked repo
        ex_liked, src_liked = get_few_shot_exemplar(category="Web & Frontend", repo_type="tool_app", db_path=self.db_path)
        self.assertEqual(ex_liked["name"], "my-org/super-web")
        self.assertIn("sqlite (user-liked: my-org/super-web)", src_liked)

    def test_format_few_shot_prompt(self):
        exemplar = CURATED_EXEMPLARS["tool_app"]
        prompt_block = format_few_shot_prompt(exemplar, "test-source")
        self.assertIn("FEW-SHOT BENCHMARK: test-source", prompt_block)
        self.assertIn("NVIDIA/OpenShell", prompt_block)
        self.assertIn("[S1]", prompt_block)
        self.assertIn("--- HẾT VÍ DỤ CHUẨN MẪU ---", prompt_block)

    def test_detect_and_soften_hype_terms(self):
        text_with_hype = "Đây là công cụ tốt nhất hiện nay, thay đổi hoàn toàn thế giới và hoàn hảo 100% không có bất kỳ nhược điểm."
        detected = detect_hype_terms(text_with_hype)
        self.assertTrue(len(detected) >= 2)

        softened = soften_hype_phrases(text_with_hype)
        self.assertNotIn("tốt nhất hiện nay", softened)
        self.assertNotIn("thay đổi hoàn toàn thế giới", softened)
        self.assertIn("được định vị hàng đầu", softened)
        self.assertIn("được kỳ vọng cải tiến đáng kể", softened)

    def test_grounding_evaluator_scoring(self):
        # 1. Unverified hype + no citations -> low score
        bad_analysis = RepoAnalysis(
            name="hype/tool",
            owner="hype",
            repo="tool",
            url="https://github.com/hype/tool",
            language="Python",
            stars_total="100",
            stars_since="50",
            timeframe="daily",
            description="Best tool",
            category="AI",
            core_purpose="Công cụ tốt nhất thế giới, không có bất kỳ nhược điểm.",
            key_features=["Tính năng vô địch"],
            how_it_works=["Chạy rất nhanh không cần nguồn nào"],
            limitations=[],
            practical_examples=[],
            research_gaps=[],
        )
        score, critique = evaluate_grounding(bad_analysis)
        self.assertLess(score, 70)
        self.assertTrue(any("tiếp thị" in c or "tuyệt đối hóa" in c for c in critique))
        self.assertTrue(any("trích dẫn" in c for c in critique))

        # 2. Rigorous, grounded analysis -> high score
        good_analysis = RepoAnalysis(
            name="solid/tool",
            owner="solid",
            repo="tool",
            url="https://github.com/solid/tool",
            language="Rust",
            stars_total="1000",
            stars_since="200",
            timeframe="daily",
            description="Grounded tool",
            category="AI",
            core_purpose="Công cụ quản lý bộ nhớ cho agent.",
            key_features=["Cơ chế sandbox [S1]"],
            how_it_works=["Luồng dữ liệu qua kernel filter [S1]."],
            limitations=["Chưa kiểm thử độc lập hiệu năng [S1]."],
            practical_examples=["Thử nghiệm: đo lường thời gian chạy và so sánh tiêu chí."],
            research_gaps=["Chưa rõ benchmark trên môi trường cụ thể."],
            adoption_notes=["Cần Docker [S1]."],
            comparisons=["Khác với gVisor [S1]."],
        )
        score_good, critique_good = evaluate_grounding(good_analysis)
        self.assertGreaterEqual(score_good, 90)

    def test_sanitize_and_ground_analysis(self):
        analysis = RepoAnalysis(
            name="auto/sanitized",
            owner="auto",
            repo="sanitized",
            url="https://github.com/auto/sanitized",
            language="Go",
            stars_total="500",
            stars_since="50",
            timeframe="daily",
            description="Great tool",
            category="DevOps",
            core_purpose="Giải pháp tốt nhất hiện nay cho container.",
            key_features=["Fast"],
            how_it_works=["Proxy [S1]"],
            limitations=[],
            research_gaps=[],
        )
        sanitized = sanitize_and_ground_analysis(analysis)
        self.assertIn("được định vị hàng đầu", sanitized.core_purpose)
        self.assertTrue(len(sanitized.limitations) >= 1)
        self.assertTrue(len(sanitized.research_gaps) >= 1)
        self.assertGreater(sanitized.grounding_score, 0)
        self.assertTrue(len(sanitized.grounding_critique) >= 1)

    @patch("src.few_shot.find_liked_exemplar_from_db", return_value=None)
    @patch("src.analyzer.urllib.request.urlopen")
    def test_analyze_repo_ai_injects_few_shot_and_returns_grounded(self, mock_urlopen, mock_find_db):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "category": "Developer Tooling",
                            "core_purpose": "Công cụ phân tích mã nguồn hiệu quả [S1].",
                            "key_features": ["AST parsing [S1]", "Linter tích hợp [S1]"],
                            "target_audience": "Kỹ sư phần mềm",
                            "use_cases": ["Kiểm tra lỗi code"],
                            "why_trending": "Tăng trưởng stars",
                            "quick_verdict": "Nên thử nghiệm trong dự án nhỏ",
                            "suitable_major": "Computer Science",
                            "target_roles": "Software Engineer",
                            "real_world_impact": "Rút ngắn thời gian review code",
                            "how_it_works": ["Trích xuất AST từ source code [S1]."],
                            "practical_examples": ["Thử nghiệm: chạy kiểm tra 10 file và đo lường thời gian."],
                            "limitations": ["Chưa hỗ trợ Python 3.13 [S1]."],
                            "adoption_notes": ["Cài đặt qua pip [S1]."],
                            "comparisons": ["So với Flake8 [S1]."],
                            "research_gaps": ["Cần đo đạc bộ nhớ tiêu hao khi file lớn."],
                        })
                    }]
                }
            }]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        repo = TrendingRepo(
            name="acme/linter",
            owner="acme",
            repo="linter",
            url="https://github.com/acme/linter",
            description="Fast Python linter written in Rust",
            language="Rust",
            language_color="#dea584",
            stars_total="3000",
            forks_total="200",
            stars_since="150",
            timeframe="daily",
        )

        analysis = analyze_repo_ai(repo, readme_raw="# Acme Linter\nFast linter.", gemini_api_key="test-key")
        self.assertIsNotNone(analysis)
        self.assertTrue(analysis.engine_used.startswith("ai"))
        self.assertIn("curated", analysis.engine_used)
        self.assertGreaterEqual(analysis.grounding_score, 80)
        self.assertTrue(len(analysis.grounding_critique) >= 1)

        # Verify prompt contained few-shot benchmark
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        payload = json.loads(req.data.decode("utf-8"))
        prompt_text = payload["contents"][0]["parts"][0]["text"]
        self.assertIn("FEW-SHOT BENCHMARK", prompt_text)
        self.assertIn("tự phản biện (self-critique)", prompt_text)


if __name__ == "__main__":
    unittest.main()
