"""GitHub Trending Scraper using Python Standard Library (zero-dependency)."""

import html.parser
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def get_ssl_context() -> ssl.SSLContext:
    """Create a resilient SSL context, handling macOS certificates."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass

    return ssl.create_default_context()




@dataclass
class TrendingRepo:
    """Represents a trending repository on GitHub."""
    name: str  # owner/repo
    owner: str
    repo: str
    url: str
    description: str
    language: str
    language_color: str
    stars_total: str
    forks_total: str
    stars_since: str
    timeframe: str  # daily, weekly, monthly
    built_by: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, any]:
        return {
            "name": self.name,
            "owner": self.owner,
            "repo": self.repo,
            "url": self.url,
            "description": self.description,
            "language": self.language,
            "language_color": self.language_color,
            "stars_total": self.stars_total,
            "forks_total": self.forks_total,
            "stars_since": self.stars_since,
            "timeframe": self.timeframe,
            "built_by": self.built_by,
        }


class GitHubTrendingHTMLParser(html.parser.HTMLParser):
    """HTML Parser for GitHub Trending pages."""

    def __init__(self, timeframe: str = "daily"):
        super().__init__()
        self.timeframe = timeframe
        self.repos: List[TrendingRepo] = []

        # Parser state
        self._in_article = False
        self._article_tags: List[str] = []
        self._current_repo: Dict[str, any] = {}

        # Tracking specific nodes
        self._in_title = False
        self._in_title_link = False
        self._in_desc = False
        self._in_lang = False
        self._in_stars_link = False
        self._in_forks_link = False
        self._in_stars_since = False

        self._current_text: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        ad = dict(attrs)
        classes = ad.get("class", "").split()

        # Check for article start: <article class="Box-row">
        if tag == "article" and "Box-row" in classes:
            self._in_article = True
            self._article_tags = [tag]
            self._current_repo = {
                "name": "",
                "owner": "",
                "repo": "",
                "url": "",
                "description": "",
                "language": "Unknown",
                "language_color": "#8b949e",
                "stars_total": "0",
                "forks_total": "0",
                "stars_since": "0",
                "built_by": [],
            }
            return

        if not self._in_article:
            return

        self._article_tags.append(tag)

        # Title: <h2> or <h3> inside article
        if tag in ("h2", "h3") and any(c in classes for c in ("h3", "h2", "lh-condensed")):
            self._in_title = True

        if self._in_title and tag == "a":
            href = ad.get("href", "")
            cleaned = href.strip("/")
            parts = cleaned.split("/")
            if len(parts) == 2:
                self._in_title_link = True
                self._current_repo["owner"] = parts[0]
                self._current_repo["repo"] = parts[1]
                self._current_repo["name"] = f"{parts[0]}/{parts[1]}"
                self._current_repo["url"] = f"https://github.com/{parts[0]}/{parts[1]}"

        # Description: <p class="col-9 ...">
        if tag == "p" and any(c.startswith("col-") or "color-fg-muted" in c or "my-1" in c for c in classes):
            self._in_desc = True
            self._current_text = []

        # Programming language: <span itemprop="programmingLanguage">
        if tag == "span" and ad.get("itemprop") == "programmingLanguage":
            self._in_lang = True
            self._current_text = []

        # Language color dot
        if tag == "span" and "repo-language-color" in classes:
            style = ad.get("style", "")
            color_match = re.search(r"background-color:\s*([^;]+)", style)
            if color_match:
                self._current_repo["language_color"] = color_match.group(1).strip()

        # Links for stars and forks
        if tag == "a":
            href = ad.get("href", "")
            if href.endswith("/stargazers"):
                self._in_stars_link = True
                self._current_text = []
            elif href.endswith("/forks") or href.endswith("/network/members"):
                self._in_forks_link = True
                self._current_text = []

        # Stars today / this week / this month
        if tag == "span" and "float-sm-right" in classes:
            self._in_stars_since = True
            self._current_text = []

        # Built by contributors
        if tag == "img" and "avatar" in classes:
            alt = ad.get("alt", "")
            if alt.startswith("@"):
                username = alt[1:]
                if username and username not in self._current_repo["built_by"]:
                    self._current_repo["built_by"].append(username)

    def handle_endtag(self, tag: str):
        if not self._in_article:
            return

        if self._in_title and tag in ("h2", "h3"):
            self._in_title = False
            self._in_title_link = False

        if self._in_desc and tag == "p":
            self._in_desc = False
            self._current_repo["description"] = " ".join("".join(self._current_text).split()).strip()
            self._current_text = []

        if self._in_lang and tag == "span":
            self._in_lang = False
            lang = "".join(self._current_text).strip()
            if lang:
                self._current_repo["language"] = lang
            self._current_text = []

        if self._in_stars_link and tag == "a":
            self._in_stars_link = False
            stars = "".join(self._current_text).strip().replace(",", "")
            if stars:
                self._current_repo["stars_total"] = stars
            self._current_text = []

        if self._in_forks_link and tag == "a":
            self._in_forks_link = False
            forks = "".join(self._current_text).strip().replace(",", "")
            if forks:
                self._current_repo["forks_total"] = forks
            self._current_text = []

        if self._in_stars_since and tag == "span":
            self._in_stars_since = False
            since_text = "".join(self._current_text).strip()
            num_match = re.search(r"([\d,]+)\s+stars", since_text)
            if num_match:
                self._current_repo["stars_since"] = num_match.group(1).replace(",", "")
            else:
                self._current_repo["stars_since"] = since_text
            self._current_text = []

        # End of article
        if tag == "article" and self._in_article:
            self._in_article = False
            if self._current_repo.get("name"):
                repo_obj = TrendingRepo(
                    name=self._current_repo["name"],
                    owner=self._current_repo["owner"],
                    repo=self._current_repo["repo"],
                    url=self._current_repo["url"],
                    description=self._current_repo["description"],
                    language=self._current_repo["language"],
                    language_color=self._current_repo["language_color"],
                    stars_total=self._current_repo["stars_total"],
                    forks_total=self._current_repo["forks_total"],
                    stars_since=self._current_repo["stars_since"],
                    timeframe=self.timeframe,
                    built_by=self._current_repo["built_by"],
                )
                self.repos.append(repo_obj)

    def handle_data(self, data: str):
        if not self._in_article:
            return

        if self._in_desc or self._in_lang or self._in_stars_link or self._in_forks_link or self._in_stars_since:
            self._current_text.append(data)


def fetch_trending_html(language: Optional[str] = None, since: str = "daily", timeout: int = 15) -> str:
    """Fetch raw HTML from GitHub Trending page."""
    base_url = "https://github.com/trending"
    if language:
        url = f"{base_url}/{urllib.parse.quote(language)}?since={since}"
    else:
        url = f"{base_url}?since={since}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
        "Cache-Control": "no-cache",
    }

    req = urllib.request.Request(url, headers=headers)
    ctx = get_ssl_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
        return response.read().decode("utf-8", errors="replace")



def parse_trending_html(html_content: str, timeframe: str = "daily") -> List[TrendingRepo]:
    """Parse HTML content and return list of TrendingRepo objects."""
    parser = GitHubTrendingHTMLParser(timeframe=timeframe)
    parser.feed(html_content)
    return parser.repos


def get_trending_repos(
    language: Optional[str] = None,
    since: str = "daily",
    limit: Optional[int] = None,
    timeout: int = 15
) -> List[TrendingRepo]:
    """Fetch and parse trending repositories."""
    html_content = fetch_trending_html(language=language, since=since, timeout=timeout)
    repos = parse_trending_html(html_content, timeframe=since)
    if limit and limit > 0:
        return repos[:limit]
    return repos
