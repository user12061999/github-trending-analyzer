"""HTML Dashboard Generator for GitHub Trending Analyzer (zero external dependencies)."""

import json
import os
import webbrowser
from datetime import datetime
from typing import List

from src.analyzer import RepoAnalysis


def generate_html_dashboard(analyses: List[RepoAnalysis], timeframe: str = "daily", language: str = None, search_endpoint: str = None, default_deep: bool = False) -> str:
    """Generate a modern, responsive single-file HTML dashboard with filters, bilingual toggle, and quick run."""
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lang_display = language.capitalize() if language else "Tất cả ngôn ngữ"
    time_map = {"search": "GitHub Search", "daily": "Hôm nay", "weekly": "Tuần này", "monthly": "Tháng này"}
    time_display = time_map.get(timeframe, timeframe)

    # Prepare JSON data for client-side search/filtering
    data_json = json.dumps([a.to_dict() for a in analyses], ensure_ascii=False).replace("<", "\\u003c")

    endpoint_json = json.dumps(search_endpoint).replace("<", "\\u003c")
    search_help = "Để trống từ khóa: lấy GitHub Trending, xếp theo stars mới giảm dần. Có từ khóa: tìm bằng GitHub Search. Tối đa 30 project mỗi lượt." if search_endpoint else f"Tìm trong {len(analyses)} project đã tải. Mở tìm kiếm GitHub bằng ./trending --serve."
    html = rf"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Trending Analyzer — Dashboard</title>
    <style>
        :root {{
            --bg-main: #0d1117;
            --bg-card: #161b22;
            --bg-header: #090d12;
            --border: #30363d;
            --border-hover: #58a6ff;
            --text-main: #c9d1d9;
            --text-muted: #8b949e;
            --text-bright: #f0f6fc;
            --accent-blue: #58a6ff;
            --accent-green: #3fb950;
            --accent-purple: #bc8cff;
            --accent-yellow: #d29922;
            --accent-red: #f85149;
            --radius: 10px;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
            line-height: 1.6;
            padding: 24px;
        }}
        .container {{
            max-width: 1280px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 28px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }}
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}
        h1 {{
            color: var(--text-bright);
            font-size: 1.8rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .badge-time {{ background: rgba(210, 153, 34, 0.2); color: var(--accent-yellow); border: 1px solid var(--accent-yellow); }}
        .badge-lang {{ background: rgba(63, 185, 80, 0.2); color: var(--accent-green); border: 1px solid var(--accent-green); }}
        .badge-count {{ background: rgba(88, 166, 255, 0.2); color: var(--accent-blue); border: 1px solid var(--accent-blue); }}
        
        .lang-selector-box {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(22, 27, 34, 0.95);
            border: 1.5px solid var(--accent-blue);
            border-radius: 20px;
            padding: 4px 12px;
            box-shadow: 0 2px 10px rgba(88, 166, 255, 0.2);
            transition: all 0.2s ease;
        }}
        .lang-selector-box:hover {{
            border-color: #79c0ff;
            box-shadow: 0 2px 14px rgba(88, 166, 255, 0.35);
        }}
        .lang-label {{
            font-size: 0.82rem;
            color: var(--text-muted);
            font-weight: 600;
            white-space: nowrap;
        }}
        .lang-dropdown {{
            background: transparent;
            border: none;
            color: var(--text-bright);
            font-size: 0.85rem;
            font-weight: 700;
            cursor: pointer;
            outline: none;
            padding: 2px 4px;
        }}
        .lang-dropdown option {{
            background: #161b22;
            color: #f0f6fc;
        }}

        [hidden] {{ display: none !important; }}
        .search-button:disabled {{ opacity: .65; cursor: wait; }}
        .search-form {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: end; margin-top: 20px; }}
        .search-field {{ display: flex; flex-direction: column; gap: 6px; }}
        .keyword-field {{ flex: 1; min-width: min(280px, 100%); }}
        .search-field label {{ color: var(--text-muted); font-size: .85rem; }}
        .search-field input, .search-field select {{ padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-main); color: var(--text-bright); font: inherit; }}
        .search-field input:focus, .search-field select:focus {{ outline: 2px solid var(--accent-blue); outline-offset: 2px; }}
        .limit-field input {{ width: 140px; }}
        .search-button {{ padding: 11px 18px; border: 1px solid var(--accent-blue); border-radius: 8px; background: var(--accent-blue); color: #0d1117; font: inherit; font-weight: 600; cursor: pointer; }}
        .reset-button {{ background: transparent; color: var(--text-bright); border-color: var(--border); }}
        .search-help, .results-summary {{ font-size: .85rem; color: var(--text-muted); margin-top: 10px; }}
        .results-summary {{ color: var(--text-bright); }}
        @media (max-width: 600px) {{
            body {{ padding: 12px; }}
            header {{ padding: 18px; }}
            .keyword-field {{ flex-basis: 100%; }}
            .search-button {{ flex-grow: 1; }}
        }}
        .controls {{
            display: flex;
            gap: 12px;
            margin-top: 20px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .select-filter {{
            padding: 10px 14px;
            background: #0d1117;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-bright);
            font-size: 0.92rem;
            outline: none;
            cursor: pointer;
        }}
        .checkbox-filter {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: #0d1117;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 9px 14px;
            color: var(--accent-yellow);
            font-size: 0.9rem;
            cursor: pointer;
            user-select: none;
        }}

        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 20px;
        }}
        .repo-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 22px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
        }}
        .repo-card:hover {{
            transform: translateY(-3px);
            border-color: var(--border-hover);
            box-shadow: 0 8px 24px rgba(88, 166, 255, 0.15);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
            gap: 12px;
        }}
        .repo-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--accent-blue);
            text-decoration: none;
            word-break: break-all;
        }}
        .repo-title:hover {{
            text-decoration: underline;
        }}
        .stars-pill {{
            background: rgba(63, 185, 80, 0.15);
            color: var(--accent-green);
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            white-space: nowrap;
        }}
        
        .pill-tag {{
            font-size: 0.76rem;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .tag-category {{ color: var(--accent-purple); background: rgba(188, 140, 255, 0.12); border: 1px solid rgba(188, 140, 255, 0.3); }}
        .tag-velocity-breakout {{ color: #f85149; background: rgba(248, 81, 73, 0.15); border: 1px solid #f85149; }}
        .tag-velocity-high {{ color: #d29922; background: rgba(210, 153, 34, 0.15); border: 1px solid #d29922; }}
        .tag-velocity-giant {{ color: #58a6ff; background: rgba(88, 166, 255, 0.15); border: 1px solid #58a6ff; }}
        .tag-maturity-prod {{ color: #3fb950; background: rgba(63, 185, 80, 0.15); border: 1px solid #3fb950; }}
        .tag-maturity-beta {{ color: #d29922; background: rgba(210, 153, 34, 0.15); border: 1px solid #d29922; }}
        .tag-maturity-exp {{ color: #f85149; background: rgba(248, 81, 73, 0.15); border: 1px solid #f85149; }}
        .tag-match {{ color: #f0883e; background: rgba(240, 136, 62, 0.15); border: 1px solid #f0883e; font-weight: bold; }}
        .tag-alternative {{ color: #d2a8ff; background: rgba(210, 168, 255, 0.15); border: 1px solid #bc8cff; font-weight: bold; }}
        .tag-new-entry {{ color: #3fb950; background: rgba(63, 185, 80, 0.15); border: 1px solid rgba(63, 185, 80, 0.4); }}
        .tag-returning {{ color: #58a6ff; background: rgba(88, 166, 255, 0.15); border: 1px solid rgba(88, 166, 255, 0.4); }}
        .tag-repo-type {{ color: #79c0ff; background: rgba(56, 139, 253, 0.15); border: 1px solid rgba(56, 139, 253, 0.4); }}
        .tag-grounding {{ color: #56d364; background: rgba(46, 160, 67, 0.15); border: 1px solid rgba(46, 160, 67, 0.4); font-weight: 600; }}
        .tech-pill {{ color: #8b949e; background: rgba(110, 118, 129, 0.2); font-size: 0.75rem; padding: 2px 6px; border-radius: 6px; }}

        .feedback-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(13, 17, 23, 0.7);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 6px 10px;
            margin-bottom: 12px;
            gap: 8px;
        }}
        .rating-buttons {{
            display: flex;
            gap: 6px;
        }}
        .btn-rate {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-rate:hover {{
            border-color: var(--text-bright);
            color: var(--text-bright);
        }}
        .btn-rate.active[data-action="like"] {{
            background: rgba(63, 185, 80, 0.25);
            border-color: var(--accent-green);
            color: #3fb950;
        }}
        .btn-rate.active[data-action="dislike"] {{
            background: rgba(248, 81, 73, 0.25);
            border-color: var(--accent-red);
            color: #f85149;
        }}
        .status-select {{
            background: #090d12;
            border: 1px solid var(--border);
            color: var(--text-main);
            border-radius: 4px;
            padding: 3px 6px;
            font-size: 0.8rem;
            cursor: pointer;
        }}
        .status-select:focus {{
            border-color: var(--accent-blue);
            outline: none;
        }}
        .btn-chat {{
            background: transparent;
            border: 1px solid var(--accent-blue);
            color: var(--accent-blue);
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-chat:hover {{
            background: rgba(88, 166, 255, 0.2);
            color: #fff;
        }}

        .section-title {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin: 12px 0 4px 0;
            font-weight: 700;
        }}
        .core-purpose {{
            background: rgba(22, 27, 34, 0.8);
            border-left: 3px solid var(--accent-yellow);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.92rem;
            color: var(--text-bright);
            margin-bottom: 12px;
            line-height: 1.5;
        }}
        .quick-run-box {{
            background: #090d12;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 0.82rem;
            color: #58a6ff;
            gap: 8px;
        }}
        .quick-run-code {{
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .btn-copy {{
            background: #21262d;
            border: 1px solid #30363d;
            color: #c9d1d9;
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 0.72rem;
            cursor: pointer;
            flex-shrink: 0;
            transition: all 0.2s;
        }}
        .btn-copy:hover {{
            background: #30363d;
            color: #fff;
        }}
        .features-list {{
            list-style: none;
            margin-bottom: 12px;
        }}
        .features-list li {{
            font-size: 0.88rem;
            padding: 3px 0;
            position: relative;
            padding-left: 18px;
            line-height: 1.45;
        }}
        .features-list li::before {{
            content: "•";
            color: var(--accent-green);
            position: absolute;
            left: 4px;
            font-weight: bold;
        }}
        .audience {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}
        .card-footer {{
            border-top: 1px solid var(--border);
            padding-top: 14px;
            margin-top: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
        }}
        .meta-stats {{
            display: flex;
            gap: 12px;
            color: var(--text-muted);
        }}
        .btn-view {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-bright);
            padding: 5px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.82rem;
            transition: all 0.2s;
        }}
        .btn-view:hover {{
            background: var(--accent-blue);
            color: #000;
            border-color: var(--accent-blue);
        }}
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
            font-size: 1.1rem;
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-top">
                <div>
                    <h1 id="mainTitle">🔥 GitHub Trending Analyzer</h1>
                    <p id="mainSubtitle" style="color: var(--text-muted); margin-top: 6px; font-size: 0.92rem;">
                        Tự động phân tích tác dụng cốt lõi, tốc độ bứt phá, độ hoàn thiện và đề xuất theo sở thích của bạn.
                    </p>
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
                    <div class="lang-selector-box">
                        <label for="langSelect" class="lang-label">🌐 Ngôn ngữ / Lang:</label>
                        <select id="langSelect" class="lang-dropdown" onchange="setLanguage(this.value)" aria-label="Select language">
                            <option value="vi">🇻🇳 Tiếng Việt</option>
                            <option value="en">🇬🇧 English</option>
                        </select>
                    </div>
                    <span id="sourceBadge" class="badge badge-time">📅 {time_display}</span>
                    <span id="langBadge" class="badge badge-lang">💻 {lang_display}</span>
                    <span id="loadedCount" class="badge badge-count">📦 {len(analyses)} dự án</span>
                </div>
            </div>

            <form id="searchForm" class="search-form">
                <div class="search-field keyword-field">
                    <label id="lblSearchInput" for="searchInput">Từ khóa</label>
                    <input type="search" id="searchInput" placeholder="Ví dụ: agent, voice, Unity" autocomplete="off" aria-describedby="searchHelp">
                </div>
                <div class="search-field" {'hidden' if not search_endpoint else ''}>
                    <label id="lblSearchScope" for="searchScope">Tìm kiếm theo</label>
                    <select id="searchScope">
                        <option id="optScopeName" value="name">Tên project</option>
                        <option id="optScopeContent" value="content">Từ khóa bên trong project (README)</option>
                    </select>
                </div>
                <div class="search-field limit-field">
                    <label id="lblResultLimit" for="resultLimit">Số lượng project</label>
                    <input type="number" id="resultLimit" min="1" max="30" step="1" value="10" required>
                </div>
                <div class="search-field">
                    <label id="lblKeywordMode" for="keywordMode">Cách khớp từ khóa</label>
                    <select id="keywordMode">
                        <option id="optModeAll" value="all">Khớp tất cả từ khóa</option>
                        <option id="optModeAny" value="any">Khớp ít nhất một từ khóa</option>
                    </select>
                </div>
                <div class="search-field" {'hidden' if not search_endpoint else ''}>
                    <label id="lblGithubLanguage" for="githubLanguage">Ngôn ngữ</label>
                    <input id="githubLanguage" placeholder="Python, Rust, C#..." maxlength="40" style="width:170px">
                </div>
                <div class="search-field" {'hidden' if not search_endpoint else ''}>
                    <label id="lblGithubSort" for="githubSort">Sắp xếp khi có từ khóa</label>
                    <select id="githubSort">
                        <option id="optSortMatch" value="best-match">Phù hợp nhất</option>
                        <option id="optSortStars" value="stars">Nhiều stars nhất</option>
                        <option id="optSortUpdated" value="updated">Cập nhật gần nhất</option>
                    </select>
                </div>
                <div class="search-field" {'hidden' if not search_endpoint else ''}>
                    <label id="lblTrendingPeriod" for="trendingPeriod">Kỳ Trending (khi từ khóa trống)</label>
                    <select id="trendingPeriod">
                        <option id="optPeriodDaily" value="daily">Hôm nay</option>
                        <option id="optPeriodWeekly" value="weekly">Tuần này</option>
                        <option id="optPeriodMonthly" value="monthly">Tháng này</option>
                    </select>
                </div>
                <label id="lblDeepContainer" {'hidden' if not search_endpoint else ''}><input id="deepResearch" type="checkbox" {'checked' if default_deep else ''}> <span id="lblDeepText">Phân tích sâu (chậm hơn)</span></label>
                <button id="searchButton" type="submit" class="search-button">🔍 Tìm kiếm</button>
                <button type="button" id="resetSearch" class="search-button reset-button">Xóa bộ lọc</button>
            </form>
            <p id="searchHelp" class="search-help">{search_help}</p>
            <p id="searchStatus" class="search-help" role="status" aria-live="polite"></p>
            <p id="searchError" class="search-help" role="alert" style="color:var(--accent-red)"></p>
            <p id="resultsSummary" class="results-summary" role="status" aria-live="polite"></p>
            <div class="controls">
                <select id="categoryFilter" class="select-filter" onchange="filterCards()">
                    <option value="">Tất cả phân loại</option>
                </select>
                <select id="repoTypeFilter" class="select-filter" onchange="filterCards()">
                    <option value="">Tất cả loại project</option>
                    <option value="tool_app">🛠️ Tool / App</option>
                    <option value="library_sdk">📦 Library / SDK</option>
                    <option value="ai_model">🧠 AI Model / Weights</option>
                    <option value="course_tutorial">📚 Khóa học / Tài liệu</option>
                    <option value="awesome_list">📋 Awesome List</option>
                    <option value="dataset_benchmark">📊 Dataset / Benchmark</option>
                </select>
                <select id="maturityFilter" class="select-filter" onchange="filterCards()">
                    <option value="">Tất cả độ hoàn thiện</option>
                    <option value="production">🟢 Production Ready</option>
                    <option value="beta">🟡 Beta / Active Dev</option>
                    <option value="experimental">🟠 Experimental</option>
                </select>
                <select {'hidden' if search_endpoint else ''} id="velocityFilter" class="select-filter" onchange="filterCards()">
                    <option value="">Tất cả tốc độ tăng trưởng</option>
                    <option value="breakout">🔥 Siêu bứt phá (Breakout)</option>
                    <option value="velocity">⚡ Tăng trưởng nhanh (High Velocity)</option>
                    <option value="giant">🏛️ Dự án kinh điển (Established)</option>
                </select>
                <select id="statusFilter" class="select-filter" onchange="filterCards()">
                    <option value="">Tất cả trạng thái</option>
                    <option value="want_to_try">🔖 Muốn thử</option>
                    <option value="tried">✅ Đã thử</option>
                    <option value="skipped">⏭️ Bỏ qua</option>
                    <option value="liked">👍 Đã Like</option>
                </select>
                <label class="checkbox-filter">
                    <input type="checkbox" id="watchlistOnly" onchange="filterCards()"> <span id="lblWatchlistText">⭐ Khớp sở thích (>0%)</span>
                </label>
                <label class="checkbox-filter" style="color: #d2a8ff;">
                    <input type="checkbox" id="altOnly" onchange="filterCards()"> <span id="lblAltText">💡 Thay thế thương mại</span>
                </label>
                <button type="button" id="syncWatchlistBtn" class="btn-copy" style="background:#238636;color:#fff;border-color:#2ea043;padding:8px 12px;font-size:0.85rem;" title="Học sở thích từ các repo bạn đánh giá cao" {'hidden' if not search_endpoint else ''}>🧠 Đồng bộ sở thích</button>
            </div>
        </header>

        <div id="cardsGrid" class="cards-grid"></div>
        <div id="emptyState" class="empty-state">Không tìm thấy repository nào phù hợp với bộ lọc hiện tại.</div>
    </div>

    <script>
        let reposData = {data_json};
        const searchEndpoint = {endpoint_json};
        let githubTotal = null;
        let resultMode = 'search';
        let searching = false;

        // Internationalization State & Dictionaries
        let currentLang = localStorage.getItem('gh_trending_dashboard_lang') || 'vi';

        const I18N = {{
            vi: {{
                mainTitle: "🔥 GitHub Trending Analyzer",
                mainSubtitle: "Tự động phân tích tác dụng cốt lõi, tốc độ bứt phá, độ hoàn thiện và đề xuất theo sở thích của bạn.",
                countBadge: (n) => `📦 ${{n}} dự án`,
                langBadge: (l) => `💻 ${{l || 'Tất cả ngôn ngữ'}}`,
                timeLabels: {{ daily: 'Hôm nay', weekly: 'Tuần này', monthly: 'Tháng này', search: 'GitHub Search' }},
                lblSearchInput: "Từ khóa",
                searchPlaceholderContent: "Ví dụ: voice cloning, rag, image generation",
                searchPlaceholderName: "Ví dụ: VoiceStudio, OpenShell",
                searchPlaceholderDefault: "Ví dụ: agent, voice, Unity",
                lblSearchScope: "Tìm kiếm theo",
                optScopeName: "Tên project",
                optScopeContent: "Từ khóa bên trong project (README)",
                lblResultLimit: "Số lượng project",
                lblKeywordMode: "Cách khớp từ khóa",
                optModeAll: "Khớp tất cả từ khóa",
                optModeAny: "Khớp ít nhất một từ khóa",
                lblGithubLanguage: "Ngôn ngữ",
                lblGithubSort: "Sắp xếp khi có từ khóa",
                optSortMatch: "Phù hợp nhất",
                optSortStars: "Nhiều stars nhất",
                optSortUpdated: "Cập nhật gần nhất",
                lblTrendingPeriod: "Kỳ Trending (khi từ khóa trống)",
                optPeriodDaily: "Hôm nay",
                optPeriodWeekly: "Tuần này",
                optPeriodMonthly: "Tháng này",
                lblDeepText: "Phân tích sâu (chậm hơn)",
                searchBtn: "🔍 Tìm kiếm",
                searchBtnSearching: "Đang tìm kiếm…",
                resetBtn: "Xóa bộ lọc",
                searchHelpDefault: (len, hasEndpoint) => hasEndpoint ? "Để trống từ khóa: lấy GitHub Trending, xếp theo stars mới giảm dần. Có từ khóa: tìm bằng GitHub Search. Tối đa 30 project mỗi lượt." : `Tìm trong ${{len}} project đã tải. Mở tìm kiếm GitHub bằng ./trending --serve.`,
                searchHelpEmpty: "Để trống từ khóa: lấy GitHub Trending, xếp theo stars mới giảm dần. Tối đa 30 project mỗi lượt.",
                searchHelpContent: "Tìm từ khóa trong README của project trên GitHub. Nhiều từ khóa ngăn cách bằng dấu phẩy.",
                searchHelpName: "Tìm từ khóa trong tên repository trên GitHub. Nhiều từ khóa ngăn cách bằng dấu phẩy.",
                searchStatusSearching: "Đang tìm trên GitHub và đọc tài liệu project. Phân tích sâu có thể mất vài phút.",
                searchStatusTrendingDone: "Đã lấy Trending, sắp xếp theo số stars mới từ cao xuống thấp.",
                searchStatusSearchDone: "Đã tìm và phân tích xong.",
                searchStatusIncomplete: "GitHub trả kết quả chưa đầy đủ; có thể thử lại với truy vấn cụ thể hơn.",
                searchStatusError: "Tìm kiếm chưa hoàn thành; danh sách trước đó được giữ lại.",
                filterCategoryAll: "Tất cả phân loại",
                filterRepoTypeAll: "Tất cả loại project",
                filterMaturityAll: "Tất cả độ hoàn thiện",
                filterVelocityAll: "Tất cả tốc độ tăng trưởng",
                filterStatusAll: "Tất cả trạng thái",
                lblWatchlistText: "⭐ Khớp sở thích (>0%)",
                lblAltText: "💡 Thay thế thương mại",
                syncWatchlist: "🧠 Đồng bộ sở thích",
                emptyState: "Không tìm thấy repository nào phù hợp với bộ lọc hiện tại.",
                summaryText: (vis, filteredLen, totalLen, ghTotal, mode) => `Hiển thị ${{vis}} / ${{filteredLen}} kết quả phù hợp · ${{totalLen}} project đã tải${{ghTotal === null ? "" : (mode === 'trending' ? ` / ${{ghTotal}} project trong danh sách Trending` : ` / ${{ghTotal}} kết quả GitHub`)}}`,
                
                // Card Titles & Details
                corePurposeTitle: "🎯 LÀM GÌ & TÁC DỤNG CỐT LÕI",
                featuresTitle: "💡 TÍNH NĂNG CHI TIẾT & ĐIỂM ĂN TIỀN",
                quickRunTitle: "⚡ LỆNH CHẠY THỬ NHANH",
                suitableMajorTitle: "🎓 PHÙ HỢP CHUYÊN NGÀNH",
                targetRolesTitle: "👤 VỊ TRÍ CÔNG VIỆC",
                realWorldImpactTitle: "💥 BÀI TOÁN THỰC TẾ GIẢI QUYẾT",
                starGrowthTitle: "📈 TĂNG TRƯỞNG STARS",
                starGrowthLabels: {{ daily: "Hôm nay", weekly: "7 ngày", monthly: "30 ngày" }},
                starGrowthNoData: "Chưa có dữ liệu",
                starGrowthCache: "Cache tối đa 10 phút",
                chatTitle: (name) => `💬 Hỏi đáp chuyên sâu: ${{name}}`,
                chatHint: 'Gợi ý câu hỏi: <em>"Có chạy offline được không?", "Khác gì so với giải pháp khác?", "Cấu hình phần cứng ra sao?"</em>',
                chatInputPlaceholder: "Nhập câu hỏi kỹ thuật...",
                chatAskBtn: "Hỏi",
                chatLoading: "⏳ Đang phân tích câu trả lời...",
                chatEmptyAns: "Không có câu trả lời.",
                chatError: "❌ Lỗi khi hỏi đáp: ",
                chatBtnText: "💬 Hỏi đáp",
                copyBtn: "Copy",
                copiedBtn: "✓ Đã copy!",
                viewOnGithub: "Mở GitHub ↗",
                statusLabels: {{
                    unread: "Trạng thái: Chưa đọc",
                    want_to_try: "🔖 Muốn thử",
                    tried: "✅ Đã thử",
                    skipped: "⏭️ Bỏ qua",
                    liked: "👍 Đã Like"
                }},
                tagNewEntry: "🌱 Mới xuất hiện",
                tagReturning: (times) => `🔄 Đã gặp ${{times || 1}} lần`,
                tagAlt: (alt) => `💡 Thay thế: ${{alt}}`,
                deepSummary: (engine, sources) => `Phân tích sâu · ${{engine}} · ${{sources}} nguồn`,
                deepTopics: {{
                    how_it_works: 'Cách hoạt động & kiến trúc',
                    practical_examples: 'Ví dụ thực tế & cách đánh giá',
                    limitations: 'Giới hạn & trường hợp không phù hợp',
                    adoption_notes: 'Yêu cầu triển khai & tích hợp',
                    comparisons: 'So sánh & trade-off',
                    research_gaps: 'Cần kiểm chứng thêm',
                    grounding_critique: '🛡️ Tự phản biện & Kiểm chứng khách quan',
                }},
                repoTypeBadges: {{
                    tool_app: "🛠️ Tool / App",
                    library_sdk: "📦 Library / SDK",
                    ai_model: "🧠 AI Model / Weights",
                    course_tutorial: "📚 Khóa học / Tài liệu",
                    awesome_list: "📋 Awesome List",
                    dataset_benchmark: "📊 Dataset / Benchmark"
                }}
            }},
            en: {{
                mainTitle: "🔥 GitHub Trending Analyzer",
                mainSubtitle: "Automated deep analysis of core purposes, breakout velocity, project maturity, and personalized recommendations.",
                countBadge: (n) => `📦 ${{n}} projects`,
                langBadge: (l) => `💻 ${{l || 'All Languages'}}`,
                timeLabels: {{ daily: 'Today', weekly: 'This Week', monthly: 'This Month', search: 'GitHub Search' }},
                lblSearchInput: "Keyword",
                searchPlaceholderContent: "e.g. voice cloning, rag, image generation",
                searchPlaceholderName: "e.g. VoiceStudio, OpenShell",
                searchPlaceholderDefault: "e.g. agent, voice, Unity",
                lblSearchScope: "Search by",
                optScopeName: "Project name",
                optScopeContent: "Keywords in project (README)",
                lblResultLimit: "Result limit",
                lblKeywordMode: "Keyword matching",
                optModeAll: "Match all keywords",
                optModeAny: "Match any keyword",
                lblGithubLanguage: "Language",
                lblGithubSort: "Sort by (with keywords)",
                optSortMatch: "Best match",
                optSortStars: "Most stars",
                optSortUpdated: "Recently updated",
                lblTrendingPeriod: "Trending Period (when keyword is empty)",
                optPeriodDaily: "Today",
                optPeriodWeekly: "This Week",
                optPeriodMonthly: "This Month",
                lblDeepText: "Deep analysis (slower)",
                searchBtn: "🔍 Search",
                searchBtnSearching: "Searching…",
                resetBtn: "Reset filters",
                searchHelpDefault: (len, hasEndpoint) => hasEndpoint ? "Leave keyword empty: fetch GitHub Trending ranked by new stars. With keywords: search GitHub Search. Max 30 projects per run." : `Search in ${{len}} loaded projects. Open GitHub live search via ./trending --serve.`,
                searchHelpEmpty: "Leave keyword empty: fetch GitHub Trending ranked by new stars. Max 30 projects per run.",
                searchHelpContent: "Search keywords in project READMEs on GitHub. Separate multiple keywords with commas.",
                searchHelpName: "Search keywords in repository names on GitHub. Separate multiple keywords with commas.",
                searchStatusSearching: "Searching GitHub and analyzing documents. Deep analysis may take a couple of minutes.",
                searchStatusTrendingDone: "Fetched GitHub Trending, sorted by new stars descending.",
                searchStatusSearchDone: "Search and analysis completed.",
                searchStatusIncomplete: "GitHub returned incomplete results; try refining your search query.",
                searchStatusError: "Search could not complete; previous results retained.",
                filterCategoryAll: "All Categories",
                filterRepoTypeAll: "All Project Types",
                filterMaturityAll: "All Maturity Levels",
                filterVelocityAll: "All Growth Speeds",
                filterStatusAll: "All Statuses",
                lblWatchlistText: "⭐ Match Watchlist (>0%)",
                lblAltText: "💡 Commercial Alternative",
                syncWatchlist: "🧠 Sync Preferences",
                emptyState: "No repositories matched the current filters.",
                summaryText: (vis, filteredLen, totalLen, ghTotal, mode) => `Showing ${{vis}} / ${{filteredLen}} matching results · ${{totalLen}} loaded projects${{ghTotal === null ? "" : (mode === 'trending' ? ` / ${{ghTotal}} Trending projects` : ` / ${{ghTotal}} GitHub results`)}}`,
                
                // Card Titles & Details
                corePurposeTitle: "🎯 WHAT IT DOES & CORE PURPOSE",
                featuresTitle: "💡 KEY FEATURES & HIGHLIGHTS",
                quickRunTitle: "⚡ QUICK RUN",
                suitableMajorTitle: "🎓 SUITABLE MAJORS",
                targetRolesTitle: "👤 TARGET ROLES",
                realWorldImpactTitle: "💥 REAL-WORLD PROBLEM SOLVED",
                starGrowthTitle: "📈 STAR GROWTH",
                starGrowthLabels: {{ daily: "Today", weekly: "7 days", monthly: "30 days" }},
                starGrowthNoData: "No data available",
                starGrowthCache: "Cached up to 10 min",
                chatTitle: (name) => `💬 Deep Q&A: ${{name}}`,
                chatHint: 'Suggested questions: <em>"Can this run offline?", "How does it compare to alternatives?", "Hardware requirements?"</em>',
                chatInputPlaceholder: "Ask a technical question...",
                chatAskBtn: "Ask",
                chatLoading: "⏳ Analyzing technical answer...",
                chatEmptyAns: "No answer found.",
                chatError: "❌ Q&A error: ",
                chatBtnText: "💬 Q&A",
                copyBtn: "Copy",
                copiedBtn: "✓ Copied!",
                viewOnGithub: "View on GitHub ↗",
                statusLabels: {{
                    unread: "Status: Unread",
                    want_to_try: "🔖 Want to try",
                    tried: "✅ Tried",
                    skipped: "⏭️ Skipped",
                    liked: "👍 Liked"
                }},
                tagNewEntry: "🌱 New Entry",
                tagReturning: (times) => `🔄 Seen ${{times || 1}} times`,
                tagAlt: (alt) => `💡 Alternative: ${{alt}}`,
                deepSummary: (engine, sources) => `Deep Analysis · ${{engine}} · ${{sources}} sources`,
                deepTopics: {{
                    how_it_works: 'Architecture & How it works',
                    practical_examples: 'Practical Examples & Evaluation',
                    limitations: 'Limitations & Non-goals',
                    adoption_notes: 'Deployment & Adoption',
                    comparisons: 'Comparisons & Trade-offs',
                    research_gaps: 'Evidence Gaps & Validation',
                    grounding_critique: '🛡️ Self-Critique & Grounding',
                }},
                repoTypeBadges: {{
                    tool_app: "🛠️ Tool / App",
                    library_sdk: "📦 Library / SDK",
                    ai_model: "🧠 AI Model / Weights",
                    course_tutorial: "📚 Course / Tutorial",
                    awesome_list: "📋 Awesome List",
                    dataset_benchmark: "📊 Dataset / Benchmark"
                }}
            }}
        }};

        // Translation Cache in Memory & LocalStorage
        let translationCache = {{}};
        try {{
            translationCache = JSON.parse(localStorage.getItem('gh_trending_trans_cache') || '{{}}');
        }} catch(e) {{}}

        function saveTransCache() {{
            try {{
                localStorage.setItem('gh_trending_trans_cache', JSON.stringify(translationCache));
            }} catch(e) {{}}
        }}

        // Offline Rule-based Tech Translator for Instant Display
        function translateTechToVietnameseInstant(text) {{
            if (!text || typeof text !== 'string') return text || '';
            let t = text.trim();
            
            // Exact / common known phrases
            if (t.includes("the open-source search engine for job seekers")) {{
                return t.replace(/the open-source search engine for job seekers/gi, "công cụ tìm kiếm việc làm mã nguồn mở dành cho người tìm việc");
            }}
            if (t.includes("A coding-agent skill for multi-phase security audits with independently verified, machine-readable findings")) {{
                return "Kỹ năng coding agent chuyên phục vụ kiểm tra an toàn bảo mật (security audit) nhiều giai đoạn với các phát hiện được kiểm chứng độc lập và máy đọc được.";
            }}
            if (t.includes("A high-throughput and memory-efficient inference and serving engine for LLMs")) {{
                return "Bộ máy phục vụ suy luận (inference & serving engine) cho LLM với thông lượng cao và tiết kiệm bộ nhớ.";
            }}
            if (t.includes("Orca is the place for working with a fleet of agents")) {{
                return "Orca là nền tảng quản lý và điều phối nhóm agent AI (như Grok Bot, Claude Code). Cho phép chạy bất kỳ coding agent nào với gói thuê bao riêng. Hỗ trợ máy tính, thiết bị di động và môi trường chạy từ xa.";
            }}

            // Patterns replacement
            t = t.replace(/^A\s+framework\s+for\s+building\s+/i, "Framework hỗ trợ xây dựng ");
            t = t.replace(/^An?\s+open-source\s+(alternative\s+to\s+)/i, "Giải pháp mã nguồn mở thay thế cho ");
            t = t.replace(/^An?\s+open-source\s+search\s+engine\s+for\s+/i, "Công cụ tìm kiếm mã nguồn mở dành cho ");
            t = t.replace(/^An?\s+open-source\s+/i, "Dự án mã nguồn mở ");
            t = t.replace(/^An?\s+autonomous\s+agent\s+framework\s+/i, "Framework agent tự hành ");
            t = t.replace(/^Autonomous\s+multi-agent\s+orchestration\s+framework\s+for\s+LLMs/i, "Framework điều phối đa agent tự hành cho LLM");
            t = t.replace(/^An?\s+agentic\s+coding\s+tool\s+/i, "Công cụ lập trình AI tự hành (agentic) ");
            t = t.replace(/^A\s+modern,\s+(?:fast|high-performance)\s+/i, "Công cụ hiện đại, hiệu năng cao ");
            t = t.replace(/^A\s+lightweight\s+and\s+(?:fast|modular)\s+/i, "Giải pháp nhẹ và tối ưu ");
            t = t.replace(/^Scale\s+/i, "Giải pháp mở rộng quy mô ");
            t = t.replace(/^AI-powered\s+/i, "Được tăng cường bởi AI, ");
            t = t.replace(/State-of-the-art serving throughput/i, "Thông lượng phục vụ tiên tiến hàng đầu");
            t = t.replace(/Efficient management of attention key and value memory with PagedAttention/i, "Quản lý bộ nhớ KV cache hiệu quả nhờ kiến trúc PagedAttention");
            t = t.replace(/Continuous batching of incoming requests/i, "Gom nhóm xử lý liên tục (continuous batching) các yêu cầu gửi đến");
            t = t.replace(/Fast model execution with CUDA\/HIP graph/i, "Thực thi mô hình siêu tốc với CUDA/HIP graph");
            t = t.replace(/Straight from the source\. Every listing is crawled directly from/i, "Dữ liệu trực tiếp từ nguồn: Mọi tin được cào trực tiếp từ");
            t = t.replace(/One schema, deduplicated/i, "Chuẩn hóa một cấu trúc chung, tự động loại bỏ tin trùng lặp");
            t = t.replace(/Actually open\. MIT-licensed and self-hostable/i, "Hoàn toàn mở: Giấy phép MIT và có thể tự triển khai (self-host)");
            return t;
        }}

        // Async Google Translation (Runs in background, updates seamlessly when online)
        async function fetchGoogleTranslation(text, targetLang) {{
            if (!text || text.trim().length === 0) return text;
            const clean = text.trim();
            const cacheKey = targetLang + '::' + clean;
            if (translationCache[cacheKey]) return translationCache[cacheKey];

            try {{
                const url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=' + targetLang + '&dt=t&q=' + encodeURIComponent(clean);
                const res = await fetch(url);
                if (!res.ok) return null;
                const data = await res.json();
                if (data && data[0]) {{
                    const translated = data[0].map(item => item[0]).join('');
                    if (translated && translated.trim()) {{
                        translationCache[cacheKey] = translated.trim();
                        saveTransCache();
                        return translated.trim();
                    }}
                }}
            }} catch (e) {{
                // Offline fallback handled gracefully
            }}
            return null;
        }}

        function isVietnamese(text) {{
            return /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i.test(text || '');
        }}

        // Helper to get bilingual explanation for core purpose
        function getDisplayCorePurpose(r, lang, elementId) {{
            if (lang === 'en') {{
                const enText = r.core_purpose_en || r.description || r.core_purpose || '';
                return enText;
            }}
            // Vietnamese mode
            if (r.core_purpose_vi && isVietnamese(r.core_purpose_vi)) {{
                return r.core_purpose_vi;
            }}
            if (r.core_purpose && isVietnamese(r.core_purpose)) {{
                return r.core_purpose;
            }}
            const rawEn = r.core_purpose_en || r.core_purpose || r.description || '';
            const cacheKey = 'vi::' + rawEn.trim();
            if (translationCache[cacheKey]) {{
                return translationCache[cacheKey];
            }}
            // Instant rule-based translation first
            const instant = translateTechToVietnameseInstant(rawEn);
            // Async fetch Google translate in background
            if (elementId && rawEn) {{
                fetchGoogleTranslation(rawEn, 'vi').then(better => {{
                    if (better && currentLang === 'vi') {{
                        const el = document.getElementById(elementId);
                        if (el) el.textContent = better;
                    }}
                }});
            }}
            return instant;
        }}

        // Helper to get bilingual features
        function getDisplayFeatures(r, lang, cardIdx) {{
            const enList = (r.key_features_en && r.key_features_en.length) ? r.key_features_en : (r.key_features || []);
            const viList = (r.key_features_vi && r.key_features_vi.length) ? r.key_features_vi : [];

            if (lang === 'en') {{
                return enList;
            }}

            // Vietnamese mode
            return enList.map((f, fIdx) => {{
                if (viList[fIdx] && isVietnamese(viList[fIdx])) {{
                    return viList[fIdx];
                }}
                if (isVietnamese(f)) return f;
                const cacheKey = 'vi::' + f.trim();
                if (translationCache[cacheKey]) return translationCache[cacheKey];
                
                const elId = `feat_${{cardIdx}}_${{fIdx}}`;
                fetchGoogleTranslation(f, 'vi').then(better => {{
                    if (better && currentLang === 'vi') {{
                        const el = document.getElementById(elId);
                        if (el) el.textContent = better;
                    }}
                }});
                return translateTechToVietnameseInstant(f);
            }});
        }}

        // Fallback role info in English
        const CATEGORY_MAP_EN = {{
            "AI & Machine Learning": {{
                major: "Artificial Intelligence (AI), Data Science, Software Engineering",
                roles: "AI Engineer, LLM/Agent Developer, Data Scientist, MLOps Engineer",
                impact: "Automates complex cognitive workflows, enhances developer productivity, and powers intelligent decision-making."
            }},
            "Developer Tooling & CLI": {{
                major: "Software Engineering, Computer Science",
                roles: "Software Engineer, Fullstack Developer, DevOps, CLI Tooling Specialist",
                impact: "Minimizes manual repetitive tasks, accelerates development workflow, and standardizes workspace environments."
            }},
            "Web & Frontend": {{
                major: "Information Technology, Web Design & UI/UX, Frontend Development",
                roles: "Frontend Developer, Fullstack Developer, Web Architect, UI/UX Engineer",
                impact: "Optimizes page load performance and delivers smooth, intuitive user interactions."
            }},
            "Backend & APIs": {{
                major: "Software Engineering, Information Systems, Distributed Systems Architecture",
                roles: "Backend Developer, API Architect, Microservices Engineer, Cloud Engineer",
                impact: "Ensures high concurrency, elastic scalability, and robust data integrity for enterprise systems."
            }},
            "DevOps & Infrastructure": {{
                major: "Computer Networks, Cloud Computing, Infrastructure Engineering",
                roles: "DevOps Engineer, SRE (Site Reliability Engineer), Cloud Architect, Platform Engineer",
                impact: "Automates CI/CD pipelines, standardizes deployment environments, and optimizes cloud infrastructure costs."
            }},
            "Database & Storage": {{
                major: "Management Information Systems, Data Engineering, Databases",
                roles: "Data Engineer, Database Administrator (DBA), Backend Developer, Big Data Architect",
                impact: "Accelerates big data queries, provides secure storage, and powers vector search for modern applications."
            }},
            "Security & Privacy": {{
                major: "Cybersecurity, Digital Forensics, Computer Networks",
                roles: "Security Researcher, Pentester, SOC Analyst, Security Specialist",
                impact: "Proactively identifies security vulnerabilities, spyware, and prevents sensitive data leaks."
            }},
            "Automation & Workflow": {{
                major: "Robotic Process Automation (RPA), Multimedia, Digital Operations",
                roles: "Automation Engineer, Growth Hacker, Video Editor, Content Creator",
                impact: "Eliminates 80-90% of manual effort for repetitive tasks like video editing, batching, and data synchronization."
            }}
        }};

        function getRoleField(r, field, lang) {{
            if (lang === 'vi') {{
                return r[field] || '';
            }}
            const enKey = field + '_en';
            if (r[enKey]) return r[enKey];
            const catMap = CATEGORY_MAP_EN[r.category] || CATEGORY_MAP_EN["Developer Tooling & CLI"];
            if (field === 'suitable_major') return catMap.major;
            if (field === 'target_roles') return catMap.roles;
            if (field === 'real_world_impact') return catMap.impact;
            return r[field] || '';
        }}

        // Populate category dropdown
        const categoryFilter = document.getElementById("categoryFilter");
        function populateCategories() {{
            categoryFilter.replaceChildren();
            const all = document.createElement('option');
            all.value = '';
            all.textContent = I18N[currentLang].filterCategoryAll;
            categoryFilter.appendChild(all);
            [...new Set(reposData.map(r => r.category).filter(Boolean))].forEach(cat => {{
                const opt = document.createElement('option'); opt.value = cat; opt.textContent = cat;
                categoryFilter.appendChild(opt);
            }});
        }}

        function setText(id, text) {{
            const el = document.getElementById(id);
            if (el) el.textContent = text;
        }}

        function setLanguage(lang) {{
            currentLang = (lang === 'en') ? 'en' : 'vi';
            try {{
                localStorage.setItem('gh_trending_dashboard_lang', currentLang);
            }} catch(e) {{}}
            const langSelect = document.getElementById('langSelect');
            if (langSelect) langSelect.value = currentLang;

            const t = I18N[currentLang] || I18N.vi;
            setText('mainTitle', t.mainTitle);
            setText('mainSubtitle', t.mainSubtitle);
            setText('lblSearchInput', t.lblSearchInput);
            setText('lblSearchScope', t.lblSearchScope);
            setText('optScopeName', t.optScopeName);
            setText('optScopeContent', t.optScopeContent);
            setText('lblResultLimit', t.lblResultLimit);
            setText('lblKeywordMode', t.lblKeywordMode);
            setText('optModeAll', t.optModeAll);
            setText('optModeAny', t.optModeAny);
            setText('lblGithubLanguage', t.lblGithubLanguage);
            setText('lblGithubSort', t.lblGithubSort);
            setText('optSortMatch', t.optSortMatch);
            setText('optSortStars', t.optSortStars);
            setText('optSortUpdated', t.optSortUpdated);
            setText('lblTrendingPeriod', t.lblTrendingPeriod);
            setText('optPeriodDaily', t.optPeriodDaily);
            setText('optPeriodWeekly', t.optPeriodWeekly);
            setText('optPeriodMonthly', t.optPeriodMonthly);
            setText('lblDeepText', t.lblDeepText);
            setText('searchButton', t.searchBtn);
            setText('resetSearch', t.resetBtn);
            setText('lblWatchlistText', t.lblWatchlistText);
            setText('lblAltText', t.lblAltText);
            setText('syncWatchlistBtn', t.syncWatchlist);
            setText('loadedCount', t.countBadge(reposData.length));
            setText('emptyState', t.emptyState);

            // Filters
            populateCategories();
            const repoType = document.getElementById('repoTypeFilter');
            if (repoType && repoType.options && repoType.options.length >= 7) {{
                const val = repoType.value;
                repoType.options[0].textContent = t.filterRepoTypeAll;
                repoType.options[1].textContent = t.repoTypeBadges.tool_app;
                repoType.options[2].textContent = t.repoTypeBadges.library_sdk;
                repoType.options[3].textContent = t.repoTypeBadges.ai_model;
                repoType.options[4].textContent = t.repoTypeBadges.course_tutorial;
                repoType.options[5].textContent = t.repoTypeBadges.awesome_list;
                repoType.options[6].textContent = t.repoTypeBadges.dataset_benchmark;
                repoType.value = val;
            }}

            const matType = document.getElementById('maturityFilter');
            if (matType && matType.options && matType.options.length >= 1) {{
                const val = matType.value;
                matType.options[0].textContent = t.filterMaturityAll;
                matType.value = val;
            }}

            const velType = document.getElementById('velocityFilter');
            if (velType && velType.options && velType.options.length >= 4) {{
                const val = velType.value;
                velType.options[0].textContent = t.filterVelocityAll;
                velType.options[1].textContent = (currentLang === 'vi') ? "🔥 Siêu bứt phá (Breakout)" : "🔥 Breakout Star";
                velType.options[2].textContent = (currentLang === 'vi') ? "⚡ Tăng trưởng nhanh (High Velocity)" : "⚡ High Velocity";
                velType.options[3].textContent = (currentLang === 'vi') ? "🏛️ Dự án kinh điển (Established)" : "🏛️ Established Giant";
                velType.value = val;
            }}

            const statType = document.getElementById('statusFilter');
            if (statType && statType.options && statType.options.length >= 5) {{
                const val = statType.value;
                statType.options[0].textContent = t.filterStatusAll;
                statType.options[1].textContent = t.statusLabels.want_to_try;
                statType.options[2].textContent = t.statusLabels.tried;
                statType.options[3].textContent = t.statusLabels.skipped;
                statType.options[4].textContent = t.statusLabels.liked;
                statType.value = val;
            }}

            updateSearchMode();
            filterCards();
        }}

        function copyCmd(btn, text) {{
            const t = I18N[currentLang];
            navigator.clipboard.writeText(text).then(() => {{
                const old = btn.textContent;
                btn.textContent = t.copiedBtn;
                setTimeout(() => {{ btn.textContent = old; }}, 2000);
            }}).catch(() => {{
                prompt("Copy:", text);
            }});
        }}

        function getVelocityBadgeClass(badge) {{
            if (!badge) return "";
            if (badge.includes("Breakout")) return "tag-velocity-breakout";
            if (badge.includes("High Velocity")) return "tag-velocity-high";
            if (badge.includes("Established")) return "tag-velocity-giant";
            return "";
        }}

        function getMaturityBadgeClass(level) {{
            if (level === "production") return "tag-maturity-prod";
            if (level === "beta") return "tag-maturity-beta";
            return "tag-maturity-exp";
        }}

        function escapeText(value) {{
            return String(value).replace(/[&<>"']/g, c => ({{'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}}[c]));
        }}

        function renderCards(list) {{
            const grid = document.getElementById("cardsGrid");
            const empty = document.getElementById("emptyState");
            const t = I18N[currentLang];
            grid.innerHTML = "";

            if (list.length === 0) {{
                empty.style.display = "block";
                return;
            }}
            empty.style.display = "none";

            list.forEach((raw, idx) => {{
                const r = Object.fromEntries(Object.entries(raw).map(([key, value]) => [key,
                    typeof value === 'string' ? escapeText(value) :
                    Array.isArray(value) ? value.map(x => typeof x === 'string' ? escapeText(x) : x) : value]));
                r.url = /^https:\/\/github\.com\/[^\s]+$/.test(raw.url) ? escapeText(raw.url) : '#';
                const card = document.createElement("div");
                card.className = "repo-card";

                const corePurposeId = `core_p_${{idx}}`;
                const displayCore = getDisplayCorePurpose(raw, currentLang, corePurposeId);
                const displayFeatures = getDisplayFeatures(raw, currentLang, idx);

                const featuresHtml = displayFeatures.map((f, fIdx) => `<li id="feat_${{idx}}_${{fIdx}}">${{escapeText(f)}}</li>`).join("");
                const techStackHtml = (r.tech_stack || []).map(item => `<span class="tech-pill">${{item}}</span>`).join("");

                const velClass = getVelocityBadgeClass(r.velocity_badge);
                const matClass = getMaturityBadgeClass(r.maturity_level);
                const growth = raw.growth;
                const growthHtml = growth ? `
                    <div class="section-title">${{t.starGrowthTitle}}</div>
                    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:8px;">
                        ${{[['daily', t.starGrowthLabels.daily], ['weekly', t.starGrowthLabels.weekly], ['monthly', t.starGrowthLabels.monthly]].map(([key, label]) =>
                            `<span class="tech-pill">${{label}}: ${{Number.isInteger(growth[key]) && growth[key] >= 0 ? '+' + growth[key].toLocaleString(currentLang === 'vi' ? 'vi-VN' : 'en-US') : t.starGrowthNoData}}</span>`).join('')}}
                    </div>
                    <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:12px;">${{escapeText(growth.note || '')}} · ${{t.starGrowthCache}}</div>
                ` : '';

                const repoTypeDisplay = t.repoTypeBadges[raw.repo_type] || r.repo_type_badge || '';
                const displayMajor = getRoleField(raw, 'suitable_major', currentLang);
                const displayRoles = getRoleField(raw, 'target_roles', currentLang);
                const displayImpact = getRoleField(raw, 'real_world_impact', currentLang);

                card.innerHTML = `
                    <div>
                        <div class="card-header">
                            <a href="${{r.url}}" target="_blank" class="repo-title">📦 ${{r.name}}</a>
                            <span class="stars-pill">${{r.timeframe === "search" ? `★ ${{r.stars_total}}` : `★ +${{r.stars_since || "0"}} · ${{t.timeLabels[r.timeframe] || r.timeframe}}`}}</span>
                        </div>

                        <!-- Status & Category Badges -->
                        <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px;">
                            <span class="pill-tag tag-category">🏷️ ${{r.category}}</span>
                            ${{repoTypeDisplay ? `<span class="pill-tag tag-repo-type">${{escapeText(repoTypeDisplay)}}</span>` : ''}}
                            ${{r.grounding_score ? `<span class="pill-tag tag-grounding" title="Grounding: ${{r.grounding_score}}/100">🛡️ Grounding: ${{r.grounding_score}}/100</span>` : ''}}
                            ${{r.is_new_entry ? `<span class="pill-tag tag-new-entry">${{t.tagNewEntry}}</span>` : `<span class="pill-tag tag-returning">${{t.tagReturning(r.times_seen)}}</span>`}}
                            ${{r.velocity_badge ? `<span class="pill-tag ${{velClass}}">${{r.velocity_badge}}</span>` : ''}}
                            ${{r.maturity_badge ? `<span class="pill-tag ${{matClass}}">${{r.maturity_badge}}</span>` : ''}}
                            ${{r.commercial_alternative ? `<span class="pill-tag tag-alternative">${{t.tagAlt(r.commercial_alternative)}}</span>` : ''}}
                            ${{r.match_score > 0 ? `<span class="pill-tag tag-match">⭐ ${{r.match_score}}% Match</span>` : ''}}
                        </div>

                        <!-- Feedback Toolbar -->
                        <div class="feedback-bar">
                            <div class="rating-buttons">
                                <button type="button" class="btn-rate btn-like ${{raw.user_rating === 1 ? 'active' : ''}}" title="Useful" data-action="like">👍</button>
                                <button type="button" class="btn-rate btn-dislike ${{raw.user_rating === -1 ? 'active' : ''}}" title="Not useful" data-action="dislike">👎</button>
                                <button type="button" class="btn-chat" title="${{t.chatBtnText}}">${{t.chatBtnText}}</button>
                            </div>
                            <select class="status-select" title="Status">
                                <option value="unread" ${{raw.user_status === 'unread' ? 'selected' : ''}}>${{t.statusLabels.unread}}</option>
                                <option value="want_to_try" ${{raw.user_status === 'want_to_try' ? 'selected' : ''}}>${{t.statusLabels.want_to_try}}</option>
                                <option value="tried" ${{raw.user_status === 'tried' ? 'selected' : ''}}>${{t.statusLabels.tried}}</option>
                                <option value="skipped" ${{raw.user_status === 'skipped' ? 'selected' : ''}}>${{t.statusLabels.skipped}}</option>
                            </select>
                        </div>

                        <!-- Interactive Repo Q&A Chat Box -->
                        <div class="chat-container" style="display:none; margin-bottom:12px; background:rgba(22,27,34,0.95); border:1px solid var(--accent-blue); border-radius:6px; padding:10px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <span style="font-size:0.8rem; font-weight:bold; color:var(--accent-blue);">${{t.chatTitle(r.name)}}</span>
                                <button type="button" class="btn-close-chat" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-size:0.9rem;">✕</button>
                            </div>
                            <div class="chat-messages" style="max-height:160px; overflow-y:auto; font-size:0.82rem; margin-bottom:8px; display:flex; flex-direction:column; gap:6px;">
                                <div style="color:var(--text-muted);">${{t.chatHint}}</div>
                            </div>
                            <div style="display:flex; gap:6px;">
                                <input type="text" class="chat-input" placeholder="${{t.chatInputPlaceholder}}" style="flex:1; background:#0d1117; border:1px solid var(--border); color:var(--text-main); padding:4px 8px; border-radius:4px; font-size:0.82rem;">
                                <button type="button" class="btn-send-chat" style="background:var(--accent-blue); color:#000; border:none; padding:4px 10px; border-radius:4px; font-weight:bold; font-size:0.82rem; cursor:pointer;">${{t.chatAskBtn}}</button>
                            </div>
                        </div>

                        ${{growthHtml}}
                        ${{techStackHtml ? `
                            <div style="display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 10px;">
                                <span style="font-size: 0.75rem; color: var(--text-muted); margin-right: 4px;">Tech:</span>
                                ${{techStackHtml}}
                            </div>
                        ` : ''}}

                        ${{r.quick_run ? `
                            <div class="section-title">${{t.quickRunTitle}}</div>
                            <div class="quick-run-box">
                                <span class="quick-run-code" title="${{r.quick_run}}">${{r.quick_run}}</span>
                                <button class="btn-copy">${{t.copyBtn}}</button>
                            </div>
                        ` : ''}}

                        <div class="section-title">${{t.corePurposeTitle}}</div>
                        <div id="${{corePurposeId}}" class="core-purpose">${{escapeText(displayCore)}}</div>

                        ${{featuresHtml ? `
                            <div class="section-title">${{t.featuresTitle}}</div>
                            <ul class="features-list">${{featuresHtml}}</ul>
                        ` : ''}}

                        ${{displayMajor ? `
                            <div class="section-title">${{t.suitableMajorTitle}}</div>
                            <div style="font-size: 0.88rem; color: var(--text-bright); margin-bottom: 8px;">📚 ${{escapeText(displayMajor)}}</div>
                        ` : ''}}

                        ${{displayRoles ? `
                            <div class="section-title">${{t.targetRolesTitle}}</div>
                            <div class="audience">${{escapeText(displayRoles)}}</div>
                        ` : ''}}

                        ${{displayImpact ? `
                            <div class="section-title">${{t.realWorldImpactTitle}}</div>
                            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px; border-left: 2px solid var(--accent-green); padding-left: 8px;">${{escapeText(displayImpact)}}</div>
                        ` : ''}}
                    </div>

                    <div class="card-footer">
                        <div class="meta-stats">
                            <span>💻 ${{r.language || "Unknown"}}</span>
                            <span>🌟 ${{r.stars_total}}</span>
                        </div>
                        <a href="${{r.url}}" target="_blank" class="btn-view">${{t.viewOnGithub}}</a>
                    </div>
                `;
                const copy = card.querySelector('.btn-copy');
                if (copy) copy.addEventListener('click', () => copyCmd(copy, raw.quick_run));

                const likeBtn = card.querySelector('.btn-like');
                const dislikeBtn = card.querySelector('.btn-dislike');
                const statusSelect = card.querySelector('.status-select');
                if (likeBtn && dislikeBtn) {{
                    likeBtn.addEventListener('click', async () => {{
                        const newRating = raw.user_rating === 1 ? 0 : 1;
                        await sendFeedback(raw.name, {{ rating: newRating }});
                        raw.user_rating = newRating;
                        likeBtn.classList.toggle('active', newRating === 1);
                        dislikeBtn.classList.remove('active');
                    }});
                    dislikeBtn.addEventListener('click', async () => {{
                        const newRating = raw.user_rating === -1 ? 0 : -1;
                        await sendFeedback(raw.name, {{ rating: newRating }});
                        raw.user_rating = newRating;
                        dislikeBtn.classList.toggle('active', newRating === -1);
                        likeBtn.classList.remove('active');
                    }});
                }}
                if (statusSelect) {{
                    statusSelect.addEventListener('change', async () => {{
                        const newStatus = statusSelect.value;
                        await sendFeedback(raw.name, {{ status: newStatus }});
                        raw.user_status = newStatus;
                    }});
                }}

                const chatBtn = card.querySelector('.btn-chat');
                const chatContainer = card.querySelector('.chat-container');
                const closeChat = card.querySelector('.btn-close-chat');
                const sendChat = card.querySelector('.btn-send-chat');
                const chatInput = card.querySelector('.chat-input');
                const chatMessages = card.querySelector('.chat-messages');

                if (chatBtn && chatContainer) {{
                    chatBtn.addEventListener('click', () => {{
                        const isHidden = chatContainer.style.display === 'none';
                        chatContainer.style.display = isHidden ? 'block' : 'none';
                        if (isHidden && chatInput) chatInput.focus();
                    }});
                    if (closeChat) {{
                        closeChat.addEventListener('click', () => {{ chatContainer.style.display = 'none'; }});
                    }}
                    const doAsk = async () => {{
                        const q = chatInput.value.trim();
                        if (!q) return;
                        chatInput.value = '';
                        const userMsg = document.createElement('div');
                        userMsg.style.cssText = 'color:var(--text-bright); font-weight:600; margin-top:4px;';
                        userMsg.textContent = 'Q: ' + q;
                        chatMessages.appendChild(userMsg);

                        const loadingMsg = document.createElement('div');
                        loadingMsg.style.cssText = 'color:var(--text-muted); font-style:italic; font-size:0.78rem;';
                        loadingMsg.textContent = t.chatLoading;
                        chatMessages.appendChild(loadingMsg);
                        chatMessages.scrollTop = chatMessages.scrollHeight;

                        try {{
                            const res = await fetch('/api/chat', {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                body: JSON.stringify({{ full_name: raw.name, question: q }})
                            }});
                            const data = await res.json();
                            loadingMsg.remove();
                            const ansMsg = document.createElement('div');
                            ansMsg.style.cssText = 'color:var(--text-main); background:rgba(63,185,80,0.08); padding:6px 8px; border-radius:4px; border-left:2px solid var(--accent-green); white-space:pre-wrap; line-height:1.4;';
                            ansMsg.textContent = data.answer || t.chatEmptyAns;
                            chatMessages.appendChild(ansMsg);
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }} catch (e) {{
                            loadingMsg.textContent = t.chatError + e.message;
                        }}
                    }};
                    if (sendChat) sendChat.addEventListener('click', doAsk);
                    if (chatInput) chatInput.addEventListener('keydown', (e) => {{ if (e.key === 'Enter') doAsk(); }});
                }}

                const details = document.createElement('details');
                const summary = document.createElement('summary');
                summary.textContent = t.deepSummary(raw.engine_used, raw.data_sources?.length || 0);
                summary.style.cssText = 'cursor:pointer;color:var(--accent-blue);padding:12px 0';
                details.appendChild(summary);
                const topics = [
                    [t.deepTopics.how_it_works, 'how_it_works'],
                    [t.deepTopics.practical_examples, 'practical_examples'],
                    [t.deepTopics.limitations, 'limitations'],
                    [t.deepTopics.adoption_notes, 'adoption_notes'],
                    [t.deepTopics.comparisons, 'comparisons'],
                    [t.deepTopics.research_gaps, 'research_gaps'],
                    [t.deepTopics.grounding_critique, 'grounding_critique'],
                ];
                topics.forEach(([title, field]) => {{
                    if (!raw[field]?.length) return;
                    const heading = document.createElement('div');
                    heading.className = 'section-title'; heading.textContent = title;
                    details.appendChild(heading);
                    raw[field].forEach(text => {{
                        const paragraph = document.createElement('p');
                        paragraph.textContent = text;
                        paragraph.style.cssText = 'white-space:pre-wrap;overflow-wrap:anywhere;font-size:.85rem;margin-bottom:12px';
                        details.appendChild(paragraph);
                    }});
                }});
                (raw.data_sources || []).forEach(source => {{
                    const row = document.createElement('p');
                    const link = document.createElement('a');
                    link.textContent = `[${{source.id}}] ${{source.title}}`;
                    if (/^https:\/\/(github\.com|raw\.githubusercontent\.com)\//.test(source.url)) link.href = source.url;
                    link.target = '_blank'; link.rel = 'noopener noreferrer';
                    row.appendChild(link);
                    row.appendChild(document.createTextNode(` · ${{source.fetched_at}} · ${{source.freshness}}`));
                    details.appendChild(row);
                }});
                card.insertBefore(details, card.querySelector('.card-footer'));
                grid.appendChild(card);
            }});
        }}

        function normalizeSearch(value) {{
            return String(value || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd');
        }}

        function filterCards() {{
            const limitInput = document.getElementById('resultLimit');
            if (!limitInput.reportValidity()) return;
            const limit = Number(limitInput.value);
            const keywords = [...new Set(document.getElementById('searchInput').value.split(',').map(value => normalizeSearch(value.trim())).filter(Boolean))];
            const mode = document.getElementById('keywordMode').value;
            const selectedCat = document.getElementById("categoryFilter").value;
            const selectedRepoType = document.getElementById("repoTypeFilter") ? document.getElementById("repoTypeFilter").value : "";
            const selectedMaturity = document.getElementById("maturityFilter").value;
            const selectedVelocity = document.getElementById("velocityFilter").value;
            const watchlistOnly = document.getElementById("watchlistOnly").checked;
            const altOnly = document.getElementById("altOnly").checked;
            const selectedStatus = document.getElementById("statusFilter") ? document.getElementById("statusFilter").value : "";

            const filtered = reposData.filter(r => {{
                const matchesCat = !selectedCat || r.category === selectedCat;
                const matchesRepoType = !selectedRepoType || r.repo_type === selectedRepoType;
                const matchesMaturity = !selectedMaturity || r.maturity_level === selectedMaturity;
                
                let matchesVelocity = true;
                if (selectedVelocity === "breakout") {{
                    matchesVelocity = (r.velocity_badge || "").includes("Breakout");
                }} else if (selectedVelocity === "velocity") {{
                    matchesVelocity = (r.velocity_badge || "").includes("High Velocity");
                }} else if (selectedVelocity === "giant") {{
                    matchesVelocity = (r.velocity_badge || "").includes("Established");
                }}

                const matchesWatchlist = !watchlistOnly || (r.match_score && r.match_score > 0);
                const matchesAlt = !altOnly || Boolean(r.commercial_alternative);

                let matchesStatus = true;
                if (selectedStatus === 'liked') {{
                    matchesStatus = r.user_rating === 1;
                }} else if (selectedStatus) {{
                    matchesStatus = r.user_status === selectedStatus;
                }}

                const techText = (r.tech_stack || []).join(" ");
                const quickText = r.quick_run || "";
                const altText = r.commercial_alternative || "";
                const researchText = ['how_it_works', 'practical_examples', 'limitations', 'adoption_notes', 'comparisons'].map(key => (r[key] || []).join(' ')).join(' ');
                const corpus = normalizeSearch([
                    r.name, r.description, r.core_purpose, r.language, r.category,
                    altText, techText, quickText, researchText, (r.key_features || []).join(' '), r.target_roles,
                ].join(' '));
                const matchesQuery = Boolean(searchEndpoint) || !keywords.length || (mode === 'all'
                    ? keywords.every(keyword => corpus.includes(keyword))
                    : keywords.some(keyword => corpus.includes(keyword)));

                return matchesCat && matchesRepoType && matchesMaturity && matchesVelocity && matchesWatchlist && matchesAlt && matchesStatus && matchesQuery;
            }});

            const visible = filtered.slice(0, limit);
            const t = I18N[currentLang];
            document.getElementById('resultsSummary').textContent = t.summaryText(visible.length, filtered.length, reposData.length, githubTotal, resultMode);
            renderCards(visible);
        }}

        async function sendFeedback(fullName, payload) {{
            if (!searchEndpoint) return;
            try {{
                const response = await fetch('/api/feedback', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ full_name: fullName, ...payload }}),
                }});
                return await response.json();
            }} catch (err) {{
                console.warn('Error saving feedback:', err);
            }}
        }}

        const syncWatchlistBtn = document.getElementById('syncWatchlistBtn');
        if (syncWatchlistBtn) {{
            syncWatchlistBtn.addEventListener('click', async () => {{
                syncWatchlistBtn.disabled = true;
                syncWatchlistBtn.textContent = (currentLang === 'vi') ? 'Đang học…' : 'Learning…';
                try {{
                    const response = await fetch('/api/sync-watchlist', {{ method: 'POST' }});
                    const data = await response.json();
                    if (data.status === 'success') {{
                        const added = data.added || {{}};
                        const info = [];
                        if (added.keywords && added.keywords.length) info.push(`• Keywords: ${{added.keywords.join(', ')}}`);
                        if (added.languages && added.languages.length) info.push(`• Languages: ${{added.languages.join(', ')}}`);
                        if (added.categories && added.categories.length) info.push(`• Categories: ${{added.categories.join(', ')}}`);
                        alert(info.length ? `🧠 Watchlist updated with:\n\n${{info.join('\n')}}` : (currentLang === 'vi' ? 'Chưa có đủ repo được like hoặc đánh dấu "Muốn thử" để học.' : 'Not enough liked or "Want to try" repositories to learn from.'));
                    }} else {{
                        alert('Error: ' + (data.error || 'Sync failed'));
                    }}
                }} catch (e) {{
                    alert(currentLang === 'vi' ? 'Lỗi kết nối khi đồng bộ sở thích.' : 'Connection error while syncing preferences.');
                }} finally {{
                    syncWatchlistBtn.disabled = false;
                    syncWatchlistBtn.textContent = I18N[currentLang].syncWatchlist;
                }}
            }});
        }}

        async function searchProjects() {{
            if (!searchEndpoint) {{ filterCards(); return; }}
            if (searching || !document.getElementById('searchForm').reportValidity()) return;
            searching = true;
            const button = document.getElementById('searchButton');
            const status = document.getElementById('searchStatus');
            const error = document.getElementById('searchError');
            const t = I18N[currentLang];
            button.disabled = true; button.textContent = t.searchBtnSearching; error.textContent = '';
            status.textContent = t.searchStatusSearching;
            try {{
                const response = await fetch(searchEndpoint, {{
                    method: 'POST', headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        query: document.getElementById('searchInput').value.trim(),
                        limit: Number(document.getElementById('resultLimit').value),
                        mode: document.getElementById('keywordMode').value,
                        scope: document.getElementById('searchScope').value,
                        language: document.getElementById('githubLanguage').value.trim(),
                        sort: document.getElementById('githubSort').value,
                        timeframe: document.getElementById('trendingPeriod').value,
                        deep: document.getElementById('deepResearch').checked,
                    }}),
                }});
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || (currentLang === 'vi' ? 'Không tìm kiếm được.' : 'Search failed.'));
                reposData = data.results; githubTotal = data.total_count; resultMode = data.mode;
                document.getElementById('sourceBadge').textContent = resultMode === 'trending' ? `📈 Trending · ${{t.timeLabels[data.timeframe] || data.timeframe}}` : `🔎 GitHub Search · ${{data.scope === 'content' ? (currentLang === 'vi' ? 'Nội dung README' : 'README Content') : (currentLang === 'vi' ? 'Tên project' : 'Project Name')}}`;
                document.getElementById('velocityFilter').hidden = resultMode !== 'trending';
                populateCategories();
                ['repoTypeFilter', 'maturityFilter', 'velocityFilter', 'statusFilter'].forEach(id => {{ const el = document.getElementById(id); if (el) el.value = ''; }});
                ['watchlistOnly', 'altOnly'].forEach(id => document.getElementById(id).checked = false);
                document.getElementById('loadedCount').textContent = t.countBadge(reposData.length);
                filterCards();
                status.textContent = resultMode === 'trending' ? t.searchStatusTrendingDone : data.incomplete_results ? t.searchStatusIncomplete : t.searchStatusSearchDone;
            }} catch (exc) {{
                error.textContent = exc.message || (currentLang === 'vi' ? 'Mất kết nối server. Hãy chạy lại ./trending --serve.' : 'Server connection lost. Please restart ./trending --serve.');
                status.textContent = t.searchStatusError;
            }} finally {{
                searching = false; button.disabled = false; button.textContent = t.searchBtn;
            }}
        }}

        function updateSearchMode() {{
            if (!searchEndpoint) return;
            const t = I18N[currentLang];
            const hasKeyword = Boolean(document.getElementById('searchInput').value.trim());
            document.getElementById('githubSort').disabled = !hasKeyword;
            document.getElementById('keywordMode').disabled = !hasKeyword;
            document.getElementById('trendingPeriod').disabled = hasKeyword;
            const content = document.getElementById('searchScope').value === 'content';
            document.getElementById('searchInput').placeholder = content ? t.searchPlaceholderContent : t.searchPlaceholderName;
            document.getElementById('searchHelp').textContent = !hasKeyword
                ? t.searchHelpEmpty
                : content
                    ? t.searchHelpContent
                    : t.searchHelpName;
        }}

        document.getElementById('searchInput').addEventListener('input', updateSearchMode);
        document.getElementById('searchScope').addEventListener('change', updateSearchMode);
        document.getElementById('searchForm').addEventListener('submit', event => {{
            event.preventDefault(); searchProjects();
        }});
        document.getElementById('resetSearch').addEventListener('click', () => {{
            document.getElementById('searchForm').reset();
            updateSearchMode();
            document.getElementById('searchError').textContent = '';
            document.getElementById('searchStatus').textContent = '';
            ['repoTypeFilter', 'categoryFilter', 'maturityFilter', 'velocityFilter', 'statusFilter'].forEach(id => {{ const el = document.getElementById(id); if (el) el.value = ''; }});
            ['watchlistOnly', 'altOnly'].forEach(id => document.getElementById(id).checked = false);
            filterCards();
        }});

        // Initialize Language and Render
        setLanguage(currentLang);
    </script>
</body>
</html>
"""
    return html


def save_and_open_html_dashboard(
    analyses: List[RepoAnalysis],
    output_path: str = "trending_dashboard.html",
    timeframe: str = "daily",
    language: str = None,
    open_browser: bool = True
) -> str:
    """Generate, save, and optionally open the HTML dashboard."""
    html_content = generate_html_dashboard(analyses, timeframe=timeframe, language=language)
    abs_path = os.path.abspath(output_path)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    if open_browser:
        try:
            webbrowser.open(f"file://{abs_path}")
        except Exception:
            pass

    return abs_path
