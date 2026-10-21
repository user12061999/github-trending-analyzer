"""Grounded Self-Critique & Anti-Hallucination Sanitizer.

Enforces citation markers [S1], [S2], scrubs or soft-tones unsubstantiated hype,
validates technical limitations, and produces an objective Grounding Quality Score.
"""

import re
from typing import Any, Dict, List, Tuple


# Regex pattern to identify unverified promotional superlatives
HYPE_PATTERNS = [
    (re.compile(r"\b(tốt nhất (hiện nay|thế giới|mọi thời đại))\b", re.IGNORECASE), "được định vị hàng đầu"),
    (re.compile(r"\b(thay đổi hoàn toàn thế giới)\b", re.IGNORECASE), "được kỳ vọng cải tiến đáng kể"),
    (re.compile(r"\b(cách mạng hóa)\b", re.IGNORECASE), "tạo bước tiến mới cho"),
    (re.compile(r"\b(không có đối thủ|vô địch|bất bại|vô song)\b", re.IGNORECASE), "có ưu thế cạnh tranh nổi bật"),
    (re.compile(r"\b(hoàn hảo 100%|tuyệt đối không có lỗi|không có bất kỳ nhược điểm)\b", re.IGNORECASE), "được thiết kế tối ưu nhưng cần kiểm chứng"),
    (re.compile(r"\b(game[ -]?changer)\b", re.IGNORECASE), "giải pháp đáng chú ý"),
    (re.compile(r"\b(best in the world|unbeatable|flawless 100%)\b", re.IGNORECASE), "top-tier open source solution"),
]

# Pattern detecting source citations e.g. [S1], [S2], [README], [docs/...]
CITATION_PATTERN = re.compile(r"\[(S\d+|README|docs\/|how-it-works|install|quickstart|features|feature-catalog|architecture)[^\]]*\]", re.IGNORECASE)


def detect_hype_terms(text: str) -> List[str]:
    """Find unverified superlative or hype phrases in a string."""
    detected = []
    if not text:
        return detected
    for pattern, _ in HYPE_PATTERNS:
        matches = pattern.findall(text)
        for m in matches:
            phrase = m[0] if isinstance(m, tuple) else m
            if phrase and phrase not in detected:
                detected.append(phrase)
    return detected


def soften_hype_phrases(text: str) -> str:
    """Soft-tone unsubstantiated superlatives into objective, realistic statements."""
    if not text:
        return text
    result = text
    for pattern, replacement in HYPE_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def count_citations(texts: List[str]) -> int:
    """Count how many items contain valid document source citations."""
    count = 0
    for t in texts:
        if isinstance(t, str) and CITATION_PATTERN.search(t):
            count += 1
    return count


def evaluate_grounding(analysis_obj_or_dict: Any) -> Tuple[int, List[str]]:
    """Evaluate grounding quality score (40 - 100) and generate self-critique notes."""
    if isinstance(analysis_obj_or_dict, dict):
        d = analysis_obj_or_dict
    else:
        d = getattr(analysis_obj_or_dict, "__dict__", {})

    score = 100
    critique: List[str] = []

    # 1. Hype & Superlative Check
    combined_prose = " ".join([
        str(d.get("core_purpose", "")),
        str(d.get("quick_verdict", "")),
        str(d.get("real_world_impact", "")),
        " ".join(d.get("key_features", [])),
    ])
    detected_hype = detect_hype_terms(combined_prose)
    if detected_hype:
        score -= 15
        critique.append(f"Phát hiện từ ngữ tiếp thị/tuyệt đối hóa chưa có benchmark độc lập: '{', '.join(detected_hype[:3])}'.")

    # 2. Source Citations Check
    tech_sections = [
        *d.get("how_it_works", []),
        *d.get("limitations", []),
        *d.get("adoption_notes", []),
        *d.get("comparisons", []),
    ]
    citations_count = count_citations(tech_sections)
    if not tech_sections or citations_count == 0:
        score -= 20
        critique.append("Thiếu trích dẫn ID nguồn [S1], [S2] hoặc section tài liệu trong phân tích kỹ thuật.")
    elif citations_count < 2:
        score -= 10
        critique.append("Mức độ trích dẫn nguồn còn mỏng (dưới 2 vị trí có nguồn dẫn).")

    # 3. Honest Limitations & Trade-offs Check
    limits = d.get("limitations", [])
    if not limits:
        score -= 20
        critique.append("Thiếu danh mục giới hạn kỹ thuật và điều kiện không nên sử dụng.")
    elif len(limits) < 2 and not any("chưa" in str(item).lower() or "giới hạn" in str(item).lower() or "cần" in str(item).lower() for item in limits):
        score -= 10
        critique.append("Phần giới hạn kỹ thuật còn sơ lược, cần bổ sung rủi ro triển khai.")

    # 4. Realistic Test / Verification Check
    examples = d.get("practical_examples", [])
    if not examples:
        score -= 15
        critique.append("Chưa có đề xuất kịch bản thử nghiệm thực tế.")
    else:
        has_eval_criteria = any(
            any(w in str(ex).lower() for w in ["đo lường", "tiêu chí", "đánh giá", "kiểm tra", "thử nghiệm", "so sánh"])
            for ex in examples
        )
        if not has_eval_criteria:
            score -= 10
            critique.append("Kịch bản thực tế chưa nêu rõ tiêu chí đánh giá hoặc cách đo lường hiệu quả.")

    # 5. Research Gaps & Unknowns Check
    gaps = d.get("research_gaps", [])
    if not gaps:
        score -= 10
        critique.append("Chưa nêu rõ các điểm mù thông tin hoặc nội dung tài liệu chưa đề cập.")

    # Ensure bounds [40, 100]
    score = max(40, min(100, score))

    if not critique:
        critique.append("Bản phân tích đạt tiêu chuẩn chặt chẽ, trích dẫn đầy đủ và phân biệt rõ tuyên bố của tác giả với kiểm chứng thực tế.")

    return score, critique


def sanitize_and_ground_analysis(analysis: Any) -> Any:
    """Sanitize hype, ensure essential safety gaps, and populate grounding scores."""
    # 1. Soft-tone superlatives
    if hasattr(analysis, "core_purpose"):
        analysis.core_purpose = soften_hype_phrases(analysis.core_purpose)
    if hasattr(analysis, "quick_verdict"):
        analysis.quick_verdict = soften_hype_phrases(analysis.quick_verdict)
    if hasattr(analysis, "real_world_impact"):
        analysis.real_world_impact = soften_hype_phrases(analysis.real_world_impact)

    # 2. Ensure limitations has at least one realistic entry
    if hasattr(analysis, "limitations"):
        if not analysis.limitations:
            analysis.limitations = [
                "Chưa kiểm chứng độc lập hiệu năng và độ ổn định trên môi trường thực tế [S1]."
            ]

    # 3. Ensure research_gaps has at least one entry
    if hasattr(analysis, "research_gaps"):
        if not analysis.research_gaps:
            analysis.research_gaps = [
                "Cần chạy thử nghiệm mẫu để xác minh các tuyên bố về hiệu suất và tính tương thích."
            ]

    # 4. Compute Grounding Score & Self-Critique
    score, critique = evaluate_grounding(analysis)
    if hasattr(analysis, "grounding_score"):
        analysis.grounding_score = score
    if hasattr(analysis, "grounding_critique"):
        analysis.grounding_critique = critique

    return analysis
