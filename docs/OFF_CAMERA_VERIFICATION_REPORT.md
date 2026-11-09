# Project ArcoIris — Off-Camera & On-Camera Verification Report

This report documents the cryptographic, structural, static disassembly, and on-camera hardware verification of the Nikon D300s (v1.02) firmware container and **Project ArcoIris Builds B1 through B5: Native Manual**.

---

## 1. Container Format & 16-Byte Trailer Verification

The decoded Nikon D300s v1.02 firmware bundle (`D300S102.bin`) is `7,864,450` bytes (`0x780082` bytes). It consists of:
- A 32-byte package header (`0x000000..0x00001F`).
- A 2-entry module directory (`0x000020..0x00006F`).
- **Block 0 (`a810_010200.bin`)** at offset `0x000070` (`524,290` bytes, ending with 2-byte big-endian CRC-16/XMODEM `0xB506`).
- **Block 1 (`b810_102_.bin`)** at offset `0x080072` (`7,340,032` bytes, ending with 2-byte big-endian CRC-16/XMODEM).
- A 16-byte trailer at offset `0x780072` (`F7 6F` followed by 14 `0x00` bytes).

| Verification Check | Result |
| :--- | :--- |
| **Stock Block 0 (`a810_010200.bin`) CRC-16/XMODEM** | Stored `0xB506` / Computed `0xB506` (**Exact Match**) |
| **Stock Block 1 (`b810_102_.bin`) CRC-16/XMODEM** | Stored `0xB00C` / Computed `0xB00C` (**Exact Match**) |
| **CRC-16/XMODEM over full block (including stored CRC)** | `0x0000` for both blocks |
| **16-byte Package Trailer (`0x780072: F7 6F 00..00`)** | Preserved untouched; verified on real D300s hardware that the camera updater validates per-block CRC-16/XMODEM and ignores the static package trailer |

---

## 2. Build Progression & Checksum Verification Matrix (`B1` → `B5: Native Manual`)

Every Project ArcoIris firmware build is deterministically generated from the official Nikon D300s v1.02 stock image (`MD5: 7f5503b795fc41c83a26e98d834d48ff`) and verified off-camera by [`d300s_tool.py`](../d300s_tool.py) and on-camera on physical Nikon D300s hardware.

| Build | Target / Capability | Block 0 CRC (`a810_010200.bin`) | Block 1 CRC (`b810_102_.bin`) | Package MD5 (`D300S102.bin`) | Hardware Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stock v1.02** | Official Nikon Factory Firmware | `0xB506` (Stock) | `0xB00C` | `7f5503b795fc41c83a26e98d834d48ff` | Baseline |
| **Build B1** | Unlock Live View EV Compensation (`+/- EV`) at `0x00222E5A` (`F3 0E -> 9F A0`) | `0xB506` (Untouched) | `0x3F88` | `6f94e2c52950e6cf77879cb9e32c7554` | ✅ Verified on D300s |
| **Build B2** | Custom Menu (`PROJECT ARCOIRIS` / `MY MODS`) & EXIF Software Tag Redirection (`0x0EFBF0 -> 0x1F6F70`) | `0xB506` (Untouched) | `0x886B` | `15cb90f5623d95f861d8f4fc9a89660e` | ✅ Verified on D300s |
| **Build B3** | Custom Settings Menu Toggle Binding Experiment | `0xB506` (Untouched) | `0xD034` | `dc73eb1180823df108b55d9bc6b7c547` | ✅ Verified on D300s |
| **Build B4** | 64-Bin Real-Time YCbCr Luminance Histogram (`0x002D2C00`, always-on) + B1 EV Comp | `0xB506` (Untouched) | `0x0AA9` | `b4b09e180a29e37cb36f3069eb4159c8` | ✅ Verified on D300s |
| **Build B5: Native Manual** | **Native Manual (`M`) Shutter Speed & ISO Live View Exposure Simulation (`0x0012C22A`)** + B4 Histogram + B1 EV Comp | `0xB506` (Untouched) | `0x46D8` | `6549191abe995c2f2b9253b3fd55ab2a` | ✅ **Verified on D300s** |

---

## 3. Build B5: Native Manual — Static & On-Camera Verification Summary

### 3.1 Off-Camera Static Verification
1. **Zero Custom Code Injection in the AE/AGC Loop**:
   - Build B5 modifies exactly **8 bytes** (`4 × 2-byte BEQ -> NOP`) over Build B4 inside Block 1 (`0x0EC290`, `0x0EC35C`, `0x0EC41A`, `0x0EC582`).
   - All four instructions are conditional 8-bit PC-relative branches (`BEQ` `E2 xx`) whose condition (`BTSTL #0x4, @0x9F87210F`) was permanently false in stock firmware.
   - Replacing `BEQ` with `NOP` (`9F A0`) exposes Nikon's factory-compiled Manual mode check (`(*(uint8_t*)0x9F872034 >> 6) == 3`) and `CALL 0x0012C22A`.
2. **Register & Stack Hygiene**:
   - `0x0012C22A` is an original Nikon compiler-generated leaf function using only caller-saved scratch registers (`R0`, `R4`, `R5`, `R13`) and returning via `RET:D` (`9F20 1240`) directly to the caller's standard epilogue (`LDM0`/`LDM1`/`RET`).

### 3.2 On-Camera Hardware Verification
Tested on physical Nikon D300s hardware:
1. **Manual (`M`) Shutter Speed Dial**: Rotating the rear command dial from `1/25s` up to `1/8000s` adjusts Live View LCD exposure and shifts the 64-bin live luminance histogram in real time (`1/3 EV` steps).
2. **Manual (`M`) ISO Control**: With **Auto ISO Sensitivity Control** set to **OFF**, holding the **ISO** button and rotating the command dial dynamically scales CMOS sensor gain (`200` to `Hi 1`) and updates Live View brightness and the histogram in real time.
3. **Shutter Speeds Slower Than `1/25s`**: Confirmed both on-camera and in the ROM lookup table at `0x001EEB6B` (`indices 0..61 == 0x00`) that Live View integration saturates at `1/25s` due to the physical 24–30 fps CMOS rolling-shutter readout period (`33.3 ms`–`40 ms`).
4. **`P`, `S`, `A` Modes & EV Compensation**: Confirmed that non-Manual modes take the `BNE` branch to `0x0012C6D2` (stock Auto-AGC with Build B1 EV Compensation active).
