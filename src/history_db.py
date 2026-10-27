"""SQLite History, Memory & Self-Evolving Knowledge Base (Python stdlib).

Stores:
1. Repository analysis snapshots across time (temporal trajectory & backtesting).
2. Human-in-the-loop feedback (ratings, reading/testing status, notes).
3. Self-evolving knowledge base (dynamically learned commercial targets & tech terms).
4. Adaptive preference extraction for personalized watchlists.
"""

import json
import os
import re
import sqlite3
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "history.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get a connection to the SQLite database, creating tables if not exists."""
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    """Initialize database schema."""
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS repo_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            captured_at TEXT NOT NULL,
            stars_total INTEGER DEFAULT 0,
            stars_since INTEGER DEFAULT 0,
            timeframe TEXT DEFAULT 'daily',
            category TEXT,
            maturity_level TEXT,
            velocity_badge TEXT,
            commercial_alternative TEXT,
            match_score INTEGER DEFAULT 0,
            engine_used TEXT DEFAULT 'heuristic',
            analysis_json TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_snapshots_name_date 
        ON repo_snapshots(full_name, captured_at);

        CREATE TABLE IF NOT EXISTS repo_feedback (
            full_name TEXT PRIMARY KEY,
            rating INTEGER DEFAULT 0, -- -1 (dislike), 0 (none), 1 (like)
            status TEXT DEFAULT 'unread', -- 'unread', 'want_to_try', 'tried', 'skipped'
            notes TEXT DEFAULT '',
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS knowledge_base (
            entity_name TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL, -- 'commercial_target', 'tech_term'
            description TEXT DEFAULT '',
            detected_from_repo TEXT DEFAULT '',
            confidence REAL DEFAULT 1.0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS repo_bookmarks (
            full_name TEXT PRIMARY KEY,
            bookmarked_at TEXT NOT NULL,
            tags TEXT DEFAULT '[]',
            notes TEXT DEFAULT '',
            repo_data TEXT DEFAULT '{}'
        );
        """)


def save_snapshot(repo_dict: Dict[str, Any], db_path: Optional[str] = None) -> int:
    """Save an analysis snapshot to historical memory."""
    name = repo_dict.get("name") or f"{repo_dict.get('owner', '')}/{repo_dict.get('repo', '')}"
    if not name or name == "/":
        return 0

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stars_total = int(repo_dict.get("stars_total") or 0)
    stars_since = int(repo_dict.get("stars_since") or 0)
    timeframe = repo_dict.get("timeframe") or "daily"
    category = repo_dict.get("category") or ""
    maturity_level = repo_dict.get("maturity_level") or ""
    velocity_badge = repo_dict.get("velocity_badge") or ""
    commercial_alternative = repo_dict.get("commercial_alternative") or ""
    match_score = int(repo_dict.get("match_score") or 0)
    engine_used = repo_dict.get("engine_used") or "heuristic"
    analysis_json = json.dumps(repo_dict, ensure_ascii=False)

    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("""
            INSERT INTO repo_snapshots (
                full_name, captured_at, stars_total, stars_since, timeframe,
                category, maturity_level, velocity_badge, commercial_alternative,
                match_score, engine_used, analysis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, now, stars_total, stars_since, timeframe,
                category, maturity_level, velocity_badge, commercial_alternative,
                match_score, engine_used, analysis_json
            ))
            return cursor.lastrowid
    finally:
        conn.close()


def get_repo_trajectory(full_name: str, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve trajectory and history for a repository."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute("""
        SELECT captured_at, stars_total, stars_since, timeframe, velocity_badge
        FROM repo_snapshots
        WHERE full_name = ?
        ORDER BY captured_at ASC
        """, (full_name,)).fetchall()

        fb = conn.execute("""
        SELECT rating, status, notes, updated_at
        FROM repo_feedback
        WHERE full_name = ?
        """, (full_name,)).fetchone()

        if not rows:
            return {
                "is_new_entry": True,
                "times_seen": 0,
                "first_seen_at": None,
                "last_seen_at": None,
                "user_rating": fb["rating"] if fb else 0,
                "user_status": fb["status"] if fb else "unread",
                "user_notes": fb["notes"] if fb else "",
            }

        first_seen = rows[0]["captured_at"]
        last_seen = rows[-1]["captured_at"]
        times_seen = len(rows)

        return {
            "is_new_entry": times_seen <= 1,
            "times_seen": times_seen,
            "first_seen_at": first_seen,
            "last_seen_at": last_seen,
            "user_rating": fb["rating"] if fb else 0,
            "user_status": fb["status"] if fb else "unread",
            "user_notes": fb["notes"] if fb else "",
        }
    finally:
        conn.close()


def set_repo_feedback(
    full_name: str,
    rating: Optional[int] = None,
    status: Optional[str] = None,
    notes: Optional[str] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Set or update human-in-the-loop feedback for a repo."""
    valid_statuses = ("unread", "want_to_try", "tried", "skipped")
    if status is not None and status not in valid_statuses:
        raise ValueError(f"Trạng thái không hợp lệ. Phải thuộc: {', '.join(valid_statuses)}")
    if rating is not None and rating not in (-1, 0, 1):
        raise ValueError("Đánh giá rating phải là -1 (dislike), 0 (neutral), hoặc 1 (like)")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    try:
        with conn:
            existing = conn.execute("SELECT rating, status, notes FROM repo_feedback WHERE full_name = ?", (full_name,)).fetchone()
            curr_rating = existing["rating"] if existing else 0
            curr_status = existing["status"] if existing else "unread"
            curr_notes = existing["notes"] if existing else ""

            new_rating = rating if rating is not None else curr_rating
            new_status = status if status is not None else curr_status
            new_notes = notes if notes is not None else curr_notes

            conn.execute("""
            INSERT INTO repo_feedback (full_name, rating, status, notes, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(full_name) DO UPDATE SET
                rating = excluded.rating,
                status = excluded.status,
                notes = excluded.notes,
                updated_at = excluded.updated_at
            """, (full_name, new_rating, new_status, new_notes, now))

            return {
                "full_name": full_name,
                "rating": new_rating,
                "status": new_status,
                "notes": new_notes,
                "updated_at": now
            }
    finally:
        conn.close()


def get_all_feedback(db_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Return all saved feedbacks indexed by full_name."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute("SELECT full_name, rating, status, notes, updated_at FROM repo_feedback").fetchall()
        return {r["full_name"]: dict(r) for r in rows}
    finally:
        conn.close()


def add_learned_knowledge(
    entity_name: str,
    entity_type: str = "commercial_target",
    description: str = "",
    detected_from_repo: str = "",
    confidence: float = 1.0,
    db_path: Optional[str] = None
) -> bool:
    """Store dynamically learned commercial target or tech term into knowledge base."""
    clean_name = entity_name.strip()
    if not clean_name or len(clean_name) < 2:
        return False

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("""
            INSERT INTO knowledge_base (entity_name, entity_type, description, detected_from_repo, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(entity_name) DO UPDATE SET
                description = CASE WHEN excluded.description != '' THEN excluded.description ELSE knowledge_base.description END,
                detected_from_repo = excluded.detected_from_repo,
                confidence = max(knowledge_base.confidence, excluded.confidence)
            """, (clean_name, entity_type, description, detected_from_repo, confidence, now))
            return True
    finally:
        conn.close()


def get_learned_knowledge(entity_type: Optional[str] = None, db_path: Optional[str] = None) -> Dict[str, str]:
    """Retrieve learned knowledge entries (name -> description)."""
    conn = get_connection(db_path)
    try:
        if entity_type:
            rows = conn.execute("SELECT entity_name, description FROM knowledge_base WHERE entity_type = ?", (entity_type,)).fetchall()
        else:
            rows = conn.execute("SELECT entity_name, description FROM knowledge_base").fetchall()
        return {r["entity_name"]: r["description"] for r in rows}
    finally:
        conn.close()


def extract_adaptive_preferences(db_path: Optional[str] = None) -> Dict[str, List[str]]:
    """Analyze liked and bookmarked repositories to automatically extract user preferences.

    Returns suggested keywords, languages, and categories to enrich watchlist.
    """
    conn = get_connection(db_path)
    try:
        # Find all repos where rating == 1 OR status IN ('want_to_try', 'tried')
        feedback_repos = conn.execute("""
        SELECT full_name FROM repo_feedback
        WHERE rating = 1 OR status IN ('want_to_try', 'tried')
        """).fetchall()

        if not feedback_repos:
            return {"keywords": [], "languages": [], "categories": []}

        names = [r["full_name"] for r in feedback_repos]
        placeholders = ",".join("?" for _ in names)

        # Get snapshots for these repos
        snapshots = conn.execute(f"""
        SELECT full_name, category, analysis_json
        FROM repo_snapshots
        WHERE full_name IN ({placeholders})
        ORDER BY id DESC
        """, names).fetchall()

        lang_counter = Counter()
        cat_counter = Counter()
        tech_counter = Counter()

        seen_repos = set()
        for snap in snapshots:
            name = snap["full_name"]
            if name in seen_repos:
                continue
            seen_repos.add(name)

            if snap["category"]:
                cat_counter[snap["category"]] += 1

            if snap["analysis_json"]:
                try:
                    data = json.loads(snap["analysis_json"])
                    lang = data.get("language")
                    if lang and lang.lower() not in ("unknown", ""):
                        lang_counter[lang] += 1
                    for tech in data.get("tech_stack", []):
                        if tech and len(tech) >= 2:
                            tech_counter[tech.lower()] += 1
                except Exception:
                    pass

        # Select top recommendations
        suggested_languages = [lang for lang, count in lang_counter.most_common(5) if count >= 1]
        suggested_categories = [cat for cat, count in cat_counter.most_common(5) if count >= 1]
        suggested_keywords = [tech for tech, count in tech_counter.most_common(10) if count >= 1]

        return {
            "keywords": suggested_keywords,
            "languages": suggested_languages,
            "categories": suggested_categories,
        }
    finally:
        conn.close()



def save_bookmark(
    full_name: str,
    repo_data: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """Save or update a bookmarked repository."""
    if not full_name or not isinstance(full_name, str):
        raise ValueError("Tên repo không hợp lệ.")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection(db_path)
    try:
        with conn:
            existing = conn.execute("SELECT bookmarked_at, tags, notes, repo_data FROM repo_bookmarks WHERE full_name = ?", (full_name,)).fetchone()
            curr_tags = json.loads(existing["tags"]) if (existing and existing["tags"]) else []
            curr_notes = existing["notes"] if existing else ""
            curr_repo_data = json.loads(existing["repo_data"]) if (existing and existing["repo_data"]) else {}
            curr_bm_at = existing["bookmarked_at"] if existing else now

            final_tags = tags if tags is not None else curr_tags
            final_notes = notes if notes is not None else curr_notes
            final_repo_data = repo_data if repo_data is not None else curr_repo_data

            conn.execute("""
            INSERT INTO repo_bookmarks (full_name, bookmarked_at, tags, notes, repo_data)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(full_name) DO UPDATE SET
                tags = excluded.tags,
                notes = excluded.notes,
                repo_data = CASE WHEN excluded.repo_data != '{}' THEN excluded.repo_data ELSE repo_bookmarks.repo_data END
            """, (full_name, curr_bm_at, json.dumps(final_tags, ensure_ascii=False), final_notes, json.dumps(final_repo_data, ensure_ascii=False)))

            return {
                "full_name": full_name,
                "bookmarked_at": curr_bm_at,
                "tags": final_tags,
                "notes": final_notes,
                "repo_data": final_repo_data,
            }
    finally:
        conn.close()


def delete_bookmark(full_name: str, db_path: Optional[str] = None) -> bool:
    """Delete a bookmarked repository."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM repo_bookmarks WHERE full_name = ?", (full_name,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_all_bookmarks(db_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Return all saved bookmarks indexed by full_name."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute("SELECT full_name, bookmarked_at, tags, notes, repo_data FROM repo_bookmarks ORDER BY bookmarked_at DESC").fetchall()
        result = {}
        for r in rows:
            try:
                tags = json.loads(r["tags"]) if r["tags"] else []
            except Exception:
                tags = []
            try:
                repo_data = json.loads(r["repo_data"]) if r["repo_data"] else {}
            except Exception:
                repo_data = {}
            result[r["full_name"]] = {
                "full_name": r["full_name"],
                "bookmarked_at": r["bookmarked_at"],
                "tags": tags,
                "notes": r["notes"] or "",
                "repo_data": repo_data,
            }
        return result
    finally:
        conn.close()
