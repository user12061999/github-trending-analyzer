"""CLI Formatter & Markdown Generator for GitHub Trending Analyzer."""

import os
import shutil
from typing import List

from src.alternatives import get_alternative_description
from src.analyzer import RepoAnalysis

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
GRAY = "\033[90m"

BG_DARK = "\033[40m"
BG_BLUE = "\033[44m"


def _wrap_text(text: str, width: int, indent: int = 0) -> List[str]:
    """Wrap text to a specific width with optional indent."""
    words = text.split()
    if not words:
        return [" " * indent]

    lines = []
    current_line = []
    current_len = indent

    for w in words:
        if current_len + len(w) + 1 <= width:
            current_line.append(w)
            current_len += len(w) + 1
        else:
            if current_line:
                lines.append(" " * indent + " ".join(current_line))
            current_line = [w]
            current_len = indent + len(w)

    if current_line:
        lines.append(" " * indent + " ".join(current_line))

    return lines


def research_sections(analysis):
    return [
        ("Cách hoạt động & kiến trúc", analysis.how_it_works),
        ("Ví dụ thực tế & cách đánh giá", analysis.practical_examples),
        ("Giới hạn & trường hợp không phù hợp", analysis.limitations),
        ("Yêu cầu triển khai & tích hợp", analysis.adoption_notes),
        ("So sánh & trade-off", analysis.comparisons),
        ("Thông tin cần kiểm chứng thêm", analysis.research_gaps),
    ]


