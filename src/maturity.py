"""Maturity Evaluation, Tech Stack Extraction, Quick Run & Velocity Detection.

Provides:
1. Velocity Score & Breakout Star detection based on star trajectory.
2. Maturity rating (Production Ready 🟢 / Beta 🟡 / Experimental 🟠).
3. Underlying tech stack extraction.
4. One-line quick run/install command detection from README.
"""

import re
from typing import List, Optional, Tuple


def parse_star_count(val: Optional[str]) -> int:
    """Parse star string like '12,450', '3.5k', '1.2M' into integer."""
    if not val:
        return 0
    clean = str(val).strip().replace(",", "").replace("+", "").replace(" ", "")
    if not clean:
        return 0
    try:
        if clean.lower().endswith("k"):
            return int(float(clean[:-1]) * 1000)
        if clean.lower().endswith("m"):
            return int(float(clean[:-1]) * 1000000)
        return int(float(clean))
    except (ValueError, TypeError):
        return 0


def calculate_velocity(stars_since_str: str, stars_total_str: str) -> Tuple[float, str, str]:
    """Calculate velocity growth rate and classify repo into velocity tiers.

    Returns:
        (growth_rate_pct, label, badge)
    """
    since = parse_star_count(stars_since_str)
    total = parse_star_count(stars_total_str)

    if total <= 0:
        return 0.0, "📈 TĂNG TRƯỞNG ỔN ĐỊNH", "📈 Steady"

    rate_pct = round((since / total) * 100, 2)

    # 1. Breakout Star: New or low total stars (< 3000) with rapid influx
    if (total < 3000 and since >= 150) or (rate_pct >= 10.0 and since >= 100):
        label = "🔥 MỚI NỔI & CỰC HOT"
        badge = f"🔥 Breakout Star (+{rate_pct}%)"
        return rate_pct, label, badge

    # 2. High Velocity: High daily addition or > 5% growth
    if rate_pct >= 5.0 or since >= 350:
        label = "⚡ TĂNG TRƯỞNG THẦN TỐC"
        badge = f"⚡ High Velocity (+{rate_pct}%)"
        return rate_pct, label, badge

    # 3. Established Giant: Big repository (> 25k stars) with steady trending
    if total >= 25000 and rate_pct < 3.0:
        label = "🏛️ DỰ ÁN KINH ĐIỂN"
        badge = f"🏛️ Established ({total//1000}k★)"
        return rate_pct, label, badge

    # 4. Steady
    label = "📈 TĂNG TRƯỞNG ỔN ĐỊNH"
    badge = f"📈 Steady (+{rate_pct}%)"
    return rate_pct, label, badge


