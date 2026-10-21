"""Dynamic Few-Shot Learning module for GitHub Trending Analyzer.

Selects context-aware exemplars from SQLite historical memory (user-liked repos)
or falls back to high-quality curated benchmarks based on RESEARCH_SAMPLE_VI.md.
"""

import json
from typing import Any, Dict, List, Optional, Tuple


CURATED_EXEMPLARS: Dict[str, Dict[str, Any]] = {
    "tool_app": {
        "name": "NVIDIA/OpenShell",
        "language": "Rust",
        "category": "AI & Machine Learning",
        "repo_type": "tool_app",
        "description": "Kernel-level execution runtime and security sandbox for autonomous coding agents.",
        "core_purpose": "Cung cấp runtime sandbox cách ly môi trường thực thi cho coding agent, kiểm soát quyền truy cập file, system call và kết nối mạng ở tầng kernel thay vì chỉ dựa vào câu lệnh prompt.",
        "key_features": [
            "Sandbox kernel cách ly hệ thống: giới hạn quyền đọc/ghi file và system call cho agent [S1], how-it-works",
            "Credential Proxy: runtime tự bổ sung token khi gửi request tới endpoint được duyệt, không cấp credentials trực tiếp cho model [S1], how-it-works",
            "Formal Verification cho policy: kiểm tra quyền hạn khi có thay đổi cấu hình bảo mật trước khi mở endpoint [S1], how-it-works",
            "Tương thích Docker, Podman và Linux virtualization [S1], quickstart",
        ],
        "target_audience": "AI Engineer, Platform Engineer và Security Architect đang triển khai autonomous coding agent cần kiểm soát rủi ro an toàn hệ thống.",
        "use_cases": [
            "Chạy coding agent tự động sửa bug trong repo mà không sợ agent đọc trộm file nhạy cảm ngoài workspace.",
            "Kiểm soát lưu lượng mạng của agent, chặn các request gửi dữ liệu nội bộ ra server lạ.",
        ],
        "why_trending": "Nhu cầu cấp thiết về an toàn khi giao quyền cho autonomous agent (Agentic AI) thao tác trực tiếp trên shell.",
        "quick_verdict": "Đáng thử nghiệm trong môi trường dev cô lập để đánh giá cơ chế policy; chưa khuyến nghị đưa ngay vào production nếu chưa có benchmark kiểm thử vượt sandbox độc lập.",
        "suitable_major": "Khoa học Máy tính / An toàn Thông tin (chuyên sâu về virtualization và OS security).",
        "target_roles": "DevSecOps, Platform Engineer, AI Security Researcher.",
        "real_world_impact": "Chuyển đổi từ mô hình phó mặc bảo mật cho prompt sang cơ chế kiểm soát cứng ở tầng hệ điều hành; giảm thiểu rủi ro prompt injection dẫn đến command injection.",
        "how_it_works": [
            "Agent thực thi trong container Ubuntu tối giản; các system call bị chặn hoặc điều hướng qua filter kernel [S1], how-it-works.",
            "Khi agent gọi mạng, runtime đối chiếu URL với policy danh sách trắng trước khi gán credential thực và forward request [S1], how-it-works.",
            "Các thay đổi quyền nhạy cảm yêu cầu duyệt (human-in-the-loop) hoặc vượt qua kiểm chứng hình thức (formal verification) [S1], how-it-works.",
        ],
        "practical_examples": [
            "Đề xuất thử nghiệm: Cấu hình sandbox cho agent chỉ đọc thư mục /src, gọi API model chỉ định; kiểm tra 3 ca: thao tác hợp lệ thành công, cố đọc /etc/passwd bị từ chối, và cố gọi server ngoài bị chặn.",
            "Tiêu chí đo lường: Tỷ lệ hoàn thành tác vụ không bị cản trở, độ trễ do lớp runtime tạo ra, và tính chi tiết của nhật ký audit log.",
        ],
        "limitations": [
            "Chưa có báo cáo kiểm thử bảo mật độc lập xác nhận khả năng chống bypass sandbox hoàn toàn [S1], readme.",
            "Chi phí vận hành và cấu hình môi trường lớn, không phù hợp cho các script đơn giản đã cô lập sẵn.",
        ],
        "adoption_notes": [
            "Yêu cầu hệ điều hành: Linux, macOS Apple Silicon hoặc Windows WSL 2 (thử nghiệm) [S1], quickstart.",
            "Cần Docker hoặc Podman; sandbox mặc định là Ubuntu tối giản chưa có sẵn runtime cho agent [S1], quickstart.",
        ],
        "comparisons": [
            "Khác với gVisor hay Docker thuần: OpenShell tích hợp sẵn credential proxy và cơ chế verification hướng riêng cho AI agent [S1], how-it-works.",
        ],
        "research_gaps": [
            "Chưa rõ mức độ tiêu hao tài nguyên (CPU/RAM overhead) khi chạy hàng loạt agent đồng thời.",
            "Chưa xác định độ tương thích với các framework agent phổ biến như LangChain, CrewAI.",
        ],
    },
    "multimedia_app": {
        "name": "debpalash/VoiceStudio",
        "language": "TypeScript",
        "category": "Audio & Speech",
        "repo_type": "tool_app",
        "description": "All-in-one local voice cloning, TTS and audio workstation app with local API and MCP support.",
        "core_purpose": "Ứng dụng desktop gom các tác vụ tạo, xử lý và clone giọng nói AI chạy hoàn toàn local trên máy cá nhân, định vị là giải pháp thay thế cục bộ cho ElevenLabs.",
        "key_features": [
            "Xử lý giọng nói đa tác vụ: Clone voice, design voice, lồng tiếng video, chuyển văn bản thành audio (TTS), audiobook [S1], feature-catalog",
            "Hỗ trợ đa engine cục bộ: Mặc định dựa trên OmniVoice, cho phép tích hợp các model khác [S1], readme",
            "Cung cấp Local API và MCP Server: Cho phép AI agent bên ngoài kết nối và kích hoạt pipeline xử lý giọng [S1], readme",
            "Giao diện Desktop hiện đại xây dựng trên Electron [S1], readme",
        ],
        "target_audience": "Game Developer, Content Creator, Podcaster, hoặc kỹ sư AI muốn tự động hóa tạo thoại mà không phụ thuộc cloud API.",
        "use_cases": [
            "Tạo voiceover mẫu cho nhân vật game hoặc lồng tiếng video ngắn mà không tốn phí bản quyền ElevenLabs.",
            "Tích hợp làm voice generation tool trong workflow tự động qua MCP server.",
        ],
        "why_trending": "Được cộng đồng quan tâm mạnh mẽ nhờ tính năng clone giọng local và cung cấp MCP server đón đầu làn sóng AI agent.",
        "quick_verdict": "Đáng đưa vào danh sách thử nghiệm workflow nội bộ; quyết định triển khai cần dựa trên chất lượng audio thực tế sinh ra trên đúng phần cứng và ngôn ngữ mục tiêu.",
        "suitable_major": "Kỹ thuật Phần mềm / Công nghệ Đa phương tiện (Game & Audio Engineering).",
        "target_roles": "Game Sound Designer, Video Editor, Automation Engineer.",
        "real_world_impact": "Loại bỏ chi phí token tính theo ký tự của cloud TTS thương mại; bảo vệ quyền riêng tư dữ liệu âm thanh độc quyền.",
        "how_it_works": [
            "Người dùng cung cấp mẫu audio tham chiếu hoặc chọn preset; engine OmniVoice trích xuất voice embedding và tổng hợp phổ âm thanh [S1], feature-catalog.",
            "Giao diện Electron giao tiếp với backend Python/Rust qua IPC hoặc local HTTP/MCP API [S1], readme.",
        ],
        "practical_examples": [
            "Đề xuất thử nghiệm: Thu âm 10 giây mẫu giọng tiếng Việt chuẩn, tổng hợp một đoạn thoại nhân vật game 100 từ; đánh giá độ tự nhiên, ngữ điệu tên riêng và thời gian render trên GPU local.",
        ],
        "limitations": [
            "Định vị 'thay thế ElevenLabs' là tuyên bố của tác giả, chưa có kiểm chứng độc lập về chất lượng âm sắc và độ cảm xúc tương đương [S1], readme.",
            "Yêu cầu cấu hình phần cứng GPU đáng kể để đạt tốc độ thời gian thực (real-time).",
        ],
        "adoption_notes": [
            "Bản phát hành sẵn dùng Electron; build từ source yêu cầu chuỗi công cụ phức tạp (Node.js, Bun, Rust/Cargo, Git) [S1], install/script.",
            "Lưu ý bản quyền: Phần mềm dùng AGPL-3.0 nhưng các model AI đi kèm có thể có license thương mại riêng biệt [S1], license-notice.",
        ],
        "comparisons": [
            "So với ElevenLabs Cloud API: Giữ toàn bộ dữ liệu trên máy và miễn phí bản quyền sử dụng, nhưng đánh đổi bằng yêu cầu GPU và chất lượng phụ thuộc model open-weight [S1], readme.",
        ],
        "research_gaps": [
            "Chưa có thông số benchmark cụ thể về chất lượng phát âm tiếng Việt có dấu.",
            "Chưa có tài liệu xác nhận khả năng tích hợp trực tiếp bằng plugin native vào Unity/Unreal Engine.",
        ],
    },
    "library_sdk": {
        "name": "astral-sh/uv",
        "language": "Rust",
        "category": "Developer Tooling & CLI",
        "repo_type": "library_sdk",
        "description": "An extremely fast Python package and project manager, written in Rust.",
        "core_purpose": "Trình quản lý gói và môi trường ảo Python tốc độ cao viết bằng Rust, thay thế pip, pip-tools và virtualenv với hiệu năng nhanh hơn từ 10-100 lần.",
        "key_features": [
            "Tốc độ cài đặt vượt trội: tận dụng Rust, multithreading và global cache chia sẻ [S1], features",
            "Quản lý Python toolchains: tự động tải và quản lý các phiên bản Python [S1], usage",
            "Khả năng tương thích cao: hỗ trợ định dạng pyproject.toml tiêu chuẩn và lockfile nhất quán [S1], readme",
        ],
        "target_audience": "Lập trình viên Python, Data Scientist và kỹ sư DevOps cần tăng tốc pipeline CI/CD và setup môi trường dev.",
        "use_cases": [
            "Rút ngắn thời gian build Docker image và chạy CI/CD từ vài phút xuống vài giây.",
            "Quản lý nhiều phiên bản Python trên máy cá nhân mà không cần pyenv.",
        ],
        "why_trending": "Giải quyết triệt để vấn đề muôn thuở về tốc độ chậm của hệ sinh thái packaging Python.",
        "quick_verdict": "Cực kỳ khuyến nghị áp dụng ngay cho môi trường dev và CI/CD nhờ tốc độ đột phá và độ ổn định cao.",
        "suitable_major": "Khoa học Máy tính / Kỹ thuật Phần mềm.",
        "target_roles": "Python Developer, DevOps Engineer, Backend Engineer.",
        "real_world_impact": "Tiết kiệm hàng trăm giờ chạy build CI/CD trên toàn đội ngũ kỹ thuật; chuẩn hóa lockfile reproducible.",
        "how_it_works": [
            "Giải quyết dependency resolution bằng thuật toán PubGrub viết bằng Rust [S1], architecture.",
            "Tải và link trực tiếp các package wheel vào virtual environment bằng hardlink hoặc reflink trên filesystem [S1], performance.",
        ],
        "practical_examples": [
            "Thử nghiệm CI/CD: Chuyển đổi lệnh `pip install -r requirements.txt` sang `uv pip install -r requirements.txt`; đo lường thời gian chạy trung bình 5 lần liên tiếp.",
        ],
        "limitations": [
            "Một số package C-extension legacy chưa có pre-built wheel có thể vẫn yêu cầu build toolchain cục bộ [S1], limitations.",
        ],
        "adoption_notes": [
            "Cài đặt độc lập qua curl script, cargo, hoặc standalone binary [S1], install.",
            "Tương thích Windows, macOS và Linux [S1], platform.",
        ],
        "comparisons": [
            "So với pip/poetry: uv nhanh hơn rõ rệt nhờ cơ chế cache và Rust engine, hỗ trợ drop-in replacement cho hầu hết lệnh pip thông dụng [S1], benchmarks.",
        ],
        "research_gaps": [
            "Kiểm thử khả năng tương thích với private PyPI repository phức tạp sử dụng token luân phiên.",
        ],
    },
}


