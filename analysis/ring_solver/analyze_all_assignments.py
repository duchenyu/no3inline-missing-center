#!/usr/bin/env python3
"""
Analyze ring assignment PATTERNS across all missing-center solutions.
Plus: try to understand why some assignments work and others don't.
"""
import sys
from collections import defaultdict, Counter
sys.path.insert(0, "D:/djr82/Documents/workbuddy/2026-07-03-16-29-36")
from analyze_rle import parse_rle

def build_rings(n):
    cx2 = cy2 = n - 1
    rings = defaultdict(list)
    for r in range(n):
        for c in range(n):
            d = (2*c - cx2)**2 + (2*r - cy2)**2
            rings[d].append((r, c))
    return dict(sorted(rings.items()))

def check_missing(pts, n):
    from collections import Counter
    cx2 = cy2 = n - 1
    dc = Counter()
    for x, y in pts:
        d = (2*x - cx2)**2 + (2*y - cy2)**2
        dc[d] += 1
    return max(dc.values()) <= 2, dc

# ========== Analyze n=12 ==========
n = 12
rings = build_rings(n)
ring_list = sorted(rings.keys())

with open(f"D:/djr82/Documents/workbuddy/2026-07-03-16-29-36/results_{n}.out") as f:
    text = f.read()
sols = parse_rle(text, n)

missing = []
for pts in sols:
    is_missing, dc = check_missing(pts, n)
    if is_missing:
        missing.append((pts, dc))

print(f"n={n}: {len(missing)} missing-center solutions")
print()

# Show EACH missing solution's ring assignment
for idx, (pts, dc) in enumerate(missing):
    used = {d: c for d, c in sorted(dc.items()) if c > 0}
    skipped = [d for d in ring_list if d not in used]
    
    total_2 = sum(1 for c in used.values() if c == 2)
    total_1 = sum(1 for c in used.values() if c == 1)
    
    print(f"  Solution #{idx+1}: {total_2}×2pt + {total_1}×1pt = {sum(used.values())}pts")
    print(f"    Used: {dict(sorted(used.items()))}")
    print(f"    Skipped: {skipped}")
    print()

# ========== Now do the same for n=14 ==========
print(f"\n{'='*60}")
print(f"n=14 Missing-Center Solutions")
print(f"{'='*60}")

n = 14
rings14 = build_rings(n)
ring14_list = sorted(rings14.keys())

with open(f"D:/djr82/Documents/workbuddy/2026-07-03-16-29-36/results_{n}.out") as f:
    text = f.read()
sols14 = parse_rle(text, n)

missing14 = []
for pts in sols14:
    is_missing, dc = check_missing(pts, n)
    if is_missing:
        missing14.append((pts, dc))

print(f"\nn=14: {len(missing14)} missing-center solutions")
print()

# Pattern analysis  
pattern_counts = Counter()
for idx, (pts, dc) in enumerate(missing14[:20]):  # First 20
    used = {d: c for d, c in sorted(dc.items()) if c > 0}
    total_2 = sum(1 for c in used.values() if c == 2)
    total_1 = sum(1 for c in used.values() if c == 1)
    pattern = (total_2, total_1)
    pattern_counts[pattern] += 1
    
    if idx < 5:  # Show first 5
        skipped = [d for d in ring14_list if d not in used]
        print(f"  Solution #{idx+1}: {total_2}×2pt + {total_1}×1pt = {sum(used.values())}pts")
        print(f"    Used: {dict(sorted(used.items()))}")
        print(f"    Skipped: {skipped}")
        print()

print(f"\nPattern distribution:")
for pattern, cnt in pattern_counts.most_common():
    print(f"  {pattern[0]}×2pt + {pattern[1]}×1pt: {cnt} solutions")

# Show common skipped rings
common_skipped = defaultdict(int)
for pts, dc in missing14:
    for d in ring14_list:
        if d not in dc or dc[d] == 0:
            common_skipped[d] += 1

print(f"\nRings skipped across n=14 missing solutions:")
for d in sorted(ring14_list):
    pct = common_skipped[d] / max(len(missing14), 1) * 100
    print(f"  d={d:4d}: skipped in {common_skipped[d]}/{len(missing14)} ({pct:.0f}%)")
