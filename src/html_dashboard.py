"""HTML Dashboard Generator for GitHub Trending Analyzer (zero external dependencies)."""

import json
import os
import webbrowser
from datetime import datetime
from typing import List

from src.analyzer import RepoAnalysis


def generate_html_dashboard(analyses: List[RepoAnalysis], timeframe: str = "daily", language: str = None, search_endpoint: str = None, default_deep: bool = False) -> str:
    """Generate a modern, responsive single-file HTML dashboard with filters and quick run."""
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
        .search-box {{
            flex: 1;
            min-width: 250px;
            position: relative;
        }}
        .search-box input {{
            width: 100%;
            padding: 10px 16px;
            background: #0d1117;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-bright);
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-box input:focus {{
            border-color: var(--accent-blue);
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
                    <h1>🔥 GitHub Trending Analyzer</h1>
                    <p style="color: var(--text-muted); margin-top: 6px; font-size: 0.92rem;">
                        Tự động phân tích tác dụng cốt lõi, tốc độ bứt phá, độ hoàn thiện và đề xuất theo sở thích của bạn.
                    </p>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span id="sourceBadge" class="badge badge-time">📅 {time_display}</span>
                    <span class="badge badge-lang">💻 {lang_display}</span>
                    <span id="loadedCount" class="badge badge-count">📦 {len(analyses)} dự án</span>
                </div>
            </div>

            <form id="searchForm" class="search-form">
                <div class="search-field keyword-field">
                    <label for="searchInput">Từ khóa</label>
                    <input type="search" id="searchInput" placeholder="Ví dụ: agent, voice, Unity" autocomplete="off" aria-describedby="searchHelp">
                </div>
                <div class="search-field" {'hidden' if not search_endpoint else ''}>
                    <label for="searchScope">Tìm kiếm theo</label>
                    <select id="searchScope">
                        <option value="name">Tên project</option>
                        <option value="content">Từ khóa bên trong project (README)</option>
                    </select>
                </div>
                <div class="search-field limit-field">
                    <label for="resultLimit">Số lượng project</label>
                    <input type="number" id="resultLimit" min="1" max="30" step="1" value="10" required>
                </div>
                <div class="search-field">
                    <label for="keywordMode">Cách khớp từ khóa</label>
                    <select id="keywordMode">
                        <option value="all">Khớp tất cả từ khóa</option>
                        <option value="any">Khớp ít nhất một từ khóa</option>
                    </select>
                </div>
                <div class="search-field" {'hidden' if not search_endpoint else ''}>
                    <label for="githubLanguage">Ngôn ngữ</label>
                    <input id="githubLanguage" placeholder="Python, Rust, C#..." maxlength="40" style="width:170px">
                </div>
                <div class="search-field" {'hidden' if not search_endpoint else ''}>
                    <label for="githubSort">Sắp xếp khi có từ khóa</label>
                    <select id="githubSort"><option value="best-match">Phù hợp nhất</option><option value="stars">Nhiều stars nhất</option><option value="updated">Cập nhật gần nhất</option></select>
                </div>
                <div class="search-field" {'hidden' if not search_endpoint else ''}>
                    <label for="trendingPeriod">Kỳ Trending (khi từ khóa trống)</label>
                    <select id="trendingPeriod"><option value="daily">Hôm nay</option><option value="weekly">Tuần này</option><option value="monthly">Tháng này</option></select>
                </div>
                <label {'hidden' if not search_endpoint else ''}><input id="deepResearch" type="checkbox" {'checked' if default_deep else ''}> Phân tích sâu (chậm hơn)</label>
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
                    <input type="checkbox" id="watchlistOnly" onchange="filterCards()"> ⭐ Khớp sở thích (>0%)
                </label>
                <label class="checkbox-filter" style="color: #d2a8ff;">
                    <input type="checkbox" id="altOnly" onchange="filterCards()"> 💡 Thay thế thương mại
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
        const periodLabels = {{daily: 'Hôm nay', weekly: 'Tuần này', monthly: 'Tháng này'}};
        let searching = false;

        // Populate category dropdown
        const categoryFilter = document.getElementById("categoryFilter");
        function populateCategories() {{
            categoryFilter.replaceChildren();
            const all = document.createElement('option'); all.value = ''; all.textContent = 'Tất cả phân loại';
            categoryFilter.appendChild(all);
            [...new Set(reposData.map(r => r.category).filter(Boolean))].forEach(cat => {{
                const opt = document.createElement('option'); opt.value = cat; opt.textContent = cat;
                categoryFilter.appendChild(opt);
            }});
        }}
        populateCategories();

        function copyCmd(btn, text) {{
            navigator.clipboard.writeText(text).then(() => {{
                const old = btn.textContent;
                btn.textContent = "✓ Đã copy!";
                setTimeout(() => {{ btn.textContent = old; }}, 2000);
            }}).catch(() => {{
                prompt("Copy lệnh sau:", text);
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

                const featuresHtml = (r.key_features || []).map(f => `<li>${{f}}</li>`).join("");
                const techStackHtml = (r.tech_stack || []).map(t => `<span class="tech-pill">${{t}}</span>`).join("");

                const velClass = getVelocityBadgeClass(r.velocity_badge);
                const matClass = getMaturityBadgeClass(r.maturity_level);
                const growth = raw.growth;
                const growthHtml = growth ? `
                    <div class="section-title">📈 TĂNG TRƯỞNG STARS</div>
                    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:8px;">
                        ${{[['daily', 'Hôm nay'], ['weekly', '7 ngày'], ['monthly', '30 ngày']].map(([key, label]) =>
                            `<span class="tech-pill">${{label}}: ${{Number.isInteger(growth[key]) && growth[key] >= 0 ? '+' + growth[key].toLocaleString('vi-VN') : 'Chưa có dữ liệu'}}</span>`).join('')}}
                    </div>
                    <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:12px;">${{escapeText(growth.note || '')}} · Cache tối đa 10 phút</div>
                ` : '';

                card.innerHTML = `
                    <div>
                        <div class="card-header">
                            <a href="${{r.url}}" target="_blank" class="repo-title">📦 ${{r.name}}</a>
                            <span class="stars-pill">${{r.timeframe === "search" ? `★ ${{r.stars_total}}` : `★ +${{r.stars_since || "0"}} · ${{periodLabels[r.timeframe] || r.timeframe}}`}}</span>
                        </div>

                        <!-- Status & Category Badges -->
                        <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px;">
                            <span class="pill-tag tag-category">🏷️ ${{r.category}}</span>
                            ${{r.repo_type_badge ? `<span class="pill-tag tag-repo-type">${{r.repo_type_badge}}</span>` : ''}}
                            ${{r.grounding_score ? `<span class="pill-tag tag-grounding" title="Chỉ số phản biện & kiểm chứng: ${{r.grounding_score}}/100">🛡️ Grounding: ${{r.grounding_score}}/100</span>` : ''}}
                            ${{r.is_new_entry ? '<span class="pill-tag tag-new-entry" title="Lần đầu xuất hiện trong hệ thống">🌱 Mới xuất hiện</span>' : `<span class="pill-tag tag-returning" title="Đã xuất hiện ${{r.times_seen || 1}} lần">🔄 Đã gặp ${{r.times_seen || 1}} lần</span>`}}
                            ${{r.velocity_badge ? `<span class="pill-tag ${{velClass}}">${{r.velocity_badge}}</span>` : ''}}
                            ${{r.maturity_badge ? `<span class="pill-tag ${{matClass}}">${{r.maturity_badge}}</span>` : ''}}
                            ${{r.commercial_alternative ? `<span class="pill-tag tag-alternative">💡 Thay thế: ${{r.commercial_alternative}}</span>` : ''}}
                            ${{r.match_score > 0 ? `<span class="pill-tag tag-match">⭐ ${{r.match_score}}% Match</span>` : ''}}
                        </div>

                        <!-- Feedback Toolbar -->
                        <div class="feedback-bar">
                            <div class="rating-buttons">
                                <button type="button" class="btn-rate btn-like ${{raw.user_rating === 1 ? 'active' : ''}}" title="Hữu ích / Đánh giá tốt" data-action="like">👍</button>
                                <button type="button" class="btn-rate btn-dislike ${{raw.user_rating === -1 ? 'active' : ''}}" title="Chưa hữu ích" data-action="dislike">👎</button>
                                <button type="button" class="btn-chat" title="Đặt câu hỏi kỹ thuật về repo này">💬 Hỏi đáp</button>
                            </div>
                            <select class="status-select" title="Trạng thái nghiên cứu">
                                <option value="unread" ${{raw.user_status === 'unread' ? 'selected' : ''}}>Trạng thái: Chưa đọc</option>
                                <option value="want_to_try" ${{raw.user_status === 'want_to_try' ? 'selected' : ''}}>🔖 Muốn thử</option>
                                <option value="tried" ${{raw.user_status === 'tried' ? 'selected' : ''}}>✅ Đã thử</option>
                                <option value="skipped" ${{raw.user_status === 'skipped' ? 'selected' : ''}}>⏭️ Bỏ qua</option>
                            </select>
                        </div>

                        <!-- Interactive Repo Q&A Chat Box -->
                        <div class="chat-container" style="display:none; margin-bottom:12px; background:rgba(22,27,34,0.95); border:1px solid var(--accent-blue); border-radius:6px; padding:10px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <span style="font-size:0.8rem; font-weight:bold; color:var(--accent-blue);">💬 Hỏi đáp chuyên sâu: ${{r.name}}</span>
                                <button type="button" class="btn-close-chat" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-size:0.9rem;">✕</button>
                            </div>
                            <div class="chat-messages" style="max-height:160px; overflow-y:auto; font-size:0.82rem; margin-bottom:8px; display:flex; flex-direction:column; gap:6px;">
                                <div style="color:var(--text-muted);">Gợi ý câu hỏi: <em>"Có chạy offline được không?", "Khác gì so với giải pháp khác?", "Cấu hình phần cứng ra sao?"</em></div>
                            </div>
                            <div style="display:flex; gap:6px;">
                                <input type="text" class="chat-input" placeholder="Nhập câu hỏi kỹ thuật..." style="flex:1; background:#0d1117; border:1px solid var(--border); color:var(--text-main); padding:4px 8px; border-radius:4px; font-size:0.82rem;">
                                <button type="button" class="btn-send-chat" style="background:var(--accent-blue); color:#000; border:none; padding:4px 10px; border-radius:4px; font-weight:bold; font-size:0.82rem; cursor:pointer;">Hỏi</button>
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
                            <div class="section-title">⚡ LỆNH CHẠY THỬ NHANH</div>
                            <div class="quick-run-box">
                                <span class="quick-run-code" title="${{r.quick_run}}">${{r.quick_run}}</span>
                                <button class="btn-copy">Copy</button>
                            </div>
                        ` : ''}}

                        <div class="section-title">🎯 LÀM GÌ & TÁC DỤNG CỐT LÕI</div>
                        <div class="core-purpose">${{r.core_purpose || r.description}}</div>

                        ${{featuresHtml ? `
                            <div class="section-title">💡 TÍNH NĂNG CHI TIẾT & ĐIỂM ĂN TIỀN</div>
                            <ul class="features-list">${{featuresHtml}}</ul>
                        ` : ''}}

                        ${{r.suitable_major ? `
                            <div class="section-title">🎓 PHÙ HỢP CHUYÊN NGÀNH</div>
                            <div style="font-size: 0.88rem; color: var(--text-bright); margin-bottom: 8px;">📚 ${{r.suitable_major}}</div>
                        ` : ''}}

                        ${{r.target_roles ? `
                            <div class="section-title">👤 VỊ TRÍ CÔNG VIỆC</div>
                            <div class="audience">${{r.target_roles}}</div>
                        ` : ''}}

                        ${{r.real_world_impact ? `
                            <div class="section-title">💥 BÀI TOÁN THỰC TẾ GIẢI QUYẾT</div>
                            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px; border-left: 2px solid var(--accent-green); padding-left: 8px;">${{r.real_world_impact}}</div>
                        ` : ''}}
                    </div>

                    <div class="card-footer">
                        <div class="meta-stats">
                            <span>💻 ${{r.language || "Unknown"}}</span>
                            <span>🌟 ${{r.stars_total}}</span>
                        </div>
                        <a href="${{r.url}}" target="_blank" class="btn-view">Mở GitHub ↗</a>
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
                        loadingMsg.textContent = '⏳ Đang phân tích câu trả lời...';
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
                            ansMsg.textContent = data.answer || 'Không có câu trả lời.';
                            chatMessages.appendChild(ansMsg);
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }} catch (e) {{
                            loadingMsg.textContent = '❌ Lỗi khi hỏi đáp: ' + e.message;
                        }}
                    }};
                    if (sendChat) sendChat.addEventListener('click', doAsk);
                    if (chatInput) chatInput.addEventListener('keydown', (e) => {{ if (e.key === 'Enter') doAsk(); }});
                }}

                const details = document.createElement('details');
                const summary = document.createElement('summary');
                summary.textContent = `Phân tích sâu · ${{raw.engine_used}} · ${{raw.data_sources?.length || 0}} nguồn`;
                summary.style.cssText = 'cursor:pointer;color:var(--accent-blue);padding:12px 0';
                details.appendChild(summary);
                const topics = [
                    ['Cách hoạt động & kiến trúc', 'how_it_works'],
                    ['Ví dụ thực tế & cách đánh giá', 'practical_examples'],
                    ['Giới hạn & trường hợp không phù hợp', 'limitations'],
                    ['Yêu cầu triển khai & tích hợp', 'adoption_notes'],
                    ['So sánh & trade-off', 'comparisons'],
                    ['Cần kiểm chứng thêm', 'research_gaps'],
                    ['🛡️ Tự phản biện & Kiểm chứng khách quan', 'grounding_critique'],
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
            document.getElementById('resultsSummary').textContent = `Hiển thị ${{visible.length}} / ${{filtered.length}} kết quả phù hợp · ${{reposData.length}} project đã tải${{githubTotal === null ? "" : (resultMode === 'trending' ? ` / ${{githubTotal}} project trong danh sách Trending` : ` / ${{githubTotal}} kết quả GitHub`)}}`;
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
                console.warn('Lỗi lưu phản hồi:', err);
            }}
        }}

        const syncWatchlistBtn = document.getElementById('syncWatchlistBtn');
        if (syncWatchlistBtn) {{
            syncWatchlistBtn.addEventListener('click', async () => {{
                syncWatchlistBtn.disabled = true;
                syncWatchlistBtn.textContent = 'Đang học…';
                try {{
                    const response = await fetch('/api/sync-watchlist', {{ method: 'POST' }});
                    const data = await response.json();
                    if (data.status === 'success') {{
                        const added = data.added || {{}};
                        const info = [];
                        if (added.keywords && added.keywords.length) info.push(`• Từ khóa: ${{added.keywords.join(', ')}}`);
                        if (added.languages && added.languages.length) info.push(`• Ngôn ngữ: ${{added.languages.join(', ')}}`);
                        if (added.categories && added.categories.length) info.push(`• Chuyên mục: ${{added.categories.join(', ')}}`);
                        alert(info.length ? `🧠 Đã học và cập nhật watchlist với:\n\n${{info.join('\n')}}` : 'Chưa có đủ repo được like hoặc đánh dấu "Muốn thử" để học.');
                    }} else {{
                        alert('Lỗi: ' + (data.error || 'Không đồng bộ được'));
                    }}
                }} catch (e) {{
                    alert('Lỗi kết nối khi đồng bộ sở thích.');
                }} finally {{
                    syncWatchlistBtn.disabled = false;
                    syncWatchlistBtn.textContent = '🧠 Đồng bộ sở thích';
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
            button.disabled = true; button.textContent = 'Đang tìm kiếm…'; error.textContent = '';
            status.textContent = 'Đang tìm trên GitHub và đọc tài liệu project. Phân tích sâu có thể mất vài phút.';
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
                if (!response.ok) throw new Error(data.error || 'Không tìm kiếm được.');
                reposData = data.results; githubTotal = data.total_count; resultMode = data.mode;
                document.getElementById('sourceBadge').textContent = resultMode === 'trending' ? `📈 Trending · ${{periodLabels[data.timeframe]}}` : `🔎 GitHub Search · ${{data.scope === 'content' ? 'Nội dung README' : 'Tên project'}}`;
                document.getElementById('velocityFilter').hidden = resultMode !== 'trending';
                populateCategories();
                ['repoTypeFilter', 'maturityFilter', 'velocityFilter', 'statusFilter'].forEach(id => {{ const el = document.getElementById(id); if (el) el.value = ''; }});
                ['watchlistOnly', 'altOnly'].forEach(id => document.getElementById(id).checked = false);
                document.getElementById('loadedCount').textContent = `📦 ${{reposData.length}} dự án`;
                filterCards();
                status.textContent = resultMode === 'trending' ? 'Đã lấy Trending, sắp xếp theo số stars mới từ cao xuống thấp.' : data.incomplete_results ? 'GitHub trả kết quả chưa đầy đủ; có thể thử lại với truy vấn cụ thể hơn.' : 'Đã tìm và phân tích xong.';
            }} catch (exc) {{
                error.textContent = exc.message || 'Mất kết nối server. Hãy chạy lại ./trending --serve.';
                status.textContent = 'Tìm kiếm chưa hoàn thành; danh sách trước đó được giữ lại.';
            }} finally {{
                searching = false; button.disabled = false; button.textContent = '🔍 Tìm kiếm';
            }}
        }}
        function updateSearchMode() {{
            if (!searchEndpoint) return;
            const hasKeyword = Boolean(document.getElementById('searchInput').value.trim());
            document.getElementById('githubSort').disabled = !hasKeyword;
            document.getElementById('keywordMode').disabled = !hasKeyword;
            document.getElementById('trendingPeriod').disabled = hasKeyword;
            const content = document.getElementById('searchScope').value === 'content';
            document.getElementById('searchInput').placeholder = content ? 'Ví dụ: voice cloning, rag, image generation' : 'Ví dụ: VoiceStudio, OpenShell';
            document.getElementById('searchHelp').textContent = !hasKeyword
                ? 'Để trống từ khóa: lấy GitHub Trending, xếp theo stars mới giảm dần. Tối đa 30 project mỗi lượt.'
                : content
                    ? 'Tìm từ khóa trong README của project trên GitHub. Nhiều từ khóa ngăn cách bằng dấu phẩy.'
                    : 'Tìm từ khóa trong tên repository trên GitHub. Nhiều từ khóa ngăn cách bằng dấu phẩy.';
        }}
        document.getElementById('searchInput').addEventListener('input', updateSearchMode);
        document.getElementById('searchScope').addEventListener('change', updateSearchMode);
        updateSearchMode();
        document.getElementById('searchForm').addEventListener('submit' , event => {{
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
        // Initial render uses the same limit and summary as an explicit search.
        filterCards();
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
