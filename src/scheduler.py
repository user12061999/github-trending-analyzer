"""Scheduler & Background Automation Engine for GitHub Trending Analyzer.

Supports recurring daily/weekly trending analysis, automatic report generation,
highlight detection (Breakout, New Entries, Watchlist matches), webhook notifications,
and exporting OS-level scheduled tasks (Windows Task Scheduler / Linux Cron).
"""

from datetime import datetime
import json
import os
import sys
import time
import urllib.request
from typing import Any, Callable, Dict, List, Optional

from src.analyzer import analyze_batch
from src.formatter import generate_markdown_report
from src.html_dashboard import generate_html_dashboard
from src.scraper import get_trending_repos
from src.watchlist import load_watchlist


def send_webhook_notification(webhook_url: str, summary: Dict[str, Any]) -> bool:
    """Send job summary to a Discord, Slack, or generic webhook endpoint."""
    if not webhook_url:
        return False

    date_str = summary.get("date", "")
    total = summary.get("total_analyzed", 0)
    breakouts = summary.get("breakouts", [])
    new_entries = summary.get("new_entries", [])
    matches = summary.get("matches", [])
    alts = summary.get("commercial_alternatives", [])

    lines = [
        f"🔥 **Báo cáo GitHub Trending ({date_str})**",
        f"Đã phân tích **{total} repository**.",
    ]
    if breakouts:
        lines.append(f"🚀 **Dự án bứt phá (Breakout):** {', '.join(breakouts[:4])}")
    if alts:
        lines.append(f"💡 **Mã nguồn mở thay thế:** {', '.join(alts[:3])}")
    if matches:
        lines.append(f"⭐ **Khớp sở thích Watchlist:** {', '.join(matches[:4])}")
    if new_entries:
        lines.append(f"🌱 **Mới xuất hiện:** {', '.join(new_entries[:4])}")

    report_file = summary.get("report_md", "")
    if report_file:
        lines.append(f"📄 Báo cáo chi tiết đã lưu tại: `{report_file}`")

    text_content = "\n".join(lines)

    # Compatible with Slack and Discord incoming webhooks
    payload = {
        "text": text_content,
        "content": text_content,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "GitHubTrendingAnalyzer/1.0"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status in (200, 204)
    except Exception as exc:
        print(f"⚠️ Không thể gửi webhook ({type(exc).__name__}): {exc}", file=sys.stderr)
        return False


def run_scheduled_job(
    timeframe: str = "daily",
    language: Optional[str] = None,
    limit: int = 15,
    use_ai: bool = False,
    model: Optional[str] = None,
    deep: bool = False,
    output_dir: str = "reports",
    webhook_url: Optional[str] = None,
    watchlist_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute a complete automated analysis run and generate persistent reports."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")

    # 1. Scrape Trending
    repos = get_trending_repos(language=language, since=timeframe, limit=limit)
    if not repos:
        return {
            "date": date_str,
            "status": "empty",
            "total_analyzed": 0,
            "message": "Không có repository trending nào.",
        }

    # 2. Load Watchlist
    wl = load_watchlist(watchlist_path) if watchlist_path or os.path.exists("watchlist.json") else None

    # 3. Analyze Batch
    analyses = analyze_batch(
        repos=repos,
        use_ai=use_ai,
        fetch_readme=True,
        watchlist=wl,
        deep=deep,
        model=model,
    )

    # 4. Detect Highlights
    breakouts = [a.name for a in analyses if "Breakout" in (a.velocity_badge or "")]
    new_entries = [a.name for a in analyses if getattr(a, "is_new_entry", False)]
    matches = [f"{a.name} ({a.match_score}%)" for a in analyses if a.match_score >= 50]
    alts = [f"{a.name} (thay {a.commercial_alternative})" for a in analyses if a.commercial_alternative]

    # 5. Output persistent artifacts
    os.makedirs(output_dir, exist_ok=True)
    lang_tag = f"_{language}" if language else ""
    md_filename = f"trending_{date_str}{lang_tag}_{timeframe}.md"
    html_filename = f"dashboard_{date_str}{lang_tag}_{timeframe}.html"

    md_path = os.path.join(output_dir, md_filename)
    html_path = os.path.join(output_dir, html_filename)

    # Save Markdown report
    md_content = generate_markdown_report(analyses, timeframe=timeframe, language=language)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Save HTML dashboard
    html_content = generate_html_dashboard(analyses, timeframe=timeframe, language=language or "all")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    summary = {
        "date": date_str,
        "timestamp": timestamp_str,
        "status": "success",
        "timeframe": timeframe,
        "language": language or "All",
        "total_analyzed": len(analyses),
        "breakouts": breakouts,
        "new_entries": new_entries,
        "matches": matches,
        "commercial_alternatives": alts,
        "report_md": md_path,
        "report_html": html_path,
    }

    # 6. Send Webhook Notification if configured
    if webhook_url:
        summary["webhook_sent"] = send_webhook_notification(webhook_url, summary)

    return summary


def export_cron_script(python_exe: str, cli_path: str, timeframe: str = "daily", hour: int = 8, minute: int = 0) -> str:
    """Generate crontab line for Unix/macOS."""
    workdir = os.path.dirname(os.path.abspath(cli_path))
    return f"{minute} {hour} * * * cd {workdir} && {python_exe} {cli_path} --since {timeframe} --schedule-once >> {workdir}/reports/cron.log 2>&1"


def export_windows_task_command(python_exe: str, cli_path: str, task_name: str = "GitHubTrendingAnalyzer", start_time: str = "08:00") -> str:
    """Generate Windows schtasks command line."""
    action = f'"{python_exe}" "{cli_path}" --schedule-once'
    return f'schtasks /Create /SC DAILY /TN "{task_name}" /TR "{action}" /ST {start_time} /F'


def run_daemon(
    interval_hours: int = 24,
    target_time: Optional[str] = "08:00",
    run_once: bool = False,
    job_kwargs: Optional[Dict[str, Any]] = None,
    max_iterations: Optional[int] = None,
) -> None:
    """Run recurring background daemon checking and executing jobs."""
    kwargs = job_kwargs or {}
    iterations = 0

    if run_once:
        print("🚀 Đang thực hiện tác vụ định kỳ (Run Once)...")
        res = run_scheduled_job(**kwargs)
        print(f"✅ Hoàn thành: {res.get('total_analyzed', 0)} repos -> {res.get('report_md')}")
        return

    print(f"⏱️ Khởi động Scheduler Daemon (mục tiêu chạy lúc {target_time or f'mỗi {interval_hours}h'}). Bấm Ctrl+C để dừng.")

    last_run_day = None
    while True:
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_day = now.strftime("%Y-%m-%d")

        should_run = False
        if target_time:
            if current_time_str == target_time and last_run_day != current_day:
                should_run = True
                last_run_day = current_day
        else:
            should_run = True

        if should_run:
            print(f"\n⏰ [{now.strftime('%Y-%m-%d %H:%M:%S')}] Kích hoạt tác vụ phân tích tự động...")
            try:
                res = run_scheduled_job(**kwargs)
                print(f"✅ Đã lưu báo cáo tại {res.get('report_md')} và {res.get('report_html')}")
            except Exception as e:
                print(f"❌ Lỗi khi chạy tác vụ tự động: {e}", file=sys.stderr)

            iterations += 1
            if max_iterations and iterations >= max_iterations:
                break

            if not target_time:
                time.sleep(interval_hours * 3600)
                continue

        time.sleep(30)
