# Mẫu video "Sư Phụ dạy" (Clip 441)

Mẫu video đăng Facebook theo phong cách trang Hang Pham. Đọc file này trước khi làm clip mới.

## Phong cách (học từ 5 video mẫu)
- Khung **3:4 (1080×1440)**, chia 2 tầng: **tầng trên** là người nói đứng ngoài trời; **tầng dưới** là nền đỏ đậm có tia sáng, chứa thẻ minh họa hoặc khung lớn.
- Nhãn trên cùng: pill đỏ viền trắng, có logo YouTube, ghi `Clip <số> || <ngày>`. **Hỏi người dùng số clip và ngày.**
- Cột vàng bên trái: "Sư Phụ / dạy / ..." (luôn ghi **Sư Phụ**, không ghi "Thầy").
- Tựa đề chính: dòng 1 chữ Anton xanh neon, dòng 2 chữ vàng trên nền đỏ viền trắng, đặt nghiêng -4°, có gạch đỏ.
- Thẻ minh họa đánh số có biểu tượng cấm: điều đang nói thì sáng viền vàng, điều đã nói giữ nguyên, điều chưa nói thì mờ.
- Phụ đề chạy theo lời nói, chữ trắng viền đen. Thanh vàng tóm tắt ở dưới.
- Đoạn giải thích hoặc kết luận dùng khung lớn viền vàng (`mode=dna`, `mode=end`).
- Video ngắn, chủ đề nóng, kết luận dứt khoát thì nhiều lượt xem nhất.

## VÙNG AN TOÀN – bản "cân bằng" (người dùng chọn)
Người dùng **thích bố cục to, đầy như bản đầu**, chỉ cần không bị tràn khi đăng. Đừng thu nhỏ quá.
- Bảng tin cắt về 4:5, **mất khoảng 60px ở trên và ở dưới** => pill để từ y≥68, thanh vàng đặt ở y 1306–1372 (không sát đáy).
- Reels cắt về 9:16, **mất khoảng 135px mỗi bên** => cột vàng để từ x≥120; thẻ, phụ đề, khung lớn đặt trong x 110–970. Mép thẻ ngoài cùng có thể bị cắt nhẹ trên Reels, chấp nhận được.
- Chỉ phần nền (video, màu nền) được tràn ra ngoài.
- Luôn tạo ảnh mô phỏng 3 kiểu hiển thị (khung đầy đủ / bảng tin crop 1080×1320 từ y=60 / Reels crop 810 rộng, x=135) để kiểm tra trước khi gửi. Xem `examples/kiem_tra_vung_an_toan.jpg`.

## Quy trình
1. Tải video (Google Drive: `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`; Facebook: `yt-dlp`).
2. Chép lời: `whisper src.mov --model medium --language vi` (bản small nghe sai nhiều). **Hỏi lại người dùng những chỗ nghe không rõ.**
3. Viết `segments.json`: `[giây_bắt_đầu, giây_kết_thúc, "1".."6" | "dna" | "end", "phụ đề"]`. Sửa nội dung thẻ trong `frame.html` (mảng `items`, tựa đề, cột vàng, thanh vàng, khung lớn).
4. Gửi **khung hình mẫu để người dùng duyệt trước**, sau đó mới ghép video.
5. Tạo lớp chữ: `WORK=<thư mục> NODE_PATH=$(npm root -g) node render-overlays.js` (frame.html, segments.json và ảnh nằm trong WORK).
6. Ghép video (video gốc quay ngang 1920×1080, người nói ở giữa):
   ```
   ffmpeg -i src.mov -f concat -safe 0 -i ov/list.txt -filter_complex "[0:v]crop=1440:960:200:100,scale=1080:720,pad=1080:1440:0:0:black,setsar=1,fps=30[b];[1:v]fps=30,format=rgba[o];[b][o]overlay=0:0:eof_action=repeat,format=yuv420p[v]" -map "[v]" -map 0:a -c:v libx264 -crf 20 -c:a aac -movflags +faststart out.mp4
   ```
   Chỉnh `crop` nếu người nói đứng lệch. Đầu người nói phải nằm dưới pill.
7. Gửi video, file `.srt` và gợi ý chú thích Facebook (emoji ⚠️🙏 + tóm tắt ý chính).

## Công cụ cần có
Setup script của môi trường cloud đã cài sẵn: FFmpeg, Whisper, VieNeu-TTS, Hyperframes, Remotion, Playwright/Chromium. Cài `yt-dlp` bằng `uv tool install yt-dlp`. Font tải từ Google Fonts (Anton, Be Vietnam Pro) nên cần mạng.
