# Hai phong cách mới: A "So sánh" và B "Vì / Nên"

Học từ 2 đoạn quay màn hình người dùng gửi (Clip 439 "Sân vận động Trống Đồng – Sân bay Long Thành", và clip "Khi mang thân người – Xưa/Nay"). Cả hai dùng khung **3:4 (1080×1440)** và phải theo **vùng an toàn "cân bằng"** trong `../su-phu-6-dieu/HUONG-DAN.md`.

## Điểm chung: CHỮ NHẢY (`jitter.js`)
Mỗi chữ cái của tựa đề hoặc câu móc liên tục đổi cỡ (88–122%), nghiêng ±5°, lệch lên xuống, thỉnh thoảng đổi hoa/thường (CHẮC XONG → CHẮC XoNG). Gắn class `jit` cho phần chữ cần nhảy. Mỗi `?v=<số>` cho ra một biến thể. Khi dựng video, render khoảng 6–12 biến thể và đổi biến thể mỗi ~0,15 giây (khoảng 7 hình/giây) bằng ffmpeg concat (`duration 0.143`).

## Phong cách A – "So sánh 2 hình" (`styleA.html`)
Dùng khi nói về 2 sự việc hoặc 2 lựa chọn, kiểu dự đoán "chắc xong?".
- Tầng trên (0–560): người nói (có thể ngồi), nhãn **pill đỏ ở góc trái** (`clip`).
- **Hộp vàng** 2 dòng chữ đen in hoa, gạch chân từng dòng (`l1`, `l2`). Chữ tự co cho vừa.
- **Dải đen** có câu móc chữ Anton đỏ viền trắng, ánh vàng, kẹp giữa ⁉️ … ⁉️ (`hook`, chữ nhảy).
- **Hai ô hình cạnh nhau** ở dưới (`img1`/`img2` là ảnh thật; hoặc `art1`/`art2` là emoji), mỗi ô có **nhãn xanh dương** viền trắng (`b1`, `b2`, ví dụ "Dự kiến hoàn thành<br>8/2028").
- Ảnh thật lấy từ thư mục Drive của người dùng nếu có. Ảnh HEIC phải đổi sang JPG trước (ffmpeg hoặc `heif-convert`).

## Phong cách B – "Vì / Nên" hoặc "Xưa / Nay" (`styleB.html`)
Dùng khi giải thích nguyên nhân và hệ quả, hoặc so sánh trước và sau.
- **Người nói phủ kín cả khung** (crop dọc từ video ngang: `crop=810:1080:<x>:0,scale=1080:1440`), có lớp tối nhẹ ở dưới.
- Tựa đề trong **hộp xanh navy phát sáng xanh** (`t`, chữ nhảy).
- Nhãn **"TẠI SAO !?"** chữ trắng trên nền đỏ viền trắng, nghiêng nhẹ (`w`).
- Hai dòng: **nhãn vàng** chữ Anton viền đen, phát sáng (`k1`, `k2`: XƯA/NAY, VÌ/NÊN, TRƯỚC/SAU…) cùng **đoạn chữ trắng viền đen** (`x1`, `x2`) và nét gạch trắng kiểu bút lông.
- Đoạn chữ giữ trong x 130–840 để tránh các nút Reels. Nên viết ngắn, tối đa khoảng 3 dòng mỗi đoạn.

## Thử nhanh
`WORK=<thư mục có styleA/B.html, jitter.js, demo/a_bg.jpg, demo/b_bg.jpg> NODE_PATH=$(npm root -g) node render-demo.js` sẽ ra ảnh trong `out/`. Ảnh mẫu đúng nằm trong `examples/`.

## Nhắc lại
- Luôn gửi khung hình và ảnh mô phỏng bảng tin/Reels cho người dùng duyệt trước khi ghép.
- Nội dung lấy đúng lời Sư Phụ; không bịa số liệu, ngày tháng, tin tức. Mốc thời gian như "Dự kiến hoàn thành 8/2028" chỉ ghi khi người dùng cung cấp hoặc Sư Phụ nói.
