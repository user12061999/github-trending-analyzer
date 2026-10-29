"""Module fetching README and repository details from GitHub (zero-dependency)."""

import os
import re
import urllib.error
import urllib.request
import json
import datetime
from typing import Optional, List, Dict, Any, Tuple

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


def _pulse_cache_key(owner: str, repo: str) -> str:
    return f"{owner}_{repo}_pulse.json"


def get_cached_pulse(owner: str, repo: str) -> Optional[dict]:
    ensure_cache_dir()
    filepath = os.path.join(CACHE_DIR, _pulse_cache_key(owner, repo))
    if os.path.isfile(filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def save_cached_pulse(owner: str, repo: str, data: dict):
    ensure_cache_dir()
    filepath = os.path.join(CACHE_DIR, _pulse_cache_key(owner, repo))
    try:
        with open(filepath, "w", encoding="utf-8", errors="replace") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def calculate_pulse_status(pushed_at: str) -> Tuple[str, str, str, int]:
    """Calculate commit recency status from pushed_at timestamp.
    Returns (status_key, badge_vi, badge_en, days_since_push).
    """
    if not pushed_at:
        return ("unknown", "⚪ Chưa rõ hoạt động", "⚪ Activity Unknown", -1)

    try:
        clean_ts = pushed_at.replace("Z", "+00:00")
        pushed_date = datetime.datetime.fromisoformat(clean_ts)
        now = datetime.datetime.now(datetime.timezone.utc)
        diff_days = max(0, (now - pushed_date).days)
        diff_hours = max(0, int((now - pushed_date).total_seconds() // 3600))
    except Exception:
        return ("unknown", "⚪ Chưa rõ hoạt động", "⚪ Activity Unknown", -1)

    if diff_days <= 7:
        time_str_vi = f"{diff_hours}h trước" if diff_days == 0 else f"{diff_days} ngày trước"
        time_str_en = f"{diff_hours}h ago" if diff_days == 0 else f"{diff_days}d ago"
        return ("active", f"🟢 Commit {time_str_vi}", f"🟢 Pushed {time_str_en}", diff_days)
    elif diff_days <= 30:
        return ("steady", f"🟡 Commit {diff_days} ngày trước", f"🟡 Pushed {diff_days}d ago", diff_days)
    elif diff_days <= 90:
        return ("slow", f"🟠 Commit {diff_days // 7} tuần trước", f"🟠 Pushed {diff_days // 7}w ago", diff_days)
    else:
        return ("dormant", f"🔴 Ngủ đông ({diff_days} ngày)", f"🔴 Hibernating ({diff_days}d)", diff_days)


def fetch_repo_community_pulse(owner: str, repo: str, timeout: int = 5, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """Fetch community health, commit recency, license, open issues, and top contributors."""
    if use_cache:
        cached = get_cached_pulse(owner, repo)
        if cached is not None:
            return cached

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/vnd.github.v3+json",
    }
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]

    ctx = get_ssl_context()
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        req = urllib.request.Request(repo_url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            if response.status == 200:
                raw = json.loads(response.read().decode("utf-8", errors="replace"))

                pushed_at = raw.get("pushed_at") or ""
                status_key, badge_vi, badge_en, days_since = calculate_pulse_status(pushed_at)

                license_info = raw.get("license") or {}
                license_name = license_info.get("name") or license_info.get("spdx_id") or ""
                license_spdx = license_info.get("spdx_id") or ""

                top_contributors = []
                try:
                    contrib_url = f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=5"
                    c_req = urllib.request.Request(contrib_url, headers=headers)
                    with urllib.request.urlopen(c_req, timeout=timeout, context=ctx) as c_resp:
                        if c_resp.status == 200:
                            c_data = json.loads(c_resp.read().decode("utf-8", errors="replace"))
                            if isinstance(c_data, list):
                                for c in c_data[:5]:
                                    top_contributors.append({
                                        "login": c.get("login") or "",
                                        "avatar_url": c.get("avatar_url") or "",
                                        "contributions": c.get("contributions") or 0,
                                        "html_url": c.get("html_url") or "",
                                    })
                except Exception:
                    pass

                pulse_data = {
                    "last_pushed_at": pushed_at,
                    "created_at": raw.get("created_at") or "",
                    "default_branch": raw.get("default_branch") or "main",
                    "pulse_status": status_key,
                    "pulse_badge_vi": badge_vi,
                    "pulse_badge_en": badge_en,
                    "days_since_push": days_since,
                    "open_issues_count": raw.get("open_issues_count", 0),
                    "watchers_count": raw.get("subscribers_count", 0),
                    "forks_count": raw.get("forks_count", 0),
                    "license_name": license_name,
                    "license_spdx": license_spdx,
                    "top_contributors": top_contributors,
                }
                if use_cache:
                    save_cached_pulse(owner, repo, pulse_data)
                return pulse_data
    except Exception:
        pass

    return None
