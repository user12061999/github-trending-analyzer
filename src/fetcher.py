"""Module fetching README and repository details from GitHub (zero-dependency)."""

import os
import re
import urllib.error
import urllib.request
import json
from typing import Optional, List, Dict, Any

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



def _release_cache_key(owner: str, repo: str) -> str:
    return f"{owner}_{repo}_release.json"


def get_cached_release(owner: str, repo: str) -> Optional[dict]:
    ensure_cache_dir()
    filepath = os.path.join(CACHE_DIR, _release_cache_key(owner, repo))
    if os.path.isfile(filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def save_cached_release(owner: str, repo: str, data: dict):
    ensure_cache_dir()
    filepath = os.path.join(CACHE_DIR, _release_cache_key(owner, repo))
    try:
        with open(filepath, "w", encoding="utf-8", errors="replace") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def extract_release_highlights(body: str, max_items: int = 5) -> List[str]:
    """Extract clean changelog bullet points from GitHub release notes markdown."""
    if not body:
        return []
    highlights = []
    lines = body.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("-", "*", "•")) and len(stripped) > 5:
            clean_item = stripped.lstrip("-*•").strip()
            clean_item = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", clean_item)
            clean_item = re.sub(r"\s*\([a-f0-9]{7,}\)", "", clean_item).strip()
            if len(clean_item) >= 8 and not clean_item.lower().startswith(("full changelog", "see full")):
                highlights.append(clean_item)
                if len(highlights) >= max_items:
                    break
    return highlights


def fetch_repo_release(owner: str, repo: str, timeout: int = 5, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """Fetch latest release or fallback to latest tag for a repository."""
    if use_cache:
        cached = get_cached_release(owner, repo)
        if cached is not None:
            return cached

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/vnd.github.v3+json",
    }
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]

    ctx = get_ssl_context()

    # 1. Try /releases/latest
    release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    try:
        req = urllib.request.Request(release_url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            if response.status == 200:
                raw_data = json.loads(response.read().decode("utf-8", errors="replace"))
                body = raw_data.get("body") or ""
                highlights = extract_release_highlights(body)
                res = {
                    "tag_name": raw_data.get("tag_name") or "",
                    "name": raw_data.get("name") or raw_data.get("tag_name") or "",
                    "published_at": raw_data.get("published_at") or "",
                    "html_url": raw_data.get("html_url") or f"https://github.com/{owner}/{repo}/releases",
                    "highlights": highlights,
                    "body_snippet": body[:800].strip(),
                    "prerelease": bool(raw_data.get("prerelease")),
                    "is_tag_only": False,
                }
                if use_cache:
                    save_cached_release(owner, repo, res)
                return res
    except urllib.error.HTTPError as e:
        if e.code != 404:
            return None
    except Exception:
        return None

    # 2. Fallback to /tags
    tags_url = f"https://api.github.com/repos/{owner}/{repo}/tags?per_page=1"
    try:
        req = urllib.request.Request(tags_url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            if response.status == 200:
                tags_data = json.loads(response.read().decode("utf-8", errors="replace"))
                if tags_data and isinstance(tags_data, list):
                    first_tag = tags_data[0]
                    tag_name = first_tag.get("name") or ""
                    if tag_name:
                        res = {
                            "tag_name": tag_name,
                            "name": tag_name,
                            "published_at": "",
                            "html_url": f"https://github.com/{owner}/{repo}/releases/tag/{tag_name}",
                            "highlights": [],
                            "body_snippet": "",
                            "prerelease": False,
                            "is_tag_only": True,
                        }
                        if use_cache:
                            save_cached_release(owner, repo, res)
                        return res
    except Exception:
        pass

    return None
