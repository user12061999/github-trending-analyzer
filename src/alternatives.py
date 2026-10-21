"""Commercial Alternative & Open Source Substitute Detection Module.

Identifies whether an open-source repository positions itself as or functions
as a self-hosted / free / open-source alternative to commercial SaaS products.
"""

import re
from typing import Dict, List, Optional, Set, Tuple

# Curated knowledge base of commercial products commonly replaced by open-source tools
KNOWN_COMMERCIAL_TARGETS: Dict[str, str] = {
    # AI & Speech
    "ElevenLabs": "Nền tảng Voice AI, tổng hợp & nhân bản giọng nói",
    "OpenAI": "Dịch vụ mô hình ngôn ngữ lớn & API AI",
    "Midjourney": "Dịch vụ tạo ảnh bằng AI thương mại",
    "Runway": "Nền tảng sinh video AI thương mại",
    "Cursor": "AI Code Editor thương mại",
    "GitHub Copilot": "Trợ lý lập trình AI đám mây",
    "Perplexity": "Công cụ tìm kiếm & trả lời câu hỏi AI",
    "Weights & Biases": "Nền tảng MLOps & Experiment Tracking",
    # Productivity & Collaboration
    "Notion": "Ứng dụng ghi chú, tài liệu & workspace cộng tác",
    "Airtable": "Bảng tính cơ sở dữ liệu quan hệ đám mây",
    "Linear": "Công cụ quản lý dự án & theo dõi vấn đề cho tech team",
    "Jira": "Hệ thống quản lý công việc và quy trình phần mềm",
    "Confluence": "Hệ thống wiki & quản lý tri thức doanh nghiệp",
    "Miro": "Bảng trắng cộng tác trực tuyến",
    "Figma": "Công cụ thiết kế UI/UX cộng tác trên trình duyệt",
    "Calendly": "Hệ thống lên lịch hẹn tự động",
    "Loom": "Dịch vụ quay và chia sẻ video màn hình nhanh",
    "Slack": "Nền tảng giao tiếp và nhắn tin đội nhóm",
    # Cloud, Infra & BaaS
    "Firebase": "Backend-as-a-Service của Google",
    "Supabase": "Backend-as-a-Service mã nguồn mở (thay thế cho Firebase)",
    "Vercel": "Nền tảng triển khai và hosting frontend",
    "Heroku": "PaaS triển khai ứng dụng đám mây",
    "AWS S3": "Dịch vụ lưu trữ đối tượng đám mây",
    "Docker Desktop": "Ứng dụng quản lý Docker GUI thương mại",
    "Cloudflare": "Mạng CDN, bảo mật và DNS đám mây",
    # DevTools & Testing
    "Postman": "Ứng dụng kiểm thử và phát triển API thương mại",
    "Retool": "Nền tảng xây dựng internal tools nhanh",
    "Zapier": "Nền tảng tự động hóa quy trình nghiệp vụ (no-code iPaaS)",
    "Make": "Nền tảng tích hợp và tự động hóa quy trình (trước là Integromat)",
    # Observability & Monitoring
    "Datadog": "Nền tảng giám sát APM, hạ tầng & logs toàn diện",
    "Splunk": "Hệ thống phân tích và quản lý log dữ liệu lớn",
    "Sentry": "Hệ thống theo dõi lỗi và giám sát hiệu năng ứng dụng",
    "New Relic": "Nền tảng quan sát và giám sát hiệu năng ứng dụng",
    # Analytics & Marketing
    "Google Analytics": "Hệ thống phân tích truy cập website",
    "Mixpanel": "Nền tảng phân tích hành vi người dùng sản phẩm",
    "Amplitude": "Nền tảng Digital Analytics chuyên sâu",
    "Intercom": "Hệ thống chat hỗ trợ khách hàng & CRM",
    # Auth & Security
    "Auth0": "Dịch vụ xác thực và quản lý định danh người dùng (IdP)",
    "Okta": "Nền tảng quản lý truy cập và định danh doanh nghiệp",
    "1Password": "Trình quản lý mật khẩu thương mại",
    "Bitwarden": "Trình quản lý mật khẩu mã nguồn mở",
    # Communication & Finance
    "Twilio": "Nền tảng API truyền thông (SMS, Voice, Video)",
    "Stripe": "Cổng thanh toán trực tuyến",
    "Lemon Squeezy": "Nền tảng thanh toán và quản lý merchant of record",
}

FALSE_POSITIVE_WORDS: Set[str] = {
    "using", "traditional", "existing", "standard", "current", "common", "commercial",
    "proprietary", "closed", "expensive", "cloud", "manual", "legacy", "other", "any",
    "complex", "heavy", "centralized", "slow", "old", "the", "a", "an", "all", "its",
    "their", "these", "those", "solution", "solutions", "tool", "tools", "framework",
    "frameworks", "library", "libraries", "service", "services", "software", "system",
    "systems", "approach", "approaches", "method", "methods", "way", "ways", "option",
    "options", "platform", "platforms", "web", "app", "application", "applications",
    "building", "creating", "writing", "running", "developing", "managing"
}


