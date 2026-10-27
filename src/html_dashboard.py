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
                <div class="search-field" {'hidden' if not search_endpoint else ''}>
                    <label id="lblDataSource" for="dataSource">Nguồn xu hướng</label>
                    <select id="dataSource" onchange="updateSearchMode()">
                        <option id="optSourceGitHub" value="github">🔥 GitHub Trending</option>
                        <option id="optSourceHN" value="hn">📰 Hacker News Trends</option>
                    </select>
                </div>
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
                    <option value="bookmarked">⭐ Đã lưu (Bookmark)</option>
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
                    how_it_works: "🏛️ Kiến trúc & Cơ chế",
                    comparisons: "📊 Benchmarks & So sánh",
                    practical_examples: "💻 Code & Lệnh chạy",
                    limitations: "⚠️ Giới hạn & Cảnh báo",
                    adoption_notes: "🚀 Triển khai & Cài đặt",
                    sources: "📚 Nguồn tài liệu"
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
                    how_it_works: "🏛️ Architecture & Internals",
                    comparisons: "📊 Benchmarks & Comparisons",
                    practical_examples: "💻 Code & Examples",
                    limitations: "⚠️ Limitations & Warnings",
                    adoption_notes: "🚀 Adoption & Setup",
                    sources: "📚 Document Sources"
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
                        </div>

                        <!-- Feedback Toolbar -->
                        <div class="feedback-bar">
                            <div class="rating-buttons">
                                <button type="button" class="btn-rate btn-like ${{raw.user_rating === 1 ? 'active' : ''}}" title="Useful" data-action="like">👍</button>
                                <button type="button" class="btn-rate btn-dislike ${{raw.user_rating === -1 ? 'active' : ''}}" title="Not useful" data-action="dislike">👎</button>
                                <button type="button" class="btn-rate btn-bookmark ${{isBookmarked ? 'active' : ''}}" title="${{isBookmarked ? t.btnBookmarked : t.btnBookmark}}" data-repo="${{r.name}}">🔖 <span class="bm-label">${{isBookmarked ? t.btnBookmarked : t.btnBookmark}}</span></button>
                                <button type="button" class="btn-chat" title="${{t.chatBtnText}}">${{t.chatBtnText}}</button>
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

                const matchesPreset = matchesDomainPreset(r, activeDomainPreset);

                return matchesCat && matchesRepoType && matchesMaturity && matchesVelocity && matchesWatchlist && matchesAlt && matchesStatus && matchesQuery && matchesPreset;
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
                document.getElementById('sourceBadge').textContent = data.source === 'hn' ? `📰 Hacker News · ${{t.timeLabels[data.timeframe] || data.timeframe}}` : resultMode === 'trending' ? `📈 Trending · ${{t.timeLabels[data.timeframe] || data.timeframe}}` : `🔎 GitHub Search · ${{data.scope === 'content' ? (currentLang === 'vi' ? 'Nội dung README' : 'README Content') : (currentLang === 'vi' ? 'Tên project' : 'Project Name')}}`;
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
        updateBookmarkBadge();
        loadServerBookmarks();
        if (searchEndpoint && (!reposData || reposData.length === 0)) {{
            searchProjects();
        }}

        // Domain Presets & Analytics Logic
        let activeDomainPreset = 'all';
        let isAnalyticsOpen = false;

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
            badges.forEach(b => {{
                const span = document.createElement('span');
                span.className = 'pill-tag';
                span.textContent = b;
                badgesContainer.appendChild(span);
            }});

            // Tabs definition
            const tabDefs = [
                {{ id: 'how_it_works', label: t.modalTabs.how_it_works, items: raw.how_it_works || [] }},
                {{ id: 'comparisons', label: t.modalTabs.comparisons, items: raw.comparisons || [] }},
                {{ id: 'practical_examples', label: t.modalTabs.practical_examples, items: raw.practical_examples || [], quickRun: raw.quick_run }},
                {{ id: 'limitations', label: t.modalTabs.limitations, items: raw.limitations || [] }},
                {{ id: 'adoption_notes', label: t.modalTabs.adoption_notes, items: raw.adoption_notes || [] }},
                {{ id: 'sources', label: t.modalTabs.sources, sources: raw.data_sources || [], evidence: raw.evidence || [] }}
            ];

            const tabsBar = document.getElementById('modalTabsBar');
            const modalBody = document.getElementById('modalBody');
            tabsBar.innerHTML = '';
            modalBody.innerHTML = '';

            let firstActive = 'how_it_works';
            for (const td of tabDefs) {{
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

                if (td.id === 'sources') {{
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
                if (e.key === 'Escape') closeDeepDiveModal();
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

