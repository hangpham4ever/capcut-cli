---
name: video-su-phu
description: Làm video Facebook theo mẫu "Sư Phụ dạy" (trang Hang Pham) — khung 3:4 hai tầng, tựa đề neon, thẻ minh họa đánh số, phụ đề tiếng Việt, chừa vùng an toàn Facebook. Dùng khi người dùng gửi video (link Google Drive/Facebook) và muốn dựng theo phong cách Sư Phụ / Clip <số>.
---

# Video "Sư Phụ dạy"

Đọc và làm đúng theo `video-templates/su-phu-6-dieu/HUONG-DAN.md` (ở gốc repo). Mẫu thiết kế là `frame.html`, script dựng lớp chữ là `render-overlays.js` trong cùng thư mục. Xem `examples/` để biết khung đúng trông thế nào.

Tóm tắt bắt buộc:
1. Tải video người dùng gửi, chép lời bằng Whisper `--model medium --language vi`.
2. Rút ra tựa đề + các ý chính từ lời Sư Phụ; hỏi lại chỗ nghe không rõ. Hỏi **số clip và ngày** cho nhãn `Clip <số> || <ngày>`. Luôn ghi **"Sư Phụ"**.
3. Copy `frame.html` sang thư mục làm việc, sửa nội dung (tựa đề, cột vàng, thẻ, khung lớn, thanh vàng). Mọi chữ phải nằm trong **vùng an toàn bản "cân bằng"** (xem HUONG-DAN.md: giữ bố cục to, chữ trong x 110–970, y 68–1372 của khung 1080×1440).
4. Gửi **khung hình mẫu + ảnh mô phỏng bảng tin/Reels** để người dùng duyệt TRƯỚC khi ghép.
5. Ghép video bằng ffmpeg theo hướng dẫn, gửi video + `.srt` + gợi ý chú thích Facebook. Nhắc người dùng tải về (container là tạm thời).

Nội dung: trình bày đúng lời Sư Phụ nói; không tự bịa tin tức, con số hay trích dẫn.