def _build_exemplar_from_data(data: Dict[str, Any], full_name: str, category: str) -> Dict[str, Any]:
    """Helper to build standard exemplar dictionary from analysis JSON data."""
    return {
        "name": data.get("name") or full_name,
        "language": data.get("language", ""),
        "category": data.get("category", category),
        "repo_type": data.get("repo_type", "tool_app"),
        "description": data.get("description", ""),
        "core_purpose": data.get("core_purpose", ""),
        "key_features": data.get("key_features", []),
        "target_audience": data.get("target_audience", ""),
        "use_cases": data.get("use_cases", []),
        "why_trending": data.get("why_trending", ""),
        "quick_verdict": data.get("quick_verdict", ""),
        "suitable_major": data.get("suitable_major", ""),
        "target_roles": data.get("target_roles", ""),
        "real_world_impact": data.get("real_world_impact", ""),
        "how_it_works": data.get("how_it_works", []),
        "practical_examples": data.get("practical_examples", []),
        "limitations": data.get("limitations", []),
        "adoption_notes": data.get("adoption_notes", []),
        "comparisons": data.get("comparisons", []),
        "research_gaps": data.get("research_gaps", []),
    }


def find_liked_exemplar_from_db(
    category: str = "",
    repo_type: str = "",
    db_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Query SQLite historical memory for a user-liked repository analysis snapshot."""
    try:
        from src.history_db import get_connection
        conn = get_connection(db_path)
    except Exception:
        return None

    try:
        # Match user-liked repos (rating == 1) prioritizing category
        rows = conn.execute("""
            SELECT s.full_name, s.category, s.analysis_json, f.rating
            FROM repo_feedback f
            JOIN repo_snapshots s ON f.full_name = s.full_name
            WHERE f.rating = 1 AND s.analysis_json IS NOT NULL
            ORDER BY
                (s.category = ?) DESC,
                s.captured_at DESC
            LIMIT 10
        """, (category or "",)).fetchall()

        if not rows:
            return None

        candidates = []
        for row in rows:
            try:
                data = json.loads(row["analysis_json"])
                if isinstance(data, dict) and data.get("core_purpose"):
                    candidates.append((data, row["full_name"], row["category"]))
            except Exception:
                continue

        if not candidates:
            return None

        # Prioritize matching repo_type if requested
        if repo_type:
            for data, full_name, cat in candidates:
                if data.get("repo_type") == repo_type:
                    return _build_exemplar_from_data(data, full_name, cat)

        # Fallback to top candidate (which matched category)
        data, full_name, cat = candidates[0]
        return _build_exemplar_from_data(data, full_name, cat)
    except Exception:
        return None
    finally:
        conn.close()


def get_few_shot_exemplar(
    category: str = "",
    repo_type: str = "",
    db_path: Optional[str] = None
) -> Tuple[Dict[str, Any], str]:
    """Retrieve best matching exemplar: from DB (user-liked) or curated benchmark fallback."""
    # 1. Try DB lookup
    liked = find_liked_exemplar_from_db(category=category, repo_type=repo_type, db_path=db_path)
    if liked:
        return liked, f"sqlite (user-liked: {liked.get('name')})"

    # 2. Curated fallback based on repo_type and category
    cat_lower = (category or "").lower()
    if "audio" in cat_lower or "voice" in cat_lower or "speech" in cat_lower or "multimedia" in cat_lower:
        return CURATED_EXEMPLARS["multimedia_app"], "curated (debpalash/VoiceStudio)"

    if repo_type == "library_sdk":
        return CURATED_EXEMPLARS["library_sdk"], "curated (astral-sh/uv)"

    return CURATED_EXEMPLARS["tool_app"], "curated (NVIDIA/OpenShell)"


def format_few_shot_prompt(exemplar: Dict[str, Any], source_origin: str) -> str:
    """Format exemplar into a concise instruction block for the LLM prompt."""
    exemplar_output = {
        "category": exemplar.get("category", ""),
        "core_purpose": exemplar.get("core_purpose", ""),
        "key_features": exemplar.get("key_features", [])[:4],
        "target_audience": exemplar.get("target_audience", ""),
        "use_cases": exemplar.get("use_cases", [])[:2],
        "why_trending": exemplar.get("why_trending", ""),
        "quick_verdict": exemplar.get("quick_verdict", ""),
        "suitable_major": exemplar.get("suitable_major", ""),
        "target_roles": exemplar.get("target_roles", ""),
        "real_world_impact": exemplar.get("real_world_impact", ""),
        "how_it_works": exemplar.get("how_it_works", [])[:3],
        "practical_examples": exemplar.get("practical_examples", [])[:2],
        "limitations": exemplar.get("limitations", [])[:2],
        "adoption_notes": exemplar.get("adoption_notes", [])[:2],
        "comparisons": exemplar.get("comparisons", [])[:1],
        "research_gaps": exemplar.get("research_gaps", [])[:2],
    }

    exemplar_json = json.dumps(exemplar_output, ensure_ascii=False, indent=2)

    return f"""--- VÍ DỤ PHÂN TÍCH CHUẨN MẪU (FEW-SHOT BENCHMARK: {source_origin}) ---
[Đầu vào mẫu]:
Dự án: {exemplar.get('name')} | Ngôn ngữ: {exemplar.get('language')}
Mô tả từ GitHub: {exemplar.get('description')}

[Đầu ra JSON chuẩn mực]:
{exemplar_json}
--- HẾT VÍ DỤ CHUẨN MẪU ---
"""
