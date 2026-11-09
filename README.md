<div align="center">

# Project ArcoIris 🌈
**Nikon D300s Firmware Reverse Engineering & Live View Modification**

[![Language: English](https://img.shields.io/badge/Language-English%20🇬🇧-ffe042?style=for-the-badge&labelColor=121622)](README.md)
[![Ngôn ngữ: Tiếng Việt](https://img.shields.io/badge/Ng%C3%B4n%20ng%E1%BB%AF-Ti%E1%BA%BFng%20Vi%E1%BB%87t%20🇻🇳-da251d?style=for-the-badge&labelColor=121622)](README.vi.md)

[![Target](https://img.shields.io/badge/Camera-Nikon%20D300s%20(v1.02)-f5b700?style=flat-square&logo=nikon&logoColor=white)](#)
[![Architecture](https://img.shields.io/badge/CPU-Fujitsu%20FR80%20%2B%20H8S-3399ff?style=flat-square)](#)
[![Build](https://img.shields.io/badge/Release-Build%20B5%3A%20Native%20Manual-2ee59d?style=flat-square)](#)
[![Block 0](https://img.shields.io/badge/Block%200%20CRC-0xB506%20(100%25%20Stock)-success?style=flat-square)](#)
[![Hardware Status](https://img.shields.io/badge/Hardware-Verified%20on%20Real%20D300s-ff3366?style=flat-square)](#)

*Native Manual (`M`) Live View Exposure Simulation • EV Compensation Preview • Real-Time 64-Bin Luminance Histogram • Custom EXIF & UI*

[🇬🇧 **Read in English**](README.md) · [🇻🇳 **Đọc bản Tiếng Việt**](README.vi.md) · [🔬 **Technical Deep-Dive (`0x0012C22A`)**](docs/LIVE_VIEW_MANUAL_EXPOSURE.md) · [🇻🇳 **Tài liệu Kỹ thuật (VI)**](docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md)

</div>

---

## 🔥 Overview

On stock **Nikon D300s (v1.02)** firmware, Live View is completely locked to an internal Automatic Gain Control (AGC) loop:
- It **does not even react to Exposure Compensation (`+/- EV`)**—we first unlocked real-time EV Compensation preview in **Build B1** via a 2-byte `NOP` patch at `0x00222E5A` (`1:0x1E2E5A:F30E:9FA0`).
- Even with EV Compensation unlocked (and our real-time 64-bin luminance histogram added in **Build B4**), switching to **Manual (`M`)** mode still left the LCD ignoring both the **Shutter Speed** dial and **ISO** settings.

By cross-referencing the **Nikon D800 (v1.11)** Live View state machine (`0x0024B898`) against the **Nikon D300s (v1.02)** Main-CPU ROM (`b810_102_.bin`), we discovered that **Nikon's engineers already wrote, compiled, and shipped a complete Manual (`M`) mode Live View exposure routine inside the D300s firmware at `0x0012C22A`**—and then disabled it behind a single permanently-zeroed RAM flag bit (`0x9F87210F` bit `0x04`) before release.

**Build B5: Native Manual** replaces **four 2-byte `BEQ` instructions with `NOP` (`9F A0`)** to activate `0x0012C22A` in Manual (`M`) mode, combining Nikon's dormant factory Manual Live View exposure engine with our **Build B1** EV Compensation unlock (`P`/`S`/`A` modes) and **Build B4** Real-Time 64-Bin Luminance Histogram.

---

## ⚡ Stock v1.02 vs. Project ArcoIris (Build B1 → B5)

| Capability | Stock Nikon D300s (v1.02) | Project ArcoIris (Build B5: Native Manual) |
| :--- | :--- | :--- |
| **Live View in Manual (`M`) Mode** | ❌ Locked to Auto-AGC (ignores Shutter & ISO dials) | ✅ **Real-Time Manual Shutter (`1/25s..1/8000s`) & ISO (`200..Hi1`) Preview (`B5`)** |
| **Live View EV Compensation (`+/- EV`)** | ❌ Ignored in Live View | ✅ **Real-Time EV Compensation (`+/- 5 EV`) Preview at `0x00222E5A` (`B1`)** |
| **Live View Luminance Histogram** | ❌ None during Live View | ✅ **Real-Time 64-Bin YCbCr Luminance Histogram Overlay (`< 0.85 ms/frame`, `B4`)** |
| **Custom Menu & EXIF Branding** | Stock strings | ✅ **`PROJECT ARCOIRIS` / `MY MODS` / EXIF `D300S ArcoIris` (`B2`)** |
| **Sub-CPU Bootloader (`Block 0`)** | `0xB506` | ✅ **`0xB506` (100% Bit-for-Bit Untouched — Zero Brick Risk)** |

---

## 🔬 How Build B5: Native Manual Works (`0x0012C22A`)

Across the entire 7.34 MB Main-CPU firmware (`b810_102_.bin`), RAM flag `0x9F87210F` is only ever written by `0x00126B96` and `0x001283B0`, both of which execute `BANDL #0xB, @R0` (`*0x9F87210F &= ~0x04`). Because bit `0x04` is never set anywhere in the ROM, the four Live View AE/AGC entry gates always branch (`BEQ`) around the Manual (`M`) mode check:

```
Stock Gate:     BTSTL #0x4, @0x9F87210F  ──►  BEQ skip_manual  ──►  (Dead Code: Check M Mode & CALL 0x0012C22A)
Build B5:       BTSTL #0x4, @0x9F87210F  ──►  NOP (9F A0)      ──►  If Mode == M: CALL 0x0012C22A! Else: Auto-AGC + B1 EV Comp
```

### Exact Binary Patch Table (Block 1 — `b810_102_.bin`)

| Gate | Function Role | Virtual Address | Block 1 Offset | Stock Bytes (`BEQ`) | Build B5 (`NOP`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | `0x0012C27E` (LV Entry / Large-Delta Mode A) | `0x0012C290` | `0x0EC290` | `E2 09` (`BEQ 0x0012C2A4`) | `9F A0` (`NOP`) |
| **Gate 2** | `0x0012C34A` (Per-Frame Tracking Mode A) | `0x0012C35C` | `0x0EC35C` | `E2 09` (`BEQ 0x0012C370`) | `9F A0` (`NOP`) |
| **Gate 3** | `0x0012C402` (LV Entry / Large-Delta Mode B) | `0x0012C41A` | `0x0EC41A` | `E2 0C` (`BEQ 0x0012C434`) | `9F A0` (`NOP`) |
| **Gate 4** | `0x0012C56A` (Per-Frame Tracking Mode B) | `0x0012C582` | `0x0EC582` | `E2 0C` (`BEQ 0x0012C59C`) | `9F A0` (`NOP`) |

When in **Manual (`M`)** mode (`(*(uint8_t*)0x9F872034 >> 6) == 3`), `0x0012C22A` copies your live Sub-CPU IPC Exposure struct (`0x9F872034`) straight into the Live View AGC target registers (`0x9F8711FC`), waking `task_0x03` (`0x0012FC16`) on every dial tick to program the CMOS sensor's electronic shutter (`0x0012F27A`) and analog/digital gain (`0x0012E4E4`) in real time.

---

## 📌 Important Hardware Operational Notes

1. **Turn `Auto ISO Sensitivity Control` OFF when shooting Manual (`M`) in Live View**:
   - `0x0012C22A` reads the active ISO from `*(int8_t*)(0x9F872034 + 0x02)` (`0x9F872036`), sent by the Sub-CPU.
   - When Auto ISO is **ON**, the Sub-CPU calculates Auto ISO from the optical viewfinder's 1,005-pixel RGB meter (which is blacked out while the mirror is flipped up in Live View) and overrides manual ISO button changes.
   - With **Auto ISO OFF**, holding the **ISO button + rotating the command dial** adjusts Live View sensor gain and histogram brightness immediately in real time.
2. **`1/25s` Physical CMOS Frame-Time Floor**:
   - Because the CMOS sensor refreshes Live View continuously at **24–30 fps** (`33.3 ms` to `40 ms` per frame), a single video frame **physically cannot integrate light for longer than one frame period (`~1/25s`)** without dropping the Live View frame rate.
   - Accordingly, Nikon's 256-byte ROM shutter lookup table (`0x001EEB6B`) clamps shutter speeds slower than or equal to **`1/25s`** (`indices 0..61`, down to `30"` and `Bulb`) at maximum full-frame integration (`0x00`), while **`1/30s` up to `1/8000s`** (`indices 62..132`) step electronic shutter speed cleanly in `1/3 EV` increments.

---

## 🚀 Quickstart: Building & Flashing Build B5: Native Manual

### 1. Build the Firmware Bundle
```bash
python3 scripts/build_b5_native_manual.py
```
Or patch directly on top of Build B4 using [`d300s_tool.py`](d300s_tool.py):
```bash
python3 d300s_tool.py patch "FLASH/REFLASH B4/D300S102.bin" "FLASH/REFLASH B5/D300S102.bin" \
  --allow-unknown-stock \
  --edit 1:0x0EC290:E209:9FA0 \
  --edit 1:0x0EC35C:E209:9FA0 \
  --edit 1:0x0EC41A:E20C:9FA0 \
  --edit 1:0x0EC582:E20C:9FA0
```

### 2. Verify Checksums Before Flashing
```bash
python3 d300s_tool.py info "FLASH/REFLASH B5/D300S102.bin"
```
Expected output:
```text
file   : FLASH/REFLASH B5/D300S102.bin  (7864450 bytes)
md5    : 6549191abe995c2f2b9253b3fd55ab2a
block 0: a810_010200.bin  off=0x0000070 len=  524290 crc stored=0xB506 computed=0xB506 OK
block 1: b810_102_.bin    off=0x0080072 len= 7340032 crc stored=0x46D8 computed=0x46D8 OK
```

### 3. Flash to Camera
1. Copy `FLASH/REFLASH B5/D300S102.bin` to the root of a formatted CF/SD card as **`D300S102.bin`**.
2. Insert the card into your D300s with a charged battery ($\ge 80\%$).
3. Open **Setup Menu (Wrench)** → **Firmware version** → **Update** → **Yes**.
4. Wait ~2 minutes for completion, restart the camera, switch to **`M` mode** (with **Auto ISO OFF**), press **Lv**, and enjoy real-time exposure simulation!

---

## 🗂️ Repository Map

| Path | Description |
| :--- | :--- |
| [`README.md`](README.md) / [`README.vi.md`](README.vi.md) | Bilingual project overview & flashing guide (English & Tiếng Việt) |
| [`d300s_tool.py`](d300s_tool.py) | Off-camera Nikon firmware XOR decrypter/encrypter, guarded byte patcher & CRC-16/XMODEM verifier |
| [`scripts/build_b5_native_manual.py`](scripts/build_b5_native_manual.py) | Single-command builder for **Build B5: Native Manual** |
| [`scripts/build_b4_histogram.py`](scripts/build_b4_histogram.py) | Builder for **Build B4** (64-bin YCbCr Live View Luminance Histogram + B1 EV Comp Preview) |
| [`patches/manifests/`](patches/manifests/) | JSON manifests for Builds `B1` (EV Comp Sim), `B2` (EXIF/Menu), `B3`, `B4` (Histogram), and `B5` (Native Manual) |
| [`docs/LIVE_VIEW_MANUAL_EXPOSURE.md`](docs/LIVE_VIEW_MANUAL_EXPOSURE.md) | Complete disassembly & state-machine documentation of `0x0012C22A` (EN) |
| [`docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md`](docs/LIVE_VIEW_MANUAL_EXPOSURE.vi.md) | Tài liệu phân tích kỹ thuật chi tiết cơ chế mở khóa `0x0012C22A` (VI) |
| [`docs/LIVE_HISTOGRAM_ENGINE.md`](docs/LIVE_HISTOGRAM_ENGINE.md) | Technical breakdown of the 64-bin FR80 assembly luminance histogram engine |
| [`docs/LIVE_VIEW_PIPELINE.md`](docs/LIVE_VIEW_PIPELINE.md) | D300s Live View display subsystem, YCbCr buffers & LCD DMA |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Firmware container encryption, dual-CPU IPC, and memory map |
| [`docs/SAFETY_AND_VERIFICATION.md`](docs/SAFETY_AND_VERIFICATION.md) | Block 0 zero-brick safety rules and verification procedures |
| [`tools/nikon_emulator/`](tools/nikon_emulator/) | NikonHacker DFR (FR80) & DTX (H8S) disassembler and firmware decoder suite |

---

## 🛡️ Golden Safety Rule

> [!CAUTION]
> **NEVER MODIFY BLOCK 0 (`a810_010200.bin`)**  
> Block 0 runs on the camera's H8S Sub-CPU / power controller. Corrupting Block 0 will permanently brick the camera. Every Project ArcoIris script enforces a strict assertion that Block 0 (`CRC 0xB506`, SHA-256 `5497cc40cec05194eb55ab7805de07d4188a916120851b0b1edc65d4c995af9c`) remains 100% bit-for-bit identical to official Nikon stock firmware.

---

## 🙏 Thank You

This project stands on the shoulders of the pioneers who cracked open camera firmware reverse engineering and built the foundational tools we rely on:

- **Simeon Pilgrim** ([`simeonpilgrim/nikon-firmware-tools`](https://github.com/simeonpilgrim/nikon-firmware-tools)) — For reverse-engineering Nikon's firmware container format, XOR encryption tables, and unpacking utilities.
- **Coderat & Vicne** (NikonHacker) — For building the Fujitsu FR80 (`DFR`) and Hitachi H8S (`DTX`) disassemblers, `NikonEmulator`, and documenting Nikon's dual-CPU architecture.
- **a1ex** (Magic Lantern) — For pioneering DSLR firmware reverse-engineering methodology and inspiring custom camera firmware projects worldwide.
- **Kevin (`fdkevin0`)** ([`fdkevin0/nikon-firmware-tools`](https://github.com/fdkevin0/nikon-firmware-tools)) & **WonderLantern** ([`WonderLantern/nikon-fw-key-tool`](https://github.com/WonderLantern/nikon-fw-key-tool)) — For their open-source Nikon firmware references, disassembler resources, and CRC/container research.
