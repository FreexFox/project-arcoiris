#!/usr/bin/env python3
"""
d300s_tool.py - off-camera bench tool for Nikon D300S firmware bundles (v1.02 verified).

    stock .bin --XOR--> plaintext bundle --guarded byte edits--> fix block CRCs --XOR--> new .bin

Format knowledge comes from Simeon Pilgrim's nikon-firmware-tools
(github.com/simeonpilgrim/nikon-firmware-tools); the three XOR tables below are copied from its xor.c.
  * XOR layer : byte i ^= T1[i&255] ^ T2[(i>>8)&255] ^ T3[(i>>16)&255]   (self-inverse)
  * header    : big-endian; block count @0x20; 32-byte records from 0x30 = name[16], offset, length, 0, 0
  * each block ends with CRC-16/XMODEM (poly 0x1021, init 0) over the block minus its last 2 bytes, big-endian

Nothing here touches a camera. Verify every output off-camera before it goes anywhere near hardware.

usage:
  d300s_tool.py info     STOCK.bin
  d300s_tool.py decode   STOCK.bin OUTDIR
  d300s_tool.py selftest STOCK.bin
  d300s_tool.py patch    STOCK.bin OUT.bin --edit BLK:OFFSET:BEFORE_HEX:AFTER_HEX [--edit ...] [--allow-unknown-stock]
      e.g. --edit 1:0x0E7F34:ED12:E012      (block index, offset inside that block, expected stock bytes, new bytes)
"""
import argparse, binascii, hashlib, os, struct, sys

T1 = bytes.fromhex(
    "e8fe46e37dab5cb9a553c4c732cd9ced94674e5b483a52b634f78e129098823c"
    "092b68a824d5109d9ad9a97f504bdd9e621c6a640211da4a6e35bda0b1d7de83"
    "5de55eccdbac18e2256907bc399714ebb273368a99b81e2eef93baeef5c57b74"
    "8de1c34f41426ce6a2066f852a2f1b3808af4400336391228770b043b566e0ff"
    "30ad8fc1f4eaf9f651d6d43e04723d5478c07e26fa5658c955c8a6162384b7cb"
    "457cd87a272dca033f170b57bb3bf0491fd1868095206bc6bfaa79d275cfaed0"
    "5ff161f3fbce29650f312cfd760c4c4d60f8886da4ec9b9247a1e421fc81a7c2"
    "0ea3400d8b599637e7f2771d280a8c5a159f01b3d3beb41a89e91305dfdc7119"
)
T2 = bytes.fromhex(
    "760f43d9dbdc9b494e42b79fec551911582369a2b868e82b91f31a34ed0a0689"
    "b2792ac8eea3b5d0fd17f9ce743947c5c15d867f6aabe5f5c996711c0925d38c"
    "0c02b1487c463e087b01546bb94fcdf1515059a4a76c3fb69dbc4c9e1637a1c0"
    "6ee2da3d22cbe75b9853923690ac312421c66335b45c1f774ae40d138dc7997e"
    "813c6028f0bf822c787a5f938470ea9a8ed227e0cf6d109c560712fa269780e3"
    "e1618a75a95ade1e5e4d660eba4b2040a88f527ddfe6af6fbefc94a03a334514"
    "620087aeb38bd4caffe90488cc41d7d6bb953218f872653b29ad441bc2d81da5"
    "dd67d530a6ef2ff2832d03bd152ed17357aafb85f4640bc4f7eb38c3f605feb0"
)
T3 = bytes.fromhex(
    "2f2506bbe38270ce86fb003af8bf76f5c3f69d9e10eafc9cdd1246934fa6ad68"
    "94b822e1625bcf6708e7480c7e7db1a93e1bc50a11aabab2d079a5dbc66aa3d4"
    "8355879b5c27ab773642612db44d1a9f648fd5430524720241156d6e47266513"
    "4995cb71ef6f2cbdfdac31de2a5e29a2bc28c756c81675e419f2be3790e83b92"
    "354bd2d7d80e518bb0ec4cb9592e6654b5d1e51e0f5ac4cdeb4e7c748efa81e2"
    "7f9aa85f3289980739c0381f01e08d1df39657a00bed09188cf40d21d92378a1"
    "c1fe3c30735d4099b66c7b14cac2e68ae9ae7ad6f13da4342bda6384b3af88b7"
    "4597dc20173f4a520333dfd3046991f0f9cc5044ff8058f7c9606b53a785ee1c"
)

KNOWN_STOCK = {"7f5503b795fc41c83a26e98d834d48ff": "Nikon D300S firmware 1.02"}


