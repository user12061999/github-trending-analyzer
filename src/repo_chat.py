"""Interactive Repo Q&A / Chat module for GitHub Trending Analyzer.

Allows developers to ask deep technical questions about any trending repository,
answered via Gemini AI with citation grounding or through heuristic semantic
document retrieval with zero external dependencies.
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from src.fetcher import fetch_repo_readme
from src.grounding import soften_hype_phrases


def get_repo_context_from_db(full_name: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve existing analysis snapshot from SQLite history."""
    try:
        from src.history_db import get_connection
        conn = get_connection(db_path)
        try:
            row = conn.execute("""
                SELECT analysis_json FROM repo_snapshots
                WHERE full_name = ?
                ORDER BY captured_at DESC LIMIT 1
            """, (full_name,)).fetchone()
            if row and row["analysis_json"]:
                return json.loads(row["analysis_json"])
        finally:
            conn.close()
    except Exception:
        pass
    return None


def heuristic_search_answer(
    full_name: str,
    question: str,
    analysis_dict: Optional[Dict[str, Any]] = None,
    readme_text: Optional[str] = None
) -> Tuple[str, List[Dict[str, str]]]:
    """Provide a grounded answer using semantic keyword matching and document extraction."""
    q_lower = question.lower()
    sources = []
    paragraphs = []

    # 1. Intent Analysis
    is_offline_req = any(w in q_lower for w in ["offline", "local", "cục bộ", "mạng", "gpu", "phần cứng", "hardware", "yêu cầu", "cấu hình", "hệ điều hành", "os", "windows", "linux", "mac"])
    is_comparison = any(w in q_lower for w in ["so sánh", "so voi", "khác gì", "thay thế", "alternative", "hơn gì", "kém gì", "vs", "compare"])
    is_architecture = any(w in q_lower for w in ["cơ chế", "hoạt động", "luồng", "kiến trúc", "how it works", "architecture", "nguyên lý"])
    is_install = any(w in q_lower for w in ["cài đặt", "chạy thử", "lệnh", "install", "quick run", "bắt đầu", "setup"])
    is_license = any(w in q_lower for w in ["license", "bản quyền", "thương mại", "commercial", "agpl", "mit", "apache"])

    if analysis_dict:
        # Check specific fields
        if is_offline_req and analysis_dict.get("adoption_notes"):
            notes = " ".join(analysis_dict["adoption_notes"])
            paragraphs.append(f"**Yêu cầu môi trường & Cấu hình:** {notes}")
            sources.append({"id": "[S1]", "title": "adoption_notes"})

        if is_comparison:
            if analysis_dict.get("commercial_alternative"):
                paragraphs.append(f"**Định vị thay thế:** Dự án được định vị là giải pháp thay thế mã nguồn mở cho **{analysis_dict['commercial_alternative']}**.")
            if analysis_dict.get("comparisons"):
                paragraphs.append("**So sánh kỹ thuật:** " + " ".join(analysis_dict["comparisons"]))
            sources.append({"id": "[S1]", "title": "comparisons"})

        if is_architecture and analysis_dict.get("how_it_works"):
            paragraphs.append("**Cơ chế hoạt động:** " + " ".join(analysis_dict["how_it_works"]))
            sources.append({"id": "[S1]", "title": "how_it_works"})

        if is_install and analysis_dict.get("quick_run"):
            paragraphs.append(f"**Lệnh cài đặt / chạy nhanh:** `{analysis_dict['quick_run']}`")
            sources.append({"id": "[S1]", "title": "quick_run"})

        if analysis_dict.get("limitations"):
            paragraphs.append("**Giới hạn cần lưu ý:** " + " ".join(analysis_dict["limitations"]))
            sources.append({"id": "[S1]", "title": "limitations"})

    # If specific paragraphs found, format coherent answer
    if paragraphs:
        answer = "\n\n".join(paragraphs)
        return answer, sources

    # Fallback to searching README if available
    if readme_text:
        keywords = [w for w in re.split(r"\s+", q_lower) if len(w) >= 3 and w not in ("cho", "với", "như", "nào", "được", "không", "những", "trong", "dự", "án")]
        matched_lines = []
        for line in readme_text.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            matches = sum(1 for kw in keywords if kw in line_str.lower())
            if matches >= 1:
                matched_lines.append((matches, line_str))

        if matched_lines:
            matched_lines.sort(key=lambda x: -x[0])
            best_excerpts = [line for _, line in matched_lines[:3]]
            sources.append({"id": "[README]", "title": "README.md"})
            answer = "Dựa trên tài liệu README của dự án:\n\n" + "\n\n".join(f"- {exc}" for exc in best_excerpts)
            return answer, sources

    # General default summary fallback
    if analysis_dict:
        core = analysis_dict.get("core_purpose", "")
        verdict = analysis_dict.get("quick_verdict", "")
        return (
            f"**Tác dụng cốt lõi của {full_name}:** {core}\n\n"
            f"**Đánh giá tổng quan:** {verdict}\n\n"
            "*(Lưu ý: Câu hỏi cụ thể của bạn chưa tìm thấy trực tiếp trong các mục trích xuất tài liệu. Bật `--ai` để có câu trả lời sâu hơn).* ",
            [{"id": "[S1]", "title": "core_purpose"}]
        )

    return ("Chưa có đủ tài liệu hoặc dữ liệu phân tích cho repository này. Hãy đảm bảo repository có README hoặc thử tải lại.", [])


