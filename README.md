# 🔥 GitHub Trending Analyzer (`gh-trending`)

Tài liệu chức năng và bàn giao: [docs/CHUC_NANG_VA_HUONG_DAN.md](docs/CHUC_NANG_VA_HUONG_DAN.md).
Tạo bản ZIP mã nguồn: `python3 scripts/package_release.py` (đầu ra trong `dist/`).

> Công cụ tự động thu thập và phân tích chuyên sâu các dự án trên [GitHub Trending](https://github.com/trending), trả lời câu hỏi: **"Dự án này làm gì, giải quyết bài toán nào, và tại sao nó lại đang hot?"** mỗi khi bạn gọi.

---

## ✨ Tính năng nổi bật

- 🚀 **Zero-Dependency:** Chạy trực tiếp bằng thư viện chuẩn của Python 3 (không cần cài thêm bất kỳ package ngoài nào).
- 💡 **Nhận diện đối thủ thương mại (Alternative to...):** Tự động phát hiện các dự án thay thế mã nguồn mở cho các sản phẩm/SaaS thương mại đắt đỏ (`ElevenLabs`, `Notion`, `Datadog`, `Cursor`, `Postman`, `Firebase`...).
- ⚡ **Nhận diện siêu bứt phá (Breakout & Velocity Score):** Tự động phát hiện các dự án mới nổi tăng trưởng thần tốc (`🔥 Breakout Star`, `⚡ High Velocity`, `🏛️ Established Giant`).
- 🎯 **Cá nhân hóa theo sở thích (Watchlist & Match Score):** Cấu hình từ khoá, ngôn ngữ, chuyên mục yêu thích trong `watchlist.json` để tự động chấm điểm phù hợp (0-100%) và ưu tiên hiển thị.
- 🏷️ **Phân loại loại Repository (Repo Type Taxonomy):** Tự động phân biệt bản chất dự án (`🛠️ Tool / App`, `📦 Library / SDK`, `🧠 AI Model / Weights`, `📚 Khóa học / Tài liệu`, `📋 Awesome List`, `📊 Dataset / Benchmark`) và áp dụng tiêu chuẩn đánh giá riêng, tránh đánh giá nhầm khóa học thành phần mềm sản xuất.
- 🟢 **Đánh giá độ "chín" dự án (Maturity Check):** Phân loại dự án sẵn sàng thực tế (`🟢 Production Ready`), đang phát triển tích cực (`🟡 Beta`), hoặc thử nghiệm (`🟠 Experimental`).
- 🛠️ **Trích xuất Tech Stack & Lệnh chạy thử nhanh (Quick Run):** Tự động nhận diện công nghệ nền tảng và lệnh một dòng copy chạy ngay (`docker run`, `pip install`, `npm`, `cargo`).
- 🕰️ **Bộ nhớ quỹ đạo & Lịch sử (SQLite Temporal Memory):** Tự động ghi nhớ snapshot phân tích, nhận diện dự án mới nổi lần đầu (`🌱 Mới xuất hiện`) và dự án quay trở lại (`🔄 Đã gặp N lần`).
- 👥 **Vòng phản hồi & Tự học sở thích (Adaptive Watchlist):** Đánh giá trực quan 👍/👎, gắn trạng thái nghiên cứu (`🔖 Muốn thử`, `✅ Đã thử`, `⏭️ Bỏ qua`) và tự động học từ khóa, ngôn ngữ bạn yêu thích để cập nhật watchlist.
- 📚 **Cơ sở tri thức tự tiến hóa (Dynamic Knowledge Base):** Tự động nhận diện và nạp thêm các sản phẩm thương mại mới vào từ điển tri thức nội bộ mỗi khi quét qua repo mới.
- 🧠 **Bộ máy phân tích tác dụng kép (Dual Engine):**
  - **Heuristic Engine (Mặc định):** Tự động phân tích cấu trúc README, trích xuất tính năng, chuyên ngành phù hợp, bài toán thực tế và phân loại tự động mà không cần API key.
  - **AI Engine (Gemini / LLM):** Kích hoạt bằng cờ `--ai` để sinh bản phân tích tiếng Việt chuyên sâu, mượt mà và sắc sảo.
- 🎨 **Giao diện đa dạng:**
  - **Terminal Card View:** Hiển thị thẻ bo viền màu sắc ANSI đẹp mắt với đầy đủ huy hiệu trạng thái.
  - **Interactive Mode (`-i`):** Menu tương tác chọn repo xem chi tiết hoặc mở thẳng trên trình duyệt.
  - **Dashboard HTML (`--web` / `--serve`):** Giao diện Dark theme sang trọng, hỗ trợ tìm kiếm trực tiếp, lọc trạng thái nghiên cứu, độ chín, bứt phá, thay thế thương mại, đồng bộ sở thích và nút Copy lệnh nhanh.
  - **Markdown Export (`-o report.md`):** Xuất tài liệu tóm tắt phục vụ lưu trữ hoặc chia sẻ.
- 🤖 **Tích hợp sẵn Antigravity Skill:** Có thể gọi tự nhiên ngay trong chat với trợ lý AI (ví dụ: *"Phân tích github trending hôm nay"*).

---

## 💻 Cách sử dụng nhanh

### 1. Phân tích Trending hôm nay (mặc định Top 10)
```bash
./trending
```
*(hoặc `python3 gh_trending.py`)*

### 2. Tìm các giải pháp thay thế mã nguồn mở cho SaaS thương mại (Alternative)
```bash
# Chỉ hiển thị các dự án thay thế phần mềm thương mại (Notion, ElevenLabs, Datadog...)
./trending --alt
```

### 3. Ưu tiên xếp hạng theo danh sách sở thích (Watchlist)
```bash
# Đọc sở thích từ watchlist.json và chấm điểm Match Score (0 - 100%)
./trending --watchlist

# Hoặc chấm điểm/lọc tức thì theo từ khóa tùy ý:
./trending --match "agent,rag,rust"
```

### 4. Lọc theo độ "chín" của dự án (Maturity)
```bash
# Chỉ xem các dự án đã sẵn sàng triển khai (Production Ready)
./trending --min-maturity production

# Xem các dự án từ Beta trở lên
./trending --min-maturity beta
```

### 5. Lọc theo loại Repository (Repo Type)
```bash
# Chỉ xem các công cụ / CLI / ứng dụng
./trending --type tool

# Xem thư viện / SDK
./trending --type library

# Xem tài liệu học tập / khóa học
./trending --type course

# Xem danh mục tài nguyên chọn lọc (Awesome Lists)
./trending --type awesome

# Xem mô hình / trọng số AI (Weights/GGUF/SafeTensors)
./trending --type model
```

### 6. Mở Dashboard HTML trực quan trên trình duyệt
```bash
./trending --web --watchlist
```
Lệnh này sẽ tự động sinh file `trending_dashboard.html` kèm các bộ lọc loại dự án, độ chín, bứt phá, sao chép lệnh chạy nhanh và mở tab mới trên trình duyệt.

### 7. Lọc theo ngôn ngữ & thời gian
```bash
# Xem trending tuần này của Python
./trending --lang python --since weekly

# Xem trending hôm nay của Rust (Top 5)
./trending --lang rust --limit 5

# Mốc thời gian hỗ trợ: daily (ngày), weekly (tuần), monthly (tháng)
./trending --since monthly --limit 10
```

### 8. Bật chế độ menu tương tác (Interactive)
```bash
./trending -i
```
Trong chế độ này, bạn có thể:
- Gõ số thứ tự (ví dụ: `1`, `2`) để xem chi tiết dự án.
- Gõ `o 1` để mở trực tiếp repo số 1 trên GitHub.
- Gõ `w` để mở giao diện Web.

### 9. Xuất báo cáo Markdown
```bash
./trending --since weekly --watchlist -o weekly_report.md
```

### 10. Phân tích bằng AI (Tuỳ chọn nâng cao)
Nếu bạn có `GEMINI_API_KEY`, bạn có thể xuất biến môi trường hoặc truyền trực tiếp:
```bash
export GEMINI_API_KEY="your_api_key_here"
./trending --ai --limit 5
```

### 11. Hệ thống AI Dynamic Few-Shot & Tự phản biện (Grounded Self-Critique)
Khi phân tích bằng AI (`--ai`), công cụ sử dụng kiến trúc học hỏi động và phản biện đa tầng:
- **Dynamic Few-Shot Learning**: Tự động tra cứu `data/history.db` để lấy các repository bạn từng bấm 👍 (thích) làm ví dụ chuẩn mực đưa vào ngữ cảnh Gemini. Nếu chưa có feedback, hệ thống kích hoạt bộ mẫu chuẩn khắt khe từ `RESEARCH_SAMPLE_VI.md` (`NVIDIA/OpenShell`, `debpalash/VoiceStudio`, `astral-sh/uv`).
- **Grounded Self-Critique Engine**:
  - Tự động phát hiện và làm mềm các từ ngữ tiếp thị, tuyên bố tuyệt đối hóa không có benchmark (như *"tốt nhất hiện nay"*, *"thay đổi thế giới"*, *"hoàn hảo 100%"*).
  - Kiểm tra độ phủ của trích dẫn nguồn `[S1]`, `[S2]`, bắt buộc nêu rõ giới hạn kỹ thuật và phương pháp đo lường thử nghiệm.
  - Chấm điểm chất lượng phản biện **Grounding Quality Score** (40 – 100/100) và xuất chi tiết phản biện trên cả Terminal, Markdown report và Web Dashboard.

### 12. Lập lịch tự động định kỳ (Scheduler Automation & Webhooks)
Tự động hóa hoàn toàn quy trình theo dõi GitHub Trending mỗi ngày:
```bash
# Chạy tự động 1 lần, lưu báo cáo Markdown & Dashboard HTML vào reports/:
./trending --schedule-once --since daily --limit 15

# Khởi động Daemon nền chạy tự động mỗi ngày vào lúc 08:00 sáng:
./trending --daemon --daemon-time "08:00"

# Gửi thông báo tóm tắt tới Discord / Slack Webhook:
./trending --schedule-once --webhook "https://discord.com/api/webhooks/..."

# Xuất lệnh tạo Scheduled Task cho Windows Task Scheduler:
./trending --export-task windows

# Xuất dòng cấu hình Crontab cho Linux / macOS:
./trending --export-task cron
```

### 13. Hỏi đáp chuyên sâu trực tiếp với Repo (Interactive Repo Q&A)
Bạn có thể đặt bất kỳ câu hỏi kỹ thuật nào về một repository cụ thể:
- **Trên Web Dashboard**: Bấm nút **💬 Hỏi đáp** trên mỗi thẻ repo để mở khung chat trực tiếp.
- **Trên Terminal**: Vào chế độ tương tác `./trending -i` và gõ:
  ```text
  ask 1 Có chạy offline trên máy cá nhân được không?
  ask 2 So sánh với LangChain thì điểm khác biệt là gì?
  ask 3 Lệnh cài đặt nhanh và cấu hình phần cứng ra sao?
  ```
- **Hỗ trợ 2 chế độ**: Tự động trả lời qua AI (`--ai`) hoặc trích xuất ngữ nghĩa chuẩn xác offline từ tài liệu dự án mà không cần API key.

---

## 🛠️ Cấu trúc thư mục

```
fervent-fermi/
├── trending                  # Shell script chạy nhanh (chmod +x)
├── gh_trending.py            # Entry point chính của CLI
├── SKILL.md                  # Cấu hình Antigravity Skill
├── src/
│   ├── __init__.py
│   ├── scraper.py            # Parser cào dữ liệu từ github.com/trending
│   ├── fetcher.py            # Tải & tiền xử lý README từ GitHub
│   ├── analyzer.py           # Bộ máy phân tích tác dụng (Heuristic + AI Grounded)
│   ├── few_shot.py           # Dynamic Few-Shot Learning (từ SQLite & Benchmark mẫu)
│   ├── grounding.py          # Tự phản biện (Self-Critique), khử hype, tính điểm Grounding
│   ├── history_db.py         # Bộ nhớ dài hạn SQLite lưu vết lịch sử & feedback
│   ├── repo_type.py          # Phân loại chuyên sâu 6 dạng repository
│   ├── alternatives.py       # Nhận diện & học hỏi đối thủ thương mại
│   ├── repo_chat.py          # Hỏi đáp kỹ thuật chuyên sâu (Repo Q&A Engine)
│   ├── scheduler.py          # Bộ lập lịch tự động định kỳ & thông báo webhook
│   ├── formatter.py          # Format thẻ bo màu Terminal & xuất Markdown
│   └── html_dashboard.py     # Sinh giao diện Web Dark-mode & Live Server
├── reports/                  # Thư mục lưu trữ báo cáo tự động định kỳ
├── tests/                    # Bộ 72 kiểm thử tự động
├── .env.example              # Mẫu cấu hình API key
└── README.md                 # Hướng dẫn sử dụng
```

---

## 🧪 Chạy kiểm thử tự động

```bash
python3 -m unittest discover tests
```

## Phân tích nội dung sâu

```bash
# Đọc README mới + metadata + tối đa 3 tài liệu được README liên kết trong cùng repo
./trending --deep --limit 5 -o deep_report.md

# AI diễn giải tiếng Việt, giải thích cơ chế và use cases, dẫn nguồn [S1], [S2]
# Chỉ bật --ai khi muốn sử dụng API của bạn; có thể phát sinh phí của provider.
export GEMINI_API_KEY="your_api_key_here"
./trending --deep --ai --model gemini-3.1-flash-lite --limit 5 --web -o deep_report.md
```

Phân tích mới gồm: cơ chế/kiến trúc, ví dụ và cách đánh giá, giới hạn, điều kiện
triển khai/tích hợp, so sánh có căn cứ, các câu hỏi còn thiếu và danh sách nguồn.
Dashboard có mục mở rộng “Phân tích sâu”. JSON chứa thêm các trường tương ứng
và evidence trích từ tài liệu. Báo cáo ghi engine đã thực sự sử dụng.

Không dùng AI: trích nguyên văn các section liên quan (có thể bằng tiếng Anh),
không tự tạo các lời khen hoặc khẳng định thiếu bằng chứng. Dùng AI: tổng hợp
và diễn giải tiếng Việt, nhưng vẫn cần kiểm tra các suy luận và dẫn nguồn.
Công cụ đọc tài liệu, không chạy code repo hoặc xác minh benchmark.
`--deep` không kết hợp với `--no-readme`. Tài liệu nằm ngoài repo, source code
và release/news chưa được thu thập tự động. API GitHub không xác thực có thể
rate limit; lỗi nguồn và fallback AI được ghi rõ. Chế độ thường vẫn có thể dùng
cache README cũ; chế độ deep yêu cầu tải lại.

Model đọc từ `--model`, rồi `GEMINI_MODEL`, mặc định `gemini-3.1-flash-lite`.
File `.env.example` là mẫu; chương trình đọc biến môi trường, không tự nạp `.env`.

Launcher dùng `python3` trên PATH. Có thể chọn interpreter riêng bằng
`GH_TRENDING_PYTHON=/path/to/python ./trending ...`. Nếu máy thiếu chứng chỉ TLS,
cần cấu hình certificate cho interpreter; công cụ không tắt xác minh TLS.

### Tìm project mới trên GitHub

```bash
./trending --serve
# Mặc định mở http://127.0.0.1:8766/; Ctrl+C để dừng.
# Đọc thêm tài liệu liên kết khi tìm kiếm:
./trending --serve --deep
# Nếu muốn diễn giải bằng API Gemini của bạn:
./trending --serve --deep --ai
```

Dashboard local có **Từ khóa**, **Số lượng project** (1–30), **Ngôn ngữ**,
**Sắp xếp** (phù hợp nhất / stars / cập nhật), cách khớp một hoặc tất cả từ khóa,
và tùy chọn **Phân tích sâu**. Bấm **Tìm kiếm** hoặc Enter để lấy project mới từ
GitHub Search rồi đọc README/phân tích. Nhiều từ khóa ngăn cách bằng dấu phẩy;
để trống lấy **GitHub Trending**, mặc định hôm nay, xếp theo **số stars mới
trong kỳ từ cao xuống thấp**. Có thể chọn tuần/tháng và lọc theo ngôn ngữ.
Số lượng được áp dụng sau khi xếp hạng toàn danh sách Trending của kỳ đã chọn;
GitHub có thể cung cấp ít project hơn số lượng yêu cầu. Đây là xếp hạng trong
danh sách Trending, không phải toàn bộ repository GitHub hoặc phần trăm tăng trưởng.

Bộ đếm ghi số project đã tải, số đang hiển thị và tổng kết quả GitHub trả về.
Các bộ lọc phía dưới áp dụng lên danh sách vừa tải; **Xóa bộ lọc** không gọi
GitHub thêm. Lỗi mạng/rate limit được hiển thị và giữ danh sách trước đó.
Kết quả GitHub Search không được gắn nhãn tăng trưởng Trending.

Mỗi kết quả tìm theo tên hoặc nội dung README có thêm **tăng trưởng stars hôm nay,
7 ngày và 30 ngày** từ [GitHub Star History API](https://docs.github.com/en/rest/activity/starring#get-repository-star-history).
Đây là stars mới được thêm, không phải tăng trưởng ròng sau khi trừ lượt bỏ star.
Các cửa sổ gồm ngày hiện tại (chưa kết thúc), tính theo ngày của bucket lịch sử;
GitHub không đảm bảo ranh giới ngày trùng UTC. Dữ liệu được cache tối đa 10 phút.
Nếu thiếu lịch sử hoặc API lỗi/giới hạn, kỳ tương ứng ghi **Chưa có dữ liệu**,
không thay bằng 0; tổng stars vẫn hiển thị riêng trên đầu thẻ.

Server chỉ bind `127.0.0.1`, không phục vụ file workspace hoặc API key.
Có thể đổi port bằng `--port 8767`, tắt tự mở tab bằng `--no-browser`.
`GITHUB_TOKEN` tùy chọn được đọc ở server để gửi request tới GitHub; kết quả
luôn giới hạn ở repository công khai. Không cần API key để tìm GitHub và dùng
heuristic. AI chỉ bật khi chạy server với `--ai`.

Dashboard HTML xuất bằng `--web` vẫn là snapshot và chỉ lọc dữ liệu đã tải.
Muốn lấy project mới trực tiếp từ nút Tìm kiếm, dùng chế độ `--serve`.

### Phạm vi tìm kiếm từ khóa

Chọn **Tìm kiếm theo**:

- **Tên project**: tìm trong tên repository (`in:name`), mặc định.
- **Từ khóa bên trong project (README)**: tìm trong nội dung README (`in:readme`),
  phù hợp để tìm chức năng hoặc công nghệ dù tên repo không chứa từ khóa đó.

Phạm vi nội dung hiện là README được GitHub lập chỉ mục, chưa tìm toàn bộ source
code hoặc mọi file trong repository. Khi từ khóa trống, cả hai lựa chọn vẫn lấy
Trending và xếp theo số stars mới trong kỳ giảm dần.
