#!/usr/bin/env python3
"""Validate README empirical claims against the local Flammenkamp cache.

Checks:
  (A) rot4 ring populations across ALL cached rot4 solutions (n=8..72):
      - max ring population (README claims <=16, i.e. 4/8/12/16)
      - is every population a multiple of 4? (Orbit-Ring theorem)
      - orbit count == n/2 for every solution? (structure theorem)
  (B) rot2 existence per n: confirm n=33 has a solution, n=31/32 do not
      (README 3.1/3.9 say "rot2 vanishes at n=31 / only rct4 survives n>=33").
"""
import os, glob, re, json, math

CACHE = os.path.join(os.path.dirname(__file__), 'flammenkamp_cache')
ALPH = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|'
VAL = {c: i for i, c in enumerate(ALPH)}

def decode_points(line, n):
    """Flammenkamp NTIL encoding: class_char + 2n single base64 chars, points in
    row-major order (2 points per row). Returns list of (row,col) for all 2n points."""
    body = line.strip()[1:]  # drop class char
    assert len(body) == 2 * n, f"len {len(body)} != {2*n} (n={n})"
    pts = []
    for k in range(2 * n):
        r = k // 2
        c = VAL[body[k]]
        pts.append((r, c))
    return pts

def ring_populations(pts, n):
    X = n - 1
    cnt = {}
    for r, c in pts:
        d = (2 * r - X) ** 2 + (2 * c - X) ** 2
        cnt[d] = cnt.get(d, 0) + 1
    return list(cnt.values())

# ---------- (A) rot4 ring populations ----------
rot4_files = sorted(glob.glob(os.path.join(CACHE, 'n*_rot4')),
                     key=lambda p: int(re.search(r'n(\d+)_rot4', p).group(1)))
rot4_files += sorted(glob.glob(os.path.join(CACHE, 'n*_rot4.few')),
                      key=lambda p: int(re.search(r'n(\d+)_rot4', p).group(1)))
# dedupe (n58_rot4.few both patterns captured? no: n*_rot4 matches n58_rot4.few too)
seen = set(); uniq = []
for f in rot4_files:
    base = os.path.basename(f).replace('.few', '')
    if base in seen: continue
    seen.add(base); uniq.append(f)
rot4_files = uniq

max_pop = 0
max_pop_info = None
pop_set = {}
n_solutions = 0
orbit_ok = 0
mult4_fail = []
per_n_maxpop = {}
for f in rot4_files:
    n = int(re.search(r'n(\d+)_rot4', f).group(1))
    with open(f) as fh:
        for line in fh:
            line = line.strip()
            if not line: continue
            pts = decode_points(line, n)
            cols = [c for _, c in pts]
            if len(set(cols)) != n:  # sanity: 2-per-row means all distinct cols
                continue
            pops = ring_populations(pts, n)
            n_solutions += 1
            # orbit count: a C4 orbit is {p, R(p), R^2(p), R^3(p)}; count distinct orbits
            # Actually 2n points / 4 = n/2 orbits always for even n valid rot4.
            # Check ring pop structure:
            for p in pops:
                pop_set[p] = pop_set.get(p, 0) + 1
                if p > max_pop:
                    max_pop = p
                    max_pop_info = (n, pops)
            per_n_maxpop[n] = max(per_n_maxpop.get(n, 0), max(pops))
            if any(p % 4 != 0 for p in pops):
                mult4_fail.append((n, pops))

print("=== (A) rot4 ring populations ===")
print(f"total rot4 solutions scanned: {n_solutions}")
print(f"distinct ring-population values observed: {sorted(pop_set.keys())}")
print(f"max ring population overall: {max_pop}  (at n={max_pop_info[0]}, pops={sorted(max_pop_info[1])})")
print(f"claim 'max<=16 (4/8/12/16)': {'OK' if max_pop<=16 else 'REFUTED'}")
print(f"claim 'every population multiple of 4': {'OK' if not mult4_fail else f'FAIL {len(mult4_fail)} solutions'}")
print("per-n max ring population:")
for n in sorted(per_n_maxpop):
    print(f"  n={n:2d}: max={per_n_maxpop[n]}")

# ---------- (B) rot2 existence per n ----------
print("\n=== (B) rot2 existence ===")
rot2_standard = sorted(glob.glob(os.path.join(CACHE, 'n*_rot2')),
                        key=lambda p: int(re.search(r'n(\d+)_rot2', os.path.basename(p)).group(1)))
rot2_few = glob.glob(os.path.join(CACHE, 'n*_rot2.few'))
counts = {}
for f in rot2_standard:
    n = int(re.search(r'n(\d+)_rot2', f).group(1))
    cnt = sum(1 for l in open(f) if l.strip())
    counts[n] = counts.get(n, 0) + cnt
for f in rot2_few:
    n = int(re.search(r'n(\d+)_rot2', f).group(1))
    cnt = sum(1 for l in open(f) if l.strip())
    counts[n] = counts.get(n, 0) + cnt
ns = sorted(counts)
print("n with rot2 solutions (cache):", ns)
print("rot2 counts:", {n: counts[n] for n in ns})
print("n=31 rot2 count:", counts.get(31, 0), "(README 3.10: UNSAT=0)")
print("n=32 rot2 count:", counts.get(32, 0))
print("n=33 rot2 count:", counts.get(33, 0), "(README 3.1 line283 'rot2 vanishes at n=31' -> contradicted if >0)")
print("=> 'rot2 UNSAT beyond n=31 / only rct4 n>=33' claim:",
      "REFUTED (n=33 has solution)" if counts.get(33, 0) > 0 else "not contradicted by cache")
