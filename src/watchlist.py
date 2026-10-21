"""Watchlist & Personalization module for GitHub Trending Analyzer.

Allows users to define custom keywords, preferred languages, and priority categories
in `watchlist.json` or via CLI `--match` to calculate a 0-100% Match Score.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_WATCHLIST_FILE = "watchlist.json"


def load_watchlist(config_path: Optional[str] = None) -> Dict[str, List[str]]:
    """Load user preferences from a JSON config file."""
    path = config_path or DEFAULT_WATCHLIST_FILE
    if not os.path.isabs(path):
        # Resolve relative to current working directory or script directory
        cwd_path = os.path.abspath(path)
        if os.path.exists(cwd_path):
            path = cwd_path
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            fallback_path = os.path.join(base_dir, path)
            if os.path.exists(fallback_path):
                path = fallback_path

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "keywords": [str(k).strip() for k in data.get("keywords", []) if str(k).strip()],
                    "languages": [str(l).strip() for l in data.get("languages", []) if str(l).strip()],
                    "categories": [str(c).strip() for c in data.get("categories", []) if str(c).strip()],
                }
        except Exception:
            pass

    return {"keywords": [], "languages": [], "categories": []}


def parse_match_argument(match_str: Optional[str]) -> Dict[str, List[str]]:
    """Parse a comma-separated match string (e.g., 'agent,rust,security') into a watchlist dict."""
    if not match_str:
        return {"keywords": [], "languages": [], "categories": []}
    tokens = [t.strip() for t in match_str.split(",") if t.strip()]
    return {
        "keywords": tokens,
        "languages": [],
        "categories": [],
    }


def merge_watchlists(primary: Dict[str, List[str]], secondary: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Merge two watchlists without duplicates."""
    return {
        "keywords": list(dict.fromkeys(primary.get("keywords", []) + secondary.get("keywords", []))),
        "languages": list(dict.fromkeys(primary.get("languages", []) + secondary.get("languages", []))),
        "categories": list(dict.fromkeys(primary.get("categories", []) + secondary.get("categories", []))),
    }


def compute_repo_match_score(
    name: str,
    description: str,
    language: str,
    category: str,
    extra_text: str = "",
    watchlist: Optional[Dict[str, List[str]]] = None,
) -> Tuple[int, List[str]]:
    """Compute a match score (0-100%) and return the matched items.

    Scoring formula:
    - Keywords (up to 50 pts): 15 pts per matched keyword, capped at 50.
    - Preferred Language (25 pts): exact/case-insensitive match with watchlist languages.
    - Priority Category (25 pts): match with watchlist categories.
    """
    if not watchlist:
        return 0, []

    keywords = watchlist.get("keywords", [])
    languages = watchlist.get("languages", [])
    categories = watchlist.get("categories", [])

    if not keywords and not languages and not categories:
        return 0, []

    score = 0
    matched: List[str] = []

    # Combined searchable text
    search_corpus = f"{name} {description} {category} {extra_text}".lower()

    # 1. Keywords matching (Max 50 points)
    matched_keywords_count = 0
    for kw in keywords:
        kw_clean = kw.lower().strip()
        if not kw_clean:
            continue
        # Use regex word boundary for short keywords (< 4 chars) to avoid false positives
        if len(kw_clean) <= 3:
            pattern = rf"\b{re.escape(kw_clean)}\b"
            if re.search(pattern, search_corpus):
                matched.append(kw)
                matched_keywords_count += 1
        else:
            if kw_clean in search_corpus:
                matched.append(kw)
                matched_keywords_count += 1

    keyword_points = min(50, matched_keywords_count * 15)
    score += keyword_points

    # 2. Language matching (25 points)
    if language:
        lang_lower = language.lower().strip()
        for pref_lang in languages:
            if lang_lower == pref_lang.lower().strip():
                score += 25
                matched.append(f"Lang:{pref_lang}")
                break

    # 3. Category matching (25 points)
    if category:
        cat_lower = category.lower().strip()
        for pref_cat in categories:
            if pref_cat.lower().strip() in cat_lower or cat_lower in pref_cat.lower().strip():
                score += 25
                matched.append(f"Cat:{pref_cat}")
                break

    final_score = min(100, score)
    return final_score, matched
