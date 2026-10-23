"""Module for fetching trending GitHub repositories from Hacker News discussions (zero-dependency)."""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple

from src.scraper import TrendingRepo, get_ssl_context


HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
RE_GITHUB_REPO = re.compile(
    r"^https?://(?:www\.)?github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)(?:/.*)?$",
    re.IGNORECASE,
)
EXCLUDED_GITHUB_OWNERS = {
    "features", "blog", "pricing", "trending", "settings", "orgs",
    "about", "security", "enterprise", "topics", "collections", "events", "readme",
}


def parse_hn_story(hit: dict) -> Optional[dict]:
    """Extract GitHub owner, repo, and HN metadata from an Algolia HN hit."""
    story_url = hit.get("url") or ""
    match = RE_GITHUB_REPO.match(story_url.strip())
    if not match:
        return None

    owner = match.group(1).strip()
    repo = match.group(2).strip()

    # Strip trailing .git if present
    if repo.lower().endswith(".git"):
        repo = repo[:-4]

    if owner.lower() in EXCLUDED_GITHUB_OWNERS or not repo:
        return None

    points = hit.get("points") or 0
    comments = hit.get("num_comments") or 0
    title = (hit.get("title") or "").strip()
    object_id = hit.get("objectID") or ""
    hn_url = f"https://news.ycombinator.com/item?id={object_id}" if object_id else ""

    return {
        "owner": owner,
        "repo": repo,
        "name": f"{owner}/{repo}",
        "url": f"https://github.com/{owner}/{repo}",
        "title": title,
        "points": points,
        "comments": comments,
        "hn_url": hn_url,
    }


def get_hn_trending_repos(
    timeframe: str = "weekly",
    limit: int = 10,
    min_points: int = 10,
    query: Optional[str] = None,
    timeout: int = 12,
) -> List[TrendingRepo]:
    """Fetch trending GitHub repositories discussed on Hacker News."""
    now = int(time.time())
    if timeframe == "daily":
        delta = 86400 * 2  # 48 hours to account for timezone and discussion ramp-up
    elif timeframe == "monthly":
        delta = 86400 * 30
    else:  # weekly (default)
        delta = 86400 * 7

    since_timestamp = now - delta

    search_query = f"{query.strip()} github.com" if query and query.strip() else "github.com"
    params = {
        "query": search_query,
        "tags": "story",
        "numericFilters": f"created_at_i>{since_timestamp},points>{min_points}",
        "hitsPerPage": "50",
    }

    req_url = f"{HN_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GitHubTrendingAnalyzer/1.0",
        "Accept": "application/json",
    }

    req = urllib.request.Request(req_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=get_ssl_context()) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as exc:
        # Fallback if Algolia has an issue or network fails
        return []

    hits = data.get("hits", [])
    repos: List[TrendingRepo] = []
    seen = set()

    # Sort hits by points descending to prioritize top-voted projects
    hits_sorted = sorted(hits, key=lambda h: h.get("points") or 0, reverse=True)

    for hit in hits_sorted:
        parsed = parse_hn_story(hit)
        if not parsed:
            continue

        full_name = parsed["name"].lower()
        if full_name in seen:
            continue
        seen.add(full_name)

        # Create a TrendingRepo instance
        repo_obj = TrendingRepo(
            name=parsed["name"],
            owner=parsed["owner"],
            repo=parsed["repo"],
            url=parsed["url"],
            description=parsed["title"] or f"Trending repository on Hacker News ({parsed['name']})",
            language="Unknown",
            language_color="#8b949e",
            stars_total=f"▲ {parsed['points']}",
            forks_total=f"💬 {parsed['comments']}",
            stars_since=str(parsed["points"]),
            timeframe=f"hn_{timeframe}",
            built_by=[],
        )
        # Attach HN metadata for rich display
        repo_obj.hn_points = parsed["points"]
        repo_obj.hn_comments = parsed["comments"]
        repo_obj.hn_url = parsed["hn_url"]
        repo_obj.hn_title = parsed["title"]

        repos.append(repo_obj)
        if len(repos) >= limit:
            break

    return repos
