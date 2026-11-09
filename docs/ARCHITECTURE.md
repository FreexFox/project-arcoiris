# Project ArcoIris — Architecture & Firmware Internals

This document details the firmware container format, dual-CPU architecture, inter-processor communication (IPC), memory layout, and encryption mechanisms of the Nikon D300s DSLR (v1.02).

---

## 1. Dual-CPU Architecture

The Nikon D300s employs a heterogeneous dual-processor architecture:

1. **Sub-CPU / IO & Power Controller (Block 0: `a810_010200.bin`)**:
   - **Size**: `524,290` bytes (`512 KB` + 2-byte CRC `0xB506`).
   - **Architecture**: Hitachi / Renesas **H8S**.
   - **Role**: Manages power states, battery handshake, physical buttons, command dials, top status LCD, 1,005-pixel RGB optical viewfinder metering, and flash control.
   - **CRITICAL SAFETY RULE**: Block 0 must **NEVER** be modified. Flashing a corrupted Block 0 can permanently brick the camera by disabling the bootloader and power management subsystem.

2. **Main Application Processor (Block 1: `b810_102_.bin`)**:
   - **Size**: `7,340,032` bytes (`7.00 MB`, stock CRC `0xB00C`, Build B5 CRC `0x46D8`).
   - **Architecture**: **Fujitsu FR80 (FR-V / FR series RISC)**, 32-bit big-endian.
   - **Base Load Address**: **`0x00040000`** (`Virtual Address = Block 1 File Offset + 0x00040000`).
   - **Role**: Runs the real-time operating system (μITRON derivative), EXPEED imaging pipeline, CMOS sensor timing/gain drivers, Live View AE/AGC state machine, menu UI, autofocus, and CF/SD filesystems.

---

## 2. Firmware Package Container & XOR Layer

Official Nikon firmware updates (`D300S102.bin`, `7,864,450` bytes) are packaged in a binary container obfuscated with a 3-table bytewise XOR stream cipher.

### 2.1 Container Structure
- **Header (`0x000000..0x00001F`)**: 32-byte package header.
- **Block Directory (`0x000020..0x00006F`)**:
  - `0x20`: Big-endian 32-bit block count (`2`).
  - Directory entries (`32` bytes each):
    - `0x30`: Entry 0 (`a810_010200.bin`), offset `0x000070`, length `524,290` bytes.
    - `0x50`: Entry 1 (`b810_102_.bin`), offset `0x080072`, length `7,340,032` bytes.
- **Block 0 Data (`0x000070..0x080071`)**: Sub-CPU payload, ending in big-endian CRC-16 (`0xB506`).
- **Block 1 Data (`0x080072..0x780071`)**: Main FR80 payload, ending in big-endian CRC-16.
- **Trailer (`0x780072..0x780081`)**: 16-byte static trailer (`F7 6F 00 ... 00`).

### 2.2 3-Table XOR Cipher
Every byte at file offset `i` in the encrypted `.bin` package is transformed using three 256-byte lookup tables ($T_1, T_2, T_3$):

$$\text{byte}[i] \leftarrow \text{byte}[i] \oplus T_1[i \bmod 256] \oplus T_2[\lfloor i / 256 \rfloor \bmod 256] \oplus T_3[\lfloor i / 65536 \rfloor \bmod 256]$$

In C / Python bitwise notation:
```python
byte[i] ^= T1[i & 0xFF] ^ T2[(i >> 8) & 0xFF] ^ T3[(i >> 16) & 0xFF]
```

Because XOR is self-inverse, decryption and encryption are identical. The three 256-byte tables yield a repetition period of $2^{24}$ bytes (`16,777,216` bytes, ~16.7 MB).

### 2.3 Checksum Algorithm
Each block ends with a 2-byte big-endian **CRC-16/XMODEM** (polynomial `0x1021`, initial value `0x0000`, no reflection, final XOR `0x0000`) computed over all preceding bytes of that block:

```python
crc = crc16_xmodem(block[:-2])
```

By the algebraic property of CRC-16/XMODEM, computing the checksum across the entire block *including* its 2-byte big-endian CRC always yields `0x0000`.

---

## 3. Main Memory, IPC & Hardware Register Map

Address conversion between Block 1 file offset (`b810_102_.bin`) and Main-CPU virtual address:

```text
Virtual Address (VA) = Block 1 Offset + 0x00040000
Bundle Offset        = Block 1 Offset + 0x00080072
```

| Virtual Address | Component / Function |
| :--- | :--- |
| `0x00040000 - 0x0073FFFF` | Main Firmware Code & Read-Only Data (`b810_102_.bin`) |
| `0x0012AF88 - 0x0012C8B6` | **Live View AE / AGC Exposure State Machine** |
| `0x0012C22A` | **Dormant Factory Manual (`M`) Live View Exposure Loader** (Unlocked in **Build B5**) |
| `0x0012C290`, `0x0012C35C`, `0x0012C41A`, `0x0012C582` | **4 Live View AE/AGC Entry Gates** (`BEQ -> NOP` in **Build B5**) |
| `0x0012FC16 - 0x0012FCF8` | **`task_0x03`**: Live View CMOS Sensor Shutter (`0x0012F27A`) & Gain (`0x0012E4E4`) Writer |
| `0x0013598E` | **Live View Display Buffer Flip Hook** (Redirected to `0x0025DA60` in **Build B4/B5**) |
| `0x001EEA6B - 0x001EED6A` | **Live View CMOS Electronic Shutter & Gain Lookup Tables** (256-byte LUTs) |
| `0x001EF0FC` | **Sub-CPU IPC Descriptor Entry 21** (Populates `0x9F872034`, 14 bytes) |
| `0x00222E5A` | **Live View EV Compensation Gate** (`F3 0E -> 9F A0` unlocked in **Build B1**) |
| `0x0025DA60 - 0x0025DAE0` | **`INFO`-Button Visibility Wrapper** for Live Histogram (**Build B4/B5**) |
| `0x002D2C00 - 0x002D2D3A` | **64-Bin YCbCr Luminance Histogram Engine** (`314` bytes FR80 assembly, **Build B4/B5**) |
| `0x40040018` | **LCD Controller Y-Plane DMA Base Address Register** |
| `0x96ED9B20` / `0x96F4A320` | **Live View YCbCr 4:2:0 Ping-Pong Framebuffers** ($640 \times 480$) |
| `0x9F8711FC` | **`lv_agc_struct`**: Live View AGC State (`+0x1D` ISO, `+0x1E` Av, `+0x1F` Tv, `+0x010E` Fine Gain) |
| `0x9F872028` / `0x9F872029` | **Active Hardware CMOS Shutter (`0x9F872028`) & Gain (`0x9F872029`) Staging Registers** |
| `0x9F872034` | **Sub-CPU IPC Exposure Struct** (`+0x00` Mode bits `7:6`, `+0x02` ISO, `+0x05` Av, `+0x09` Tv) |
| `0x9F87210F` | **Live View Feature Bitmask** (Bit `0x04` permanently cleared in stock ROM; bypassed in **Build B5**) |
| `0x9F87CBA9` | **Live View `INFO` Overlay Mode State** (`0x03` = Clean HDMI / Clean Display, hides Histogram) |
