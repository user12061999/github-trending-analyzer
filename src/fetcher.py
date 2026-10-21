"""Module fetching README and repository details from GitHub (zero-dependency)."""

import os
import re
import urllib.error
import urllib.request
from typing import Optional

from src.scraper import get_ssl_context


CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache")


def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_key(owner: str, repo: str) -> str:
    return f"{owner}_{repo}_README.md"


def get_cached_readme(owner: str, repo: str) -> Optional[str]:
    ensure_cache_dir()
    filepath = os.path.join(CACHE_DIR, _cache_key(owner, repo))
    if os.path.isfile(filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception:
            return None
    return None


def save_cached_readme(owner: str, repo: str, content: str):
    ensure_cache_dir()
    filepath = os.path.join(CACHE_DIR, _cache_key(owner, repo))
    try:
        with open(filepath, "w", encoding="utf-8", errors="replace") as f:
            f.write(content)
    except Exception:
        pass


def fetch_repo_readme(owner: str, repo: str, timeout: int = 10, use_cache: bool = True) -> Optional[str]:
    """Fetch README content for a given owner and repository."""
    if use_cache:
        cached = get_cached_readme(owner, repo)
        if cached:
            return cached

    candidate_urls = [
        f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/readme.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/README.rst",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/plain,text/markdown,*/*",
    }

    for url in candidate_urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            ctx = get_ssl_context()
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
                if response.status == 200:

                    content = response.read().decode("utf-8", errors="replace")
                    if content and len(content.strip()) > 20:
                        if use_cache:
                            save_cached_readme(owner, repo, content)
                        return content
        except Exception:
            continue

    return None


def clean_markdown_for_analysis(content: str, max_chars: int = 4000) -> str:
    """Clean markdown text by removing badges, HTML comments, base64 images, and HTML tags."""
    if not content:
        return ""

    # Remove HTML comments <!-- ... -->
    text = re.sub(r"<!--[\s\S]*?-->", "", content)

    # Remove full blocks of <picture>...</picture>, <svg>...</svg>, <video>...</video>, etc.
    text = re.sub(r"<(picture|svg|video|style|script)[^>]*>[\s\S]*?<\/\1>", "", text, flags=re.IGNORECASE)

    # Remove badge images [![...](...)](...) or ![...](...)
    text = re.sub(r"\[!\[.*?\]\(.*?\)\]\(.*?\)", "", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # Remove remaining HTML tags like <source ...>, <img ...>, <p ...>, etc.
    text = re.sub(r"<[^>]+>", " ", text)

    # Clean redundant spaces and empty lines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    cleaned = text.strip()

    if len(cleaned) > max_chars:
        return cleaned[:max_chars] + "\n\n...(đã rút gọn)..."
    return cleaned

