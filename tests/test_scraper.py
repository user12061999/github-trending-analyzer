"""Unit tests for GitHub Trending Scraper."""

import unittest
from src.scraper import parse_trending_html

SAMPLE_TRENDING_HTML = """
<!DOCTYPE html>
<html>
<body>
<div class="explore-pjax-container container-lg p-responsive pt-6">
  <div class="Box">
    <div class="Box-row">
      <article class="Box-row">
        <h2 class="h3 lh-condensed">
          <a href="/anthropics/claude-code" data-hydro-click="...">
            <span class="text-normal">anthropics / </span>claude-code
          </a>
        </h2>
        <p class="col-9 color-fg-muted my-1 pr-4">
          Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you turn ideas into software.
        </p>
        <div class="f6 color-fg-muted mt-2">
          <span class="d-inline-block ml-0 mr-3">
            <span class="repo-language-color" style="background-color: #3178c6"></span>
            <span itemprop="programmingLanguage">TypeScript</span>
          </span>
          <a href="/anthropics/claude-code/stargazers" class="Link--muted d-inline-block mr-3">
            15,420
          </a>
          <a href="/anthropics/claude-code/forks" class="Link--muted d-inline-block mr-3">
            1,200
          </a>
          <span class="d-inline-block mr-3">
            Built by
            <a href="/alice"><img class="avatar mb-1 avatar-user" src="..." width="20" height="20" alt="@alice" /></a>
            <a href="/bob"><img class="avatar mb-1 avatar-user" src="..." width="20" height="20" alt="@bob" /></a>
          </span>
          <span class="d-inline-block float-sm-right">
            2,450 stars today
          </span>
        </div>
      </article>
      <article class="Box-row">
        <h2 class="h3 lh-condensed">
          <a href="/rust-lang/rust">
            <span class="text-normal">rust-lang / </span>rust
          </a>
        </h2>
        <p class="col-9 color-fg-muted my-1 pr-4">
          Empowering everyone to build reliable and efficient software.
        </p>
        <div class="f6 color-fg-muted mt-2">
          <span class="d-inline-block ml-0 mr-3">
            <span class="repo-language-color" style="background-color: #dea584"></span>
            <span itemprop="programmingLanguage">Rust</span>
          </span>
          <a href="/rust-lang/rust/stargazers" class="Link--muted d-inline-block mr-3">
            98,000
          </a>
          <span class="d-inline-block float-sm-right">
            180 stars today
          </span>
        </div>
      </article>
    </div>
  </div>
</div>
</body>
</html>
"""


class TestGitHubTrendingScraper(unittest.TestCase):

    def test_parse_trending_html(self):
        repos = parse_trending_html(SAMPLE_TRENDING_HTML, timeframe="daily")
        self.assertEqual(len(repos), 2)

        # Check first repo
        r1 = repos[0]
        self.assertEqual(r1.name, "anthropics/claude-code")
        self.assertEqual(r1.owner, "anthropics")
        self.assertEqual(r1.repo, "claude-code")
        self.assertEqual(r1.url, "https://github.com/anthropics/claude-code")
        self.assertIn("agentic coding tool", r1.description)
        self.assertEqual(r1.language, "TypeScript")
        self.assertEqual(r1.language_color, "#3178c6")
        self.assertEqual(r1.stars_total, "15420")
        self.assertEqual(r1.stars_since, "2450")
        self.assertEqual(r1.built_by, ["alice", "bob"])

        # Check second repo
        r2 = repos[1]
        self.assertEqual(r2.name, "rust-lang/rust")
        self.assertEqual(r2.owner, "rust-lang")
        self.assertEqual(r2.language, "Rust")
        self.assertEqual(r2.stars_total, "98000")
        self.assertEqual(r2.stars_since, "180")


if __name__ == "__main__":
    unittest.main()
