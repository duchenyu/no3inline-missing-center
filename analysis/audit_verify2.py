#!/usr/bin/env python3
"""Focused re-verification for the 5 new D4-table rows + even re-disappearance."""
import os, re, glob

CACHE = os.path.join(os.path.dirname(__file__), "flammenkamp_cache")
ALPH = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

def val(ch):
    return ALPH.index(ch)

def decode_line(line, n):
    body = line[1:1+2*n]
    pts = []
    for r in range(n):
        c1 = val(body[2*r]); c2 = val(body[2*r+1])
        pts.append((r, c1)); pts.append((r, c2))
    return pts

def has_center(pts, n):
    X = n - 1; rings = {}
    for (r, c) in pts:
        d = (2*r - X)**2 + (2*c - X)**2
        rings[d] = rings.get(d, 0) + 1
    return any(v >= 3 for v in rings.values())

def d4_for_n(n):
    tot = miss = 0
    for path in glob.glob(os.path.join(CACHE, f"n{n}_*")):
        fn = os.path.basename(path)
        if not re.match(rf"n{n}_\w+", fn):
            continue
        with open(path) as f:
            lines = [l.strip() for l in f if l.strip()]
        for ln in lines:
            try:
                pts = decode_line(ln, n)
            except Exception:
                continue
            tot += 1
            if not has_center(pts, n):
                miss += 1
    return tot, miss

print("=== 5 new rows (n=23,25,26,28,29) ===")
for n in [23,25,26,28,29]:
    tot, miss = d4_for_n(n)
    rate = 100.0*miss/tot if tot else 0
    print(f"n={n:2d}  Total={tot:7d}  Missing={miss:5d}  Rate={rate:4.1f}%")

print("\n=== even-n re-disappearance (n=32..72 step 2) ===")
for n in range(32, 73, 2):
    tot, miss = d4_for_n(n)
    print(f"n={n:2d}  Total={tot:7d}  Missing={miss}")

print("\n=== rot2 transition numbers (odd n) ===")
for n in [23,25,27,29,31,33]:
    p = os.path.join(CACHE, f"n{n}_rot2")
    if os.path.exists(p):
        with open(p) as f:
            c = sum(1 for l in f if l.strip())
        print(f"n={n} rot2={c}")
    else:
        print(f"n={n} rot2=MISSING")

print("\n=== n=29 total classes breakdown ===")
for cls in ["iden","rot2","dia1","ort1","rot4","rct4","dia2","ort2","full"]:
    p = os.path.join(CACHE, f"n29_{cls}")
    if os.path.exists(p):
        with open(p) as f:
            c = sum(1 for l in f if l.strip())
        print(f"  n29_{cls}={c}")
