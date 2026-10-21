# GitHub Trending Analyzer — Chức năng và hướng dẫn

Bản đóng gói ngày 01/10/2026. Tài liệu mô tả hành vi của mã nguồn đi kèm.

## 1. Mục đích

Tìm repository công khai trên GitHub, theo dõi stars mới và đọc tài liệu để
hiểu project làm gì, hoạt động thế nào, phù hợp với ai và còn giới hạn gì.
Công cụ có dashboard local, CLI và xuất báo cáo. Không cần package Python bên ngoài.

## 2. Cài đặt và chạy

Yêu cầu: Python 3.8 trở lên, kết nối Internet và chứng chỉ TLS hợp lệ cho Python.
Không cần Node.js, cơ sở dữ liệu hoặc API key ở chế độ mặc định.

Giải nén ZIP, mở terminal trong thư mục `github-trending-analyzer`, chạy:

```bash
python3 gh_trending.py --serve
```

Trên Windows có thể dùng `py -3 gh_trending.py --serve`.
Trên macOS/Linux cũng có thể dùng launcher:

```bash
chmod +x trending
./trending --serve
```

Mở `http://127.0.0.1:8766/`. Nhấn Ctrl+C ở terminal để dừng.
Nếu port đang được dùng:

```bash
python3 gh_trending.py --serve --port 8767 --no-browser
```

Server chỉ chạy trên máy local. File HTML xuất riêng không thay thế server tìm kiếm.

## 3. Tìm project trên dashboard

| Điều khiển | Chức năng |
|---|---|
| Từ khóa | Nhập một từ hoặc nhiều từ khóa ngăn cách bằng dấu phẩy |
| Tìm kiếm theo tên project | GitHub Search với `in:name` |
| Tìm theo nội dung project | GitHub Search với `in:readme`; tìm nội dung README được lập chỉ mục |
| Số lượng project | Từ 1 đến 30; có thể nhận ít hơn nếu GitHub không đủ kết quả |
| Cách khớp | Khớp tất cả hoặc ít nhất một từ khóa |
| Ngôn ngữ | Giới hạn ngôn ngữ lập trình của repository |
| Sắp xếp khi có từ khóa | Phù hợp nhất, tổng stars giảm dần hoặc cập nhật gần nhất |
| Kỳ Trending | Hôm nay, tuần này hoặc tháng này; dùng khi từ khóa trống |
| Phân tích sâu | Tải README mới, metadata và tài liệu liên kết trước khi phân tích |
| Tìm kiếm / Enter | Gọi GitHub và phân tích danh sách project mới |

Ví dụ: chọn **Tên project**, nhập `ml-agents`, số lượng `1` để tìm theo tên.
Chọn **Nội dung README**, nhập `voice cloning` để tìm chức năng dù tên repo
không có cụm từ đó. Chế độ nội dung chưa tìm toàn bộ source code hoặc mọi file.
Kết quả loại bỏ fork và repository archived, chỉ lấy repository công khai.

### Khi để trống từ khóa

Lấy toàn bộ danh sách GitHub Trending của kỳ/ngôn ngữ đã chọn, xếp theo số
stars mới giảm dần rồi mới lấy số lượng yêu cầu. Khi bằng số stars mới,
ưu tiên tổng stars lớn hơn rồi theo tên. Đây là xếp hạng trong danh sách
Trending GitHub cung cấp, không phải toàn bộ repository trên GitHub.

Các lựa chọn cách khớp và sắp xếp tìm kiếm bị vô hiệu hóa khi từ khóa trống.
Kỳ Trending bị vô hiệu hóa khi có từ khóa. Dữ liệu GitHub có thể thay đổi
giữa các lần tìm; thứ tự ổn định nếu dữ liệu nguồn không đổi.

### Bộ đếm và lọc sau khi tải

Dashboard ghi số đang hiển thị, số đã tải và tổng kết quả GitHub báo về.
Với Trending, tổng là số project trong trang Trending đã lấy. Tổng GitHub
Search không có nghĩa công cụ đã tải tất cả các kết quả đó.

Bộ lọc phân loại, độ hoàn thiện, bứt phá (Trending), khớp sở thích và thay thế
thương mại chỉ lọc danh sách đã tải. **Xóa bộ lọc** reset form và các bộ lọc,
không gọi GitHub và không tự tải danh sách khác. Nếu tìm kiếm lỗi, giữ lại
kết quả trước đó và hiển thị thông báo.

## 4. Tăng trưởng project

| Loại kết quả | Dữ liệu hiển thị |
|---|---|
| Trending | Stars mới trong kỳ ngày/tuần/tháng từ trang GitHub Trending; nhãn velocity theo heuristic |
| Tìm theo tên hoặc README | Tổng stars riêng; stars mới hôm nay, 7 ngày và 30 ngày từ GitHub Star History API |

