---
name: video-su-phu
description: Làm video Facebook theo mẫu "Sư Phụ dạy" (trang Hang Pham) — 4 phong cách (6 điều / So sánh 2 hình / Vì-Nên Xưa-Nay / Thiên khải), khung 3:4, chữ nhảy, tựa đề neon, thẻ minh họa đánh số, phụ đề tiếng Việt, chừa vùng an toàn Facebook. Dùng khi người dùng gửi video (link Google Drive/Facebook) và muốn dựng theo phong cách Sư Phụ / Clip <số>.
---

# Video "Sư Phụ dạy"

**Có 4 phong cách — hỏi người dùng muốn dùng phong cách nào nếu họ chưa nói:**
- **Mặc định "6 điều"** (danh sách đánh số, thẻ sáng dần): `video-templates/su-phu-6-dieu/`
- **A "So sánh 2 hình"** (hộp vàng + câu móc ⁉️ chữ nhảy + 2 ô hình có nhãn xanh): `video-templates/phong-cach-moi/styleA.html`
- **B "Vì/Nên – Xưa/Nay"** (người nói phủ kín khung, tựa xanh phát sáng chữ nhảy, "TẠI SAO !?", nhãn vàng + đoạn chữ): `video-templates/phong-cach-moi/styleB.html`
- **C "Thiên khải"** (nền vũ trụ, chữ vàng ánh kim, khung video viền vàng, thẻ "Ý k/N"; không ghi số clip/ngày): `video-templates/thien-khai/`
Đọc thêm `video-templates/phong-cach-moi/HUONG-DAN.md` khi dùng A hoặc B, `video-templates/thien-khai/HUONG-DAN.md` khi dùng C.

## ⭐ Người dùng đã dặn – luôn làm
- **Bố cục rộng**, không thu nhỏ dồn vào giữa: khung video và thẻ rộng khoảng x 80–1000. Chữ quan trọng vẫn nằm trong vùng an toàn (xem `video-templates/thien-khai/HUONG-DAN.md`).
- **Tựa đề luôn có hiệu ứng động** nổi bật (chữ rơi vào, vệt sáng quét, chữ "thở", sao lấp lánh hoặc chữ nhảy). Thẻ hoặc ý mới thì bật lên. Không để chữ đứng yên suốt video.
- Ngoài người nói đang cử động, chữ trên màn hình cũng phải có chuyển động để người xem không thấy nhàm chán.

Đọc và làm đúng theo `video-templates/su-phu-6-dieu/HUONG-DAN.md` (ở gốc repo). Mẫu thiết kế là `frame.html`, script dựng lớp chữ là `render-overlays.js` trong cùng thư mục. Xem `examples/` để biết khung đúng trông thế nào.

Tóm tắt bắt buộc:
1. Tải video người dùng gửi, chép lời bằng Whisper `--model medium --language vi`.
2. Rút ra tựa đề + các ý chính từ lời Sư Phụ; hỏi lại chỗ nghe không rõ. Hỏi **số clip và ngày** cho nhãn `Clip <số> || <ngày>`. Luôn ghi **"Sư Phụ"**.
3. Copy `frame.html` sang thư mục làm việc, sửa nội dung (tựa đề, cột vàng, thẻ, khung lớn, thanh vàng). Mọi chữ phải nằm trong **vùng an toàn bản "cân bằng"** (xem HUONG-DAN.md: giữ bố cục to, chữ trong x 110–970, y 68–1372 của khung 1080×1440).
4. Gửi **khung hình mẫu + ảnh mô phỏng bảng tin/Reels** để người dùng duyệt TRƯỚC khi ghép.
5. Ghép video bằng ffmpeg theo hướng dẫn, gửi video + `.srt` + gợi ý chú thích Facebook. Nhắc người dùng tải về (container là tạm thời).

Nội dung: trình bày đúng lời Sư Phụ nói; không tự bịa tin tức, con số hay trích dẫn.
