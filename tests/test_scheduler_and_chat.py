"""Unit tests for Repo Q&A / Chat and Background Scheduler Automation."""

from datetime import datetime
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.repo_chat import ask_repo, heuristic_search_answer
from src.scheduler import (
    export_cron_script,
    export_windows_task_command,
    run_scheduled_job,
    send_webhook_notification,
)
from src.analyzer import RepoAnalysis
from src.scraper import TrendingRepo


class TestRepoChat(unittest.TestCase):

    def setUp(self):
        self.mock_analysis = {
            "name": "cool/agent-runner",
            "description": "Local agent sandbox runtime",
            "core_purpose": "Môi trường cô lập thực thi agent an toàn.",
            "key_features": ["Kernel sandbox [S1]", "Credential proxy [S1]"],
            "how_it_works": ["Điều hướng system calls qua kernel filter [S1]."],
            "adoption_notes": ["Yêu cầu Linux hoặc Windows WSL 2, cần Docker hoặc Podman [S1]."],
            "limitations": ["Chưa có benchmark kiểm thử vượt sandbox độc lập [S1]."],
            "comparisons": ["So với Docker thuần: có credential proxy và policy verification [S1]."],
            "commercial_alternative": "Docker Desktop",
            "quick_run": "docker run -d cool/agent-runner",
        }

    def test_heuristic_search_answer_offline_and_requirements(self):
        ans, sources = heuristic_search_answer("cool/agent-runner", "Yêu cầu phần cứng và hệ điều hành thế nào?", self.mock_analysis)
        self.assertIn("Linux hoặc Windows WSL 2", ans)
        self.assertTrue(len(sources) >= 1)

    def test_heuristic_search_answer_comparisons(self):
        ans, sources = heuristic_search_answer("cool/agent-runner", "Dự án này so sánh hoặc khác gì với giải pháp khác?", self.mock_analysis)
        self.assertIn("Docker Desktop", ans)
        self.assertIn("credential proxy", ans)

    def test_heuristic_search_answer_install(self):
        ans, sources = heuristic_search_answer("cool/agent-runner", "Lệnh cài đặt hoặc chạy nhanh là gì?", self.mock_analysis)
        self.assertIn("docker run -d cool/agent-runner", ans)

    @patch("src.repo_chat.fetch_repo_readme", return_value="# Cool Tool\nFast tool.")
    @patch("src.repo_chat.ask_repo_ai")
    def test_ask_repo_with_ai_fallback(self, mock_ai, mock_fetch):
        mock_ai.return_value = ("Đây là câu trả lời từ AI [S1].", [{"id": "[AI]", "title": "Gemini"}])
        res = ask_repo("cool/agent-runner", "Làm sao để dùng?", use_ai=True, cached_analysis=self.mock_analysis)
        self.assertIn("câu trả lời từ AI", res["answer"])
        self.assertTrue(res["engine_used"].startswith("ai"))


class TestScheduler(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_export_task_commands(self):
        cron = export_cron_script("python3", "/opt/app/gh_trending.py", timeframe="weekly", hour=9, minute=15)
        self.assertIn("15 9 * * *", cron)
        self.assertIn("/opt/app/gh_trending.py", cron)

        win = export_windows_task_command("python.exe", "C:\\app\\gh_trending.py", start_time="07:30")
        self.assertIn("schtasks /Create", win)
        self.assertIn("07:30", win)
        self.assertIn("GitHubTrendingAnalyzer", win)

    @patch("src.scheduler.get_trending_repos")
    @patch("src.scheduler.analyze_batch")
    def test_run_scheduled_job(self, mock_analyze, mock_get_repos):
        repo = TrendingRepo("acme/tool", "acme", "tool", "https://github.com/acme/tool", "Desc", "Python", "#fff", "100", "10", "20", "daily")
        mock_get_repos.return_value = [repo]

        analysis = RepoAnalysis(
            name="acme/tool",
            owner="acme",
            repo="tool",
            url="https://github.com/acme/tool",
            language="Python",
            stars_total="100",
            stars_since="20",
            timeframe="daily",
            description="Desc",
            category="AI",
            core_purpose="A cool tool",
            velocity_badge="🚀 Breakout Velocity",
            is_new_entry=True,
            commercial_alternative="Datadog",
            match_score=80,
        )
        mock_analyze.return_value = [analysis]

        summary = run_scheduled_job(
            timeframe="daily",
            limit=1,
            output_dir=self.temp_dir.name,
        )

        self.assertEqual(summary["status"], "success")
        self.assertEqual(summary["total_analyzed"], 1)
        self.assertIn("acme/tool", summary["breakouts"])
        self.assertIn("acme/tool", summary["new_entries"])
        self.assertTrue(os.path.exists(summary["report_md"]))
        self.assertTrue(os.path.exists(summary["report_html"]))

        with open(summary["report_md"], "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("acme/tool", content)
            self.assertIn("Datadog", content)

    @patch("src.scheduler.urllib.request.urlopen")
    def test_send_webhook_notification(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        summary = {
            "date": "2026-10-21",
            "total_analyzed": 5,
            "breakouts": ["team/fast"],
            "new_entries": ["new/star"],
            "matches": ["team/match (90%)"],
            "commercial_alternatives": ["team/alt (thay Notion)"],
            "report_md": "reports/trending_2026-10-21.md",
        }

        sent = send_webhook_notification("https://discord.com/api/webhooks/test", summary)
        self.assertTrue(sent)
        self.assertTrue(mock_urlopen.called)


if __name__ == "__main__":
    unittest.main()
