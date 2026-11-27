# Phong cách C – "Thiên khải" (bản động)

Dùng cho bài giảng tâm linh, ý nghĩa ngày lễ, giải thích nhiều ý. Không ghi số clip hay ngày; chỉ tập trung vào tựa đề và các ý chính.

## ⭐ Hai yêu cầu người dùng đã dặn (áp dụng cho MỌI phong cách)
1. **Bố cục RỘNG:** trên bảng tin Facebook, khung video và thẻ không được nhỏ dồn vào giữa. Khung video và thẻ rộng **x 80–1000** (920px). Chữ quan trọng (tựa đề ≤830px, phụ đề) vẫn ở giữa, trong khoảng x 110–970. Chấp nhận Reels cắt nhẹ mép khung hoặc thẻ.
2. **TỰA ĐỀ PHẢI ĐỘNG**, nổi bật và hút mắt. Không để chữ đứng yên suốt video:
   - Mở đầu (0–1,2 giây): từng chữ rơi xuống, phóng to rồi về cỡ thật, lần lượt từng chữ.
   - Sau đó lặp lại liên tục (chu kỳ 2,6 giây): vệt sáng trắng quét ngang chữ vàng, chữ "thở" (phóng to và thu nhỏ khoảng 2,5%), ánh sáng mạnh lên rồi dịu xuống, 3 ngôi sao ✦ lấp lánh.
   - Khi chuyển sang ý mới, thẻ ý chính **bật lên** trong 0,4 giây (trượt lên, phóng to rồi về cỡ thật).

## Bố cục (1080×1440)
- Nền vũ trụ xanh đêm, sao, hào quang vàng.
- "SƯ PHỤ GIẢNG" + tựa đề 2 dòng (Playfair Display vàng ánh kim; dòng 2 tối đa 96px, tự co ≤830px).
- Nhãn phụ viền vàng (ví dụ "18 tháng 10 âm lịch • Ngày của Mẹ").
- Khung video viền vàng phát sáng: ngoài x80 y392 920×500, **lòng khung x85 y397 910×490**.
- Thẻ ý chính x80 y938 920×272: nhãn "Ý k / N", biểu tượng tròn, tiêu đề (chữ khóa trong `<b>` tô vàng), dòng giải thích.
- Chấm tiến độ y1232, phụ đề y1262–1362.

## Cấu hình
Sửa `window.CFG` trong `styleC.html`: `kick`, `t1`, `t2`, `chip`, `P` (mảng `[emoji, tiêu đề HTML, giải thích]`). `segments.json`: `[bắt_đầu, kết_thúc, số_ý, "phụ đề"]`.

## Dựng
1. Khung duyệt: gọi `window.render({k, sub, t:3, bg:'<ảnh 910x490>'})` rồi chụp. Gửi kèm ảnh mô phỏng bảng tin/Reels.
2. Hai lớp: `WORK=<thư mục> DUR=<giây> NODE_PATH=$(npm root -g) node render-overlays.js` tạo `ovb/list.txt` (nền, thẻ, phụ đề) và `ovt/list.txt` (tựa đề động).
3. Ghép (nếu video gốc có chữ in sẵn thì chỉ crop phần cảnh quay; kiểm tra bằng ảnh có lưới):
```
ffmpeg -i src.mov -f concat -safe 0 -i ovb/list.txt -f concat -safe 0 -i ovt/list.txt -filter_complex "color=c=black:s=1080x1440:r=30:d=<giây>[cv];[0:v]crop=<w>:<h>:<x>:<y>,scale=910:-2,crop=910:490,setsar=1,fps=30[v0];[cv][v0]overlay=85:397:shortest=1[b];[1:v]fps=30,format=rgba[o];[b][o]overlay=0:0:eof_action=repeat[b2];[2:v]fps=30,format=rgba[t];[b2][t]overlay=0:0:eof_action=repeat,format=yuv420p[v]" -map "[v]" -map 0:a -c:v libx264 -crf 20 -c:a aac -movflags +faststart out.mp4
```
