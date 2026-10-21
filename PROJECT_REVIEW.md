# Review GitHub Trending Analyzer

Ngày review: 01/10/2026.

## Nhận định

Project có nền tảng tốt cho công cụ khám phá repository cá nhân: Python standard library, phân tách scraper/fetcher/analyzer/formatter, cùng một dữ liệu phục vụ CLI, JSON, Markdown và dashboard. Watchlist và nhận diện alternative là hai hướng đáng giữ vì giúp chuyển từ xem danh sách trending sang tìm công cụ phù hợp.

Ưu tiên tiếp theo nên là độ tin cậy và tính cụ thể của nghiên cứu. Hiện nhiều kết luận tích cực được tạo từ template hoặc từ khóa, chưa đủ bằng chứng để dùng làm quyết định lựa chọn công cụ. Không cần viết lại project hoặc thêm framework web ở giai đoạn này.

Phạm vi: đọc source, tài liệu, báo cáo mẫu và tests; chạy unit tests và các probe Python offline. Không chỉnh sửa source trong lần review này. Không chạy dashboard trong trình duyệt, không gọi API AI có tính phí, không xác minh lại từng repo trong report.md trên GitHub.

## Các chỉnh sửa ưu tiên

### 1. P1 — Kết luận nghiên cứu cần bằng chứng

Vị trí: `src/analyzer.py:459-537`, đặc biệt fallback tại 504-510.

Khi không trích được features, analyzer tự thêm nhận xét như tối ưu hiệu năng, thay thế công cụ thương mại và tài liệu sẵn sàng triển khai. Đây là những thông tin chưa được kiểm tra. `why_trending` suy diễn nguyên nhân từ số sao; số sao chỉ chứng minh lượng quan tâm, không xác định được nguyên nhân. Knowledge base `KNOWN_REPOS_VI` cũng cần nguồn và ngày kiểm tra để tránh nội dung cũ được dùng mãi.

Chỉnh sửa đề xuất:

- Tách thông tin trích từ nguồn, nhận định của analyzer và dữ liệu chưa đủ.
- Thay fallback features bằng danh sách rỗng và thông báo thiếu dữ liệu.
- Thêm evidence cho từng nhận xét: URL nguồn, đoạn trích hoặc section, thời điểm lấy dữ liệu.
- Lý do trending chưa có release/news chứng minh phải ghi là giả thuyết hoặc chưa xác định.
- Giữ mô tả gốc nếu heuristic không dịch được, thay vì tạo câu tiếng Việt chung chung.
- Thêm loại repository: tool, library, model, tutorial/course, resource list, dataset. Các loại này cần tiêu chí đánh giá khác nhau.

Ví dụ từ report.md: `cs341-illinois/coursebook` được phân loại Web & Frontend và Production Ready. Cần kiểm tra đúng loại repository trước khi áp dụng tiêu chí triển khai phần mềm.

### 2. P1 — Maturity đang khẳng định quá mạnh

Vị trí: `src/maturity.py:121-184`.

Probe offline: README chỉ chứa `badge.svg`, `pip install sample`, `docker run sample`, với 0 stars, vẫn nhận Production Ready. Bộ chấm điểm không xác minh CI có chạy đạt, releases, license thực tế hay trạng thái bảo trì. Không có README cũng có thể bị diễn giải thành Experimental, trong khi thực tế chỉ thiếu dữ liệu.

Chỉnh sửa đề xuất:

- Đổi nhãn hiện tại thành tín hiệu về độ hoàn thiện, thêm `unknown` khi thiếu dữ liệu.
- Thu thập metadata: archived, license, release gần nhất, hoạt động commit, trạng thái CI nếu có quyền truy cập.
- Hiển thị các tín hiệu đã kiểm tra và các tín hiệu chưa biết.
- Không coi star count là bằng chứng đủ cho độ ổn định hoặc chất lượng.
- Dùng tiêu chí riêng cho course/list/dataset thay vì gắn Production Ready.

### 3. P1 — Chế độ AI gọi model đã ngừng phục vụ và fallback im lặng

Vị trí: `src/analyzer.py:541-648`, endpoint tại 590.

