<div align="center">

# Project ArcoIris 🌈
**Firmware Tùy Chỉnh Cho Máy Ảnh Nikon D300s (v1.02)**

[![Language: English](https://img.shields.io/badge/Language-English%20🇬🇧-ffe042?style=for-the-badge&labelColor=121622)](README.md)
[![Ngôn ngữ: Tiếng Việt](https://img.shields.io/badge/Ng%C3%B4n%20ng%E1%BB%AF-Ti%E1%BA%BFng%20Vi%E1%BB%87t%20🇻🇳-da251d?style=for-the-badge&labelColor=121622)](README.vi.md)

[![Release](https://img.shields.io/badge/B%E1%BA%A3n%20Build-B5%3A%20Native%20Manual-2ee59d?style=flat-square)](https://github.com/FreexFox/project-arcoiris/releases/tag/v1.02-b5)
[![Target](https://img.shields.io/badge/M%C3%A1y%20%E1%BA%A3nh-Nikon%20D300s%20(v1.02)-f5b700?style=flat-square&logo=nikon&logoColor=white)](#)
[![Block 0](https://img.shields.io/badge/Block%200%20CRC-0xB506%20(100%25%20Zin)-success?style=flat-square)](#)
[![Hardware Status](https://img.shields.io/badge/Ph%E1%BA%A7n%20c%E1%BB%A9ng-%C4%90%C3%A3%20Test%20Th%E1%BB%B1c%20T%E1%BA%BF%20Tr%C3%AAn%20D300s-ff3366?style=flat-square)](#)

*Giả lập Phơi sáng Thủ công (`M`) Thời gian thực • Giả lập Bù trừ EV • Biểu đồ Histogram 64-Bin Trực tiếp*

[📥 **Tải Ngay Build B5 (`D300S102.bin`)**](https://github.com/FreexFox/project-arcoiris/releases/latest) · [🇬🇧 **Read in English**](README.md) · [🔬 **Phân tích Kỹ thuật Chi tiết**](docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md)

</div>

---

## ✨ Project ArcoIris Mang Lại Gì Cho Chiếc D300s Của Bạn?

Trên firmware gốc của **Nikon D300s (v1.02)**, màn hình Live View bị khóa cứng vào chế độ tự động cân bằng sáng khiến việc canh phơi sáng trên màn hình gần như bất khả thi:
- **Không phản hồi Bù trừ sáng (`+/- EV`)** — bấm giữ nút EV và xoay bánh xe nhưng màn hình Live View không hề sáng lên hay tối đi.
- **Không phản hồi Tốc độ màn trập và ISO ở chế độ `M`** — khi chụp Manual (`M`), dù bạn xoay tốc độ lên `1/8000s` hay tăng ISO lên `Hi 1`, màn hình LCD vẫn giữ nguyên một mức sáng tự động.
- **Không có biểu đồ Histogram khi Live View** — bạn buộc phải chụp thử một tấm rồi bấm xem lại ảnh mới biết ảnh bị cháy sáng hay tối đen.

**Project ArcoIris (Build B5: Native Manual)** giải quyết trọn vẹn cả 3 điểm yếu này trực tiếp trên phần cứng Nikon D300s:
1. **Giả lập Phơi sáng Thời gian thực ở Chế độ `M` (`Build B5`)**: Đánh thức tính năng điều khiển phơi sáng Live View nguyên bản bị Nikon khóa ẩn trong firmware, giúp **Tốc độ màn trập** (`1/25s` đến `1/8000s`) và **ISO** (`200` đến `Hi 1`) làm thay đổi độ sáng màn hình ngay tức thì khi bạn xoay bánh xe.
2. **Giả lập Bù trừ sáng EV (`+/- EV`) Trực tiếp (`Build B1`)**: Hiển thị ngay độ sáng thay đổi khi chỉnh `+/- 5 EV` ở các chế độ `P`, `S`, `A`.
3. **Biểu đồ Luminance Histogram 64-Bin Thời gian thực (`Build B4`)**: Hiển thị biểu đồ Histogram độ chói dạng kính mờ ở góc dưới bên trái màn hình Live View, nhảy mượt mà theo từng nấc Tốc độ màn trập, ISO và EV.

| Tính năng | Firmware Nikon D300s Gốc (v1.02) | Project ArcoIris (Build B5: Native Manual) |
| :--- | :--- | :--- |
| **Live View ở chế độ Manual (`M`)** | ❌ Tự động bù sáng (xoay Tốc & ISO màn hình không đổi) | ✅ **Giả lập Phơi sáng Thời gian thực theo Tốc (`1/25s..1/8000s`) & ISO (`200..Hi1`) (`B5`)** |
| **Bù trừ sáng EV (`+/- EV`) khi Live View** | ❌ Không phản hồi trên màn hình Live View | ✅ **Giả lập Bù trừ sáng (`+/- 5 EV`) trực tiếp ở chế độ `P` / `S` / `A` (`B1`)** |
| **Biểu đồ Histogram khi Live View** | ❌ Không có | ✅ **Biểu đồ Luminance Histogram 64-Bin Thời gian thực (`B4`)** |
| **Cá nhân hóa Menu & EXIF** | Mặc định | ✅ **`PROJECT ARCOIRIS` / `MY MODS` / EXIF `D300S ArcoIris` (`B2`)** |
| **Bootloader / Chip Nguồn (`Block 0`)** | `0xB506` | ✅ **Giữ nguyên Zin 100% (`0xB506`) — Không bao giờ lo Brick** |

---

## 📥 Tải Về & Hướng Dẫn Cài Đặt (Chỉ Mất 2 Phút)

### 1. Tải File Firmware Đã Đóng Gói Sẵn
Tải trực tiếp file **`D300S102.bin`** tại trang **[Releases (`v1.02-b5` — Build B5: Native Manual)](https://github.com/FreexFox/project-arcoiris/releases/tag/v1.02-b5)**:
- **Tên file**: `D300S102.bin` (`7,864,450` bytes)
- **Mã kiểm tra MD5**: `6549191abe995c2f2b9253b3fd55ab2a`
- **CRC Block 0**: `0xB506` (Zin 100%) · **CRC Block 1**: `0x46D8` (Hợp lệ)

### 2. Các Bước Nạp Lên Máy Ảnh Nikon D300s
1. Format thẻ nhớ CF hoặc SD ngay trong máy ảnh.
2. Chép file **`D300S102.bin`** vào **thư mục gốc (ngoài cùng)** của thẻ nhớ (không để bên trong thư mục `DCIM`).
3. Lắp thẻ nhớ vào máy D300s (đảm bảo pin còn trên **80%**).
4. Bấm nút `MENU` → chọn **Setup Menu (biểu tượng cờ-lê)** → **Firmware version** → **Update** → **Yes**.
5. Đợi khoảng 2 phút cho tới khi máy báo cập nhật hoàn tất, tắt máy bật lại là xong!

---

## 📸 Lưu Ý Quan Trọng Khi Sử Dụng Trên Máy

1. **Nhớ TẮT `Auto ISO` khi chụp chế độ `M` trong Live View**:
   - Vào **Shooting Menu (biểu tượng máy ảnh)** → **ISO sensitivity settings** → **Auto ISO sensitivity control** → chọn **OFF**.
   - *Lý do*: Khi bật Auto ISO, chip phụ (Sub-CPU) tự động tính ISO dựa trên cảm biến đo sáng quang học nằm trên gù ngắm (vốn bị gương lật che tối đen khi bật Live View) và ghi đè lên nút ISO chỉnh tay. Khi **TẮT Auto ISO**, bạn giữ nút **ISO + xoay bánh xe lệnh** là độ sáng màn hình và biểu đồ Histogram sẽ thay đổi tức thì.
2. **Tại sao tốc độ màn trập chậm hơn `1/25s` không làm màn hình Live View sáng thêm?**:
   - Khi chạy Live View, cảm biến CMOS phải xuất hình ảnh liên tục ở tốc độ **24–30 khung hình/giây** (`1/30s` đến `1/25s` mỗi khung hình). Về mặt vật lý, một khung hình video trực tiếp không thể phơi sáng lâu hơn chính chu kỳ quét của nó (`~1/25s`).
   - Do đó, trong dải từ **`1/25s` lên tới `1/8000s`**, mỗi nấc xoay bánh xe (`1/3 EV`) sẽ làm màn hình sáng/tối chính xác tuyệt đối. Các tốc độ chậm hơn `1/25s` (`1/20s` xuống tới `30"` và `Bulb`) sẽ giữ ở mức sáng tối đa của một khung hình (`1/25s`) trên màn hình xem trước (khi bấm chụp thật, máy vẫn phơi sáng đúng số giây bạn đã chọn).
3. **Biểu Đồ Histogram Luôn Hiển Thị (Trong Bản B4/B5)**:
   - Ở bản Build B4 và B5 hiện tại, biểu đồ Luminance Histogram 64-bin ở góc dưới bên trái **luôn hiển thị cố định** khi bật Live View (tính năng bấm nút bật/tắt ẩn/hiện biểu đồ sẽ được bổ sung ở bản **Build B6**).

---

## 🛡️ Cam Kết An Toàn Tuyệt Đối (Zero-Brick)

> [!CAUTION]
> **Giữ Nguyên Zin 100% Block 0 (`a810_010200.bin`)**  
> Nikon D300s sử dụng kiến trúc 2 vi xử lý độc lập: **Block 0** (chip phụ H8S quản lý nguồn điện, nút bấm và nạp lại firmware từ thẻ nhớ) và **Block 1** (chip chính Fujitsu FR80 xử lý giao diện và Live View). Mọi bản build của Project ArcoIris **không bao giờ chạm vào Block 0 (`CRC 0xB506` nguyên bản 100% từng bit)** và luôn kiểm tra mã vòng CRC-16/XMODEM của Block 1 trước khi xuất file. Bạn luôn có thể nạp về lại firmware gốc v1.02 của Nikon bất cứ lúc nào qua thẻ nhớ.

---

## 📜 Lịch Sử Phát Triển Các Bản Build (`B1` → `B5: Native Manual`)

| Bản Build | Tóm tắt tính năng | CRC Block 1 | Mã MD5 (`D300S102.bin`) |
| :--- | :--- | :--- | :--- |
| **Stock v1.02** | Firmware gốc chính hãng của Nikon D300s | `0xB00C` | `7f5503b795fc41c83a26e98d834d48ff` |
| **Build B1** | Mở khóa giả lập **Bù trừ sáng EV (`+/- EV`)** khi Live View (`0x00222E5A`: `F3 0E -> 9F A0`) | `0x3F88` | `6f94e2c52950e6cf77879cb9e32c7554` |
| **Build B2** | Cá nhân hóa chuỗi ký tự Menu (`PROJECT ARCOIRIS` / `MY MODS`) & thẻ EXIF Software (`D300S ArcoIris`) | `0x886B` | `15cb90f5623d95f861d8f4fc9a89660e` |
| **Build B3** | Thử nghiệm liên kết nút bật/tắt trong Custom Settings Menu | `0xD034` | `dc73eb1180823df108b55d9bc6b7c547` |
| **Build B4** | Bổ sung **Biểu đồ Luminance Histogram 64-Bin Thời gian thực** (`0x002D2C00`, luôn hiển thị khi Live View) | `0x0AA9` | `b4b09e180a29e37cb36f3069eb4159c8` |
| **Build B5: Native Manual** | **Mở khóa hàm điều khiển phơi sáng Live View chế độ `M` nguyên bản bị ẩn của Nikon (`0x0012C22A`)** trên nền B4 | `0x46D8` | `6549191abe995c2f2b9253b3fd55ab2a` |

---

## 🔬 Phân Tích Kỹ Thuật Chuyên Sâu (Dành Cho Dịch Ngược & Lập Trình Viên)

### Cơ Chế Mở Khóa Build B5: Native Manual (`0x0012C22A`)

Khi đối chiếu chéo trình quản lý trạng thái Live View của **Nikon D800 (v1.11)** (`0x0024B898`) với ROM Main-CPU của **Nikon D300s (v1.02)** (`b810_102_.bin`), chúng tôi phát hiện ra rằng **các kỹ sư của Nikon thực chất đã viết sẵn, biên dịch và nhúng nguyên một hàm nạp thông số phơi sáng Live View chế độ `M` hoàn chỉnh vào trong firmware của D300s tại địa chỉ `0x0012C22A`** — nhưng trước khi xuất xưởng, họ đã vô hiệu hóa nó đằng sau một bit cờ RAM (`0x9F87210F` bit `0x04`).

Trong toàn bộ 7.34 MB firmware của Main-CPU (`b810_102_.bin`), địa chỉ `0x9F87210F` chỉ được ghi tại đúng 2 nơi (`0x00126B96` và `0x001283B0`), và cả hai nơi đều chạy lệnh `BANDL #0xB, @R0` (`*0x9F87210F &= ~0x04`) — tức là **luôn luôn xóa bit `0x04` về `0`**. Vì vậy, cả 4 cổng kiểm tra phơi sáng Live View đều luôn nhảy (`BEQ`) bỏ qua đoạn kiểm tra chế độ `M`:

```text
Firmware gốc:   BTSTL #0x4, @0x9F87210F  ──►  BEQ skip_manual  ──►  (Code bị bỏ quên: Kiểm tra Mode M & Gọi 0x0012C22A)
Build B5:       BTSTL #0x4, @0x9F87210F  ──►  NOP (9F A0)      ──►  Nếu Mode == M: Gọi 0x0012C22A! Nếu P/S/A: Auto-AGC + B1 EV Comp
```

| Cổng (Gate) | Vai trò hàm | Địa chỉ ảo (VA) | Offset trong Block 1 | Byte Gốc (`BEQ`) | Build B5 (`NOP`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | `0x0012C27E` (Khởi tạo LV / Chênh sáng lớn Mode A) | `0x0012C290` | `0x0EC290` | `E2 09` (`BEQ 0x0012C2A4`) | `9F A0` (`NOP`) |
| **Gate 2** | `0x0012C34A` (Cập nhật từng khung hình Mode A) | `0x0012C35C` | `0x0EC35C` | `E2 09` (`BEQ 0x0012C370`) | `9F A0` (`NOP`) |
| **Gate 3** | `0x0012C402` (Khởi tạo LV / Chênh sáng lớn Mode B) | `0x0012C41A` | `0x0EC41A` | `E2 0C` (`BEQ 0x0012C434`) | `9F A0` (`NOP`) |
| **Gate 4** | `0x0012C56A` (Cập nhật từng khung hình Mode B) | `0x0012C582` | `0x0EC582` | `E2 0C` (`BEQ 0x0012C59C`) | `9F A0` (`NOP`) |

Khi ở chế độ **Manual (`M`)** (`(*(uint8_t*)0x9F872034 >> 6) == 3`), hàm `0x0012C22A` đọc trực tiếp gói tin IPC từ Sub-CPU (`0x9F872034`: ISO tại `+0x02`, Khẩu độ tại `+0x05`, Tốc độ màn trập tại `+0x09`) và nạp thẳng vào cấu trúc điều khiển cảm biến Live View (`0x9F8711FC`), đánh thức tiến trình `task_0x03` (`0x0012FC16`) mỗi khi bạn xoay bánh xe để nạp lại thanh ghi màn trập điện tử (`0x0012F27A`) và độ lợi ISO (`0x0012E4E4`) của cảm biến CMOS theo thời gian thực.

👉 **Đọc toàn bộ mã hợp ngữ (Disassembly) & tài liệu phân tích chi tiết**:
- 🇻🇳 [**Phân Tích Kỹ Thuật Giả Lập Phơi Sáng Live View Chế Độ `M` (`0x0012C22A`) — Tiếng Việt**](docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md)
- 🇬🇧 [**Native Manual Live View Exposure Simulation (`0x0012C22A`) — English**](docs/LIVE_VIEW_MANUAL_EXPOSURE.md)

---

### Tự Build Từ Mã Nguồn & Kiểm Tra Checksum

```bash
# 1. Đóng gói tự động bản Build B5: Native Manual từ nền Build B4
python3 scripts/build_b5_native_manual.py

# 2. Kiểm tra cấu trúc container và mã vòng CRC-16/XMODEM của Block 0 / Block 1
python3 d300s_tool.py info "FLASH/REFLASH B5/D300S102.bin"
```

---

### Sơ Đồ Thư Mục & Tài Liệu Kỹ Thuật

| Đường dẫn | Mô tả |
| :--- | :--- |
| [`d300s_tool.py`](d300s_tool.py) | Công cụ giải mã/mã hóa XOR firmware Nikon, vá byte an toàn & kiểm tra CRC-16/XMODEM |
| [`scripts/build_b5_native_manual.py`](scripts/build_b5_native_manual.py) | Script đóng gói tự động bản **Build B5: Native Manual** (mở khóa `0x0012C22A`) |
| [`scripts/build_b4_histogram.py`](scripts/build_b4_histogram.py) | Script đóng gói bản **Build B4** (Biểu đồ Luminance Histogram 64-bin + Bù trừ sáng EV B1) |
| [`patches/manifests/`](patches/manifests/) | Các file JSON manifest cho Build `B1`, `B2`, `B3`, `B4` và `B5: Native Manual` |
| [`docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md`](docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md) | Tài liệu phân tích kỹ thuật chi tiết mã hợp ngữ & cơ chế mở khóa `0x0012C22A` (VI / [EN](docs/LIVE_VIEW_MANUAL_EXPOSURE.md)) |
| [`docs/LIVE_HISTOGRAM_ENGINE.md`](docs/LIVE_HISTOGRAM_ENGINE.md) | Phân tích kỹ thuật bộ dựng biểu đồ Luminance Histogram 64-bin bằng hợp ngữ FR80 (314 bytes) |
| [`docs/LIVE_VIEW_PIPELINE.md`](docs/LIVE_VIEW_PIPELINE.md) | Hệ thống hiển thị Live View D300s, bộ đệm YCbCr 4:2:0 & DMA màn hình LCD |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Định dạng đóng gói mã hóa XOR, giao tiếp liên nhân (IPC) và bản đồ bộ nhớ/thanh ghi |
| [`docs/OFF_CAMERA_VERIFICATION_REPORT.md`](docs/OFF_CAMERA_VERIFICATION_REPORT.md) | Báo cáo kiểm chứng mã vòng CRC container & ma trận kiểm thử thực tế từ Build `B1`–`B5` |
| [`docs/SAFETY_AND_VERIFICATION.md`](docs/SAFETY_AND_VERIFICATION.md) | Quy tắc bảo vệ an toàn tuyệt đối cho Block 0 và quy trình kiểm chứng trước khi nạp |
| [`tools/nikon_emulator/`](tools/nikon_emulator/) | Bộ công cụ dịch ngược NikonHacker DFR (FR80) & DTX (H8S) |

---

## 🙏 Lời Cảm Ơn (Thank You)

Dự án này được xây dựng dựa trên nền tảng tri thức và công cụ của những người tiên phong trong lĩnh vực dịch ngược firmware máy ảnh:

- **Simeon Pilgrim** ([`simeonpilgrim/nikon-firmware-tools`](https://github.com/simeonpilgrim/nikon-firmware-tools)) — Người đầu tiên giải mã cấu trúc đóng gói firmware Nikon, bảng mã hóa XOR và công cụ giải nén.
- **Coderat & Vicne** (NikonHacker) — Tác giả bộ công cụ dịch ngược Fujitsu FR80 (`DFR`), Hitachi H8S (`DTX`), `NikonEmulator` và các tài liệu nền tảng về kiến trúc chip kép của Nikon.
- **a1ex** (Magic Lantern) — Người đặt nền móng cho phương pháp luận dịch ngược firmware DSLR và truyền cảm hứng cho cộng đồng mod firmware máy ảnh toàn cầu.
- **Kevin (`fdkevin0`)** ([`fdkevin0/nikon-firmware-tools`](https://github.com/fdkevin0/nikon-firmware-tools)) & **WonderLantern** ([`WonderLantern/nikon-fw-key-tool`](https://github.com/WonderLantern/nikon-fw-key-tool)) — Đóng góp mã nguồn mở về trình dịch ngược, kiểm tra mã vòng CRC và cấu trúc container firmware Nikon.