def ask_repo_ai(
    full_name: str,
    question: str,
    context_text: str,
    gemini_api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Optional[Tuple[str, List[Dict[str, str]]]]:
    """Ask Gemini a targeted technical question regarding a repository."""
    key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        return None

    model = model or os.environ.get("GEMINI_MODEL") or "gemini-3.1-flash-lite"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{urllib.parse.quote(model, safe='')}:generateContent"

    system_prompt = (
        f"Bạn là chuyên gia tư vấn kỹ thuật mã nguồn mở cấp cao. "
        f"Người dùng đang đặt câu hỏi kỹ thuật về repository '{full_name}'.\n"
        f"Hãy trả lời bằng tiếng Việt dựa TRỰC TIẾP trên ngữ cảnh tài liệu dự án được cung cấp dưới đây.\n"
        f"Nguyên tắc cốt lõi:\n"
        f"1. Khách quan, trung thực; trích dẫn nguồn ID [S1], [S2] hoặc section tài liệu khi nêu chi tiết kỹ thuật.\n"
        f"2. Phân biệt rõ ràng giữa tuyên bố của tác giả với kiểm chứng thực tế.\n"
        f"3. Nếu tài liệu không nhắc đến hoặc chưa có thông tin, hãy trả lời thẳng thắn là 'Tài liệu chưa cung cấp thông tin này' thay vì tự suy đoán.\n"
        f"4. Súc tích, thực dụng, đi thẳng vào câu trả lời có cấu trúc rõ ràng."
    )

    user_prompt = f"""Ngữ cảnh tài liệu về dự án '{full_name}':
\"\"\"
{context_text[:12000]}
\"\"\"

Câu hỏi của lập trình viên:
{question}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\n{user_prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
        }
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json", "x-goog-api-key": key},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode("utf-8")
            result = json.loads(body)
            answer = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            answer = soften_hype_phrases(answer)
            return answer, [{"id": "[AI]", "title": f"Gemini ({model})"}]
    except Exception as exc:
        print(f"⚠️ Repo Q&A AI không hoàn thành ({type(exc).__name__}), chuyển sang trích xuất heuristic.", file=sys.stderr)
        return None


def ask_repo(
    full_name: str,
    question: str,
    use_ai: bool = False,
    gemini_api_key: Optional[str] = None,
    model: Optional[str] = None,
    db_path: Optional[str] = None,
    cached_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Main Q&A interface for a repository."""
    # 1. Fetch analysis from memory/DB or argument
    analysis = cached_analysis or get_repo_context_from_db(full_name, db_path=db_path)

    # 2. Fetch README if available
    owner, repo_name = full_name.split("/") if "/" in full_name else ("", full_name)
    readme_text = fetch_repo_readme(owner, repo_name, use_cache=True) if owner else None

    # 3. Assemble context
    context_parts = []
    if analysis:
        context_parts.append(f"Mô tả: {analysis.get('description', '')}")
        context_parts.append(f"Tác dụng cốt lõi: {analysis.get('core_purpose', '')}")
        if analysis.get("key_features"):
            context_parts.append("Tính năng: " + "; ".join(analysis["key_features"]))
        if analysis.get("how_it_works"):
            context_parts.append("Cách hoạt động: " + "; ".join(analysis["how_it_works"]))
        if analysis.get("adoption_notes"):
            context_parts.append("Yêu cầu triển khai: " + "; ".join(analysis["adoption_notes"]))
        if analysis.get("limitations"):
            context_parts.append("Giới hạn: " + "; ".join(analysis["limitations"]))
        if analysis.get("comparisons"):
            context_parts.append("So sánh: " + "; ".join(analysis["comparisons"]))
        if analysis.get("commercial_alternative"):
            context_parts.append(f"Thay thế thương mại: {analysis['commercial_alternative']}")
        if analysis.get("quick_run"):
            context_parts.append(f"Lệnh chạy thử: {analysis['quick_run']}")

    if readme_text:
        context_parts.append(f"Nội dung README:\n{readme_text[:6000]}")

    full_context = "\n\n".join(context_parts)

    # 4. Resolve via AI or Heuristic
    answer_text = None
    sources = []
    engine = "heuristic"

    if use_ai:
        ai_res = ask_repo_ai(
            full_name=full_name,
            question=question,
            context_text=full_context,
            gemini_api_key=gemini_api_key,
            model=model,
        )
        if ai_res:
            answer_text, sources = ai_res
            engine = f"ai (gemini: {model or 'flash-lite'})"

    if not answer_text:
        answer_text, sources = heuristic_search_answer(
            full_name=full_name,
            question=question,
            analysis_dict=analysis,
            readme_text=readme_text,
        )

    return {
        "full_name": full_name,
        "question": question,
        "answer": answer_text,
        "sources": sources,
        "engine_used": engine,
    }
