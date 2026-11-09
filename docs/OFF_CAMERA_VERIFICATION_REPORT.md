# Nikon D300S Firmware RE: Off-Camera Verification Report

Oct 31, 2026 · @Nguyễn Thắng Lợi

## Container format and the 16-byte trailer

The 16-byte trailer is a package CRC that the D300S camera very likely does not enforce: the stock image itself fails the obvious CRC rule and ships anyway.

The decoded D300S 1.02 bundle is 7,864,450 bytes. It holds a 32-byte header, a directory at 0x20 (two files, directory size 0x70), the A block (`a810_010200.bin`, offset 0x70, 524,290 bytes), the B block (`b810_102_.bin`, offset 0x80072, 7,340,032 bytes) and a 16-byte trailer at 0x780072 (`F76F` plus 14 zero bytes). Each block ends in its own CRC16.

| Check | Result |
| --- | --- |
| Block A CRC (stored / computed) | B506 / B506, match |
| Block B CRC (stored / computed) | B00C / B00C, match |
| CRC of each block including its own CRC | 0000 for both, same property the Z-series docs describe |
| Package CRC rule (CRC16/XMODEM over file minus trailer) | computed 2DD4, stored F76F, **mismatch** |
| Sweep: 8 polynomials, all reflection/init/xor variants, 45 byte ranges, decoded and raw files | 5,760 combinations per file, 0 hits (about 0.2 expected by chance) |

Two outside sources explain the shape. The [WonderLantern nikon-fw-key-tool](https://github.com/WonderLantern/nikon-fw-key-tool) README documents the same container for Z-series bodies: the trailer is a big-endian 16-bit package CRC followed by 14 zero bytes, and repairing module CRCs leaves the package CRC unchanged. Simeon Pilgrim's [2011 firmware notes](https://simeonpilgrim.com/blog/2011/11/18/nikon-firmware-insights-01/) say the footer holds "a checksum and padding" and that "the package checksum is not checked".

The inference: Nikon's own stock file fails the simple package-CRC rule, so the camera cannot be enforcing that rule. This agrees with the community Star Eater patch, which never rewrites the trailer and is released for this exact stock hash (MD5 `7f5503b795fc41c83a26e98d834d48ff`). Confidence: strong circumstantial evidence, not proof, because nobody has observed the camera's own check.

The D300S XOR tables share the Z-series structure (three 256-byte tables, 2^24-byte period) but not the values: their SHA-256 prefixes differ from the Z tables' published ones. The first 32 header bytes remain unexplained; the community patches leave them untouched.

## Audit of the Phase 2 report

The Phase 2 report is right about the patch sites and wrong or unsupported on several claims that matter for safety. I checked each against our disassembly, the community repo and Simeon Pilgrim's notes.

| Phase 2 claim | Verdict | Evidence |
| --- | --- | --- |
| Star Eater patch reproduces the community output byte-for-byte | **Confirmed** | Same MD5 (`1d65e70d598fb9eb9c79e06563e7ed0d`) as our build of the community tool from source |
| Patch sites 0x127F34 and 0x128186 are `BGT` flipped to `BRA`, no delay slots | **Confirmed** | Listings match our disassembly instruction for instruction |
| Flag byte at +0x111 is signed 1/6-EV units, 0x0C is 1/4 s | **Plausible** | Code path confirmed (`0x222E76` sets the offset, value scaled by 64/6 into `0x9FD001DE`); the "shutter speed" label is an inference |
| Bit +0x2C&0x04 has a **sole consumer** at 0x122FB2 | **Contradicted** | Four more readers test it: 0x1222F2, 0x13A62C, 0x13C89E, 0x1C1982 |
| The two-site patch keeps the flag at 0 | **Contradicted** | A third setter at 0x12815A sets bits 0x02 and 0x04 with no exposure test, when bit 7 of byte +0x189 is clear |
| Quote from Form1.cs: "Exposure times of 1/4 second or slower..." | **Not found** | Absent from the repo; the real help text says the patch is "for astrophotography ONLY" |
| Sensor is Sony IMX021 | **Conflicts** | The community camera matrix lists the D300 and D300s as Sony IMX038; the report cites no source |
| Block 0 is a protected-ROM bootloader with CF-card recovery | **Unsupported** | Simeon documents the A file as the IO-control CPU firmware; our D300 v1.10 to v1.11 diff shows A is reflashed by Nikon updates; no source for any recovery path |
| Candidate Patch A is "VERIFIED SAFE" | **Overstated** | Verified identical to community output; never tested on this camera |
| Trailer is preserved by "all official updaters" | **Unsupported** | Only the community tool is known to leave it untouched |
| Emulator plan: run Block 1 in the Java emulator to confirm the patched branches | **Weak** | That emulator's peripheral models are for D5100-class bodies; it has no D300S register map |
| 0x9F88C8E8 to 0x9F88C8F5 are R/Gr/Gb/B gain registers, "VERIFIED" | **Not tested** | Labelled verified while the report's own table says register specs are unknown; treat as inference |

What survives: the Star Eater edit itself is a one-byte change at each of two conditional branches, and the patched path is one the stock firmware already takes for every exposure shorter than 1/4 s. That argument is about control flow only. It does not show that the camera accepts the file.
