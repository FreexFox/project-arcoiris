#!/usr/bin/env python3
"""
Build B5: Native Manual — Native Manual Live View Exposure Simulation + Live Histogram
======================================================================================
Builds Project ArcoIris Build B5 on top of Build B4 by unlocking Nikon's dormant
factory Manual Live View exposure routine `0x0012C22A` via four 2-byte `BEQ -> NOP`
patches in Block 1 (`b810_102_.bin`):

  - Gate 1 (LV Entry / Large-Delta Mode A): VA 0x0012C290 (Block 1 + 0x0EC290): E2 09 -> 9F A0
  - Gate 2 (Per-Frame Tracking Mode A):     VA 0x0012C35C (Block 1 + 0x0EC35C): E2 09 -> 9F A0
  - Gate 3 (LV Entry / Large-Delta Mode B): VA 0x0012C41A (Block 1 + 0x0EC41A): E2 0C -> 9F A0
  - Gate 4 (Per-Frame Tracking Mode B):     VA 0x0012C582 (Block 1 + 0x0EC582): E2 0C -> 9F A0

Hardware-verified on physical Nikon D300s (v1.02).
Block 0 (`a810_010200.bin`) is verified 100% bit-for-bit untouched (`CRC 0xB506`).
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(ROOT, "d300s_tool.py")
BASE_B4 = os.path.join(ROOT, "FLASH", "REFLASH B4", "D300S102.bin")
OUT_B5 = os.path.join(ROOT, "FLASH", "REFLASH B5", "D300S102.bin")


def main():
    if not os.path.exists(BASE_B4):
        print(f"Error: Base B4 firmware not found at {BASE_B4}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUT_B5), exist_ok=True)
    cmd = [
        sys.executable,
        TOOL,
        "patch",
        BASE_B4,
        OUT_B5,
        "--allow-unknown-stock",
        "--edit", "1:0x0EC290:E209:9FA0",
        "--edit", "1:0x0EC35C:E209:9FA0",
        "--edit", "1:0x0EC41A:E20C:9FA0",
        "--edit", "1:0x0EC582:E20C:9FA0",
    ]
    subprocess.run(cmd, check=True)
    subprocess.run([sys.executable, TOOL, "info", OUT_B5], check=True)


if __name__ == "__main__":
    main()
