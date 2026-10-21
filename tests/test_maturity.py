"""Unit tests for maturity evaluation, velocity calculation, tech stack, and quick run."""

import unittest
from src.maturity import (
    calculate_velocity,
    evaluate_maturity,
    extract_quick_run,
    extract_tech_stack,
    parse_star_count,
)


class TestMaturity(unittest.TestCase):

    def test_parse_star_count(self):
        self.assertEqual(parse_star_count("1,234"), 1234)
        self.assertEqual(parse_star_count("5.5k"), 5500)
        self.assertEqual(parse_star_count("1.2M"), 1200000)
        self.assertEqual(parse_star_count("+450"), 450)
        self.assertEqual(parse_star_count(None), 0)

    def test_calculate_velocity_breakout(self):
        # Total < 3000 stars, 300 stars today -> Breakout
        rate, label, badge = calculate_velocity("300", "1,500")
        self.assertIn("Breakout Star", badge)
        self.assertEqual(rate, 20.0)

    def test_calculate_velocity_established(self):
        # 50k stars, 200 stars today -> Established Giant
        rate, label, badge = calculate_velocity("200", "50,000")
        self.assertIn("Established", badge)

    def test_evaluate_maturity_production(self):
        readme = """
        # Production Tool
        [![Build](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg)](link)
        Full documentation available at https://docs.example.com.
        Run `docker run -p 8080:8080 mytool`
        Install with `pip install mytool`
        Comprehensive tests included with pytest.
        Licensed under Apache 2.0.
        """
        level, badge = evaluate_maturity("mytool", "Fast production tool", readme, "6,000")
        self.assertEqual(level, "production")
        self.assertIn("Production Ready", badge)

    def test_evaluate_maturity_experimental(self):
        readme = "A toy proof of concept experiment for research purposes only."
        level, badge = evaluate_maturity("poc-project", "PoC demo", readme, "200")
        self.assertEqual(level, "experimental")
        self.assertIn("Experimental", badge)

    def test_extract_tech_stack(self):
        text = "Built with PyTorch, FastAPI and Docker. Uses PostgreSQL and Redis for persistence."
        stack = extract_tech_stack(text)
        self.assertIn("PyTorch", stack)
        self.assertIn("FastAPI", stack)
        self.assertIn("Docker", stack)
        self.assertIn("PostgreSQL", stack)
        self.assertIn("Redis", stack)

    def test_extract_quick_run(self):
        readme_docker = "Quick start:\n```bash\ndocker run -d -p 3000:3000 myapp\n```"
        cmd = extract_quick_run(readme_docker)
        self.assertEqual(cmd, "docker run -d -p 3000:3000 myapp")

        readme_pip = "Installation:\n`pip install my-cool-tool`"
        cmd2 = extract_quick_run(readme_pip)
        self.assertEqual(cmd2, "pip install my-cool-tool")


if __name__ == "__main__":
    unittest.main()
