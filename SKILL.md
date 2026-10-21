---
name: github-trending-analyzer
description: Tự động cào và phân tích chuyên sâu các repository đang thịnh hành trên GitHub Trending (https://github.com/trending). Giải thích rõ tác dụng cốt lõi, vấn đề giải quyết, tính năng nổi bật và bối cảnh ứng dụng thực tế bằng tiếng Việt mỗi khi người dùng yêu cầu.
---

# GitHub Trending Analyzer Skill

Kỹ năng tự động theo dõi, thu thập và bóc tách các dự án mã nguồn mở đang thịnh hành trên GitHub Trending theo ngày (`daily`), tuần (`weekly`), tháng (`monthly`) hoặc theo từng ngôn ngữ lập trình cụ thể (`python`, `rust`, `go`, `typescript`,...).

## Khi nào kích hoạt Skill này?
Kích hoạt mỗi khi người dùng có các yêu cầu như:
- "Phân tích github trending hôm nay"
- "Hôm nay có repo nào hot trên GitHub?"
- "Các dự án trending trên GitHub đang làm gì, tác dụng ra sao?"
- "Xem trending tuần này của Python / Rust / TypeScript"
- "GitHub trending có công cụ AI / DevOps nào mới?"

## Quy trình thực thi

### Bước 1: Thu thập dữ liệu Trending
Chạy lệnh Python trong workspace để lấy dữ liệu mới nhất (đã hỗ trợ chế độ zero-dependency chuẩn):
```bash
./trending --since daily --limit 10 --json
# Hoặc lọc theo ngôn ngữ:
./trending --lang python --since weekly --limit 5 --json
```

### Bước 2: Bóc tách & Phân tích tác dụng (Deep Dissection)
Với mỗi repository được chọn, phân tích theo cấu trúc 5 điểm cốt lõi bằng tiếng Việt:
1. **📦 Tên & Thông tin cơ bản:** Link repo, tác giả, ngôn ngữ, số stars mới nhận hôm nay/tuần này.
2. **🎯 Tác dụng cốt lõi (Core Purpose):** Dự án này sinh ra để làm gì? Giải quyết nỗi đau/khó khăn nào mà lập trình viên gặp phải? Thay thế hoặc cải tiến công cụ nào?
3. **💡 Tính năng nổi bật & Điểm ăn tiền (Key Highlights):** 2-3 tính năng tạo nên sự khác biệt.
4. **👥 Đối tượng & Bối cảnh sử dụng (Target Audience & Use Cases):** Ai nên dùng (AI Engineer, Backend Dev, DevOps...)? Khi nào thì nên áp dụng vào dự án thực tế?
5. **🚀 Đánh giá & Lý do đang hot:** Điểm đột phá về mặt công nghệ hoặc lý do dự án thu hút cộng đồng.

### Bước 3: Trình bày kết quả
- Trình bày dạng thẻ (Card/Markdown) rõ ràng, sử dụng biểu tượng trực quan.
- Có thể gợi ý người dùng mở Dashboard HTML trực quan bằng cách chạy `./trending --web`.
