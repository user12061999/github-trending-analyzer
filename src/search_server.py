"""Local dashboard and GitHub repository search. Standard library only."""
import json
import os
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src.analyzer import analyze_repository
from src.html_dashboard import generate_html_dashboard
from src.scraper import TrendingRepo, get_ssl_context, get_trending_repos
from src.maturity import parse_star_count
from src.watchlist import load_watchlist
from src.growth import get_star_growth


def validate_search(query, limit, mode, language, sort, scope='name'):
    if scope not in ('name', 'content'):
        raise ValueError('Phạm vi tìm kiếm phải là tên project hoặc nội dung README.')
    if not isinstance(query, str) or len(query) > 256:
        raise ValueError('Từ khóa phải là chuỗi tối đa 256 ký tự.')
    if type(limit) is not int or not 1 <= limit <= 30:
        raise ValueError('Số lượng project phải từ 1 đến 30.')
    if mode not in ('any', 'all') or sort not in ('best-match', 'stars', 'updated'):
        raise ValueError('Lựa chọn tìm kiếm không hợp lệ.')
    if not isinstance(language, str) or not re.fullmatch(r'[\w#+. -]{0,40}', language):
        raise ValueError('Ngôn ngữ không hợp lệ.')


def search_github(query, limit=10, mode='all', language='', sort='best-match', scope='name'):
    validate_search(query, limit, mode, language, sort, scope)
    terms = [term.strip() for term in query.split(',') if term.strip()]
    if len(terms) > 6:
        raise ValueError('Dùng tối đa 6 từ khóa, ngăn cách bằng dấu phẩy.')
    q = (' OR ' if mode == 'any' else ' ').join(terms) or 'stars:>0'
    q += (' in:name' if scope == 'name' else ' in:readme') + ' is:public fork:false archived:false'
    if language.strip():
        q += ' language:' + json.dumps(language.strip())
    params = {'q': q, 'per_page': limit, 'order': 'desc'}
    if sort != 'best-match':
        params['sort'] = sort
    elif not terms:
        params['sort'] = 'stars'
    headers = {'User-Agent': 'gh-trending-research', 'Accept': 'application/vnd.github+json'}
    # Always restrict results to public repositories, even with an optional token.
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    request = urllib.request.Request('https://api.github.com/search/repositories?' + urllib.parse.urlencode(params), headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20, context=get_ssl_context()) as response:
            data = json.loads(response.read(4_000_000))
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 429):
            raise RuntimeError('GitHub giới hạn lượt tìm kiếm hoặc từ chối truy cập. Thử lại sau; có thể cấu hình GITHUB_TOKEN ở server.') from None
        if exc.code == 422:
            raise ValueError('GitHub không chấp nhận truy vấn này. Kiểm tra từ khóa và cú pháp bộ lọc.') from None
        raise RuntimeError(f'GitHub trả lỗi HTTP {exc.code}. Thử lại sau.') from None
    repos = []
    for item in data.get('items', [])[:limit]:
        name = item.get('full_name', '')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', name):
            continue
        owner, repo_name = name.split('/')
        repos.append(TrendingRepo(name, owner, repo_name, f'https://github.com/{name}', item.get('description') or '',
                                  item.get('language') or 'Unknown', '#8b949e', str(item.get('stargazers_count', 0)),
                                  str(item.get('forks_count', 0)), '0', 'search'))
    return repos, int(data.get('total_count', 0)), bool(data.get('incomplete_results', False))


def search_and_analyze(payload, use_ai=False, model=None, watchlist=None):
    if not isinstance(payload, dict) or type(payload.get('deep', False)) is not bool:
        raise ValueError('Dữ liệu tìm kiếm không hợp lệ.')
    query, limit = payload.get('query', ''), payload.get('limit', 10)
    language, sort = payload.get('language', ''), payload.get('sort', 'best-match')
    scope = payload.get('scope', 'name')
    validate_search(query, limit, payload.get('mode', 'all'), language, sort, scope)
    timeframe = payload.get('timeframe', 'daily')
    if timeframe not in ('daily', 'weekly', 'monthly'):
        raise ValueError('Kỳ Trending phải là daily, weekly hoặc monthly.')
    trending = not query.strip()
    if trending:
        # Fetch the full Trending page, rank by new stars, then apply the limit.
        repos = get_trending_repos(language=language.strip().lower().replace(' ', '-') or None,
                                   since=timeframe, limit=None)
        total, incomplete = len(repos), False
        repos.sort(key=lambda repo: (-parse_star_count(repo.stars_since), -parse_star_count(repo.stars_total), repo.name.lower()))
        repos = repos[:limit]
    else:
        repos, total, incomplete = search_github(query, limit, payload.get('mode', 'all'), language, sort, scope=scope)
    def analyze(repo):
        result = analyze_repository(repo, deep=payload.get('deep', False), use_ai=use_ai, model=model, watchlist=watchlist)
        if not trending:
            result.velocity_score = 0
            result.velocity_badge = result.velocity_label = ''
            result.why_trending = 'Kết quả GitHub Search theo truy vấn; không phải dữ liệu GitHub Trending.'
        data = result.to_dict()
        if not trending:
            data['growth'] = get_star_growth(result.owner, result.repo)
        return data
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(analyze, repos))
    return {'results': results, 'total_count': total, 'incomplete_results': incomplete,
            'mode': 'trending' if trending else 'search', 'timeframe': timeframe if trending else 'search',
            'scope': scope if not trending else None}


