#!/usr/bin/env python3
"""miskit - CTF misc one-shot attacks (baked into ctf-forensics at /opt/miskit).

Generalized versions of classic misc script templates (idea provenance:
Des-CTF-Knowledge, MIT). Inputs are files/values, not hardcoded.

Usage:
  miskit crc <crc32val...> [--len N] [--charset S]   # brute strings matching CRC32
  miskit pngfix <file.png> [--max W]                 # brute IHDR width/height by CRC
  miskit usbkey <reports.txt>                        # USB HID reports -> typed text
  miskit ttl <file> [--base 128] [--mode diff|lsb]   # TTL stego decode
  miskit base <string | --file F> [--layers 5]       # nested base16/32/58/64/85 autodetect
  miskit stegcrack <file> <wordlist>                 # steghide password brute
"""
from __future__ import annotations

import argparse
import binascii
import base64
import struct
import string
import sys
import zlib


def info(msg): print(f"[*] {msg}", file=sys.stderr)


# ---------------------------------------------------------------- crc

def cmd_crc(args):
    charset = args.charset or string.ascii_letters + string.digits + "{}_-"
    targets = [int(v, 16) if v.startswith("0x") else int(v) for v in args.vals]
    found = ["?"] * len(targets)

    def rec(prefix: str, crcs: list, depth: int):
        if depth > args.len:
            return
        for ch in charset:
            c = ch.encode()
            crcs2 = [zlib.crc32(c, crc) for crc in crcs]
            for i, t in enumerate(targets):
                if crcs2[i] & 0xFFFFFFFF == t:
                    found[i] = prefix + ch
                    info(f"matched #{i + 1}: {found[i]}")
            if depth < args.len:
                rec(prefix + ch, crcs2, depth + 1)

    for length in range(1, args.len + 1):
        info(f"length {length} ...")
        rec("", [zlib.crc32(b"")] * len(targets), 1)
    print("result:", "".join(found))


# ---------------------------------------------------------------- pngfix

