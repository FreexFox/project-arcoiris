#!/usr/bin/env python3
import struct

class FR80Assembler:
    def __init__(self, base_addr=0x002D2C00):
        self.base_addr = base_addr
        self.code = bytearray()
        self.labels = {}
        self.fixups = []  # (offset, opcode_hi, label, inst_addr)
        self.listing = []

    @property
    def pc(self):
        return self.base_addr + len(self.code)

    def label(self, name):
        self.labels[name] = self.pc

    def emit16(self, word, text=""):
        addr = self.pc
        self.code += struct.pack(">H", word)
        self.listing.append((addr, struct.pack(">H", word).hex().upper(), text))

    def emit32(self, w1, w2, text=""):
        addr = self.pc
        b = struct.pack(">HH", w1, w2)
        self.code += b
        self.listing.append((addr, b.hex().upper(), text))

    def emit48(self, w1, w2, w3, text=""):
        addr = self.pc
        b = struct.pack(">HHH", w1, w2, w3)
        self.code += b
        self.listing.append((addr, b.hex().upper(), text))

    def ldi8(self, imm8, reg):
        assert 0 <= imm8 <= 0xFF and 0 <= reg <= 15
        self.emit16(0xC000 | (imm8 << 4) | reg, f"LDI:8   #0x{imm8:02X}, R{reg}")

    def ldi20(self, imm20, reg):
        assert 0 <= imm20 <= 0xFFFFF and 0 <= reg <= 15
        w1 = 0x9B00 | (((imm20 >> 16) & 0xF) << 4) | reg
        w2 = imm20 & 0xFFFF
        self.emit32(w1, w2, f"LDI:20  #0x{imm20:05X}, R{reg}")

    def ldi32(self, imm32, reg):
        assert 0 <= imm32 <= 0xFFFFFFFF and 0 <= reg <= 15
        w1 = 0x9F80 | reg
        w2 = (imm32 >> 16) & 0xFFFF
        w3 = imm32 & 0xFFFF
        self.emit48(w1, w2, w3, f"LDI:32  #0x{imm32:08X}, R{reg}")

    def branch(self, cond_opcode, label_name, mnemonic):
        addr = self.pc
        self.fixups.append((len(self.code), cond_opcode, label_name, addr, mnemonic))
        self.code += b"\x00\x00"
        self.listing.append((addr, "????", f"{mnemonic:<7} {label_name}"))

    def bge(self, label): self.branch(0xEB00, label, "BGE")
    def bgt(self, label): self.branch(0xED00, label, "BGT")
    def ble(self, label): self.branch(0xEC00, label, "BLE")
    def beq(self, label): self.branch(0xE200, label, "BEQ")
    def bne(self, label): self.branch(0xE300, label, "BNE")
    def bc(self, label):  self.branch(0xE400, label, "BC")
    def bra(self, label): self.branch(0xE000, label, "BRA")

    def finalize(self):
        for off, cond_op, label_name, addr, mnemonic in self.fixups:
            target = self.labels[label_name]
            disp = (target - (addr + 2)) // 2
            assert -128 <= disp <= 127, f"Branch out of range: {label_name} disp={disp}"
            word = cond_op | (disp & 0xFF)
            struct.pack_into(">H", self.code, off, word)
            for idx, (l_addr, _, _) in enumerate(self.listing):
                if l_addr == addr:
                    self.listing[idx] = (addr, f"{word:04X}", f"{mnemonic:<7} 0x{target:08X} ({label_name})")
                    break
        return bytes(self.code)


