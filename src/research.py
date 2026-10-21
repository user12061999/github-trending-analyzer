"""Source-backed research context; no third-party dependencies or code execution."""
import json
import posixpath
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from src.fetcher import clean_markdown_for_analysis
from src.scraper import get_ssl_context

TOPICS = {
    'how_it_works': ('architecture', 'how it works', 'workflow', 'design', 'concept', 'pipeline', 'engine', 'model', 'kiến trúc'),
    'practical_examples': ('usage', 'example', 'tutorial', 'use case', 'demo', 'sử dụng'),
    'limitations': ('limitation', 'warning', 'caveat', 'requirement', 'security', 'known issue', 'disclaimer', 'constraint', 'performance', 'hardware', 'migration'),
    'adoption_notes': ('install', 'quick start', 'quickstart', 'getting started', 'deployment', 'configuration', 'license', 'prerequisite', 'macos', 'windows', 'linux'),
    'comparisons': ('comparison', 'alternative', 'versus', 'benchmark', 'why ', 'difference'),
}


def sections(content):
    """Split Markdown on headings outside fences, preserving code/examples."""
    title, lines, fenced = 'Introduction', [], False
    result = []
    for line in content.splitlines():
        if re.match(r'^\s*(```|~~~)', line):
            fenced = not fenced
        heading = None if fenced else re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if heading:
            if lines:
                result.append((title, '\n'.join(lines).strip()))
            title, lines = heading.group(1), []
        else:
            lines.append(line)
    if lines:
        result.append((title, '\n'.join(lines).strip()))
    return [(t, b) for t, b in result if b.strip()]


def request_text(url, timeout=10):
    request = urllib.request.Request(url, headers={'User-Agent': 'gh-trending-research', 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(request, timeout=timeout, context=get_ssl_context()) as response:
        return response.read(300_000).decode('utf-8', errors='replace')


def linked_documents(readme, owner, repo, branch='HEAD'):
    """Only fetch explicit text-document links inside this repository."""
    found = []
    for target in re.findall(r'\[[^\]\n]+\]\(([^\s)]+)', readme):
        parsed = urllib.parse.urlsplit(target)
        path = urllib.parse.unquote(parsed.path)
        if parsed.scheme or parsed.netloc:
            prefix = f'/{owner}/{repo}/blob/{branch}/'
            if parsed.scheme != 'https' or parsed.netloc != 'github.com' or not path.startswith(prefix):
                continue
            path = path[len(prefix):]
        path = posixpath.normpath(path.lstrip('/'))
        if path.startswith('../') or path == '..' or not path.lower().endswith(('.md', '.rst', '.txt')):
            continue
        if 'readme' in path.lower() or any(x in path.lower() for x in ('contributing', 'code_of_conduct', 'changelog', 'agents.md', 'skill.md')):
            continue
        if path not in found:
            found.append(path)
    def priority(path):
        name = path.lower()
        if any(word in name for word in ('architecture', 'feature', 'performance', 'limitation', 'comparison')):
            return 0
        if any(word in name for word in ('usage', 'install', 'guide', 'quick', 'example')):
            return 1
        return 2
    return sorted(found, key=priority)[:3]


def collect_sources(repo, readme, deep=False):
    sources, gaps = [], []
    fetched_at = datetime.now(timezone.utc).isoformat()
    if readme:
        sources.append({'id': 'S1', 'title': 'README', 'url': repo.url + '#readme', 'content': readme[:80000], 'fetched_at': fetched_at,
                        'freshness': 'fresh fetch requested' if deep else 'cache freshness unknown'})
    else:
        gaps.append('Không tải được README; chưa đủ dữ liệu để phân tích nội dung.')
    if not deep:
        return sources, gaps
    branch = 'HEAD'
    try:
        metadata = json.loads(request_text(f'https://api.github.com/repos/{repo.owner}/{repo.repo}'))
        branch = metadata.get('default_branch') or branch
        facts = {key: metadata.get(key) for key in ('description', 'archived', 'created_at', 'pushed_at', 'homepage', 'topics')}
        facts['license'] = (metadata.get('license') or {}).get('spdx_id')
        sources.append({'id': f'S{len(sources)+1}', 'title': 'GitHub metadata', 'url': repo.url,
                        'content': json.dumps(facts, ensure_ascii=False), 'fetched_at': fetched_at, 'freshness': 'fresh'})
    except Exception as exc:
        gaps.append(f'Không lấy được metadata GitHub ({type(exc).__name__}); chưa xác minh license và trạng thái bảo trì.')
    for path in linked_documents(readme or '', repo.owner, repo.repo, branch):
        url = f'https://raw.githubusercontent.com/{repo.owner}/{repo.repo}/{urllib.parse.quote(branch, safe="")}/{urllib.parse.quote(path, safe="/")}'
        try:
            content = request_text(url)
            sources.append({'id': f'S{len(sources)+1}', 'title': path, 'url': url, 'content': content[:60000], 'fetched_at': fetched_at, 'freshness': 'fresh'})
        except Exception as exc:
            gaps.append(f'Không đọc được tài liệu {path} ({type(exc).__name__}).')
    return sources, gaps


def extract_research(sources):
    """Return verbatim section evidence rather than synthetic feature claims."""
    result = {topic: [] for topic in TOPICS}
    result['evidence'] = []
    result['research_gaps'] = []
    for source in sources:
        if source['title'] == 'GitHub metadata':
            result['adoption_notes'].append(f"Metadata GitHub [{source['id']}]: {source['content']}")
            continue
        clean = clean_markdown_for_analysis(source['content'], max_chars=80000)
        for title, body in sections(clean):
            for topic, words in TOPICS.items():
                if any(word in (source['title'] if title == 'Introduction' else title).lower() for word in words) and len(result[topic]) < 3:
                    excerpt = body[:1600]
                    result[topic].append(f"Trích tài liệu — {title} [{source['id']}]:\n{excerpt}")
                    result['evidence'].append({'source_id': source['id'], 'section': title, 'quote': excerpt, 'topic': topic})
    for topic, items in result.items():
        if topic in TOPICS and not items:
            result['research_gaps'].append(f'Chưa tìm thấy bằng chứng cho mục {topic} trong các nguồn đã đọc.')
    return result


def research_context(sources, budget=20000):
    """Allocate context across sources and relevant sections, not only README prefix."""
    if not sources:
        return 'Không có tài liệu nguồn.'
    chunks = []
    allowance = budget // len(sources)
    for source in sources:
        clean = clean_markdown_for_analysis(source['content'], max_chars=80000)
        parts = sections(clean)
        important = [(t, b) for t, b in parts if any(w in t.lower() for words in TOPICS.values() for w in words) or 'feature' in t.lower()]
        others = [(t, b) for t, b in parts if (t, b) not in important]
        selected = others[:1] + important + others[1:]
        per_section = max(300, allowance // max(1, len(selected)))
        text = '\n\n'.join(f'## {t}\n{b[:per_section]}' for t, b in selected)
        chunks.append(f"SOURCE {source['id']} | {source['title']} | {source['url']}\n{text[:allowance]}")
    return '\n\n'.join(chunks)
