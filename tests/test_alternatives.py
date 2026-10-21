"""Unit tests for commercial alternative detection."""

import unittest
from src.alternatives import (
    clean_target_name,
    detect_commercial_alternative,
    get_alternative_description,
)


class TestAlternatives(unittest.TestCase):

    def test_detect_known_target_in_description(self):
        desc = "VoiceStudio is the open-source, fully-local ElevenLabs alternative for voice cloning."
        alt = detect_commercial_alternative("VoiceStudio", desc)
        self.assertEqual(alt, "ElevenLabs")

    def test_detect_alternative_to_pattern(self):
        desc = "A modern self-hosted alternative to Notion and Airtable for knowledge management."
        alt = detect_commercial_alternative("my-notes", desc)
        self.assertIn(alt, ["Notion", "Airtable"])

    def test_detect_drop_in_replacement(self):
        readme = """
        # MyDatadogAgent
        A lightweight drop-in replacement for Datadog APM with zero overhead.
        """
        alt = detect_commercial_alternative("agent", "APM tool", readme_raw=readme)
        self.assertEqual(alt, "Datadog")

    def test_detect_like_x_but_open_source(self):
        desc = "Like Cursor but completely open-source and free to run locally."
        alt = detect_commercial_alternative("open-cursor", desc)
        self.assertEqual(alt, "Cursor")

    def test_no_false_positives_on_generic_phrases(self):
        desc = "A great alternative to traditional web frameworks."
        alt = detect_commercial_alternative("simple-web", desc)
        self.assertIsNone(alt)

        desc2 = "Provides an alternative approach for developers."
        alt2 = detect_commercial_alternative("tool", desc2)
        self.assertIsNone(alt2)

    def test_clean_target_name(self):
        self.assertEqual(clean_target_name(" ElevenLabs! "), "ElevenLabs")
        self.assertEqual(clean_target_name("the Notion"), "Notion")
        self.assertIsNone(clean_target_name("traditional"))
        self.assertIsNone(clean_target_name("using"))

    def test_get_alternative_description(self):
        desc = get_alternative_description("ElevenLabs")
        self.assertIn("Voice AI", desc)


if __name__ == "__main__":
    unittest.main()