def clean_target_name(raw_name: str) -> Optional[str]:
    """Clean and validate an extracted commercial target name."""
    if not raw_name:
        return None
    # Strip common punctuation and leading/trailing noise
    clean = re.sub(r"^[^\w]+|[^\w]+$", "", raw_name.strip())
    clean = re.sub(r"^(the|an?|your|our|any|all)\s+", "", clean, flags=re.IGNORECASE).strip()

    if not clean or len(clean) < 2 or len(clean) > 35:
        return None

    # Check against known dictionary first (highest priority)
    for known, _ in KNOWN_COMMERCIAL_TARGETS.items():
        if clean.lower() == known.lower():
            return known

    # Token check for false positives
    words = clean.lower().split()
    for w in words:
        if w in FALSE_POSITIVE_WORDS:
            return None

    # For unknown targets, require proper noun formatting (capitalized first letter)
    first_token = clean.split()[0]
    if not first_token[0].isupper():
        return None

    return clean


def detect_commercial_alternative(
    name: str,
    description: str,
    readme_raw: Optional[str] = None
) -> Optional[str]:
    """Detect if this repo is an alternative to a commercial SaaS or software.

    Returns:
        The recognized commercial product name (e.g. 'ElevenLabs', 'Notion') or None.
    """
    desc = description or ""
    readme_preview = (readme_raw or "")[:5000]
    corpus = f"{desc}\n{readme_preview}"

    # Check against known dictionary + dynamically learned knowledge base
    dynamic_targets = {}
    try:
        from src.history_db import get_learned_knowledge, add_learned_knowledge
        dynamic_targets = get_learned_knowledge("commercial_target")
    except Exception:
        pass

    all_targets = {**KNOWN_COMMERCIAL_TARGETS, **dynamic_targets}

    # 1. High precision check against known & learned targets in comparison context
    for target in all_targets:
        target_pat = rf"\b{re.escape(target)}\b"
        if re.search(target_pat, corpus, re.IGNORECASE):
            # Verify comparison intent exists in the text
            comp_keywords = [
                rf"alternative\s+to\s+{re.escape(target)}",
                rf"{re.escape(target)}\s+alternative",
                rf"replacement\s+for\s+{re.escape(target)}",
                rf"replace\s+{re.escape(target)}",
                rf"substitute\s+for\s+{re.escape(target)}",
                rf"drop-in\s+(?:replacement\s+)?for\s+{re.escape(target)}",
                rf"like\s+{re.escape(target)}\s+but",
                rf"instead\s+of\s+{re.escape(target)}",
                rf"switch\s+from\s+{re.escape(target)}",
                rf"open-source\s+(?:version\s+of\s+)?{re.escape(target)}",
                rf"self-hosted\s+(?:version\s+of\s+)?{re.escape(target)}",
                rf"vs\.?\s+{re.escape(target)}",
            ]
            for ckw in comp_keywords:
                if re.search(ckw, corpus, re.IGNORECASE):
                    return target

    # 2. General regex patterns to capture unlisted commercial targets
    general_patterns = [
        r"(?:open[\s-]source|self[\s-]hosted|free|drop[\s-]in|local|private)?\s*(?:alternative|replacement|substitute)\s+(?:to|for)\s+([A-Z][A-Za-z0-9_\-]+(?:\s+[A-Z][A-Za-z0-9_\-]+)?)",
        r"([A-Z][A-Za-z0-9_\-]+(?:\s+[A-Z][A-Za-z0-9_\-]+)?)\s+(?:alternative|replacement)",
        r"(?:replaces?|drop-in replacement for)\s+([A-Z][A-Za-z0-9_\-]+(?:\s+[A-Z][A-Za-z0-9_\-]+)?)",
        r"(?:like|similar to)\s+([A-Z][A-Za-z0-9_\-]+(?:\s+[A-Z][A-Za-z0-9_\-]+)?)\s+but\s+(?:open[\s-]source|free|local)",
    ]

    for pat in general_patterns:
        matches = re.finditer(pat, corpus)
        for m in matches:
            candidate = clean_target_name(m.group(1))
            if candidate:
                # Automatically learn this candidate into the dynamic knowledge base
                try:
                    from src.history_db import add_learned_knowledge
                    add_learned_knowledge(candidate, "commercial_target", f"Phát hiện tự động từ {name}", detected_from_repo=name)
                except Exception:
                    pass
                return candidate

    return None


def get_alternative_description(target: Optional[str]) -> str:
    """Return Vietnamese description / role of the commercial target if known."""
    if not target:
        return ""
    for known, desc in KNOWN_COMMERCIAL_TARGETS.items():
        if known.lower() == target.lower():
            return desc
    try:
        from src.history_db import get_learned_knowledge
        dynamic = get_learned_knowledge("commercial_target")
        for dyn_target, desc in dynamic.items():
            if dyn_target.lower() == target.lower() and desc:
                return desc
    except Exception:
        pass
    return f"Sản phẩm / dịch vụ thương mại {target}"
