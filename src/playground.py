"""Playground, Docker Manifest & 1-Click Cloud Execution Generator.

Generates:
- Cloud 1-Click Playground URLs (Codespaces, Gitpod, Colab, StackBlitz, GitHub.dev, Replit)
- Docker compose & Dockerfile specifications
- Ready-to-run Local Scripts (Bash, PowerShell, One-liner)
- Port and runtime environment inference
"""

import os
import re
from typing import Any, Dict, List, Optional


def infer_runtime_env(
    repo_name: str,
    language: str = "",
    description: str = "",
    topics: Optional[List[str]] = None,
    quick_run: str = "",
    repo_type: str = "tool_app",
    tech_stack: Optional[List[str]] = None,
    readme_raw: Optional[str] = None,
) -> Dict[str, Any]:
    """Infers the runtime environment, primary port, build tools and startup commands."""
    topics = topics or []
    tech_stack = tech_stack or []
    slug = repo_name.split("/")[-1].lower() if "/" in repo_name else repo_name.lower()
    slug = re.sub(r"[^a-z0-9_-]", "-", slug).strip("-") or "app"

    text = f"{repo_name} {language} {description} {' '.join(topics)} {' '.join(tech_stack)} {quick_run}".lower()
    readme_lower = (readme_raw[:4000] if readme_raw else "").lower()

    # Detect port
    port = 8080
    framework = "Generic App"
    category = "general"

    # 1. Specialized / AI Services
    if "ollama" in text or "11434" in text:
        port = 11434
        framework = "Ollama / Local LLM"
        category = "ai"
    elif any(k in text for k in ("streamlit", "st.")):
        port = 8501
        framework = "Streamlit"
        category = "ai_web"
    elif any(k in text for k in ("gradio", "gr.")):
        port = 7860
        framework = "Gradio"
        category = "ai_web"
    elif any(k in text for k in ("fastapi", "uvicorn")):
        port = 8000
        framework = "FastAPI"
        category = "backend"
    elif any(k in text for k in ("flask",)):
        port = 5000
        framework = "Flask"
        category = "backend"
    elif any(k in text for k in ("django",)):
        port = 8000
        framework = "Django"
        category = "backend"
    # 2. Modern Web / Frontend Frameworks
    elif any(k in text for k in ("vite",)):
        port = 5173
        framework = "Vite"
        category = "frontend"
    elif any(k in text for k in ("next.js", "nextjs", "react", "vue", "nuxt", "svelte", "astro", "remix")):
        port = 3000
        framework = "Node / Modern Web"
        category = "frontend"
    elif language.lower() in ("typescript", "javascript"):
        port = 3000
        framework = "Node.js"
        category = "frontend"
    elif language.lower() in ("python", "jupyter notebook"):
        port = 8000
        framework = "Python"
        category = "python"
    elif language.lower() in ("go", "golang"):
        port = 8080
        framework = "Go"
        category = "backend"
    elif language.lower() in ("rust",):
        port = 8080
        framework = "Rust"
        category = "system"
    elif language.lower() in ("java", "kotlin"):
        port = 8080
        framework = "Java / JVM"
        category = "backend"
    elif repo_type in ("course_tutorial", "awesome_list", "dataset_benchmark"):
        port = 8000
        framework = "Docs / Static Content"
        category = "docs"

    # Determine commands based on runtime
    lang_lower = language.lower()
    
    # Custom quick run override if available
    install_cmd = ""
    run_cmd = ""

    if quick_run and ("docker " in quick_run or "docker-compose" in quick_run):
        run_cmd = quick_run
        install_cmd = "docker pull " + (repo_name.lower()) if "docker run" in quick_run else "# Sử dụng Docker sẵn có"
    elif category == "frontend" or lang_lower in ("typescript", "javascript"):
        install_cmd = "npm install"
        run_cmd = "npm run dev"
        if "pnpm" in text or "pnpm" in readme_lower:
            install_cmd = "pnpm install"
            run_cmd = "pnpm dev"
        elif "yarn" in text or "yarn" in readme_lower:
            install_cmd = "yarn install"
            run_cmd = "yarn dev"
    elif lang_lower in ("python", "jupyter notebook") or category in ("ai_web", "python") or framework in ("FastAPI", "Flask", "Django", "Streamlit", "Gradio"):
        if framework == "FastAPI":
            install_cmd = "pip install -r requirements.txt"
            run_cmd = f"uvicorn main:app --reload --port {port}"
        elif framework == "Streamlit":
            install_cmd = "pip install -r requirements.txt"
            run_cmd = f"streamlit run app.py --server.port {port}"
        elif framework == "Gradio":
            install_cmd = "pip install -r requirements.txt"
            run_cmd = "python app.py"
        elif framework == "Flask":
            install_cmd = "pip install -r requirements.txt"
            run_cmd = f"flask run --port {port}"
        elif framework == "Django":
            install_cmd = "pip install -r requirements.txt"
            run_cmd = f"python manage.py runserver 0.0.0.0:{port}"
        else:
            install_cmd = "pip install -r requirements.txt"
            run_cmd = "python main.py"
    elif lang_lower in ("go", "golang"):
        install_cmd = "go mod download"
        run_cmd = "go run ."
    elif lang_lower in ("rust",):
        install_cmd = "cargo build"
        run_cmd = "cargo run"
    elif lang_lower in ("java", "kotlin"):
        install_cmd = "./gradlew build || mvn clean package"
        run_cmd = "java -jar build/libs/*.jar || java -jar target/*.jar"
    elif category == "docs":
        install_cmd = "# Tài liệu / Khóa học không cần cài đặt đặc thù"
        run_cmd = f"python -m http.server {port}"
    else:
        install_cmd = "# Cài đặt theo README dự án"
        run_cmd = f"# Khởi chạy trên cổng {port}"

    if quick_run and not ("docker" in quick_run):
        # If quick_run matches install or run, prioritize it
        if any(w in quick_run for w in ("pip install", "npm install", "cargo install", "brew install", "go install")):
            install_cmd = quick_run
        elif any(w in quick_run for w in ("python ", "npx ", "cargo run", "go run", "npm ")):
            run_cmd = quick_run

    return {
        "slug": slug,
        "language": language,
        "framework": framework,
        "category": category,
        "port": port,
        "install_cmd": install_cmd,
        "run_cmd": run_cmd,
        "quick_run": quick_run,
    }