def cmd_pngfix(args):
    data = open(args.file, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("not a PNG"); return
    ihdr_type = data[12:16]
    if ihdr_type != b"IHDR":
        print("first chunk is not IHDR"); return
    chunk_data = data[16:29]
    stored = struct.unpack(">I", data[29:33])[0]
    tail = chunk_data[8:]
    info(f"brute width/height up to {args.max} (stored ihdr crc {stored:#x})")
    # PNG chunk CRC covers chunk type + data
    type_crc = zlib.crc32(b"IHDR")
    for w in range(1, args.max + 1):
        head_w = struct.pack(">I", w)
        base_w = zlib.crc32(head_w, type_crc)
        for h in range(1, args.max + 1):
            crc = zlib.crc32(tail, zlib.crc32(struct.pack(">I", h), base_w))
            if crc & 0xFFFFFFFF == stored:
                fixed = data[:16] + head_w + struct.pack(">I", h) + data[24:]
                out = args.file + ".fixed.png"
                open(out, "wb").write(fixed)
                print(f"restored: width={w} height={h} -> {out}")
                return
    print(f"no (w,h) pair <= {args.max} matches the IHDR CRC (try a larger --max)")


# ---------------------------------------------------------------- usb hid

_HID = {
    0x04: "a", 0x05: "b", 0x06: "c", 0x07: "d", 0x08: "e", 0x09: "f", 0x0A: "g",
    0x0B: "h", 0x0C: "i", 0x0D: "j", 0x0E: "k", 0x0F: "l", 0x10: "m", 0x11: "n",
    0x12: "o", 0x13: "p", 0x14: "q", 0x15: "r", 0x16: "s", 0x17: "t", 0x18: "u",
    0x19: "v", 0x1A: "w", 0x1B: "x", 0x1C: "y", 0x1D: "z",
    0x1E: "1", 0x1F: "2", 0x20: "3", 0x21: "4", 0x22: "5", 0x23: "6", 0x24: "7",
    0x25: "8", 0x26: "9", 0x27: "0",
    0x28: "\n", 0x2A: "\b", 0x2B: "\t", 0x2C: " ",
    0x2D: "-", 0x2E: "=", 0x2F: "[", 0x30: "]", 0x31: "\\", 0x33: ";", 0x34: "'",
    0x35: "`", 0x36: ",", 0x37: ".", 0x38: "/",
}
_HID_SHIFT = {
    "-": "_", "=": "+", "[": "{", "]": "}", "\\": "|", ";": ":", "'": '"',
    "`": "~", ",": "<", ".": ">", "/": "?", "1": "!", "2": "@", "3": "#",
    "4": "$", "5": "%", "6": "^", "7": "&", "8": "*", "9": "(", "0": ")",
}


def cmd_usbkey(args):
    out = []
    for line in open(args.file, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line or "no data" in line.lower():
            continue
        hx = line.replace(":", " ").split()
        try:
            bs = bytes.fromhex("".join(hx))
        except ValueError:
            continue
        if len(bs) < 3:
            continue
        mod, key = bs[0], bs[2]
        if key == 0x00 or key not in _HID:
            continue
        ch = _HID[key]
        if mod & 0x22:  # left/right shift held
            ch = _HID_SHIFT.get(ch, ch.upper())
        out.append(ch)
    print("typed:", "".join(out))


# ---------------------------------------------------------------- ttl

def cmd_ttl(args):
    vals = []
    for line in open(args.file, encoding="utf-8", errors="replace"):
        line = line.strip()
        for token in line.split():
            if token.isdigit():
                vals.append(int(token))
    info(f"{len(vals)} numeric values")
    out = []
    if args.mode == "lsb":
        bits = "".join(str(v & 1) for v in vals)
        for i in range(0, len(bits) - 7, 8):
            out.append(chr(int(bits[i:i + 8], 2)))
    else:  # diff from a base TTL (e.g. 128 windows / 64 linux)
        for v in vals:
            if 0 <= args.base - v < 256:
                out.append(chr(args.base - v))
    print("decoded:", "".join(out))


# ---------------------------------------------------------------- nested base

def _b58decode(s: str) -> bytes:
    alpha = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n = 0
    for ch in s:
        if ch not in alpha:
            raise ValueError
        n = n * 58 + alpha.index(ch)
    raw = n.to_bytes((n.bit_length() + 7) // 8 or 1, "big")
    pad = len(s) - len(s.lstrip("1"))
    return b"\x00" * pad + raw


def _try_decode(s: str):
    t = s.strip()
    if not t:
        return None
    candidates = []
    if len(t) % 2 == 0 and all(c in "0123456789abcdefABCDEF" for c in t):
        candidates.append(("hex", base64.b16decode, (t.upper(),)))
    candidates.append(("base32", base64.b32decode, (t + "=" * (-len(t) % 8),)))
    candidates.append(("base64", base64.b64decode, (t + "=" * (-len(t) % 4),)))
    candidates.append(("base64url", base64.urlsafe_b64decode, (t + "=" * (-len(t) % 4),)))
    candidates.append(("base85", base64.a85decode, (t,)))
    candidates.append(("base58", _b58decode, (t,)))
    for name, fn, argv in candidates:
        try:
            raw = fn(*argv)
            if raw and all(32 <= c < 127 or c in (9, 10, 13) for c in raw):
                return name, raw.decode()
        except Exception:
            continue
    return None


def cmd_base(args):
    s = open(args.file).read() if args.file else args.text
    s = s.strip()
    for layer in range(1, args.layers + 1):
        r = _try_decode(s)
        if not r:
            print(f"layer {layer}: no further base decoding (stopped)")
            break
        name, raw = r
        print(f"layer {layer}: {name} -> {raw[:200]}{'...' if len(raw) > 200 else ''}")
        s = raw
    print("final:", s)


# ---------------------------------------------------------------- steghide

def cmd_stegcrack(args):
    import subprocess
    import tempfile
    candidates = []
    for line in open(args.wordlist, encoding="utf-8", errors="replace"):
        pw = line.rstrip("\r\n")
        candidates.append(pw)
    # unique sink per attempt: steghide prompts on existing files, which would
    # fail even with the correct password
    sink = tempfile.mktemp()
    for i, pw in enumerate(candidates):
        r = subprocess.run(
            ["steghide", "extract", "-sf", args.file, "-p", pw, "-xf", sink],
            capture_output=True, text=True)
        if r.returncode == 0:
            print(f"password: {pw!r}")
            if args.extract:
                subprocess.run(["steghide", "extract", "-sf", args.file,
                                "-p", pw, "-xf", args.extract])
            return
        if i % 200 == 0:
            info(f"{i} tried")
    print("no password found in wordlist")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="miskit", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("crc")
    p.add_argument("vals", nargs="+")
    p.add_argument("--len", type=int, default=4)
    p.add_argument("--charset", default=None)
    p = sp.add_parser("pngfix"); p.add_argument("file"); p.add_argument("--max", type=int, default=1024)
    p = sp.add_parser("usbkey"); p.add_argument("file")
    p = sp.add_parser("ttl"); p.add_argument("file")
    p.add_argument("--base", type=int, default=128); p.add_argument("--mode", default="diff")
    p = sp.add_parser("base"); p.add_argument("text", nargs="?"); p.add_argument("--file")
    p.add_argument("--layers", type=int, default=5)
    p = sp.add_parser("stegcrack"); p.add_argument("file"); p.add_argument("wordlist")
    p.add_argument("--extract")
    args = ap.parse_args()
    globals()[f"cmd_{args.cmd}"](args)


if __name__ == "__main__":
    main()