def build_histogram_cave():
    a = FR80Assembler(0x002D2C00)

    # Prologue: save all registers (R0..R13, FP) and allocate 128B on stack for uint16_t bins[64]
    a.emit16(0x8FFE, "STM1    (FP,R13,R12,R11,R10,R9,R8)")
    a.emit16(0x8EFF, "STM0    (R7,R6,R5,R4,R3,R2,R1,R0)")
    a.emit16(0x8B08, "MOV     R0, R8          ; R8 = Y plane base (0x96ED9B20 / 0x96F4A320)")
    a.emit16(0xA3E0, "ADDSP   #-0x080         ; allocate 128 bytes for bins[64]")
    a.emit16(0x8BF9, "MOV     R15, R9         ; R9 = &bins[0]")

    # Phase 1: Zero bins[0..63] (128 bytes)
    a.ldi8(0x00, 0)
    a.ldi8(0x7C, 13)
    a.label("zero_loop")
    a.emit16(0x1090, "ST      R0, @(R13, R9)")
    a.emit16(0xA5CD, "ADD2    #-4, R13")
    a.bge("zero_loop")

    # Phase 2: Subsample 32 rows x 64 cols = 2048 pixels across active 640x426 Y plane
    # Start at (x=64, y=48) -> offset = 48*640 + 64 = 0x07840
    # Row step = 10 rows = 6400 = 0x01900; Col step = 8 pixels
    a.ldi20(0x07840, 4)
    a.emit16(0xA684, "ADD     R8, R4          ; R4 = row start ptr")
    a.ldi20(0x01900, 5)
    a.ldi8(0x7E, 6)   # R6 = 0x7E mask for (Y >> 2) * 2
    a.ldi8(32, 7)     # R7 = 32 sample rows
    a.label("sample_row")
    a.emit16(0x8B4A, "MOV     R4, R10         ; R10 = pixel ptr")
    a.ldi8(64, 11)    # R11 = 64 sample cols
    a.label("sample_col")
    a.emit16(0x06AD, "LDUB    @R10, R13       ; R13 = Y")
    a.emit16(0xB01D, "LSR     #1, R13         ; R13 = Y >> 1")
    a.emit16(0x826D, "AND     R6, R13         ; R13 = (Y >> 2) * 2")
    a.emit16(0x0190, "LDUH    @(R13, R9), R0  ; R0 = bins[bin]")
    a.emit16(0xA410, "ADD     #1, R0")
    a.emit16(0x1190, "STH     R0, @(R13, R9)  ; bins[bin] = R0")
    a.emit16(0xA48A, "ADD     #8, R10         ; R10 += 8")
    a.emit16(0xA5FB, "ADD2    #-1, R11")
    a.bgt("sample_col")
    a.emit16(0xA654, "ADD     R5, R4          ; R4 += 6400")
    a.emit16(0xA5F7, "ADD2    #-1, R7")
    a.bgt("sample_row")

    # Phase 3: Find max_count in R7 across bins[1..62], with minimum floor = 32
    a.ldi8(32, 7)
    a.ldi8(0x7C, 13)  # start at bin 62 (offset 124 = 0x7C)
    a.label("max_loop")
    a.emit16(0x0190, "LDUH    @(R13, R9), R0")
    a.emit16(0xAA70, "CMP     R7, R0")
    a.ble("max_skip")
    a.emit16(0x8B07, "MOV     R0, R7")
    a.label("max_skip")
    a.emit16(0xA5ED, "ADD2    #-2, R13")
    a.emit16(0xA82D, "CMP     #2, R13")
    a.bge("max_loop")

    # Phase 4A: Neutralize Cb & Cr (0x80) in 66x34 chroma block for (x=16..147, y=324..391)
    # Cb offset = 0x4B000 + 162*320 + 8 = 0x057A88
    # Cr offset = 0x5DC00 + 162*320 + 8 = 0x06A688
    a.ldi32(0x00057A88, 4)
    a.emit16(0xA684, "ADD     R8, R4          ; R4 = Cb ptr")
    a.ldi32(0x0006A688, 5)
    a.emit16(0xA685, "ADD     R8, R5          ; R5 = Cr ptr")
    a.ldi20(0x00140, 6)  # R6 = 320 chroma stride
    a.ldi8(0x80, 0)
    a.ldi8(34, 10)
    a.label("chroma_row")
    a.ldi8(65, 13)
    a.label("chroma_col")
    a.emit16(0x1240, "STB     R0, @(R13, R4)")
    a.emit16(0x1250, "STB     R0, @(R13, R5)")
    a.emit16(0xA5FD, "ADD2    #-1, R13")
    a.bge("chroma_col")
    a.emit16(0xA664, "ADD     R6, R4")
    a.emit16(0xA665, "ADD     R6, R5")
    a.emit16(0xA5FA, "ADD2    #-1, R10")
    a.bgt("chroma_row")

    # Phase 4B: Darken Y plane (Y = Y >> 2) in 132x68 box at (x=16..147, y=324..391)
    # Offset = 324*640 + 16 = 0x032A10
    a.ldi32(0x00032A10, 4)
    a.emit16(0xA684, "ADD     R8, R4          ; R4 = Y box top-left")
    a.ldi20(0x00280, 6)  # R6 = 640 luma stride
    a.ldi8(68, 10)
    a.label("box_row")
    a.ldi8(131, 13)
    a.label("box_col")
    a.emit16(0x0240, "LDUB    @(R13, R4), R0")
    a.emit16(0xB020, "LSR     #2, R0")
    a.emit16(0x1240, "STB     R0, @(R13, R4)")
    a.emit16(0xA5FD, "ADD2    #-1, R13")
    a.bge("box_col")
    a.emit16(0xA664, "ADD     R6, R4")
    a.emit16(0xA5FA, "ADD2    #-1, R10")
    a.bgt("box_row")

    # Phase 5: Draw crisp light-gray border (Y=0x98) and 25%/50%/75% vertical guide lines (Y=0x48)
    # Top border at y=325, x=17..146 (offset 325*640 + 17 = 0x032C91)
    # Bottom border at y=390, x=17..146 (offset 390*640 + 17 = 0x03CF11)
    a.ldi32(0x00032C91, 4)
    a.emit16(0xA684, "ADD     R8, R4          ; R4 = top border")
    a.ldi32(0x0003CF11, 5)
    a.emit16(0xA685, "ADD     R8, R5          ; R5 = bottom border")
    a.ldi8(0x98, 0)
    a.ldi8(129, 13)
    a.label("hborder_loop")
    a.emit16(0x1240, "STB     R0, @(R13, R4)")
    a.emit16(0x1250, "STB     R0, @(R13, R5)")
    a.emit16(0xA5FD, "ADD2    #-1, R13")
    a.bge("hborder_loop")

    # Left/Right borders (x=17, x=146 -> offset 0 and 129 from x=17) and grid lines (x=50, 82, 114 -> offset 33, 65, 97 from x=17)
    # across 64 inner rows y=326..389 (start at y=326, x=17 -> offset 326*640 + 17 = 0x032F11)
    a.ldi32(0x00032F11, 4)
    a.emit16(0xA684, "ADD     R8, R4          ; R4 = inner row start (x=17, y=326)")
    a.ldi8(0x98, 0)      # R0 = border luma 0x98
    a.ldi8(0x48, 1)      # R1 = grid line luma 0x48
    a.ldi8(64, 10)       # 64 inner rows
    a.label("vgrid_loop")
    a.emit16(0x1640, "STB     R0, @R4         ; left border (x=17)")
    a.ldi8(129, 13)
    a.emit16(0x1240, "STB     R0, @(R13, R4)  ; right border (x=146)")
    a.ldi8(33, 13)
    a.emit16(0x1241, "STB     R1, @(R13, R4)  ; 25% grid (x=50)")
    a.ldi8(65, 13)
    a.emit16(0x1241, "STB     R1, @(R13, R4)  ; 50% grid (x=82)")
    a.ldi8(97, 13)
    a.emit16(0x1241, "STB     R1, @(R13, R4)  ; 75% grid (x=114)")
    a.emit16(0xA664, "ADD     R6, R4          ; R4 += 640")
    a.emit16(0xA5FA, "ADD2    #-1, R10")
    a.bgt("vgrid_loop")

    # Phase 6: Draw 64 vertical 2px-wide histogram bars (Y=0xF0) from baseline y=389 (x=18..145)
    # Baseline (x=18, y=389) offset = 389*640 + 18 = 0x03CC92
    a.ldi32(0x0003CC92, 4)
    a.emit16(0xA684, "ADD     R8, R4          ; R4 = baseline bar ptr (x=18, y=389)")
    a.ldi8(0xF0, 5)      # R5 = 0xF0 bright white bar luma
    a.ldi8(0, 11)        # R11 = bin byte offset (0..126 step 2)
    a.label("bin_loop")
    a.emit16(0x8BBD, "MOV     R11, R13")
    a.emit16(0x0190, "LDUH    @(R13, R9), R0  ; R0 = bins[b]")
    a.emit16(0xA800, "CMP     #0, R0")
    a.beq("next_bin")
    a.emit16(0xAA70, "CMP     R7, R0          ; compare bins[b] vs max_count")
    a.bc("do_div")
    a.ldi8(64, 2)        # clamp height to 64
    a.bra("draw_bar")

    a.label("do_div")
    a.ldi8(0, 2)         # R2 = quot = 0
    a.ldi8(6, 3)         # R3 = 6 bits
    a.label("div_loop")
    a.emit16(0xB410, "LSL     #1, R0")
    a.emit16(0xB412, "LSL     #1, R2")
    a.emit16(0xAA70, "CMP     R7, R0")
    a.bc("div_skip")
    a.emit16(0xAC70, "SUB     R7, R0")
    a.emit16(0xA412, "ADD     #1, R2")
    a.label("div_skip")
    a.emit16(0xA5F3, "ADD2    #-1, R3")
    a.bgt("div_loop")
    a.emit16(0xA802, "CMP     #0, R2")
    a.bne("draw_bar")
    a.ldi8(1, 2)         # non-zero bin gets at least 1px bar

    a.label("draw_bar")
    a.emit16(0x8B4A, "MOV     R4, R10         ; R10 = bottom of bar")
    a.ldi8(1, 13)        # R13 = 1 (for 2nd pixel column)
    a.label("bar_loop")
    a.emit16(0x16A5, "STB     R5, @R10")
    a.emit16(0x12A5, "STB     R5, @(R13, R10)")
    a.emit16(0xAC6A, "SUB     R6, R10         ; move 1 row up (-640)")
    a.emit16(0xA5F2, "ADD2    #-1, R2")
    a.bgt("bar_loop")

    a.label("next_bin")
    a.emit16(0xA424, "ADD     #2, R4          ; next bar x += 2")
    a.emit16(0xA42B, "ADD     #2, R11         ; next bin offset += 2")
    a.ldi8(0x80, 0)
    a.emit16(0xAA0B, "CMP     R0, R11")
    a.bc("bin_loop")

    # Epilogue: free 128B stack, restore R0..R13, FP, perform displaced LCD Y DMA write, RET
    a.emit16(0xA320, "ADDSP   #0x080")
    a.emit16(0x8CFF, "LDM0    (R0,R1,R2,R3,R4,R5,R6,R7)")
    a.emit16(0x8D7F, "LDM1    (R8,R9,R10,R11,R12,R13,FP)")
    a.ldi32(0x40040018, 12)
    a.emit16(0x14C0, "ST      R0, @R12        ; 0x40040018")
    a.emit16(0x9720, "RET")

    code = a.finalize()
    return a, code