def format_repo_card(analysis: RepoAnalysis, index: int, total: int, width: int = 80) -> str:
    """Format a single repository analysis as a bordered terminal card."""
    lines = []
    card_width = min(width, 100)
    inner_width = card_width - 4

    top_border = f"{CYAN}╭{'─' * (card_width - 2)}╮{RESET}"
    mid_border = f"{CYAN}├{'─' * (card_width - 2)}┤{RESET}"
    bot_border = f"{CYAN}╰{'─' * (card_width - 2)}╯{RESET}"

    lines.append(top_border)

    # Header: Index, Name, Language, Stars
    lang_badge = f"{YELLOW}[{analysis.language}]{RESET}" if analysis.language else ""
    stars_badge = f"{GREEN}★ +{analysis.stars_since}{RESET}" if analysis.stars_since else ""
    total_stars = f"{DIM}(🌟 {analysis.stars_total}){RESET}" if analysis.stars_total else ""

    header_left = f"{BOLD}{WHITE}#{index}/{total} 📦 {CYAN}{analysis.name}{RESET}"
    header_right = f"{lang_badge} {stars_badge} {total_stars}".strip()
    
    # Simple line printing
    lines.append(f"{CYAN}│{RESET} {header_left}  {header_right}")
    lines.append(f"{CYAN}│{RESET} {GRAY}🔗 {analysis.url}{RESET}")
    lines.append(f"{CYAN}│{RESET} {MAGENTA}🏷️  Phân loại:{RESET} {BOLD}{analysis.category}{RESET}  {DIM}(Engine: {analysis.engine_used}){RESET}")

    # Velocity, Maturity, Alternative & Match Score Badges
    status_badges = []
    if getattr(analysis, "repo_type_badge", None):
        status_badges.append(f"{BLUE}{BOLD}{analysis.repo_type_badge}{RESET}")
    if analysis.velocity_badge:
        v_color = RED if "Breakout" in analysis.velocity_badge else (YELLOW if "Velocity" in analysis.velocity_badge else CYAN)
        status_badges.append(f"{v_color}{BOLD}{analysis.velocity_badge}{RESET}")
    if analysis.maturity_badge:
        m_color = GREEN if "Production" in analysis.maturity_badge else (YELLOW if "Beta" in analysis.maturity_badge else MAGENTA)
        status_badges.append(f"{m_color}{BOLD}{analysis.maturity_badge}{RESET}")
    if getattr(analysis, "grounding_score", None):
        g_color = GREEN if analysis.grounding_score >= 80 else (YELLOW if analysis.grounding_score >= 60 else RED)
        status_badges.append(f"{g_color}{BOLD}🛡️ Grounding: {analysis.grounding_score}/100{RESET}")
    if analysis.commercial_alternative:
        status_badges.append(f"{MAGENTA}{BOLD}💡 Thay thế: {analysis.commercial_alternative}{RESET}")
    if analysis.match_score > 0:
        kw_info = f"({', '.join(analysis.matched_keywords[:3])})" if analysis.matched_keywords else ""
        status_badges.append(f"{YELLOW}{BOLD}⭐ {analysis.match_score}% Match {kw_info}{RESET}")

    if status_badges:
        lines.append(f"{CYAN}│{RESET} " + "  ".join(status_badges))

    if analysis.commercial_alternative:
        alt_desc = get_alternative_description(analysis.commercial_alternative)
        desc_str = f" — {alt_desc}" if alt_desc else ""
        lines.append(f"{CYAN}│{RESET} {BOLD}{MAGENTA}💡 THAY THẾ MÃ NGUỒN MỞ CHO:{RESET} {WHITE}{BOLD}{analysis.commercial_alternative}{RESET}{DIM}{desc_str}{RESET}")

    if analysis.tech_stack:
        lines.append(f"{CYAN}│{RESET} {BOLD}{CYAN}🛠️  Tech Stack:{RESET} {WHITE}{' • '.join(analysis.tech_stack)}{RESET}")

    lines.append(mid_border)

    # Quick Run Command (if available)
    if analysis.quick_run:
        lines.append(f"{CYAN}│{RESET} {BOLD}{GREEN}⚡ LỆNH CHẠY THỬ / CÀI ĐẶT NHANH:{RESET}")
        lines.append(f"{CYAN}│{RESET}   {YELLOW}{BOLD}{analysis.quick_run}{RESET}")
        lines.append(mid_border)

    # Core Purpose (Làm gì & Tác dụng)
    lines.append(f"{CYAN}│{RESET} {BOLD}{YELLOW}🎯 LÀM GÌ & TÁC DỤNG CỐT LÕI:{RESET}")
    purpose_lines = _wrap_text(analysis.core_purpose, inner_width, indent=3)
    for pl in purpose_lines:
        lines.append(f"{CYAN}│{RESET}{pl}")

    # Key Features (Tính năng chi tiết)
    if analysis.key_features:
        lines.append(f"{CYAN}│{RESET} {BOLD}{GREEN}💡 TÍNH NĂNG CHI TIẾT & ĐIỂM ĂN TIỀN:{RESET}")
        for feat in analysis.key_features:
            feat_lines = _wrap_text(f"• {feat}", inner_width, indent=3)
            for fl in feat_lines:
                lines.append(f"{CYAN}│{RESET}{fl}")

    # Suitable Major & Target Roles
    if analysis.suitable_major or analysis.target_roles:
        lines.append(f"{CYAN}│{RESET} {BOLD}{BLUE}🎓 PHÙ HỢP CHUYÊN NGÀNH & VAI TRÒ:{RESET}")
        if analysis.suitable_major:
            major_lines = _wrap_text(f"📚 Chuyên ngành: {analysis.suitable_major}", inner_width, indent=3)
            for ml in major_lines:
                lines.append(f"{CYAN}│{RESET}{ml}")
        if analysis.target_roles:
            role_lines = _wrap_text(f"👤 Vị trí phù hợp: {analysis.target_roles}", inner_width, indent=3)
            for rl in role_lines:
                lines.append(f"{CYAN}│{RESET}{rl}")

    # Real-World Impact (Bài toán giải quyết)
    if analysis.real_world_impact:
        lines.append(f"{CYAN}│{RESET} {BOLD}{WHITE}💥 BÀI TOÁN THỰC TẾ GIẢI QUYẾT:{RESET}")
        impact_lines = _wrap_text(analysis.real_world_impact, inner_width, indent=3)
        for il in impact_lines:
            lines.append(f"{CYAN}│{RESET}{il}")

    # Use Cases
    if analysis.use_cases:
        lines.append(f"{CYAN}│{RESET} {BOLD}{CYAN}🚀 KỊCH BẢN ỨNG DỤNG:{RESET}")
        for uc in analysis.use_cases[:2]:
            uc_lines = _wrap_text(f"✔ {uc}", inner_width, indent=3)
            for ucl in uc_lines:
                lines.append(f"{CYAN}│{RESET}{ucl}")

    for title, items in research_sections(analysis):
        if items:
            lines.append(f"{CYAN}│{RESET} {BOLD}{CYAN}{title}:{RESET}")
            for item in items:
                for line in _wrap_text(f"• {item}", inner_width, indent=3):
                    lines.append(f"{CYAN}│{RESET}{line}")
    if analysis.data_sources:
        lines.append(f"{CYAN}│{RESET} {BOLD}NGUỒN TÀI LIỆU:{RESET}")
        for source in analysis.data_sources:
            lines.append(f"{CYAN}│{RESET} [{source['id']}] {source['title']}: {source['url']}")

    # Why Trending / Quick Verdict
    if analysis.why_trending or analysis.quick_verdict:
        lines.append(f"{CYAN}│{RESET} {BOLD}{MAGENTA}🔥 ĐÁNH GIÁ & ĐỘ HOT:{RESET}")
        commentary = f"{analysis.why_trending} {analysis.quick_verdict}".strip()
        comm_lines = _wrap_text(commentary, inner_width, indent=3)
        for cl in comm_lines:
            lines.append(f"{CYAN}│{RESET}{cl}")

    lines.append(bot_border)
    return "\n".join(lines)



