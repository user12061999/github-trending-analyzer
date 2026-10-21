"""Tests for SQLite history, feedback loop, adaptive preferences and dynamic knowledge."""

import json
import os
import shutil
import tempfile
import unittest

from src.history_db import (
    add_learned_knowledge,
    extract_adaptive_preferences,
    get_all_feedback,
    get_connection,
    get_learned_knowledge,
    get_repo_trajectory,
    save_snapshot,
    set_repo_feedback,
)
from src.alternatives import detect_commercial_alternative, get_alternative_description


class TestHistoryAndFeedback(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_history.db")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_snapshot_and_trajectory(self):
        repo_data = {
            "name": "test-org/smart-tool",
            "owner": "test-org",
            "repo": "smart-tool",
            "stars_total": 1200,
            "stars_since": 150,
            "timeframe": "daily",
            "category": "AI & Machine Learning",
            "maturity_level": "production",
            "velocity_badge": "🔥 Breakout Star",
            "commercial_alternative": "Notion",
            "match_score": 75,
            "engine_used": "heuristic",
        }
        # First snapshot
        row_id1 = save_snapshot(repo_data, db_path=self.db_path)
        self.assertGreater(row_id1, 0)

        traj1 = get_repo_trajectory("test-org/smart-tool", db_path=self.db_path)
        self.assertTrue(traj1["is_new_entry"])
        self.assertEqual(traj1["times_seen"], 1)
        self.assertIsNotNone(traj1["first_seen_at"])

        # Second snapshot for the same repo (seen again)
        row_id2 = save_snapshot(repo_data, db_path=self.db_path)
        self.assertGreater(row_id2, row_id1)

        traj2 = get_repo_trajectory("test-org/smart-tool", db_path=self.db_path)
        self.assertFalse(traj2["is_new_entry"])
        self.assertEqual(traj2["times_seen"], 2)

    def test_repo_feedback_ratings_and_status(self):
        # Set feedback
        fb = set_repo_feedback(
            full_name="test-org/agent-kit",
            rating=1,
            status="want_to_try",
            notes="Cần thử nghiệm cho pipeline sắp tới",
            db_path=self.db_path,
        )
        self.assertEqual(fb["rating"], 1)
        self.assertEqual(fb["status"], "want_to_try")

        # Query all feedback
        all_fb = get_all_feedback(db_path=self.db_path)
        self.assertIn("test-org/agent-kit", all_fb)
        self.assertEqual(all_fb["test-org/agent-kit"]["rating"], 1)
        self.assertEqual(all_fb["test-org/agent-kit"]["notes"], "Cần thử nghiệm cho pipeline sắp tới")

        # Update feedback (partial update)
        fb_updated = set_repo_feedback(
            full_name="test-org/agent-kit",
            status="tried",
            db_path=self.db_path,
        )
        self.assertEqual(fb_updated["status"], "tried")
        self.assertEqual(fb_updated["rating"], 1)  # rating preserved

        # Trajectory incorporates user feedback
        traj = get_repo_trajectory("test-org/agent-kit", db_path=self.db_path)
        self.assertEqual(traj["user_rating"], 1)
        self.assertEqual(traj["user_status"], "tried")

    def test_dynamic_knowledge_learning(self):
        # Add dynamic commercial target
        added = add_learned_knowledge(
            entity_name="CustomSaaS",
            entity_type="commercial_target",
            description="Nền tảng Cloud Workflow thương mại",
            detected_from_repo="test-org/open-workflow",
            db_path=self.db_path,
        )
        self.assertTrue(added)

        learned = get_learned_knowledge("commercial_target", db_path=self.db_path)
        self.assertIn("CustomSaaS", learned)
        self.assertEqual(learned["CustomSaaS"], "Nền tảng Cloud Workflow thương mại")

    def test_adaptive_preferences_extraction(self):
        # Save snapshots for two repos
        save_snapshot({
            "name": "org-a/rust-agent",
            "language": "Rust",
            "category": "AI & Machine Learning",
            "tech_stack": ["Rust", "Tokio", "LLM"],
        }, db_path=self.db_path)

        save_snapshot({
            "name": "org-b/fast-db",
            "language": "Rust",
            "category": "Database & Storage",
            "tech_stack": ["Rust", "RocksDB", "Raft"],
        }, db_path=self.db_path)

        # Mark both as liked or want_to_try
        set_repo_feedback("org-a/rust-agent", rating=1, status="want_to_try", db_path=self.db_path)
        set_repo_feedback("org-b/fast-db", rating=1, status="tried", db_path=self.db_path)

        prefs = extract_adaptive_preferences(db_path=self.db_path)
        self.assertIn("Rust", prefs["languages"])
        self.assertTrue(any(c in ("AI & Machine Learning", "Database & Storage") for c in prefs["categories"]))
        self.assertTrue(any(k in ("rust", "tokio", "llm", "rocksdb", "raft") for k in prefs["keywords"]))


if __name__ == "__main__":
    unittest.main()