def make_handler(use_ai=False, model=None, deep=False):
    page = generate_html_dashboard([], timeframe='search', search_endpoint='/api/search', default_deep=deep).encode()
    slots = threading.BoundedSemaphore(2)
    watchlist = load_watchlist()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, status, data, content_type='application/json; charset=utf-8'):
            content = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            try:
                self.wfile.write(content)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def allowed(self):
            expected = f'127.0.0.1:{self.server.server_port}'
            return self.headers.get('Host') == expected and self.headers.get('Origin', f'http://{expected}') == f'http://{expected}'

        def do_GET(self):
            if not self.allowed():
                self.send(403, {'error': 'Truy cập local không hợp lệ.'})
            elif self.path == '/':
                self.send(200, page, 'text/html; charset=utf-8')
            elif self.path == '/api/feedback':
                from src.history_db import get_all_feedback
                self.send(200, get_all_feedback())
            elif self.path == '/api/adaptive-watchlist':
                from src.history_db import extract_adaptive_preferences
                self.send(200, extract_adaptive_preferences())
            elif self.path == '/api/knowledge':
                from src.history_db import get_learned_knowledge
                self.send(200, get_learned_knowledge())
            else:
                self.send(404, {'error': 'Không tìm thấy.'})

        def do_POST(self):
            if not self.allowed():
                self.send(403, {'error': 'Chỉ nhận tìm kiếm từ dashboard local.'}); return
            if self.path == '/api/feedback':
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    if not 0 < length <= 4096:
                        raise ValueError('Dữ liệu feedback không hợp lệ.')
                    payload = json.loads(self.rfile.read(length))
                    full_name = payload.get('full_name')
                    if not full_name or not isinstance(full_name, str):
                        raise ValueError('Tên repo không hợp lệ.')
                    from src.history_db import set_repo_feedback
                    result = set_repo_feedback(
                        full_name=full_name,
                        rating=payload.get('rating'),
                        status=payload.get('status'),
                        notes=payload.get('notes'),
                    )
                    self.send(200, result)
                except Exception as exc:
                    self.send(400, {'error': str(exc)})
                return

            if self.path == '/api/sync-watchlist':
                try:
                    from src.history_db import extract_adaptive_preferences
                    from src.watchlist import merge_watchlists
                    prefs = extract_adaptive_preferences()
                    nonlocal watchlist
                    watchlist = merge_watchlists(watchlist, prefs)
                    # Persist to watchlist.json
                    cfg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'watchlist.json')
                    with open(cfg_path, 'w', encoding='utf-8') as f:
                        json.dump(watchlist, f, indent=2, ensure_ascii=False)
                    self.send(200, {'status': 'success', 'watchlist': watchlist, 'added': prefs})
                except Exception as exc:
                    self.send(500, {'error': str(exc)})
                return

            if self.path == '/api/chat':
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    if not 0 < length <= 8192:
                        raise ValueError('Dữ liệu câu hỏi không hợp lệ.')
                    payload = json.loads(self.rfile.read(length))
                    full_name = payload.get('full_name')
                    question = payload.get('question')
                    if not full_name or not question:
                        raise ValueError('Thiếu tên repo hoặc câu hỏi.')
                    from src.repo_chat import ask_repo
                    ans = ask_repo(
                        full_name=full_name,
                        question=question,
                        use_ai=use_ai,
                        model=model,
                    )
                    self.send(200, ans)
                except Exception as exc:
                    self.send(400, {'error': str(exc)})
                return

            if self.path != '/api/search':
                self.send(404, {'error': 'Không tìm thấy.'}); return
            if not slots.acquire(blocking=False):
                self.send(429, {'error': 'Server đang phân tích. Hãy đợi lượt hiện tại hoàn thành.'}); return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 4096:
                    raise ValueError('Dữ liệu tìm kiếm quá lớn hoặc trống.')
                payload = json.loads(self.rfile.read(length))
                self.send(200, search_and_analyze(payload, use_ai, model, watchlist))
            except (ValueError, TypeError) as exc:
                self.send(400, {'error': str(exc)})
            except RuntimeError as exc:
                self.send(502, {'error': str(exc)})
            except Exception:
                self.send(502, {'error': 'Không tải hoặc phân tích được dữ liệu GitHub. Kiểm tra kết nối rồi thử lại.'})
            finally:
                slots.release()
    return Handler


def serve_dashboard(port=8766, use_ai=False, model=None, deep=False, open_browser=True):
    server = ThreadingHTTPServer(('127.0.0.1', port), make_handler(use_ai, model, deep))
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'Dashboard tìm kiếm GitHub: {url}\nNhấn Ctrl+C để dừng server.', flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
