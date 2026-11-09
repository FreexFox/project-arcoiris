# Project ArcoIris — Architecture & Firmware Internals

This document details the firmware container format, CPU architecture, memory layout, and encryption mechanisms of the Nikon D300s DSLR.

---

## 1. Dual-CPU Architecture

The Nikon D300s employs a heterogeneous dual-processor architecture:

1. **Sub-CPU / IO & Power Controller (Block 0: `a810_010200.bin`)**:
   - Size: 524,290 bytes (512 KB + 2-byte CRC).
   - Manages power states, battery communication, physical buttons, top status LCD, and flash controller.
   - **CRITICAL SAFETY RULE**: Block 0 must **NEVER** be modified. Flashing a corrupted Block 0 can permanently brick the camera by disabling the bootloader and battery management sub-system.

2. **Main Application Processor (Block 1: `b810_102_.bin`)**:
   - Size: 7,340,032 bytes (~7 MB).
   - Architecture: **Fujitsu FR80 (FR series RISC)**, 32-bit big-endian.
   - Base Load Address: **`0x00040000`**.
   - Handles the real-time operating system (ITRON / μITRON derivative), image processing pipeline, EXPEED imaging engine control, menu system, autofocus algorithms, SD/CF filesystem, and Live View display.

---

## 2. Firmware Package Container & XOR Layer

Official Nikon firmware updates (`D300S102.bin`, 7,864,450 bytes) are packaged in a proprietary container encrypted with a 3-table XOR stream cipher.

### 2.1 Container Structure
- **Header (`0x00..0x1F`)**: 32-byte header with package metadata.
- **Block Directory (`0x20..0x6F`)**:
  - `0x20`: Big-endian 32-bit block count (always `2`).
  - Directory entries (32 bytes each):
    - `0x30`: Entry 0 (`a810_010200.bin`), offset `0x70`, length `524,290` bytes.
    - `0x50`: Entry 1 (`b810_102_.bin`), offset `0x80072`, length `7,340,032` bytes.
- **Block 0 Data (`0x000070..0x080071`)**: Sub-CPU payload, ending in big-endian CRC-16.
- **Block 1 Data (`0x080072..0x780071`)**: Main FR80 payload, ending in big-endian CRC-16.
- **Trailer (`0x780072..0x780081`)**: 16-byte trailer (`F7 6F 00 ... 00`). Not validated by the camera updater.

### 2.2 3-Table XOR Cipher
Every byte at offset `i` in the package is encrypted via:
$$\text{byte}[i] \leftarrow \text{byte}[i] \oplus T_1[i \ \& \ 255] \oplus T_2[(i \gg 8) \ \& \ 255] \oplus T_3[(i \gg 16) \ \& \ 255]$$

Because XOR is self-inverse, decryption and encryption use identical operations. The tables $T_1$, $T_2$, and $T_3$ are 256 bytes each with a repetition period of $2^{24}$ bytes (~16.7 MB).

### 2.3 Checksum Algorithm
Each block ends with a 2-byte **CRC-16/XMODEM** (polynomial `0x1021`, initial value `0x0000`):
$$\text{CRC} = \text{CRC-16/XMODEM}(\text{payload}[0 \dots \text{len}-3])$$

When computed over the entire block (including the stored CRC bytes), the resulting CRC is always `0x0000`.

---

## 3. Main Memory & Register Map

Address calculations in Block 1 follow:
$$\text{Physical Address} = \text{Block 1 Offset} + \text{0x00040000}$$

| Address Range | Component / Function |
| :--- | :--- |
| `0x00040000 - 0x0073FFFF` | Main Firmware Code & Read-Only Data (Flash / SDRAM mirror) |
| `0x002D2C00 - 0x002D3000` | Code Cave Region (`0xFF` padding in stock firmware) |
| `0x40000000 - 0x4004003F` | Image Processing & Display Hardware Controller Registers |
| `0x40040018` | **LCD Controller Y-Plane DMA Base Address Register** |
| `0x90000000 - 0x97FFFFFF` | Main SDRAM (128 MB) |
| `0x96ED9B20` | Live View Ping-Pong Buffer 0 (YCbCr 4:2:0) |
| `0x96F4A320` | Live View Ping-Pong Buffer 1 (YCbCr 4:2:0) |
| `0x9F92DFDC` | Current Active Live View Buffer Index (`0` or `1`) |
