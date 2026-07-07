#!/usr/bin/env python3
"""Audit verification: decode Flammenkamp base-62 cache and mvr RLE, check paper claims."""
import os, re, glob, json

CACHE = os.path.join(os.path.dirname(__file__), "flammenkamp_cache")
MVR = os.path.join(os.path.dirname(__file__), "mvr_cache")

ALPH = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

def val(ch):
    return ALPH.index(ch)

def decode_line(line, n):
    """line = symm_prefix + 2n chars. Returns list of (r,c) points."""
    body = line[1:1+2*n]
    pts = []
    for r in range(n):
        c1 = val(body[2*r])
        c2 = val(body[2*r+1])
        pts.append((r, c1))
        pts.append((r, c2))
    return pts

def has_center(pts, n):
    X = n - 1
    rings = {}
    for (r, c) in pts:
        d = (2*r - X)**2 + (2*c - X)**2
        rings[d] = rings.get(d, 0) + 1
    return any(v >= 3 for v in rings.values())

# ---- 1. D4 table per n (sum over classes) ----
d4 = {}  # n -> [total, missing]
for path in glob.glob(os.path.join(CACHE, "n*_*")):
    fn = os.path.basename(path)
    m = re.match(r"n(\d+)_(\w+)", fn)
    if not m:
        continue
    n = int(m.group(1))
    cls = m.group(2)
    if cls in ("full", "ort1", "dia2"):  # full is redundant; we sum class files separately
        pass
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    tot = len(lines)
    miss = 0
    for ln in lines:
        n2 = int(m.group(1))
        try:
            pts = decode_line(ln, n2)
        except Exception:
            continue
        if not has_center(pts, n2):
            miss += 1
    if n not in d4:
        d4[n] = [0, 0]
    d4[n][0] += tot
    d4[n][1] += miss

print("=== D4-inequivalent per n (from cache, all present classes) ===")
for n in sorted(d4):
    tot, miss = d4[n]
    rate = 100.0*miss/tot if tot else 0
    print(f"n={n:2d}  Total={tot:7d}  Missing={miss:6d}  Rate={rate:5.2f}%")

# ---- 2. rot4 counts: regular cache + mvr ----
print("\n=== rot4 counts ===")
rot4_cache = {}
for path in glob.glob(os.path.join(CACHE, "n*_rot4")):
    fn = os.path.basename(path)
    n = int(re.match(r"n(\d+)_rot4", fn).group(1))
    with open(path) as f:
        c = sum(1 for l in f if l.strip())
    rot4_cache[n] = c
for n in sorted(rot4_cache):
    print(f"n={n:2d} (cache reg) rot4={rot4_cache[n]}")

print("-- mvr c4-N.out line counts --")
for path in sorted(glob.glob(os.path.join(MVR, "c4-*.out"))):
    fn = os.path.basename(path)
    n = int(re.match(r"c4-(\d+)\.out", fn).group(1))
    with open(path) as f:
        c = sum(1 for l in f if l.strip())
    print(f"n={n:2d} (mvr) rot4={c}")

# ---- 3. rot2 counts for odd n=23,25,27,29 ----
print("\n=== rot2 counts (odd n) ===")
for n in [21,23,25,27,29,31]:
    p = os.path.join(CACHE, f"n{n}_rot2")
    if os.path.exists(p):
        with open(p) as f:
            c = sum(1 for l in f if l.strip())
        print(f"n={n} rot2={c}")
    else:
        print(f"n={n} rot2=FILE MISSING")

# ---- 4. rct4 presence at n=11,13,15 ----
print("\n=== rct4 presence ===")
for n in [9,11,13,15,17,19]:
    p = os.path.join(CACHE, f"n{n}_rct4")
    print(f"n={n} rct4 file exists: {os.path.exists(p)}")

# ---- 5. orbit structure for n=12,14,16,18 ----
def orbit_structure(pts, n):
    X = n - 1
    R = lambda p: ((n-1-(p[1])), p[0])  # 90deg rotation (n-1-j, i)
    seen = set(pts)
    orbits = []
    for p in pts:
        if p in seen:
            orb = []
            cur = p
            while cur in seen:
                seen.discard(cur)
                orb.append(cur)
                cur = R(cur)
            orbits.append(orb)
    rings = {}
    for (r,c) in pts:
        d = (2*r-X)**2+(2*c-X)**2
        rings[d]=rings.get(d,0)+1
    pops = sorted(rings.values())
    return len(orbits), len(rings), pops

print("\n=== orbit structure (rot4 solutions) ===")
for n in [12,14,16,18]:
    p = os.path.join(CACHE, f"n{n}_rot4")
    if not os.path.exists(p):
        continue
    alln=[]; allr=[]; allmax=[]; allpops=[]
    with open(p) as f:
        for ln in f:
            ln=ln.strip()
            if not ln: continue
            pts=decode_line(ln,n)
            no,nr,pops=orbit_structure(pts,n)
            alln.append(no); allr.append(nr); allmax.append(max(pops)); allpops.append(pops)
    import statistics
    print(f"n={n}: orbits(n/2={n//2}) min/max={min(alln)}/{max(alln)}  rings min/max={min(allr)}/{max(allr)}  maxpop={allmax}  popset_distinct={set(tuple(p) for p in allpops)}")

# ---- 6. n=72 rot4 has center? ----
p = os.path.join(CACHE, "n72_rot4.few")
print(f"\nn72_rot4.few exists: {os.path.exists(p)} (needs .few decoder; skipping decode)")
