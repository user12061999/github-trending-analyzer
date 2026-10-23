#!/usr/bin/env python3
"""
GitHub Trending Analyzer (`gh-trending`)
CLI entry point for analyzing trending repositories and their practical applications.
Zero-dependency by default (Python 3.8+ standard library).
"""

import argparse
import json
import os
import sys
import webbrowser

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.analyzer import analyze_batch, analyze_repository
from src.fetcher import fetch_repo_readme
from src.formatter import (
    BOLD,
    CYAN,
    DIM,
    GREEN,
    MAGENTA,
    RESET,
    WHITE,
    YELLOW,
    format_repo_card,
    generate_markdown_report,
    print_banner,
)
from src.html_dashboard import save_and_open_html_dashboard
from src.scraper import get_trending_repos
from src.watchlist import load_watchlist, merge_watchlists, parse_match_argument


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="🔥 GitHub Trending Analyzer — Phân tích tác dụng và tính năng của các repo đang hot trên GitHub.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--since", "-s",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="Mốc thời gian trending (mặc định: daily)\n- daily: hôm nay\n- weekly: tuần này\n- monthly: tháng này",
    )
    parser.add_argument(
        "--lang", "--language", "-l",
        dest="language",
        type=str,
        default=None,
        help="Lọc theo ngôn ngữ lập trình (ví dụ: python, rust, typescript, go, c++...)",
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=10,
        help="Số lượng repository cần phân tích (mặc định: 10)",
    )
    parser.add_argument(
        "--source",
        choices=["github", "hn"],
        default="github",
        help="Nguồn dữ liệu xu hướng:\n- github: GitHub Trending (mặc định)\n- hn: Hacker News Developer Trends",
    )
    parser.add_argument(
        "--hn",
        action="store_true",
        help="Lấy các repository đang được cộng đồng bàn luận sôi nổi nhất trên Hacker News",
    )
    parser.add_argument("--serve", action="store_true", help="Mở dashboard tìm kiếm project mới từ GitHub")
    parser.add_argument("--port", type=int, default=8766, help="Port dashboard local (mặc định 8766)")
    parser.add_argument("--no-browser", action="store_true", help="Không tự mở trình duyệt khi chạy server")
    parser.add_argument("--deep", action="store_true", help="Đọc README mới, metadata và tối đa 3 tài liệu liên kết trong repo")
    parser.add_argument("--model", default=None, help="Model Gemini (hoặc GEMINI_MODEL)")
    parser.add_argument(
        "--ai",
        action="store_true",
        help="Bật phân tích nâng cao bằng AI (Gemini) nếu có GEMINI_API_KEY",
    )
    parser.add_argument(
        "--gemini-key",
        type=str,
        default=None,
        help="Khoá API Google Gemini (hoặc đặt biến môi trường GEMINI_API_KEY)",
    )
    parser.add_argument(
        "--html", "--web",
        dest="open_web",
        action="store_true",
        help="Sinh và tự động mở Dashboard HTML trực quan trên trình duyệt",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Đường dẫn file để xuất báo cáo Markdown (ví dụ: -o report.md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Xuất dữ liệu thô dưới dạng JSON",
    )
    parser.add_argument(
        "--no-readme",
        action="store_true",
        help="Bỏ qua việc tải README chi tiết (chạy nhanh hơn, phân tích dựa trên mô tả)",
    )
    parser.add_argument(
        "--watchlist", "-w",
        action="store_true",
        help="Lọc và ưu tiên sắp xếp theo sở thích cấu hình trong watchlist.json",
    )
    parser.add_argument(
        "--match", "-m",
        type=str,
        default=None,
        help="Chấm điểm tương thích theo từ khóa tức thì (ví dụ: -m 'agent,rag,rust')",
    )
    parser.add_argument(
        "--min-maturity",
        choices=["production", "beta", "experimental"],
        default=None,
        help="Lọc độ hoàn thiện dự án tối thiểu (production, beta, experimental)",
    )
    parser.add_argument(
        "--alt", "--alternatives-only",
        dest="alternatives_only",
        action="store_true",
        help="Chỉ hiển thị các dự án định vị thay thế cho phần mềm/SaaS thương mại (ví dụ: ElevenLabs, Notion, Datadog...)",
    )
    parser.add_argument(
        "--type", "--repo-type",
        dest="repo_type",
        choices=["tool", "library", "model", "course", "awesome", "dataset"],
        default=None,
        help="Lọc theo loại repository:\n- tool: Công cụ / CLI / App\n- library: Thư viện / SDK\n- model: AI Model / Weights\n- course: Khóa học / Giáo trình / Sách\n- awesome: Awesome List\n- dataset: Dataset / Benchmark",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Bật chế độ menu tương tác (chọn repo để xem chi tiết hoặc mở trình duyệt)",
    )
    parser.add_argument(
        "--schedule-once",
        action="store_true",
        help="Chạy tác vụ tự động một lần, lưu báo cáo vào reports/ và gửi webhook nếu có",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Chạy ở chế độ tiến trình nền định kỳ (Scheduler Daemon)",
    )
    parser.add_argument(
        "--daemon-time",
        type=str,
        default="08:00",
        help="Thời gian chạy định kỳ mỗi ngày cho daemon (mặc định: 08:00)",
    )
    parser.add_argument(
        "--export-task",
        choices=["windows", "cron"],
        default=None,
        help="Xuất lệnh cài đặt tác vụ tự động theo hệ điều hành (windows hoặc cron)",
    )
    parser.add_argument(
        "--webhook",
        type=str,
        default=None,
        help="Webhook URL nhận thông báo tóm tắt khi hoàn thành tác vụ tự động (Discord / Slack)",
    )
    args = parser.parse_args()
    if args.deep and args.no_readme:
        parser.error("--deep cần README; không kết hợp với --no-readme")
    return args


def interactive_menu(analyses):
    """Provide an interactive terminal prompt to inspect repos or open them."""
    while True:
        print(f"\n{BOLD}{CYAN}=== MENU TƯƠNG TÁC ==={RESET}")
        print(f"Nhập số thứ tự (1-{len(analyses)}) để xem phân tích chi tiết")
        print(f"Nhập 'ask <số> <câu hỏi>' để đặt câu hỏi kỹ thuật (ví dụ: ask 1 có chạy offline không?)")
        print(f"Nhập 'o <số>' để mở repo trên trình duyệt (ví dụ: o 1)")
        print(f"Nhập 'w' để mở Dashboard HTML | Nhập 'q' để thoát")

        try:
            choice = input(f"{YELLOW}👉 Lựa chọn của bạn: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nĐã thoát.")
            break

        if not choice or choice.lower() == "q":
            print("Tạm biệt!")
            break

        if choice.lower() == "w":
            save_and_open_html_dashboard(analyses, open_browser=True)
            print(f"{GREEN}✓ Đã mở Dashboard HTML trên trình duyệt!{RESET}")
            continue

        if choice.lower().startswith("o "):
            parts = choice.split()
            if len(parts) >= 2 and parts[1].isdigit():
                idx = int(parts[1]) - 1
                if 0 <= idx < len(analyses):
                    repo_url = analyses[idx].url
                    print(f"{CYAN}Đang mở {repo_url}...{RESET}")
                    webbrowser.open(repo_url)
                else:
                    print(f"{MAGENTA}Số thứ tự không hợp lệ.{RESET}")
            continue

        if choice.lower().startswith("ask "):
            parts = choice.split(maxsplit=2)
            if len(parts) >= 3 and parts[1].isdigit():
                idx = int(parts[1]) - 1
                if 0 <= idx < len(analyses):
                    question = parts[2]
                    target_repo = analyses[idx]
                    print(f"\n{CYAN}⏳ Đang phân tích câu hỏi cho {target_repo.name}...{RESET}")
                    from src.repo_chat import ask_repo
                    ans_data = ask_repo(
                        full_name=target_repo.name,
                        question=question,
                        cached_analysis=target_repo.to_dict(),
                    )
                    print(f"\n{GREEN}{BOLD}💬 Trả lời ({ans_data['engine_used']}):{RESET}")
                    print(f"{WHITE}{ans_data['answer']}{RESET}\n")
                else:
                    print(f"{MAGENTA}Số thứ tự không hợp lệ.{RESET}")
            else:
                print(f"{YELLOW}Cú pháp đúng: ask <số thứ tự> <câu hỏi>{RESET}")
            continue

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(analyses):
                card = format_repo_card(analyses[idx], idx + 1, len(analyses), width=90)
                print(f"\n{card}")
            else:
                print(f"{MAGENTA}Số thứ tự không hợp lệ.{RESET}")
        else:
            print(f"{MAGENTA}Lệnh không nhận diện được.{RESET}")


def main():
    args = parse_arguments()

    if getattr(args, "export_task", None):
        from src.scheduler import export_cron_script, export_windows_task_command
        cli_path = os.path.abspath(__file__)
        py_exe = sys.executable
        if args.export_task == "windows":
            cmd = export_windows_task_command(py_exe, cli_path, start_time=args.daemon_time or "08:00")
            print(f"\n{BOLD}{GREEN}✓ Lệnh tạo tác vụ Windows Task Scheduler:{RESET}")
            print(f"{YELLOW}{cmd}{RESET}\n")
        else:
            cron = export_cron_script(py_exe, cli_path, timeframe=args.since)
            print(f"\n{BOLD}{GREEN}✓ Dòng cấu hình Crontab (Linux/macOS):{RESET}")
            print(f"{YELLOW}{cron}{RESET}\n")
        return

    if getattr(args, "daemon", False) or getattr(args, "schedule_once", False):
        from src.scheduler import run_daemon
        run_daemon(
            target_time=args.daemon_time if not args.schedule_once else None,
            run_once=args.schedule_once,
            job_kwargs={
                "timeframe": args.since,
                "language": args.language,
                "limit": args.limit,
                "use_ai": args.ai,
                "model": args.model,
                "deep": args.deep,
                "webhook_url": getattr(args, "webhook", None),
            }
        )
        return

    if args.serve:
        from src.search_server import serve_dashboard
        serve_dashboard(port=args.port, use_ai=args.ai, model=args.model, deep=args.deep, open_browser=not args.no_browser)
        return

    source = "hn" if args.hn else args.source
    if not args.json:
        src_name = "Hacker News discussions" if source == "hn" else "https://github.com/trending"
        print(f"{CYAN}⏳ Đang cào dữ liệu từ {src_name}...{RESET}")

    try:
        if source == "hn":
            from src.hacker_news import get_hn_trending_repos
            repos = get_hn_trending_repos(
                timeframe=args.since,
                limit=args.limit,
            )
        else:
            repos = get_trending_repos(
                language=args.language,
                since=args.since,
                limit=args.limit,
            )
    except Exception as e:
        src_label = "Hacker News" if source == "hn" else "GitHub Trending"
        print(f"\n{BOLD}\033[31m❌ Lỗi khi tải dữ liệu từ {src_label}:{RESET} {e}")
        print(f"{DIM}Gợi ý: Kiểm tra kết nối Internet hoặc thử lại sau giây lát.{RESET}\n")
        sys.exit(1)

    if not repos:
        print(f"\n{YELLOW}⚠️  Không tìm thấy repository trending nào với tiêu chí đã chọn.{RESET}")
        sys.exit(0)

    if not args.json:
        fetch_msg = "và tải README" if not args.no_readme else "(bỏ qua README)"
        print(f"{CYAN}🧠 Đang phân tích tác dụng {len(repos)} repository {fetch_msg}...{RESET}")

    # Prepare Watchlist if enabled
    active_watchlist = None
    if args.watchlist or args.match:
        base_wl = load_watchlist() if args.watchlist else {"keywords": [], "languages": [], "categories": []}
        match_wl = parse_match_argument(args.match) if args.match else {"keywords": [], "languages": [], "categories": []}
        active_watchlist = merge_watchlists(base_wl, match_wl)
        if not args.json:
            criteria_str = []
            if active_watchlist.get("keywords"):
                criteria_str.append(f"Keywords: {', '.join(active_watchlist['keywords'][:4])}")
            if active_watchlist.get("languages"):
                criteria_str.append(f"Langs: {', '.join(active_watchlist['languages'][:3])}")
            print(f"{YELLOW}⭐ Chế độ sở thích đã bật ({' | '.join(criteria_str)}){RESET}")

    # Analyze repositories
    analyses = analyze_batch(
        repos=repos,
        use_ai=args.ai,
        fetch_readme=not args.no_readme,
        gemini_api_key=args.gemini_key,
        watchlist=active_watchlist,
        deep=args.deep,
        model=args.model,
    )

    # Filter by minimum maturity if requested
    if args.min_maturity:
        orig_count = len(analyses)
        if args.min_maturity == "production":
            analyses = [a for a in analyses if a.maturity_level == "production"]
        elif args.min_maturity == "beta":
            analyses = [a for a in analyses if a.maturity_level in ("production", "beta")]
        if not args.json:
            print(f"{MAGENTA}🔍 Đã lọc theo độ chín '{args.min_maturity}': còn {len(analyses)}/{orig_count} repos.{RESET}")

    # Filter by commercial alternatives if requested
    if args.alternatives_only:
        orig_count = len(analyses)
        analyses = [a for a in analyses if a.is_commercial_alt]
        if not args.json:
            print(f"{MAGENTA}💡 Đã lọc theo giải pháp thay thế thương mại: còn {len(analyses)}/{orig_count} repos.{RESET}")

    # Filter by repository type if requested
    if args.repo_type:
        type_mapping = {
            "tool": "tool_app",
            "library": "library_sdk",
            "model": "ai_model",
            "course": "course_tutorial",
            "awesome": "awesome_list",
            "dataset": "dataset_benchmark",
        }
        target_type = type_mapping.get(args.repo_type, args.repo_type)
        orig_count = len(analyses)
        analyses = [a for a in analyses if getattr(a, "repo_type", "") == target_type]
        if not args.json:
            print(f"{MAGENTA}🏷️  Đã lọc theo loại dự án '{args.repo_type}': còn {len(analyses)}/{orig_count} repos.{RESET}")

    # Prioritize & sort by Match Score if watchlist active
    if active_watchlist:
        analyses.sort(key=lambda a: (a.match_score, a.velocity_score), reverse=True)

    # Output JSON if requested
    if args.json:
        print(json.dumps([a.to_dict() for a in analyses], indent=2, ensure_ascii=False))
        return

    # Print Terminal Banner & Cards
    print_banner(timeframe=args.since, language=args.language, total=len(analyses))

    for i, a in enumerate(analyses, 1):
        card = format_repo_card(a, i, len(analyses))
        print(card)
        print()

    # Export Markdown if requested
    if args.output:
        md_content = generate_markdown_report(analyses, timeframe=args.since, language=args.language)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"{GREEN}✓ Đã xuất báo cáo Markdown ra file:{RESET} {BOLD}{args.output}{RESET}")

    # HTML Dashboard if requested
    if args.open_web:
        html_file = save_and_open_html_dashboard(
            analyses,
            output_path="trending_dashboard.html",
            timeframe=args.since,
            language=args.language,
            open_browser=True,
        )
        print(f"{GREEN}✓ Đã tạo và mở Dashboard HTML:{RESET} {BOLD}{html_file}{RESET}")

    # Interactive mode if requested
    if args.interactive:
        interactive_menu(analyses)


if __name__ == "__main__":
    main()
