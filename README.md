<div align="center">

# Project ArcoIris 🌈
**Custom Firmware for the Nikon D300s (v1.02)**

[![Language: English](https://img.shields.io/badge/Language-English%20🇬🇧-ffe042?style=for-the-badge&labelColor=121622)](README.md)
[![Ngôn ngữ: Tiếng Việt](https://img.shields.io/badge/Ng%C3%B4n%20ng%E1%BB%AF-Ti%E1%BA%BFng%20Vi%E1%BB%87t%20🇻🇳-da251d?style=for-the-badge&labelColor=121622)](README.vi.md)

[![Release](https://img.shields.io/badge/Release-Build%20B5%3A%20Native%20Manual-2ee59d?style=flat-square)](https://github.com/FreexFox/project-arcoiris/releases/tag/v1.02-b5)
[![Target](https://img.shields.io/badge/Camera-Nikon%20D300s%20(v1.02)-f5b700?style=flat-square&logo=nikon&logoColor=white)](#)
[![Block 0](https://img.shields.io/badge/Block%200%20CRC-0xB506%20(100%25%20Stock)-success?style=flat-square)](#)
[![Hardware Status](https://img.shields.io/badge/Hardware-Verified%20on%20Real%20D300s-ff3366?style=flat-square)](#)

*Real-Time Manual (`M`) Live View Exposure Simulation • EV Compensation Preview • 64-Bin Live Luminance Histogram*

[📥 **Download Build B5 (`D300S102.bin`)**](https://github.com/FreexFox/project-arcoiris/releases/latest) · [🇻🇳 **Đọc bản Tiếng Việt**](README.vi.md) · [🔬 **Technical Deep-Dive**](docs/LIVE_VIEW_MANUAL_EXPOSURE.md)

</div>

---

## ✨ What is Project ArcoIris?

On stock **Nikon D300s (v1.02)** firmware, Live View is locked to an automatic brightness loop that makes manual exposure control blind:
- **Stock Live View ignores Exposure Compensation (`+/- EV`)** — turning the EV dial does not change screen brightness.
- **Stock Live View ignores Manual (`M`) Shutter Speed and ISO** — spinning the Shutter Speed dial or changing ISO in `M` mode has zero effect on the LCD preview.
- **Stock Live View has no Live Histogram** — you have to take a test photo first just to see your exposure histogram.

**Project ArcoIris (Build B5: Native Manual)** fixes all three on real Nikon D300s hardware:
1. **Manual (`M`) Mode Exposure Simulation (`Build B5`)**: Unlocks Nikon's own hidden factory routine inside the firmware so your **Shutter Speed** (`1/25s` to `1/8000s`) and **ISO** (`200` to `Hi 1`) control Live View brightness in real time.
2. **EV Compensation (`+/- EV`) Preview (`Build B1`)**: Unlocks real-time Exposure Compensation preview (`+/- 5 EV`) in `P`, `S`, and `A` modes.
3. **Real-Time 64-Bin Luminance Histogram (`Build B4`)**: Adds a smooth, tear-free smoked-glass histogram overlay in the bottom-left corner of Live View that reacts immediately as you turn your Shutter Speed, ISO, or EV dials.

| Feature | Stock Nikon D300s (v1.02) | Project ArcoIris (Build B5: Native Manual) |
| :--- | :--- | :--- |
| **Live View in Manual (`M`) Mode** | ❌ Auto-brightness only (ignores Shutter & ISO) | ✅ **Real-Time Shutter Speed (`1/25s..1/8000s`) & ISO (`200..Hi1`) Preview (`B5`)** |
| **Live View EV Compensation (`+/- EV`)** | ❌ Ignored in Live View | ✅ **Real-Time `+/- 5 EV` Preview in `P` / `S` / `A` Modes (`B1`)** |
| **Live View Luminance Histogram** | ❌ None during Live View | ✅ **Real-Time 64-Bin Luminance Histogram Overlay (`B4`)** |
| **Custom Menu & EXIF Branding** | Stock strings | ✅ **`PROJECT ARCOIRIS` / `MY MODS` / EXIF `D300S ArcoIris` (`B2`)** |
| **Bootloader / Power CPU (`Block 0`)** | `0xB506` | ✅ **100% Untouched Stock (`0xB506`) — Zero Brick Risk** |

---

## 📥 Download & Installation Guide (2 Minutes)

### 1. Download Prebuilt Firmware
Download **`D300S102.bin`** directly from the **[Releases Page (`v1.02-b5` — Build B5: Native Manual)](https://github.com/FreexFox/project-arcoiris/releases/tag/v1.02-b5)**:
- **File Name**: `D300S102.bin` (`7,864,450` bytes)
- **MD5 Checksum**: `6549191abe995c2f2b9253b3fd55ab2a`
- **Block 0 CRC**: `0xB506` (100% Stock) · **Block 1 CRC**: `0x46D8` (Valid)

### 2. Flash to Your Nikon D300s
1. Format a CompactFlash (CF) or SD card in your camera.
2. Copy **`D300S102.bin`** to the **root folder** of the memory card (not inside `DCIM` or any subfolder).
3. Insert the card into your D300s with a well-charged battery ($\ge 80\%$).
4. Go to **Setup Menu (Wrench Icon)** → **Firmware version** → **Update** → **Yes**.
5. Wait ~2 minutes until the update finishes, then turn the camera off and back on.

---

## 📸 How to Use on Your Camera (Important Tips)

1. **Turn `Auto ISO` OFF when shooting Manual (`M`) in Live View**:
   - Go to **Shooting Menu (Camera Icon)** → **ISO sensitivity settings** → **Auto ISO sensitivity control** → **OFF**.
   - *Why?* When Auto ISO is ON, the camera's sub-processor calculates ISO from the optical viewfinder meter (which is blocked while the mirror is flipped up for Live View) and overrides manual ISO button changes. With **Auto ISO OFF**, holding the **ISO button + rotating the command dial** changes Live View brightness and the histogram in real time.
2. **Why Shutter Speeds slower than `1/25s` do not brighten Live View further**:
   - In Live View, the CMOS sensor refreshes the screen at **24–30 fps** (each video frame lasts `1/30s` to `1/25s`). Physically, a live video frame cannot gather light for longer than a single frame period (`~1/25s`) without freezing the display refresh rate.
   - Therefore, from **`1/25s` up to `1/8000s`**, every `1/3 EV` dial click darkens/brightens Live View accurately. Shutter speeds slower than `1/25s` (`1/20s` down to `30"` and `Bulb`) stay clamped at the `1/25s` maximum single-frame brightness during preview (your actual captured photo still exposes for the full selected time).
3. **Showing / Hiding the Live Histogram**:
   - Press the **`INFO`** button on the back of the camera during Live View to cycle display overlays. Selecting the clean display / HDMI mode automatically hides the histogram.

---

## 🛡️ Safety & Zero-Brick Guarantee

> [!CAUTION]
> **Block 0 (`a810_010200.bin`) Is 100% Untouched**  
> The Nikon D300s has two processors: **Block 0** (the H8S Sub-CPU that controls battery power, buttons, and boot recovery) and **Block 1** (the Fujitsu FR80 Main-CPU that runs menus and Live View). Every Project ArcoIris build leaves **Block 0 100% bit-for-bit identical to official Nikon stock firmware (`CRC 0xB506`)** and validates all Block 1 CRC-16/XMODEM checksums before packaging. You can re-flash back to official Nikon v1.02 at any time using a memory card.

---

## 📜 Build Evolution (`B1` → `B5: Native Manual`)

| Build | Summary of Changes | Block 1 CRC | Package MD5 |
| :--- | :--- | :--- | :--- |
| **Stock v1.02** | Official Nikon D300s Factory Firmware | `0xB00C` | `7f5503b795fc41c83a26e98d834d48ff` |
| **Build B1** | Unlocked real-time **EV Compensation (`+/- EV`)** in Live View (`0x00222E5A`: `F3 0E -> 9F A0`) | `0x3F88` | `6f94e2c52950e6cf77879cb9e32c7554` |
| **Build B2** | Custom menu strings (`PROJECT ARCOIRIS` / `MY MODS`) & EXIF Software tag (`D300S ArcoIris`) | `0x886B` | `15cb90f5623d95f861d8f4fc9a89660e` |
| **Build B3** | Custom Settings menu toggle binding & state persistence tests | `0xD034` | `dc73eb1180823df108b55d9bc6b7c547` |
| **Build B4** | Added **64-Bin Real-Time YCbCr Luminance Histogram** (`0x002D2C00`) + `INFO` visibility wrapper (`0x0025DA60`) | `0x0AA9` | `b4b09e180a29e37cb36f3069eb4159c8` |
| **Build B5: Native Manual** | **Unlocked Nikon's dormant factory Manual (`M`) Live View exposure routine (`0x0012C22A`)** on top of Build B4 | `0x46D8` | `6549191abe995c2f2b9253b3fd55ab2a` |

---

## 🔬 Technical Deep-Dive (For Reverse Engineers & Developers)

### How Build B5 Works (`0x0012C22A`)

By cross-referencing the **Nikon D800 (v1.11)** Live View Exposure Preview state machine (`0x0024B898`) against the **Nikon D300s (v1.02)** Main-CPU ROM (`b810_102_.bin`), we found that **Nikon's engineers already wrote, compiled, and shipped a complete Manual (`M`) mode Live View exposure loader inside the D300s firmware at `0x0012C22A`**—and then disabled it behind a single RAM flag bit (`0x9F87210F` bit `0x04`).

Across the entire 7.34 MB Main-CPU ROM, `0x9F87210F` is only written at `0x00126B96` and `0x001283B0`, both of which execute `BANDL #0xB, @R0` (`*0x9F87210F &= ~0x04`). Because bit `0x04` is never set anywhere in the firmware, all four Live View AE/AGC entry gates unconditionally branch (`BEQ`) around the Manual (`M`) mode check:

```text
Stock Gate:     BTSTL #0x4, @0x9F87210F  ──►  BEQ skip_manual  ──►  (Dormant: Check M Mode & CALL 0x0012C22A)
Build B5:       BTSTL #0x4, @0x9F87210F  ──►  NOP (9F A0)      ──►  If Mode == M: CALL 0x0012C22A! Else: Auto-AGC + B1 EV Comp
```

| Gate | Function Role | Virtual Address | Block 1 Offset | Stock Bytes (`BEQ`) | Build B5 (`NOP`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | `0x0012C27E` (LV Entry / Large-Delta Mode A) | `0x0012C290` | `0x0EC290` | `E2 09` (`BEQ 0x0012C2A4`) | `9F A0` (`NOP`) |
| **Gate 2** | `0x0012C34A` (Per-Frame Tracking Mode A) | `0x0012C35C` | `0x0EC35C` | `E2 09` (`BEQ 0x0012C370`) | `9F A0` (`NOP`) |
| **Gate 3** | `0x0012C402` (LV Entry / Large-Delta Mode B) | `0x0012C41A` | `0x0EC41A` | `E2 0C` (`BEQ 0x0012C434`) | `9F A0` (`NOP`) |
| **Gate 4** | `0x0012C56A` (Per-Frame Tracking Mode B) | `0x0012C582` | `0x0EC582` | `E2 0C` (`BEQ 0x0012C59C`) | `9F A0` (`NOP`) |

When shooting in **Manual (`M`)** mode (`(*(uint8_t*)0x9F872034 >> 6) == 3`), `0x0012C22A` copies the Sub-CPU IPC Exposure struct (`0x9F872034`: ISO at `+0x02`, Aperture at `+0x05`, Shutter Speed at `+0x09`) directly into the Live View AGC state structure (`0x9F8711FC`), waking `task_0x03` (`0x0012FC16`) on every dial tick to program the CMOS sensor's electronic shutter (`0x0012F27A`) and analog/digital gain (`0x0012E4E4`).

👉 **Read the full disassembly & technical walkthrough**:
- 🇬🇧 [**Native Manual Live View Exposure Simulation (`0x0012C22A`) — English**](docs/LIVE_VIEW_MANUAL_EXPOSURE.md)
- 🇻🇳 [**Phân Tích Kỹ Thuật Giả Lập Phơi Sáng Live View Chế Độ `M` (`0x0012C22A`) — Tiếng Việt**](docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md)

---

### Building from Source & Verifying Checksums

```bash
# 1. Build B5: Native Manual from Build B4
python3 scripts/build_b5_native_manual.py

# 2. Verify container structure and Block 0 / Block 1 CRC-16/XMODEM checksums
python3 d300s_tool.py info "FLASH/REFLASH B5/D300S102.bin"
```

---

### Repository & Documentation Map

| Path | Description |
| :--- | :--- |
| [`d300s_tool.py`](d300s_tool.py) | Off-camera Nikon firmware XOR decrypter/encrypter, guarded byte patcher & CRC-16/XMODEM verifier |
| [`scripts/build_b5_native_manual.py`](scripts/build_b5_native_manual.py) | Builder for **Build B5: Native Manual** (`0x0012C22A` unlock) |
| [`scripts/build_b4_histogram.py`](scripts/build_b4_histogram.py) | Builder for **Build B4** (64-bin YCbCr Live View Luminance Histogram + B1 EV Comp Preview) |
| [`patches/manifests/`](patches/manifests/) | JSON patch manifests for Builds `B1`, `B2`, `B3`, `B4`, and `B5: Native Manual` |
| [`docs/LIVE_VIEW_MANUAL_EXPOSURE.md`](docs/LIVE_VIEW_MANUAL_EXPOSURE.md) | Complete disassembly & state-machine documentation of `0x0012C22A` (EN / [VI](docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md)) |
| [`docs/LIVE_HISTOGRAM_ENGINE.md`](docs/LIVE_HISTOGRAM_ENGINE.md) | Technical breakdown of the 314-byte FR80 assembly 64-bin luminance histogram engine |
| [`docs/LIVE_VIEW_PIPELINE.md`](docs/LIVE_VIEW_PIPELINE.md) | D300s Live View display pipeline, YCbCr 4:2:0 buffers, `INFO` gate & LCD DMA |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Firmware container XOR encryption, dual-CPU IPC, and memory/register map |
| [`docs/OFF_CAMERA_VERIFICATION_REPORT.md`](docs/OFF_CAMERA_VERIFICATION_REPORT.md) | Container CRC analysis & Build `B1`–`B5` off-camera and on-camera verification matrix |
| [`docs/SAFETY_AND_VERIFICATION.md`](docs/SAFETY_AND_VERIFICATION.md) | Block 0 zero-brick safety invariants and pre-flash verification protocol |
| [`tools/nikon_emulator/`](tools/nikon_emulator/) | NikonHacker DFR (FR80) & DTX (H8S) disassembler and firmware decoder suite |

---

## 🙏 Thank You

This project stands on the shoulders of the pioneers who cracked open camera firmware reverse engineering and built the foundational tools we rely on:

- **Simeon Pilgrim** ([`simeonpilgrim/nikon-firmware-tools`](https://github.com/simeonpilgrim/nikon-firmware-tools)) — For reverse-engineering Nikon's firmware container format, XOR encryption tables, and unpacking utilities.
- **Coderat & Vicne** (NikonHacker) — For building the Fujitsu FR80 (`DFR`) and Hitachi H8S (`DTX`) disassemblers, `NikonEmulator`, and documenting Nikon's dual-CPU architecture.
- **a1ex** (Magic Lantern) — For pioneering DSLR firmware reverse-engineering methodology and inspiring custom camera firmware projects worldwide.
- **Kevin (`fdkevin0`)** ([`fdkevin0/nikon-firmware-tools`](https://github.com/fdkevin0/nikon-firmware-tools)) & **WonderLantern** ([`WonderLantern/nikon-fw-key-tool`](https://github.com/WonderLantern/nikon-fw-key-tool)) — For their open-source Nikon firmware references, disassembler resources, and CRC/container research.
