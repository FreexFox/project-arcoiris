# Project ArcoIris — Live Histogram Assembly Engine

This document describes the 314-byte Fujitsu FR80 assembly engine residing at `0x002D2C00` (Block 1 offset `1:0x292C00`).

---

## 1. Design Constraints & Performance

- **Target CPU**: Fujitsu FR80 RISC @ 133 MHz.
- **Frame Budget**: Live View runs at 30 FPS (~33.3 ms per frame). The engine completes in **85,233 cycles (~0.64 ms)**, using under **2% of frame CPU capacity**.
- **Footprint**: Exactly 314 bytes of code, fitting safely into unused padding (`0xFF`) at `0x002D2C00`.
- **Register Hygiene**: Saves all general-purpose registers (`R0..R13, FP`) using `STM0` / `STM1` and restores them using `LDM0` / `LDM1`. Stack frame is cleanly allocated and freed via `ADDSP`.

---

## 2. Processing Pipeline

### Step 1: Subsampling & Binning (2,048 Pixels)
Instead of processing all 272,640 pixels (which would take ~15 ms), the engine takes a regular subsample across the active display:
- Columns: 64 samples per row ($x = 64 \dots 568$, step 8 pixels)
- Rows: 32 rows ($y = 48 \dots 358$, step 10 rows)
- Total samples: $64 \times 32 = 2,048$ pixels

Each sampled luminance value $Y \in [0, 255]$ is mapped to 64 bins:
$$\text{bin} = Y \gg 2 \quad (0 \le \text{bin} \le 63)$$
`bins[bin]` is stored as a 16-bit counter in stack memory (`ADDSP #-0x80`).

### Step 2: Peak Detection & Anti-Clip Normalization
To prevent an overexposed sky or deep shadow background from flattening the midtone histogram:
- The engine searches for `max_count` across interior bins `bins[1 .. 62]` only.
- Clamped with a floor:
  $$\text{max\_count} = \max(\max(\text{bins}[1 \dots 62]), 32)$$
This guarantees that dynamic range across midtones remains clear even in extreme lighting.

### Step 3: Smoked-Glass Translucent Background
The background box ($x = 16 \dots 147, y = 324 \dots 391$) is rendered directly into the frame:
1. **Desaturation**: Chroma planes `Cb` (`+0x57A88`) and `Cr` (`+0x6A688`) are set to neutral gray (`0x80`).
2. **Translucent Dimming**: Existing luminance values in the Y plane are shifted right by 2 ($Y \leftarrow Y \gg 2$), reducing brightness to 25% while preserving visibility of underlying image details.

### Step 4: Frame & Zone Divider Lines
- Outer border ($x = 17 \dots 146, y = 325 \dots 390$): 1px light gray line ($Y = \text{0x98}$).
- Tonal zone guides: 3 vertical dashed grid lines at 25% ($x=50$), 50% ($x=82$), and 75% ($x=114$) ($Y = \text{0x48}$).

### Step 5: 64-Bar Fixed-Point Scaling & Drawing
For each bin $b \in [0, 63]$:
- If `bins[b] == 0`, bar height is 0.
- If `bins[b] >= max_count`, bar height is clamped to 64 px.
- Otherwise, a 6-bit fixed-point restoring division computes:
  $$\text{height} = \left\lfloor \frac{\text{bins}[b] \times 64}{\text{max\_count}} \right\rfloor$$
- Vertical bar of width 2px is drawn in solid white ($Y = \text{0xF0}$) from baseline $y = 389$ upwards.

---

## 3. Disassembly Listing

```assembly
002D2C00  8FFE          STM1    (FP,R13,R12,R11,R10,R9,R8)
002D2C02  8EFF          STM0    (R7,R6,R5,R4,R3,R2,R1,R0)
002D2C04  8B08          MOV     R0, R8          ; R8 = Y plane base
002D2C06  A3E0          ADDSP   #-0x080         ; allocate 128 bytes for bins[64]
002D2C08  8BF9          MOV     R15, R9         ; R9 = &bins[0]
; ... Zero bins ...
002D2C14  9B047840      LDI:20  #0x07840, R4    ; row start offset (y=48, x=64)
; ... Subsample 2,048 pixels ...
002D2C3E  C207          LDI:8   #0x20, R7       ; min floor = 32
; ... Find max non-clipped peak in bins[1..62] ...
002D2C50  9F8400057A88  LDI:32  #0x00057A88, R4 ; Cb plane
002D2C58  9F850006A688  LDI:32  #0x0006A688, R5 ; Cr plane
; ... Neutralize chroma to 0x80 ...
002D2C7A  9F8400032A10  LDI:32  #0x00032A10, R4 ; Y box
; ... Darken Y plane (Y >>= 2) ...
; ... Draw border & 25%/50%/75% guides ...
; ... Render 64 histogram bars with restoring division ...
002D2D2A  A320          ADDSP   #0x080          ; free stack
002D2D2C  8CFF          LDM0    (R0..R7)
002D2D2E  8D7F          LDM1    (R8..R13, FP)
002D2D30  9F8C40040018  LDI:32  #0x40040018, R12
002D2D36  14C0          ST      R0, @R12        ; displaced instruction
002D2D38  9720          RET
```