Cửa sổ 7/30 ngày bao gồm ngày hiện tại, chưa kết thúc. Lịch sử được gom từ
bucket ngày của GitHub; ranh giới ngày có thể lệch UTC. Đây là số lượt thêm
star, không trừ lượt bỏ star và không phải phần trăm tăng trưởng ròng.

Tăng trưởng tìm kiếm được cache trong bộ nhớ server tối đa 10 phút. Khởi động
lại server xóa cache này. Nếu API lỗi, giới hạn truy cập hoặc thiếu ngày trong
một cửa sổ, cửa sổ đó ghi **Chưa có dữ liệu**. Số **+0** chỉ dùng khi có dữ liệu
đủ xác nhận không có stars mới trong cửa sổ tương ứng. Kết quả Search không
được tự gắn nhãn GitHub Trending hoặc Breakout.

Nguồn: [GitHub Star History API](https://docs.github.com/en/rest/activity/starring#get-repository-star-history).

## 5. Nội dung phân tích trên thẻ project

- Tên, link GitHub, ngôn ngữ, tổng stars và tăng trưởng.
- Tác dụng cốt lõi, mô tả, phân loại và tính năng trích từ tài liệu.
- Tech stack và lệnh chạy thử nếu tìm thấy. Nút **Copy** chỉ sao chép lệnh,
  công cụ không tự chạy hoặc cài project được tìm thấy.
- Chuyên ngành/vị trí phù hợp và bài toán thực tế theo bộ phân tích.
- Điểm phù hợp với watchlist, nhãn độ hoàn thiện, nhận diện thay thế thương mại.
- Mục mở rộng **Phân tích sâu**: cơ chế/kiến trúc, ví dụ, giới hạn, điều kiện
  áp dụng, so sánh, bằng chứng, nguồn và thông tin còn thiếu.

Các nhãn độ hoàn thiện, velocity, phân loại, phù hợp và thay thế là kết quả
heuristic từ mô tả/tài liệu/stars, không phải kiểm chứng production hoặc
đánh giá bảo mật. Công cụ không chạy repo, không xác minh benchmark, không
thu thập release/news tự động và không đọc toàn bộ code.

### Phân tích thường và sâu

Chế độ thường đọc README, có thể dùng cache trên đĩa `.cache/` chưa có TTL.
Chế độ sâu yêu cầu README mới, thêm metadata GitHub và tối đa 3 tài liệu
văn bản được README liên kết trong cùng repo. Không tự thu thập tài liệu
ngoài repository. Nguồn tải thất bại và khoảng trống bằng chứng được ghi rõ.

### Heuristic và AI

Mặc định dùng heuristic: trích nội dung từ tài liệu, có thể giữ tiếng Anh.
Bật `--ai` để gửi nội dung cho Gemini tổng hợp bằng tiếng Việt. Nếu thiếu
key, API lỗi hoặc kết quả sai schema, dùng heuristic và ghi cảnh báo ở terminal.
Tên engine thực sự dùng được ghi trong kết quả.

```bash
# Chỉ bật AI khi muốn dùng tài khoản API Gemini của mình
export GEMINI_API_KEY="your_api_key_here"
python3 gh_trending.py --serve --deep --ai
```

Model: `--model`, rồi `GEMINI_MODEL`, mặc định `gemini-3.1-flash-lite`.
Tìm kiếm và heuristic là request Python tới GitHub, không gọi Codex.
Chế độ AI gọi API Gemini riêng và có thể phát sinh phí theo tài khoản provider.

## 6. Watchlist

Chỉnh `watchlist.json`: `keywords`, `languages`, `categories` là các danh sách
sở thích. Server đọc cấu hình lúc khởi động; sửa file xong cần chạy lại server.
Dashboard hiển thị Match Score và có checkbox lọc project điểm lớn hơn 0.
CLI dùng `--watchlist` để chấm điểm/ưu tiên hoặc `--match` cho từ khóa tức thì.

```bash
python3 gh_trending.py --watchlist --since weekly
python3 gh_trending.py --match "agent,rag,rust"
```

## 7. CLI và xuất tài liệu

```bash
python3 gh_trending.py --help
python3 gh_trending.py --lang python --since weekly --limit 5
python3 gh_trending.py --deep --limit 5 -o deep_report.md
python3 gh_trending.py --web --watchlist
python3 gh_trending.py --json > results.json
python3 gh_trending.py --min-maturity beta --alt
python3 gh_trending.py -i
```

`--web`/`--html` sinh snapshot `trending_dashboard.html`: lọc dữ liệu có sẵn,
không tìm project mới trên GitHub. `--serve` cung cấp dashboard tìm kiếm live.
`-o` xuất Markdown; `--json` xuất dữ liệu phân tích. `--no-readme` chỉ phân tích
mô tả và không kết hợp với `--deep`. CLI Trending lấy giới hạn từ scraper;
quy tắc xếp toàn trang theo stars mới trước giới hạn áp dụng cho dashboard live.

Menu `-i`: nhập số để xem repo, `o 1` mở repo, `w` mở snapshot, `q` thoát.
Trong chế độ `--serve`, dùng form để chọn từ khóa/ngôn ngữ/số lượng; các cờ
lọc CLI như `--alt`, `--match`, `--since`, `--limit` không cấu hình form server.

## 8. Cấu hình môi trường

| Biến | Mục đích |
|---|---|
| `GITHUB_TOKEN` | Tùy chọn cho GitHub Search và star history; không làm kết quả trở thành repo private |
| `GEMINI_API_KEY` | Dùng khi bật `--ai` |
| `GEMINI_MODEL` | Chọn model nếu không truyền `--model` |
| `GH_TRENDING_PYTHON` | Chọn interpreter cho launcher `./trending` |

`.env.example` chỉ là mẫu, chương trình **không tự nạp `.env`**. Đặt biến trong
môi trường terminal trước khi chạy. Với server, dùng biến `GEMINI_API_KEY`;
cờ `--gemini-key` hiện chỉ được truyền vào pipeline CLI.

## 9. Luồng xử lý và cấu trúc mã

Dashboard → `POST /api/search` → kiểm tra input → GitHub Trending/Search →
phân tích tối đa 4 project song song → bổ sung lịch sử stars cho Search → JSON → thẻ.
Server nhận tối đa 2 request phân tích cùng lúc; lượt dư nhận thông báo bận.

| File | Vai trò |
|---|---|
| `gh_trending.py`, `trending` | CLI và launcher |
| `src/search_server.py` | HTTP local, truy vấn, điều phối phân tích |
| `src/scraper.py` | Thu thập/parser Trending và TLS |
| `src/growth.py` | Lịch sử stars, gom cửa sổ thời gian, cache |
| `src/fetcher.py`, `src/research.py` | README/cache, metadata và tài liệu liên kết |
| `src/analyzer.py` | Model dữ liệu, heuristic và Gemini |
| `src/maturity.py`, `src/alternatives.py`, `src/watchlist.py` | Nhãn đánh giá và điểm sở thích |
| `src/html_dashboard.py`, `src/formatter.py` | Dashboard, terminal, Markdown |
| `tests/` | Kiểm tra tự động |

Server kiểm tra Host/Origin local; không phục vụ file workspace hoặc key.
HTML escape dữ liệu repo và JSON nhúng; nội dung tài liệu không được thực thi.

## 10. Kiểm tra và xử lý lỗi

```bash
python3 -m unittest discover -s tests -q
```

Bản mã nguồn trước đóng gói đạt 45 kiểm tra. Kiểm tra tự động dùng dữ liệu mock,
không đảm bảo GitHub/Gemini luôn hoạt động hoặc trả cùng kết quả trong tương lai.

| Hiện tượng | Cách xử lý |
|---|---|
| Không vào được dashboard | Chạy server, kiểm tra đúng port và `127.0.0.1` |
| Nút tìm chỉ lọc danh sách cũ | Đang mở snapshot; chạy `--serve` |
| GitHub giới hạn/từ chối | Đợi rồi thử lại; tùy chọn cấu hình `GITHUB_TOKEN` |
| Tăng trưởng chưa có dữ liệu | API lỗi hoặc thiếu lịch sử; không suy ra project không tăng |
| Nội dung còn tiếng Anh | Heuristic giữ nội dung gốc; bật AI nếu cần diễn giải |
| Thiếu nguồn/README | Xem research gaps và kiểm tra kết nối/repo gốc |
| Lỗi TLS | Cấu hình chứng chỉ Python; không tắt xác minh TLS |

## 11. Thành phần ZIP

ZIP chứa mã nguồn, tests, launcher, watchlist, `.env.example`, README,
tài liệu này, tài liệu review/mẫu nghiên cứu và skill tích hợp đi kèm.
Không chứa `.git`, môi trường Python, cache tải về, credentials hoặc báo cáo
HTML/Markdown sinh ở các lượt chạy trước. Có thể tạo lại báo cáo từ CLI.

Chạy `python3 scripts/package_release.py` để tạo lại ZIP cùng manifest SHA-256.
