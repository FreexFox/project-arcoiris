<div align="center">

# Project ArcoIris 🌈
**Nghiên Cứu Dịch Ngược & Nâng Cấp Firmware Live View Cho Nikon D300s**

[![Language: English](https://img.shields.io/badge/Language-English%20🇬🇧-ffe042?style=for-the-badge&labelColor=121622)](README.md)
[![Ngôn ngữ: Tiếng Việt](https://img.shields.io/badge/Ng%C3%B4n%20ng%E1%BB%AF-Ti%E1%BA%BFng%20Vi%E1%BB%87t%20🇻🇳-da251d?style=for-the-badge&labelColor=121622)](README.vi.md)

[![Target](https://img.shields.io/badge/M%C3%A1y%20%E1%BA%A3nh-Nikon%20D300s%20(v1.02)-f5b700?style=flat-square&logo=nikon&logoColor=white)](#)
[![Architecture](https://img.shields.io/badge/Vi%20x%E1%BB%AD%20l%C3%BD-Fujitsu%20FR80%20%2B%20H8S-3399ff?style=flat-square)](#)
[![Build](https://img.shields.io/badge/B%E1%BA%A3n%20Build-B5%3A%20Native%20Manual-2ee59d?style=flat-square)](#)
[![Block 0](https://img.shields.io/badge/Block%200%20CRC-0xB506%20(100%25%20Zin)-success?style=flat-square)](#)
[![Hardware Status](https://img.shields.io/badge/Ph%E1%BA%A7n%20c%E1%BB%A9ng-%C4%90%C3%A3%20Test%20Th%E1%BB%B1c%20T%E1%BA%BF%20Tr%C3%AAn%20D300s-ff3366?style=flat-square)](#)

*Giả lập Phơi sáng Thủ công (`M`) Thời gian thực • Giả lập Bù trừ EV • Biểu đồ Histogram 64-Bin Trực tiếp • Cá nhân hóa EXIF & Giao diện*

[🇬🇧 **Read in English**](README.md) · [🇻🇳 **Đọc bản Tiếng Việt**](README.vi.md) · [🔬 **Technical Deep-Dive (EN)**](docs/LIVE_VIEW_MANUAL_EXPOSURE.md) · [🇻🇳 **Phân tích Kỹ thuật Chi tiết (`0x0012C22A`)**](docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md)

</div>

---

## 🔥 Tổng Quan Dự Án

Trên firmware gốc của **Nikon D300s (v1.02)**, màn hình Live View bị khóa cứng vào vòng lặp tự động điều chỉnh độ lợi (Auto-AGC):
- Firmware gốc **thậm chí không phản hồi với thao tác Bù trừ sáng (`+/- EV`)** trên Live View — tính năng giả lập bù trừ sáng EV thời gian thực được mở khóa lần đầu tiên ở bản **Build B1** thông qua bản vá `NOP` 2-byte tại địa chỉ `0x00222E5A` (`1:0x1E2E5A:F30E:9FA0`).
- Tuy nhiên, ngay cả khi đã có bù trừ sáng EV (ở **B1**) và biểu đồ Luminance Histogram 64-bin thời gian thực (ở **Build B4**), khi chuyển sang chế độ **Manual (`M`)**, màn hình LCD vẫn hoàn toàn phớt lờ bánh xe **Tốc độ màn trập** và nút **ISO**.

Khi đối chiếu chéo trình quản lý trạng thái Live View của **Nikon D800 (v1.11)** (`0x0024B898`) với ROM Main-CPU của **Nikon D300s (v1.02)** (`b810_102_.bin`), chúng tôi phát hiện ra rằng **các kỹ sư của Nikon thực chất đã viết sẵn, biên dịch và nhúng nguyên một hàm điều khiển phơi sáng Live View chế độ `M` hoàn chỉnh vào trong firmware của D300s tại địa chỉ `0x0012C22A`** — nhưng trước khi xuất xưởng, họ đã khóa nó lại đằng sau một bit cờ RAM luôn bằng `0` (`0x9F87210F` bit `0x04`)!

**Build B5: Native Manual** thay thế **4 lệnh nhảy `BEQ` (8 byte) thành `NOP` (`9F A0`)** để đánh thức hàm `0x0012C22A` nguyên bản của Nikon ở chế độ `M`, kết hợp cùng bản vá bù trừ sáng EV của **Build B1** (cho các chế độ `P`/`S`/`A`) và **Biểu đồ Histogram độ chói 64-bin thời gian thực** của **Build B4**.

---

## ⚡ So Sánh Firmware Gốc v1.02 vs. Project ArcoIris (Build B1 → B5)

| Tính năng | Firmware Nikon D300s Gốc (v1.02) | Project ArcoIris (Build B5: Native Manual) |
| :--- | :--- | :--- |
| **Live View ở chế độ Manual (`M`)** | ❌ Khóa cứng Auto-AGC (xoay Tốc & ISO màn hình không đổi) | ✅ **Giả lập Phơi sáng Thời gian thực theo Tốc (`1/25s..1/8000s`) & ISO (`200..Hi1`) (`B5`)** |
| **Bù trừ sáng EV (`+/- EV`) khi Live View** | ❌ Không phản hồi trên màn hình Live View | ✅ **Giả lập Bù trừ sáng (`+/- 5 EV`) trực tiếp tại `0x00222E5A` (`B1`)** |
| **Biểu đồ Histogram khi Live View** | ❌ Không có | ✅ **Biểu đồ Luminance Histogram 64-Bin Thời gian thực (`< 0.85 ms/khung hình`, `B4`)** |
| **Cá nhân hóa Menu & EXIF** | Mặc định | ✅ **`PROJECT ARCOIRIS` / `MY MODS` / EXIF `D300S ArcoIris` (`B2`)** |
| **Bootloader Sub-CPU (`Block 0`)** | `0xB506` | ✅ **`0xB506` (Giữ nguyên Zin 100% từng bit — Không bao giờ lo Brick)** |

---

## 🔬 Cơ Chế Mở Khóa Build B5: Native Manual (`0x0012C22A`)

Trong toàn bộ 7.34 MB firmware của Main-CPU (`b810_102_.bin`), địa chỉ cờ RAM `0x9F87210F` chỉ được ghi tại đúng 2 nơi (`0x00126B96` và `0x001283B0`), và cả hai nơi đều chạy lệnh `BANDL #0xB, @R0` (`*0x9F87210F &= ~0x04`) — tức là **luôn luôn xóa bit `0x04` về `0`**. Vì không có bất kỳ lệnh nào trong ROM bật bit `0x04` lên `1`, cả 4 cổng kiểm tra phơi sáng Live View đều luôn nhảy (`BEQ`) bỏ qua đoạn kiểm tra chế độ `M`:

```
Firmware gốc:   BTSTL #0x4, @0x9F87210F  ──►  BEQ skip_manual  ──►  (Code bị bỏ quên: Kiểm tra Mode M & Gọi 0x0012C22A)
Build B5:       BTSTL #0x4, @0x9F87210F  ──►  NOP (9F A0)      ──►  Nếu Mode == M: Gọi 0x0012C22A! Nếu P/S/A: Auto-AGC + B1 EV Comp
```

### Bảng Địa Chỉ Vá Binary Chính Xác (Block 1 — `b810_102_.bin`)

| Cổng (Gate) | Vai trò hàm | Địa chỉ ảo (VA) | Offset trong Block 1 | Byte Gốc (`BEQ`) | Build B5 (`NOP`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | `0x0012C27E` (Khởi tạo LV / Chênh sáng lớn Mode A) | `0x0012C290` | `0x0EC290` | `E2 09` (`BEQ 0x0012C2A4`) | `9F A0` (`NOP`) |
| **Gate 2** | `0x0012C34A` (Cập nhật từng khung hình Mode A) | `0x0012C35C` | `0x0EC35C` | `E2 09` (`BEQ 0x0012C370`) | `9F A0` (`NOP`) |
| **Gate 3** | `0x0012C402` (Khởi tạo LV / Chênh sáng lớn Mode B) | `0x0012C41A` | `0x0EC41A` | `E2 0C` (`BEQ 0x0012C434`) | `9F A0` (`NOP`) |
| **Gate 4** | `0x0012C56A` (Cập nhật từng khung hình Mode B) | `0x0012C582` | `0x0EC582` | `E2 0C` (`BEQ 0x0012C59C`) | `9F A0` (`NOP`) |

Khi bạn để chế độ **Manual (`M`)** (`(*(uint8_t*)0x9F872034 >> 6) == 3`), hàm `0x0012C22A` sẽ đọc trực tiếp gói tin IPC từ Sub-CPU (`0x9F872034`: ISO tại `+0x02`, Khẩu độ tại `+0x05`, Tốc độ màn trập tại `+0x09`) và nạp thẳng vào cấu trúc điều khiển cảm biến Live View (`0x9F8711FC`), đánh thức tiến trình `task_0x03` (`0x0012FC16`) mỗi khi bạn xoay bánh xe để nạp lại thanh ghi màn trập điện tử (`0x0012F27A`) và khuếch đại ISO (`0x0012E4E4`) của cảm biến CMOS ngay lập tức.

---

## 📌 Lưu Ý Quan Trọng Khi Sử Dụng Thực Tế

1. **Nhớ TẮT `Auto ISO Sensitivity Control` khi chụp chế độ `M` trong Live View**:
   - Hàm `0x0012C22A` đọc giá trị ISO từ địa chỉ `0x9F872036` do chip phụ (Sub-CPU) gửi sang.
   - Nếu bạn bật **Auto ISO**, Sub-CPU sẽ tính ISO tự động dựa trên cảm biến đo sáng quang học 1.005 pixel trên gù ngắm (vốn bị gương lật che kín khi bật Live View) và ghi đè lên giá trị ISO bấm tay của bạn.
   - Chỉ cần **TẮT Auto ISO**, mỗi khi bạn giữ nút **ISO + xoay bánh xe lệnh**, độ sáng màn hình Live View và biểu đồ Histogram sẽ thay đổi mượt mà theo từng nấc ISO ngay lập tức.
2. **Giới hạn vật lý tốc độ màn trập ở mức `1/25s` khi Live View**:
   - Do cảm biến CMOS khi chạy Live View phải quét hình liên tục ở tốc độ **24–30 khung hình/giây** (`33.3 ms` đến `40 ms` mỗi khung hình), một khung hình video **không thể phơi sáng lâu hơn thời gian của chính khung hình đó (`~1/25s`)** nếu không làm tụt tốc độ làm tươi màn hình.
   - Vì vậy, bảng tra cứu (LUT) 256-byte trong ROM của Nikon (`0x001EEB6B`) khóa các tốc độ chậm hơn hoặc bằng **`1/25s`** (`index 0..61`, từ `1/25s` xuống tới `30"` và `Bulb`) ở mức phơi sáng tối đa của một khung hình (`0x00`), trong khi dải tốc độ từ **`1/30s` lên tới `1/8000s`** (`index 62..132`) thay đổi thời gian tích hợp điện tử của cảm biến chính xác theo từng nấc `1/3 EV`.

---

## 🚀 Hướng Dẫn Build & Nạp Firmware (Build B5: Native Manual)

### 1. Build File Firmware Tự Động
```bash
python3 scripts/build_b5_native_manual.py
```
Hoặc chạy trực tiếp công cụ [`d300s_tool.py`](d300s_tool.py) từ nền bản Build B4:
```bash
python3 d300s_tool.py patch "FLASH/REFLASH B4/D300S102.bin" "FLASH/REFLASH B5/D300S102.bin" \
  --allow-unknown-stock \
  --edit 1:0x0EC290:E209:9FA0 \
  --edit 1:0x0EC35C:E209:9FA0 \
  --edit 1:0x0EC41A:E20C:9FA0 \
  --edit 1:0x0EC582:E20C:9FA0
```

### 2. Kiểm Tra Mã Băm & Checksum Trước Khi Nạp
```bash
python3 d300s_tool.py info "FLASH/REFLASH B5/D300S102.bin"
```
Kết quả chuẩn phải khớp hoàn toàn:
```text
file   : FLASH/REFLASH B5/D300S102.bin  (7864450 bytes)
md5    : 6549191abe995c2f2b9253b3fd55ab2a
block 0: a810_010200.bin  off=0x0000070 len=  524290 crc stored=0xB506 computed=0xB506 OK
block 1: b810_102_.bin    off=0x0080072 len= 7340032 crc stored=0x46D8 computed=0x46D8 OK
```

### 3. Nạp Lên Máy Ảnh Nikon D300s
1. Chép file `FLASH/REFLASH B5/D300S102.bin` vào thư mục gốc của thẻ nhớ CF/SD và đổi tên thành **`D300S102.bin`**.
2. Lắp thẻ vào máy với pin đã sạc đầy ($\ge 80\%$).
3. Vào **Setup Menu (Hình cờ-lê)** → **Firmware version** → **Update** → **Yes**.
4. Chờ khoảng 2 phút đến khi báo hoàn tất, tắt máy bật lại, chuyển sang chế độ **`M`** (**Tắt Auto ISO**), bấm nút **Lv** và tận hưởng!

---

## 🗂️ Cấu Trúc Thư Mục Dự Án

| Đường dẫn | Mô tả |
| :--- | :--- |
| [`README.md`](README.md) / [`README.vi.md`](README.vi.md) | Tổng quan dự án & hướng dẫn nạp firmware song ngữ (English & Tiếng Việt) |
| [`d300s_tool.py`](d300s_tool.py) | Công cụ giải mã/mã hóa XOR firmware Nikon, vá byte an toàn & kiểm tra CRC-16/XMODEM |
| [`scripts/build_b5_native_manual.py`](scripts/build_b5_native_manual.py) | Script đóng gói tự động bản **Build B5: Native Manual** |
| [`scripts/build_b4_histogram.py`](scripts/build_b4_histogram.py) | Script đóng gói bản **Build B4** (Biểu đồ Luminance Histogram 64-bin + Bù trừ sáng EV B1) |
| [`patches/manifests/`](patches/manifests/) | Các file JSON manifest cho Build `B1` (Bù trừ EV), `B2` (EXIF/Menu), `B3`, `B4` (Histogram) và `B5` (Native Manual) |
| [`docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md`](docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md) | Tài liệu phân tích kỹ thuật chi tiết mã hợp ngữ & cơ chế mở khóa `0x0012C22A` (VI) |
| [`docs/LIVE_VIEW_MANUAL_EXPOSURE.md`](docs/LIVE_VIEW_MANUAL_EXPOSURE.md) | Complete disassembly & state-machine documentation of `0x0012C22A` (EN) |
| [`docs/LIVE_HISTOGRAM_ENGINE.md`](docs/LIVE_HISTOGRAM_ENGINE.md) | Phân tích kỹ thuật bộ dựng biểu đồ Luminance Histogram 64-bin bằng hợp ngữ FR80 |
| [`docs/LIVE_VIEW_PIPELINE.md`](docs/LIVE_VIEW_PIPELINE.md) | Hệ thống hiển thị Live View D300s, bộ đệm YCbCr & DMA màn hình LCD |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Định dạng đóng gói firmware, giao tiếp liên nhân (IPC) và bản đồ bộ nhớ |
| [`docs/SAFETY_AND_VERIFICATION.md`](docs/SAFETY_AND_VERIFICATION.md) | Quy tắc bảo vệ an toàn tuyệt đối cho Block 0 và quy trình kiểm chứng trước khi nạp |
| [`tools/nikon_emulator/`](tools/nikon_emulator/) | Bộ công cụ dịch ngược NikonHacker DFR (FR80) & DTX (H8S) |

---

## 🛡️ Nguyên Tắc An Toàn Tuyệt Đối (Zero-Brick)

> [!CAUTION]
> **TUYỆT ĐỐI KHÔNG BAO GIỜ CHỈNH SỬA BLOCK 0 (`a810_010200.bin`)**  
> Block 0 là firmware điều khiển nguồn và Sub-CPU H8S. Mọi bản vá của Project ArcoIris chỉ can thiệp vào Block 1 (Main-CPU FR80) và luôn kiểm tra nghiêm ngặt để đảm bảo Block 0 (`CRC 0xB506`, SHA-256 `5497cc40cec05194eb55ab7805de07d4188a916120851b0b1edc65d4c995af9c`) nguyên bản 100% từng bit so với firmware gốc của Nikon.

---

## 🙏 Lời Cảm Ơn (Thank You)

Dự án này được xây dựng dựa trên nền tảng tri thức và công cụ của những người tiên phong trong lĩnh vực dịch ngược firmware máy ảnh:

- **Simeon Pilgrim** ([`simeonpilgrim/nikon-firmware-tools`](https://github.com/simeonpilgrim/nikon-firmware-tools)) — Người đầu tiên giải mã cấu trúc đóng gói firmware Nikon, bảng mã hóa XOR và công cụ giải nén.
- **Coderat & Vicne** (NikonHacker) — Tác giả bộ công cụ dịch ngược Fujitsu FR80 (`DFR`), Hitachi H8S (`DTX`), `NikonEmulator` và các tài liệu nền tảng về kiến trúc chip kép của Nikon.
- **a1ex** (Magic Lantern) — Người đặt nền móng cho phương pháp luận dịch ngược firmware DSLR và truyền cảm hứng cho cộng đồng mod firmware máy ảnh toàn cầu.
- **Kevin (`fdkevin0`)** ([`fdkevin0/nikon-firmware-tools`](https://github.com/fdkevin0/nikon-firmware-tools)) & **WonderLantern** ([`WonderLantern/nikon-fw-key-tool`](https://github.com/WonderLantern/nikon-fw-key-tool)) — Đóng góp mã nguồn mở về trình dịch ngược, kiểm tra mã vòng CRC và cấu trúc container firmware Nikon.
