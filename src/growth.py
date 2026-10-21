"""Aggregate public GitHub star history without downloading user identities."""
import json
import os
import re
import threading
import time
import urllib.request
from datetime import datetime, timedelta, timezone

from src.scraper import get_ssl_context

_cache = {}
_lock = threading.Lock()


def aggregate_history(history, today):
    if not isinstance(history, list) or not history:
        raise ValueError('Missing star history')
    days = {}
    for bucket in history:
        if not isinstance(bucket, dict) or type(bucket.get('week')) is not int:
            raise ValueError('Invalid week')
        values = bucket.get('days')
        if not isinstance(values, list) or len(values) != 7 or any(type(n) is not int or n < 0 for n in values):
            raise ValueError('Invalid daily counts')
        start = datetime.fromtimestamp(bucket['week'], timezone.utc).date()
        for offset, count in enumerate(values):
            day = start + timedelta(days=offset)
            if day in days:
                raise ValueError('Overlapping weeks')
            days[day] = count
    result = {}
    for label, length in [('daily', 1), ('weekly', 7), ('monthly', 30)]:
        window = [today - timedelta(days=i) for i in range(length)]
        result[label] = sum(days[d] for d in window) if all(d in days for d in window) else None
    return result


def get_star_growth(owner, repo):
    today = datetime.now(timezone.utc).date()
    key = (owner.lower(), repo.lower(), today)
    with _lock:
        cached = _cache.get(key)
        if cached and time.monotonic() - cached[0] < 600:
            return dict(cached[1])
    result = {'daily': None, 'weekly': None, 'monthly': None,
              'source': f'https://api.github.com/repos/{owner}/{repo}/stargazers/history',
              'fetched_at': datetime.now(timezone.utc).isoformat(),
              'note': 'Stars mới được thêm, không trừ lượt bỏ star. Hôm nay chưa kết thúc; ranh giới ngày của GitHub có thể lệch UTC.'}
    try:
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', f'{owner}/{repo}'):
            raise ValueError('Invalid repository')
        headers = {'User-Agent': 'gh-trending-research', 'Accept': 'application/vnd.github+json',
                   'X-GitHub-Api-Version': '2026-03-10'}
        if os.environ.get('GITHUB_TOKEN'):
            headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
        request = urllib.request.Request(result['source'] + '?per_page=6&page=1', headers=headers)
        with urllib.request.urlopen(request, timeout=10, context=get_ssl_context()) as response:
            result.update(aggregate_history(json.loads(response.read(100_000)), today))
        result['status'] = 'available' if result['daily'] is not None else 'unavailable'
    except (OSError, ValueError, TypeError, OverflowError):
        result['status'] = 'unavailable'
    with _lock:
        # Bound memory in the long-running local server.
        if len(_cache) >= 1000:
            _cache.clear()
        _cache[key] = (time.monotonic(), dict(result))
    return result