def print_banner(timeframe: str = "daily", language: str = None, total: int = 0):
    """Print an attractive header banner in the terminal."""
    lang_str = f" ({language})" if language else ""
    time_map = {
        "daily": "Hôm nay (Daily)",
        "weekly": "Tuần này (Weekly)",
        "monthly": "Tháng này (Monthly)",
    }
    time_str = time_map.get(timeframe, timeframe)

    cols = shutil.get_terminal_size((80, 20)).columns
    width = min(cols, 90)

    print()
    print(f"{CYAN}{BOLD}{'═' * width}{RESET}")
    print(f"{CYAN}{BOLD}  🔥 GITHUB TRENDING ANALYZER — PHÂN TÍCH TÁC DỤNG DỰ ÁN MÃ NGUỒN MỞ{RESET}")
    print(f"  {DIM}Mốc thời gian:{RESET} {YELLOW}{time_str}{RESET} | {DIM}Ngôn ngữ:{RESET} {GREEN}{lang_str or 'Tất cả'}{RESET} | {DIM}Số lượng:{RESET} {WHITE}{total} repos{RESET}")
    print(f"{CYAN}{BOLD}{'═' * width}{RESET}\n")


def generate_markdown_report(analyses: List[RepoAnalysis], timeframe: str = "daily", language: str = None) -> str:
    """Generate a clean, structured Markdown report."""
    lang_str = f" ({language})" if language else ""
    md = [
        f"# 📊 Báo cáo phân tích GitHub Trending — {timeframe.capitalize()}{lang_str}",
        "",
        "> Báo cáo tự động phân tích tác dụng cốt lõi, giá trị thực tiễn và lý do thịnh hành của các dự án mã nguồn mở.",
        "",
        "## 📑 Mục lục tóm tắt",
        "",
        "| # | Repository | Ngôn ngữ | Stars Mới | Bứt phá | Độ chín | Thay thế | Match | Phân loại |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for i, a in enumerate(analyses, 1):
        stars_s = f"+{a.stars_since}" if a.stars_since else "-"
        match_s = f"{a.match_score}%" if a.match_score > 0 else "-"
        alt_s = f"`{a.commercial_alternative}`" if a.commercial_alternative else "-"
        md.append(f"| {i} | [{a.name}]({a.url}) | `{a.language}` | {stars_s} | {a.velocity_badge or '-'} | {a.maturity_badge or '-'} | {alt_s} | {match_s} | {a.category} |")

    md.extend(["", "---", "", "## 🔍 Phân tích chi tiết từng dự án", ""])

    for i, a in enumerate(analyses, 1):
        md.append(f"### {i}. [{a.name}]({a.url})")
        md.append(f"- **Ngôn ngữ**: `{a.language}` | **Tổng sao**: ⭐ {a.stars_total} (+{a.stars_since} {a.timeframe})")
        md.append(f"- **Độ bứt phá**: {a.velocity_badge or 'Bình thường'} | **Độ hoàn thiện**: {a.maturity_badge or 'Đang phát triển'}")
        if a.commercial_alternative:
            alt_desc = get_alternative_description(a.commercial_alternative)
            md.append(f"- **💡 Thay thế mã nguồn mở cho**: **{a.commercial_alternative}** ({alt_desc})")
        if a.match_score > 0:
            md.append(f"- **Điểm tương thích sở thích**: ⭐ `{a.match_score}%` ({', '.join(a.matched_keywords)})")
        if a.tech_stack:
            md.append(f"- **Tech Stack**: `{', '.join(a.tech_stack)}`")
        if getattr(a, "repo_type_badge", None):
            md.append(f"- **Loại dự án**: {a.repo_type_badge}")
        if getattr(a, "grounding_score", None):
            md.append(f"- **🛡️ Phản biện & Xác thực (Grounding)**: `{a.grounding_score}/100`")
        md.append(f"- **Phân loại**: `{a.category}`")
        md.append(f"- **Mô tả gốc**: *{a.description or 'Không có mô tả'}*")
        md.append("")

        if a.quick_run:
            md.append("#### ⚡ Lệnh chạy thử / Cài đặt nhanh")
            md.append("```bash")
            md.append(a.quick_run)
            md.append("```")
            md.append("")

        md.append("#### 🎯 Tác dụng cốt lõi & Vấn đề giải quyết")
        md.append(f"{a.core_purpose}")
        md.append("")

        if a.key_features:
            md.append("#### 💡 Tính năng & Điểm ăn tiền")
            for f in a.key_features:
                md.append(f"- {f}")
            md.append("")

        if a.suitable_major:
            md.append(f"#### 🎓 Phù hợp chuyên ngành: {a.suitable_major}")
            if a.target_roles:
                md.append(f"- **Vị trí phù hợp:** {a.target_roles}")
            md.append("")

        if a.real_world_impact:
            md.append(f"#### 💥 Bài toán thực tế giải quyết")
            md.append(a.real_world_impact)
            md.append("")

        if a.use_cases:
            md.append("#### 🚀 Bối cảnh ứng dụng thực tế")
            for uc in a.use_cases:
                md.append(f"- {uc}")
            md.append("")

        if a.why_trending or a.quick_verdict:
            md.append("#### ⚡ Lý do hot & Đánh giá nhanh")
            if a.why_trending:
                md.append(f"- **Lý do trending:** {a.why_trending}")
            if a.quick_verdict:
                md.append(f"- **Đánh giá nhanh:** {a.quick_verdict}")
            md.append("")

        md.append(f"**Chế độ phân tích:** {a.research_depth} | **Engine:** {a.engine_used}")
        md.append("")
        for title, items in research_sections(a):
            if items:
                md.extend([f"#### {title}", ""])
                for item in items:
                    md.append("- " + item.replace("\n", "\n  "))
                md.append("")
        if getattr(a, "grounding_critique", None):
            md.extend(["#### 🛡️ Tự phản biện & Kiểm chứng khách quan", ""])
            for c in a.grounding_critique:
                md.append(f"- {c}")
            md.append("")
        if a.data_sources:
            md.extend(["#### Nguồn đã đọc", ""])
            for source in a.data_sources:
                md.append(f"- [{source['id']}] [{source['title']}]({source['url']}) — {source['fetched_at']}; {source['freshness']}")
            md.append("")
        md.append("---")
        md.append("")

    return "\n".join(md)