def generate_cloud_links(
    repo_name: str,
    language: str = "",
    description: str = "",
    topics: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Generates direct 1-click cloud playground URLs."""
    topics = topics or []
    text = f"{repo_name} {language} {description} {' '.join(topics)}".lower()
    lang_lower = language.lower()

    links = []

    # 1. GitHub Codespaces (Universal, always works for any GitHub repo)
    links.append({
        "id": "codespaces",
        "name": "GitHub Codespaces",
        "icon": "🚀",
        "badge": "Full Linux VM",
        "url": f"https://codespaces.new/{repo_name}",
        "description": "Máy ảo Linux đám mây của GitHub (60h miễn phí/tháng, sẵn sàng trong 30s).",
        "recommended": True,
        "type": "cloud_vm",
    })

    # 2. Gitpod (Automated dev environment)
    links.append({
        "id": "gitpod",
        "name": "Gitpod",
        "icon": "⚡",
        "badge": "Automated Cloud Dev",
        "url": f"https://gitpod.io/#https://github.com/{repo_name}",
        "description": "Khởi động môi trường dev tự động cài dependencies từ git repo.",
        "recommended": False,
        "type": "cloud_vm",
    })

    # 3. Google Colab (For Python / AI / ML / Notebooks)
    is_colab_friendly = (
        lang_lower in ("python", "jupyter notebook")
        or any(k in text for k in ("pytorch", "tensorflow", "llm", "ai", "model", "deep-learning", "diffusion", "rag", "notebook"))
    )
    if is_colab_friendly:
        links.append({
            "id": "colab",
            "name": "Google Colab",
            "icon": "🔬",
            "badge": "Free GPU / TPU",
            "url": f"https://colab.research.google.com/github/{repo_name}/blob/main/",
            "description": "Chạy thử mô hình AI hoặc notebook trên GPU/TPU miễn phí của Google.",
            "recommended": True,
            "type": "notebook_gpu",
        })

    # 4. StackBlitz (WebContainers for Web / Node / JS / TS)
    is_stackblitz_friendly = (
        lang_lower in ("typescript", "javascript", "html", "css", "vue", "svelte")
        or any(k in text for k in ("react", "vue", "angular", "next", "vite", "web", "frontend", "svelte", "astro"))
    )
    if is_stackblitz_friendly:
        links.append({
            "id": "stackblitz",
            "name": "StackBlitz WebContainers",
            "icon": "⚡",
            "badge": "In-Browser Node.js",
            "url": f"https://stackblitz.com/github/{repo_name}",
            "description": "Khởi chạy Node.js và dev server ngay trong trình duyệt qua WebAssembly.",
            "recommended": True,
            "type": "in_browser",
        })

    # 5. GitHub.dev (VS Code Web editor)
    links.append({
        "id": "github_dev",
        "name": "GitHub.dev (VS Code Web)",
        "icon": "💻",
        "badge": "Web VS Code",
        "url": f"https://github.dev/{repo_name}",
        "description": "Đọc và duyệt mã nguồn tức thì bằng giao diện VS Code trong trình duyệt (phím tắt '.')",
        "recommended": False,
        "type": "editor",
    })

    # 6. Replit
    links.append({
        "id": "replit",
        "name": "Replit",
        "icon": "🌐",
        "badge": "Online IDE",
        "url": f"https://replit.com/github/{repo_name}",
        "description": "Import và chạy mã nguồn trực tiếp trên môi trường đám mây Replit.",
        "recommended": False,
        "type": "cloud_vm",
    })

    return links


def generate_docker_manifest(
    repo_name: str,
    runtime_info: Dict[str, Any],
) -> Dict[str, str]:
    """Generates docker-compose.yml and Dockerfile tailored to the repository runtime."""
    slug = runtime_info["slug"]
    port = runtime_info["port"]
    category = runtime_info["category"]
    framework = runtime_info["framework"]
    lang_lower = (runtime_info.get("language") or "").lower()
    quick_run = runtime_info.get("quick_run", "")

    # Check if there is an explicit docker image in quick_run (e.g. docker run ... image:tag)
    explicit_image = ""
    if quick_run and "docker run" in quick_run:
        parts = quick_run.split()
        for p in reversed(parts):
            if not p.startswith("-") and not p.startswith("http") and "/" in p or ":" in p:
                explicit_image = p.strip("`'\"")
                break

    # Generate Dockerfile
    if lang_lower in ("go", "golang") or "go" in framework.lower():
        dockerfile = f"""# Dockerfile sinh tự động cho {repo_name} (Go Multi-stage)
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server .

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/server /app/server
EXPOSE {port}
CMD ["/app/server"]
""".strip()
    elif lang_lower in ("rust",) or "rust" in framework.lower():
        dockerfile = f"""# Dockerfile sinh tự động cho {repo_name} (Rust Multi-stage)
FROM rust:1.78-alpine AS builder
WORKDIR /app
RUN apk add --no-cache musl-dev
COPY Cargo.toml Cargo.lock* ./
COPY src ./src
RUN cargo build --release

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/target/release/* /app/app
EXPOSE {port}
CMD ["/app/app"]
""".strip()
    elif category == "frontend" or lang_lower in ("typescript", "javascript"):
        dockerfile = f"""# Dockerfile sinh tự động cho {repo_name}
FROM node:20-alpine

WORKDIR /app

# Sao chép file cấu hình dependencies
COPY package*.json pnpm-lock.yaml* yarn.lock* ./

# Cài đặt thư viện phụ thuộc
RUN npm install

# Sao chép toàn bộ mã nguồn
COPY . .

# Mở cổng phát triển
EXPOSE {port}

# Lệnh chạy ứng dụng
ENV PORT={port}
CMD ["npm", "run", "dev"]
""".strip()
    elif category in ("backend", "ai_web", "python") or lang_lower in ("python", "jupyter notebook"):
        dockerfile = f"""# Dockerfile sinh tự động cho {repo_name} ({framework})
FROM python:3.11-slim

WORKDIR /app

# Cài đặt công cụ hệ thống nếu cần
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl git build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Cài đặt python dependencies
COPY requirements.txt* pyproject.toml* ./
RUN pip install --no-cache-dir -U pip && \\
    (test -f requirements.txt && pip install --no-cache-dir -r requirements.txt || true)

# Sao chép mã nguồn
COPY . .

EXPOSE {port}
ENV PYTHONUNBUFFERED=1
ENV PORT={port}

CMD ["python", "main.py"]
""".strip()
    elif lang_lower in ("java", "kotlin"):
        dockerfile = f"""# Dockerfile sinh tự động cho {repo_name} (Java / JVM)
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
COPY . .
RUN chmod +x gradlew* mvnw* 2>/dev/null || true
RUN ./gradlew build -x test || ./mvnw clean package -DskipTests || true

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/build/libs/*.jar /app/app.jar
EXPOSE {port}
CMD ["java", "-jar", "/app/app.jar"]
""".strip()
    else:
        dockerfile = f"""# Dockerfile cơ bản cho {repo_name}
FROM alpine:latest
WORKDIR /app
COPY . .
EXPOSE {port}
CMD ["echo", "Container {slug} sẵn sàng trên cổng {port}"]
""".strip()

    # Generate docker-compose.yml
    if explicit_image:
        docker_compose = f"""version: '3.8'

services:
  {slug}:
    image: {explicit_image}
    container_name: {slug}-playground
    ports:
      - "{port}:{port}"
    environment:
      - PORT={port}
    volumes:
      - {slug}-data:/root
    restart: unless-stopped

volumes:
  {slug}-data:
""".strip()
        docker_run_cmd = quick_run
    else:
        docker_compose = f"""version: '3.8'

services:
  {slug}:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {slug}-playground
    ports:
      - "{port}:{port}"
    environment:
      - PORT={port}
      - ENV=development
    volumes:
      - .:/app
    restart: unless-stopped
""".strip()
        docker_run_cmd = f"docker compose up --build -d"

    return {
        "docker_compose": docker_compose,
        "dockerfile": dockerfile,
        "docker_run_cmd": docker_run_cmd,
    }


def generate_local_scripts(
    repo_name: str,
    runtime_info: Dict[str, Any],
) -> Dict[str, str]:
    """Generates Bash and PowerShell quick run scripts."""
    slug = runtime_info["slug"]
    install_cmd = runtime_info["install_cmd"]
    run_cmd = runtime_info["run_cmd"]
    port = runtime_info["port"]

    bash_script = f"""#!/usr/bin/env bash
# ========================================================
# 🚀 1-Click Quick Run Script for {repo_name}
# Tự động sinh bởi GitHub Trending Analyzer
# ========================================================
set -e

REPO="{repo_name}"
URL="https://github.com/{repo_name}.git"
DIR="{slug}"

echo -e "\\033[1;36m========================================================\\033[0m"
echo -e "\\033[1;32m🚀 Khởi chạy dự án: $REPO\\033[0m"
echo -e "\\033[1;36m========================================================\\033[0m"

# 1. Clone repository nếu chưa có
if [ ! -d "$DIR" ]; then
    echo -e "\\033[1;33m📦 Đang clone repository từ $URL...\\033[0m"
    git clone "$URL" "$DIR"
fi

cd "$DIR"

# 2. Cài đặt dependencies
echo -e "\\033[1;33m⚡ Đang cài đặt thư viện phụ thuộc...\\033[0m"
{install_cmd}

# 3. Khởi chạy
echo -e "\\033[1;32m🎉 Khởi chạy ứng dụng (Port dự kiến: {port})...\\033[0m"
{run_cmd}
""".strip()

    powershell_script = f"""# ========================================================
# 🚀 1-Click Quick Run Script for {repo_name} (Windows PowerShell)
# Tự động sinh bởi GitHub Trending Analyzer
# ========================================================
$ErrorActionPreference = "Stop"

$Repo = "{repo_name}"
$Url = "https://github.com/{repo_name}.git"
$Dir = "{slug}"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "🚀 Khởi chạy dự án: $Repo" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Clone repository nếu chưa có
if (-not (Test-Path $Dir)) {{
    Write-Host "📦 Đang clone repository từ $Url..." -ForegroundColor Yellow
    git clone $Url $Dir
}}

Set-Location $Dir

# 2. Cài đặt dependencies
Write-Host "⚡ Đang cài đặt thư viện phụ thuộc..." -ForegroundColor Yellow
{install_cmd}

# 3. Khởi chạy
Write-Host "🎉 Khởi chạy ứng dụng (Port dự kiến: {port})..." -ForegroundColor Green
{run_cmd}
""".strip()

    one_liner = f"git clone https://github.com/{repo_name}.git {slug} && cd {slug} && {install_cmd} && {run_cmd}"

    return {
        "bash": bash_script,
        "powershell": powershell_script,
        "one_liner": one_liner,
    }


def generate_playground_manifest(
    repo_name: str,
    language: str = "",
    description: str = "",
    topics: Optional[List[str]] = None,
    quick_run: str = "",
    repo_type: str = "tool_app",
    tech_stack: Optional[List[str]] = None,
    readme_raw: Optional[str] = None,
) -> Dict[str, Any]:
    """Generates complete playground suite for a repository."""
    topics = topics or []
    tech_stack = tech_stack or []

    runtime_info = infer_runtime_env(
        repo_name=repo_name,
        language=language,
        description=description,
        topics=topics,
        quick_run=quick_run,
        repo_type=repo_type,
        tech_stack=tech_stack,
        readme_raw=readme_raw,
    )

    cloud_links = generate_cloud_links(
        repo_name=repo_name,
        language=language,
        description=description,
        topics=topics,
    )

    docker_assets = generate_docker_manifest(
        repo_name=repo_name,
        runtime_info=runtime_info,
    )

    local_scripts = generate_local_scripts(
        repo_name=repo_name,
        runtime_info=runtime_info,
    )

    return {
        "repo_name": repo_name,
        "slug": runtime_info["slug"],
        "framework": runtime_info["framework"],
        "port": runtime_info["port"],
        "category": runtime_info["category"],
        "install_cmd": runtime_info["install_cmd"],
        "run_cmd": runtime_info["run_cmd"],
        "cloud_links": cloud_links,
        "docker": docker_assets,
        "scripts": local_scripts,
    }
