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

        /* Unified Modern Search Form */
        .search-form {{
            margin-top: 18px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .search-bar-primary {{
            display: flex;
            align-items: center;
            background: var(--bg-main);
            border: 1.5px solid var(--border);
            border-radius: 12px;
            padding: 5px 8px;
            gap: 8px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
            transition: all 0.2s ease;
        }}
        .search-bar-primary:focus-within {{
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.2);
        }}
        .search-scope-wrapper {{
            position: relative;
            flex-shrink: 0;
        }}
        .search-scope-select {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-bright);
            font-size: 0.85rem;
            font-weight: 600;
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            outline: none;
            transition: all 0.15s ease;
        }}
        .search-scope-select:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--border-hover);
        }}
        .search-input-wrapper {{
            display: flex;
            align-items: center;
            flex: 1;
            position: relative;
        }}
        .search-input-wrapper .search-icon {{
            font-size: 1rem;
            color: var(--text-muted);
            margin-left: 6px;
            margin-right: 6px;
            pointer-events: none;
            user-select: none;
        }}
        .search-input-wrapper input[type="search"] {{
            width: 100%;
            background: transparent;
            border: none;
            color: var(--text-bright);
            font-size: 0.95rem;
            padding: 8px 4px;
            outline: none;
        }}
        .search-input-wrapper input[type="search"]::placeholder {{
            color: #6e7681;
        }}
        .clear-input-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 0.9rem;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 50%;
            transition: color 0.15s ease;
        }}
        .clear-input-btn:hover {{
            color: var(--text-bright);
        }}
        .search-button {{
            padding: 9px 18px;
            border: 1px solid var(--accent-blue);
            border-radius: 8px;
            background: var(--accent-blue);
            color: #0d1117;
            font: inherit;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.15s ease;
        }}
        .search-button:hover {{
            background: #79c0ff;
            border-color: #79c0ff;
        }}
        .btn-toggle-advanced {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-muted);
            padding: 9px 14px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.15s ease;
        }}
        .btn-toggle-advanced:hover, .btn-toggle-advanced.active, .btn-toggle-advanced.has-active-filters {{
            background: rgba(88, 166, 255, 0.12);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}
        .advanced-badge {{
            background: var(--accent-blue);
            color: #0d1117;
            font-size: 0.72rem;
            font-weight: 800;
            border-radius: 10px;
            padding: 1px 6px;
        }}

        /* Collapsible Advanced Options Panel */
        .advanced-search-panel {{
            background: #161b22;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
            animation: fadeInPanel 0.2s ease-out;
        }}
        @keyframes fadeInPanel {{
            from {{ opacity: 0; transform: translateY(-6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .advanced-panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 10px;
            margin-bottom: 12px;
            border-bottom: 1px solid rgba(48, 54, 61, 0.6);
        }}
        .advanced-panel-title {{
            font-size: 0.88rem;
            font-weight: 700;
            color: var(--text-bright);
        }}
        .btn-close-advanced {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 1rem;
            cursor: pointer;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .btn-close-advanced:hover {{
            color: var(--text-bright);
            background: rgba(255, 255, 255, 0.08);
        }}
        .advanced-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }}
        .advanced-field {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .advanced-field label {{
            color: var(--text-muted);
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .advanced-field input, .advanced-field select {{
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--bg-main);
            color: var(--text-bright);
            font: inherit;
            font-size: 0.88rem;
            outline: none;
        }}
        .advanced-field input:focus, .advanced-field select:focus {{
            border-color: var(--accent-blue);
        }}
        .advanced-panel-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 12px;
            margin-top: 12px;
            border-top: 1px solid rgba(48, 54, 61, 0.6);
        }}
        .btn-reset-options {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 0.82rem;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .btn-reset-options:hover {{
            color: var(--accent-red);
            border-color: var(--accent-red);
        }}
        .btn-collapse-panel {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-bright);
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
        }}
        .btn-collapse-panel:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}

        /* Search Meta Bar (Status & Summary Strip) */
        .search-meta-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
            gap: 10px;
            flex-wrap: wrap;
            min-height: 28px;
        }}
        .meta-left {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .meta-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 14px;
            font-size: 0.82rem;
            font-weight: 600;
        }}
        .meta-summary {{
            background: rgba(88, 166, 255, 0.12);
            color: var(--accent-blue);
            border: 1px solid rgba(88, 166, 255, 0.3);
        }}
        .meta-status {{
            background: rgba(210, 153, 34, 0.15);
            color: var(--accent-yellow);
            border: 1px solid rgba(210, 153, 34, 0.35);
        }}
        .meta-error {{
            background: rgba(248, 81, 73, 0.15);
            color: var(--accent-red);
            border: 1px solid rgba(248, 81, 73, 0.35);
        }}
        .btn-help-hint {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 0.82rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 8px;
            border-radius: 6px;
            transition: all 0.15s ease;
        }}
        .btn-help-hint:hover {{
            color: var(--accent-blue);
            background: rgba(88, 166, 255, 0.08);
        }}
        .search-help-box {{
            background: rgba(22, 27, 34, 0.8);
            border: 1px dashed var(--border);
            border-radius: 8px;
            padding: 8px 12px;
            margin-top: 6px;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}

        @media (max-width: 768px) {{
            body {{ padding: 12px; }}
            header {{ padding: 16px; }}
            .search-bar-primary {{ flex-wrap: wrap; }}
            .search-scope-wrapper {{ width: 100%; }}
            .search-scope-select {{ width: 100%; }}
            .search-input-wrapper {{ width: 100%; }}
            .search-button, .btn-toggle-advanced {{ flex: 1; }}
        }}

        /* Secondary Filter Toolbar */
        .controls {{
            display: flex;
            gap: 8px;
            margin-top: 14px;
            flex-wrap: wrap;
            align-items: center;
            background: rgba(13, 17, 23, 0.6);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 12px;
        }}
        .filter-toolbar-label {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-muted);
            margin-right: 4px;
            white-space: nowrap;
        }}
        .select-filter {{
            padding: 6px 10px;
            background: #161b22;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-bright);
            font-size: 0.84rem;
            outline: none;
            cursor: pointer;
        }}
        .select-filter:hover {{
            border-color: var(--border-hover);
        }}
        .checkbox-filter {{
            display: flex;
            align-items: center;
            gap: 6px;
            background: #161b22;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 6px 10px;
            color: var(--accent-yellow);
            font-size: 0.82rem;
            cursor: pointer;
            user-select: none;
        }}
        .checkbox-filter:hover {{
            border-color: var(--border-hover);
        }}
        .btn-clear-filters {{
            background: transparent;
            border: 1px dashed var(--border);
            color: var(--text-muted);
            border-radius: 6px;
            padding: 5px 10px;
            font-size: 0.8rem;
            cursor: pointer;
            margin-left: auto;
            white-space: nowrap;
            transition: all 0.15s ease;
        }}
        .btn-clear-filters:hover {{
            color: var(--accent-red);
            border-color: var(--accent-red);
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

        /* Deep Dive Modal & Tabs */
        .modal-backdrop {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(5px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            padding: 20px;
            box-sizing: border-box;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }}
        .modal-backdrop.open {{
            opacity: 1;
            pointer-events: auto;
        }}
        .modal-dialog {{
            background: #0d1117;
            border: 1px solid var(--border);
            border-radius: 12px;
            width: 100%;
            max-width: 900px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7);
            overflow: hidden;
            transform: translateY(20px);
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .modal-backdrop.open .modal-dialog {{
            transform: translateY(0);
        }}
        .modal-header {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #161b22;
        }}
        .modal-header-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--text-bright);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .modal-header-title a {{
            color: var(--accent-blue);
            text-decoration: none;
        }}
        .modal-header-title a:hover {{
            text-decoration: underline;
        }}
        .modal-close-btn {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 1.2rem;
            cursor: pointer;
            border-radius: 6px;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }}
        .modal-close-btn:hover {{
            color: #fff;
            border-color: #8b949e;
            background: #21262d;
        }}
        .modal-badges {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            padding: 10px 20px;
            background: #0d1117;
            border-bottom: 1px solid var(--border);
        }}
        .modal-tabs {{
            display: flex;
            gap: 4px;
            padding: 8px 16px;
            background: #161b22;
            border-bottom: 1px solid var(--border);
            overflow-x: auto;
        }}
        .modal-tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 8px 14px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .modal-tab-btn:hover {{
            color: var(--text-bright);
            background: rgba(255, 255, 255, 0.05);
        }}
        .modal-tab-btn.active {{
            color: #000;
            background: var(--accent-blue);
        }}
        .modal-body {{
            padding: 20px;
            overflow-y: auto;
            font-size: 0.9rem;
            line-height: 1.6;
            color: #c9d1d9;
            flex: 1;
        }}
        .modal-tab-pane {{
            display: none;
        }}
        .modal-tab-pane.active {{
            display: block;
        }}
        .evidence-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 14px;
        }}
        .evidence-title {{
            font-size: 0.88rem;
            font-weight: bold;
            color: var(--accent-purple);
            margin-bottom: 8px;
        }}
        .evidence-content {{
            font-size: 0.85rem;
            white-space: pre-wrap;
            word-break: break-word;
        }}
        .evidence-code-block {{
            background: #0d1117;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 12px;
            margin: 8px 0;
            position: relative;
            overflow-x: auto;
            font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
            font-size: 0.84rem;
        }}
        .btn-deep-dive {{
            background: #21262d;
            border: 1px solid var(--accent-blue);
            color: var(--accent-blue);
            padding: 7px 14px;
            border-radius: 6px;
            font-size: 0.84rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
            margin-top: 10px;
            margin-bottom: 10px;
            width: 100%;
            justify-content: center;
        }}
        .btn-deep-dive:hover {{
            background: var(--accent-blue);
            color: #000;
        }}

        /* Domain Presets Quick-Filter Bar */
        .preset-filters-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 16px;
            padding: 10px 14px;
            background: #161b22;
            border: 1px solid var(--border);
            border-radius: 8px;
            flex-wrap: wrap;
        }}
        .preset-pills-wrap {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .preset-label {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-right: 4px;
        }}
        .preset-pill {{
            background: #21262d;
            border: 1px solid #30363d;
            color: var(--text-main);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }}
        .preset-pill:hover {{
            background: #30363d;
            border-color: var(--accent-blue);
            color: #fff;
        }}
        .preset-pill.active {{
            background: rgba(56, 139, 253, 0.15);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
            font-weight: 600;
        }}
        .preset-count {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 1px 6px;
            font-size: 0.72rem;
            color: #c9d1d9;
        }}
        .btn-toggle-analytics {{
            background: rgba(35, 134, 54, 0.15);
            border: 1px solid #2ea043;
            color: #3fb950;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
            margin-left: auto;
        }}
        .btn-toggle-analytics:hover {{
            background: #238636;
            color: #fff;
        }}
        .btn-rate.btn-bookmark {{
            color: #d29922;
            background: rgba(210, 153, 34, 0.1);
            border-color: rgba(210, 153, 34, 0.35);
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 0.78rem;
            padding: 3px 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-rate.btn-bookmark:hover {{
            background: rgba(210, 153, 34, 0.25);
            border-color: #d29922;
            color: #e3b341;
        }}
        .btn-rate.btn-bookmark.active {{
            background: #d29922;
            color: #0d1117;
            font-weight: 700;
            border-color: #e3b341;
            box-shadow: 0 0 8px rgba(210, 153, 34, 0.4);
        }}
        .preset-pill.preset-bm-pill {{
            border-color: rgba(210, 153, 34, 0.4);
            color: #d29922;
        }}
        .preset-pill.preset-bm-pill.active {{
            background: rgba(210, 153, 34, 0.22);
            border-color: #e3b341;
            color: #f0c674;
        }}
        .bookmark-summary {{
            background: rgba(210, 153, 34, 0.08);
            border-left: 3px solid #d29922;
            border-radius: 4px;
            padding: 6px 10px;
            margin-bottom: 10px;
            font-size: 0.8rem;
        }}
        .bm-tag-pill {{
            display: inline-block;
            background: rgba(210, 153, 34, 0.2);
            color: #e3b341;
            padding: 1px 7px;
            border-radius: 12px;
            font-size: 0.72rem;
            font-weight: 600;
            border: 1px solid rgba(210, 153, 34, 0.35);
        }}
        .btn-edit-bm {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 0.75rem;
            padding: 0 4px;
        }}
        .btn-edit-bm:hover {{
            color: #e3b341;
        }}
        .bookmark-editor {{
            background: rgba(22, 27, 34, 0.98);
            border: 1px solid #d29922;
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 12px;
            animation: fadeIn 0.2s ease;
        }}
        .modal-backdrop {{
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(3px);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .export-modal-box {{
            background: #161b22;
            border: 1px solid var(--border);
            border-radius: 8px;
            width: 90%;
            max-width: 680px;
            padding: 18px 22px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        }}
        .topics-bar {{
            background: rgba(22, 27, 34, 0.7);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 14px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .topic-pill {{
            background: #21262d;
            border: 1px solid rgba(88, 166, 255, 0.25);
            color: #58a6ff;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.76rem;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }}
        .topic-pill:hover {{
            background: rgba(56, 139, 253, 0.2);
            border-color: #58a6ff;
            color: #79c0ff;
        }}
        .topic-pill.active {{
            background: #1f6feb;
            border-color: #58a6ff;
            color: #ffffff;
            font-weight: 700;
            box-shadow: 0 0 8px rgba(31, 111, 235, 0.5);
        }}
        .card-topic-tag {{
            display: inline-block;
            background: rgba(56, 139, 253, 0.1);
            color: #58a6ff;
            border: 1px solid rgba(56, 139, 253, 0.25);
            padding: 1px 7px;
            border-radius: 10px;
            font-size: 0.72rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .card-topic-tag:hover {{
            background: rgba(56, 139, 253, 0.28);
            border-color: #58a6ff;
            color: #ffffff;
        }}

        /* Analytics & Chart Panel */
        .analytics-panel {{
            background: #161b22;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 18px 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            animation: fadeIn 0.25s ease;
        }}
        .analytics-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 10px;
            margin-bottom: 14px;
        }}
        .analytics-header h3 {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-bright);
            margin: 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .analytics-sub {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}
        .velocity-chart-bars {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin: 12px 0 20px 0;
        }}
        .velocity-bar-row {{
            display: grid;
            grid-template-columns: 220px 1fr 100px;
            align-items: center;
            gap: 12px;
            font-size: 0.83rem;
        }}
        .velocity-bar-name {{
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            color: var(--text-bright);
            font-weight: 500;
            text-decoration: none;
        }}
        .velocity-bar-name:hover {{
            color: var(--accent-blue);
            text-decoration: underline;
        }}
        .velocity-bar-bg {{
            background: #21262d;
            border-radius: 6px;
            height: 18px;
            overflow: hidden;
            position: relative;
        }}
        .velocity-bar-fill {{
            height: 100%;
            border-radius: 6px;
            background: linear-gradient(90deg, #238636, #3fb950);
            transition: width 0.4s ease;
        }}
        .velocity-bar-val {{
            text-align: right;
            font-weight: 600;
            color: var(--accent-green);
            font-size: 0.82rem;
        }}
        .analytics-grid-two {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            border-top: 1px solid var(--border);
            padding-top: 14px;
        }}
        @media (max-width: 768px) {{
            .analytics-grid-two {{ grid-template-columns: 1fr; }}
            .velocity-bar-row {{ grid-template-columns: 130px 1fr 80px; }}
        }}
        .analytics-card {{
            background: #0d1117;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 14px;
        }}
        .analytics-card h4 {{
            margin: 0 0 10px 0;
            font-size: 0.88rem;
            color: var(--text-muted);
            font-weight: 600;
        }}
        .domain-stacked-bar {{
            height: 16px;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            background: #21262d;
            margin-bottom: 12px;
        }}
        .domain-legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            font-size: 0.78rem;
        }}
        .legend-item {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: #c9d1d9;
        }}
        .legend-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }}
        .maturity-bars {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .maturity-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.8rem;
        }}
        .mini-momentum-pill {{
            font-size: 0.72rem;
            font-weight: 600;
            border-radius: 10px;
            padding: 2px 7px;
            background: rgba(56, 139, 253, 0.15);
            color: var(--accent-blue);
            display: inline-flex;
            align-items: center;
            gap: 4px;
            margin-left: 6px;
        }}
        /* 1-Click IDE Launch Menu */
        .footer-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .ide-dropdown-wrapper {{
            position: relative;
            display: inline-block;
        }}
        .btn-ide {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-bright);
            padding: 5px 9px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.15s ease;
        }}
        .btn-ide:hover {{
            background: rgba(88, 166, 255, 0.15);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}
        .ide-menu {{
            display: none;
            position: absolute;
            bottom: calc(100% + 6px);
            right: 0;
            background: #161b22;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 6px;
            min-width: 175px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            z-index: 50;
            flex-direction: column;
            gap: 2px;
        }}
        .ide-dropdown-wrapper:hover .ide-menu,
        .ide-dropdown-wrapper:focus-within .ide-menu {{
            display: flex;
        }}
        .ide-menu-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 7px 10px;
            border-radius: 6px;
            color: var(--text-main);
            text-decoration: none;
            font-size: 0.82rem;
            font-weight: 500;
            transition: background 0.12s ease;
        }}
        .ide-menu-item:hover {{
            background: rgba(88, 166, 255, 0.12);
            color: var(--text-bright);
        }}

        /* Compare Button on Card */
        .btn-compare {{
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-muted);
            padding: 4px 8px;
            font-size: 0.8rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.15s ease;
        }}
        .btn-compare:hover {{
            border-color: var(--accent-purple);
            color: var(--accent-purple);
            background: rgba(188, 140, 255, 0.08);
        }}
        .btn-compare.active {{
            background: rgba(188, 140, 255, 0.18);
            border-color: var(--accent-purple);
            color: #d2a8ff;
            font-weight: 700;
        }}

        /* Floating Compare Dock */
        .compare-dock {{
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(22, 27, 34, 0.95);
            backdrop-filter: blur(8px);
            border: 1.5px solid var(--accent-purple);
            border-radius: 30px;
            padding: 8px 18px;
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6), 0 0 15px rgba(188, 140, 255, 0.25);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 16px;
            max-width: 90vw;
            animation: slideUpDock 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        @keyframes slideUpDock {{
            from {{ transform: translate(-50%, 30px); opacity: 0; }}
            to {{ transform: translate(-50%, 0); opacity: 1; }}
        }}
        .compare-dock-inner {{
            display: flex;
            align-items: center;
            gap: 14px;
            flex-wrap: wrap;
        }}
        .compare-dock-info {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .compare-dock-title {{
            font-size: 0.85rem;
            font-weight: 700;
            color: #d2a8ff;
            white-space: nowrap;
        }}
        .compare-chips {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}
        .compare-chip {{
            background: #0d1117;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 3px 10px;
            font-size: 0.78rem;
            color: var(--text-bright);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .compare-chip-remove {{
            cursor: pointer;
            color: var(--text-muted);
            font-weight: bold;
            font-size: 0.85rem;
        }}
        .compare-chip-remove:hover {{
            color: var(--accent-red);
        }}
        .compare-dock-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .btn-launch-compare {{
            background: var(--accent-purple);
            border: 1px solid #d2a8ff;
            color: #0d1117;
            font-weight: 800;
            font-size: 0.85rem;
            padding: 6px 14px;
            border-radius: 20px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
        }}
        .btn-launch-compare:hover {{
            background: #d2a8ff;
            box-shadow: 0 0 12px rgba(188, 140, 255, 0.5);
        }}
        .btn-clear-compare {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 1rem;
            cursor: pointer;
            padding: 4px;
            border-radius: 50%;
        }}
        .btn-clear-compare:hover {{
            color: var(--text-bright);
        }}

        /* Comparison Modal */
        .comparison-modal-dialog {{
            background: #0d1117;
            border: 1.5px solid var(--border);
            border-radius: 14px;
            width: 95vw;
            max-width: 1200px;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
            transform: translateY(20px);
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .modal-backdrop.open .comparison-modal-dialog {{
            transform: translateY(0);
        }}
        .comparison-modal-body {{
            padding: 20px;
            overflow-y: auto;
            flex: 1;
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
            align-items: stretch;
        }}
        .comparison-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .comparison-card-header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
        }}
        .comparison-section-title {{
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .comparison-section-content {{
            font-size: 0.85rem;
            color: var(--text-bright);
            line-height: 1.45;
        }}

        /* Star History Curve */
        .star-history-wrapper {{
            background: #090d12;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            margin-top: 14px;
            text-align: center;
        }}
        .star-history-img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            filter: contrast(1.05);
        }}
        /* 1-Click Run & Playground Button */
        .btn-playground {{
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(99, 102, 241, 0.15));
            border: 1px solid rgba(56, 189, 248, 0.4);
            color: #38bdf8;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s ease;
        }}
        .btn-playground:hover {{
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(99, 102, 241, 0.3));
            border-color: #38bdf8;
            color: #ffffff;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
            transform: translateY(-1px);
        }}

        /* Playground Modal Dialog */
        .playground-modal-dialog {{
            background: #0d1117;
            border: 1.5px solid rgba(56, 189, 248, 0.35);
            border-radius: 14px;
            width: 95vw;
            max-width: 950px;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.85), 0 0 25px rgba(56, 189, 248, 0.15);
        }}
        .playground-modal-body {{
            padding: 20px;
            overflow-y: auto;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        /* Playground Container & Tabs */
        .playground-container {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .playground-meta-bar {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 0.82rem;
        }}
        .playground-subtabs {{
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
            margin-bottom: 6px;
            overflow-x: auto;
        }}
        .pg-subtab-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        .pg-subtab-btn:hover {{
            color: var(--text-bright);
            background: rgba(255, 255, 255, 0.05);
        }}
        .pg-subtab-btn.active {{
            background: rgba(56, 189, 248, 0.15);
            border-color: rgba(56, 189, 248, 0.4);
            color: #38bdf8;
        }}

        /* Cloud Launch Grid */
        .playground-cloud-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 14px;
        }}
        .playground-cloud-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            transition: all 0.2s ease;
            position: relative;
        }}
        .playground-cloud-card:hover {{
            border-color: rgba(56, 189, 248, 0.5);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        }}
        .playground-cloud-card.recommended {{
            border-color: rgba(63, 185, 80, 0.45);
            background: linear-gradient(180deg, rgba(63, 185, 80, 0.05) 0%, var(--bg-card) 100%);
        }}
        .cloud-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }}
        .cloud-card-title {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-bright);
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .cloud-card-badge {{
            font-size: 0.72rem;
            padding: 2px 7px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-muted);
            font-weight: 600;
        }}
        .cloud-card-desc {{
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.45;
            flex: 1;
        }}
        .btn-cloud-launch {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #38bdf8;
            padding: 7px 12px;
            border-radius: 6px;
            font-size: 0.83rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.15s ease;
            cursor: pointer;
        }}
        .btn-cloud-launch:hover {{
            background: #38bdf8;
            color: #0d1117;
            font-weight: 700;
        }}

        /* Playground Code Card */
        .playground-code-card {{
            background: #090d12;
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .playground-code-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #161b22;
            padding: 8px 14px;
            border-bottom: 1px solid var(--border);
            font-size: 0.82rem;
        }}
        .playground-file-pill {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-weight: 700;
            color: #e6edf3;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .playground-actions-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .btn-pg-action {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-bright);
            padding: 4px 10px;
            border-radius: 5px;
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.15s ease;
        }}
        .btn-pg-action:hover {{
            background: rgba(56, 189, 248, 0.15);
            border-color: rgba(56, 189, 248, 0.4);
            color: #38bdf8;
        }}
        .playground-code-area {{
            margin: 0;
            padding: 14px;
            background: #090d12;
            color: #79c0ff;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.84rem;
            line-height: 1.5;
            overflow-x: auto;
            max-height: 380px;
            white-space: pre;
        }}
        .playground-tip-box {{
            background: rgba(56, 189, 248, 0.06);
            border-left: 3px solid #38bdf8;
            padding: 10px 14px;
            border-radius: 0 6px 6px 0;
            font-size: 0.82rem;
            color: var(--text-main);
            line-height: 1.5;
        }}

        /* Inline Star History Card Section */
        .card-sh-section {{
            background: #090d12;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 12px;
            margin: 12px 0;
            transition: all 0.2s ease;
        }}
        .card-sh-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .card-sh-title {{
            font-size: 0.8rem;
            font-weight: 700;
            color: #d2a8ff;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .btn-toggle-card-sh {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            padding: 2px 6px;
            border-radius: 4px;
            transition: all 0.15s ease;
        }}
        .btn-toggle-card-sh:hover {{
            color: var(--text-bright);
            background: rgba(255, 255, 255, 0.08);
        }}
        .card-sh-body {{
            margin-top: 8px;
            text-align: center;
        }}
        .sh-chart-wrapper {{
            background: #0d1117;
            border: 1px solid rgba(48, 54, 61, 0.5);
            border-radius: 6px;
            padding: 6px;
            overflow: hidden;
        }}
        .card-star-history-img {{
            width: 100%;
            max-height: 220px;
            object-fit: contain;
            display: block;
            margin: 0 auto;
            border-radius: 4px;
            filter: contrast(1.04);
        }}
        .card-sh-actions {{
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 8px;
        }}
        .btn-sh-link {{
            color: var(--text-muted);
            font-size: 0.75rem;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 6px;
            border-radius: 4px;
            transition: all 0.15s ease;
        }}
        .btn-sh-link:hover {{
            color: var(--accent-blue);
            background: rgba(88, 166, 255, 0.1);
        }}
        .btn-toggle-all-sh {{
            background: #161b22;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: #d2a8ff;
            font-size: 0.82rem;
            font-weight: 600;
            padding: 6px 10px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.15s ease;
        }}
        .btn-toggle-all-sh:hover {{
            border-color: var(--accent-purple);
            background: rgba(188, 140, 255, 0.1);
        }}

        .star-history-actions {{
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 12px;
            flex-wrap: wrap;
        }}
        .btn-star-history-link {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-bright);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
        }}
        .btn-star-history-link:hover {{
            background: rgba(88, 166, 255, 0.12);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}
        /* Similar Button on Card */
        .btn-similar {{
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-muted);
            padding: 4px 8px;
            font-size: 0.8rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.15s ease;
        }}
        .btn-similar:hover {{
            border-color: var(--accent-blue);
            color: var(--accent-blue);
            background: rgba(88, 166, 255, 0.08);
        }}

        /* Similar Projects Modal */
        .similar-modal-dialog {{
            background: #0d1117;
            border: 1.5px solid var(--border);
            border-radius: 14px;
            width: 90vw;
            max-width: 980px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
            transform: translateY(20px);
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .modal-backdrop.open .similar-modal-dialog {{
            transform: translateY(0);
        }}
        .similar-modal-body {{
            padding: 18px 20px;
            overflow-y: auto;
            flex: 1;
        }}
        .similar-subtitle {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 16px;
            line-height: 1.5;
        }}
        .similar-loading {{
            padding: 30px;
            text-align: center;
            color: var(--accent-blue);
            font-size: 0.92rem;
            font-weight: 600;
        }}
        .similar-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 14px;
        }}
        .similar-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            transition: border-color 0.15s ease;
        }}
        .similar-card:hover {{
            border-color: var(--border-hover);
        }}
        .similar-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            gap: 8px;
        }}
        .similar-reason-pill {{
            font-size: 0.74rem;
            color: var(--accent-yellow);
            background: rgba(210, 153, 34, 0.12);
            border: 1px solid rgba(210, 153, 34, 0.3);
            border-radius: 12px;
            padding: 2px 8px;
            display: inline-block;
        }}
        .similar-card-actions {{
            display: flex;
            gap: 6px;
            margin-top: auto;
            padding-top: 10px;
            border-top: 1px solid rgba(48, 54, 61, 0.5);
            flex-wrap: wrap;
            align-items: center;
        }}
        .similar-modal-footer {{
            padding: 12px 20px;
            border-top: 1px solid var(--border);
            background: #161b22;
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            align-items: center;
        }}

        /* Community Pulse Styles */
        .tag-pulse {{
            border-radius: 12px;
            padding: 2px 8px;
            font-size: 0.74rem;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .tag-pulse.active {{
            background: rgba(63, 185, 80, 0.12);
            color: #3fb950;
            border: 1px solid rgba(63, 185, 80, 0.3);
        }}
        .tag-pulse.steady {{
            background: rgba(210, 153, 34, 0.12);
            color: #d29922;
            border: 1px solid rgba(210, 153, 34, 0.3);
        }}
        .tag-pulse.slow {{
            background: rgba(240, 136, 62, 0.12);
            color: #f0883e;
            border: 1px solid rgba(240, 136, 62, 0.3);
        }}
        .tag-pulse.dormant {{
            background: rgba(248, 81, 73, 0.12);
            color: #f85149;
            border: 1px solid rgba(248, 81, 73, 0.3);
        }}
        .tag-license {{
            background: rgba(188, 140, 255, 0.12);
            color: #bc8cff;
            border: 1px solid rgba(188, 140, 255, 0.3);
            border-radius: 12px;
            padding: 2px 8px;
            font-size: 0.74rem;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .pulse-wrapper {{
            display: flex;
            flex-direction: column;
            gap: 16px;
            padding: 4px 0;
        }}
        .pulse-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }}
        .pulse-stat-card {{
            background: #161b22;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 14px 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .pulse-stat-header {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .pulse-stat-val {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-bright);
        }}
        .pulse-stat-sub {{
            font-size: 0.78rem;
            color: var(--text-muted);
        }}
        .contributors-box {{
            background: #090d12;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px 18px;
        }}
        .contributors-title {{
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--accent-blue);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .contributors-list {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .contributor-item {{
            background: #161b22;
            border: 1px solid rgba(48, 54, 61, 0.7);
            border-radius: 8px;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            transition: all 0.15s ease;
        }}
        .contributor-item:hover {{
            border-color: var(--accent-blue);
            background: #1f242c;
            transform: translateY(-2px);
        }}
        .contributor-avatar {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 1px solid var(--border);
            object-fit: cover;
        }}
        .contributor-info {{
            display: flex;
            flex-direction: column;
        }}
        .contributor-login {{
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-bright);
        }}
        .contributor-commits {{
            font-size: 0.72rem;
            color: var(--text-muted);
        }}
        .pulse-verdict-box {{
            background: rgba(88, 166, 255, 0.06);
            border: 1px solid rgba(88, 166, 255, 0.25);
            border-radius: 10px;
            padding: 14px 16px;
        }}
        .pulse-verdict-title {{
            font-size: 0.88rem;
            font-weight: 700;
            color: var(--accent-blue);
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .pulse-verdict-desc {{
            font-size: 0.82rem;
            color: var(--text-main);
            line-height: 1.5;
        }}

        /* Release Radar Styles */
        .tag-release {{
            background: rgba(138, 180, 248, 0.12);
            color: #8ab4f8;
            border: 1px solid rgba(138, 180, 248, 0.3);
            border-radius: 12px;
            padding: 2px 8px;
            font-size: 0.74rem;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .release-radar-wrapper {{
            display: flex;
            flex-direction: column;
            gap: 16px;
            padding: 4px 0;
        }}
        .release-hero-card {{
            background: #161b22;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .release-hero-info {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .release-tag-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #8ab4f8;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .release-meta {{
            font-size: 0.82rem;
            color: var(--text-muted);
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .release-highlights-box {{
            background: #090d12;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px 18px;
        }}
        .release-highlights-title {{
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--accent-green);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .release-highlights-list {{
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .release-highlight-item {{
            font-size: 0.85rem;
            color: var(--text-main);
            line-height: 1.5;
            display: flex;
            align-items: flex-start;
            gap: 8px;
        }}
        .release-highlight-bullet {{
            color: var(--accent-blue);
            font-size: 0.9rem;
            line-height: 1.4;
        }}
        .release-body-box {{
            background: #0d1117;
            border: 1px solid rgba(48, 54, 61, 0.6);
            border-radius: 8px;
            padding: 12px 14px;
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.5;
            max-height: 250px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-word;
        }}
        .btn-release-github {{
            background: #21262d;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--accent-blue);
            padding: 6px 12px;
            font-size: 0.82rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
        }}
        .btn-release-github:hover {{
            background: #30363d;
            border-color: var(--accent-blue);
        }}

        /* Architecture Diagram Styles */
        .arch-wrapper {{
            display: flex;
            flex-direction: column;
            gap: 16px;
            padding: 4px 0;
        }}
        .arch-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .arch-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-bright);
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .arch-subtitle {{
            font-size: 0.84rem;
            color: var(--text-muted);
            margin-top: 4px;
        }}
        .arch-actions {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .btn-arch-action {{
            background: #21262d;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-main);
            padding: 5px 10px;
            font-size: 0.8rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
            transition: all 0.15s ease;
        }}
        .btn-arch-action:hover {{
            background: #30363d;
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}
        .arch-canvas {{
            background: #090d12;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 24px 16px;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow-x: auto;
            min-height: 200px;
        }}
        .arch-canvas svg {{
            max-width: 100%;
            height: auto;
        }}
        .arch-loading {{
            color: var(--accent-blue);
            font-size: 0.9rem;
            font-weight: 600;
        }}
        .arch-stages {{
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 14px 16px;
        }}
        .arch-stages-title {{
            font-size: 0.88rem;
            font-weight: 700;
            color: var(--accent-yellow);
            margin-bottom: 10px;
        }}
        .arch-stages-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        .arch-stage-card {{
            background: #0d1117;
            border: 1px solid rgba(48, 54, 61, 0.6);
            border-radius: 8px;
            padding: 10px;
        }}
        .arch-stage-header {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--accent-blue);
            margin-bottom: 4px;
        }}
        .arch-stage-desc {{
            font-size: 0.78rem;
            color: var(--text-muted);
            line-height: 1.4;
            word-break: break-word;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        if (typeof mermaid !== 'undefined') {{
            mermaid.initialize({{
                startOnLoad: false,
                theme: 'dark',
                securityLevel: 'loose',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }}
            }});
        }}
    </script>
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
                <!-- Clean Hero Search Bar -->
                <div class="search-bar-primary">
                    <div class="search-scope-wrapper" {'hidden' if not search_endpoint else ''}>
                        <select id="searchScope" class="search-scope-select" aria-label="Phạm vi tìm kiếm">
                            <option id="optScopeTopic" value="topic">🏷️ Chủ đề / Tag (GitHub Topics)</option>
                            <option id="optScopeName" value="name">📦 Tên project</option>
                            <option id="optScopeContent" value="content">📄 Từ khóa bên trong project (README)</option>
                        </select>
                    </div>
                    <div class="search-input-wrapper">
                        <span class="search-icon">🔍</span>
                        <label id="lblSearchInput" for="searchInput" style="display:none;">Từ khóa</label>
                        <input type="search" id="searchInput" placeholder="Ví dụ: agent, voice, Unity" autocomplete="off" aria-describedby="searchHelp">
                        <button type="button" id="clearSearchInputBtn" class="clear-input-btn" title="Xóa từ khóa" style="display:none;" onclick="clearSearchInput()">✕</button>
                    </div>
                    <button id="searchButton" type="submit" class="search-button">🔍 Tìm kiếm</button>
                    <button type="button" id="toggleAdvancedSearchBtn" class="btn-toggle-advanced" aria-expanded="false" onclick="toggleAdvancedSearch()">
                        <span id="lblAdvancedToggle">⚙️ Tùy chọn</span>
                        <span id="advancedOptionsBadge" class="advanced-badge" style="display:none;">0</span>
                    </button>
                </div>

                <!-- Collapsible Advanced Search Panel -->
                <div id="advancedSearchPanel" class="advanced-search-panel" style="display:none;">
                    <div class="advanced-panel-header">
                        <span class="advanced-panel-title" id="lblAdvancedTitle">⚙️ Tùy chọn tìm kiếm & nghiên cứu nâng cao</span>
                        <button type="button" class="btn-close-advanced" onclick="toggleAdvancedSearch(false)">✕</button>
                    </div>
                    <div class="advanced-grid">
                        <div class="advanced-field" {'hidden' if not search_endpoint else ''}>
                            <label id="lblDataSource" for="dataSource">Nguồn xu hướng</label>
                            <select id="dataSource" onchange="updateSearchMode(); updateAdvancedBadge();">
                                <option id="optSourceGitHub" value="github">🔥 GitHub Trending</option>
                                <option id="optSourceHN" value="hn">📰 Hacker News Trends</option>
                            </select>
                        </div>
                        <div class="advanced-field" {'hidden' if not search_endpoint else ''}>
                            <label id="lblTrendingPeriod" for="trendingPeriod">Kỳ Trending (khi từ khóa trống)</label>
                            <select id="trendingPeriod" onchange="updateAdvancedBadge();">
                                <option id="optPeriodDaily" value="daily">Hôm nay</option>
                                <option id="optPeriodWeekly" value="weekly">Tuần này</option>
                                <option id="optPeriodMonthly" value="monthly">Tháng này</option>
                            </select>
                        </div>
                        <div class="advanced-field" {'hidden' if not search_endpoint else ''}>
                            <label id="lblGithubLanguage" for="githubLanguage">Ngôn ngữ</label>
                            <input id="githubLanguage" placeholder="Python, Rust, C#..." maxlength="40" oninput="updateAdvancedBadge();">
                        </div>
                        <div class="advanced-field" {'hidden' if not search_endpoint else ''}>
                            <label id="lblGithubSort" for="githubSort">Sắp xếp khi có từ khóa</label>
                            <select id="githubSort" onchange="updateAdvancedBadge();">
                                <option id="optSortMatch" value="best-match">Phù hợp nhất</option>
                                <option id="optSortStars" value="stars">Nhiều stars nhất</option>
                                <option id="optSortUpdated" value="updated">Cập nhật gần nhất</option>
                            </select>
                        </div>
                        <div class="advanced-field">
                            <label id="lblKeywordMode" for="keywordMode">Cách khớp từ khóa</label>
                            <select id="keywordMode" onchange="updateAdvancedBadge();">
                                <option id="optModeAll" value="all">Khớp tất cả từ khóa</option>
                                <option id="optModeAny" value="any">Khớp ít nhất một từ khóa</option>
                            </select>
                        </div>
                        <div class="advanced-field limit-field">
                            <label id="lblResultLimit" for="resultLimit">Số lượng project</label>
                            <input type="number" id="resultLimit" min="1" max="30" step="1" value="10" required onchange="updateAdvancedBadge();">
                        </div>
                        <div class="advanced-field" style="justify-content: flex-end; padding-bottom: 4px;" {'hidden' if not search_endpoint else ''}>
                            <label id="lblDeepContainer" class="checkbox-filter" style="margin: 0;">
                                <input id="deepResearch" type="checkbox" {'checked' if default_deep else ''} onchange="updateAdvancedBadge();">
                                <span id="lblDeepText">Phân tích sâu (chậm hơn)</span>
                            </label>
                        </div>
                    </div>
                    <div class="advanced-panel-footer">
                        <button type="button" id="resetSearch" class="btn-reset-options">↺ Đặt lại mặc định</button>
                        <button type="button" class="btn-collapse-panel" onclick="toggleAdvancedSearch(false)">Thu gọn ▲</button>
                    </div>
                </div>
            </form>

            <!-- Sleek Status & Summary Meta Bar -->
            <div class="search-meta-bar">
                <div class="meta-left">
                    <span id="resultsSummary" class="meta-pill meta-summary" role="status" aria-live="polite"></span>
                    <span id="searchStatus" class="meta-pill meta-status" role="status" aria-live="polite" style="display:none;"></span>
                    <span id="searchError" class="meta-pill meta-error" role="alert" style="display:none;"></span>
                </div>
                <div class="meta-right">
                    <button type="button" id="btnToggleHelp" class="btn-help-hint" onclick="toggleSearchHelp()" title="Mẹo tìm kiếm">
                        <span>💡</span> <span id="lblHelpHint">Mẹo tìm kiếm</span>
                    </button>
                </div>
            </div>
            <div id="searchHelpContainer" class="search-help-box" style="display:none;">
                <p id="searchHelp" class="search-help" style="margin:0;">{search_help}</p>
            </div>

            <!-- Refined Quick Filter Toolbar -->
            <div class="controls">
                <span class="filter-toolbar-label" id="lblFilterToolbar">🎯 Lọc kết quả:</span>
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
                    <option value="bookmarked">⭐ Đã lưu (Bookmark)</option>
                </select>
                <label class="checkbox-filter">
                    <input type="checkbox" id="watchlistOnly" onchange="filterCards()"> <span id="lblWatchlistText">⭐ Khớp sở thích (>0%)</span>
                </label>
                <label class="checkbox-filter" style="color: #d2a8ff;">
                    <input type="checkbox" id="altOnly" onchange="filterCards()"> <span id="lblAltText">💡 Thay thế thương mại</span>
                </label>
                <button type="button" id="syncWatchlistBtn" class="btn-copy" style="background:#238636;color:#fff;border-color:#2ea043;padding:6px 12px;font-size:0.82rem;" title="Học sở thích từ các repo bạn đánh giá cao" {'hidden' if not search_endpoint else ''}>🧠 Đồng bộ sở thích</button>
                <button type="button" id="btnToggleAllCharts" class="btn-toggle-all-sh" onclick="toggleAllStarCharts()" title="Bật/Tắt hiển thị biểu đồ Stars trên toàn bộ các thẻ">
                    <span>📈</span> <span id="lblToggleAllCharts">Thu gọn biểu đồ Stars</span>
                </button>
                <button type="button" id="clearFiltersBtn" class="btn-clear-filters" onclick="clearCardFilters()" title="Xóa các bộ lọc kết quả bên trên">↺ Bỏ lọc</button>
            </div></header>

        <!-- Domain Presets Bar -->
        <div class="preset-filters-bar">
            <div class="preset-pills-wrap">
                <span class="preset-label" id="lblDomainPresets">🎯 Chuyên môn:</span>
                <button type="button" class="preset-pill active" data-preset="all" onclick="selectDomainPreset('all')">
                    <span>🌟</span> <span id="presetAll">Tất cả</span> <span class="preset-count" id="countAll">0</span>
                </button>
                <button type="button" class="preset-pill" data-preset="ai" onclick="selectDomainPreset('ai')">
                    <span>🤖</span> <span id="presetAi">AI & Agent</span> <span class="preset-count" id="countAi">0</span>
                </button>
                <button type="button" class="preset-pill" data-preset="web" onclick="selectDomainPreset('web')">
                    <span>🌐</span> <span id="presetWeb">Web & Fullstack</span> <span class="preset-count" id="countWeb">0</span>
                </button>
                <button type="button" class="preset-pill" data-preset="security" onclick="selectDomainPreset('security')">
                    <span>🛡️</span> <span id="presetSecurity">DevSecOps & Cloud</span> <span class="preset-count" id="countSecurity">0</span>
                </button>
                <button type="button" class="preset-pill" data-preset="mobile" onclick="selectDomainPreset('mobile')">
                    <span>📱</span> <span id="presetMobile">Mobile & Game</span> <span class="preset-count" id="countMobile">0</span>
                </button>
                <button type="button" class="preset-pill" data-preset="systems" onclick="selectDomainPreset('systems')">
                    <span>⚡</span> <span id="presetSystems">Systems & Hiệu năng</span> <span class="preset-count" id="countSystems">0</span>
                </button>
                <button type="button" class="preset-pill preset-bm-pill" data-preset="bookmarks" onclick="selectDomainPreset('bookmarks')">
                    <span>🔖</span> <span id="presetBookmarks">Đã lưu</span> <span class="preset-count" id="countBookmarks">0</span>
                </button>
            </div>
            <div style="display:flex; gap:8px; align-items:center;">
                <button type="button" id="exportBookmarksBtn" class="btn-toggle-analytics" onclick="openExportModal()" style="display:none; background:rgba(210,153,34,0.15); border-color:#d29922; color:#e3b341;">
                    <span>📤</span> <span id="lblBtnExportBookmarks">Xuất Danh Sách Lưu</span>
                </button>
                <button type="button" id="toggleAnalyticsBtn" class="btn-toggle-analytics" onclick="toggleAnalyticsPanel()">
                    <span>📊</span> <span id="lblBtnAnalytics">Xem Biểu đồ Tăng trưởng</span>
                </button>
            </div>
        </div>

        <!-- Analytics & Chart Panel -->
        <div id="analyticsPanel" class="analytics-panel" style="display:none;">
            <div class="analytics-header">
                <h3 id="chartVelocityTitle">⚡ Bảng xếp hạng Tốc độ Tăng trưởng Sao</h3>
                <span class="analytics-sub" id="analyticsSubtitle">Top dự án bứt phá trong kỳ</span>
            </div>
            <div id="velocityChartBars" class="velocity-chart-bars"></div>
            
            <div class="analytics-grid-two">
                <div class="analytics-card">
                    <h4 id="chartDomainTitle">🌐 Phân bổ Lĩnh vực Công nghệ</h4>
                    <div id="domainStackedBar" class="domain-stacked-bar"></div>
                    <div id="domainLegend" class="domain-legend"></div>
                </div>
                <div class="analytics-card">
                    <h4 id="chartMaturityTitle">🟢 Tỷ lệ Độ hoàn thiện</h4>
                    <div id="maturityBars" class="maturity-bars"></div>
                </div>
            </div>
        </div>

        <!-- Trending Topics / Tags Bar -->
        <div id="topicsBar" class="topics-bar" style="display:none;">
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                <span class="preset-label" id="lblTrendingTopics">🏷️ Chủ đề nổi bật:</span>
                <div id="topicsPills" style="display:flex; gap:6px; flex-wrap:wrap; align-items:center;"></div>
            </div>
            <div id="activeTopicBadge" style="display:none; align-items:center; gap:6px; margin-left:auto;">
                <span id="activeTopicText" class="bm-tag-pill" style="cursor:pointer;" onclick="clearTopicFilter()"></span>
            </div>
        </div>

        <div id="cardsGrid" class="cards-grid"></div>
        <div id="emptyState" class="empty-state">Không tìm thấy repository nào phù hợp với bộ lọc hiện tại.</div>
    </div>
        <!-- Export Bookmarks Modal -->
        <div id="exportModal" class="modal-backdrop" style="display:none;" onclick="if(event.target===this)closeExportModal()">
            <div class="export-modal-box">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid var(--border); padding-bottom:8px;">
                    <h3 style="margin:0; font-size:1.05rem; color:#e3b341;" id="exportModalTitle">📤 Xuất Danh Sách Repo Đã Lưu</h3>
                    <button type="button" onclick="closeExportModal()" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-size:1.2rem;">✕</button>
                </div>
                <div style="margin-bottom:10px; font-size:0.82rem; color:var(--text-muted);" id="exportModalSubtitle">
                    Bản tóm tắt Markdown của các repo bạn đã lưu kèm tag và ghi chú:
                </div>
                <textarea id="exportTextarea" readonly style="width:100%; height:220px; background:#0d1117; border:1px solid var(--border); color:var(--text-main); font-family:monospace; font-size:0.8rem; padding:8px; border-radius:6px; resize:vertical; margin-bottom:12px;"></textarea>
                <div style="display:flex; justify-content:flex-end; gap:8px;">
                    <button type="button" onclick="closeExportModal()" class="btn-copy" style="background:#21262d; color:var(--text-main); border-color:var(--border);" id="exportCloseBtn">Đóng</button>
                    <button type="button" onclick="copyExportMarkdown()" class="btn-copy" style="background:#238636; color:#fff; border-color:#2ea043;" id="exportCopyBtn">📋 Sao chép Markdown</button>
                </div>
            </div>
        </div>


    <script>
        let reposData = {data_json};
        const searchEndpoint = {endpoint_json};
        let githubTotal = null;
        let resultMode = 'search';
        let searching = false;
        let activeDomainPreset = 'all';
        const compareSet = new Set();
        let isAnalyticsOpen = false;
        let activeTopicFilter = '';
        // Bookmarks & Personal Notes Management
        let bookmarksMap = {{}};
        try {{
            const cachedBm = localStorage.getItem('gh_bookmarks');
            if (cachedBm) bookmarksMap = JSON.parse(cachedBm);
        }} catch (e) {{
            console.warn('Could not read bookmarks from localStorage:', e);
        }}

        function saveBookmarkToStorage(name, repoData, tags, notes) {{
            const curr = bookmarksMap[name] || {{}};
            bookmarksMap[name] = {{
                full_name: name,
                bookmarked_at: curr.bookmarked_at || new Date().toISOString(),
                tags: tags !== undefined ? tags : (curr.tags || []),
                notes: notes !== undefined ? notes : (curr.notes || ''),
                repo_data: (repoData && repoData.name) ? repoData : (curr.repo_data || {{}})
            }};
            try {{ localStorage.setItem('gh_bookmarks', JSON.stringify(bookmarksMap)); }} catch (e) {{}}
            updateBookmarkBadge();
            if (searchEndpoint) {{
                fetch('/api/bookmarks', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        action: 'save',
                        full_name: name,
                        tags: bookmarksMap[name].tags,
                        notes: bookmarksMap[name].notes,
                        repo_data: bookmarksMap[name].repo_data
                    }})
                }}).catch(err => console.warn('Sync bookmark failed:', err));
            }}
        }}

        function removeBookmarkFromStorage(name) {{
            delete bookmarksMap[name];
            try {{ localStorage.setItem('gh_bookmarks', JSON.stringify(bookmarksMap)); }} catch (e) {{}}
            updateBookmarkBadge();
            if (searchEndpoint) {{
                fetch('/api/bookmarks', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{ action: 'delete', full_name: name }})
                }}).catch(err => console.warn('Sync delete bookmark failed:', err));
            }}
        }}

        function updateBookmarkBadge() {{
            const countEl = document.getElementById('countBookmarks');
            const bmCount = Object.keys(bookmarksMap).length;
            if (countEl) countEl.textContent = bmCount;
            const exportBtn = document.getElementById('exportBookmarksBtn');
            if (exportBtn) exportBtn.style.display = bmCount > 0 ? 'inline-flex' : 'none';
        }}

        async function loadServerBookmarks() {{
            if (!searchEndpoint) return;
            try {{
                const res = await fetch('/api/bookmarks');
                if (res.ok) {{
                    const data = await res.json();
                    if (data && typeof data === 'object') {{
                        Object.assign(bookmarksMap, data);
                        try {{ localStorage.setItem('gh_bookmarks', JSON.stringify(bookmarksMap)); }} catch (e) {{}}
                        updateBookmarkBadge();
                        filterCards();
                    }}
                }}
            }} catch (e) {{
                console.warn('Could not fetch server bookmarks:', e);
            }}
        }}

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
                lblAdvancedToggle: "⚙️ Tùy chọn",
                lblAdvancedTitle: "⚙️ Tùy chọn tìm kiếm & nghiên cứu nâng cao",
                lblHelpHint: "Mẹo tìm kiếm",
                lblFilterToolbar: "🎯 Lọc kết quả:",
                btnCompare: "So sánh",
                btnCompared: "Đã chọn",
                btnCompareTitle: "Chọn để so sánh đối chiếu với repo khác",
                compareDockTitle: "So sánh Repository:",
                btnLaunchCompare: "So sánh đối chiếu",
                compareLimitAlert: "Tối đa so sánh 4 repository cùng lúc.",
                compareModalTitle: "Bảng Ma Trận So Sánh Đối Chiếu Repository",
                compareRemoveRepo: "Bỏ repo này khỏi so sánh",
                starHistoryComparisonTitle: "Biểu đồ Đối chiếu Tăng trưởng Stars (Star History)",
                starHistoryTitle: "Biểu đồ Tăng trưởng Stars",
                openStarHistoryWeb: "Mở biểu đồ tương tác trên Star-History.com",
                starHistoryOfflineMsg: "Không thể tải trước hình ảnh từ Star History (có thể do giới hạn API hoặc offline). Bạn có thể mở trực tiếp liên kết bên dưới.",
                btnIdeTitle: "Mở và thử nghiệm trong IDE",
                btnIdeCode: "⚡ Code",
                cloneCursor: "🚀 Cursor",
                cloneVsCode: "💻 VS Code",
                openGithubDev: "🌐 GitHub.dev",
                openCodespace: "☁️ Codespace",
                btnPlayground: "⚡ Chạy thử",
                btnPlaygroundTitle: "Khởi chạy tức thì trên Cloud hoặc xem Docker Compose & Run Script",
                playgroundModalTitle: (name) => `⚡ Chạy thử & Playground: ${{name}}`,
                pgCloudTab: "☁️ Cloud 1-Click",
                pgDockerTab: "🐳 Docker Compose",
                pgScriptsTab: "💻 Local Scripts",
                pgDockerComposeTitle: "Tệp docker-compose.yml",
                pgDockerfileTitle: "Tệp Dockerfile tối ưu",
                pgRunCmdTitle: "Lệnh chạy Docker nhanh (CLI)",
                pgBashTitle: "Bash Script (Linux / macOS / WSL)",
                pgPowershellTitle: "PowerShell Script (Windows)",
                pgOneLinerTitle: "Lệnh 1 dòng (One-liner Terminal)",
                pgCopyBtn: "📋 Sao chép",
                pgDownloadBtn: "💾 Tải file",
                pgLaunchBtn: "Khởi chạy ↗",
                pgCopied: "✓ Đã sao chép vào bộ nhớ tạm!",
                pgTipDocker: "💡 Hướng dẫn Docker: Lưu file vào thư mục dự án rồi gõ 'docker compose up -d' để chạy ngầm.",
                pgTipScript: "💡 Hướng dẫn Script: Tự động clone, cài dependencies và khởi động ứng dụng chỉ với 1 click.",
                cardStarHistoryShow: "Mở rộng",
                cardStarHistoryHide: "Thu gọn",
                btnCollapseAllCharts: "Thu gọn biểu đồ Stars",
                btnExpandAllCharts: "Hiện biểu đồ Stars",
                btnSimilar: "Tìm tương tự",
                btnSimilarTitle: "Tìm các repository tương đương giải quyết bài toán tương tự trên GitHub",
                similarModalTitle: (name) => `Dự án tương tự với ${{name}}`,
                similarModalSubtitle: "Gợi ý các repository mã nguồn mở tương đương dựa trên chủ đề, tech stack và mục đích sử dụng:",
                similarLoading: "Đang tìm kiếm và phân tích các repository tương đương trên GitHub...",
                similarEmpty: "Không tìm thấy repository tương tự nào trên GitHub phù hợp với tiêu chí.",
                similarCompareBtn: "⚖️ So sánh với repo này",
                archTitle: "Sơ đồ Kiến trúc & Luồng Dữ liệu (Pipeline)",
                archSubtitle: "Mô hình hóa tương tác giữa người dùng, module xử lý, storage và luồng dữ liệu:",
                archCopyBtn: "Sao chép Mermaid",
                archCopied: "Đã sao chép!",
                archLiveEditor: "Mermaid Live Editor",
                archOfflineFallback: "Mermaid.js chưa tải (đang offline). Bạn có thể xem hoặc sao chép mã Mermaid bên dưới:",
                archPipelineStages: "Các giai đoạn xử lý cốt lõi:",
                archStageInput: "1. Tầng Đầu vào (Input / Ingestion)",
                archStageProcess: "2. Tầng Xử lý & Engine (Core Processing)",
                archStageStorage: "3. Tầng Lưu trữ & Tích hợp (Storage & Services)",
                archStageOutput: "4. Tầng Đầu ra & Phản hồi (Output & Delivery)",
                latestReleaseTitle: "Bản phát hành mới nhất",
                releaseRadarTitle: "Radar Bản phát hành & Nhật ký Thay đổi (Changelog)",
                releaseTag: "Phiên bản:",
                releasePublished: "Ngày phát hành:",
                releasePrereleaseBadge: "Bản thử nghiệm (Pre-release)",
                releaseHighlightsTitle: "Điểm mới & Tính năng cập nhật nổi bật:",
                releaseFullNotesTitle: "Trích đoạn Ghi chú Phát hành (Release Notes):",
                releaseViewOnGitHub: "Xem trên GitHub Releases",
                releaseNoRelease: "Dự án này chưa phát hành bản Release chính thức trên GitHub (thường cập nhật trực tiếp qua commit trên nhánh chính).",
                noReleaseText: "Chưa có bản release chính thức",
                latestPulseTitle: "Trạng thái bảo trì",
                pulseTitle: "Sức khỏe Bảo trì & Hoạt động Cộng đồng (Pulse)",
                pulseSubtitle: "Chỉ số cam kết bảo trì từ maintainers, tần suất cập nhật code và mạng lưới đóng góp:",
                pulseLatestPush: "Hoạt động Commit",
                pulseOpenIssues: "Issues đang mở",
                pulseLicense: "Giấy phép (License)",
                pulseWatchersForks: "Cộng đồng & Forks",
                pulseTopContribTitle: "Top Contributors (Đóng góp hàng đầu):",
                pulseHealthVerdictTitle: "Đánh giá mức độ duy trì & Cam kết bảo trì:",
                pulseVerdictActive: "Dự án đang được cập nhật liên tục và bảo trì rất tích cực bởi cộng đồng. Rất an toàn để tích hợp.",
                pulseVerdictSteady: "Dự án duy trì nhịp độ cập nhật ổn định trong tháng qua. Có tính khả dụng tốt.",
                pulseVerdictSlow: "Dự án cập nhật chậm (hơn 1 tháng không có commit mới). Cần kiểm tra kỹ các issue mở trước khi đưa vào sản xuất.",
                pulseVerdictDormant: "Dự án có dấu hiệu ngủ đông (>3 tháng chưa commit). Hãy cân nhắc kỹ hoặc chuẩn bị phương án tự fork & duy trì.",
                pulseNoData: "Chưa có dữ liệu sức khỏe cộng đồng từ GitHub API (có thể do offline hoặc rate limit).",
                pulseCommitsCount: (n) => `${{n}} đóng góp`,
                similarComparedBtn: "✅ Đã chọn so sánh",
                similarOpenCompare: (n) => `So sánh đối chiếu (${{n}})`,
                similarCloseBtn: "Đóng",
                clearFiltersBtn: "↺ Bỏ lọc",
                clearInputTitle: "Xóa từ khóa",
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
                btnDeepDive: "🔬 Chi tiết kiến trúc & Deep Dive",
                lblDomainPresets: "🎯 Chuyên môn:",
                presetAll: "Tất cả",
                presetAi: "AI & Agent",
                presetWeb: "Web & Fullstack",
                presetSecurity: "DevSecOps & Cloud",
                presetMobile: "Mobile & Game",
                presetSystems: "Systems & Hiệu năng",
                presetBookmarks: "Đã lưu",
                btnBookmark: "Lưu",
                btnBookmarked: "Đã lưu",
                bookmarkEditTitle: "📝 Ghi chú & Tag Cá Nhân",
                bookmarkTagsPlaceholder: "Thêm tag (cách nhau bởi dấu phẩy, vd: ai-agent, production, cần-thử)...",
                bookmarkNotesPlaceholder: "Ghi chú cá nhân (vd: Kiến trúc Orca rất hay, nghiên cứu cho sprint tới)...",
                bookmarkSaveBtn: "💾 Lưu ghi chú",
                bookmarkRemoveBtn: "🗑️ Bỏ lưu repo",
                emptyBookmarks: "Bạn chưa lưu repo nào. Hãy nhấp nút 🔖 Lưu ở bất kỳ repo nào để tạo bộ sưu tập riêng!",
                btnExportBookmarks: "Xuất Danh Sách Lưu",
                exportModalTitle: "📤 Xuất Danh Sách Repo Đã Lưu",
                exportModalSubtitle: "Bản tóm tắt Markdown của các repo bạn đã lưu kèm tag và ghi chú:",
                exportCopyBtn: "📋 Sao chép Markdown",
                exportCopied: "✓ Đã sao chép Markdown vào clipboard!",
                exportCloseBtn: "Đóng",
                statusBookmarked: "⭐ Đã lưu (Bookmark)",
                bmPersonalNotes: "⭐ Ghi chú cá nhân",

                bmEditBtn: "✏️ Sửa",
                optScopeTopic: "🏷️ Chủ đề / Tag (GitHub Topics)",
                searchPlaceholderTopic: "Nhập topic/tag (vd: agent, rag, mcp, llm, terminal, rust)...",
                searchHelpTopic: "Tìm kiếm repo có gắn topic/tag tương ứng trên GitHub. Có thể nhập nhiều tag cách nhau bằng dấu phẩy.",
                lblTrendingTopics: "🏷️ Chủ đề nổi bật:",
                tagFilterActive: (t) => `Đang lọc tag: #${{t}} ✕`,
                lblBtnAnalytics: "Xem Biểu đồ Tăng trưởng",
                lblBtnAnalyticsHide: "Ẩn Biểu đồ Tăng trưởng",
                chartVelocityTitle: "⚡ Bảng xếp hạng Tốc độ Tăng trưởng Sao",
                analyticsSubtitle: "Top dự án bứt phá trong kỳ",
                chartDomainTitle: "🌐 Phân bổ Lĩnh vực Công nghệ",
                chartMaturityTitle: "🟢 Tỷ lệ Độ hoàn thiện",
                chartStarsUnit: "sao mới",
                lblDataSource: "Nguồn xu hướng",
                optSourceGitHub: "🔥 GitHub Trending",
                optSourceHN: "📰 Hacker News Trends",
                modalTabs: {{
                    playground: "⚡ Chạy thử (Playground)",
                    architecture: "🏗️ Sơ đồ Kiến trúc & Luồng",
                    release_radar: "📦 Bản phát hành (Changelog)",
                    community_pulse: "👥 Sức khỏe & Cộng đồng (Pulse)",
                    how_it_works: "🏛️ Cơ chế & Chi tiết",
                    comparisons: "📊 Benchmarks & So sánh",
                    practical_examples: "💻 Code & Lệnh chạy",
                    limitations: "⚠️ Giới hạn & Cảnh báo",
                    adoption_notes: "🚀 Triển khai & Cài đặt",
                    sources: "📚 Nguồn tài liệu",
                    star_history: "📈 Star History"
                }},
                modalNoEvidence: "Chưa có trích dẫn tài liệu cho phần này. Bạn có thể bật tùy chọn 'Phân tích sâu' khi tìm kiếm để tải thêm tài liệu liên kết.",
                modalSourcesTitle: "Nguồn tài liệu đã xác minh:",
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
                lblAdvancedToggle: "⚙️ Options",
                lblAdvancedTitle: "⚙️ Advanced Search & Research Options",
                lblHelpHint: "Search Tips",
                lblFilterToolbar: "🎯 Filter Results:",
                btnCompare: "Compare",
                btnCompared: "Selected",
                btnCompareTitle: "Select to compare side-by-side with other repos",
                compareDockTitle: "Compare Repositories:",
                btnLaunchCompare: "Compare Side-by-Side",
                compareLimitAlert: "You can compare up to 4 repositories at once.",
                compareModalTitle: "Side-by-Side Repository Comparison Matrix",
                compareRemoveRepo: "Remove this repo from comparison",
                starHistoryComparisonTitle: "Star Growth Comparison Chart (Star History)",
                starHistoryTitle: "Star Growth Curve",
                openStarHistoryWeb: "Open interactive chart on Star-History.com",
                starHistoryOfflineMsg: "Unable to load preview image from Star History (API rate limit or offline). You can view directly via the link below.",
                btnIdeTitle: "Open and test in IDE",
                btnIdeCode: "⚡ Code",
                cloneCursor: "🚀 Cursor",
                cloneVsCode: "💻 VS Code",
                openGithubDev: "🌐 GitHub.dev",
                openCodespace: "☁️ Codespace",
                btnPlayground: "⚡ Run / Playground",
                btnPlaygroundTitle: "Instant 1-Click Cloud Launch & Docker Playground",
                playgroundModalTitle: (name) => `⚡ Run & Playground: ${{name}}`,
                pgCloudTab: "☁️ Cloud 1-Click",
                pgDockerTab: "🐳 Docker Compose",
                pgScriptsTab: "💻 Local Scripts",
                pgDockerComposeTitle: "docker-compose.yml Manifest",
                pgDockerfileTitle: "Optimized Dockerfile",
                pgRunCmdTitle: "Quick Docker Run Command (CLI)",
                pgBashTitle: "Bash Script (Linux / macOS / WSL)",
                pgPowershellTitle: "PowerShell Script (Windows)",
                pgOneLinerTitle: "One-liner Terminal Command",
                pgCopyBtn: "📋 Copy",
                pgDownloadBtn: "💾 Download File",
                pgLaunchBtn: "Launch ↗",
                pgCopied: "✓ Copied to clipboard!",
                pgTipDocker: "💡 Docker Tip: Save file into repo directory and run 'docker compose up -d' to start in background.",
                pgTipScript: "💡 Script Tip: Automatically clones repo, installs dependencies and launches the application.",
                cardStarHistoryShow: "Expand",
                cardStarHistoryHide: "Collapse",
                btnCollapseAllCharts: "Collapse Star Charts",
                btnExpandAllCharts: "Show Star Charts",
                btnSimilar: "Find Similar",
                btnSimilarTitle: "Find equivalent open-source projects solving similar problems on GitHub",
                similarModalTitle: (name) => `Similar Projects to ${{name}}`,
                similarModalSubtitle: "Open-source alternatives and equivalent tools based on topics, tech stack, and purpose:",
                similarLoading: "Searching and analyzing similar repositories on GitHub...",
                similarEmpty: "No similar repositories found matching the criteria on GitHub.",
                similarCompareBtn: "⚖️ Compare with this",
                archTitle: "Architecture & Data Flow Pipeline",
                archSubtitle: "Visualizing user interactions, internal processing engine, storage, and data pipeline:",
                archCopyBtn: "Copy Mermaid",
                archCopied: "Copied!",
                archLiveEditor: "Mermaid Live Editor",
                archOfflineFallback: "Mermaid.js not loaded (offline mode). You can view or copy the Mermaid code below:",
                archPipelineStages: "Core Pipeline Stages:",
                archStageInput: "1. Ingestion / Input Layer",
                archStageProcess: "2. Core Processing Engine",
                archStageStorage: "3. Storage & Integrations",
                archStageOutput: "4. Output & Delivery Layer",
                latestReleaseTitle: "Latest Release",
                releaseRadarTitle: "Release Radar & Changelog",
                releaseTag: "Version:",
                releasePublished: "Published:",
                releasePrereleaseBadge: "Pre-release",
                releaseHighlightsTitle: "Highlights & Key Updates in this Release:",
                releaseFullNotesTitle: "Release Notes Excerpt:",
                releaseViewOnGitHub: "View on GitHub Releases",
                releaseNoRelease: "No official GitHub release found for this repository (updates may be pushed directly to the main branch).",
                noReleaseText: "No official release yet",
                latestPulseTitle: "Maintenance Status",
                pulseTitle: "Community Pulse & Maintenance Health",
                pulseSubtitle: "Tracking maintainer commitment, code freshness, open issues, and top contributors:",
                pulseLatestPush: "Latest Commit Activity",
                pulseOpenIssues: "Open Issues",
                pulseLicense: "License",
                pulseWatchersForks: "Watchers & Network",
                pulseTopContribTitle: "Top Active Contributors:",
                pulseHealthVerdictTitle: "Maintenance Health Assessment:",
                pulseVerdictActive: "Project is under highly active maintenance with recent commits. Very safe for adoption.",
                pulseVerdictSteady: "Project maintains a steady cadence of updates within the past month. Good reliability.",
                pulseVerdictSlow: "Activity has slowed down (>1 month without commits). Review open issues before production usage.",
                pulseVerdictDormant: "Project shows signs of hibernation (>3 months without commits). Consider self-forking if needed.",
                pulseNoData: "No community pulse data available from GitHub API (offline or rate-limited).",
                pulseCommitsCount: (n) => `${{n}} contributions`,
                similarComparedBtn: "✅ Selected for comparison",
                similarOpenCompare: (n) => `Compare Side-by-Side (${{n}})`,
                similarCloseBtn: "Close",
                clearFiltersBtn: "↺ Clear Filters",
                clearInputTitle: "Clear keyword",
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
                btnDeepDive: "🔬 Architecture & Deep Dive",
                lblDomainPresets: "🎯 Domain:",
                presetAll: "All",
                presetAi: "AI & Agents",
                presetWeb: "Web & Fullstack",
                presetSecurity: "DevSecOps & Cloud",
                presetMobile: "Mobile & Game",
                presetSystems: "Systems & Perf",
                presetBookmarks: "Saved",
                btnBookmark: "Bookmark",
                btnBookmarked: "Bookmarked",
                bookmarkEditTitle: "📝 Personal Notes & Tags",
                bookmarkTagsPlaceholder: "Add tags (comma separated, e.g. ai-agent, production, to-try)...",
                bookmarkNotesPlaceholder: "Personal notes (e.g. Great architecture, research in next sprint)...",
                bookmarkSaveBtn: "💾 Save Note",
                bookmarkRemoveBtn: "🗑️ Remove Bookmark",
                emptyBookmarks: "No bookmarked repositories yet. Click 🔖 Bookmark on any repo to build your personal collection!",
                btnExportBookmarks: "Export Bookmarks",
                exportModalTitle: "📤 Export Bookmarked Repositories",
                exportModalSubtitle: "Markdown summary of your bookmarked repositories with custom tags and notes:",
                exportCopyBtn: "📋 Copy Markdown",
                exportCopied: "✓ Copied Markdown to clipboard!",
                exportCloseBtn: "Close",
                statusBookmarked: "⭐ Bookmarked",
                bmPersonalNotes: "⭐ Personal Notes",

                bmEditBtn: "✏️ Edit",
                optScopeTopic: "🏷️ Topics / Tags (GitHub Topics)",
                searchPlaceholderTopic: "Enter topic/tag (e.g. agent, rag, mcp, llm, terminal, rust)...",
                searchHelpTopic: "Search repos tagged with specific GitHub topics. Separate multiple tags with commas.",
                lblTrendingTopics: "🏷️ Trending Topics:",
                tagFilterActive: (t) => `Filtered by tag: #${{t}} ✕`,
                lblBtnAnalytics: "View Growth Chart",
                lblBtnAnalyticsHide: "Hide Growth Chart",
                chartVelocityTitle: "⚡ Star Growth & Velocity Leaderboard",
                analyticsSubtitle: "Top momentum projects in period",
                chartDomainTitle: "🌐 Technology Domain Breakdown",
                chartMaturityTitle: "🟢 Project Maturity Distribution",
                chartStarsUnit: "new stars",
                lblDataSource: "Trending Source",
                optSourceGitHub: "🔥 GitHub Trending",
                optSourceHN: "📰 Hacker News Trends",
                modalTabs: {{
                    playground: "⚡ 1-Click Run & Playground",
                    architecture: "🏗️ Architecture & Pipeline",
                    release_radar: "📦 Releases & Changelog",
                    community_pulse: "👥 Community & Pulse",
                    how_it_works: "🏛️ Internals & Mechanics",
                    comparisons: "📊 Benchmarks & Comparisons",
                    practical_examples: "💻 Code & Examples",
                    limitations: "⚠️ Limitations & Warnings",
                    adoption_notes: "🚀 Adoption & Setup",
                    sources: "📚 Document Sources",
                    star_history: "📈 Star History"
                }},
                modalNoEvidence: "No direct documentation excerpt found for this section yet. Enable 'Deep Research' in search to fetch linked documents.",
                modalSourcesTitle: "Verified Document Sources:",
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
            setText('optScopeTopic', t.optScopeTopic);
            setText('optScopeContent', t.optScopeContent);
            setText('lblTrendingTopics', t.lblTrendingTopics);
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
            setText('lblAdvancedToggle', t.lblAdvancedToggle);
            setText('lblAdvancedTitle', t.lblAdvancedTitle);
            setText('lblHelpHint', t.lblHelpHint);
            setText('lblFilterToolbar', t.lblFilterToolbar);
            setText('clearFiltersBtn', t.clearFiltersBtn);
            setText('lblCompareDockTitle', `⚖️ ${{t.compareDockTitle}}`);
            setText('cmpModalTitle', t.compareModalTitle);
            const globalShBtn = document.getElementById('lblToggleAllCharts');
            if (globalShBtn) globalShBtn.textContent = allStarChartsVisible ? t.btnCollapseAllCharts : t.btnExpandAllCharts;
            updateCompareDockUI();
            const clrInp = document.getElementById('clearSearchInputBtn');
            if (clrInp) clrInp.title = t.clearInputTitle;
            setText('loadedCount', t.countBadge(reposData.length));
            setText('emptyState', t.emptyState);
            setText('lblDomainPresets', t.lblDomainPresets);
            setText('presetAll', t.presetAll);
            setText('presetAi', t.presetAi);
            setText('presetWeb', t.presetWeb);
            setText('presetSecurity', t.presetSecurity);
            setText('presetMobile', t.presetMobile);
            setText('presetSystems', t.presetSystems);
            setText('presetBookmarks', t.presetBookmarks);
            setText('lblBtnExportBookmarks', t.btnExportBookmarks);
            setText('exportModalTitle', t.exportModalTitle);
            setText('exportModalSubtitle', t.exportModalSubtitle);
            setText('exportCopyBtn', t.exportCopyBtn);
            setText('exportCloseBtn', t.exportCloseBtn);
            setText('lblBtnAnalytics', isAnalyticsOpen ? t.lblBtnAnalyticsHide : t.lblBtnAnalytics);
            setText('chartVelocityTitle', t.chartVelocityTitle);
            setText('analyticsSubtitle', t.analyticsSubtitle);
            setText('chartDomainTitle', t.chartDomainTitle);
            setText('chartMaturityTitle', t.chartMaturityTitle);

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
            if (statType && statType.options && statType.options.length >= 6) {{
                const val = statType.value;
                statType.options[0].textContent = t.filterStatusAll;
                statType.options[1].textContent = t.statusLabels.want_to_try;
                statType.options[2].textContent = t.statusLabels.tried;
                statType.options[3].textContent = t.statusLabels.skipped;
                statType.options[4].textContent = t.statusLabels.liked;
                statType.options[5].textContent = t.statusBookmarked;
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
                const bmData = bookmarksMap[raw.name] || null;
                const isBookmarked = Boolean(bmData);
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
                            ${{r.latest_release && r.latest_release.tag_name ? `<span class="pill-tag tag-release" title="${{t.latestReleaseTitle}}">🏷️ ${{escapeText(r.latest_release.tag_name)}}</span>` : ''}}
                            ${{r.community_pulse && r.community_pulse.pulse_status ? `
                                <span class="pill-tag tag-pulse ${{r.community_pulse.pulse_status}}" title="${{t.latestPulseTitle}}">
                                    ${{currentLang === 'vi' ? (r.community_pulse.pulse_badge_vi || '') : (r.community_pulse.pulse_badge_en || '')}}
                                </span>
                            ` : ''}}
                            ${{r.community_pulse && r.community_pulse.license_spdx ? `
                                <span class="pill-tag tag-license" title="${{t.pulseLicense}}">
                                    📜 ${{escapeText(r.community_pulse.license_spdx)}}
                                </span>
                            ` : ''}}
                        </div>

                        <!-- Repository Topics / Tags -->
                        ${{(raw.topics && raw.topics.length) ? `
                            <div style="display:flex; gap:5px; flex-wrap:wrap; margin-bottom:10px;">
                                ${{(raw.topics.slice(0, 8)).map(tag => `<span class="card-topic-tag" title="Lọc theo tag #${{escapeText(tag)}}" onclick="filterByTopic('${{escapeText(tag)}}')">#${{escapeText(tag)}}</span>`).join('')}}
                            </div>
                        ` : ''}}

                        <!-- Feedback Toolbar -->
                        <div class="feedback-bar">
                            <div class="rating-buttons">
                                <button type="button" class="btn-rate btn-like ${{raw.user_rating === 1 ? 'active' : ''}}" title="Useful" data-action="like">👍</button>
                                <button type="button" class="btn-rate btn-dislike ${{raw.user_rating === -1 ? 'active' : ''}}" title="Not useful" data-action="dislike">👎</button>
                                <button type="button" class="btn-rate btn-bookmark ${{isBookmarked ? 'active' : ''}}" title="${{isBookmarked ? t.btnBookmarked : t.btnBookmark}}" data-repo="${{r.name}}">🔖 <span class="bm-label">${{isBookmarked ? t.btnBookmarked : t.btnBookmark}}</span></button>
                                <button type="button" class="btn-chat" title="${{t.chatBtnText}}">${{t.chatBtnText}}</button>
                                <button type="button" class="btn-similar" onclick="openSimilarModal('${{escapeText(raw.name)}}', ${{idx}})" title="${{t.btnSimilarTitle}}">
                                    <span>🔎</span> <span class="similar-label">${{t.btnSimilar}}</span>
                                </button>
                                <button type="button" class="btn-compare ${{compareSet.has(raw.name) ? 'active' : ''}}" data-name="${{escapeText(raw.name)}}" title="${{t.btnCompareTitle}}">⚖️ <span class="compare-label">${{compareSet.has(raw.name) ? t.btnCompared : t.btnCompare}}</span></button>
                            </div>
                            <select class="status-select" title="Status">
                                <option value="unread" ${{raw.user_status === 'unread' ? 'selected' : ''}}>${{t.statusLabels.unread}}</option>
                                <option value="want_to_try" ${{raw.user_status === 'want_to_try' ? 'selected' : ''}}>${{t.statusLabels.want_to_try}}</option>
                                <option value="tried" ${{raw.user_status === 'tried' ? 'selected' : ''}}>${{t.statusLabels.tried}}</option>
                                <option value="skipped" ${{raw.user_status === 'skipped' ? 'selected' : ''}}>${{t.statusLabels.skipped}}</option>
                            </select>
                        </div>

                        <!-- Bookmark Summary & Notes Highlight -->
                        <div class="bookmark-summary" id="bmSummary_${{idx}}" style="${{isBookmarked && ((bmData?.tags && bmData.tags.length) || bmData?.notes) ? '' : 'display:none;'}}">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                <span style="font-weight:600; color:#e3b341; font-size:0.75rem;">${{t.bmPersonalNotes}}</span>
                                <button type="button" class="btn-edit-bm" data-idx="${{idx}}">${{t.bmEditBtn}}</button>
                            </div>
                            <div class="bm-tags-list" style="display:flex; gap:4px; flex-wrap:wrap; margin-bottom:4px;">
                                ${{(bmData?.tags || []).map(tag => `<span class="bm-tag-pill">🏷️ ${{escapeText(tag)}}</span>`).join('')}}
                            </div>
                            <div class="bm-notes-text" style="color:var(--text-main); font-style:italic; font-size:0.8rem;">
                                ${{escapeText(bmData?.notes || '')}}
                            </div>
                        </div>

                        <!-- Bookmark Editor (expandable) -->
                        <div class="bookmark-editor" id="bmEditor_${{idx}}" style="display:none;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                <span style="font-size:0.8rem; font-weight:bold; color:#e3b341;">${{t.bookmarkEditTitle}}</span>
                                <button type="button" class="btn-close-bm-editor" data-idx="${{idx}}" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-size:0.9rem;">✕</button>
                            </div>
                            <div style="display:flex; flex-direction:column; gap:6px;">
                                <input type="text" class="bm-tags-input" placeholder="${{t.bookmarkTagsPlaceholder}}" value="${{escapeText((bmData?.tags || []).join(', '))}}" style="background:#0d1117; border:1px solid var(--border); color:var(--text-main); padding:4px 8px; border-radius:4px; font-size:0.82rem;">
                                <textarea class="bm-notes-input" placeholder="${{t.bookmarkNotesPlaceholder}}" rows="2" style="background:#0d1117; border:1px solid var(--border); color:var(--text-main); padding:4px 8px; border-radius:4px; font-size:0.82rem; resize:vertical;">${{escapeText(bmData?.notes || '')}}</textarea>
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <button type="button" class="btn-remove-bm" data-idx="${{idx}}" style="background:transparent; border:1px solid #da3633; color:#f85149; padding:3px 8px; border-radius:4px; font-size:0.75rem; cursor:pointer;">${{t.bookmarkRemoveBtn}}</button>
                                    <button type="button" class="btn-save-bm" data-idx="${{idx}}" style="background:#d29922; color:#0d1117; border:none; padding:4px 12px; border-radius:4px; font-weight:bold; font-size:0.82rem; cursor:pointer;">${{t.bookmarkSaveBtn}}</button>
                                </div>
                            </div>
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
                        <!-- Inline Star History on Card -->
                        <div class="card-sh-section">
                            <div class="card-sh-header">
                                <span class="card-sh-title">📈 ${{t.starHistoryTitle}}</span>
                                <button type="button" class="btn-toggle-card-sh" onclick="toggleCardStarHistory(this, '${{idx}}')">
                                    <span class="sh-arrow">▴</span> <span class="sh-text">${{t.cardStarHistoryHide}}</span>
                                </button>
                            </div>
                            <div class="card-sh-body" id="cardSh_${{idx}}">
                                <div class="sh-chart-wrapper">
                                    <div class="sh-loading" style="font-size:0.78rem; color:var(--text-muted); padding:8px 0;">⏳ Đang tải biểu đồ...</div>
                                    <img src="https://api.star-history.com/svg?repos=${{escapeText(r.name)}}&type=Date" 
                                         alt="${{escapeText(r.name)}} Star History" 
                                         class="card-star-history-img" 
                                         loading="lazy" 
                                         onload="this.previousElementSibling.style.display='none';" 
                                         onerror="this.previousElementSibling.textContent='${{t.starHistoryOfflineMsg}}';">
                                </div>
                                <div class="card-sh-actions">
                                    <a href="https://star-history.com/#${{escapeText(r.name)}}&Date" target="_blank" rel="noopener noreferrer" class="btn-sh-link">
                                        <span>🌐</span> <span>Star-History.com</span>
                                    </a>
                                    <a href="https://github.com/${{escapeText(r.name)}}/pulse" target="_blank" rel="noopener noreferrer" class="btn-sh-link">
                                        <span>📊</span> <span>GitHub Pulse</span>
                                    </a>
                                </div>
                            </div>
                        </div>
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
                        <div class="footer-actions">
                            <button type="button" class="btn-playground" title="${{t.btnPlaygroundTitle}}">
                                <span>⚡</span> <span>${{t.btnPlayground}}</span>
                            </button>
                            <div class="ide-dropdown-wrapper">
                                <button type="button" class="btn-ide" title="${{t.btnIdeTitle}}">
                                    <span>${{t.btnIdeCode}}</span> <span style="font-size:0.7rem;">▾</span>
                                </button>
                                <div class="ide-menu">
                                    <a href="cursor://vscode.git/clone?url=${{escapeText(r.url)}}.git" class="ide-menu-item" title="Clone và mở trong Cursor">
                                        <span>${{t.cloneCursor}}</span>
                                    </a>
                                    <a href="vscode://vscode.git/clone?url=${{escapeText(r.url)}}.git" class="ide-menu-item" title="Clone và mở trong VS Code">
                                        <span>${{t.cloneVsCode}}</span>
                                    </a>
                                    <a href="https://github.dev/${{escapeText(r.name)}}" target="_blank" rel="noopener noreferrer" class="ide-menu-item" title="Mở trong trình soạn thảo web GitHub.dev">
                                        <span>${{t.openGithubDev}}</span>
                                    </a>
                                    <a href="https://codespaces.new/${{escapeText(r.name)}}" target="_blank" rel="noopener noreferrer" class="ide-menu-item" title="Khởi chạy GitHub Codespaces">
                                        <span>${{t.openCodespace}}</span>
                                    </a>
                                </div>
                            </div>
                            <a href="${{r.url}}" target="_blank" class="btn-view">${{t.viewOnGithub}}</a>
                        </div>
                    </div>
                `;
                const copy = card.querySelector('.btn-copy');
                if (copy) copy.addEventListener('click', () => copyCmd(copy, raw.quick_run));

                const pgBtn = card.querySelector('.btn-playground');
                if (pgBtn) pgBtn.addEventListener('click', () => openPlaygroundModal(raw));

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

                // Bookmark Event Listeners
                const bmBtn = card.querySelector('.btn-bookmark');
                const bmSummary = card.querySelector(`#bmSummary_${{idx}}`);
                const bmEditor = card.querySelector(`#bmEditor_${{idx}}`);
                const editBmBtn = card.querySelector('.btn-edit-bm');
                const closeBmEditorBtn = card.querySelector('.btn-close-bm-editor');
                const saveBmBtn = card.querySelector('.btn-save-bm');
                const removeBmBtn = card.querySelector('.btn-remove-bm');
                const tagsInput = card.querySelector('.bm-tags-input');
                const notesInput = card.querySelector('.bm-notes-input');

                if (bmBtn && bmEditor) {{
                    bmBtn.addEventListener('click', () => {{
                        const currentlyBookmarked = Boolean(bookmarksMap[raw.name]);
                        if (!currentlyBookmarked) {{
                            saveBookmarkToStorage(raw.name, raw, [], '');
                            bmBtn.classList.add('active');
                            const label = bmBtn.querySelector('.bm-label');
                            if (label) label.textContent = t.btnBookmarked;
                            bmEditor.style.display = 'block';
                            if (tagsInput) tagsInput.focus();
                        }} else {{
                            const isHidden = bmEditor.style.display === 'none';
                            bmEditor.style.display = isHidden ? 'block' : 'none';
                            if (isHidden && tagsInput) tagsInput.focus();
                        }}
                    }});
                }}
                if (editBmBtn && bmEditor) {{
                    editBmBtn.addEventListener('click', () => {{
                        bmEditor.style.display = 'block';
                        if (tagsInput) tagsInput.focus();
                    }});
                }}
                if (closeBmEditorBtn && bmEditor) {{
                    closeBmEditorBtn.addEventListener('click', () => {{
                        bmEditor.style.display = 'none';
                    }});
                }}
                if (saveBmBtn) {{
                    saveBmBtn.addEventListener('click', () => {{
                        const rawTags = (tagsInput ? tagsInput.value : '').split(',').map(s => s.trim()).filter(Boolean);
                        const tags = [...new Set(rawTags)];
                        const notes = notesInput ? notesInput.value.trim() : '';
                        saveBookmarkToStorage(raw.name, raw, tags, notes);
                        bmBtn.classList.add('active');
                        const label = bmBtn.querySelector('.bm-label');
                        if (label) label.textContent = t.btnBookmarked;
                        if (bmSummary) {{
                            const tagsList = bmSummary.querySelector('.bm-tags-list');
                            if (tagsList) tagsList.innerHTML = tags.map(tag => `<span class="bm-tag-pill">🏷️ ${{escapeText(tag)}}</span>`).join('');
                            const notesText = bmSummary.querySelector('.bm-notes-text');
                            if (notesText) notesText.textContent = notes;
                            bmSummary.style.display = (tags.length || notes) ? 'block' : 'none';
                        }}
                        bmEditor.style.display = 'none';
                    }});
                }}
                if (removeBmBtn) {{
                    removeBmBtn.addEventListener('click', () => {{
                        removeBookmarkFromStorage(raw.name);
                        bmBtn.classList.remove('active');
                        const label = bmBtn.querySelector('.bm-label');
                        if (label) label.textContent = t.btnBookmark;
                        if (bmSummary) bmSummary.style.display = 'none';
                        bmEditor.style.display = 'none';
                        if (activeDomainPreset === 'bookmarks') {{
                            filterCards();
                        }}
                    }});
                }}

                const compareBtn = card.querySelector('.btn-compare');
                if (compareBtn) {{
                    compareBtn.addEventListener('click', () => toggleCompareRepo(raw.name));
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
                const deepBtn = document.createElement('button');
                deepBtn.type = 'button';
                deepBtn.className = 'btn-deep-dive';
                deepBtn.innerHTML = `<span>🔬</span> <span>${{t.btnDeepDive}}</span>`;
                deepBtn.addEventListener('click', () => openDeepDiveModal(raw, idx));
                card.insertBefore(deepBtn, card.querySelector('.card-footer'));
                card.insertBefore(details, card.querySelector('.card-footer'));
                grid.appendChild(card);
            }});
        }}


        // Topic / Tag Filtering Logic
        function filterByTopic(tag) {{
            if (activeTopicFilter === tag) {{
                activeTopicFilter = '';
            }} else {{
                activeTopicFilter = tag;
            }}
            updateTopicPillsUI();
            filterCards();
        }}

        function clearTopicFilter() {{
            activeTopicFilter = '';
            updateTopicPillsUI();
            filterCards();
        }}

        function updateTopicPillsUI() {{
            const badge = document.getElementById('activeTopicBadge');
            const text = document.getElementById('activeTopicText');
            const t = I18N[currentLang];
            if (badge && text) {{
                if (activeTopicFilter) {{
                    badge.style.display = 'flex';
                    text.textContent = t.tagFilterActive(activeTopicFilter);
                }} else {{
                    badge.style.display = 'none';
                }}
            }}
            document.querySelectorAll('.topic-pill').forEach(btn => {{
                btn.classList.toggle('active', btn.getAttribute('data-tag') === activeTopicFilter);
            }});
        }}

        function renderTrendingTopics(repos) {{
            const bar = document.getElementById('topicsBar');
            const container = document.getElementById('topicsPills');
            if (!bar || !container) return;

            const topicCounts = {{}};
            (repos || []).forEach(r => {{
                (r.topics || []).forEach(tag => {{
                    const clean = String(tag).toLowerCase().trim();
                    if (clean && clean.length > 1) {{
                        topicCounts[clean] = (topicCounts[clean] || 0) + 1;
                    }}
                }});
            }});

            const sortedTopics = Object.entries(topicCounts).sort((a, b) => b[1] - a[1]).slice(0, 12);
            if (sortedTopics.length === 0) {{
                bar.style.display = 'none';
                return;
            }}
            bar.style.display = 'flex';
            container.innerHTML = '';
            sortedTopics.forEach(([tag, count]) => {{
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'topic-pill' + (activeTopicFilter === tag ? ' active' : '');
                btn.setAttribute('data-tag', tag);
                btn.innerHTML = `#${{escapeText(tag)}} <span style="opacity:0.75; font-size:0.7rem;">(${{count}})</span>`;
                btn.onclick = () => filterByTopic(tag);
                container.appendChild(btn);
            }});
            updateTopicPillsUI();
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

            let sourceRepos = reposData;
            if (activeDomainPreset === 'bookmarks') {{
                const bmList = Object.values(bookmarksMap).map(b => b.repo_data).filter(r => r && r.name);
                sourceRepos = bmList;
                if (sourceRepos.length === 0) {{
                    const empty = document.getElementById("emptyState");
                    const grid = document.getElementById("cardsGrid");
                    const t = I18N[currentLang];
                    empty.textContent = t.emptyBookmarks;
                    empty.style.display = "block";
                    grid.innerHTML = "";
                    updateBookmarkBadge();
                    document.getElementById('resultsSummary').textContent = t.summaryText(0, 0, reposData.length, githubTotal, resultMode);
                    return;
                }}
            }}

            const filtered = sourceRepos.filter(r => {{
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
                }} else if (selectedStatus === 'bookmarked') {{
                    matchesStatus = Boolean(bookmarksMap[r.name]);
                }} else if (selectedStatus) {{
                    matchesStatus = r.user_status === selectedStatus;
                }}

                const techText = (r.tech_stack || []).join(" ");
                const topicsText = (r.topics || []).join(" ");
                const quickText = r.quick_run || "";
                const altText = r.commercial_alternative || "";
                const researchText = ['how_it_works', 'practical_examples', 'limitations', 'adoption_notes', 'comparisons'].map(key => (r[key] || []).join(' ')).join(' ');
                const corpus = normalizeSearch([
                    r.name, r.description, r.core_purpose, r.language, r.category,
                    altText, techText, topicsText, quickText, researchText, (r.key_features || []).join(' '), r.target_roles,
                ].join(' '));

                let matchesTopic = true;
                if (activeTopicFilter) {{
                    matchesTopic = (r.topics || []).some(t => String(t).toLowerCase() === activeTopicFilter.toLowerCase());
                }}
                const matchesQuery = Boolean(searchEndpoint) || !keywords.length || (mode === 'all'
                    ? keywords.every(keyword => corpus.includes(keyword))
                    : keywords.some(keyword => corpus.includes(keyword)));

                const matchesPreset = matchesDomainPreset(r, activeDomainPreset);

                return matchesCat && matchesRepoType && matchesMaturity && matchesVelocity && matchesWatchlist && matchesAlt && matchesStatus && matchesQuery && matchesPreset && matchesTopic;
            }});

            // Update Domain Preset Counts
            if (document.getElementById('countAll')) {{
                document.getElementById('countAll').textContent = reposData.length;
                ['ai', 'web', 'security', 'mobile', 'systems'].forEach(preset => {{
                    const c = reposData.filter(r => matchesDomainPreset(r, preset)).length;
                    const el = document.getElementById('count' + preset.charAt(0).toUpperCase() + preset.slice(1));
                    if (el) el.textContent = c;
                }});
            }}
                if (document.getElementById('countBookmarks')) {{
                    document.getElementById('countBookmarks').textContent = Object.keys(bookmarksMap).length;
                }}
                const expBtn = document.getElementById('exportBookmarksBtn');
                if (expBtn) expBtn.style.display = Object.keys(bookmarksMap).length > 0 ? 'inline-flex' : 'none';

            renderTrendingTopics(sourceRepos);
            // Refresh Analytics if open
            if (isAnalyticsOpen) {{
                renderAnalyticsCharts(filtered);
            }}

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

                function clearSearchInput() {{
            const input = document.getElementById('searchInput');
            const btn = document.getElementById('clearSearchInputBtn');
            if (input) {{
                input.value = '';
                input.focus();
            }}
            if (btn) btn.style.display = 'none';
            updateSearchMode();
        }}

        function toggleAdvancedSearch(forceState) {{
            const panel = document.getElementById('advancedSearchPanel');
            const btn = document.getElementById('toggleAdvancedSearchBtn');
            if (!panel) return;
            const isCurrentlyOpen = panel.style.display !== 'none';
            const nextState = (forceState !== undefined) ? forceState : !isCurrentlyOpen;
            panel.style.display = nextState ? 'block' : 'none';
            if (btn) {{
                if (nextState) {{
                    btn.classList.add('active');
                    btn.setAttribute('aria-expanded', 'true');
                }} else {{
                    btn.classList.remove('active');
                    btn.setAttribute('aria-expanded', 'false');
                }}
            }}
        }}

        function toggleSearchHelp() {{
            const container = document.getElementById('searchHelpContainer');
            if (!container) return;
            container.style.display = (container.style.display === 'none') ? 'block' : 'none';
        }}

        function updateAdvancedBadge() {{
            let count = 0;
            const src = document.getElementById('dataSource');
            if (src && src.value !== 'github') count++;
            const period = document.getElementById('trendingPeriod');
            if (period && period.value !== 'daily') count++;
            const lang = document.getElementById('githubLanguage');
            if (lang && lang.value.trim() !== '') count++;
            const sort = document.getElementById('githubSort');
            if (sort && sort.value !== 'best-match') count++;
            const mode = document.getElementById('keywordMode');
            if (mode && mode.value !== 'all') count++;
            const limit = document.getElementById('resultLimit');
            if (limit && Number(limit.value) !== 10) count++;
            const deep = document.getElementById('deepResearch');
            if (deep && deep.checked) count++;

            const badge = document.getElementById('advancedOptionsBadge');
            const toggleBtn = document.getElementById('toggleAdvancedSearchBtn');
            if (badge) {{
                if (count > 0) {{
                    badge.textContent = count;
                    badge.style.display = 'inline-block';
                    if (toggleBtn) toggleBtn.classList.add('has-active-filters');
                }} else {{
                    badge.style.display = 'none';
                    if (toggleBtn) toggleBtn.classList.remove('has-active-filters');
                }}
            }}
        }}

        function clearCardFilters() {{
            ['categoryFilter', 'repoTypeFilter', 'maturityFilter', 'velocityFilter', 'statusFilter'].forEach(id => {{
                const el = document.getElementById(id);
                if (el) el.value = '';
            }});
            const wl = document.getElementById('watchlistOnly');
            if (wl) wl.checked = false;
            const alt = document.getElementById('altOnly');
            if (alt) alt.checked = false;
            activeTopicFilter = '';
            updateTopicPillsUI();
            filterCards();
        }}

        async function searchProjects() {{
            if (!searchEndpoint) {{ filterCards(); return; }}
            if (searching || !document.getElementById('searchForm').reportValidity()) return;
            searching = true;
            const button = document.getElementById('searchButton');
            const status = document.getElementById('searchStatus');
            const error = document.getElementById('searchError');
            const t = I18N[currentLang];
            button.disabled = true; button.textContent = t.searchBtnSearching;
            if (error) {{ error.textContent = ''; error.style.display = 'none'; }}
            if (status) {{
                status.textContent = t.searchStatusSearching;
                status.style.display = 'inline-flex';
            }}
            try {{
                const response = await fetch(searchEndpoint, {{
                    method: 'POST', headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        source: document.getElementById('dataSource')?.value || 'github',
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
                document.getElementById('sourceBadge').textContent = data.source === 'hn' ? `📰 Hacker News · ${{t.timeLabels[data.timeframe] || data.timeframe}}` : resultMode === 'trending' ? `📈 Trending · ${{t.timeLabels[data.timeframe] || data.timeframe}}` : `🔎 GitHub Search · ${{data.scope === 'topic' ? (currentLang === 'vi' ? 'Chủ đề / Tag' : 'Topics / Tags') : data.scope === 'content' ? (currentLang === 'vi' ? 'Nội dung README' : 'README Content') : (currentLang === 'vi' ? 'Tên project' : 'Project Name')}}`;
                document.getElementById('velocityFilter').hidden = resultMode !== 'trending';
                populateCategories();
                ['repoTypeFilter', 'maturityFilter', 'velocityFilter', 'statusFilter'].forEach(id => {{ const el = document.getElementById(id); if (el) el.value = ''; }});
                ['watchlistOnly', 'altOnly'].forEach(id => document.getElementById(id).checked = false);
                document.getElementById('loadedCount').textContent = t.countBadge(reposData.length);
                filterCards();
                if (status) {{
                    status.textContent = resultMode === 'trending' ? t.searchStatusTrendingDone : data.incomplete_results ? t.searchStatusIncomplete : t.searchStatusSearchDone;
                    status.style.display = 'inline-flex';
                    setTimeout(() => {{
                        if (!searching && status) status.style.display = 'none';
                    }}, 3000);
                }}
            }} catch (exc) {{
                if (error) {{
                    error.textContent = exc.message || (currentLang === 'vi' ? 'Mất kết nối server. Hãy chạy lại ./trending --serve.' : 'Server connection lost. Please restart ./trending --serve.');
                    error.style.display = 'inline-flex';
                }}
                if (status) {{
                    status.textContent = t.searchStatusError;
                    status.style.display = 'inline-flex';
                }}
            }} finally {{
                searching = false; button.disabled = false; button.textContent = t.searchBtn;
            }}
        }}

        function updateSearchMode() {{
            if (!searchEndpoint) return;
            const t = I18N[currentLang];
            const searchInput = document.getElementById('searchInput');
            const clearBtn = document.getElementById('clearSearchInputBtn');
            const hasKeyword = Boolean(searchInput.value.trim());
            if (clearBtn) clearBtn.style.display = hasKeyword ? 'inline-block' : 'none';

            document.getElementById('githubSort').disabled = !hasKeyword;
            document.getElementById('keywordMode').disabled = !hasKeyword;
            document.getElementById('trendingPeriod').disabled = hasKeyword;
            const scopeVal = document.getElementById('searchScope').value;
            if (scopeVal === 'topic') {{
                searchInput.placeholder = t.searchPlaceholderTopic;
                document.getElementById('searchHelp').textContent = t.searchHelpTopic;
            }} else if (scopeVal === 'content') {{
                searchInput.placeholder = t.searchPlaceholderContent;
                document.getElementById('searchHelp').textContent = !hasKeyword ? t.searchHelpEmpty : t.searchHelpContent;
            }} else {{
                searchInput.placeholder = t.searchPlaceholderName;
                document.getElementById('searchHelp').textContent = !hasKeyword ? t.searchHelpEmpty : t.searchHelpName;
            }}
            updateAdvancedBadge();
        }}

        document.getElementById('searchInput').addEventListener('input', updateSearchMode);
        document.getElementById('searchScope').addEventListener('change', updateSearchMode);
        document.getElementById('searchForm').addEventListener('submit', event => {{
            event.preventDefault(); searchProjects();
        }});
        document.getElementById('resetSearch').addEventListener('click', () => {{
            document.getElementById('searchForm').reset();
            updateSearchMode();
            updateAdvancedBadge();
            const err = document.getElementById('searchError');
            if (err) {{ err.textContent = ''; err.style.display = 'none'; }}
            const st = document.getElementById('searchStatus');
            if (st) {{ st.textContent = ''; st.style.display = 'none'; }}
            activeTopicFilter = '';
            updateTopicPillsUI();
            ['repoTypeFilter', 'categoryFilter', 'maturityFilter', 'velocityFilter', 'statusFilter'].forEach(id => {{ const el = document.getElementById(id); if (el) el.value = ''; }});
            ['watchlistOnly', 'altOnly'].forEach(id => document.getElementById(id).checked = false);
            filterCards();
        }});

// Startup deferred to end of script

        // Domain Presets & Analytics Logic

        const DOMAIN_PRESETS = {{
            ai: {{
                categories: ['AI & Machine Learning', 'Data Science & Big Data'],
                keywords: ['ai', 'agent', 'agents', 'llm', 'gpt', 'claude', 'deepseek', 'model', 'rag', 'embedding', 'transformer', 'prompt', 'vision', 'diffusion', 'inference', 'neural', 'langchain', 'ollama', 'tree-sitter', 'openai', 'anthropic']
            }},
            web: {{
                categories: ['Web & Frontend', 'Backend & API'],
                keywords: ['web', 'frontend', 'backend', 'fullstack', 'react', 'vue', 'angular', 'next', 'nuxt', 'svelte', 'api', 'http', 'fastapi', 'flask', 'django', 'node', 'express', 'nest', 'php', 'html', 'css', 'tailwind', 'graphql', 'rest']
            }},
            security: {{
                categories: ['DevOps & Infrastructure', 'Security & Privacy', 'Cloud & Serverless'],
                keywords: ['security', 'audit', 'vuln', 'vulnerability', 'cve', 'cloud', 'docker', 'kubernetes', 'k8s', 'devops', 'infra', 'infrastructure', 'linux', 'kernel', 'monitoring', 'ci/cd', 'pipeline', 'penetration', 'firewall', 'proxy', 'auth', 'iam']
            }},
            mobile: {{
                categories: ['Mobile Development', 'Game Development & Graphics'],
                keywords: ['mobile', 'android', 'ios', 'flutter', 'react-native', 'swift', 'kotlin', 'dart', 'game', 'gaming', 'unity', 'unreal', 'godot', 'graphics', 'vfx', '3d', 'shader', 'opengl', 'vulkan', 'metal', 'webgl']
            }},
            systems: {{
                categories: ['Developer Tooling & CLI', 'System Programming', 'Databases & Storage'],
                keywords: ['c', 'c++', 'rust', 'zig', 'go', 'golang', 'assembly', 'system', 'systems', 'cli', 'compiler', 'interpreter', 'runtime', 'database', 'sqlite', 'redis', 'postgres', 'memory', 'performance', 'jit', 'ast', 'parser']
            }}
        }};

        function matchesDomainPreset(r, preset) {{
            if (!preset || preset === 'all') return true;
            if (preset === 'bookmarks') return Boolean(bookmarksMap[r.name]);
            const def = DOMAIN_PRESETS[preset];
            if (!def) return true;
            if (def.categories.includes(r.category)) return true;
            const corpus = normalizeSearch([
                r.name, r.description, r.core_purpose, r.language, r.category,
                (r.tech_stack || []).join(' '), (r.key_features || []).join(' '), r.target_roles || ''
            ].join(' '));
            return def.keywords.some(k => corpus.includes(k));
        }}

        function selectDomainPreset(preset) {{
            activeDomainPreset = preset;
            document.querySelectorAll('.preset-pill').forEach(btn => {{
                btn.classList.toggle('active', btn.getAttribute('data-preset') === preset);
            }});
            filterCards();
        }}

        function toggleAnalyticsPanel() {{
            const panel = document.getElementById('analyticsPanel');
            const btn = document.getElementById('lblBtnAnalytics');
            const t = I18N[currentLang];
            if (!panel) return;
            isAnalyticsOpen = !isAnalyticsOpen;
            panel.style.display = isAnalyticsOpen ? 'block' : 'none';
            if (btn) btn.textContent = isAnalyticsOpen ? t.lblBtnAnalyticsHide : t.lblBtnAnalytics;
            if (isAnalyticsOpen) {{
                renderAnalyticsCharts();
            }}
        }}

        function renderAnalyticsCharts(reposToChart) {{
            const repos = reposToChart || reposData || [];
            if (!repos.length) return;
            const t = I18N[currentLang];

            // 1. Velocity Leaderboard
            const sortedByStars = [...repos].sort((a, b) => {{
                const sA = Number(String(a.stars_since || a.hn_points || 0).replace(/[^0-9]/g, '')) || 0;
                const sB = Number(String(b.stars_since || b.hn_points || 0).replace(/[^0-9]/g, '')) || 0;
                return sB - sA;
            }}).slice(0, 8);

            const maxStars = Math.max(1, ...(sortedByStars.map(r => Number(String(r.stars_since || r.hn_points || 0).replace(/[^0-9]/g, '')) || 0)));
            const barsContainer = document.getElementById('velocityChartBars');
            if (barsContainer) {{
                barsContainer.innerHTML = '';
                sortedByStars.forEach(r => {{
                    const stars = Number(String(r.stars_since || r.hn_points || 0).replace(/[^0-9]/g, '')) || 0;
                    const pct = Math.max(8, Math.round((stars / maxStars) * 100));
                    const row = document.createElement('div');
                    row.className = 'velocity-bar-row';
                    row.innerHTML = `
                        <a href="${{r.url}}" target="_blank" class="velocity-bar-name" title="${{r.name}}">📦 ${{r.name}}</a>
                        <div class="velocity-bar-bg">
                            <div class="velocity-bar-fill" style="width: ${{pct}}%;"></div>
                        </div>
                        <div class="velocity-bar-val">${{r.hn_points ? '▲ ' + stars : '+' + stars.toLocaleString()}} ${{t.chartStarsUnit}}</div>
                    `;
                    barsContainer.appendChild(row);
                }});
            }}

            // 2. Domain Distribution Stacked Bar
            const domainCounts = {{ ai: 0, web: 0, security: 0, mobile: 0, systems: 0, other: 0 }};
            const domainColors = {{
                ai: '#a371f7',
                web: '#58a6ff',
                security: '#f85149',
                mobile: '#f0883e',
                systems: '#3fb950',
                other: '#8b949e'
            }};
            const domainNames = {{
                ai: 'AI & Agent',
                web: 'Web',
                security: 'Security',
                mobile: 'Mobile/Game',
                systems: 'Systems',
                other: 'Other'
            }};

            repos.forEach(r => {{
                let matched = false;
                for (const d of ['ai', 'web', 'security', 'mobile', 'systems']) {{
                    if (matchesDomainPreset(r, d)) {{
                        domainCounts[d]++;
                        matched = true;
                        break;
                    }}
                }}
                if (!matched) domainCounts.other++;
            }});

            const total = repos.length;
            const stackedBar = document.getElementById('domainStackedBar');
            const legend = document.getElementById('domainLegend');
            if (stackedBar && legend) {{
                stackedBar.innerHTML = '';
                legend.innerHTML = '';
                for (const [key, count] of Object.entries(domainCounts)) {{
                    if (count === 0) continue;
                    const pct = Math.round((count / total) * 100);
                    const seg = document.createElement('div');
                    seg.style.cssText = `width: ${{pct}}%; background: ${{domainColors[key]}}; height: 100%; transition: width 0.3s;`;
                    seg.title = `${{domainNames[key]}}: ${{count}} (${{pct}}%)`;
                    stackedBar.appendChild(seg);

                    const legItem = document.createElement('div');
                    legItem.className = 'legend-item';
                    legItem.innerHTML = `<span class="legend-dot" style="background: ${{domainColors[key]}}"></span> ${{domainNames[key]}}: <strong>${{pct}}%</strong> (${{count}})`;
                    legend.appendChild(legItem);
                }}
            }}

            // 3. Maturity Breakdown
            const matCounts = {{ production: 0, beta: 0, experimental: 0 }};
            repos.forEach(r => {{
                if (r.maturity_level === 'production') matCounts.production++;
                else if (r.maturity_level === 'experimental') matCounts.experimental++;
                else matCounts.beta++;
            }});
            const matContainer = document.getElementById('maturityBars');
            if (matContainer) {{
                matContainer.innerHTML = `
                    <div class="maturity-row"><span>🟢 Production Ready:</span> <strong>${{matCounts.production}} (${{Math.round(matCounts.production / total * 100)}}%)</strong></div>
                    <div class="maturity-row"><span>🟡 Beta / Active:</span> <strong>${{matCounts.beta}} (${{Math.round(matCounts.beta / total * 100)}}%)</strong></div>
                    <div class="maturity-row"><span>🟠 Experimental:</span> <strong>${{matCounts.experimental}} (${{Math.round(matCounts.experimental / total * 100)}}%)</strong></div>
                `;
            }}
        }}

        // Deep Dive Modal Logic
        function closeDeepDiveModal() {{
            const modal = document.getElementById('deepDiveModal');
            if (modal) {{
                modal.classList.remove('open');
                setTimeout(() => {{ modal.style.display = 'none'; }}, 200);
            }}
        }}

                // Side-by-Side Comparison & Dock Logic
                let allStarChartsVisible = true;
        function toggleCardStarHistory(btn, idx) {{
            const body = document.getElementById(`cardSh_${{idx}}`);
            if (!body) return;
            const isHidden = body.style.display === 'none';
            body.style.display = isHidden ? 'block' : 'none';
            const arrow = btn.querySelector('.sh-arrow');
            const text = btn.querySelector('.sh-text');
            const t = I18N[currentLang];
            if (arrow) arrow.textContent = isHidden ? '▴' : '▾';
            if (text) text.textContent = isHidden ? t.cardStarHistoryHide : t.cardStarHistoryShow;
        }}

        function toggleAllStarCharts() {{
            allStarChartsVisible = !allStarChartsVisible;
            const t = I18N[currentLang];
            const bodies = document.querySelectorAll('.card-sh-body');
            bodies.forEach(b => {{
                b.style.display = allStarChartsVisible ? 'block' : 'none';
            }});
            document.querySelectorAll('.btn-toggle-card-sh').forEach(btn => {{
                const arrow = btn.querySelector('.sh-arrow');
                const text = btn.querySelector('.sh-text');
                if (arrow) arrow.textContent = allStarChartsVisible ? '▴' : '▾';
                if (text) text.textContent = allStarChartsVisible ? t.cardStarHistoryHide : t.cardStarHistoryShow;
            }});
            const globalBtn = document.getElementById('lblToggleAllCharts');
            if (globalBtn) {{
                globalBtn.textContent = allStarChartsVisible ? t.btnCollapseAllCharts : t.btnExpandAllCharts;
            }}
        }}

        function toggleCompareRepo(name) {{
            if (compareSet.has(name)) {{
                compareSet.delete(name);
            }} else {{
                if (compareSet.size >= 4) {{
                    const t = I18N[currentLang];
                    alert(t.compareLimitAlert || "Tối đa so sánh 4 repository cùng lúc.");
                    return;
                }}
                compareSet.add(name);
            }}
            updateCompareDockUI();
            document.querySelectorAll(`.btn-compare[data-name="${{CSS.escape(name)}}"]`).forEach(btn => {{
                btn.classList.toggle('active', compareSet.has(name));
                const label = btn.querySelector('.compare-label');
                if (label) {{
                    const t = I18N[currentLang];
                    label.textContent = compareSet.has(name) ? t.btnCompared : t.btnCompare;
                }}
            }});
        }}

        function clearComparison() {{
            compareSet.clear();
            updateCompareDockUI();
            document.querySelectorAll('.btn-compare').forEach(btn => {{
                btn.classList.remove('active');
                const label = btn.querySelector('.compare-label');
                if (label) label.textContent = I18N[currentLang].btnCompare;
            }});
        }}

        function updateCompareDockUI() {{
            const dock = document.getElementById('compareDock');
            const chips = document.getElementById('compareChips');
            const launchBtnText = document.getElementById('lblBtnLaunchCompare');
            if (!dock) return;
            const t = I18N[currentLang];
            if (compareSet.size === 0) {{
                dock.style.display = 'none';
                return;
            }}
            dock.style.display = 'flex';
            if (launchBtnText) {{
                launchBtnText.textContent = `${{t.btnLaunchCompare}} (${{compareSet.size}})`;
            }}
            if (chips) {{
                chips.innerHTML = Array.from(compareSet).map(name => `
                    <span class="compare-chip">
                        <span>${{escapeText(name)}}</span>
                        <span class="compare-chip-remove" onclick="toggleCompareRepo('${{escapeText(name)}}')">✕</span>
                    </span>
                `).join('');
            }}
        }}

                let currentSimilarSourceRepo = null;
        async function openSimilarModal(name, idx) {{
            const modal = document.getElementById('similarModal');
            const title = document.getElementById('similarModalTitle');
            const sub = document.getElementById('similarModalSubtitle');
            const loading = document.getElementById('similarLoadingState');
            const errorEl = document.getElementById('similarErrorState');
            const grid = document.getElementById('similarCardsGrid');
            const cmpBtn = document.getElementById('btnSimilarOpenCompare');
            if (!modal) return;
            const t = I18N[currentLang];

            currentSimilarSourceRepo = name;
            title.textContent = t.similarModalTitle(name);
            sub.textContent = t.similarModalSubtitle;
            grid.innerHTML = '';
            errorEl.style.display = 'none';
            loading.style.display = 'block';
            if (cmpBtn) cmpBtn.style.display = (compareSet.size >= 2) ? 'inline-flex' : 'none';

            modal.style.display = 'flex';
            setTimeout(() => {{ modal.classList.add('open'); }}, 10);

            // Fetch similar from server
            const repoObj = reposData[idx] || {{ name }};
            try {{
                const res = await fetch('/api/similar', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        full_name: name,
                        category: repoObj.category || '',
                        topics: repoObj.topics || [],
                        language: repoObj.language || '',
                        description: repoObj.description || repoObj.core_purpose || ''
                    }})
                }});
                const data = await res.json();
                loading.style.display = 'none';

                if (!res.ok) throw new Error(data.error || 'Lỗi tìm kiếm.');
                const list = data.similar_repos || [];
                if (list.length === 0) {{
                    grid.innerHTML = `<div style="grid-column: 1 / -1; text-align:center; padding:30px; color:var(--text-muted); font-size:0.9rem;">${{t.similarEmpty}}</div>`;
                    return;
                }}

                grid.innerHTML = list.map(item => {{
                    const isCmp = compareSet.has(item.name);
                    const rawUrl = item.url || `https://github.com/${{item.name}}`;
                    return `
                        <div class="similar-card">
                            <div class="similar-card-header">
                                <a href="${{escapeText(rawUrl)}}" target="_blank" style="font-size:0.95rem; font-weight:700; color:var(--accent-blue); text-decoration:none; word-break:break-word;">
                                    📦 ${{escapeText(item.name)}}
                                </a>
                                <span class="stars-pill" style="font-size:0.75rem;">★ ${{item.stars_total ? Number(item.stars_total).toLocaleString() : '0'}}</span>
                            </div>
                            <div style="display:flex; gap:6px; flex-wrap:wrap; font-size:0.78rem;">
                                <span class="pill-tag">${{escapeText(item.language || 'Unknown')}}</span>
                                <span class="pill-tag tag-category">${{escapeText(item.category || '')}}</span>
                            </div>
                            ${{item.similarity_reason ? `<span class="similar-reason-pill">💡 ${{escapeText(item.similarity_reason)}}</span>` : ''}}
                            <div style="font-size:0.84rem; color:var(--text-bright); line-height:1.4; flex:1;">
                                ${{escapeText(item.core_purpose || item.description || '')}}
                            </div>
                            <div class="similar-card-actions">
                                <button type="button" class="btn-compare ${{isCmp ? 'active' : ''}}" style="padding:4px 8px; font-size:0.78rem;" onclick="addSimilarToCompare(this, '${{escapeText(item.name)}}')">
                                    <span>${{isCmp ? t.similarComparedBtn : t.similarCompareBtn}}</span>
                                </button>
                                <div class="ide-dropdown-wrapper">
                                    <button type="button" class="btn-ide" style="padding:4px 7px; font-size:0.75rem;">
                                        <span>⚡ Code</span> <span style="font-size:0.65rem;">▾</span>
                                    </button>
                                    <div class="ide-menu">
                                        <a href="cursor://vscode.git/clone?url=${{escapeText(rawUrl)}}.git" class="ide-menu-item">
                                            <span>🚀 Cursor</span>
                                        </a>
                                        <a href="vscode://vscode.git/clone?url=${{escapeText(rawUrl)}}.git" class="ide-menu-item">
                                            <span>💻 VS Code</span>
                                        </a>
                                        <a href="https://github.dev/${{escapeText(item.name)}}" target="_blank" class="ide-menu-item">
                                            <span>🌐 GitHub.dev</span>
                                        </a>
                                    </div>
                                </div>
                                <a href="${{escapeText(rawUrl)}}" target="_blank" class="btn-view" style="padding:3px 8px; font-size:0.75rem; margin-left:auto;">${{t.viewOnGithub}}</a>
                            </div>
                        </div>
                    `;
                }}).join('');

                // Also inject into reposData if not already present, so comparison modal can access it!
                list.forEach(simItem => {{
                    if (!reposData.some(r => r.name === simItem.name)) {{
                        reposData.push(simItem);
                    }}
                }});

            }} catch (err) {{
                loading.style.display = 'none';
                errorEl.textContent = err.message;
                errorEl.style.display = 'block';
            }}
        }}

        function addSimilarToCompare(btn, name) {{
            const t = I18N[currentLang];
            // If source repo not in compareSet, add it first!
            if (currentSimilarSourceRepo && !compareSet.has(currentSimilarSourceRepo)) {{
                toggleCompareRepo(currentSimilarSourceRepo);
            }}
            toggleCompareRepo(name);
            const isCmp = compareSet.has(name);
            btn.classList.toggle('active', isCmp);
            btn.querySelector('span').textContent = isCmp ? t.similarComparedBtn : t.similarCompareBtn;

            const cmpBtn = document.getElementById('btnSimilarOpenCompare');
            if (cmpBtn) {{
                cmpBtn.style.display = (compareSet.size >= 2) ? 'inline-flex' : 'none';
                const label = document.getElementById('lblSimilarOpenCompare');
                if (label) label.textContent = t.similarOpenCompare(compareSet.size);
            }}
        }}

        function closeSimilarModal() {{
            const modal = document.getElementById('similarModal');
            if (modal) {{
                modal.classList.remove('open');
                setTimeout(() => {{ modal.style.display = 'none'; }}, 200);
            }}
        }}

        function formatReleaseDate(isoString) {{
            if (!isoString) return '';
            try {{
                const d = new Date(isoString);
                if (isNaN(d.getTime())) return isoString;
                const diffMs = Date.now() - d.getTime();
                const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                const formatted = d.toLocaleDateString(currentLang === 'vi' ? 'vi-VN' : 'en-US', {{ year: 'numeric', month: 'short', day: 'numeric' }});
                if (diffDays <= 0) return `${{formatted}} (${{currentLang === 'vi' ? 'Hôm nay' : 'Today'}})`;
                if (diffDays === 1) return `${{formatted}} (${{currentLang === 'vi' ? 'Hôm qua' : 'Yesterday'}})`;
                if (diffDays < 30) return `${{formatted}} (${{diffDays}} ${{currentLang === 'vi' ? 'ngày trước' : 'days ago'}})`;
                return formatted;
            }} catch (e) {{
                return isoString;
            }}
        }}

        function downloadTextFile(filename, content) {{
            const blob = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            setTimeout(() => {{
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}, 100);
        }}

        function generateClientPlayground(raw) {{
            const name = raw.name || '';
            const lang = (raw.language || '').toLowerCase();
            const desc = (raw.description || '').toLowerCase();
            const quick = raw.quick_run || '';
            let slug = name.split('/').pop().toLowerCase().replace(/[^a-z0-9_-]/g, '-').replace(/^-+|-+$/g, '') || 'app';
            let port = 8080;
            let framework = 'App';
            let category = 'general';

            if (desc.includes('ollama') || quick.includes('11434')) {{
                port = 11434; framework = 'Ollama / LLM'; category = 'ai';
            }} else if (desc.includes('streamlit')) {{
                port = 8501; framework = 'Streamlit'; category = 'ai_web';
            }} else if (desc.includes('gradio')) {{
                port = 7860; framework = 'Gradio'; category = 'ai_web';
            }} else if (desc.includes('fastapi') || desc.includes('uvicorn')) {{
                port = 8000; framework = 'FastAPI'; category = 'backend';
            }} else if (desc.includes('flask')) {{
                port = 5000; framework = 'Flask'; category = 'backend';
            }} else if (desc.includes('vite')) {{
                port = 5173; framework = 'Vite'; category = 'frontend';
            }} else if (['typescript', 'javascript'].includes(lang) || desc.includes('react') || desc.includes('next')) {{
                port = 3000; framework = 'Node.js / Web'; category = 'frontend';
            }} else if (['python', 'jupyter notebook'].includes(lang)) {{
                port = 8000; framework = 'Python'; category = 'python';
            }} else if (['go', 'golang'].includes(lang)) {{
                port = 8080; framework = 'Go'; category = 'backend';
            }} else if (lang === 'rust') {{
                port = 8080; framework = 'Rust'; category = 'system';
            }}

            let installCmd = 'npm install';
            let runCmd = 'npm run dev';
            if (category === 'frontend') {{
                if (quick.includes('pnpm')) {{ installCmd = 'pnpm install'; runCmd = 'pnpm dev'; }}
                else if (quick.includes('yarn')) {{ installCmd = 'yarn install'; runCmd = 'yarn dev'; }}
            }} else if (['backend', 'ai_web', 'python'].includes(category)) {{
                installCmd = 'pip install -r requirements.txt';
                runCmd = framework === 'FastAPI' ? `uvicorn main:app --reload --port ${{port}}` : 'python main.py';
            }} else if (lang.includes('go')) {{
                installCmd = 'go mod download';
                runCmd = 'go run .';
            }} else if (lang === 'rust') {{
                installCmd = 'cargo build';
                runCmd = 'cargo run';
            }}
            if (quick && !quick.includes('docker')) {{
                if (quick.includes('install')) installCmd = quick;
                else runCmd = quick;
            }}

            const cloudLinks = [
                {{
                    id: 'codespaces',
                    name: 'GitHub Codespaces',
                    icon: '🚀',
                    badge: 'Full Linux VM',
                    url: `https://codespaces.new/${{name}}`,
                    description: 'Máy ảo Linux đám mây của GitHub (60h miễn phí/tháng, sẵn sàng trong 30s).',
                    recommended: true,
                }},
                {{
                    id: 'gitpod',
                    name: 'Gitpod',
                    icon: '⚡',
                    badge: 'Automated Dev',
                    url: `https://gitpod.io/#https://github.com/${{name}}`,
                    description: 'Khởi động môi trường dev tự động cài dependencies từ git repo.',
                    recommended: false,
                }},
                {{
                    id: 'github_dev',
                    name: 'GitHub.dev',
                    icon: '💻',
                    badge: 'Web VS Code',
                    url: `https://github.dev/${{name}}`,
                    description: 'Đọc và duyệt mã nguồn tức thì bằng giao diện VS Code trong trình duyệt.',
                    recommended: false,
                }}
            ];

            if (['python', 'jupyter notebook'].includes(lang) || desc.includes('ai') || desc.includes('model') || desc.includes('pytorch')) {{
                cloudLinks.push({{
                    id: 'colab',
                    name: 'Google Colab',
                    icon: '🔬',
                    badge: 'Free GPU / TPU',
                    url: `https://colab.research.google.com/github/${{name}}/blob/main/`,
                    description: 'Chạy thử mô hình AI hoặc notebook trên GPU/TPU miễn phí của Google.',
                    recommended: true,
                }});
            }}
            if (['typescript', 'javascript'].includes(lang) || category === 'frontend') {{
                cloudLinks.push({{
                    id: 'stackblitz',
                    name: 'StackBlitz',
                    icon: '⚡',
                    badge: 'In-Browser Node',
                    url: `https://stackblitz.com/github/${{name}}`,
                    description: 'Khởi chạy Node.js và dev server ngay trong trình duyệt qua WebAssembly.',
                    recommended: true,
                }});
            }}

            const dockerCompose = `version: '3.8'\n\nservices:\n  ${{slug}}:\n    build: .\n    container_name: ${{slug}}-playground\n    ports:\n      - "${{port}}:${{port}}"\n    environment:\n      - PORT=${{port}}\n      - ENV=development\n    volumes:\n      - .:/app\n    restart: unless-stopped`;
            const dockerfile = category === 'frontend' ?
                `FROM node:20-alpine\nWORKDIR /app\nCOPY package*.json ./\nRUN npm install\nCOPY . .\nEXPOSE ${{port}}\nCMD ["npm", "run", "dev"]` :
                `FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt* ./\nRUN pip install --no-cache-dir -r requirements.txt || true\nCOPY . .\nEXPOSE ${{port}}\nCMD ["python", "main.py"]`;

            return {{
                repo_name: name,
                slug: slug,
                framework: framework,
                port: port,
                category: category,
                install_cmd: installCmd,
                run_cmd: runCmd,
                cloud_links: cloudLinks,
                docker: {{
                    docker_compose: dockerCompose,
                    dockerfile: dockerfile,
                    docker_run_cmd: 'docker compose up --build -d'
                }},
                scripts: {{
                    bash: `#!/usr/bin/env bash\nset -e\ngit clone https://github.com/${{name}}.git ${{slug}}\ncd ${{slug}}\n${{installCmd}}\n${{runCmd}}`,
                    powershell: `$ErrorActionPreference = "Stop"\ngit clone https://github.com/${{name}}.git ${{slug}}\nSet-Location ${{slug}}\n${{installCmd}}\n${{runCmd}}`,
                    one_liner: `git clone https://github.com/${{name}}.git ${{slug}} && cd ${{slug}} && ${{installCmd}} && ${{runCmd}}`
                }}
            }};
        }}

        function buildPlaygroundDOM(manifest, raw) {{
            const t = I18N[currentLang];
            const wrap = document.createElement('div');
            wrap.className = 'playground-container';

            const slug = manifest.slug || 'app';
            const port = manifest.port || 8080;
            const framework = manifest.framework || 'Generic';
            const docker = manifest.docker || {{}};
            const scripts = manifest.scripts || {{}};
            const cloudLinks = manifest.cloud_links || [];

            // Meta Info Bar
            const metaBar = document.createElement('div');
            metaBar.className = 'playground-meta-bar';
            metaBar.innerHTML = `
                <span><strong>Framework:</strong> <code style="color:#58a6ff;">${{escapeText(framework)}}</code></span>
                <span><strong>Default Port:</strong> <code style="color:#3fb950;">:${{port}}</code></span>
                <span><strong>Container:</strong> <code style="color:#bc8cff;">${{escapeText(slug)}}-playground</code></span>
            `;
            wrap.appendChild(metaBar);

            // Subtabs
            const subtabs = document.createElement('div');
            subtabs.className = 'playground-subtabs';
            subtabs.innerHTML = `
                <button type="button" class="pg-subtab-btn active" data-tab="cloud">
                    <span>${{t.pgCloudTab}}</span> (${{cloudLinks.length}})
                </button>
                <button type="button" class="pg-subtab-btn" data-tab="docker">
                    <span>${{t.pgDockerTab}}</span>
                </button>
                <button type="button" class="pg-subtab-btn" data-tab="scripts">
                    <span>${{t.pgScriptsTab}}</span>
                </button>
            `;
            wrap.appendChild(subtabs);

            // Panes Container
            const panesWrap = document.createElement('div');

            // --- Pane 1: Cloud 1-Click ---
            const paneCloud = document.createElement('div');
            paneCloud.className = 'pg-pane pg-pane-cloud';
            const cloudGrid = document.createElement('div');
            cloudGrid.className = 'playground-cloud-grid';
            cloudLinks.forEach(cl => {{
                const card = document.createElement('div');
                card.className = `playground-cloud-card ${{cl.recommended ? 'recommended' : ''}}`;
                card.innerHTML = `
                    <div class="cloud-card-header">
                        <div class="cloud-card-title">
                            <span>${{cl.icon || '🚀'}}</span>
                            <span>${{escapeText(cl.name)}}</span>
                        </div>
                        <span class="cloud-card-badge">${{escapeText(cl.badge || 'Cloud')}}</span>
                    </div>
                    <div class="cloud-card-desc">${{escapeText(cl.description || '')}}</div>
                    <a href="${{escapeText(cl.url)}}" target="_blank" rel="noopener noreferrer" class="btn-cloud-launch">
                        <span>${{t.pgLaunchBtn}}</span>
                    </a>
                `;
                cloudGrid.appendChild(card);
            }});
            paneCloud.appendChild(cloudGrid);
            panesWrap.appendChild(paneCloud);

            // --- Pane 2: Docker Compose & Dockerfile ---
            const paneDocker = document.createElement('div');
            paneDocker.className = 'pg-pane pg-pane-docker';
            paneDocker.style.display = 'none';

            let curDockerMode = 'compose';
            const dockerSubNav = document.createElement('div');
            dockerSubNav.className = 'playground-subtabs';
            dockerSubNav.style.marginTop = '4px';
            dockerSubNav.innerHTML = `
                <button type="button" class="pg-subtab-btn active" data-dmode="compose">
                    <span>📄 docker-compose.yml</span>
                </button>
                <button type="button" class="pg-subtab-btn" data-dmode="dockerfile">
                    <span>🐳 Dockerfile</span>
                </button>
                <button type="button" class="pg-subtab-btn" data-dmode="cli">
                    <span>⚡ CLI Run</span>
                </button>
            `;

            const dockerCodeCard = document.createElement('div');
            dockerCodeCard.className = 'playground-code-card';
            
            function renderDockerCard() {{
                let title = 'docker-compose.yml';
                let content = docker.docker_compose || '';
                if (curDockerMode === 'dockerfile') {{
                    title = 'Dockerfile';
                    content = docker.dockerfile || '';
                }} else if (curDockerMode === 'cli') {{
                    title = 'Command Line';
                    content = docker.docker_run_cmd || 'docker compose up -d';
                }}

                dockerCodeCard.innerHTML = `
                    <div class="playground-code-header">
                        <div class="playground-file-pill">
                            <span>📄</span> <span>${{title}}</span>
                        </div>
                        <div class="playground-actions-group">
                            <button type="button" class="btn-pg-action btn-pg-copy">
                                <span>${{t.pgCopyBtn}}</span>
                            </button>
                            ${{curDockerMode !== 'cli' ? `
                                <button type="button" class="btn-pg-action btn-pg-dl">
                                    <span>${{t.pgDownloadBtn}}</span>
                                </button>
                            ` : ''}}
                        </div>
                    </div>
                    <pre class="playground-code-area"><code>${{escapeText(content)}}</code></pre>
                `;

                const cpBtn = dockerCodeCard.querySelector('.btn-pg-copy');
                if (cpBtn) {{
                    cpBtn.addEventListener('click', () => {{
                        navigator.clipboard.writeText(content).then(() => {{
                            const old = cpBtn.innerHTML;
                            cpBtn.innerHTML = `<span>✓ ${{t.pgCopied}}</span>`;
                            setTimeout(() => {{ cpBtn.innerHTML = old; }}, 1600);
                        }});
                    }});
                }}
                const dlBtn = dockerCodeCard.querySelector('.btn-pg-dl');
                if (dlBtn) {{
                    dlBtn.addEventListener('click', () => {{
                        downloadTextFile(title, content);
                    }});
                }}
            }}

            dockerSubNav.querySelectorAll('.pg-subtab-btn').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    dockerSubNav.querySelectorAll('.pg-subtab-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    curDockerMode = btn.getAttribute('data-dmode');
                    renderDockerCard();
                }});
            }});

            renderDockerCard();

            const dockerTip = document.createElement('div');
            dockerTip.className = 'playground-tip-box';
            dockerTip.style.marginTop = '12px';
            dockerTip.textContent = t.pgTipDocker;

            paneDocker.appendChild(dockerSubNav);
            paneDocker.appendChild(dockerCodeCard);
            paneDocker.appendChild(dockerTip);
            panesWrap.appendChild(paneDocker);

            // --- Pane 3: Local Scripts ---
            const paneScripts = document.createElement('div');
            paneScripts.className = 'pg-pane pg-pane-scripts';
            paneScripts.style.display = 'none';

            let curScriptMode = 'powershell';
            const scriptSubNav = document.createElement('div');
            scriptSubNav.className = 'playground-subtabs';
            scriptSubNav.style.marginTop = '4px';
            scriptSubNav.innerHTML = `
                <button type="button" class="pg-subtab-btn active" data-smode="powershell">
                    <span>🪟 PowerShell (Windows)</span>
                </button>
                <button type="button" class="pg-subtab-btn" data-smode="bash">
                    <span>🐧 Bash (Linux / Mac / WSL)</span>
                </button>
                <button type="button" class="pg-subtab-btn" data-smode="oneliner">
                    <span>⚡ One-liner</span>
                </button>
            `;

            const scriptCodeCard = document.createElement('div');
            scriptCodeCard.className = 'playground-code-card';

            function renderScriptCard() {{
                let title = 'run.ps1';
                let content = scripts.powershell || '';
                if (curScriptMode === 'bash') {{
                    title = 'run.sh';
                    content = scripts.bash || '';
                }} else if (curScriptMode === 'oneliner') {{
                    title = 'Terminal One-Liner';
                    content = scripts.one_liner || '';
                }}

                scriptCodeCard.innerHTML = `
                    <div class="playground-code-header">
                        <div class="playground-file-pill">
                            <span>📜</span> <span>${{title}}</span>
                        </div>
                        <div class="playground-actions-group">
                            <button type="button" class="btn-pg-action btn-pg-script-copy">
                                <span>${{t.pgCopyBtn}}</span>
                            </button>
                            ${{curScriptMode !== 'oneliner' ? `
                                <button type="button" class="btn-pg-action btn-pg-script-dl">
                                    <span>${{t.pgDownloadBtn}}</span>
                                </button>
                            ` : ''}}
                        </div>
                    </div>
                    <pre class="playground-code-area"><code>${{escapeText(content)}}</code></pre>
                `;

                const cpBtn = scriptCodeCard.querySelector('.btn-pg-script-copy');
                if (cpBtn) {{
                    cpBtn.addEventListener('click', () => {{
                        navigator.clipboard.writeText(content).then(() => {{
                            const old = cpBtn.innerHTML;
                            cpBtn.innerHTML = `<span>✓ ${{t.pgCopied}}</span>`;
                            setTimeout(() => {{ cpBtn.innerHTML = old; }}, 1600);
                        }});
                    }});
                }}
                const dlBtn = scriptCodeCard.querySelector('.btn-pg-script-dl');
                if (dlBtn) {{
                    dlBtn.addEventListener('click', () => {{
                        downloadTextFile(title, content);
                    }});
                }}
            }}

            scriptSubNav.querySelectorAll('.pg-subtab-btn').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    scriptSubNav.querySelectorAll('.pg-subtab-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    curScriptMode = btn.getAttribute('data-smode');
                    renderScriptCard();
                }});
            }});

            renderScriptCard();

            const scriptTip = document.createElement('div');
            scriptTip.className = 'playground-tip-box';
            scriptTip.style.marginTop = '12px';
            scriptTip.textContent = t.pgTipScript;

            paneScripts.appendChild(scriptSubNav);
            paneScripts.appendChild(scriptCodeCard);
            paneScripts.appendChild(scriptTip);
            panesWrap.appendChild(paneScripts);

            // Subtabs switching logic
            subtabs.querySelectorAll('.pg-subtab-btn').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    subtabs.querySelectorAll('.pg-subtab-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    const tab = btn.getAttribute('data-tab');
                    paneCloud.style.display = tab === 'cloud' ? 'block' : 'none';
                    paneDocker.style.display = tab === 'docker' ? 'block' : 'none';
                    paneScripts.style.display = tab === 'scripts' ? 'block' : 'none';
                }});
            }});

            wrap.appendChild(panesWrap);
            return wrap;
        }}

        function openPlaygroundModal(raw) {{
            const modal = document.getElementById('playgroundModal');
            const title = document.getElementById('playgroundModalTitle');
            const body = document.getElementById('playgroundModalBody');
            if (!modal || !body) return;

            const t = I18N[currentLang];
            if (title) title.innerHTML = `<span>⚡</span> <span>${{t.playgroundModalTitle(escapeText(raw.name))}}</span>`;

            const manifest = raw.playground || generateClientPlayground(raw);
            body.innerHTML = '';
            body.appendChild(buildPlaygroundDOM(manifest, raw));

            modal.style.display = 'flex';
            setTimeout(() => {{ modal.classList.add('open'); }}, 10);
        }}

        function closePlaygroundModal() {{
            const modal = document.getElementById('playgroundModal');
            if (modal) {{
                modal.classList.remove('open');
                setTimeout(() => {{ modal.style.display = 'none'; }}, 200);
            }}
        }}

        async function renderMermaidSafe(canvasId, fallbackId, code) {{
            const canvas = document.getElementById(canvasId);
            const fallback = document.getElementById(fallbackId);
            if (!canvas) return;
            if (!code || !code.trim()) {{
                canvas.innerHTML = '<div style="color:var(--text-muted); padding:20px; text-align:center;">Chưa có sơ đồ kiến trúc.</div>';
                return;
            }}
            if (typeof mermaid === 'undefined') {{
                canvas.style.display = 'none';
                if (fallback) fallback.style.display = 'block';
                return;
            }}
            try {{
                const cleanCode = code.trim();
                const uniqueId = 'mermaidSvg_' + Math.random().toString(36).substring(2, 9);
                const res = await mermaid.render(uniqueId, cleanCode);
                canvas.innerHTML = res.svg;
                canvas.style.display = 'flex';
                if (fallback) fallback.style.display = 'none';
            }} catch (err) {{
                console.warn('Mermaid render error:', err);
                canvas.style.display = 'none';
                if (fallback) fallback.style.display = 'block';
            }}
        }}

        function copyMermaidCode(btn) {{
            const code = btn._mermaidCode || '';
            const t = I18N[currentLang];
            navigator.clipboard.writeText(code).then(() => {{
                const span = btn.querySelector('span:last-child');
                const orig = span ? span.textContent : '';
                if (span) span.textContent = t.archCopied;
                btn.style.borderColor = 'var(--accent-green)';
                btn.style.color = 'var(--accent-green)';
                setTimeout(() => {{
                    if (span) span.textContent = orig;
                    btn.style.borderColor = '';
                    btn.style.color = '';
                }}, 2000);
            }}).catch(() => {{
                prompt('Mermaid Code:', code);
            }});
        }}

        function openComparisonModal() {{
            const modal = document.getElementById('comparisonModal');
            const body = document.getElementById('comparisonModalBody');
            if (!modal || !body || compareSet.size === 0) return;
            const t = I18N[currentLang];
            const selectedRepos = reposData.filter(r => compareSet.has(r.name));
            if (!selectedRepos.length) return;

            const repoNames = selectedRepos.map(r => r.name);
            const starHistoryUrl = `https://api.star-history.com/svg?repos=${{repoNames.join(',')}}&type=Date`;
            const starHistoryWeb = `https://star-history.com/#${{repoNames.join('&')}}&Date`;

            let html = `
                <div class="comparison-grid">
                    ${{selectedRepos.map((r, i) => {{
                        const velClass = getVelocityBadgeClass(r.velocity_badge);
                        const matClass = getMaturityBadgeClass(r.maturity_level);
                        const displayCore = getDisplayCorePurpose(r, currentLang, `cmp_p_${{i}}`);
                        const displayMajor = getRoleField(r, 'suitable_major', currentLang);
                        const displayRoles = getRoleField(r, 'target_roles', currentLang);
                        const displayImpact = getRoleField(r, 'real_world_impact', currentLang);
                        const repoTypeDisplay = t.repoTypeBadges[r.repo_type] || r.repo_type_badge || '';
                        const rawUrl = r.url || `https://github.com/${{r.name}}`;

                        return `
                            <div class="comparison-card">
                                <div class="comparison-card-header">
                                    <div style="display:flex; justify-content:space-between; align-items:start; gap:8px; margin-bottom:8px;">
                                        <a href="${{escapeText(rawUrl)}}" target="_blank" style="font-size:1.05rem; font-weight:700; color:var(--accent-blue); text-decoration:none; word-break:break-word;">
                                            📦 ${{escapeText(r.name)}}
                                        </a>
                                        <button type="button" class="btn-clear-compare" onclick="toggleCompareRepo('${{escapeText(r.name)}}'); openComparisonModal();" title="${{t.compareRemoveRepo}}">✕</button>
                                    </div>
                                    <div style="display:flex; gap:6px; flex-wrap:wrap; font-size:0.8rem; margin-bottom:10px;">
                                        <span class="pill-tag">★ ${{r.stars_total ? Number(r.stars_total).toLocaleString() : '0'}}</span>
                                        ${{r.stars_since ? `<span class="pill-tag">+${{r.stars_since}} stars</span>` : ''}}
                                        <span class="pill-tag">${{escapeText(r.language || 'Unknown')}}</span>
                                    </div>
                                    <div style="display:flex; gap:6px; flex-wrap:wrap;">
                                        <a href="cursor://vscode.git/clone?url=${{escapeText(rawUrl)}}.git" class="btn-ide" title="Open in Cursor" style="padding:4px 8px; font-size:0.75rem;">${{t.cloneCursor}}</a>
                                        <a href="vscode://vscode.git/clone?url=${{escapeText(rawUrl)}}.git" class="btn-ide" title="Open in VS Code" style="padding:4px 8px; font-size:0.75rem;">${{t.cloneVsCode}}</a>
                                        <a href="https://github.dev/${{escapeText(r.name)}}" target="_blank" class="btn-ide" title="Open in GitHub.dev" style="padding:4px 8px; font-size:0.75rem;">${{t.openGithubDev}}</a>
                                    </div>
                                </div>

                                <div>
                                    <div class="comparison-section-title">${{t.corePurposeTitle}}</div>
                                    <div class="comparison-section-content" style="color:var(--text-bright); font-weight:500;">${{escapeText(displayCore)}}</div>
                                </div>

                                <div>
                                    <div class="comparison-section-title">${{t.modalTabs.comparisons || 'Độ hoàn thiện & Loại'}}</div>
                                    <div style="display:flex; gap:6px; flex-wrap:wrap;">
                                        <span class="pill-tag tag-category">🏷️ ${{escapeText(r.category || '')}}</span>
                                        ${{repoTypeDisplay ? `<span class="pill-tag tag-repo-type">${{escapeText(repoTypeDisplay)}}</span>` : ''}}
                                        ${{r.maturity_badge ? `<span class="pill-tag ${{matClass}}">${{escapeText(r.maturity_badge)}}</span>` : ''}}
                                        ${{r.velocity_badge ? `<span class="pill-tag ${{velClass}}">${{escapeText(r.velocity_badge)}}</span>` : ''}}
                                    </div>
                                </div>

                                ${{ (r.tech_stack && r.tech_stack.length) ? `
                                    <div>
                                        <div class="comparison-section-title">Tech Stack</div>
                                        <div style="display:flex; gap:4px; flex-wrap:wrap;">
                                            ${{r.tech_stack.map(st => `<span class="tech-pill">${{escapeText(st)}}</span>`).join('')}}
                                        </div>
                                    </div>
                                ` : ''}}

                                ${{ (displayMajor || displayRoles) ? `
                                    <div>
                                        <div class="comparison-section-title">${{t.suitableMajorTitle}} & ${{t.targetRolesTitle}}</div>
                                        <div class="comparison-section-content" style="font-size:0.8rem; color:var(--text-muted);">
                                            ${{displayMajor ? `📚 ${{escapeText(displayMajor)}}<br>` : ''}}
                                            ${{displayRoles ? `👤 ${{escapeText(displayRoles)}}` : ''}}
                                        </div>
                                    </div>
                                ` : ''}}

                                ${{ displayImpact ? `
                                    <div>
                                        <div class="comparison-section-title">${{t.realWorldImpactTitle}}</div>
                                        <div class="comparison-section-content" style="font-size:0.8rem; border-left:2px solid var(--accent-green); padding-left:6px;">${{escapeText(displayImpact)}}</div>
                                    </div>
                                ` : ''}}

                                ${{ r.commercial_alternative ? `
                                    <div>
                                        <div class="comparison-section-title">${{t.lblAltText}}</div>
                                        <span class="pill-tag tag-alternative">${{t.tagAlt(r.commercial_alternative)}}</span>
                                    </div>
                                ` : ''}}

                                ${{ r.latest_release && r.latest_release.tag_name ? `
                                    <div>
                                        <div class="comparison-section-title">${{t.latestReleaseTitle}}</div>
                                        <div class="comparison-section-content" style="font-size:0.8rem;">
                                            <span class="pill-tag tag-release">🏷️ ${{escapeText(r.latest_release.tag_name)}}</span>
                                            ${{r.latest_release.published_at ? `<div style="font-size:0.75rem; color:var(--text-muted); margin-top:3px;">📅 ${{formatReleaseDate(r.latest_release.published_at)}}</div>` : ''}}
                                        </div>
                                    </div>
                                ` : ''}}

                                ${{ r.community_pulse ? `
                                    <div>
                                        <div class="comparison-section-title">${{t.pulseTitle}}</div>
                                        <div class="comparison-section-content" style="font-size:0.8rem; display:flex; flex-direction:column; gap:4px;">
                                            <div>
                                                <span class="pill-tag tag-pulse ${{r.community_pulse.pulse_status || 'active'}}">
                                                    ${{currentLang === 'vi' ? (r.community_pulse.pulse_badge_vi || '') : (r.community_pulse.pulse_badge_en || '')}}
                                                </span>
                                                ${{r.community_pulse.license_spdx ? `<span class="pill-tag tag-license">📜 ${{escapeText(r.community_pulse.license_spdx)}}</span>` : ''}}
                                            </div>
                                            <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">
                                                ⚠️ ${{Number(r.community_pulse.open_issues_count || 0).toLocaleString()}} ${{t.pulseOpenIssues.toLowerCase()}} · 🍴 ${{Number(r.community_pulse.forks_count || 0).toLocaleString()}} forks
                                            </div>
                                        </div>
                                    </div>
                                ` : ''}}

                                ${{ r.quick_run ? `
                                    <div>
                                        <div class="comparison-section-title">${{t.quickRunTitle}}</div>
                                        <div class="quick-run-box" style="margin:0;">
                                            <span class="quick-run-code">${{escapeText(r.quick_run)}}</span>
                                        </div>
                                    </div>
                                ` : ''}}
                            </div>
                        `;
                    }}).join('')}}
                </div>

                <!-- Multi-Repo Star History Comparison Chart -->
                <div class="star-history-wrapper">
                    <div style="font-size:0.92rem; font-weight:700; color:#d2a8ff; margin-bottom:10px;">
                        📈 ${{t.starHistoryComparisonTitle || 'So sánh Biểu đồ Lịch sử Tăng trưởng Stars (Star History)'}}
                    </div>
                    <img src="${{starHistoryUrl}}" alt="Star History Comparison" class="star-history-img" loading="lazy" onerror="this.style.display='none'">
                    <div class="star-history-actions">
                        <a href="${{starHistoryWeb}}" target="_blank" rel="noopener noreferrer" class="btn-star-history-link">
                            <span>🌐</span> <span>${{t.openStarHistoryWeb || 'Xem biểu đồ tương tác trên Star-History.com'}}</span>
                        </a>
                    </div>
                </div>
            `;

            body.innerHTML = html;
            modal.style.display = 'flex';
            setTimeout(() => {{ modal.classList.add('open'); }}, 10);
        }}

        function closeComparisonModal() {{
            const modal = document.getElementById('comparisonModal');
            if (modal) {{
                modal.classList.remove('open');
                setTimeout(() => {{ modal.style.display = 'none'; }}, 200);
            }}
        }}

        function openDeepDiveModal(raw, idx) {{
            const modal = document.getElementById('deepDiveModal');
            if (!modal) return;
            const t = I18N[currentLang];
            const titleLink = document.getElementById('modalTitle');
            titleLink.textContent = raw.name;
            titleLink.href = raw.url;

            // Badges
            const badgesContainer = document.getElementById('modalBadges');
            badgesContainer.innerHTML = '';
            const badges = [
                `💻 ${{raw.language || 'Unknown'}}`,
                raw.timeframe === 'search' ? `★ ${{raw.stars_total}}` : `★ +${{raw.stars_since || '0'}}`,
                `🛡️ Grounding: ${{raw.grounding_score || 85}}/100`,
                `⚙️ Engine: ${{raw.engine_used || 'heuristic'}}`
            ];
            if (raw.velocity_badge) badges.push(raw.velocity_badge);
            if (raw.hn_points) badges.push(`📰 HN: ▲ ${{raw.hn_points}} pts`);
            if (raw.latest_release && raw.latest_release.tag_name) badges.push(`🏷️ Release: ${{raw.latest_release.tag_name}}`);
            if (raw.community_pulse && raw.community_pulse.pulse_status) badges.push(currentLang === 'vi' ? raw.community_pulse.pulse_badge_vi : raw.community_pulse.pulse_badge_en);
            if (raw.community_pulse && raw.community_pulse.license_spdx) badges.push(`📜 ${{raw.community_pulse.license_spdx}}`);
            badges.forEach(b => {{
                const span = document.createElement('span');
                span.className = 'pill-tag';
                span.textContent = b;
                badgesContainer.appendChild(span);
            }});

            // Tabs definition
            const tabDefs = [
                {{ id: 'playground', label: t.modalTabs.playground, playground: raw.playground }},
                {{ id: 'architecture', label: t.modalTabs.architecture, mermaid: raw.architecture_mermaid }},
                {{ id: 'release_radar', label: t.modalTabs.release_radar, release: raw.latest_release }},
                {{ id: 'community_pulse', label: t.modalTabs.community_pulse, pulse: raw.community_pulse }},
                {{ id: 'how_it_works', label: t.modalTabs.how_it_works, items: raw.how_it_works || [] }},
                {{ id: 'comparisons', label: t.modalTabs.comparisons, items: raw.comparisons || [] }},
                {{ id: 'practical_examples', label: t.modalTabs.practical_examples, items: raw.practical_examples || [], quickRun: raw.quick_run }},
                {{ id: 'limitations', label: t.modalTabs.limitations, items: raw.limitations || [] }},
                {{ id: 'adoption_notes', label: t.modalTabs.adoption_notes, items: raw.adoption_notes || [] }},
                {{ id: 'sources', label: t.modalTabs.sources, sources: raw.data_sources || [], evidence: raw.evidence || [] }},
                {{ id: 'star_history', label: t.modalTabs.star_history }}
            ];

            const tabsBar = document.getElementById('modalTabsBar');
            const modalBody = document.getElementById('modalBody');
            tabsBar.innerHTML = '';
            modalBody.innerHTML = '';

            let firstActive = 'playground';
            for (const td of tabDefs) {{
                if (td.id === 'playground') {{
                    firstActive = td.id;
                    break;
                }}
                if (td.id === 'architecture' && td.mermaid) {{
                    firstActive = td.id;
                    break;
                }}
                if ((td.items && td.items.length) || (td.sources && td.sources.length) || td.quickRun) {{
                    firstActive = td.id;
                    break;
                }}
            }}

            tabDefs.forEach(td => {{
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `modal-tab-btn ${{td.id === firstActive ? 'active' : ''}}`;
                const count = td.items ? td.items.length : (td.sources ? td.sources.length : 0);
                btn.textContent = `${{td.label}}${{count > 0 ? ` (${{count}})` : ''}}`;
                btn.addEventListener('click', () => {{
                    modal.querySelectorAll('.modal-tab-btn').forEach(b => b.classList.remove('active'));
                    modal.querySelectorAll('.modal-tab-pane').forEach(p => p.classList.remove('active'));
                    btn.classList.add('active');
                    const pane = document.getElementById(`pane_${{td.id}}`);
                    if (pane) pane.classList.add('active');
                }});
                tabsBar.appendChild(btn);

                // Create Pane
                const pane = document.createElement('div');
                pane.id = `pane_${{td.id}}`;
                pane.className = `modal-tab-pane ${{td.id === firstActive ? 'active' : ''}}`;

                if (td.id === 'playground') {{
                    const manifest = td.playground || raw.playground || generateClientPlayground(raw);
                    pane.appendChild(buildPlaygroundDOM(manifest, raw));
                }} else if (td.id === 'community_pulse') {{
                    const pulseWrap = document.createElement('div');
                    pulseWrap.className = 'pulse-wrapper';
                    const pulse = td.pulse;

                    if (pulse && (pulse.last_pushed_at || pulse.license_name || pulse.open_issues_count !== undefined)) {{
                        const pushTimeStr = pulse.last_pushed_at ? formatReleaseDate(pulse.last_pushed_at) : (currentLang === 'vi' ? 'Chưa xác định' : 'Unknown');
                        const statusBadge = currentLang === 'vi' ? (pulse.pulse_badge_vi || '🟢 Rất tích cực') : (pulse.pulse_badge_en || '🟢 Highly Active');
                        const statusKey = pulse.pulse_status || 'active';

                        let verdictText = t.pulseVerdictActive;
                        if (statusKey === 'steady') verdictText = t.pulseVerdictSteady;
                        else if (statusKey === 'slow') verdictText = t.pulseVerdictSlow;
                        else if (statusKey === 'dormant') verdictText = t.pulseVerdictDormant;

                        const contribs = pulse.top_contributors || [];

                        pulseWrap.innerHTML = `
                            <div class="pulse-grid">
                                <div class="pulse-stat-card">
                                    <div class="pulse-stat-header">
                                        <span>⚡</span> <span>${{t.pulseLatestPush}}</span>
                                    </div>
                                    <div class="pulse-stat-val">
                                        <span class="pill-tag tag-pulse ${{statusKey}}" style="font-size:0.82rem;">${{statusBadge}}</span>
                                    </div>
                                    <div class="pulse-stat-sub">📅 ${{pushTimeStr}}</div>
                                </div>

                                <div class="pulse-stat-card">
                                    <div class="pulse-stat-header">
                                        <span>⚠️</span> <span>${{t.pulseOpenIssues}}</span>
                                    </div>
                                    <div class="pulse-stat-val" style="color:var(--accent-yellow);">
                                        ${{Number(pulse.open_issues_count || 0).toLocaleString()}}
                                    </div>
                                    <div class="pulse-stat-sub">
                                        <a href="https://github.com/${{escapeText(raw.name)}}/issues" target="_blank" rel="noopener noreferrer" style="color:var(--accent-blue); text-decoration:none;">
                                            Xem Issues trên GitHub ↗
                                        </a>
                                    </div>
                                </div>

                                <div class="pulse-stat-card">
                                    <div class="pulse-stat-header">
                                        <span>📜</span> <span>${{t.pulseLicense}}</span>
                                    </div>
                                    <div class="pulse-stat-val" style="font-size:0.95rem; color:#bc8cff;">
                                        ${{escapeText(pulse.license_name || 'Chưa định rõ (No license)')}}
                                    </div>
                                    <div class="pulse-stat-sub">Branch: <code>${{escapeText(pulse.default_branch || 'main')}}</code></div>
                                </div>

                                <div class="pulse-stat-card">
                                    <div class="pulse-stat-header">
                                        <span>👥</span> <span>${{t.pulseWatchersForks}}</span>
                                    </div>
                                    <div class="pulse-stat-val" style="color:var(--accent-blue);">
                                        👁️ ${{Number(pulse.watchers_count || 0).toLocaleString()}} · 🍴 ${{Number(pulse.forks_count || 0).toLocaleString()}}
                                    </div>
                                    <div class="pulse-stat-sub">Mạng lưới theo dõi & forks</div>
                                </div>
                            </div>

                            ${{contribs.length > 0 ? `
                                <div class="contributors-box">
                                    <div class="contributors-title">
                                        <span>👥</span> <span>${{t.pulseTopContribTitle}}</span>
                                    </div>
                                    <div class="contributors-list">
                                        ${{contribs.map(c => `
                                            <a href="${{escapeText(c.html_url)}}" target="_blank" rel="noopener noreferrer" class="contributor-item">
                                                ${{c.avatar_url ? `<img src="${{escapeText(c.avatar_url)}}" alt="${{escapeText(c.login)}}" class="contributor-avatar" loading="lazy">` : '<div class="contributor-avatar" style="background:#30363d;"></div>'}}
                                                <div class="contributor-info">
                                                    <span class="contributor-login">@${{escapeText(c.login)}}</span>
                                                    <span class="contributor-commits">${{t.pulseCommitsCount(Number(c.contributions || 0).toLocaleString())}}</span>
                                                </div>
                                            </a>
                                        `).join('')}}
                                    </div>
                                </div>
                            ` : ''}}

                            <div class="pulse-verdict-box">
                                <div class="pulse-verdict-title">
                                    <span>🛡️</span> <span>${{t.pulseHealthVerdictTitle}}</span>
                                </div>
                                <div class="pulse-verdict-desc">${{verdictText}}</div>
                            </div>
                        `;
                    }} else {{
                        pulseWrap.innerHTML = `
                            <div style="background:#161b22; border:1px solid var(--border); border-radius:10px; padding:30px 20px; text-align:center;">
                                <div style="font-size:2rem; margin-bottom:10px;">👥</div>
                                <div style="font-size:0.95rem; font-weight:600; color:var(--text-bright); margin-bottom:6px;">
                                    ${{t.pulseNoData}}
                                </div>
                                <div style="font-size:0.82rem; color:var(--text-muted); margin-bottom:16px;">
                                    ${{t.pulseTitle}}
                                </div>
                                <a href="https://github.com/${{escapeText(raw.name)}}/pulse" target="_blank" rel="noopener noreferrer" class="btn-release-github">
                                    <span>📊</span> <span>Mở trang GitHub Pulse trực tiếp ↗</span>
                                </a>
                            </div>
                        `;
                    }}
                    pane.appendChild(pulseWrap);
                }} else if (td.id === 'release_radar') {{
                    const relWrap = document.createElement('div');
                    relWrap.className = 'release-radar-wrapper';
                    const rel = td.release;
                    if (rel && rel.tag_name) {{
                        const pubDateStr = rel.published_at ? formatReleaseDate(rel.published_at) : '';
                        const relUrl = rel.html_url || `https://github.com/${{escapeText(raw.name)}}/releases`;
                        const highlights = rel.highlights || [];
                        const bodySnippet = rel.body_snippet || '';

                        relWrap.innerHTML = `
                            <div class="release-hero-card">
                                <div class="release-hero-info">
                                    <div class="release-tag-title">
                                        <span>🏷️</span>
                                        <span>${{escapeText(rel.tag_name)}}</span>
                                        ${{rel.prerelease ? `<span class="pill-tag" style="background:rgba(210,153,34,0.15); color:var(--accent-yellow); border-color:rgba(210,153,34,0.4); font-size:0.75rem;">${{t.releasePrereleaseBadge}}</span>` : ''}}
                                        ${{rel.is_tag_only ? `<span class="pill-tag" style="background:rgba(139,148,158,0.15); color:var(--text-muted); font-size:0.75rem;">Git Tag</span>` : ''}}
                                    </div>
                                    <div class="release-meta">
                                        ${{rel.name && rel.name !== rel.tag_name ? `<span><strong>${{escapeText(rel.name)}}</strong></span>` : ''}}
                                        ${{pubDateStr ? `<span>📅 ${{t.releasePublished}} ${{pubDateStr}}</span>` : ''}}
                                    </div>
                                </div>
                                <div>
                                    <a href="${{escapeText(relUrl)}}" target="_blank" rel="noopener noreferrer" class="btn-release-github">
                                        <span>📦</span> <span>${{t.releaseViewOnGitHub}}</span> <span>↗</span>
                                    </a>
                                </div>
                            </div>

                            ${{highlights.length > 0 ? `
                                <div class="release-highlights-box">
                                    <div class="release-highlights-title">
                                        <span>${{t.releaseHighlightsTitle}}</span>
                                    </div>
                                    <ul class="release-highlights-list">
                                        ${{highlights.map(h => `
                                            <li class="release-highlight-item">
                                                <span class="release-highlight-bullet">▹</span>
                                                <span>${{escapeText(h)}}</span>
                                            </li>
                                        `).join('')}}
                                    </ul>
                                </div>
                            ` : ''}}

                            ${{bodySnippet ? `
                                <div>
                                    <div style="font-size:0.85rem; font-weight:700; color:var(--text-muted); margin-bottom:8px;">
                                        ${{t.releaseFullNotesTitle}}
                                    </div>
                                    <div class="release-body-box">${{escapeText(bodySnippet)}}</div>
                                </div>
                            ` : ''}}
                        `;
                    }} else {{
                        relWrap.innerHTML = `
                            <div style="background:#161b22; border:1px solid var(--border); border-radius:10px; padding:30px 20px; text-align:center;">
                                <div style="font-size:2rem; margin-bottom:10px;">📦</div>
                                <div style="font-size:0.95rem; font-weight:600; color:var(--text-bright); margin-bottom:6px;">
                                    ${{t.releaseNoRelease}}
                                </div>
                                <div style="font-size:0.82rem; color:var(--text-muted); margin-bottom:16px;">
                                    ${{t.releaseRadarTitle}}
                                </div>
                                <a href="https://github.com/${{escapeText(raw.name)}}/commits" target="_blank" rel="noopener noreferrer" class="btn-release-github">
                                    <span>📜</span> <span>Xem lịch sử commits trên GitHub</span> <span>↗</span>
                                </a>
                            </div>
                        `;
                    }}
                    pane.appendChild(relWrap);
                }} else if (td.id === 'architecture') {{
                    const archWrap = document.createElement('div');
                    archWrap.className = 'arch-wrapper';
                    const mermaidCode = td.mermaid || '';
                    let liveEditorUrl = 'https://mermaid.live';
                    try {{
                        const payload = JSON.stringify({{ code: mermaidCode, mermaid: {{ theme: 'dark' }} }});
                        const b64 = btoa(unescape(encodeURIComponent(payload)));
                        liveEditorUrl = `https://mermaid.live/edit#base64:${{b64}}`;
                    }} catch (e) {{}}

                    const stageInputDesc = `${{escapeText(raw.language || 'Code / Arguments')}} · ${{escapeText((raw.topics || []).slice(0, 3).join(', ') || 'Payload')}}`;
                    const stageProcDesc = `${{escapeText(raw.name)}} (${{escapeText(raw.repo_type_badge || 'Core Engine')}})`;
                    const stageStoreDesc = `${{escapeText((raw.tech_stack || []).slice(0, 4).join(', ') || 'Runtime Drivers & Services')}}`;
                    const stageOutDesc = `${{escapeText(raw.core_purpose || raw.description || 'Target State / Output')}}`;

                    archWrap.innerHTML = `
                        <div class="arch-header">
                            <div>
                                <div class="arch-title">${{t.archTitle}}</div>
                                <div class="arch-subtitle">${{t.archSubtitle}}</div>
                            </div>
                            <div class="arch-actions">
                                <button type="button" class="btn-arch-action" id="btnCopyArch_${{idx}}" onclick="copyMermaidCode(this)">
                                    <span>📋</span> <span>${{t.archCopyBtn}}</span>
                                </button>
                                <a href="${{liveEditorUrl}}" target="_blank" rel="noopener noreferrer" class="btn-arch-action">
                                    <span>↗️</span> <span>${{t.archLiveEditor}}</span>
                                </a>
                            </div>
                        </div>
                        <div class="arch-canvas" id="archCanvas_${{idx}}">
                            <div class="arch-loading">⏳ Đang dựng sơ đồ kiến trúc...</div>
                        </div>
                        <div class="arch-fallback" id="archFallback_${{idx}}" style="display:none;">
                            <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:8px;">
                                ${{t.archOfflineFallback}}
                            </div>
                            <pre class="evidence-code-block"><code>${{escapeText(mermaidCode)}}</code></pre>
                        </div>
                        <div class="arch-stages">
                            <div class="arch-stages-title">${{t.archPipelineStages}}</div>
                            <div class="arch-stages-grid">
                                <div class="arch-stage-card">
                                    <div class="arch-stage-header">${{t.archStageInput}}</div>
                                    <div class="arch-stage-desc">${{stageInputDesc}}</div>
                                </div>
                                <div class="arch-stage-card">
                                    <div class="arch-stage-header">${{t.archStageProcess}}</div>
                                    <div class="arch-stage-desc">${{stageProcDesc}}</div>
                                </div>
                                <div class="arch-stage-card">
                                    <div class="arch-stage-header">${{t.archStageStorage}}</div>
                                    <div class="arch-stage-desc">${{stageStoreDesc}}</div>
                                </div>
                                <div class="arch-stage-card">
                                    <div class="arch-stage-header">${{t.archStageOutput}}</div>
                                    <div class="arch-stage-desc">${{stageOutDesc}}</div>
                                </div>
                            </div>
                        </div>
                    `;
                    pane.appendChild(archWrap);

                    const copyBtn = archWrap.querySelector(`#btnCopyArch_${{idx}}`);
                    if (copyBtn) copyBtn._mermaidCode = mermaidCode;

                    setTimeout(() => {{
                        renderMermaidSafe(`archCanvas_${{idx}}`, `archFallback_${{idx}}`, mermaidCode);
                    }}, 60);
                }} else if (td.id === 'star_history') {{
                    const wrap = document.createElement('div');
                    wrap.className = 'star-history-wrapper';
                    const shUrl = `https://api.star-history.com/svg?repos=${{escapeText(raw.name)}}&type=Date`;
                    const shWeb = `https://star-history.com/#${{escapeText(raw.name)}}&Date`;
                    wrap.innerHTML = `
                        <div style="font-size:0.92rem; font-weight:700; color:var(--text-bright); margin-bottom:12px;">
                            📈 ${{t.starHistoryTitle}} (${{escapeText(raw.name)}})
                        </div>
                        <img src="${{shUrl}}" alt="${{escapeText(raw.name)}} Star History" class="star-history-img" loading="lazy" onerror="this.nextElementSibling.style.display='block'; this.style.display='none';">
                        <div style="display:none; color:var(--text-muted); font-size:0.85rem; padding:12px;">
                            ${{t.starHistoryOfflineMsg}}
                        </div>
                        <div class="star-history-actions">
                            <a href="${{shWeb}}" target="_blank" rel="noopener noreferrer" class="btn-star-history-link">
                                <span>🌐</span> <span>${{t.openStarHistoryWeb}}</span>
                            </a>
                            <a href="https://github.com/${{escapeText(raw.name)}}/pulse" target="_blank" rel="noopener noreferrer" class="btn-star-history-link">
                                <span>📊</span> <span>GitHub Pulse / Insights</span>
                            </a>
                        </div>
                    `;
                    pane.appendChild(wrap);
                }} else if (td.id === 'sources') {{
                    if (td.sources && td.sources.length) {{
                        const h = document.createElement('div');
                        h.className = 'evidence-title';
                        h.textContent = t.modalSourcesTitle;
                        pane.appendChild(h);
                        td.sources.forEach(src => {{
                            const sc = document.createElement('div');
                            sc.className = 'evidence-card';
                            sc.innerHTML = `<strong>[${{src.id}}]</strong> <a href="${{src.url}}" target="_blank" style="color:var(--accent-blue); text-decoration:none;">${{escapeText(src.title)}}</a> · <span style="color:var(--text-muted); font-size:0.8rem;">${{src.fetched_at}} (${{src.freshness}})</span>`;
                            pane.appendChild(sc);
                        }});
                    }} else {{
                        pane.innerHTML = `<div style="color:var(--text-muted); padding:20px; text-align:center;">${{t.modalNoEvidence}}</div>`;
                    }}
                }} else {{
                    let hasContent = false;
                    if (td.quickRun) {{
                        hasContent = true;
                        const qrBox = document.createElement('div');
                        qrBox.className = 'evidence-card';
                        qrBox.innerHTML = `<div class="evidence-title">⚡ Quick Run / Installation:</div><pre class="evidence-code-block"><code>${{escapeText(td.quickRun)}}</code></pre>`;
                        pane.appendChild(qrBox);
                    }}
                    if (td.items && td.items.length) {{
                        hasContent = true;
                        td.items.forEach(item => {{
                            const card = document.createElement('div');
                            card.className = 'evidence-card';
                            const formatted = escapeText(item).replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, '<pre class="evidence-code-block"><code>$2</code></pre>');
                            card.innerHTML = `<div class="evidence-content">${{formatted}}</div>`;
                            pane.appendChild(card);
                        }});
                    }}
                    if (!hasContent) {{
                        pane.innerHTML = `<div style="color:var(--text-muted); padding:20px; text-align:center;">${{t.modalNoEvidence}}</div>`;
                    }}
                }}
                modalBody.appendChild(pane);
            }});

            modal.style.display = 'flex';
            setTimeout(() => {{ modal.classList.add('open'); }}, 10);
        }}

        // Close on backdrop click and Esc key
        document.addEventListener('DOMContentLoaded', () => {{
            const modal = document.getElementById('deepDiveModal');
            const closeBtn = document.getElementById('modalCloseBtn');
            if (closeBtn) closeBtn.addEventListener('click', closeDeepDiveModal);
            if (modal) {{
                modal.addEventListener('click', (e) => {{
                    if (e.target === modal) closeDeepDiveModal();
                }});
            }}
            document.addEventListener('keydown', (e) => {{
                if (e.key === 'Escape') {{
                    closeDeepDiveModal();
                    closeComparisonModal();
                    closeSimilarModal();
                }}
            }});
        }});


        // Export Bookmarks Logic
        function openExportModal() {{
            const modal = document.getElementById('exportModal');
            const textarea = document.getElementById('exportTextarea');
            if (!modal || !textarea) return;
            const t = I18N[currentLang];

            const list = Object.values(bookmarksMap).filter(b => b && b.full_name);
            if (!list.length) {{
                textarea.value = (currentLang === 'vi') ? "Chưa có repository nào trong danh sách đã lưu." : "No saved repositories.";
            }} else {{
                let md = `# 🔖 GitHub Trending Saved Repositories (${{list.length}})\n\n`;
                md += `*Exported on ${{new Date().toLocaleDateString(currentLang === 'vi' ? 'vi-VN' : 'en-US')}}*\n\n---\n\n`;
                list.forEach((b, i) => {{
                    const r = b.repo_data || {{}};
                    const url = r.url || `https://github.com/${{b.full_name}}`;
                    const stars = r.stars_total ? ` (★ ${{r.stars_total.toLocaleString()}})` : '';
                    md += `### ${{i + 1}}. [${{b.full_name}}](${{url}})${{stars}}\n`;
                    if (b.tags && b.tags.length) {{
                        md += `- **Tags:** ${{b.tags.map(tag => `\`${{tag}}\``).join(', ')}}\n`;
                    }}
                    if (b.notes) {{
                        md += `- **Notes:** ${{b.notes}}\n`;
                    }}
                    if (r.category) {{
                        md += `- **Category:** ${{r.category}}\n`;
                    }}
                    if (r.core_purpose) {{
                        md += `- **Core Purpose:** ${{r.core_purpose}}\n`;
                    }}
                    if (r.tech_stack && r.tech_stack.length) {{
                        md += `- **Tech Stack:** ${{r.tech_stack.join(', ')}}\n`;
                    }}
                    md += `\n`;
                }});
                textarea.value = md;
            }}
            modal.style.display = 'flex';
        }}

        function closeExportModal() {{
            const modal = document.getElementById('exportModal');
            if (modal) modal.style.display = 'none';
        }}

        function copyExportMarkdown() {{
            const textarea = document.getElementById('exportTextarea');
            const btn = document.getElementById('exportCopyBtn');
            const t = I18N[currentLang];
            if (!textarea) return;
            navigator.clipboard.writeText(textarea.value).then(() => {{
                const old = btn.textContent;
                btn.textContent = t.exportCopied;
                setTimeout(() => {{ btn.textContent = old; }}, 2000);
            }}).catch(() => {{
                textarea.select();
                document.execCommand('copy');
                alert(t.exportCopied);
            }});
        }}

        // Final Startup Initialization (after all variables & functions are declared)
        setLanguage(currentLang);
        updateAdvancedBadge();
        updateBookmarkBadge();
        loadServerBookmarks();
        if (searchEndpoint && (!reposData || reposData.length === 0)) {{
            searchProjects();
        }}
    </script>
        <!-- Deep Dive Modal -->
        <div id="deepDiveModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
            <div class="modal-dialog">
                <div class="modal-header">
                    <div class="modal-header-title">
                        <span id="modalIcon">🔬</span>
                        <a id="modalTitle" href="#" target="_blank">repo/name</a>
                    </div>
                    <button type="button" class="modal-close-btn" id="modalCloseBtn" aria-label="Close">✕</button>
                </div>
                <div id="modalBadges" class="modal-badges"></div>
                <div class="modal-tabs" id="modalTabsBar"></div>
                <div class="modal-body" id="modalBody"></div>
            </div>
        </div>
        <!-- Floating Compare Dock -->
        <div id="compareDock" class="compare-dock" style="display:none;">
            <div class="compare-dock-inner">
                <div class="compare-dock-info">
                    <span class="compare-dock-title" id="lblCompareDockTitle">⚖️ So sánh Repository:</span>
                    <div id="compareChips" class="compare-chips"></div>
                </div>
                <div class="compare-dock-actions">
                    <button type="button" id="btnLaunchCompare" class="btn-launch-compare" onclick="openComparisonModal()">
                        <span>⚖️</span> <span id="lblBtnLaunchCompare">So sánh đối chiếu (0)</span>
                    </button>
                    <button type="button" class="btn-clear-compare" onclick="clearComparison()" title="Bỏ chọn tất cả">✕</button>
                </div>
            </div>
        </div>

        <!-- Side-by-Side Comparison Modal -->
        <div id="comparisonModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="cmpModalTitle" style="display:none;" onclick="if(event.target===this)closeComparisonModal()">
            <div class="comparison-modal-dialog">
                <div class="modal-header">
                    <div class="modal-header-title">
                        <span>⚖️</span>
                        <span id="cmpModalTitle">Bảng Ma Trận So Sánh Đối Chiếu Repository</span>
                    </div>
                    <button type="button" class="modal-close-btn" onclick="closeComparisonModal()" aria-label="Close">✕</button>
                </div>
                <div class="comparison-modal-body" id="comparisonModalBody"></div>
            </div>
        </div>
        <!-- Similar Repositories Modal -->
        <div id="similarModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="similarModalTitle" style="display:none;" onclick="if(event.target===this)closeSimilarModal()">
            <div class="similar-modal-dialog">
                <div class="modal-header">
                    <div class="modal-header-title">
                        <span>🔎</span>
                        <span id="similarModalTitle">Dự án tương tự</span>
                    </div>
                    <button type="button" class="modal-close-btn" onclick="closeSimilarModal()" aria-label="Close">✕</button>
                </div>
                <div class="similar-modal-body">
                    <div class="similar-subtitle" id="similarModalSubtitle">
                        Gợi ý các repository mã nguồn mở tương đương dựa trên chủ đề, tech stack và mục đích sử dụng:
                    </div>
                    <div id="similarLoadingState" class="similar-loading" style="display:none;">
                        <span class="loading-spinner">⏳</span> <span id="lblSimilarLoading">Đang tìm kiếm các repository tương đương trên GitHub...</span>
                    </div>
                    <div id="similarErrorState" class="similar-error" style="display:none; color:var(--accent-red); margin-bottom:12px;"></div>
                    <div id="similarCardsGrid" class="similar-grid"></div>
                </div>
                <div class="similar-modal-footer">
                    <button type="button" id="btnSimilarOpenCompare" class="btn-launch-compare" style="display:none;" onclick="closeSimilarModal(); openComparisonModal();">
                        <span>⚖️</span> <span id="lblSimilarOpenCompare">So sánh đối chiếu</span>
                    </button>
                    <button type="button" class="btn-copy" style="background:#21262d; border-color:var(--border); color:var(--text-main);" onclick="closeSimilarModal()">Đóng</button>
                </div>
            </div>
        </div>
        <!-- 1-Click Run & Docker Playground Modal -->
        <div id="playgroundModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="playgroundModalTitle" style="display:none;" onclick="if(event.target===this)closePlaygroundModal()">
            <div class="playground-modal-dialog">
                <div class="modal-header">
                    <div class="modal-header-title">
                        <span>⚡</span>
                        <span id="playgroundModalTitle">1-Click Run & Docker Playground</span>
                    </div>
                    <button type="button" class="modal-close-btn" onclick="closePlaygroundModal()" aria-label="Close">✕</button>
                </div>
                <div class="playground-modal-body" id="playgroundModalBody"></div>
            </div>
        </div>
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

