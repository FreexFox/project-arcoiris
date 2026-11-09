# Project ArcoIris — Live Histogram Assembly Engine

This document describes the 314-byte Fujitsu FR80 assembly engine residing at `0x002D2C00` (Block 1 offset `0x292C00`) and its `INFO`-button visibility wrapper at `0x0025DA60` (Block 1 offset `0x21DA60`), included in **Builds B4 and B5: Native Manual**.

---

## 1. Design Constraints & Performance

- **Target CPU**: Fujitsu FR80 RISC @ 133 MHz.
- **Frame Budget**: Live View runs at 24–30 FPS (`33.3 ms` to `40 ms` per frame). The histogram engine completes in **85,233 cycles (~0.64 ms)**, consuming under **2% of frame CPU time**.
- **Footprint**:
  - `314` bytes at `0x002D2C00` (core 64-bin YCbCr sampling, normalization, and drawing routine).
  - `128` bytes at `0x0025DA60` (`INFO`-button overlay mode check and frame dispatcher).
- **Register Hygiene**: Saves all general-purpose registers (`R0..R13, FP`) using `STM0` / `STM1` and restores them using `LDM0` / `LDM1`. The 128-byte histogram bin array is allocated and freed cleanly on the stack via `ADDSP #-0x80` / `ADDSP #0x80`.

---

## 2. Processing Pipeline

### Step 0: `INFO` Button Visibility Check (`0x0025DA60`)
Before running the histogram engine, the hook wrapper reads `*(uint8_t*)0x9F87CBA9` (the active Live View `INFO` overlay mode). If the user has cycled the `INFO` button to the clean display / HDMI output mode (`0x03`), the wrapper skips drawing the histogram and immediately commits the pristine frame to the LCD DMA controller (`0x40040018`).

### Step 1: Subsampling & Binning (2,048 Pixels)
Instead of scanning all `272,640` Y-plane pixels (which would take ~15 ms per frame), the engine samples a uniform grid across the active sensor image (`640 × 426`):
- **Columns**: `64` samples per row (`x = 64 .. 568`, step `8` pixels)
- **Rows**: `32` rows (`y = 48 .. 358`, step `10` rows)
- **Total samples**: `64 × 32 = 2,048` pixels

Each sampled 8-bit luminance value $Y \in [0, 255]$ is mapped into one of 64 bins:

$$\text{bin} = \lfloor Y / 4 \rfloor \quad (0 \le \text{bin} \le 63)$$

In bitwise form: `bin = Y >> 2`. Each `bins[bin]` counter is stored as a 16-bit unsigned integer on the stack (`ADDSP #-0x80`). Because it samples the live YCbCr backbuffer produced by the EXPEED pipeline, the histogram automatically reflects **Build B5: Native Manual** Shutter Speed and ISO changes as well as **Build B1** EV Compensation changes in real time.

### Step 2: Peak Detection & Anti-Clip Normalization
To prevent a bright clipped sky (`bin 63`) or crushed shadow backdrop (`bin 0`) from flattening the midtone distribution:
- The engine scans interior bins `bins[1 .. 62]` to find the peak midtone count.
- The peak is clamped with a minimum floor of `32`:

$$\mathrm{max\_count} = \max\left(\max_{1 \le b \le 62} \mathrm{bins}[b],\; 32\right)$$

### Step 3: Smoked-Glass Translucent Background
The background box (`x = 16 .. 147`, `y = 324 .. 391`) is blended directly into the off-screen YCbCr 4:2:0 frame:
1. **Chroma Desaturation**: The corresponding `Cb` (`+0x57A88`) and `Cr` (`+0x6A688`) chroma planes are set to neutral achromatic gray (`0x80`).
2. **Translucent Dimming**: Existing Y-plane luminance pixels inside the box are right-shifted by 2 (`Y = Y >> 2`), dimming the underlying scene to 25% brightness so the scene remains faintly visible through the widget.

### Step 4: Frame & Zone Divider Lines
- **Outer border** (`x = 17 .. 146`, `y = 325 .. 390`): 1 px light gray border (`Y = 0x98`).
- **Quarter-tone zone guides**: 3 vertical dashed guide lines at 25% (`x = 50`), 50% (`x = 82`), and 75% (`x = 114`) luminance (`Y = 0x48`).

### Step 5: 64-Bar Fixed-Point Scaling & Drawing
For each bin $b \in [0, 63]$:
- If `bins[b] == 0`, bar height is `0`.
- If `bins[b] >= max_count`, bar height is clamped to `64` px.
- Otherwise, a 6-bit fixed-point restoring division loop computes:

$$\mathrm{height} = \left\lfloor \frac{\mathrm{bins}[b] \times 64}{\mathrm{max\_count}} \right\rfloor$$

- Each bin is drawn as a 2-pixel-wide solid white vertical bar (`Y = 0xF0`) rising upward from baseline `y = 389`.

---

## 3. Core Disassembly Listing (`0x002D2C00`)

```assembly
002D2C00: 8FFE          STM1    (FP,R13,R12,R11,R10,R9,R8)
002D2C02: 8EFF          STM0    (R7,R6,R5,R4,R3,R2,R1,R0)
002D2C04: 8B08          MOV     R0, R8          ; R8 = Y plane base (0x96ED9B20 / 0x96F4A320)
002D2C06: A3E0          ADDSP   #-0x080         ; allocate 128 bytes for uint16_t bins[64]
002D2C08: 8BF9          MOV     R15, R9         ; R9 = &bins[0]
; ... Zero 64 bins ...
002D2C14: 9B04 7840     LDI:20  #0x07840, R4    ; row start offset (y=48, x=64)
; ... Subsample 64x32 = 2,048 Y-plane pixels ...
002D2C3E: C207          LDI:8   #0x20, R7       ; min peak floor = 32
; ... Find max non-clipped peak in bins[1..62] ...
002D2C50: 9F84 00057A88 LDI:32  #0x00057A88, R4 ; Cb plane offset for box
002D2C58: 9F85 0006A688 LDI:32  #0x0006A688, R5 ; Cr plane offset for box
; ... Neutralize box chroma to 0x80 ...
002D2C7A: 9F84 00032A10 LDI:32  #0x00032A10, R4 ; Y plane offset for box (y=324, x=16)
; ... Dim Y plane (Y >>= 2), draw border & 25%/50%/75% guides ...
; ... Render 64 histogram bars (2px wide each) with 6-bit restoring division ...
002D2D2A: A320          ADDSP   #0x080          ; free stack frame
002D2D2C: 8CFF          LDM0    (R0..R7)
002D2D2E: 8D7F          LDM1    (R8..R13, FP)
002D2D30: 9F8C 40040018 LDI:32  #0x40040018, R12
002D2D36: 14C0          ST      R0, @R12        ; displaced LCD DMA base write
002D2D38: 9720          RET
```
