"""Repository Type Taxonomy & Classification Module (Python stdlib).

Classifies repositories into distinct architectural and functional types:
- tool_app: Standalone software, CLI utilities, desktop/web apps, server daemons
- library_sdk: Code libraries, frameworks, SDKs meant to be imported into other projects
- ai_model: Model weights, checkpoints, LoRA, GGUF/safetensors
- course_tutorial: University courses, tutorials, educational books, lecture notes
- awesome_list: Curated resource collections, awesome lists, link directories
- dataset_benchmark: Datasets, evaluation suites, benchmarks
"""

import re
from typing import Dict, Optional, Tuple

REPO_TYPES: Dict[str, Dict[str, str]] = {
    "tool_app": {
        "label": "Công cụ / Ứng dụng",
        "badge": "🛠️ Tool / App",
        "description": "Phần mềm độc lập, CLI tool, ứng dụng web/desktop hoặc server.",
    },
    "library_sdk": {
        "label": "Thư viện / SDK",
        "badge": "📦 Library / SDK",
        "description": "Thư viện lập trình, SDK, package để tích hợp vào dự án khác.",
    },
    "ai_model": {
        "label": "Mô hình / Trọng số AI",
        "badge": "🧠 AI Model / Weights",
        "description": "Checkpoint, trọng số mô hình AI, file GGUF, SafeTensors hoặc LoRA.",
    },
    "course_tutorial": {
        "label": "Khóa học / Giáo trình",
        "badge": "📚 Khóa học / Tài liệu",
        "description": "Giáo trình đại học, bài giảng, tutorial hướng dẫn từng bước hoặc sách.",
    },
    "awesome_list": {
        "label": "Danh mục tài nguyên",
        "badge": "📋 Awesome List",
        "description": "Bộ sưu tập tài nguyên, danh sách link chọn lọc hoặc cheat sheet.",
    },
    "dataset_benchmark": {
        "label": "Dữ liệu / Benchmark",
        "badge": "📊 Dataset / Benchmark",
        "description": "Tập dữ liệu huấn luyện hoặc bộ benchmark đánh giá hiệu năng/mô hình.",
    },
}


def detect_repo_type(
    name: str,
    description: str = "",
    readme_raw: Optional[str] = None,
    language: str = "",
) -> Tuple[str, str]:
    """Detect the repository type from name, description, and README corpus.

    Returns:
        (type_key, type_badge)
        e.g. ('course_tutorial', '📚 Khóa học / Tài liệu')
    """
    clean_name = (name or "").lower()
    clean_desc = (description or "").lower()
    readme_preview = (readme_raw or "")[:4000].lower()
    corpus = f"{clean_name}\n{clean_desc}\n{readme_preview}"

    # 1. Awesome List / Resource Collection check
    if re.search(r"(?:^|/)(?:awesome[-_]|.*[-_]awesome$|awesome$|curated[-_]list)", clean_name):
        return "awesome_list", REPO_TYPES["awesome_list"]["badge"]
    if re.search(r"\b(?:awesome list|curated list of|collection of awesome|curated collection of|useful resources for|cheat-?sheet collection)\b", corpus):
        return "awesome_list", REPO_TYPES["awesome_list"]["badge"]

    # 2. Course, Tutorial, Book, Educational Material
    course_name_pattern = r"(?:coursebook|tutorial|course|lecture|interview|handbook|roadmap|guide|curriculum|100[-_]?days|learn[-_]|study[-_]?guide|bootcamp)"
    if re.search(course_name_pattern, clean_name):
        return "course_tutorial", REPO_TYPES["course_tutorial"]["badge"]
    course_desc_pattern = r"\b(?:coursebook|syllabus|lecture notes|university of|cs\d{3}|course materials|interactive tutorial|step-by-step (?:tutorial|guide)|learning (?:path|roadmap)|curriculum|free book|interview prep(?:aration)?|for beginners|coding interview)\b"
    if re.search(course_desc_pattern, corpus):
        return "course_tutorial", REPO_TYPES["course_tutorial"]["badge"]

    # 3. AI Model Weights / Checkpoints
    if re.search(r"(?:[-_]gguf$|[-_]safetensors$|checkpoints?|weights?|lora|[-_]model$)", clean_name):
        if re.search(r"\b(?:weights|checkpoint|gguf|safetensors|model parameters|huggingface)\b", corpus):
            return "ai_model", REPO_TYPES["ai_model"]["badge"]
    if re.search(r"\b(?:model weights|pretrained (?:weights|model)|gguf format|safetensors format|lora adapter|foundation model weights|fine-tuned checkpoints)\b", corpus):
        return "ai_model", REPO_TYPES["ai_model"]["badge"]

    # 4. Dataset / Benchmark
    if re.search(r"(?:dataset|benchmark|[-_]eval$|eval[-_])", clean_name):
        return "dataset_benchmark", REPO_TYPES["dataset_benchmark"]["badge"]
    if re.search(r"\b(?:evaluation benchmark|benchmark suite|ground truth dataset|training dataset|test corpus|evaluation dataset)\b", corpus):
        return "dataset_benchmark", REPO_TYPES["dataset_benchmark"]["badge"]

    # 5. Library / SDK / Package
    library_patterns = r"\b(?:library for|sdk for|client (?:library|sdk)|wrapper for|rust crate|python package|go package|gem for|bindings for|driver for|framework for (?:building|developing)|middleware for|toolkit for (?:building|developers)|npm package)\b"
    if re.search(library_patterns, clean_desc) or re.search(library_patterns, readme_preview[:1500]):
        return "library_sdk", REPO_TYPES["library_sdk"]["badge"]

    # 6. Default: Tool / Application / CLI
    return "tool_app", REPO_TYPES["tool_app"]["badge"]
