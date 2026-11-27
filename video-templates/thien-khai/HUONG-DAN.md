# Phong cách C – "Thiên khải"

Dùng cho bài giảng tâm linh, ý nghĩa ngày lễ, giải thích nhiều ý. Người dùng chọn kiểu này khi muốn **không ghi số clip hay ngày**, chỉ tập trung vào tựa đề và các ý chính.

## Bố cục (1080×1440, vùng an toàn "cân bằng")
- Nền vũ trụ xanh đêm, có sao và hào quang vàng.
- Dòng nhỏ "SƯ PHỤ GIẢNG" + tựa đề 2 dòng chữ Playfair Display vàng ánh kim. Dòng 2 to và tự co cho vừa ≤780px.
- Nhãn phụ viền vàng giải thích ngắn (ví dụ "18 tháng 10 âm lịch • Ngày của Mẹ").
- Cảnh quay trong khung viền vàng phát sáng: khung ngoài x130 y392 820×470, lòng khung x135 y397 810×460.
- Thẻ ý chính: nhãn "Ý k / N", biểu tượng tròn, tiêu đề in hoa (chữ khóa trong `<b>` tô vàng), một dòng giải thích. Sửa mảng `P` trong `styleC.html`.
- Hàng chấm tiến độ, phụ đề, rồi khoảng trống dưới cùng.

## Dựng video
1. Sửa tựa đề, nhãn phụ, mảng `P` trong `styleC.html`. Viết `segments.json`: `[bắt_đầu, kết_thúc, số_ý, "phụ đề"]`.
2. Gửi khung hình duyệt trước (dùng `?k=<ý>&bg=<ảnh>&sub=...` để xem có ảnh trong khung).
3. Lớp chữ (lòng khung trong suốt nhờ mask SVG): `WORK=<thư mục> NODE_PATH=$(npm root -g) node render-overlays.js`
4. Ghép. Nếu video gốc đã có chữ in sẵn, chỉ crop phần cảnh quay; kiểm tra bằng ảnh có lưới trước:
```
ffmpeg -i src.mov -f concat -safe 0 -i ov/list.txt -filter_complex "color=c=black:s=1080x1440:r=30:d=<giây>[cv];[0:v]crop=<w>:<h>:<x>:<y>,scale=810:-2,crop=810:460,setsar=1,fps=30[v0];[cv][v0]overlay=135:397:shortest=1[b];[1:v]fps=30,format=rgba[o];[b][o]overlay=0:0:eof_action=repeat,format=yuv420p[v]" -map "[v]" -map 0:a -c:v libx264 -crf 20 -c:a aac -movflags +faststart out.mp4
```