# Common tech stack signatures to detect in README or description
TECH_STACK_SIGNATURES = {
    # AI / ML
    "PyTorch": [r"\bpytorch\b", r"\btorch\b"],
    "TensorFlow": [r"\btensorflow\b"],
    "Transformers": [r"\btransformers\b", r"\bhuggingface\b"],
    "LangChain": [r"\blangchain\b"],
    "LlamaIndex": [r"\bllamaindex\b"],
    "Ollama": [r"\bollama\b"],
    "vLLM": [r"\bvllm\b"],
    "CUDA": [r"\bcuda\b", r"\bnvidia\b"],
    "ONNX": [r"\bonnx\b"],
    # Backend & Web
    "FastAPI": [r"\bfastapi\b"],
    "Next.js": [r"\bnext\.?js\b"],
    "React": [r"\breact\b", r"\breactjs\b"],
    "Vue": [r"\bvue\.?js\b", r"\bvue\b"],
    "Svelte": [r"\bsvelte\b"],
    "Tailwind": [r"\btailwind\b", r"\btailwindcss\b"],
    "Tokio": [r"\btokio\b"],
    "Express": [r"\bexpress\.?js\b"],
    # Infra & DB
    "Docker": [r"\bdocker\b", r"\bdocker-compose\b", r"\bdockerfile\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "PostgreSQL": [r"\bpostgres\b", r"\bpostgresql\b"],
    "SQLite": [r"\bsqlite\b"],
    "Redis": [r"\bredis\b"],
    "DuckDB": [r"\bduckdb\b"],
    "Qdrant": [r"\bqdrant\b"],
    "Chroma": [r"\bchromadb\b", r"\bchroma\b"],
    "Milvus": [r"\bmilvus\b"],
    # Client / Native
    "WebAssembly": [r"\bwebassembly\b", r"\bwasm\b"],
    "Electron": [r"\belectron\b"],
    "Tauri": [r"\btauri\b"],
}


def extract_tech_stack(corpus: str) -> List[str]:
    """Extract recognized technologies and frameworks from README/description."""
    if not corpus:
        return []
    corpus_lower = corpus.lower()
    detected = []
    for tech, patterns in TECH_STACK_SIGNATURES.items():
        for pat in patterns:
            if re.search(pat, corpus_lower):
                detected.append(tech)
                break
    return detected[:6]


def evaluate_maturity(
    name: str,
    description: str,
    readme_raw: Optional[str] = None,
    stars_total_str: str = "0",
    repo_type: str = "tool_app",
) -> Tuple[str, str]:
    """Evaluate project maturity into Production Ready, Beta, Experimental, or Educational.

    Returns:
        (maturity_level, maturity_badge)
        Levels: 'production', 'beta', 'experimental', 'comprehensive', 'active_dev'
    """
    # 0. Specialized evaluation for non-software repositories
    if repo_type == "course_tutorial":
        readme = (readme_raw or "").lower()
        if any(w in readme for w in ("syllabus", "table of contents", "chapter", "lecture", "assignment", "curriculum")) or parse_star_count(stars_total_str) >= 500:
            return "comprehensive", "📚 Giáo trình hoàn chỉnh"
        return "active_dev", "🟡 Đang cập nhật tài liệu"

    if repo_type == "awesome_list":
        return "comprehensive", "📋 Danh mục chọn lọc"

    if repo_type == "dataset_benchmark":
        return "comprehensive", "📊 Dataset / Benchmark hoàn chỉnh"

    total_stars = parse_star_count(stars_total_str)
    readme = (readme_raw or "").lower()
    desc = (description or "").lower()
    full_text = f"{desc}\n{readme[:4000]}"

    # 1. Experimental check (explicit markers)
    experimental_keywords = [
        "proof of concept", "poc", "experimental", "toy project", "demo only",
        "research prototype", "work in progress", "wip", "not ready for production",
        "early preview", "pre-alpha", "for research purposes only"
    ]
    for exp_kw in experimental_keywords:
        if exp_kw in full_text:
            return "experimental", "🟠 Experimental / Prototype"

    # 2. Production Ready check
    score = 0
    # CI/CD & Tests
    if re.search(r"actions/workflows|circleci|travis-ci|codecov|badge\.svg", readme):
        score += 2
    if re.search(r"\btests?\b|pytest|npm test|cargo test|go test|benchmark", readme):
        score += 2

    # Docker / Deployment ready
    if re.search(r"docker run|docker-compose|helm|kubernetes|k8s|deploy", readme):
        score += 2

    # Package distribution (pip, npm, cargo, brew)
    if re.search(r"pip install|npm install|cargo install|brew install|go install", readme):
        score += 2

    # License
    if re.search(r"license|apache 2\.0|mit license|bsd", readme):
        score += 1

    # Community & Documentation
    if re.search(r"documentation|docs\.|readthedocs|contributing\.md|api reference", readme):
        score += 2

    # High star baseline
    if total_stars >= 5000:
        score += 2
    elif total_stars >= 2000:
        score += 1

    if score >= 6:
        return "production", "🟢 Production Ready"
    elif score >= 3:
        return "beta", "🟡 Beta / Active Dev"
    else:
        return "experimental", "🟠 Experimental / Prototype"


def extract_quick_run(
    readme_raw: Optional[str] = None,
    language: str = "",
    repo_type: str = "tool_app",
) -> Optional[str]:
    """Detect and extract a one-liner quick run / installation command from README."""
    if not readme_raw or repo_type in ("course_tutorial", "awesome_list", "dataset_benchmark"):
        return None

    # Prefer installation/quick-start sections. Keep exact arguments and versions.
    from src.research import sections
    parts = sections(readme_raw)
    preferred = [(title, body) for title, body in parts if any(word in title.lower() for word in
                 ("install", "quickstart", "quick start", "getting started", "setup"))]
    candidates = preferred or parts
    command_start = re.compile(r"^(?:docker run|docker compose up|docker-compose up|pip install|pip3 install|uv pip install|npx|npm install|pnpm add|cargo install|brew install|go install|curl)\s+\S", re.I)
    for _, body in candidates:
        for line in body.splitlines():
            command = line.strip()
            if command.startswith("$ "):
                command = command[2:]
            if command.startswith("`") and command.endswith("`"):
                command = command.strip("`")
            # Inline installation instructions: extract the complete backtick command.
            inline = re.findall(r"`([^`\n]+)`", command)
            for value in inline or [command]:
                if command_start.match(value) and len(value) <= 500 and not value.endswith("\\") and "..." not in value:
                    return value
    return None