Code hardcode `gemini-1.5-flash`. Theo [Google Gemini API release notes](https://ai.google.dev/gemini-api/docs/changelog), model này đã shutdown ngày 29/09/2025. Lỗi bị bắt chung và trả `None`, khiến yêu cầu `--ai` chuyển sang heuristic mà không có cảnh báo rõ ràng.

Chỉnh sửa đề xuất:

- Cho chọn model bằng cấu hình hoặc `--model`; kiểm tra model đang được provider hỗ trợ khi triển khai.
- Phân loại lỗi: thiếu key, model không tồn tại, rate limit, timeout, JSON không hợp lệ.
- Cảnh báo fallback qua stderr; xuất `engine_used`, model và trạng thái fallback trong mọi giao diện.
- Validate kiểu dữ liệu JSON trả về, đặc biệt các trường list/string.
- Chuẩn hóa taxonomy: AI đang được phép tạo category tự do, có thể làm lệch watchlist.
- Bổ sung suitable_major, target_roles, real_world_impact hoặc điều chỉnh giao diện để hiển thị target_audience/use_cases của AI. Hiện dashboard thiên về các trường heuristic, nên AI có thể cho card thiếu nội dung.
- Tham số `openai_api_key` hiện chưa có implementation; bỏ tham số hoặc thực sự làm adapter provider.

### 4. P1 — Dashboard chèn dữ liệu bên ngoài vào HTML/JavaScript

Vị trí: `src/html_dashboard.py:20`, 372-456.

JSON được đặt trực tiếp trong script; dữ liệu repo/AI được nối vào `innerHTML`. Quick Run còn được đặt trong thuộc tính `onclick`. Probe xác nhận chuỗi `</script><script>window.__probe=1</script>` xuất hiện nguyên vẹn trong tài liệu sinh ra. Điều này tạo đường chèn script; probe mới xác nhận HTML sinh ra, chưa thực thi payload trong browser.

Chỉnh sửa đề xuất:

- Khi nhúng JSON trong script, escape ký tự `<` thành chuỗi JSON `\u003c` để không đóng script ngoài ý muốn.
- Dùng DOM API và `textContent` cho dữ liệu; validate URL trước khi gán href.
- Gắn event listener cho Copy thay vì ghép lệnh vào inline onclick.
- Kiểm tra với dữ liệu chứa dấu nháy, HTML, xuống dòng và script terminator.

### 5. P1 — Quick Run cắt mất tham số quan trọng

Vị trí: `src/maturity.py:187-237`.

Các probe đã tái hiện:

| Lệnh gốc | Kết quả hiện tại |
|---|---|
| `pip install tool==1.2.3` | `pip install tool` |
| `npx skills add owner/repo` | `npx skills add` |
| `docker run -e TOKEN=$TOKEN image` | `docker run -e TOKEN=` |

Chỉnh sửa đề xuất: đọc code block đầy đủ trong section Installation/Quick Start; giữ nguyên dòng lệnh và tham số, kèm nguồn và prerequisites. Nếu không đủ thông tin, không xuất lệnh. Trong report.md cũng đã có `npx skills add` được đưa ra làm lệnh chạy VoiceStudio, nhưng lệnh này không có đối tượng cần cài và chưa chứng minh là lệnh chạy ứng dụng.

### 6. P2 — Dữ liệu có thể cũ và thiếu provenance

Vị trí: `src/fetcher.py:24-51`.

Cache README không có TTL hoặc mốc commit. Bất kỳ cache có nội dung đều được dùng tiếp, nên số sao mới có thể đi cùng mô tả/commands cũ.

Đề xuất: lưu fetched_at, source_url, branch/commit khi có; TTL cấu hình được, `--refresh`, cơ chế stale-cache fallback có nhãn rõ ràng. Dùng khóa cache không bị va chạm do nối owner/repo bằng underscore. Báo cáo cần thời điểm dữ liệu được thu thập, không chỉ thời điểm HTML được tạo.

### 7. P2 — Velocity và personalization cần làm rõ ý nghĩa

Vị trí: `src/maturity.py:31-67`, `src/watchlist.py:65-135`, `gh_trending.py:174-235`.

- Velocity không nhận timeframe, vì vậy +350 stars/ngày và +350 stars/tháng bị dùng cùng ngưỡng. Tách stars_in_period, stars_per_day ước tính và tỷ trọng so với tổng sao. Nếu gọi là phần trăm tăng trưởng thì cần xác định mẫu số; `since/total` hiện là tỷ trọng trên tổng hiện tại.
- Không có ngày tạo repo thì nhãn mới nổi chỉ là suy đoán từ tổng sao thấp.
- Match Score là điểm heuristic, không phải xác suất phù hợp. Đổi `%` thành `/100`, hoặc giải thích cách tính cạnh score.
- Probe: `--match rust` không match repo có language Rust nếu corpus không có chữ rust. Thêm language vào corpus hoặc cú pháp rõ `lang:rust`.
- Keyword-only match bị giới hạn 50 điểm, kể cả tất cả keywords đều phù hợp. Nên chuẩn hóa theo những nhóm tiêu chí thực sự được người dùng cấu hình.
- CLI cắt top N trước khi lọc và xếp hạng. Nên thu thập đủ candidate, lọc/rank rồi lấy N; hiển thị phạm vi dữ liệu để người dùng hiểu kết quả.

### 8. P2 — Network/CLI cần lỗi rõ và hành vi ổn định

- `src/scraper.py:13-21`: nếu import certifi lỗi hoặc không có certifi, code tắt xác minh TLS. Trong môi trường review certifi có mặt, context thực tế vẫn xác minh TLS. Sửa fallback thành `ssl.create_default_context()`; lỗi certificate cần hướng dẫn khắc phục.
- README fetch thử nhiều URL tuần tự, bắt mọi lỗi như nhau. Thêm retry/backoff cho lỗi tạm thời; giới hạn timeout toàn repo; phân biệt 404 với rate limit/network.
- `analyze_batch` tuần tự; cân nhắc ThreadPoolExecutor với số workers giới hạn cho tải README, giữ thứ tự output và hạn chế request.
- Validate `--limit > 0`.
- `--json` vẫn in thông báo text vào stdout trong trường hợp lỗi/không có repo. Giữ stdout là JSON, đưa diagnostic sang stderr.
- Quy định rõ kết hợp `--json` với `--output`/`--web`; hiện JSON return sớm khiến các lựa chọn sau không thực hiện.
- Watchlist lỗi parse hiện bị nuốt; cần cảnh báo và validate cấu trúc config.
- Nếu HTML GitHub đổi làm parser không tìm thấy article, cần cảnh báo parser thay vì mặc định diễn giải thành không có trending.

## Update đáng làm cho mục tiêu research

1. Snapshot và lịch sử bằng SQLite: giữ nguồn, thời gian, GitHub rank, stars trong kỳ và phân tích; nhận diện repo xuất hiện lần đầu hoặc quay lại trending.
2. Hai mức nghiên cứu: scan toàn candidate bằng heuristic; chỉ phân tích sâu shortlist. Tách giới hạn candidate và giới hạn deep research.
3. Bản phân tích theo quyết định: làm gì, phù hợp trường hợp nào, khác gì alternatives, license, chi phí/API/GPU, độ khó cài, hạn chế và bằng chứng.
4. Lưu trạng thái nghiên cứu: chưa đọc, muốn thử, đã thử, đã áp dụng, bỏ qua; kèm ghi chú. Dùng các quyết định này để cải thiện personalization sau này.
5. Dashboard có bảng tổng quan ngắn và card chi tiết khi mở; hiển thị nguồn, tuổi dữ liệu, engine và các trường thiếu dữ liệu.

## Thứ tự triển khai đề xuất

| Đợt | Nội dung | Điều kiện hoàn thành |
|---|---|---|
| 1 | AI model/fallback, Quick Run, HTML injection, TLS fallback, bỏ kết luận không có nguồn | Có regression tests cho lỗi đã tái hiện; lỗi và thiếu dữ liệu được hiển thị rõ |
| 2 | Metadata, evidence, cache TTL, repo type, maturity/velocity/match semantics | Mỗi kết luận có nguồn hoặc trạng thái suy luận/chưa đủ dữ liệu; lọc/rank trước limit |
| 3 | Snapshot/history, shortlist/deep analysis, ghi chú và dashboard tổng quan | So sánh được giữa các lần chạy và quản lý được quyết định thử công cụ |

## Kiểm chứng và giới hạn

- `python3 -m unittest discover tests -v`: 22/22 tests đạt.
- Probe offline xác nhận false positive maturity, mất tham số Quick Run, match language và chèn script terminator nguyên vẹn.
- Tests hiện tập trung vào trường hợp thuận lợi của các hàm phân tích. Cần bổ sung fetch/cache, AI fallback/schema, CLI filter/limit/JSON và dashboard escaping.
- Chưa kiểm chứng browser rendering/Copy/filter hoặc kết nối AI thực tế; unit tests đạt không chứng minh các đường này chạy đúng.
- Git hiện có một commit `Initial commit`; các file project hiển thị untracked. Không đủ lịch sử để đánh giá diff của các update trước đây. Sau khi có `.gitignore` cho cache/venv/secrets, nên tạo baseline source và tách generated reports khỏi source để quản lý thay đổi rõ ràng.