def _pad(n):
    assert n <= 1 << 24, "XOR pad only defined for 2^24 bytes"
    o1 = int.from_bytes(T1, "big")
    ones = int.from_bytes(b"\x01" * 256, "big")
    out = bytearray()
    for blk in range((n + 255) // 256):
        c = T2[blk & 0xFF] ^ T3[(blk >> 8) & 0xFF]
        out += (o1 ^ (c * ones)).to_bytes(256, "big")
    return bytes(out[:n])


def xor_layer(data):
    return (int.from_bytes(data, "big") ^ int.from_bytes(_pad(len(data)), "big")).to_bytes(len(data), "big")


def blocks(b):
    n = struct.unpack_from(">I", b, 0x20)[0]
    res, pos = [], 0x30
    for _ in range(n):
        name = b[pos:pos + 16].split(b"\x00")[0].decode("ascii", "replace")
        res.append((name, struct.unpack_from(">I", b, pos + 16)[0], struct.unpack_from(">I", b, pos + 20)[0]))
        pos += 32
    return res


def crc16(data):
    return binascii.crc_hqx(data, 0)  # poly 0x1021, init 0 == XMODEM


def fix_crcs(b):
    b = bytearray(b)
    for _, off, ln in blocks(b):
        c = crc16(bytes(b[off:off + ln - 2]))
        b[off + ln - 2], b[off + ln - 1] = c >> 8, c & 0xFF
    return bytes(b)


def load(path):
    raw = open(path, "rb").read()
    return raw, xor_layer(raw)


def cmd_info(a):
    raw, dec = load(a.stock)
    md5 = hashlib.md5(raw).hexdigest()
    print(f"file   : {a.stock}  ({len(raw)} bytes)\nmd5    : {md5}  -> {KNOWN_STOCK.get(md5, 'UNKNOWN stock image')}")
    for i, (name, off, ln) in enumerate(blocks(dec)):
        stored = struct.unpack(">H", dec[off + ln - 2:off + ln])[0]
        calc = crc16(dec[off:off + ln - 2])
        print(f"block {i}: {name:16s} off=0x{off:07X} len={ln:8d} crc stored=0x{stored:04X} computed=0x{calc:04X} {'OK' if stored == calc else 'BAD'}")
    end = max(o + l for _, o, l in blocks(dec))
    print(f"trailer: {dec[end:].hex()}  (purpose unknown; left untouched, like the community tool)")


def cmd_decode(a):
    raw, dec = load(a.stock)
    os.makedirs(a.outdir, exist_ok=True)
    open(os.path.join(a.outdir, "bundle_decoded.bin"), "wb").write(dec)
    for name, off, ln in blocks(dec):
        open(os.path.join(a.outdir, name), "wb").write(dec[off:off + ln])
        print("wrote", os.path.join(a.outdir, name), ln)


def cmd_selftest(a):
    raw, dec = load(a.stock)
    ok_crc = all(struct.unpack(">H", dec[o + l - 2:o + l])[0] == crc16(dec[o:o + l - 2]) for _, o, l in blocks(dec))
    rt = xor_layer(fix_crcs(dec))
    print("stored CRCs match recomputed :", ok_crc)
    print("lossless round trip          :", rt == raw)
    sys.exit(0 if (ok_crc and rt == raw) else 1)


def parse_edit(s):
    blk, off, before, after = s.split(":")
    before, after = bytes.fromhex(before), bytes.fromhex(after)
    assert len(before) == len(after), "edits must be same length"
    return int(blk), int(off, 0), before, after


def cmd_patch(a):
    raw, dec = load(a.stock)
    md5 = hashlib.md5(raw).hexdigest()
    if md5 not in KNOWN_STOCK and not a.allow_unknown_stock:
        sys.exit(f"refusing: {md5} is not a known stock image (use --allow-unknown-stock to override)")
    b, bl = bytearray(dec), blocks(dec)
    for s in a.edit:
        blk, off, before, after = parse_edit(s)
        if off + len(before) > bl[blk][2] - 2:
            sys.exit(f"edit {s}: runs into the block's CRC bytes")
        p = bl[blk][1] + off
        if bytes(b[p:p + len(before)]) != before:
            sys.exit(f"edit {s}: stock bytes there are {bytes(b[p:p+len(before)]).hex()}, not {before.hex()} - refusing")
        b[p:p + len(after)] = after
    new = fix_crcs(bytes(b))
    out = xor_layer(new)
    open(a.out, "wb").write(out)
    changed = [i for i in range(len(dec)) if dec[i] != new[i]]
    print(f"wrote {a.out} ({len(out)} bytes) md5={hashlib.md5(out).hexdigest()}")
    print(f"{len(changed)} bytes differ from stock (edits + CRC bytes):")
    for i in changed:
        blk = next((k for k, (_, o, l) in enumerate(bl) if o <= i < o + l), None)
        where = f"block {blk}+0x{i - bl[blk][1]:X}" if blk is not None else "outside blocks"
        print(f"  0x{i:07X} ({where}): {dec[i]:02X} -> {new[i]:02X}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    for n, f in (("info", cmd_info), ("decode", cmd_decode), ("selftest", cmd_selftest), ("patch", cmd_patch)):
        s = sp.add_parser(n); s.set_defaults(fn=f); s.add_argument("stock")
        if n == "decode": s.add_argument("outdir")
        if n == "patch":
            s.add_argument("out"); s.add_argument("--edit", action="append", default=[], required=True)
            s.add_argument("--allow-unknown-stock", action="store_true")
    a = p.parse_args(); a.fn(a)