if __name__ == "__main__":
    import subprocess, shutil, hashlib, os
    from pathlib import Path

    repo_dir = Path(__file__).resolve().parent.parent
    d300s_tool = repo_dir / "scripts" / "d300s_tool.py"
    if not d300s_tool.exists():
        d300s_tool = repo_dir / "d300s_tool.py"

    a, code = build_histogram_cave()
    print(f"Total assembled size: {len(code)} bytes (0x{len(code):X})")
    for addr, hex_b, txt in a.listing:
        print(f"  {addr:08X}  {hex_b:<12}  {txt}")

    old_cave_hex = "ff" * len(code)
    new_cave_hex = code.hex()

    stock_fw = repo_dir / "D300SUpdate" / "D300S102.bin"
    flash_dir = repo_dir / "FLASH" / "BRANDING"
    flash_dir.mkdir(parents=True, exist_ok=True)
    out_b4 = flash_dir / "D300S102_ARCOIRIS_B4.bin"
    out_flash = flash_dir / "D300S102.bin"

    edits = [
        # 1. Menu & Version Branding
        f"1:0x427FC2:{b'CUSTOM SETTING MENU'.hex()}:{b'PROJECT ARCOIRIS   '.hex()}",
        f"1:0x42829A:{b'Firmware version'.hex()}:{b'Project ArcoIris'.hex()}",
        f"1:0x428581:{b'MY MENU'.hex()}:{b'MY MODS'.hex()}",
        # 2. EXIF Software Tag Branding ("ArcoIris")
        "1:0x114CD9:0efbf004:1f6f708b",
        "1:0x12767F:0efbf0:1f6f70",
        "1:0x12769E:04:8b",
        f"1:0x1B6F70:{b'2013/04/11 for mass production'.hex()}:{b'ArcoIris\x00 Project ArcoIris B4\x00'.hex()}",
        # 3. Direct Live View Exposure Simulation (NOP at 0x00222E5A)
        "1:0x1E2E5A:f30e:9fa0",
        # 4. Live View Real-Time Histogram Hook (0x0013598E) + Code Cave (0x002D2C00)
        "1:0x0F598E:9f8c4004001814c0:9f8c002d2c00971c",
        f"1:0x292C00:{old_cave_hex}:{new_cave_hex}",
    ]

    cmd = ["python3", str(d300s_tool), "patch", str(stock_fw), str(out_b4)]
    for e in edits:
        cmd.extend(["--edit", e])

    subprocess.run(cmd, check=True)
    shutil.copy2(str(out_b4), str(out_flash))
    subprocess.run(["python3", str(d300s_tool), "info", str(out_b4)], check=True)

    for path in [stock_fw, out_b4, out_flash]:
        h = hashlib.md5(open(path, "rb").read()).hexdigest()
        print(f"MD5 {path}: {h}")

